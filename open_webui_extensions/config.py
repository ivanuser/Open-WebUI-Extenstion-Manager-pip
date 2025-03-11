"""
Configuration utilities for Open WebUI Extensions.
"""

import os
import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger("webui-extensions.config")

DEFAULT_CONFIG = {
    "extensions_dir": str(Path.home() / ".openwebui" / "extensions"),
    "extension_registry_file": "registry.json",
    "use_dev_server": False,
    "dev_server_host": "localhost",
    "dev_server_port": 5000,
}

def get_config_file_path() -> str:
    """Get the path to the configuration file."""
    # Look for config files in order of precedence
    config_paths = [
        # Environment variable
        os.environ.get("OPENWEBUI_EXTENSIONS_CONFIG"),
        # User home directory
        str(Path.home() / ".openwebui" / "extensions.json"),
        str(Path.home() / ".config" / "openwebui" / "extensions.json"),
        # System directory
        "/etc/openwebui/extensions.json",
        # Current directory
        "./extensions.json",
    ]
    
    # Find the first config file that exists
    for path in config_paths:
        if path and os.path.exists(path):
            return path
    
    # Default to user home directory if no config file exists
    default_path = str(Path.home() / ".openwebui" / "extensions.json")
    return default_path

def load_config() -> Dict[str, Any]:
    """Load the extension system configuration."""
    config_path = get_config_file_path()
    
    # If the config file exists, load it
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            
            # Merge with default config for missing keys
            for key, value in DEFAULT_CONFIG.items():
                if key not in config:
                    config[key] = value
            
            return config
        except Exception as e:
            logger.error(f"Error loading config from {config_path}: {e}")
    
    # If the config file doesn't exist, create it with default values
    try:
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f, indent=2)
    except Exception as e:
        logger.error(f"Error creating config file at {config_path}: {e}")
    
    return DEFAULT_CONFIG.copy()

def save_config(config: Dict[str, Any]) -> bool:
    """Save the extension system configuration.
    
    Args:
        config: The configuration to save.
        
    Returns:
        True if the configuration was saved successfully, False otherwise.
    """
    config_path = get_config_file_path()
    
    try:
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving config to {config_path}: {e}")
        return False

def get_config_value(key: str, default: Any = None) -> Any:
    """Get a configuration value.
    
    Args:
        key: The configuration key.
        default: The default value to return if the key doesn't exist.
        
    Returns:
        The configuration value, or the default if the key doesn't exist.
    """
    config = load_config()
    return config.get(key, default)

def set_config_value(key: str, value: Any) -> bool:
    """Set a configuration value.
    
    Args:
        key: The configuration key.
        value: The value to set.
        
    Returns:
        True if the value was set successfully, False otherwise.
    """
    config = load_config()
    config[key] = value
    return save_config(config)

# Global configuration
config = load_config()

# Functions to get specific configuration values
def get_extensions_dir() -> str:
    """Get the extensions directory."""
    return config.get("extensions_dir", DEFAULT_CONFIG["extensions_dir"])

def get_registry_file() -> str:
    """Get the path to the extension registry file."""
    extensions_dir = get_extensions_dir()
    registry_file = config.get("extension_registry_file", DEFAULT_CONFIG["extension_registry_file"])
    return os.path.join(extensions_dir, registry_file)

def is_dev_server_enabled() -> bool:
    """Check if the development server is enabled."""
    return config.get("use_dev_server", DEFAULT_CONFIG["use_dev_server"])

def get_dev_server_host() -> str:
    """Get the development server host."""
    return config.get("dev_server_host", DEFAULT_CONFIG["dev_server_host"])

def get_dev_server_port() -> int:
    """Get the development server port."""
    return config.get("dev_server_port", DEFAULT_CONFIG["dev_server_port"])
