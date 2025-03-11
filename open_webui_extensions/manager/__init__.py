"""
Extension manager for Open WebUI.
"""

from fastapi import FastAPI
from typing import Any, Dict

def create_manager(app: FastAPI) -> Dict[str, Any]:
    """Create the extension manager.
    
    Args:
        app: The FastAPI application.
        
    Returns:
        A dictionary containing the manager components.
    """
    # Initialize the extension system
    from ..extension_system.registry import initialize_registry
    registry = initialize_registry()
    
    # Create API router
    from .api import create_router
    router = create_router(registry)
    
    # Register API routes
    app.include_router(router, prefix="/api/extensions", tags=["extensions"])
    
    # Register UI routes
    from .ui import register_ui_routes
    register_ui_routes(app)
    
    return {
        "registry": registry,
        "router": router,
    }
