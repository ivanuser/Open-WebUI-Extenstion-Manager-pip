"""
Decorators for extension features.
"""

import functools
from typing import Any, Callable, Dict, List, Optional, Type, Union

def hook(hook_name: str) -> Callable:
    """Decorator to register a method as a hook callback.
    
    Args:
        hook_name: The name of the hook.
        
    Returns:
        The decorated method.
    """
    def decorator(method: Callable) -> Callable:
        # Add the _hook attribute to the method
        method._hook = hook_name
        
        @functools.wraps(method)
        def wrapper(*args, **kwargs):
            return method(*args, **kwargs)
        
        # Store the wrapper function and hook name in the class
        if not hasattr(wrapper, "_hook"):
            wrapper._hook = hook_name
        
        # The wrapper function needs to be modified when the class is instantiated
        return wrapper
    
    return decorator

def ui_component(component_id: str, mount_points: Optional[List[str]] = None) -> Callable:
    """Decorator to register a method as a UI component renderer.
    
    Args:
        component_id: The ID of the component.
        mount_points: A list of mount points where the component can be rendered.
        
    Returns:
        The decorated method.
    """
    def decorator(method: Callable) -> Callable:
        # Add the _ui_component attribute to the method
        method._ui_component = {
            "id": component_id,
            "mount_points": mount_points or [],
        }
        
        @functools.wraps(method)
        def wrapper(*args, **kwargs):
            return method(*args, **kwargs)
        
        # Store the wrapper function and component info in the class
        if not hasattr(wrapper, "_ui_component"):
            wrapper._ui_component = method._ui_component
        
        return wrapper
    
    return decorator

def api_route(path: str, methods: Optional[List[str]] = None) -> Callable:
    """Decorator to register a method as an API route handler.
    
    Args:
        path: The API route path.
        methods: A list of HTTP methods to register the route for.
        
    Returns:
        The decorated method.
    """
    def decorator(method: Callable) -> Callable:
        # Add the _api_route attribute to the method
        method._api_route = {
            "path": path,
            "methods": methods or ["GET"],
        }
        
        @functools.wraps(method)
        def wrapper(*args, **kwargs):
            return method(*args, **kwargs)
        
        # Store the wrapper function and route info in the class
        if not hasattr(wrapper, "_api_route"):
            wrapper._api_route = method._api_route
        
        return wrapper
    
    return decorator

def tool(tool_id: str) -> Callable:
    """Decorator to register a method as a tool.
    
    Args:
        tool_id: The ID of the tool.
        
    Returns:
        The decorated method.
    """
    def decorator(method: Callable) -> Callable:
        # Add the _tool attribute to the method
        method._tool = {
            "id": tool_id,
        }
        
        @functools.wraps(method)
        def wrapper(*args, **kwargs):
            return method(*args, **kwargs)
        
        # Store the wrapper function and tool info in the class
        if not hasattr(wrapper, "_tool"):
            wrapper._tool = method._tool
        
        return wrapper
    
    return decorator

def setting(name: str, default: Any = None, type_: Optional[Type] = None, 
           options: Optional[List[Dict[str, Any]]] = None, description: str = "") -> Callable:
    """Decorator to register a setting for an extension.
    
    Args:
        name: The name of the setting.
        default: The default value of the setting.
        type_: The type of the setting.
        options: A list of options for the setting (for dropdowns).
        description: A description of the setting.
        
    Returns:
        The decorated class.
    """
    def decorator(cls: Type) -> Type:
        # Initialize _settings if it doesn't exist
        if not hasattr(cls, "_settings"):
            cls._settings = []
        
        # Add the setting to the class
        setting_info = {
            "name": name,
            "default": default,
            "value": default,
            "type": type_.__name__ if type_ is not None else type(default).__name__ if default is not None else "str",
            "options": options,
            "description": description,
        }
        
        cls._settings.append(setting_info)
        
        # Also add the setting as a class attribute
        if not hasattr(cls, name):
            setattr(cls, name, default)
        
        return cls
    
    return decorator
