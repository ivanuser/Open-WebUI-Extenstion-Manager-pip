"""
API endpoints for the extension manager.
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Body
from typing import Any, Dict, List, Optional

from ..extension_system.registry import ExtensionRegistry


def create_router(registry: ExtensionRegistry) -> APIRouter:
    """Create the API router for the extension manager.
    
    Args:
        registry: The extension registry.
        
    Returns:
        The API router.
    """
    router = APIRouter()
    
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
    
    return router
