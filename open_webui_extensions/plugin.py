"""
Plugin interface for Open WebUI.

This module provides a plugin interface that hooks into Open WebUI
without requiring direct access to its files.
"""

import os
import logging
import importlib
from pathlib import Path
from typing import Any, Dict, List, Optional, Type

logger = logging.getLogger("webui-extensions.plugin")

class OpenWebUIExtensionsPlugin:
    """
    A plugin that adds extension capabilities to Open WebUI.
    
    This plugin is registered with Open WebUI through the entry point
    system and is used to inject the extension system into the Open WebUI
    application.
    """
    
    def __init__(self):
        """Initialize the plugin."""
        self.app = None
        self.initialized = False
        self.extension_manager = None
    
    def initialize(self, app: Any) -> None:
        """
        Initialize the plugin with the Open WebUI application.
        
        Args:
            app: The Open WebUI FastAPI application.
        """
        try:
            self.app = app
            
            # Initialize the extension system
            from .extension_system.registry import initialize_registry
            registry = initialize_registry()
            
            # Register API routes
            from .manager.api import create_router
            router = create_router(registry)
            self.app.include_router(router, prefix="/api/extensions", tags=["extensions"])
            
            # Register UI routes
            from .manager.ui import register_ui_routes
            self.app.add_route("/admin/extensions", self._extensions_route)
            self.app.add_route("/admin/extensions/{name}", self._extensions_detail_route)
            
            # Add extension manager to admin menu
            self._add_to_admin_menu()
            
            # Initialize extensions
            registry.initialize_all()
            
            # Register hooks for Open WebUI extension points
            self._register_hooks()
            
            logger.info("Open WebUI Extensions plugin initialized successfully.")
            self.initialized = True
        except Exception as e:
            logger.error(f"Error initializing Open WebUI Extensions plugin: {e}")
            raise
    
    async def _extensions_route(self, request):
        """Render the extensions manager page."""
        from fastapi.responses import HTMLResponse
        from .manager.ui import render_extensions_page
        return HTMLResponse(render_extensions_page())
        
    async def _extensions_detail_route(self, request, name: str):
        """Render the extension detail page."""
        from fastapi.responses import HTMLResponse
        from .manager.ui import render_extension_detail_page
        return HTMLResponse(render_extension_detail_page(name))
    
    def _add_to_admin_menu(self) -> None:
        """Add the extension manager to the admin menu."""
        try:
            # Method 1: Add directly to admin menu in app state (most common)
            if hasattr(self.app, "state") and hasattr(self.app.state, "admin_menu"):
                self.app.state.admin_menu.append({
                    "name": "Extensions",
                    "icon": "puzzle-piece", 
                    "url": "/admin/extensions"
                })
                logger.info("Added Extensions to admin menu in app.state.admin_menu")
                return
            
            # Method 2: Try to use a built-in function (if it exists)
            if hasattr(self.app, "add_admin_menu_item"):
                self.app.add_admin_menu_item("Extensions", "puzzle-piece", "/admin/extensions")
                logger.info("Added Extensions to admin menu using add_admin_menu_item")
                return
                
            # Method 3: Try to find admin menu in app extra data
            if hasattr(self.app, "extra") and "admin_menu" in self.app.extra:
                self.app.extra["admin_menu"].append({
                    "name": "Extensions",
                    "icon": "puzzle-piece",
                    "url": "/admin/extensions"
                })
                logger.info("Added Extensions to admin menu in app.extra")
                return
                
            # If all methods fail, try to inject into the frontend via middleware
            from fastapi.middleware.base import BaseHTTPMiddleware
            from fastapi.responses import Response
            
            class AdminMenuMiddleware(BaseHTTPMiddleware):
                async def dispatch(self, request, call_next):
                    response = await call_next(request)
                    
                    # Only modify HTML responses
                    if "text/html" in response.headers.get("content-type", ""):
                        content = response.body.decode()
                        # Find the admin menu area and inject our item
                        if "<nav" in content and "admin-nav" in content:
                            menu_item = """
                            <li>
                                <a href="/admin/extensions" class="flex items-center p-2 text-gray-900 rounded-lg dark:text-white hover:bg-gray-100 dark:hover:bg-gray-700 group">
                                    <svg class="w-5 h-5 text-gray-500 transition duration-75 dark:text-gray-400 group-hover:text-gray-900 dark:group-hover:text-white" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                                        <path d="M11 4a1 1 0 114 0v1a1 1 0 01-1 1h-2a1 1 0 01-1-1V4zM12 9a3 3 0 00-3 3m0 0a3 3 0 003 3m0 0a3 3 0 003-3m0 0a3 3 0 00-3-3"/>
                                        <path d="M19 9a1 1 0 110-2 1 1 0 010 2zm0 0a1 1 0 100 2 1 1 0 000-2z"/>
                                    </svg>
                                    <span class="ml-3">Extensions</span>
                                </a>
                            </li>
                            """
                            modified_content = content.replace("</ul>", f"{menu_item}</ul>", 1)
                            return Response(
                                content=modified_content.encode(),
                                status_code=response.status_code,
                                headers=dict(response.headers),
                                media_type=response.media_type
                            )
                    return response
            
            self.app.add_middleware(AdminMenuMiddleware)
            logger.info("Added Extensions to admin menu via middleware injection")
            
        except Exception as e:
            logger.error(f"Error adding Extensions to admin menu: {e}")
            logger.warning("The extension manager can be accessed at /admin/extensions")
    
    def _register_hooks(self) -> None:
        """Register hooks for Open WebUI extension points."""
        try:
            # Import our hooks system
            from .extension_system.hooks import execute_hook
            
            # Try to find hook points in Open WebUI
            # 1. Chat completion hooks
            if hasattr(self.app, "middleware"):
                # Register pre-processing middleware for chat payloads
                from fastapi.middleware.base import BaseHTTPMiddleware
                from fastapi.responses import Response
                
                class ExtensionMiddleware(BaseHTTPMiddleware):
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
                                    # This requires some FastAPI internals access
                                    request._body = modified_body
                            except Exception as e:
                                logger.error(f"Error in chat_pre_process hook: {e}")
                        
                        # Continue with the request
                        response = await call_next(request)
                        
                        # Post-process the response
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
                                    return Response(
                                        content=modified_body,
                                        status_code=response.status_code,
                                        headers=dict(response.headers),
                                        media_type=response.media_type
                                    )
                                
                                # Otherwise, rebuild the original response
                                return Response(
                                    content=body,
                                    status_code=response.status_code,
                                    headers=dict(response.headers),
                                    media_type=response.media_type
                                )
                            except Exception as e:
                                logger.error(f"Error in chat_post_process hook: {e}")
                                
                        return response
                
                self.app.add_middleware(ExtensionMiddleware)
                logger.info("Registered extension middleware for chat processing")

            # 2. UI initialization hooks
            # This is harder to inject without direct file access, but we can try 
            # to inject into the frontend via response manipulation
            from fastapi.middleware.base import BaseHTTPMiddleware
            from fastapi.responses import Response
            
            class UIHookMiddleware(BaseHTTPMiddleware):
                async def dispatch(self, request, call_next):
                    response = await call_next(request)
                    
                    # Only modify HTML responses to the main UI
                    if request.url.path == "/" and "text/html" in response.headers.get("content-type", ""):
                        content = response.body.decode()
                        
                        # Create JS that will load our UI components from our API
                        extension_loader = """
                        <script>
                            document.addEventListener('DOMContentLoaded', async () => {
                                try {
                                    // Load UI components from extensions
                                    const response = await fetch('/api/extensions/ui-components');
                                    if (response.ok) {
                                        const data = await response.json();
                                        
                                        // Process mount points
                                        if (data.components) {
                                            for (const mountPoint in data.components) {
                                                const components = data.components[mountPoint];
                                                const mountElement = document.querySelector(`[data-mount-point="${mountPoint}"]`);
                                                
                                                if (mountElement) {
                                                    // Create a container for extension components
                                                    const container = document.createElement('div');
                                                    container.className = 'extension-components';
                                                    
                                                    // Add each component
                                                    for (const component of components) {
                                                        const div = document.createElement('div');
                                                        div.className = 'extension-component';
                                                        div.innerHTML = component.html;
                                                        
                                                        // Execute any scripts in the component
                                                        const scripts = div.querySelectorAll('script');
                                                        scripts.forEach(oldScript => {
                                                            const newScript = document.createElement('script');
                                                            Array.from(oldScript.attributes).forEach(attr => {
                                                                newScript.setAttribute(attr.name, attr.value);
                                                            });
                                                            newScript.textContent = oldScript.textContent;
                                                            oldScript.parentNode.replaceChild(newScript, oldScript);
                                                        });
                                                        
                                                        container.appendChild(div);
                                                    }
                                                    
                                                    // Add to the mount point
                                                    mountElement.appendChild(container);
                                                }
                                            }
                                        }
                                        
                                        // Execute the ui_init hook to notify extensions
                                        fetch('/api/extensions/hooks/ui_init', { method: 'POST' });
                                    }
                                } catch (error) {
                                    console.error('Error loading extension components:', error);
                                }
                            });
                        </script>
                        """
                        
                        # Inject our script before the closing body tag
                        modified_content = content.replace("</body>", f"{extension_loader}</body>", 1)
                        
                        # Additionally, add mount points to key locations if they don't exist
                        if "<nav" in modified_content and not 'data-mount-point="sidebar"' in modified_content:
                            modified_content = modified_content.replace(
                                "<nav", 
                                '<div data-mount-point="sidebar"></div><nav', 
                                1
                            )
                            
                        if "<main" in modified_content and not 'data-mount-point="main"' in modified_content:
                            modified_content = modified_content.replace(
                                "<main", 
                                '<div data-mount-point="main"></div><main', 
                                1
                            )
                            
                        if "<footer" in modified_content and not 'data-mount-point="footer"' in modified_content:
                            modified_content = modified_content.replace(
                                "<footer", 
                                '<div data-mount-point="footer"></div><footer', 
                                1
                            )
                        
                        return Response(
                            content=modified_content.encode(),
                            status_code=response.status_code,
                            headers=dict(response.headers),
                            media_type=response.media_type
                        )
                    
                    return response
            
            self.app.add_middleware(UIHookMiddleware)
            logger.info("Registered UI hook middleware for extension components")
            
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
