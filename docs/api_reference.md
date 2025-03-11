# API Reference

This document provides a reference for the Extension API in Open WebUI.

## Table of Contents

- [Base Classes](#base-classes)
- [Hooks](#hooks)
- [Decorators](#decorators)
- [Utilities](#utilities)

## Base Classes

### Extension

The base class for all extensions.

```python
class Extension(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """The name of the extension."""
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        """The version of the extension."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """A description of what the extension does."""
        pass
    
    @property
    @abstractmethod
    def author(self) -> str:
        """The author(s) of the extension."""
        pass
    
    @property
    def dependencies(self) -> List[str]:
        """List of other extensions this extension depends on."""
        return []
    
    @property
    def type(self) -> str:
        """The type of extension (UI, API, Model, Tool, Theme)."""
        return "generic"
    
    @property
    def settings(self) -> Dict[str, Any]:
        """The extension's default settings."""
        return {}
    
    @property
    def static_dir(self) -> Optional[str]:
        """The directory containing static files for this extension."""
        pass
    
    def initialize(self, context: Dict[str, Any]) -> bool:
        """Initialize the extension with the given context."""
        return True
    
    def activate(self) -> bool:
        """Activate the extension."""
        return True
    
    def deactivate(self) -> bool:
        """Deactivate the extension."""
        return True
    
    def uninstall(self) -> bool:
        """Perform cleanup when uninstalling the extension."""
        return True
```

### UIExtension

Base class for UI extensions.

```python
class UIExtension(Extension):
    @property
    def type(self) -> str:
        return "ui"
    
    @property
    @abstractmethod
    def components(self) -> Dict[str, Any]:
        """A dictionary of UI components provided by this extension."""
        pass
    
    @property
    def mount_points(self) -> Dict[str, List[str]]:
        """A dictionary mapping mount points to component IDs."""
        return {}
```

### APIExtension

Base class for API extensions.

```python
class APIExtension(Extension):
    @property
    def type(self) -> str:
        return "api"
    
    @property
    @abstractmethod
    def routes(self) -> List[Any]:
        """A list of API routes provided by this extension."""
        pass
```

### ModelExtension

Base class for model adapter extensions.

```python
class ModelExtension(Extension):
    @property
    def type(self) -> str:
        return "model"
    
    @abstractmethod
    def load_model(self) -> Any:
        """Load the AI model."""
        pass
    
    @abstractmethod
    def generate(self, prompt: str, params: Dict[str, Any]) -> str:
        """Generate a response from the model."""
        pass
```

### ToolExtension

Base class for tool extensions.

```python
class ToolExtension(Extension):
    @property
    def type(self) -> str:
        return "tool"
    
    @property
    @abstractmethod
    def tools(self) -> Dict[str, Callable]:
        """A dictionary of tools provided by this extension."""
        pass
```

### ThemeExtension

Base class for theme extensions.

```python
class ThemeExtension(Extension):
    @property
    def type(self) -> str:
        return "theme"
    
    @property
    @abstractmethod
    def styles(self) -> Dict[str, str]:
        """A dictionary of style definitions."""
        pass
    
    @property
    @abstractmethod
    def theme_name(self) -> str:
        """The name of the theme."""
        pass
```

## Hooks

Hooks allow extensions to integrate with Open WebUI at specific points in the application's lifecycle.

### Available Hooks

#### UI Hooks

- `ui_init`: Called when the UI is initialized
- `ui_render`: Called when the UI is rendered
- `ui_sidebar`: Called when the sidebar is rendered
- `ui_header`: Called when the header is rendered
- `ui_footer`: Called when the footer is rendered
- `ui_chat`: Called when the chat interface is rendered
- `ui_settings`: Called when the settings page is rendered

#### API Hooks

- `api_init`: Called when the API is initialized
- `api_register_routes`: Called when API routes are registered
- `api_before_request`: Called before processing an API request
- `api_after_request`: Called after processing an API request

#### Model Hooks

- `model_init`: Called when a model is initialized
- `model_register`: Called when a model is registered
- `model_before_generate`: Called before generating text
- `model_after_generate`: Called after generating text

#### System Hooks

- `system_init`: Called when the system is initialized
- `system_shutdown`: Called when the system is shut down
- `system_settings_load`: Called when system settings are loaded
- `system_settings_save`: Called when system settings are saved

### Registering Hooks

You can register hooks using the `@hook` decorator:

```python
from open_webui_extensions import hook

class MyExtension(Extension):
    @hook("ui_init")
    def on_ui_init(self) -> None:
        """Hook called when the UI is initialized."""
        print("UI initialized")
    
    @hook("model_before_generate", priority=5)
    def on_model_before_generate(self, prompt: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Hook called before generating text."""
        print(f"Generating text with prompt: {prompt[:50]}...")
        # You can modify the prompt or parameters here
        return params
```

## Decorators

The extension system provides several decorators to simplify extension development.

### @hook

Register a method as a hook handler.

```python
@hook(hook_name: str, priority: int = 10)
```

Arguments:
- `hook_name`: The name of the hook to register for
- `priority`: The priority of the handler (lower numbers run first)

### @ui_component

Register a method as a UI component.

```python
@ui_component(component_id: str, mount_points: List[str] = None)
```

Arguments:
- `component_id`: The ID of the component
- `mount_points`: A list of mount points for the component

### @api_route

Register a method as an API route.

```python
@api_route(path: str, methods: List[str] = None, tags: List[str] = None, summary: str = None, response_model: Type = None)
```

Arguments:
- `path`: The URL path for the route
- `methods`: A list of HTTP methods for the route
- `tags`: A list of tags for the route
- `summary`: A summary of the route
- `response_model`: The response model for the route

### @tool

Register a method as a tool.

```python
@tool(name: str, description: str = None)
```

Arguments:
- `name`: The name of the tool
- `description`: A description of the tool

### @setting

Register a class attribute as a setting.

```python
@setting(name: str, default: Any = None, type_: Type = None, description: str = None, options: List[Dict[str, Any]] = None, required: bool = False, category: str = "General")
```

Arguments:
- `name`: The name of the setting
- `default`: The default value of the setting
- `type_`: The type of the setting
- `description`: A description of the setting
- `options`: A list of options for the setting
- `required`: Whether the setting is required
- `category`: The category of the setting

## Utilities

The extension system provides several utility functions for extensions.

### Extension Registry API

The extension registry manages installed extensions.

```python
from open_webui_extensions.extension_system.registry import get_registry

registry = get_registry()

# List extensions
extensions = registry.list_extensions()

# Get extension info
extension_info = registry.get_extension_info("extension-name")

# Get extension instance
extension_instance = registry.get_extension_instance("extension-name")

# Install an extension
success, name, message = registry.install_extension("path/or/url")

# Enable an extension
success, message = registry.enable_extension("extension-name")

# Disable an extension
success, message = registry.disable_extension("extension-name")

# Uninstall an extension
success, message = registry.uninstall_extension("extension-name")

# Update extension settings
success, message = registry.update_extension_settings("extension-name", {"setting": "value"})
```

### Command-line Interface

The extension system provides a command-line interface (CLI) for managing extensions.

```bash
# List extensions
webui-extensions list

# Install an extension
webui-extensions install path/or/url

# Enable an extension
webui-extensions enable extension-name

# Disable an extension
webui-extensions disable extension-name

# Show extension info
webui-extensions info extension-name

# Uninstall an extension
webui-extensions uninstall extension-name
```
