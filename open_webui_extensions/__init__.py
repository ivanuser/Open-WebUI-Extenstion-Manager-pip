"""
Open WebUI Extensions - Extension system for pip-installed Open WebUI.

This package provides a framework for developing, installing, and managing
extensions for Open WebUI that works with pip-installed instances.
"""

__version__ = "0.1.0"

from .extension_system import (
    Extension,
    UIExtension,
    APIExtension,
    ModelExtension,
    ToolExtension,
    ThemeExtension,
)

from .extension_system.hooks import (
    register_hook,
    register_callback,
    execute_hook,
)

from .extension_system.decorators import (
    hook,
    ui_component,
    api_route,
    tool,
    setting,
)
