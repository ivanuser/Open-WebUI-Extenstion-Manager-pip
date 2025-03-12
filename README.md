# Open WebUI Extension System

An extension system for pip-installed Open WebUI that enables developers to create, install, and manage extensions.

## Features

- **Extension Framework**: A robust framework for developing extensions
- **Extension Manager**: Web-based interface for managing extensions
- **Extension Registry**: System for discovering and loading extensions
- **Extension API**: Standard interfaces for extensions to integrate with Open WebUI

## Installation

### Prerequisites

- Open WebUI installed via pip
- Python 3.9 or higher

### Install from PyPI

```bash
pip install open-webui-extensions
```

### Install from GitHub

```bash
pip install git+https://github.com/open-webui/open-webui-extensions.git
```

## Usage

### Web Interface

After installation, you can access the extension manager at `/admin/extensions` in your Open WebUI instance.

### Command Line

The extension system provides a command-line interface for managing extensions:

```bash
# Set up the extension system
webui-extensions setup

# List installed extensions
webui-extensions list

# Install an extension
webui-extensions install /path/to/extension

# Enable an extension
webui-extensions enable extension-name

# Disable an extension
webui-extensions disable extension-name

# Show extension information
webui-extensions info extension-name

# Uninstall an extension
webui-extensions uninstall extension-name
```

## Developing Extensions

### Extension Structure

A basic extension consists of a Python module or package with the following structure:

```
hello_world/
├── __init__.py  # Main extension file
└── static/      # Optional static files
```

The main extension file (`__init__.py`) should define a class that inherits from one of the base extension classes and creates an instance of that class.

### Base Extension Classes

The extension system provides several base classes for different types of extensions:

- `Extension`: Base class for all extensions
- `UIExtension`: Extensions that add UI components
- `APIExtension`: Extensions that add API endpoints
- `ModelExtension`: Extensions that add new AI models
- `ToolExtension`: Extensions that add new tools or capabilities
- `ThemeExtension`: Extensions that customize the appearance

### Example Extension

Here's a simple UI extension example:

```python
from open_webui_extensions import UIExtension, ui_component, hook

class HelloWorldExtension(UIExtension):
    """A simple Hello World extension."""
    
    @property
    def name(self) -> str:
        return "hello-world"
    
    @property
    def version(self) -> str:
        return "0.1.0"
    
    @property
    def description(self) -> str:
        return "A simple Hello World extension for Open WebUI."
    
    @property
    def author(self) -> str:
        return "Open WebUI Team"
    
    @property
    def components(self) -> dict:
        return {
            "hello_sidebar": self.render_sidebar,
        }
    
    @property
    def mount_points(self) -> dict:
        return {
            "sidebar": ["hello_sidebar"],
        }
    
    @ui_component("hello_sidebar")
    def render_sidebar(self):
        """Render the sidebar component."""
        return {
            "html": """
            <div style="padding: 1rem; text-align: center;">
                <h3>Hello from Open WebUI Extensions!</h3>
                <p>This component is rendered in the sidebar.</p>
            </div>
            """
        }
    
    @hook("ui_init")
    def on_ui_init(self):
        """Hook called when the UI is initialized."""
        print("UI initialized - Hello World extension is ready!")

# Create an instance of the extension
extension = HelloWorldExtension()
```

### Development Server

The extension system provides a development server for testing extensions:

```bash
# Run the development server
python -m open_webui_extensions.dev_server

# Run with custom host and port
python -m open_webui_extensions.dev_server --host 0.0.0.0 --port 8000
```

This starts a server with a mock Open WebUI interface where you can test your extension.

### Extension Decorators

The following decorators are available for adding functionality to your extensions:

- `@hook(hook_name)`: Register a method as a hook callback
- `@ui_component(component_id, mount_points)`: Register a method as a UI component renderer
- `@api_route(path, methods)`: Register a method as an API route handler
- `@tool(tool_id)`: Register a method as a tool
- `@setting(name, default, type_, options, description)`: Register a setting for an extension

### Hook Points

The following hook points are available:

- `ui_init`: Called when the UI is initialized
- `model_before_generate`: Called before generating text
- `model_after_generate`: Called after generating text
- `chat_pre_process`: Called before processing a chat request
- `chat_post_process`: Called after processing a chat response
- `extension_loaded`: Called when an extension is loaded
- `extension_unloaded`: Called when an extension is unloaded

## Mount Points

The following mount points are available for UI components:

- `sidebar`: The sidebar panel
- `chat`: The chat interface
- `main`: The main content area
- `footer`: The footer area

## License

This project is licensed under the MIT License - see the LICENSE file for details.
