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

## Integrating with Open WebUI

There are several ways to integrate the extension system with your Open WebUI installation:

### Method 1: Automatic Installation

Run the automated installer script:

```bash
webui-extensions-install
```

This script will try to find your Open WebUI installation and integrate the extension system automatically.

### Method 2: Patching Open WebUI

Use the patching script to modify your Open WebUI installation:

```bash
webui-extensions-patch
```

This script will find your Open WebUI main.py file, create a backup, and patch it to include the extension system.

### Method 3: Manual Integration

1. Find your Open WebUI's main.py file
2. Add the following lines:

```python
# Add at the top with other imports
from open_webui_extensions.plugin import initialize_extension_system

# Add after the FastAPI app is created (app = FastAPI(...))
app = initialize_extension_system(app)
```

### Method 4: Development Mode

For development or testing, you can run the extension system as a separate server:

```bash
python -m open_webui_extensions.dev_server
```

Then access the extension manager at http://localhost:5000/admin/extensions

## Using the Extension System

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

For more detailed examples and advanced extension development, see the [documentation](docs/creating_extensions.md).

## Hook Points

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

## Troubleshooting

### Extension System Not Appearing in Open WebUI

If the extension manager doesn't appear in Open WebUI after installation:

1. Check that you've restarted Open WebUI after installing the extension system
2. Try accessing the extension manager directly at `/admin/extensions`
3. Check the Open WebUI logs for any errors related to extension loading
4. Try running the extension system in development mode and access it at http://localhost:5000/admin/extensions

### Issues Installing Extensions

If you're having trouble installing or running extensions:

1. Make sure you've set up the extension system with `webui-extensions setup`
2. Check that the extension directory exists at `~/.openwebui/extensions`
3. Try installing an example extension with the full path:
   ```bash
   webui-extensions install /path/to/open-webui-extensions/example_extensions/hello_world
   ```
4. Check the logs for any errors during extension loading

## License

This project is licensed under the MIT License - see the LICENSE file for details.
