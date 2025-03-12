"""
Plugin interface for Open WebUI.

This module provides direct integration with Open WebUI application.
"""

import os
import logging
import importlib
from pathlib import Path
from typing import Any, Dict, List, Optional, Type

from fastapi import FastAPI, Request, Response

logger = logging.getLogger("webui-extensions.plugin")

# Check if we have access to needed modules
try:
    from fastapi.middleware.base import BaseHTTPMiddleware
    HAS_MIDDLEWARE = True
except ImportError:
    logger.warning("fastapi.middleware.base not found, some features will be disabled")
    HAS_MIDDLEWARE = False
    # Create a dummy BaseHTTPMiddleware class
    class BaseHTTPMiddleware:
        def __init__(self, app):
            self.app = app
        
        async def __call__(self, scope, receive, send):
            await self.app(scope, receive, send)

class OpenWebUIExtensionsPlugin:
    """
    A plugin that adds extension capabilities to Open WebUI.
    
    This class provides direct integration with the Open WebUI application.
    """
    
    def __init__(self):
        """Initialize the plugin."""
        self.app = None
        self.initialized = False
        self.extension_manager = None
    
    def initialize(self, app: Any) -> bool:
        """
        Initialize the plugin with the Open WebUI application.
        
        Args:
            app: The Open WebUI FastAPI application.
            
        Returns:
            True if initialization was successful, False otherwise.
        """
        try:
            self.app = app
            
            # Initialize the extension system
            from open_webui_extensions.extension_system.registry import initialize_registry
            registry = initialize_registry()
            
            # Register API routes
            from open_webui_extensions.manager.api import create_router
            router = create_router(registry)
            self.app.include_router(router, prefix="/api/extensions", tags=["extensions"])
            
            # Register direct UI routes that bypass the frontend router
            from fastapi.responses import HTMLResponse, RedirectResponse
            
            @self.app.get("/ext-manager")
            async def get_extensions_manager():
                from open_webui_extensions.manager.ui import render_extensions_page
                return HTMLResponse(render_extensions_page())
            
            @self.app.get("/ext-manager/{name}")
            async def get_extension_detail(name: str):
                from open_webui_extensions.manager.ui import render_extension_detail_page
                return HTMLResponse(render_extension_detail_page(name))
            
            # Create a special debug route
            @self.app.get("/ext-debug")
            async def extension_debug():
                try:
                    # Check if admin menu contains the extension entry
                    admin_menu = []
                    if hasattr(self.app.state, "admin_menu"):
                        admin_menu = self.app.state.admin_menu
                    
                    # List extension API routes
                    routes = []
                    for route in self.app.routes:
                        if "/api/extensions" in route.path or "/ext-" in route.path:
                            routes.append(f"{route.methods} {route.path}")
                    
                    # Check registry status
                    from open_webui_extensions.extension_system.registry import get_registry
                    extensions = get_registry().list_extensions()
                    
                    # Create a debug page
                    html = f"""
                    <html>
                    <head>
                        <title>Extension System Debug</title>
                        <style>
                            body {{ font-family: system-ui, sans-serif; line-height: 1.5; padding: 2rem; }}
                            h1, h2 {{ color: #0066cc; }}
                            pre {{ background: #f5f5f5; padding: 1rem; overflow: auto; }}
                            .card {{ border: 1px solid #ddd; border-radius: 0.5rem; padding: 1rem; margin-bottom: 1rem; }}
                            .success {{ color: green; }}
                            .error {{ color: red; }}
                        </style>
                    </head>
                    <body>
                        <h1>Extension System Debug</h1>
                        
                        <h2>Direct Extension Links</h2>
                        <p>These links bypass Open WebUI's frontend router:</p>
                        <ul>
                            <li><a href="/ext-manager" target="_blank">Extension Manager</a></li>
                            <li><a href="/api/extensions" target="_blank">Extensions API</a></li>
                        </ul>
                        
                        <h2>Admin Menu Items</h2>
                        <pre>{admin_menu}</pre>
                        
                        <h2>Extension Routes</h2>
                        <pre>{routes}</pre>
                        
                        <h2>Installed Extensions</h2>
                        <div>
                            {"".join([f'<div class="card"><h3>{ext.name}</h3><p>Version: {ext.version}</p><p>Status: {"Active" if ext.active else "Inactive"}</p><p>{ext.description}</p></div>' for ext in extensions])}
                        </div>
                        
                        <h2>Extension System Status</h2>
                        <pre>Plugin initialized: {self.initialized}</pre>
                    </body>
                    </html>
                    """
                    return HTMLResponse(content=html)
                except Exception as e:
                    logger.error(f"Error in debug page: {e}")
                    return HTMLResponse(f"<html><body><h1>Error</h1><p>{e}</p></body></html>")
            
            # Add extension manager to admin menu
            self._add_to_admin_menu()
            
            # Initialize extensions
            registry.initialize_all()
            
            # Register hooks if middleware is available
            if HAS_MIDDLEWARE:
                self._register_hooks()
            
            logger.info("Open WebUI Extensions plugin initialized successfully.")
            self.initialized = True
            return True
        except Exception as e:
            logger.error(f"Error initializing Open WebUI Extensions plugin: {e}")
            return False
    
    def _add_to_admin_menu(self) -> None:
        """Add the extension manager to the admin menu."""
        try:
            # Try to add to admin menu state if exists
            if hasattr(self.app, "state") and hasattr(self.app.state, "admin_menu"):
                # Check if the menu already has an Extensions item
                for item in self.app.state.admin_menu:
                    if isinstance(item, dict) and item.get("name") == "Extensions":
                        logger.info("Extensions menu item already exists")
                        return
                        
                # Add the menu item - point to our direct route instead of admin/extensions
                self.app.state.admin_menu.append({
                    "name": "Extensions",
                    "icon": "puzzle-piece", 
                    "url": "/ext-manager"  # Use our direct route
                })
                logger.info("Added Extensions to admin menu in app.state.admin_menu")
                
            # Print the current admin menu items for debugging
            if hasattr(self.app, "state") and hasattr(self.app.state, "admin_menu"):
                menu_items = [item.get("name") if isinstance(item, dict) else str(item) 
                             for item in self.app.state.admin_menu]
                logger.info(f"Current admin menu items: {menu_items}")
                
        except Exception as e:
            logger.error(f"Error adding Extensions to admin menu: {e}")
    
    def _register_hooks(self) -> None:
        """Register hooks for chat processing if middleware is available."""
        # Skip if middleware isn't available
        if not HAS_MIDDLEWARE:
            logger.warning("Middleware not available, skipping hook registration")
            return
            
        try:
            # Import our hooks system
            from open_webui_extensions.extension_system.hooks import execute_hook
            
            # Register chat route middleware
            class ChatMiddleware(BaseHTTPMiddleware):
                async def dispatch(self, request, call_next):
                    # Only process chat completion requests
                    if request.url.path == "/api/chat/completions" and request.method == "POST":
                        # Get the body before it's consumed
                        body = await request.body()
                        
                        # Execute the pre-processing hook
                        try:
                            modified_body = await execute_hook("chat_pre_process", body)
                            if modified_body and modified_body != body:
                                # Replace the request body with our modified version
                                request._body = modified_body
                        except Exception as e:
                            logger.error(f"Error in chat_pre_process hook: {e}")
                    
                    # Continue with the request
                    response = await call_next(request)
                    
                    # Post-process the response for chat completions
                    if request.url.path == "/api/chat/completions" and request.method == "POST":
                        try:
                            # Get the response content
                            body = b""
                            async for chunk in response.body_iterator:
                                body += chunk
                            
                            # Execute the post-processing hook
                            modified_body = await execute_hook("chat_post_process", body)
                            
                            # If the hook modified the body, return a new response
                            if modified_body and modified_body != body:
                                from fastapi.responses import Response
                                return Response(
                                    content=modified_body,
                                    status_code=response.status_code,
                                    headers=dict(response.headers),
                                    media_type=response.media_type
                                )
                            
                            # Otherwise, rebuild the original response
                            from fastapi.responses import Response
                            return Response(
                                content=body,
                                status_code=response.status_code,
                                headers=dict(response.headers),
                                media_type=response.media_type
                            )
                        except Exception as e:
                            logger.error(f"Error in chat_post_process hook: {e}")
                    
                    return response
            
            # Add the middleware if possible
            try:
                self.app.add_middleware(ChatMiddleware)
                logger.info("Registered chat middleware for extension hooks")
            except Exception as e:
                logger.error(f"Error adding chat middleware: {e}")
            
        except Exception as e:
            logger.error(f"Error registering hooks: {e}")
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get information about the plugin.
        
        Returns:
            A dictionary containing plugin information.
        """
        return {
            "name": "Open WebUI Extensions",
            "version": "0.1.0",
            "description": "Extension system for Open WebUI",
            "author": "Open WebUI Team",
            "homepage": "https://github.com/open-webui/extensions",
            "initialized": self.initialized,
        }


def initialize_extension_system(app: FastAPI) -> FastAPI:
    """
    Initialize the extension system and integrate it with Open WebUI.
    
    Args:
        app: The FastAPI application to integrate with.
        
    Returns:
        The modified FastAPI application.
    """
    plugin = OpenWebUIExtensionsPlugin()
    if plugin.initialize(app):
        logger.info("Extension system initialized successfully!")
    else:
        logger.error("Failed to initialize extension system")
    return app
