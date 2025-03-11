"""
Hook system for extensions.
"""

import logging
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger("webui-extensions.hooks")

class HookRegistry:
    """Registry for hooks."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(HookRegistry, cls).__new__(cls)
            cls._instance._hooks = {}
            cls._instance._callbacks = {}
            cls._instance._register_default_hooks()
        return cls._instance
    
    def _register_default_hooks(self):
        """Register default hooks."""
        # UI hooks
        self.register_hook("ui_init", "Called when the UI is initialized")
        self.register_hook("ui_render", "Called when the UI is rendered")
        self.register_hook("ui_sidebar", "Called when the sidebar is rendered")
        self.register_hook("ui_header", "Called when the header is rendered")
        self.register_hook("ui_footer", "Called when the footer is rendered")
        self.register_hook("ui_chat", "Called when the chat interface is rendered")
        self.register_hook("ui_settings", "Called when the settings page is rendered")
        
        # API hooks
        self.register_hook("api_init", "Called when the API is initialized")
        self.register_hook("api_register_routes", "Called when API routes are registered")
        self.register_hook("api_before_request", "Called before processing an API request")
        self.register_hook("api_after_request", "Called after processing an API request")
        
        # Model hooks
        self.register_hook("model_init", "Called when a model is initialized")
        self.register_hook("model_register", "Called when a model is registered")
        self.register_hook("model_before_generate", "Called before generating text")
        self.register_hook("model_after_generate", "Called after generating text")
        
        # System hooks
        self.register_hook("system_init", "Called when the system is initialized")
        self.register_hook("system_shutdown", "Called when the system is shut down")
        self.register_hook("system_settings_load", "Called when system settings are loaded")
        self.register_hook("system_settings_save", "Called when system settings are saved")
    
    def register_hook(self, name: str, description: str = "") -> None:
        """Register a new hook.
        
        Args:
            name: The name of the hook.
            description: A description of the hook.
        """
        if name in self._hooks:
            logger.warning(f"Hook {name} already registered. Overwriting.")
        
        self._hooks[name] = {
            "description": description,
            "callbacks": [],
        }
        
        if name not in self._callbacks:
            self._callbacks[name] = []
    
    def register_callback(self, hook_name: str, callback: Callable, extension_name: str, priority: int = 10) -> bool:
        """Register a callback for a hook.
        
        Args:
            hook_name: The name of the hook to register for.
            callback: The callback function.
            extension_name: The name of the extension registering the callback.
            priority: The priority of the callback (lower numbers run first).
            
        Returns:
            True if the callback was registered successfully, False otherwise.
        """
        if hook_name not in self._hooks:
            logger.warning(f"Hook {hook_name} not registered. Registering now.")
            self.register_hook(hook_name)
        
        callback_info = {
            "callback": callback,
            "extension": extension_name,
            "priority": priority,
        }
        
        self._callbacks[hook_name].append(callback_info)
        # Sort callbacks by priority
        self._callbacks[hook_name].sort(key=lambda x: x["priority"])
        return True
    
    def unregister_callback(self, hook_name: str, extension_name: str) -> bool:
        """Unregister all callbacks for a hook from an extension.
        
        Args:
            hook_name: The name of the hook.
            extension_name: The name of the extension.
            
        Returns:
            True if any callbacks were unregistered, False otherwise.
        """
        if hook_name not in self._callbacks:
            return False
        
        initial_count = len(self._callbacks[hook_name])
        self._callbacks[hook_name] = [
            cb for cb in self._callbacks[hook_name] 
            if cb["extension"] != extension_name
        ]
        
        return len(self._callbacks[hook_name]) < initial_count
    
    def execute_hook(self, hook_name: str, *args, **kwargs) -> List[Any]:
        """Execute all callbacks for a hook.
        
        Args:
            hook_name: The name of the hook to execute.
            *args: Positional arguments to pass to the callbacks.
            **kwargs: Keyword arguments to pass to the callbacks.
            
        Returns:
            A list of results from all callbacks.
        """
        if hook_name not in self._callbacks:
            logger.warning(f"No callbacks registered for hook {hook_name}")
            return []
        
        results = []
        for callback_info in self._callbacks[hook_name]:
            try:
                result = callback_info["callback"](*args, **kwargs)
                results.append(result)
            except Exception as e:
                logger.error(f"Error executing callback for hook {hook_name} from extension {callback_info['extension']}: {e}")
        
        return results
    
    def get_hooks(self) -> Dict[str, Dict[str, Any]]:
        """Get all registered hooks.
        
        Returns:
            A dictionary of hook information.
        """
        return self._hooks
    
    def get_callbacks(self, hook_name: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        """Get all registered callbacks for a hook.
        
        Args:
            hook_name: The name of the hook to get callbacks for, or None for all hooks.
            
        Returns:
            A dictionary of callback information.
        """
        if hook_name is not None:
            return {hook_name: self._callbacks.get(hook_name, [])}
        return self._callbacks


# Singleton instance
_hook_registry = HookRegistry()

# Public API
def register_hook(name: str, description: str = "") -> None:
    """Register a new hook.
    
    Args:
        name: The name of the hook.
        description: A description of the hook.
    """
    _hook_registry.register_hook(name, description)

def register_callback(hook_name: str, callback: Callable, extension_name: str, priority: int = 10) -> bool:
    """Register a callback for a hook.
    
    Args:
        hook_name: The name of the hook to register for.
        callback: The callback function.
        extension_name: The name of the extension registering the callback.
        priority: The priority of the callback (lower numbers run first).
        
    Returns:
        True if the callback was registered successfully, False otherwise.
    """
    return _hook_registry.register_callback(hook_name, callback, extension_name, priority)

def unregister_callback(hook_name: str, extension_name: str) -> bool:
    """Unregister all callbacks for a hook from an extension.
    
    Args:
        hook_name: The name of the hook.
        extension_name: The name of the extension.
        
    Returns:
        True if any callbacks were unregistered, False otherwise.
    """
    return _hook_registry.unregister_callback(hook_name, extension_name)

def execute_hook(hook_name: str, *args, **kwargs) -> List[Any]:
    """Execute all callbacks for a hook.
    
    Args:
        hook_name: The name of the hook to execute.
        *args: Positional arguments to pass to the callbacks.
        **kwargs: Keyword arguments to pass to the callbacks.
        
    Returns:
        A list of results from all callbacks.
    """
    return _hook_registry.execute_hook(hook_name, *args, **kwargs)

def get_hooks() -> Dict[str, Dict[str, Any]]:
    """Get all registered hooks.
    
    Returns:
        A dictionary of hook information.
    """
    return _hook_registry.get_hooks()

def get_callbacks(hook_name: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
    """Get all registered callbacks for a hook.
    
    Args:
        hook_name: The name of the hook to get callbacks for, or None for all hooks.
        
    Returns:
        A dictionary of callback information.
    """
    return _hook_registry.get_callbacks(hook_name)
