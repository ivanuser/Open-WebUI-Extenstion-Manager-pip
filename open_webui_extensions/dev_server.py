"""
Development server for testing extensions.
"""

import os
import sys
import argparse
import logging
import importlib
import uvicorn
from pathlib import Path
from typing import Any, Dict, List

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .config import get_dev_server_host, get_dev_server_port
from .extension_system.registry import initialize_registry, get_registry

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger("webui-extensions.dev-server")

app = FastAPI(title="Open WebUI Extensions Dev Server")

# Get templates directory
templates_dir = Path(__file__).parent / "manager" / "ui" / "templates"
if not templates_dir.exists():
    templates_dir = Path(__file__).parent / "dev_server_templates"
    templates_dir.mkdir(exist_ok=True)
    
    # Create a basic template
    index_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Open WebUI Extensions Dev Server</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                margin: 0;
                padding: 2rem;
                max-width: 1200px;
                margin: 0 auto;
            }
            
            .extension-card {
                border: 1px solid #ccc;
                border-radius: 0.5rem;
                padding: 1rem;
                margin-bottom: 1rem;
            }
            
            .extension-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 1rem;
            }
            
            .extension-meta {
                margin-bottom: 1rem;
                color: #666;
            }
            
            .extension-actions {
                display: flex;
                gap: 0.5rem;
            }
            
            .btn {
                padding: 0.5rem 1rem;
                border-radius: 0.25rem;
                cursor: pointer;
                border: none;
                background-color: #f0f0f0;
            }
            
            .btn-primary {
                background-color: #007bff;
                color: white;
            }
            
            .btn-danger {
                background-color: #dc3545;
                color: white;
            }
            
            .active-badge, .inactive-badge {
                padding: 0.25rem 0.5rem;
                border-radius: 0.25rem;
                font-size: 0.8rem;
            }
            
            .active-badge {
                background-color: #28a745;
                color: white;
            }
            
            .inactive-badge {
                background-color: #6c757d;
                color: white;
            }
            
            .mount-point {
                margin-top: 2rem;
                border: 1px solid #ccc;
                border-radius: 0.5rem;
                padding: 1rem;
            }
            
            .mount-point-header {
                margin-bottom: 1rem;
                padding-bottom: 0.5rem;
                border-bottom: 1px solid #eee;
            }
        </style>
    </head>
    <body>
        <h1>Open WebUI Extensions Dev Server</h1>
        
        <div id="extensions-container">
            <h2>Installed Extensions</h2>
            <div id="extension-list">Loading extensions...</div>
        </div>
        
        <div class="mount-point">
            <div class="mount-point-header">
                <h2>Sidebar Mount Point</h2>
            </div>
            <div id="sidebar-mount-point"></div>
        </div>
        
        <div class="mount-point">
            <div class="mount-point-header">
                <h2>Chat Mount Point</h2>
            </div>
            <div id="chat-mount-point"></div>
        </div>
        
        <script>
            // Load extensions
            async function loadExtensions() {
                try {
                    const response = await fetch('/api/extensions/');
                    const data = await response.json();
                    
                    const extensionList = document.getElementById('extension-list');
                    
                    if (data.success && data.extensions && data.extensions.length > 0) {
                        extensionList.innerHTML = '';
                        
                        data.extensions.forEach(extension => {
                            const card = document.createElement('div');
                            card.className = 'extension-card';
                            
                            card.innerHTML = `
                                <div class="extension-header">
                                    <h3>${extension.name} <small>v${extension.version}</small></h3>
                                    <span class="${extension.active ? 'active-badge' : 'inactive-badge'}">
                                        ${extension.active ? 'Active' : 'Inactive'}
                                    </span>
                                </div>
                                <div class="extension-meta">
                                    <p>${extension.description}</p>
                                    <p>Author: ${extension.author}</p>
                                    <p>Type: ${extension.type}</p>
                                </div>
                                <div class="extension-actions">
                                    ${extension.active 
                                        ? '<button class="btn" onclick="disableExtension(\'' + extension.name + '\')">Disable</button>' 
                                        : '<button class="btn btn-primary" onclick="enableExtension(\'' + extension.name + '\')">Enable</button>'}
                                    <button class="btn" onclick="reloadExtension(\'' + extension.name + '\')">Reload</button>
                                </div>
                            `;
                            
                            extensionList.appendChild(card);
                        });
                        
                        // Load mount points
                        loadMountPoints();
                    } else {
                        extensionList.innerHTML = '<p>No extensions found.</p>';
                    }
                } catch (error) {
                    document.getElementById('extension-list').innerHTML = `<p>Error loading extensions: ${error.message}</p>`;
                }
            }
            
            // Load mount points
            async function loadMountPoints() {
                try {
                    const response = await fetch('/api/extensions/mount-points');
                    const data = await response.json();
                    
                    if (data.success) {
                        // Load sidebar components
                        const sidebarMountPoint = document.getElementById('sidebar-mount-point');
                        sidebarMountPoint.innerHTML = '';
                        
                        if (data.mount_points.sidebar && data.mount_points.sidebar.length > 0) {
                            data.mount_points.sidebar.forEach(component => {
                                const componentDiv = document.createElement('div');
                                componentDiv.className = 'component';
                                componentDiv.innerHTML = component.html;
                                sidebarMountPoint.appendChild(componentDiv);
                            });
                        } else {
                            sidebarMountPoint.innerHTML = '<p>No sidebar components.</p>';
                        }
                        
                        // Load chat components
                        const chatMountPoint = document.getElementById('chat-mount-point');
                        chatMountPoint.innerHTML = '';
                        
                        if (data.mount_points.chat && data.mount_points.chat.length > 0) {
                            data.mount_points.chat.forEach(component => {
                                const componentDiv = document.createElement('div');
                                componentDiv.className = 'component';
                                componentDiv.innerHTML = component.html;
                                chatMountPoint.appendChild(componentDiv);
                            });
                        } else {
                            chatMountPoint.innerHTML = '<p>No chat components.</p>';
                        }
                    }
                } catch (error) {
                    console.error('Error loading mount points:', error);
                }
            }
            
            // Enable extension
            async function enableExtension(name) {
                try {
                    const response = await fetch('/api/extensions/enable', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ name })
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        loadExtensions();
                    } else {
                        alert(`Failed to enable extension: ${data.message}`);
                    }
                } catch (error) {
                    alert(`Error: ${error.message}`);
                }
            }
            
            // Disable extension
            async function disableExtension(name) {
                try {
                    const response = await fetch('/api/extensions/disable', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ name })
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        loadExtensions();
                    } else {
                        alert(`Failed to disable extension: ${data.message}`);
                    }
                } catch (error) {
                    alert(`Error: ${error.message}`);
                }
            }
            
            // Reload extension
            async function reloadExtension(name) {
                try {
                    const response = await fetch('/api/extensions/reload', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ name })
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        loadExtensions();
                    } else {
                        alert(`Failed to reload extension: ${data.message}`);
                    }
                } catch (error) {
                    alert(`Error: ${error.message}`);
                }
            }
            
            // Initial load
            document.addEventListener('DOMContentLoaded', loadExtensions);
        </script>
    </body>
    </html>
    """
    
    (templates_dir / "index.html").write_text(index_html)

templates = Jinja2Templates(directory=str(templates_dir))

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Root endpoint."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/extensions/")
async def list_extensions():
    """List all extensions."""
    try:
        registry = get_registry()
        extensions = registry.list_extensions()
        
        return {
            "success": True,
            "extensions": [ext.to_dict() for ext in extensions],
        }
    except Exception as e:
        logger.error(f"Error listing extensions: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": str(e)},
        )

@app.post("/api/extensions/enable")
async def enable_extension(request: Request):
    """Enable an extension."""
    try:
        data = await request.json()
        name = data.get("name")
        
        if not name:
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": "Extension name is required"},
            )
        
        registry = get_registry()
        success, message = registry.enable_extension(name)
        
        if success:
            extension = registry.get_extension_info(name)
            return {
                "success": success,
                "message": message,
                "extension": extension.to_dict() if extension else None,
            }
        else:
            return {
                "success": success,
                "message": message,
            }
    except Exception as e:
        logger.error(f"Error enabling extension: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": str(e)},
        )

@app.post("/api/extensions/disable")
async def disable_extension(request: Request):
    """Disable an extension."""
    try:
        data = await request.json()
        name = data.get("name")
        
        if not name:
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": "Extension name is required"},
            )
        
        registry = get_registry()
        success, message = registry.disable_extension(name)
        
        if success:
            extension = registry.get_extension_info(name)
            return {
                "success": success,
                "message": message,
                "extension": extension.to_dict() if extension else None,
            }
        else:
            return {
                "success": success,
                "message": message,
            }
    except Exception as e:
        logger.error(f"Error disabling extension: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": str(e)},
        )

@app.post("/api/extensions/reload")
async def reload_extension(request: Request):
    """Reload an extension."""
    try:
        data = await request.json()
        name = data.get("name")
        
        if not name:
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": "Extension name is required"},
            )
        
        registry = get_registry()
        
        # Disable the extension if it's active
        info = registry.get_extension_info(name)
        if info and info.active:
            registry.disable_extension(name)
        
        # Reload the extension
        registry.discover()
        
        # Re-enable the extension if it was active before
        if info and info.active:
            success, message = registry.enable_extension(name)
        else:
            success, message = True, f"Extension {name} reloaded successfully"
        
        if success:
            extension = registry.get_extension_info(name)
            return {
                "success": success,
                "message": message,
                "extension": extension.to_dict() if extension else None,
            }
        else:
            return {
                "success": success,
                "message": message,
            }
    except Exception as e:
        logger.error(f"Error reloading extension: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": str(e)},
        )

@app.get("/api/extensions/mount-points")
async def get_mount_points():
    """Get components for all mount points."""
    try:
        registry = get_registry()
        extensions = registry.list_extensions()
        
        # Dictionary to store components by mount point
        mount_points = {
            "sidebar": [],
            "header": [],
            "footer": [],
            "chat": [],
            "settings": [],
        }
        
        # Collect components from active extensions
        for ext_info in extensions:
            if not ext_info.active:
                continue
            
            ext = registry.get_extension_instance(ext_info.name)
            if not ext:
                continue
            
            # Check if the extension has components and mount points
            if hasattr(ext, "components") and hasattr(ext, "mount_points"):
                components = ext.components
                mount_points_map = ext.mount_points
                
                # Add components to their mount points
                for mount_point, component_ids in mount_points_map.items():
                    if mount_point not in mount_points:
                        mount_points[mount_point] = []
                    
                    for component_id in component_ids:
                        if component_id in components:
                            render_func = components[component_id]
                            try:
                                component_html = render_func()
                                if isinstance(component_html, dict) and "html" in component_html:
                                    mount_points[mount_point].append({
                                        "extension": ext_info.name,
                                        "component_id": component_id,
                                        "html": component_html["html"],
                                    })
                            except Exception as e:
                                logger.error(f"Error rendering component {component_id} from {ext_info.name}: {e}")
        
        return {
            "success": True,
            "mount_points": mount_points,
        }
    except Exception as e:
        logger.error(f"Error getting mount points: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": str(e)},
        )

def get_parser():
    """Get the argument parser."""
    parser = argparse.ArgumentParser(description="Open WebUI Extensions development server")
    
    parser.add_argument(
        "--host",
        help="Host to run the server on (default: localhost)",
        default=None,
    )
    
    parser.add_argument(
        "--port",
        type=int,
        help="Port to run the server on (default: 5000)",
        default=None,
    )
    
    parser.add_argument(
        "--extensions-dir",
        help="Directory containing extensions",
        default=None,
    )
    
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload",
        default=True,
    )
    
    return parser

def main():
    """Run the development server."""
    parser = get_parser()
    args = parser.parse_args()
    
    # Initialize the extension registry
    extensions_dir = args.extensions_dir
    initialize_registry(extensions_dir)
    
    # Get host and port
    host = args.host or get_dev_server_host()
    port = args.port or get_dev_server_port()
    
    # Run the server
    print(f"Starting development server at http://{host}:{port}")
    uvicorn.run("open_webui_extensions.dev_server:app", host=host, port=port, reload=args.reload)

if __name__ == "__main__":
    main()
