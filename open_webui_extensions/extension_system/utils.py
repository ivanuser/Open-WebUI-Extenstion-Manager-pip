"""
Utility functions for the extension system.
"""

import os
import sys
import importlib.util
import inspect
import logging
import yaml
import json
import shutil
import tempfile
import zipfile
import requests
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Type

from .base import Extension

logger = logging.getLogger("webui-extensions.utils")

def setup_extensions_directory(directory_path: str) -> str:
    """Set up the extensions directory.
    
    Args:
        directory_path: The path to the extensions directory.
        
    Returns:
        The absolute path to the extensions directory.
    """
    directory = Path(directory_path).resolve()
    
    # Create the directory if it doesn't exist
    directory.mkdir(parents=True, exist_ok=True)
    
    # Create subdirectories
    (directory / "installed").mkdir(exist_ok=True)
    (directory / "temp").mkdir(exist_ok=True)
    
    # Create an empty registry file if it doesn't exist
    registry_file = directory / "registry.json"
    if not registry_file.exists():
        with open(registry_file, "w", encoding="utf-8") as f:
            json.dump({"extensions": {}}, f, indent=2)
    
    return str(directory)

def load_extension_module(path: str) -> Optional[Any]:
    """Load an extension module from a file path.
    
    Args:
        path: The path to the extension module.
        
    Returns:
        The loaded module, or None if loading failed.
    """
    try:
        module_name = f"open_webui_extension_{Path(path).stem}"
        spec = importlib.util.spec_from_file_location(module_name, path)
        if spec is None:
            logger.error(f"Failed to create module spec from {path}")
            return None
        
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        logger.error(f"Failed to load extension module {path}: {e}")
        return None

def find_extension_class(module: Any) -> Optional[Type[Extension]]:
    """Find an Extension subclass in a module.
    
    Args:
        module: The module to search.
        
    Returns:
        The Extension subclass, or None if not found.
    """
    try:
        # First, look for an 'extension' variable
        if hasattr(module, "extension") and isinstance(module.extension, Extension):
            return module.extension.__class__
        
        # Then look for Extension subclasses
        for name, obj in inspect.getmembers(module):
            if (inspect.isclass(obj) and 
                issubclass(obj, Extension) and 
                obj != Extension and
                not inspect.isabstract(obj)):
                return obj
        
        logger.warning(f"No Extension subclass found in module {module.__name__}")
        return None
    except Exception as e:
        logger.error(f"Error finding extension class in module {module.__name__}: {e}")
        return None

def get_extension_instance(module: Any) -> Optional[Extension]:
    """Get an extension instance from a module.
    
    Args:
        module: The module to get the extension from.
        
    Returns:
        An instance of the extension, or None if not found.
    """
    try:
        # First, look for an 'extension' variable
        if hasattr(module, "extension") and isinstance(module.extension, Extension):
            return module.extension
        
        # Then look for Extension subclasses and instantiate one
        extension_class = find_extension_class(module)
        if extension_class is not None:
            return extension_class()
        
        return None
    except Exception as e:
        logger.error(f"Error getting extension instance from module {module.__name__}: {e}")
        return None

def load_extension(path: str) -> Optional[Extension]:
    """Load an extension from a file path.
    
    Args:
        path: The path to the extension module.
        
    Returns:
        An instance of the extension, or None if loading failed.
    """
    module = load_extension_module(path)
    if module is None:
        return None
    
    return get_extension_instance(module)

def discover_extensions(directory: str) -> List[str]:
    """Discover extension modules in a directory.
    
    Args:
        directory: The directory to search.
        
    Returns:
        A list of paths to extension modules.
    """
    extension_paths = []
    
    try:
        installed_dir = Path(directory) / "installed"
        if not installed_dir.exists():
            installed_dir.mkdir(parents=True, exist_ok=True)
        
        for ext_dir in installed_dir.iterdir():
            if ext_dir.is_dir():
                init_py = ext_dir / "__init__.py"
                if init_py.exists():
                    extension_paths.append(str(init_py))
                else:
                    # Look for main module file
                    for file in ext_dir.glob("*.py"):
                        if file.name in ["extension.py", "main.py", f"{ext_dir.name}.py"]:
                            extension_paths.append(str(file))
                            break
    except Exception as e:
        logger.error(f"Error discovering extensions in {directory}: {e}")
    
    return extension_paths

