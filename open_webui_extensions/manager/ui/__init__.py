"""
UI rendering for the extension manager.
"""

import os
from pathlib import Path
from typing import Dict, Any, List, Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape
from fastapi.responses import HTMLResponse

# Get the directory of this file
current_dir = os.path.dirname(os.path.abspath(__file__))

# Create a Jinja2 environment for loading templates
env = Environment(
    loader=FileSystemLoader(os.path.join(current_dir, "templates")),
    autoescape=select_autoescape(['html', 'xml'])
)


def register_ui_routes(app):
    """Register UI routes for the extension manager.
    
    Args:
        app: The FastAPI application.
    """
    @app.get("/admin/extensions")
    async def get_extensions_manager():
        """Render the extensions manager page."""
        return HTMLResponse(render_extensions_page())
    
    @app.get("/admin/extensions/{name}")
    async def get_extension_detail(name: str):
        """Render the extension detail page."""
        return HTMLResponse(render_extension_detail_page(name))


def render_extensions_page() -> str:
    """Render the extensions manager page.
    
    Returns:
        The HTML content of the extensions manager page.
    """
    # Use absolute import instead of relative
    from open_webui_extensions.extension_system.registry import get_registry
    
    # Get the extension registry
    registry = get_registry()
    
    # Get all extensions
    extensions = registry.list_extensions()
    
    # Render the template
    template = env.get_template("extensions.html")
    return template.render(extensions=extensions)


def render_extension_detail_page(name: str) -> str:
    """Render the extension detail page.
    
    Args:
        name: The name of the extension.
        
    Returns:
        The HTML content of the extension detail page.
    """
    # Use absolute import instead of relative
    from open_webui_extensions.extension_system.registry import get_registry
    
    # Get the extension registry
    registry = get_registry()
    
    # Get the extension
    extension_info = registry.get_extension_info(name)
    extension_instance = registry.get_extension_instance(name)
    
    # Render the template
    template = env.get_template("extension_detail.html")
    return template.render(
        extension_info=extension_info,
        extension_instance=extension_instance
    )
