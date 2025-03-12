"""
Development server for testing extensions outside Open WebUI.
"""

import os
import sys
import importlib.util
import logging
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path

import uvicorn
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .extension_system.registry import initialize_registry
from .manager.api import create_router
from .manager.ui import register_ui_routes

logger = logging.getLogger("webui-extensions.dev-server")

def create_dev_app() -> FastAPI:
    """Create a development application for testing extensions.
    
    Returns:
        The FastAPI application.
    """
    app = FastAPI(
        title="Open WebUI Extensions Development Server",
        description="Development server for testing Open WebUI extensions.",
        version="0.1.0",
    )
    
    # Initialize the extension registry
    registry = initialize_registry()
    
    # Register extension manager API routes
    router = create_router(registry)
    app.include_router(router, prefix="/api/extensions", tags=["extensions"])
    
    # Register extension manager UI routes
    register_ui_routes(app)
    
    # Mount static files
    static_dir = os.path.join(os.path.dirname(__file__), "manager", "ui", "static")
    if os.path.exists(static_dir):
        app.mount("/static", StaticFiles(directory=static_dir), name="static")
    
    @app.get("/")
    async def index():
        """Redirect to the extensions manager."""
        return Response(status_code=307, headers={"Location": "/admin/extensions"})
    
    @app.get("/mock-mountpoint")
    async def mock_mountpoint():
        """A mock page that renders components from extensions."""
        # Get UI components from extensions
        extensions = registry.list_extensions()
        
        mount_points = {
            "sidebar": [],
            "chat": [],
            "main": [],
            "footer": [],
        }
        
        for ext_info in extensions:
            if not ext_info.active:
                continue
            
            # Get the extension instance
            extension = registry.get_extension_instance(ext_info.name)
            
            # Skip non-UI extensions
            if not extension or extension.type != "ui":
                continue
            
            # Get the mount points and components
            if hasattr(extension, "mount_points") and hasattr(extension, "components"):
                for mount_point, components in extension.mount_points.items():
                    if mount_point not in mount_points:
                        mount_points[mount_point] = []
                    
                    for component_id in components:
                        if component_id in extension.components:
                            # Get the component renderer function
                            renderer = extension.components[component_id]
                            
                            # Try to render the component
                            try:
                                if callable(renderer):
                                    component_data = renderer()
                                    
                                    # If the renderer returns a dictionary with HTML, add it
                                    if isinstance(component_data, dict) and "html" in component_data:
                                        mount_points[mount_point].append({
                                            "id": component_id,
                                            "extension": ext_info.name,
                                            "html": component_data["html"],
                                        })
                            except Exception as e:
                                logger.error(f"Error rendering component {component_id} from {ext_info.name}: {e}")
        
        # Render the page
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Open WebUI Mock Interface</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                    line-height: 1.5;
                    padding: 0;
                    margin: 0;
                }}
                
                .layout {{
                    display: grid;
                    grid-template-columns: 300px 1fr;
                    grid-template-rows: 1fr auto;
                    grid-template-areas:
                        "sidebar main"
                        "footer footer";
                    height: 100vh;
                }}
                
                .sidebar {{
                    grid-area: sidebar;
                    background-color: #f5f5f5;
                    border-right: 1px solid #e0e0e0;
                    padding: 1rem;
                    overflow-y: auto;
                }}
                
                .main {{
                    grid-area: main;
                    padding: 1rem;
                    overflow-y: auto;
                }}
                
                .footer {{
                    grid-area: footer;
                    background-color: #f5f5f5;
                    border-top: 1px solid #e0e0e0;
                    padding: 1rem;
                }}
                
                .chat {{
                    border: 1px solid #e0e0e0;
                    border-radius: 0.5rem;
                    padding: 1rem;
                    margin-bottom: 1rem;
                }}
                
                h1, h2, h3 {{
                    margin-top: 0;
                }}
            </style>
        </head>
        <body>
            <div class="layout">
                <div class="sidebar">
                    <h2>Sidebar</h2>
                    <div data-mount-point="sidebar">
                        {''.join([component["html"] for component in mount_points["sidebar"]])}
                    </div>
                </div>
                
                <div class="main">
                    <h1>Mock Interface</h1>
                    <p>This page simulates the Open WebUI interface for testing extensions.</p>
                    
                    <div data-mount-point="main">
                        {''.join([component["html"] for component in mount_points["main"]])}
                    </div>
                    
                    <h2>Chat Interface</h2>
                    <div class="chat">
                        <div data-mount-point="chat">
                            {''.join([component["html"] for component in mount_points["chat"]])}
                        </div>
                    </div>
                </div>
                
                <div class="footer">
                    <div data-mount-point="footer">
                        {''.join([component["html"] for component in mount_points["footer"]])}
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        return HTMLResponse(content=html)
    
    # Execute the UI init hook to notify extensions
    from .extension_system.hooks import execute_hook
    import asyncio
    
    @app.on_event("startup")
    async def startup_event():
        # Get all extensions
        registry.discover()
        
        # Initialize extensions
        registry.initialize_all()
        
        # Execute the UI init hook
        await execute_hook("ui_init")
    
    return app

def run_dev_server(host: str = "localhost", port: int = 5000, reload: bool = True) -> None:
    """Run the development server.
    
    Args:
        host: The host to bind to.
        port: The port to bind to.
        reload: Whether to enable auto-reload.
    """
    # Create the app
    app = create_dev_app()
    
    # Run the server
    uvicorn.run(
        "open_webui_extensions.dev_server:create_dev_app",
        host=host,
        port=port,
        reload=reload,
    )

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Parse command line arguments
    import argparse
    
    parser = argparse.ArgumentParser(description="Open WebUI Extensions Development Server")
    parser.add_argument("--host", default="localhost", help="The host to bind to")
    parser.add_argument("--port", type=int, default=5000, help="The port to bind to")
    parser.add_argument("--no-reload", action="store_true", help="Disable auto-reload")
    
    args = parser.parse_args()
    
    # Run the server
    run_dev_server(host=args.host, port=args.port, reload=not args.no_reload)