def load_extension_config(path: str) -> Dict[str, Any]:
    """Load an extension configuration from a file.
    
    Args:
        path: The path to the configuration file.
        
    Returns:
        The configuration as a dictionary.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            if path.endswith(".yaml") or path.endswith(".yml"):
                return yaml.safe_load(f) or {}
            elif path.endswith(".json"):
                return json.load(f)
            else:
                logger.warning(f"Unknown configuration file format: {path}")
                return {}
    except Exception as e:
        logger.error(f"Error loading extension configuration from {path}: {e}")
        return {}

def save_extension_config(config: Dict[str, Any], path: str) -> bool:
    """Save an extension configuration to a file.
    
    Args:
        config: The configuration to save.
        path: The path to save the configuration to.
        
    Returns:
        True if the configuration was saved successfully, False otherwise.
    """
    try:
        directory = os.path.dirname(path)
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
        
        with open(path, "w", encoding="utf-8") as f:
            if path.endswith(".yaml") or path.endswith(".yml"):
                yaml.dump(config, f, default_flow_style=False)
            elif path.endswith(".json"):
                json.dump(config, f, indent=2)
            else:
                logger.warning(f"Unknown configuration file format: {path}")
                return False
        return True
    except Exception as e:
        logger.error(f"Error saving extension configuration to {path}: {e}")
        return False

def download_from_url(url: str, target_path: str) -> bool:
    """Download a file from a URL.
    
    Args:
        url: The URL to download from.
        target_path: The path to save the file to.
        
    Returns:
        True if the file was downloaded successfully, False otherwise.
    """
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(target_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return True
    except Exception as e:
        logger.error(f"Error downloading from {url}: {e}")
        return False

def extract_zip(zip_path: str, target_dir: str) -> bool:
    """Extract a ZIP file.
    
    Args:
        zip_path: The path to the ZIP file.
        target_dir: The directory to extract to.
        
    Returns:
        True if the file was extracted successfully, False otherwise.
    """
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(target_dir)
        return True
    except Exception as e:
        logger.error(f"Error extracting ZIP file {zip_path}: {e}")
        return False

def find_extension_dir(base_dir: str) -> Optional[str]:
    """Find the extension directory in a base directory.
    
    This function looks for a directory containing an __init__.py file
    or other common extension entry points.
    
    Args:
        base_dir: The base directory to search.
        
    Returns:
        The path to the extension directory, or None if not found.
    """
    base_path = Path(base_dir)
    
    # Check for __init__.py in the base directory
    if (base_path / "__init__.py").exists():
        return str(base_path)
    
    # Look for common extension entry point files
    for file in ["extension.py", "main.py"]:
        if (base_path / file).exists():
            return str(base_path)
    
    # Look for a single subdirectory with an extension
    subdirs = [d for d in base_path.iterdir() if d.is_dir() and not d.name.startswith(".")]
    if len(subdirs) == 1:
        subdir = subdirs[0]
        if (subdir / "__init__.py").exists() or any((subdir / f).exists() for f in ["extension.py", "main.py"]):
            return str(subdir)
    
    # Look for any subdirectory with an extension
    for subdir in subdirs:
        if (subdir / "__init__.py").exists() or any((subdir / f).exists() for f in ["extension.py", "main.py"]):
            return str(subdir)
    
    return None

def install_from_directory(source_dir: str, target_dir: str) -> Optional[str]:
    """Install an extension from a directory.
    
    Args:
        source_dir: The source directory.
        target_dir: The target directory.
        
    Returns:
        The path to the installed extension, or None if installation failed.
    """
    try:
        # Find the extension directory
        ext_dir = find_extension_dir(source_dir)
        if ext_dir is None:
            logger.error(f"No extension found in directory {source_dir}")
            return None
        
        # Load the extension to get its name
        ext_path = None
        if Path(ext_dir, "__init__.py").exists():
            ext_path = str(Path(ext_dir, "__init__.py"))
        else:
            for file in ["extension.py", "main.py"]:
                if Path(ext_dir, file).exists():
                    ext_path = str(Path(ext_dir, file))
                    break
        
        if ext_path is None:
            logger.error(f"No extension entry point found in directory {ext_dir}")
            return None
        
        extension = load_extension(ext_path)
        if extension is None:
            logger.error(f"Failed to load extension from {ext_path}")
            return None
        
        # Create the target directory
        ext_name = extension.name
        install_dir = os.path.join(target_dir, "installed", ext_name)
        if os.path.exists(install_dir):
            logger.warning(f"Extension {ext_name} already exists, removing")
            shutil.rmtree(install_dir)
        
        # Copy the extension
        shutil.copytree(ext_dir, install_dir)
        
        return install_dir
    except Exception as e:
        logger.error(f"Error installing from directory {source_dir}: {e}")
        return None

def install_from_zip(zip_path: str, target_dir: str) -> Optional[str]:
    """Install an extension from a ZIP file.
    
    Args:
        zip_path: The path to the ZIP file.
        target_dir: The target directory.
        
    Returns:
        The path to the installed extension, or None if installation failed.
    """
    try:
        # Create a temporary directory for extraction
        temp_dir = os.path.join(target_dir, "temp", f"extract_{os.path.basename(zip_path)}")
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        os.makedirs(temp_dir, exist_ok=True)
        
        # Extract the ZIP file
        if not extract_zip(zip_path, temp_dir):
            return None
        
        # Install from the extracted directory
        result = install_from_directory(temp_dir, target_dir)
        
        # Clean up
        shutil.rmtree(temp_dir)
        
        return result
    except Exception as e:
        logger.error(f"Error installing from ZIP {zip_path}: {e}")
        return None

def install_from_url(url: str, target_dir: str) -> Optional[str]:
    """Install an extension from a URL.
    
    Args:
        url: The URL to download from.
        target_dir: The target directory.
        
    Returns:
        The path to the installed extension, or None if installation failed.
    """
    try:
        # Create a temporary file for download
        temp_file = os.path.join(target_dir, "temp", f"download_{os.path.basename(url)}")
        os.makedirs(os.path.dirname(temp_file), exist_ok=True)
        
        # Download the file
        if not download_from_url(url, temp_file):
            return None
        
        # If it's a ZIP file, install from ZIP
        if url.endswith(".zip") or zipfile.is_zipfile(temp_file):
            result = install_from_zip(temp_file, target_dir)
        else:
            logger.error(f"Unsupported file type: {url}")
            result = None
        
        # Clean up
        if os.path.exists(temp_file):
            os.remove(temp_file)
        
        return result
    except Exception as e:
        logger.error(f"Error installing from URL {url}: {e}")
        return None
