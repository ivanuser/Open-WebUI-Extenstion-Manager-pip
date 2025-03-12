"""
Hook system for extension integration.

This module provides a hook system that allows extensions to integrate
with Open WebUI at specific points.
"""

import inspect
import logging
from typing import Any, Callable, Dict, List, Optional, Set

logger = logging.getLogger("webui-extensions.hooks")

# Dictionary mapping hook names to registered callbacks
_hook_registry: Dict[str, List[Callable]] = {}

# Set of hooks that have been registered
_registered_hooks: Set[str] = set()

def register_hook(hook_name: str) -> None:
    """Register a hook.
    
    Args:
        hook_name: The name of the hook.
    """
    if hook_name not in _registered_hooks:
        _registered_hooks.add(hook_name)
        _hook_registry[hook_name] = []
        logger.info(f"Registered hook: {hook_name}")

def register_callback(hook_name: str, callback: Callable) -> None:
    """Register a callback for a hook.
    
    Args:
        hook_name: The name of the hook.
        callback: The callback function.
    """
    if hook_name not in _registered_hooks:
        register_hook(hook_name)
    
    if callback not in _hook_registry[hook_name]:
        _hook_registry[hook_name].append(callback)
        logger.info(f"Registered callback for hook: {hook_name}")

async def execute_hook(hook_name: str, data: Any = None) -> Any:
    """Execute a hook with the given data.
    
    Args:
        hook_name: The name of the hook.
        data: The data to pass to the callbacks.
        
    Returns:
        The result of the hook execution.
    """
    if hook_name not in _registered_hooks:
        logger.debug(f"No callbacks registered for hook: {hook_name}")
        return data
    
    result = data
    
    for callback in _hook_registry[hook_name]:
        try:
            # Check if the callback is a coroutine function
            if inspect.iscoroutinefunction(callback):
                # Pass the current result to the callback
                result = await callback(result)
            else:
                # Call the callback with the current result
                result = callback(result)
        except Exception as e:
            logger.error(f"Error executing callback for hook {hook_name}: {e}")
    
    return result

def get_registered_hooks() -> Set[str]:
    """Get the names of all registered hooks.
    
    Returns:
        A set of hook names.
    """
    return _registered_hooks.copy()

def get_callbacks_for_hook(hook_name: str) -> List[Callable]:
    """Get all callbacks registered for a hook.
    
    Args:
        hook_name: The name of the hook.
        
    Returns:
        A list of callback functions.
    """
    if hook_name not in _registered_hooks:
        return []
    
    return _hook_registry[hook_name].copy()

def clear_hook_callbacks(hook_name: str) -> None:
    """Clear all callbacks for a hook.
    
    Args:
        hook_name: The name of the hook.
    """
    if hook_name in _registered_hooks:
        _hook_registry[hook_name] = []
        logger.info(f"Cleared callbacks for hook: {hook_name}")

def clear_all_hooks() -> None:
    """Clear all hooks and callbacks."""
    global _hook_registry, _registered_hooks
    _hook_registry = {}
    _registered_hooks = set()
    logger.info("Cleared all hooks and callbacks")

def register_hooks_from_instance(instance: Any) -> None:
    """Register hooks from an extension instance.
    
    This function looks for methods in the instance that have been
    decorated with the @hook decorator and registers them as callbacks
    for the corresponding hooks.
    
    Args:
        instance: The extension instance.
    """
    # Skip if the instance doesn't have a _hooks attribute
    if not hasattr(instance, "_hooks"):
        return
    
    # Register each hook
    for hook_name, method_name in instance._hooks.items():
        # Get the method from the instance
        method = getattr(instance, method_name, None)
        
        # Skip if the method doesn't exist
        if not method:
            logger.warning(f"Method {method_name} not found in {instance.name}")
            continue
        
        # Register the method as a callback
        register_callback(hook_name, method)
        logger.info(f"Registered hook {hook_name} -> {instance.name}.{method_name}")

# Register default hooks
register_hook("ui_init")
register_hook("model_before_generate")
register_hook("model_after_generate")
register_hook("chat_pre_process")
register_hook("chat_post_process")
register_hook("extension_loaded")
register_hook("extension_unloaded")
