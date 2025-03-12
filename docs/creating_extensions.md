# Creating Extensions for Open WebUI

This guide explains how to create extensions for Open WebUI using the Open WebUI Extension System.

## Extension Types

The extension system supports several types of extensions:

1. **UI Extensions**: Add new UI components to Open WebUI
2. **API Extensions**: Add new API endpoints
3. **Model Adapters**: Integrate new AI models
4. **Tool Extensions**: Add new tools or capabilities
5. **Theme Extensions**: Customize the appearance

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Open WebUI Extensions installed

### Creating a Basic Extension

The easiest way to get started is to use one of the example extensions as a template. Let's create a simple UI extension:

1. Create a directory for your extension:

```bash
mkdir my-extension
cd my-extension
```

2. Create the main extension file (`__init__.py`):

```python
"""
My first Open WebUI extension.
"""

from open_webui_extensions import UIExtension, ui_component, hook

class MyExtension(UIExtension):
    """A simple UI extension."""
    
    @property
    def name(self) -> str:
        return "my-extension"
    
    @property
    def version(self) -> str:
        return "0.1.0"
    
    @property
    def description(self) -> str:
        return "My first Open WebUI extension."
    
    @property
    def author(self) -> str:
        return "Your Name"
    
    @property
    def components(self) -> dict:
        return {
            "my_sidebar": self.render_sidebar,
        }
    
    @property
    def mount_points(self) -> dict:
        return {
            "sidebar": ["my_sidebar"],
        }
    
    @ui_component("my_sidebar")
    def render_sidebar(self):
        """Render the sidebar component."""
        return {
            "html": """
            <div style="padding: 1rem; text-align: center;">
                <h3>My Extension</h3>
                <p>This is my first Open WebUI extension!</p>
            </div>
            """
        }
    
    @hook("ui_init")
    def on_ui_init(self):
        """Hook called when the UI is initialized."""
        print("UI initialized - My extension is ready!")

# Create an instance of the extension
extension = MyExtension()
```

### Testing Your Extension

1. Install your extension in development mode:

```bash
webui-extensions install /path/to/my-extension
```

2. Enable your extension:

```bash
webui-extensions enable my-extension
```

3. Test your extension using the development server:

```bash
python -m open_webui_extensions.dev_server
```

4. Open your browser and navigate to `http://localhost:5000/mock-mountpoint` to see your extension in action.

## Advanced Extension Development

### Adding Settings

You can add settings to your extension using the `@setting` decorator:

```python
from open_webui_extensions import UIExtension, ui_component, setting

@setting(name="greeting", default="Hello, World!", description="The greeting message")
@setting(name="greeting_color", default="#007bff", description="The color of the greeting")
class MyExtension(UIExtension):
    # ... rest of your extension code ...
    
    @ui_component("my_sidebar")
    def render_sidebar(self):
        """Render the sidebar component."""
        return {
            "html": f"""
            <div style="padding: 1rem; text-align: center;">
                <h3 style="color: {self.greeting_color}">{self.greeting}</h3>
                <p>This is my first Open WebUI extension!</p>
            </div>
            """
        }
```

These settings will appear in the extension manager UI and can be configured by users.

### Adding API Routes

To add API endpoints, use the `APIExtension` class and the `@api_route` decorator:

```python
from open_webui_extensions import APIExtension, api_route

class MyAPIExtension(APIExtension):
    """An API extension."""
    
    @property
    def name(self) -> str:
        return "my-api-extension"
    
    @property
    def version(self) -> str:
        return "0.1.0"
    
    @property
    def description(self) -> str:
        return "An API extension for Open WebUI."
    
    @property
    def author(self) -> str:
        return "Your Name"
    
    @property
    def routes(self) -> list:
        # This will be populated by the @api_route decorator
        return getattr(self, "_routes", [])
    
    @api_route("/hello/{name}", methods=["GET"])
    async def hello(self, name: str):
        """Say hello to someone."""
        return {
            "message": f"Hello, {name}!"
        }

# Create an instance of the extension
extension = MyAPIExtension()
```

### Adding Tools

To add tools that can be used by AI models, use the `ToolExtension` class and the `@tool` decorator:

