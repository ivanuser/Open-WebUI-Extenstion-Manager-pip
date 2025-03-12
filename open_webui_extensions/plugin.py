"""
Plugin interface for Open WebUI.

This module provides API integration with Open WebUI application.
"""

import os
import logging
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
    
    This class provides API integration with the Open WebUI application.
    """
    
    def __init__(self):
        """Initialize the plugin."""
        self.app = None
        self.initialized = False
    
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
            
            # Initialize extensions
            registry.initialize_all()
            
            # Register hooks if middleware is available
            if HAS_MIDDLEWARE:
                self._register_hooks()
            
            logger.info("Open WebUI Extensions plugin initialized successfully.")
            logger.info("API available at /api/extensions")
            logger.info("Use separate extension manager at http://localhost:5000/admin/extensions")
            
            self.initialized = True
            return True
        except Exception as e:
            logger.error(f"Error initializing Open WebUI Extensions plugin: {e}")
            return False
    
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
