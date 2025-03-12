"""
API endpoints for the extension manager.
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Body, Request
from typing import Any, Dict, List, Optional

from open_webui_extensions.extension_system.registry import ExtensionRegistry
from open_webui_extensions.extension_system.hooks import execute_hook


def create_router(registry: ExtensionRegistry) -> APIRouter:
    """Create the API router for the extension manager.
    
    Args:
        registry: The extension registry.
        
    Returns:
        The API router.
    """
    router = APIRouter()
    
    # Handle root endpoint both with and without trailing slash
    @router.get("")
    @router.get("/")
    async def list_extensions():
        """List all extensions."""
        try:
            extensions = registry.list_extensions()
            return {
                "success": True,
                "extensions": [ext.to_dict() for ext in extensions],
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/{name}")
    async def get_extension(name: str):
        """Get information about an extension."""
        try:
            extension = registry.get_extension_info(name)
            if not extension:
                return {
                    "success": False,
                    "message": f"Extension {name} not found",
                }
            
            return {
                "success": True,
                "extension": extension.to_dict(),
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.post("/install")
    async def install_extension(source: str = Body(..., embed=True)):
        """Install an extension."""
        try:
            success, name, message = registry.install_extension(source)
            
            if success and name:
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
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.post("/uninstall")
    async def uninstall_extension(name: str = Body(..., embed=True)):
        """Uninstall an extension."""
        try:
            success, message = registry.uninstall_extension(name)
            
            return {
                "success": success,
                "message": message,
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.post("/enable")
    async def enable_extension(name: str = Body(..., embed=True)):
        """Enable an extension."""
        try:
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
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.post("/disable")
    async def disable_extension(name: str = Body(..., embed=True)):
        """Disable an extension."""
        try:
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
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.post("/settings")
    async def update_settings(
        name: str = Body(...),
        settings: Dict[str, Any] = Body(...),
    ):
        """Update extension settings."""
        try:
            success, message = registry.update_extension_settings(name, settings)
            
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
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.post("/discover")
    async def discover_extensions():
        """Discover installed extensions."""
        try:
            extensions = registry.discover()
            
            return {
                "success": True,
                "message": f"Discovered {len(extensions)} extensions",
                "extensions": [ext.to_dict() for ext in extensions.values()],
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.post("/initialize")
    async def initialize_extensions():
        """Initialize all extensions."""
        try:
            results = registry.initialize_all()
            
            # Count successes and failures
            successes = sum(1 for success, _ in results.values() if success)
            failures = len(results) - successes
            
            return {
                "success": failures == 0,
                "message": f"Initialized {successes} extensions successfully, {failures} failed",
                "results": {name: {"success": success, "message": message} for name, (success, message) in results.items()},
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/ui-components")
    async def get_ui_components():
        """Get UI components from all extensions."""
        try:
            # Organize components by mount point
            mount_points = {}
            
            # Get all active extensions
            extensions = [ext for ext in registry.list_extensions() if ext.active]
            
            for ext_info in extensions:
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
                                    # Log error but continue with other components
                                    print(f"Error rendering component {component_id} from {ext_info.name}: {e}")
            
            return {
                "success": True,
                "components": mount_points,
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.post("/hooks/{hook_name}")
    async def execute_hook_endpoint(hook_name: str, request: Request):
        """Execute a hook."""
        try:
            # Get request body if any
            body = await request.body()
            data = body if body else None
            
            # Execute the hook
            result = await execute_hook(hook_name, data)
            
            return {
                "success": True,
                "hook": hook_name,
                "result": result if result is not None else "Hook executed",
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
            
    return router
