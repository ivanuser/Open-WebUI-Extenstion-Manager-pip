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
            register_ui_routes(self.app)
            
            # Add extension manager to admin menu
            self._add_to_admin_menu()
            
            # Initialize extensions
            registry.initialize_all()
            
            logger.info("Open WebUI Extensions plugin initialized successfully.")
            self.initialized = True
        except Exception as e:
            logger.error(f"Error initializing Open WebUI Extensions plugin: {e}")
            raise
    
    def _add_to_admin_menu(self) -> None:
        """Add the extension manager to the admin menu."""
        try:
            # Try to find Open WebUI's admin menu registration function
            # This is a bit of a hack since we don't know exactly how Open WebUI
            # is structured, so we're using some runtime introspection
            
            # Method 1: Try to find admin menu through app state
            if hasattr(self.app, "state") and hasattr(self.app.state, "admin_menu"):
                self.app.state.admin_menu.append({
                    "name": "Extensions",
                    "icon": "puzzle-piece",
                    "url": "/admin/extensions"
                })
                return
            
            # Method 2: Try to use an extension point if it exists
            try:
                # Look for an extension point or event system
                if hasattr(self.app, "add_admin_menu_item"):
                    self.app.add_admin_menu_item("Extensions", "puzzle-piece", "/admin/extensions")
                    return
                
                # Method 3: Try to find admin menu in app metadata
                if hasattr(self.app, "extra") and "admin_menu" in self.app.extra:
                    self.app.extra["admin_menu"].append({
                        "name": "Extensions",
                        "icon": "puzzle-piece",
                        "url": "/admin/extensions"
                    })
                    return
            except:
                pass
            
            # If we couldn't find a way to add to the admin menu,
            # we'll just log a warning and continue
            logger.warning("Could not add extensions to admin menu. "
                        "You can access the extension manager at /admin/extensions")
                        
        except Exception as e:
            logger.error(f"Error adding to admin menu: {e}")
    
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
