"""
UI components for the extension manager.
"""

import os
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


# Get the path to the UI templates
_templates_dir = Path(__file__).parent / "templates"
_static_dir = Path(__file__).parent / "static"

# Create the templates object
if _templates_dir.exists():
    templates = Jinja2Templates(directory=str(_templates_dir))
else:
    # Create the directory and a basic template
    _templates_dir.mkdir(parents=True, exist_ok=True)
    (_templates_dir / "index.html").write_text("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Extension Manager</title>
        <link rel="stylesheet" href="/api/extensions/ui/static/styles.css">
    </head>
    <body>
        <div id="extension-manager-app"></div>
        <script src="/api/extensions/ui/static/main.js"></script>
    </body>
    </html>
    """)
    templates = Jinja2Templates(directory=str(_templates_dir))

# Create the static directory if it doesn't exist
if not _static_dir.exists():
    _static_dir.mkdir(parents=True, exist_ok=True)
    
    # Create a basic CSS file
    (_static_dir / "styles.css").write_text("""
    body {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        margin: 0;
        padding: 0;
    }
    
    #extension-manager-app {
        max-width: 1200px;
        margin: 0 auto;
        padding: 2rem;
    }
    """)
    
    # Create a basic JavaScript file
    (_static_dir / "main.js").write_text("""
    // Main extension manager script
    document.addEventListener('DOMContentLoaded', () => {
        const app = document.getElementById('extension-manager-app');
        
        app.innerHTML = `
            <h1>Extension Manager</h1>
            <div id="extension-list"></div>
            <div id="extension-controls">
                <button id="refresh-btn">Refresh</button>
                <button id="install-btn">Install Extension</button>
            </div>
            <div id="install-form" style="display: none;">
                <h2>Install Extension</h2>
                <form id="install-extension-form">
                    <div class="form-group">
                        <label for="extension-source">Source:</label>
                        <input type="text" id="extension-source" required placeholder="URL or local path">
                    </div>
                    <div class="form-actions">
                        <button type="button" id="cancel-install-btn">Cancel</button>
                        <button type="submit">Install</button>
                    </div>
                </form>
            </div>
        `;
        
        const extensionList = document.getElementById('extension-list');
        const refreshBtn = document.getElementById('refresh-btn');
        const installBtn = document.getElementById('install-btn');
        const installForm = document.getElementById('install-form');
        const cancelInstallBtn = document.getElementById('cancel-install-btn');
        const installExtensionForm = document.getElementById('install-extension-form');
        
        // Load extensions
        async function loadExtensions() {
            try {
                const response = await fetch('/api/extensions/');
                const data = await response.json();
                
                if (data.success) {
                    renderExtensions(data.extensions);
                } else {
                    extensionList.innerHTML = `<div class="error">${data.message || 'Failed to load extensions'}</div>`;
                }
            } catch (error) {
                extensionList.innerHTML = `<div class="error">Error: ${error.message}</div>`;
            }
        }
        
        // Render extensions
        function renderExtensions(extensions) {
            if (!extensions || extensions.length === 0) {
                extensionList.innerHTML = '<div class="empty-state">No extensions installed</div>';
                return;
            }
            
            extensionList.innerHTML = '';
            
            extensions.forEach(ext => {
                const card = document.createElement('div');
                card.className = 'extension-card';
                card.dataset.name = ext.name;
                
                card.innerHTML = `
                    <div class="extension-card-header">
                        <h3>${ext.name}</h3>
                        <span class="version">v${ext.version}</span>
                        <span class="status ${ext.active ? 'active' : 'inactive'}">${ext.active ? 'Active' : 'Inactive'}</span>
                    </div>
                    <div class="extension-card-body">
                        <p>${ext.description}</p>
                        <div class="extension-meta">
                            <span class="author">By ${ext.author}</span>
                            <span class="type">${ext.type}</span>
                        </div>
                    </div>
                    <div class="extension-card-actions">
                        ${ext.active 
                            ? '<button class="disable-btn">Disable</button>' 
                            : '<button class="enable-btn">Enable</button>'}
                        <button class="settings-btn">Settings</button>
                        <button class="uninstall-btn">Uninstall</button>
                    </div>
                `;
                
                extensionList.appendChild(card);
                
                // Add event listeners
                card.querySelector('.enable-btn')?.addEventListener('click', () => enableExtension(ext.name));
                card.querySelector('.disable-btn')?.addEventListener('click', () => disableExtension(ext.name));
                card.querySelector('.settings-btn')?.addEventListener('click', () => showSettings(ext));
                card.querySelector('.uninstall-btn')?.addEventListener('click', () => uninstallExtension(ext.name));
            });
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
        
        // Uninstall extension
        async function uninstallExtension(name) {
            if (!confirm(`Are you sure you want to uninstall ${name}?`)) {
                return;
            }
            
            try {
                const response = await fetch('/api/extensions/uninstall', {
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
                    alert(`Failed to uninstall extension: ${data.message}`);
                }
            } catch (error) {
                alert(`Error: ${error.message}`);
            }
        }
        
        // Show settings
        function showSettings(extension) {
            alert('Settings not implemented yet');
        }
        
        // Install extension
        async function installExtension(source) {
            try {
                const response = await fetch('/api/extensions/install', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ source })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    loadExtensions();
                    installForm.style.display = 'none';
                } else {
                    alert(`Failed to install extension: ${data.message}`);
                }
            } catch (error) {
                alert(`Error: ${error.message}`);
            }
        }
        
        // Event listeners
        refreshBtn.addEventListener('click', loadExtensions);
        
        installBtn.addEventListener('click', () => {
            installForm.style.display = 'block';
        });
        
        cancelInstallBtn.addEventListener('click', () => {
            installForm.style.display = 'none';
        });
        
        installExtensionForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const source = document.getElementById('extension-source').value;
            installExtension(source);
        });
        
        // Initial load
        loadExtensions();
    });
    """)


def register_ui_routes(app: FastAPI) -> None:
    """Register UI routes for the extension manager.
    
    Args:
        app: The FastAPI application.
    """
    # Mount static files
    app.mount(
        "/api/extensions/ui/static",
        StaticFiles(directory=str(_static_dir)),
        name="extension_manager_static",
    )
    
    # Register the main UI route
    @app.get("/admin/extensions", response_class=HTMLResponse)
    async def extension_manager_ui(request: Request):
        """Render the extension manager UI."""
        return templates.TemplateResponse("index.html", {"request": request})
