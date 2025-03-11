"""
Registry for managing extensions.
"""

import os
import json
import logging
import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Type
import threading

from .base import Extension
from .utils import (
    load_extension,
    discover_extensions,
    install_from_directory,
    install_from_zip,
    install_from_url,
    setup_extensions_directory,
)
from .decorators import register_hooks_from_instance

logger = logging.getLogger("webui-extensions.registry")

class ExtensionInfo:
    """Information about an extension."""
    
    def __init__(self, name: str, version: str, description: str, author: str, 
                 type: str = "generic", path: Optional[str] = None,
                 active: bool = False, dependencies: List[str] = None,
                 settings: Dict[str, Any] = None):
        self.name = name
        self.version = version
        self.description = description
        self.author = author
        self.type = type
        self.path = path
        self.active = active
        self.dependencies = dependencies or []
        self.settings = settings or {}
        self.install_date = datetime.datetime.now().isoformat()
        self.update_date = self.install_date
        self.error = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dictionary."""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "type": self.type,
            "path": self.path,
            "active": self.active,
            "dependencies": self.dependencies,
            "settings": self.settings,
            "install_date": self.install_date,
            "update_date": self.update_date,
            "error": self.error,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExtensionInfo":
        """Create from a dictionary."""
        info = cls(
            name=data["name"],
            version=data["version"],
            description=data["description"],
            author=data["author"],
            type=data.get("type", "generic"),
            path=data.get("path"),
            active=data.get("active", False),
            dependencies=data.get("dependencies", []),
            settings=data.get("settings", {}),
        )
        info.install_date = data.get("install_date", info.install_date)
        info.update_date = data.get("update_date", info.update_date)
        info.error = data.get("error")
        return info
    
    @classmethod
    def from_extension(cls, extension: Extension, path: Optional[str] = None) -> "ExtensionInfo":
        """Create from an extension instance."""
        # Get settings in the right format
        settings = {}
        for key, value in extension.settings.items():
            if isinstance(value, dict):
                settings[key] = value
            else:
                settings[key] = {
                    "name": key,
                    "default": value,
                    "value": value,
                    "type": type(value).__name__ if value is not None else "str",
                    "description": f"Setting for {key}",
                }
        
        return cls(
            name=extension.name,
            version=extension.version,
            description=extension.description,
            author=extension.author,
            type=extension.type,
            path=path,
            dependencies=extension.dependencies,
            settings=settings,
        )


class ExtensionRegistry:
    """Registry for managing extensions."""
    
    _instance = None
    _lock = threading.RLock()
    
    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(ExtensionRegistry, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance
    
    def __init__(self, extensions_dir: Optional[str] = None):
        """Initialize the registry.
        
        Args:
            extensions_dir: The directory containing extensions.
        """
        with self._lock:
            if self._initialized:
                return
            
            if extensions_dir is None:
                # Try to find a suitable extensions directory
                extensions_dir = os.environ.get("OPENWEBUI_EXTENSIONS_DIR")
                if extensions_dir is None:
                    # Try common locations
                    for path in [
                        os.path.join(Path.home(), ".openwebui", "extensions"),
                        os.path.join(Path.home(), ".config", "openwebui", "extensions"),
                        "./extensions",
                    ]:
                        if os.path.exists(path):
                            extensions_dir = path
                            break
                    
                    if extensions_dir is None:
                        # Create a default location
                        extensions_dir = os.path.join(Path.home(), ".openwebui", "extensions")
            
            self.extensions_dir = setup_extensions_directory(extensions_dir)
            self.registry_file = os.path.join(self.extensions_dir, "registry.json")
            
            # Initialize internal state
            self.extensions: Dict[str, ExtensionInfo] = {}
            self.instances: Dict[str, Extension] = {}
            
            # Load the registry
            self._load_registry()
            
            self._initialized = True
    
    def _load_registry(self) -> None:
        """Load the registry from the registry file."""
        try:
            if os.path.exists(self.registry_file):
                with open(self.registry_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                for ext_data in data.get("extensions", {}).values():
                    info = ExtensionInfo.from_dict(ext_data)
                    self.extensions[info.name] = info
        except Exception as e:
            logger.error(f"Error loading registry: {e}")
    
    def _save_registry(self) -> None:
        """Save the registry to the registry file."""
        try:
            data = {
                "extensions": {
                    ext.name: ext.to_dict() for ext in self.extensions.values()
                }
            }
            
            with open(self.registry_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving registry: {e}")
    
    def discover(self) -> Dict[str, ExtensionInfo]:
        """Discover installed extensions.
        
        Returns:
            A dictionary mapping extension names to information.
        """
        with self._lock:
            # Discover extension paths
            extension_paths = discover_extensions(self.extensions_dir)
            
            # Load extensions from paths
            for path in extension_paths:
                try:
                    extension = load_extension(path)
                    if extension is not None:
                        info = ExtensionInfo.from_extension(extension, os.path.dirname(path))
                        
                        # Update existing extension or add new one
                        if info.name in self.extensions:
                            existing = self.extensions[info.name]
                            info.active = existing.active
                            info.settings = existing.settings
                            info.install_date = existing.install_date
                        
                        self.extensions[info.name] = info
                        self.instances[info.name] = extension
                except Exception as e:
                    logger.error(f"Error loading extension from {path}: {e}")
            
            # Save the registry
            self._save_registry()
            
            return self.extensions
    
    def get_extension_info(self, name: str) -> Optional[ExtensionInfo]:
        """Get information about an extension.
        
        Args:
            name: The name of the extension.
            
        Returns:
            The extension information, or None if not found.
        """
        with self._lock:
            return self.extensions.get(name)
    
    def get_extension_instance(self, name: str) -> Optional[Extension]:
        """Get an extension instance.
        
        Args:
            name: The name of the extension.
            
        Returns:
            The extension instance, or None if not found.
        """
        with self._lock:
            return self.instances.get(name)
    
    def list_extensions(self) -> List[ExtensionInfo]:
        """List all extensions.
        
        Returns:
            A list of extension information.
        """
        with self._lock:
            # If no extensions in registry, discover them
            if not self.extensions:
                self.discover()
            
            return list(self.extensions.values())
    
    def install_extension(self, source: str) -> Tuple[bool, Optional[str], str]:
        """Install an extension.
        
        Args:
            source: The source of the extension (path or URL).
            
        Returns:
            A tuple containing:
            - A boolean indicating success or failure.
            - The name of the installed extension, or None if installation failed.
            - A message describing the result.
        """
        with self._lock:
            try:
                # Check if source is a URL or local path
                if source.startswith(("http://", "https://")):
                    # Install from URL
                    install_path = install_from_url(source, self.extensions_dir)
                    if not install_path:
                        return False, None, f"Failed to install extension from URL: {source}"
                elif os.path.isdir(source):
                    # Install from directory
                    install_path = install_from_directory(source, self.extensions_dir)
                    if not install_path:
                        return False, None, f"Failed to install extension from directory: {source}"
                elif os.path.isfile(source) and source.endswith(".zip"):
                    # Install from ZIP file
                    install_path = install_from_zip(source, self.extensions_dir)
                    if not install_path:
                        return False, None, f"Failed to install extension from ZIP file: {source}"
                else:
                    return False, None, f"Invalid extension source: {source}"
                
                # Find the extension entry point
                entry_point = None
                if os.path.isfile(os.path.join(install_path, "__init__.py")):
                    entry_point = os.path.join(install_path, "__init__.py")
                else:
                    for file in ["extension.py", "main.py"]:
                        if os.path.isfile(os.path.join(install_path, file)):
                            entry_point = os.path.join(install_path, file)
                            break
                
                if not entry_point:
                    return False, None, f"Could not find extension entry point in {install_path}"
                
                # Load the extension
                extension = load_extension(entry_point)
                if not extension:
                    return False, None, f"Failed to load extension from {entry_point}"
                
                # Create extension info
                info = ExtensionInfo.from_extension(extension, install_path)
                
                # Update registry
                self.extensions[info.name] = info
                self.instances[info.name] = extension
                
                # Save registry
                self._save_registry()
                
                return True, info.name, f"Extension {info.name} installed successfully"
            except Exception as e:
                logger.error(f"Error installing extension: {e}")
                return False, None, f"Error installing extension: {e}"
    
    def uninstall_extension(self, name: str) -> Tuple[bool, str]:
        """Uninstall an extension.
        
        Args:
            name: The name of the extension.
            
        Returns:
            A tuple containing:
            - A boolean indicating success or failure.
            - A message describing the result.
        """
        with self._lock:
            try:
                # Check if extension exists
                if name not in self.extensions:
                    return False, f"Extension {name} not found"
                
                # Get extension info
                info = self.extensions[name]
                
                # Deactivate the extension if it's active
                if info.active and name in self.instances:
                    success, message = self.disable_extension(name)
                    if not success:
                        return False, f"Failed to disable extension: {message}"
                
                # Remove the extension directory
                if info.path and os.path.exists(info.path):
                    import shutil
                    shutil.rmtree(info.path)
                
                # Remove from registry
                del self.extensions[name]
                if name in self.instances:
                    del self.instances[name]
                
                # Save registry
                self._save_registry()
                
                return True, f"Extension {name} uninstalled successfully"
            except Exception as e:
                logger.error(f"Error uninstalling extension {name}: {e}")
                return False, f"Error uninstalling extension: {e}"
    
    def enable_extension(self, name: str) -> Tuple[bool, str]:
        """Enable an extension.
        
        Args:
            name: The name of the extension.
            
        Returns:
            A tuple containing:
            - A boolean indicating success or failure.
            - A message describing the result.
        """
        with self._lock:
            try:
                # Check if extension exists
                if name not in self.extensions:
                    return False, f"Extension {name} not found"
                
                # Get extension info
                info = self.extensions[name]
                
                # Check if already active
                if info.active:
                    return True, f"Extension {name} is already active"
                
                # Load the extension if not already loaded
                if name not in self.instances:
                    if not info.path:
                        return False, f"Extension {name} has no path"
                    
                    entry_point = None
                    if os.path.isfile(os.path.join(info.path, "__init__.py")):
                        entry_point = os.path.join(info.path, "__init__.py")
                    else:
                        for file in ["extension.py", "main.py"]:
                            if os.path.isfile(os.path.join(info.path, file)):
                                entry_point = os.path.join(info.path, file)
                                break
                    
                    if not entry_point:
                        return False, f"Could not find extension entry point in {info.path}"
                    
                    extension = load_extension(entry_point)
                    if not extension:
                        return False, f"Failed to load extension from {entry_point}"
                    
                    self.instances[name] = extension
                
                # Get the extension instance
                extension = self.instances[name]
                
                # Check dependencies
                for dep_name in extension.dependencies:
                    if dep_name not in self.extensions:
                        return False, f"Missing dependency: {dep_name}"
                    
                    dep_info = self.extensions[dep_name]
                    if not dep_info.active:
                        # Try to enable the dependency
                        success, message = self.enable_extension(dep_name)
                        if not success:
                            return False, f"Failed to enable dependency {dep_name}: {message}"
                
                # Initialize and activate the extension
                try:
                    success = extension.initialize({})
                    if not success:
                        return False, f"Failed to initialize extension {name}"
                    
                    # Register hooks
                    register_hooks_from_instance(extension)
                    
                    success = extension.activate()
                    if not success:
                        return False, f"Failed to activate extension {name}"
                    
                    # Update extension status
                    info.active = True
                    info.error = None
                    
                    # Save registry
                    self._save_registry()
                    
                    return True, f"Extension {name} enabled successfully"
                except Exception as e:
                    logger.error(f"Error enabling extension {name}: {e}")
                    info.error = str(e)
                    self._save_registry()
                    return False, f"Error enabling extension: {e}"
            except Exception as e:
                logger.error(f"Error enabling extension {name}: {e}")
                return False, f"Error enabling extension: {e}"
    
    def disable_extension(self, name: str) -> Tuple[bool, str]:
        """Disable an extension.
        
        Args:
            name: The name of the extension.
            
        Returns:
            A tuple containing:
            - A boolean indicating success or failure.
            - A message describing the result.
        """
        with self._lock:
            try:
                # Check if extension exists
                if name not in self.extensions:
                    return False, f"Extension {name} not found"
                
                # Get extension info
                info = self.extensions[name]
                
                # Check if already inactive
                if not info.active:
                    return True, f"Extension {name} is already inactive"
                
                # Check if other active extensions depend on this one
                for other_name, other_info in self.extensions.items():
                    if other_info.active and other_name != name:
                        other_ext = self.instances.get(other_name)
                        if other_ext and name in other_ext.dependencies:
                            return False, f"Extension {other_name} depends on {name}"
                
                # Deactivate the extension
                if name in self.instances:
                    extension = self.instances[name]
                    
                    try:
                        success = extension.deactivate()
                        if not success:
                            return False, f"Failed to deactivate extension {name}"
                    except Exception as e:
                        logger.error(f"Error deactivating extension {name}: {e}")
                        info.error = str(e)
                
                # Update extension status
                info.active = False
                
                # Save registry
                self._save_registry()
                
                return True, f"Extension {name} disabled successfully"
            except Exception as e:
                logger.error(f"Error disabling extension {name}: {e}")
                return False, f"Error disabling extension: {e}"
    
    def update_extension_settings(self, name: str, settings: Dict[str, Any]) -> Tuple[bool, str]:
        """Update extension settings.
        
        Args:
            name: The name of the extension.
            settings: The settings to update.
            
        Returns:
            A tuple containing:
            - A boolean indicating success or failure.
            - A message describing the result.
        """
        with self._lock:
            try:
                # Check if extension exists
                if name not in self.extensions:
                    return False, f"Extension {name} not found"
                
                # Get extension info
                info = self.extensions[name]
                
                # Update settings
                for key, value in settings.items():
                    if key in info.settings:
                        info.settings[key]["value"] = value
                
                # Update extension instance
                if name in self.instances:
                    extension = self.instances[name]
                    for key, value in settings.items():
                        if hasattr(extension, key):
                            setattr(extension, key, value)
                
                # Save registry
                self._save_registry()
                
                return True, f"Settings for {name} updated successfully"
            except Exception as e:
                logger.error(f"Error updating settings for {name}: {e}")
                return False, f"Error updating settings: {e}"
    
    def initialize_all(self) -> Dict[str, Tuple[bool, str]]:
        """Initialize all extensions.
        
        Returns:
            A dictionary mapping extension names to initialization results.
        """
        with self._lock:
            # If no extensions in registry, discover them
            if not self.extensions:
                self.discover()
            
            # Get extensions that should be active
            active_extensions = [name for name, info in self.extensions.items() if info.active]
            
            # Initialize extensions
            results = {}
            for name in active_extensions:
                success, message = self.enable_extension(name)
                results[name] = (success, message)
            
            return results


# Singleton instance
_registry_instance = None

def initialize_registry(extensions_dir: Optional[str] = None) -> ExtensionRegistry:
    """Initialize the extension registry.
    
    Args:
        extensions_dir: The directory containing extensions.
        
    Returns:
        The initialized registry.
    """
    global _registry_instance
    if _registry_instance is None:
        _registry_instance = ExtensionRegistry(extensions_dir)
    return _registry_instance

def get_registry() -> ExtensionRegistry:
    """Get the extension registry.
    
    Returns:
        The extension registry.
    """
    global _registry_instance
    if _registry_instance is None:
        _registry_instance = initialize_registry()
    return _registry_instance
