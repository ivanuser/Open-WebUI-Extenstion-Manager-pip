"""
Extension system for Open WebUI.

This module provides a framework for developing, installing, and managing
extensions for Open WebUI.
"""

from .base import (
    Extension,
    UIExtension,
    APIExtension,
    ModelExtension,
    ToolExtension,
    ThemeExtension,
)

from .registry import (
    initialize_registry,
    get_registry,
)

from .hooks import (
    register_hook,
    register_callback,
    execute_hook,
)

from .decorators import (
    hook,
    ui_component,
    api_route,
    tool,
    setting,
)

from .utils import (
    load_extension,
    discover_extensions,
    setup_extensions_directory,
)

__all__ = [
    # Base classes
    "Extension",
    "UIExtension",
    "APIExtension",
    "ModelExtension", 
    "ToolExtension",
    "ThemeExtension",
    
    # Registry
    "initialize_registry",
    "get_registry",
    
    # Hooks
    "register_hook",
    "register_callback",
    "execute_hook",
    
    # Decorators
    "hook",
    "ui_component",
    "api_route",
    "tool",
    "setting",
    
    # Utilities
    "load_extension",
    "discover_extensions",
    "setup_extensions_directory",
]