```python
from open_webui_extensions import ToolExtension, tool

class MyToolExtension(ToolExtension):
    """A tool extension."""
    
    @property
    def name(self) -> str:
        return "my-tool-extension"
    
    @property
    def version(self) -> str:
        return "0.1.0"
    
    @property
    def description(self) -> str:
        return "A tool extension for Open WebUI."
    
    @property
    def author(self) -> str:
        return "Your Name"
    
    @property
    def tools(self) -> dict:
        # This will be populated by the @tool decorator
        return getattr(self, "_tools", {})
    
    @tool("calculate")
    def calculate(self, expression: str) -> dict:
        """
        Calculate the result of a mathematical expression.
        
        Args:
            expression: The expression to calculate, e.g., "2 + 2".
            
        Returns:
            A dictionary containing the result of the calculation.
        """
        try:
            result = eval(expression, {"__builtins__": {}}, {})
            return {
                "success": True,
                "result": result,
                "expression": expression
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "expression": expression
            }

# Create an instance of the extension
extension = MyToolExtension()
```

### Adding UI Components with JavaScript

You can include JavaScript in your UI components for interactivity:

```python
@ui_component("interactive_component")
def render_interactive(self):
    """Render an interactive component."""
    return {
        "html": f"""
        <div id="interactive-component" style="padding: 1rem; border: 1px solid #ccc; border-radius: 0.5rem;">
            <h3>Interactive Component</h3>
            <p>Click the button to change the text:</p>
            <p id="text-display">Original text</p>
            <button id="change-text-btn" class="btn">Change Text</button>
            
            <script>
                // Make sure to use a unique ID for your component
                (function() {{
                    const btn = document.getElementById('change-text-btn');
                    const display = document.getElementById('text-display');
                    
                    btn.addEventListener('click', function() {{
                        display.textContent = 'Text changed at ' + new Date().toLocaleTimeString();
                    }});
                }})();
            </script>
        </div>
        """
    }
```

### Using Static Files

You can include static files (CSS, JavaScript, images, etc.) in your extension:

1. Create a `static` directory in your extension package:

```
my-extension/
├── __init__.py
└── static/
    ├── styles.css
    └── script.js
```

2. Access the static files in your components:

```python
@ui_component("styled_component")
def render_styled(self):
    """Render a component with custom styles."""
    return {
        "html": f"""
        <div class="my-extension-component">
            <h3>Styled Component</h3>
            <p>This component uses custom styles.</p>
            
            <style>
                /* Include your styles directly */
                .my-extension-component {{
                    padding: 1rem;
                    border: 1px solid #ccc;
                    border-radius: 0.5rem;
                    background-color: #f9f9f9;
                }}
                
                .my-extension-component h3 {{
                    color: #007bff;
                }}
            </style>
        </div>
        """
    }
```

## Extension Lifecycle

The extension system manages the lifecycle of extensions through the following methods:

1. `initialize(context)`: Called when the extension is registered
2. `activate()`: Called when the extension is enabled
3. `deactivate()`: Called when the extension is disabled
4. `uninstall()`: Called when the extension is uninstalled

You can override these methods to perform custom actions during these lifecycle events.

## Packaging Your Extension

To distribute your extension, you have several options:

1. **Directory**: Simply share the directory containing your extension files.
2. **ZIP file**: Create a ZIP file containing your extension directory.
3. **Git Repository**: Host your extension on GitHub or another Git platform.

Users can install your extension using any of these methods with the `webui-extensions install` command.

## Best Practices

1. **Follow naming conventions**: Use kebab-case for extension names (e.g., `my-extension`).
2. **Include documentation**: Add docstrings to your classes and methods.
3. **Handle errors gracefully**: Catch and handle exceptions to prevent your extension from crashing.
4. **Use settings for configuration**: Allow users to configure your extension through settings.
5. **Test thoroughly**: Test your extension with the development server before distributing it.
6. **Keep extensions focused**: Each extension should have a clear, specific purpose.
7. **Respect user privacy**: Don't collect or transmit user data without explicit consent.
8. **Optimize performance**: Ensure your extension doesn't slow down the UI or backend.

## Advanced Topics

### Dependency Management

If your extension depends on other Python packages, you have two options:

1. **Document dependencies**: List required packages in your documentation.
2. **Include a requirements.txt file**: Users can install dependencies manually.

### Extension Communication

Extensions can communicate with each other through the hook system. Register callbacks for hooks that other extensions might trigger.

### Styling Guidelines

When adding UI components, try to match the Open WebUI styling to provide a consistent user experience:

1. Use the built-in CSS classes when possible.
2. For custom styles, use inline styles or include a scoped CSS block.
3. Consider both light and dark themes in your styling.

### Security Considerations

1. Always validate and sanitize user inputs.
2. Be cautious when evaluating JavaScript code or executing commands.
3. Request only the permissions your extension actually needs.
4. Disclose any network communications or data sharing in your documentation.
