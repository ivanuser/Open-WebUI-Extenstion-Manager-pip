"""
Plugin interface for Open WebUI.

This module provides direct integration with Open WebUI application.
"""

import os
import logging
import importlib
from pathlib import Path
from typing import Any, Dict, List, Optional, Type

from fastapi import FastAPI
from fastapi.middleware.base import BaseHTTPMiddleware
from fastapi.responses import Response, HTMLResponse

logger = logging.getLogger("webui-extensions.plugin")

class OpenWebUIExtensionMiddleware(BaseHTTPMiddleware):
    """Middleware to inject extension UI elements into Open WebUI."""
    
    async def dispatch(self, request, call_next):
        # Pass through request to Open WebUI
        response = await call_next(request)
        
        # Check if this is a request for the admin interface
        if request.url.path.startswith("/admin") and "text/html" in response.headers.get("content-type", ""):
            content = response.body.decode()
            
            # Inject our extension menu item
            if "<ul" in content and "sidebar-menu" in content:
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
        
        # For the main UI, inject our extension mount points and loader script
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
            
            # Register UI routes
            @self.app.get("/admin/extensions")
            async def get_extensions_manager():
                from open_webui_extensions.manager.ui import render_extensions_page
                return HTMLResponse(render_extensions_page())
            
            @self.app.get("/admin/extensions/{name}")
            async def get_extension_detail(name: str):
                from open_webui_extensions.manager.ui import render_extension_detail_page
                return HTMLResponse(render_extension_detail_page(name))
            
            # Add middleware for UI integration
            self.app.add_middleware(OpenWebUIExtensionMiddleware)
            
            # Add extension manager to admin menu (for backward compatibility)
            self._add_to_admin_menu()
            
            # Initialize extensions
            registry.initialize_all()
            
            # Register chat hooks
            self._register_chat_hooks()
            
            logger.info("Open WebUI Extensions plugin initialized successfully.")
            self.initialized = True
            return True
        except Exception as e:
            logger.error(f"Error initializing Open WebUI Extensions plugin: {e}")
            return False
    
    def _add_to_admin_menu(self) -> None:
        """Add the extension manager to the admin menu."""
        try:
            # This is now handled by the middleware, but we'll keep this
            # for backward compatibility
            if hasattr(self.app, "state") and hasattr(self.app.state, "admin_menu"):
                self.app.state.admin_menu.append({
                    "name": "Extensions",
                    "icon": "puzzle-piece", 
                    "url": "/admin/extensions"
                })
                logger.info("Added Extensions to admin menu in app.state.admin_menu")
            
        except Exception as e:
            logger.error(f"Error adding Extensions to admin menu: {e}")
    
    def _register_chat_hooks(self) -> None:
        """Register hooks for chat processing."""
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
            
            # Add the middleware
            self.app.add_middleware(ChatMiddleware)
            logger.info("Registered chat middleware for extension hooks")
            
        except Exception as e:
            logger.error(f"Error registering chat hooks: {e}")
    
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
    plugin.initialize(app)
    return app
