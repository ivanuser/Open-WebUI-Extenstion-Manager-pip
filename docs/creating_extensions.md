# Creating Extensions

This guide will walk you through the process of creating extensions for Open WebUI.

## Extension Structure

An extension is a Python package with a specific structure:

```
my-extension/
├── __init__.py        # Main extension entry point
├── static/            # Static assets (optional)
│   ├── styles.css
│   └── scripts.js
```

At minimum, an extension needs an `__init__.py` file that defines an extension class and creates an instance of it.

## Extension Types

Open WebUI supports several types of extensions:

- **UI Extensions**: Add new UI components to Open WebUI
- **API Extensions**: Add new API endpoints
- **Model Extensions**: Integrate new AI models
- **Tool Extensions**: Add new tools or capabilities
- **Theme Extensions**: Customize the appearance

Each type has its own base class that provides specific functionality.

## Basic Extension Structure

Here's a simple example of an extension:

```python
from open_webui_extensions import Extension

class MyExtension(Extension):
    @property
    def name(self) -> str:
        return "my-extension"
    
    @property
    def version(self) -> str:
        return "0.1.0"
    
    @property
    def description(self) -> str:
        return "My awesome extension for Open WebUI."
    
    @property
    def author(self) -> str:
        return "Your Name"
    
    def initialize(self, context: Dict[str, Any]) -> bool:
        """Initialize the extension."""
        return True
    
    def activate(self) -> bool:
        """Activate the extension."""
        return True
    
    def deactivate(self) -> bool:
        """Deactivate the extension."""
        return True

# Create an instance of the extension
extension = MyExtension()
```

Every extension must implement the following properties:

- `name`: A unique identifier for the extension
- `version`: The version of the extension
- `description`: A description of what the extension does
- `author`: The name of the extension author

And the following methods:

- `initialize`: Called when the extension is first loaded
- `activate`: Called when the extension is enabled
- `deactivate`: Called when the extension is disabled

## UI Extensions

UI extensions add new components to the Open WebUI interface. Here's an example:

```python
from open_webui_extensions import UIExtension, ui_component

class MyUIExtension(UIExtension):
    # ... properties ...
    
    @property
    def components(self) -> Dict[str, Any]:
        return {
            "my_sidebar_component": self.render_sidebar,
            "my_chat_component": self.render_chat,
        }
    
    @property
    def mount_points(self) -> Dict[str, List[str]]:
        return {
            "sidebar": ["my_sidebar_component"],
            "chat": ["my_chat_component"],
        }
    
    @ui_component("my_sidebar_component", mount_points=["sidebar"])
    def render_sidebar(self) -> Dict[str, Any]:
        """Render the sidebar component."""
        return {
            "html": """
            <div style="padding: 1rem;">
                <h3>My Sidebar Component</h3>
                <p>This is a custom component in the sidebar.</p>
            </div>
            """
        }
    
    @ui_component("my_chat_component", mount_points=["chat"])
    def render_chat(self) -> Dict[str, Any]:
        """Render the chat component."""
        return {
            "html": """
            <div style="padding: 0.5rem; background-color: #f5f5f5; border-radius: 0.25rem;">
                <p>This is a custom component in the chat interface.</p>
            </div>
            """
        }

# Create an instance of the extension
extension = MyUIExtension()
```

Available mount points include:

- `sidebar`: Components shown in the sidebar
- `header`: Components shown in the header
- `footer`: Components shown in the footer
- `chat`: Components shown in the chat interface
- `settings`: Components shown in the settings page

## API Extensions

API extensions add new API endpoints to Open WebUI. Here's an example:

```python
from open_webui_extensions import APIExtension, api_route

class MyAPIExtension(APIExtension):
    # ... properties ...
    
    @property
    def routes(self) -> List[Any]:
        # This is automatically populated from @api_route decorators
        return []
    
    @api_route("/hello", methods=["GET"])
    async def hello(self) -> Dict[str, Any]:
        """A simple API endpoint."""
        return {
            "message": "Hello from my extension!",
            "extension": self.name,
            "version": self.version,
        }
    
    @api_route("/echo", methods=["POST"])
    async def echo(self, request_body: Dict[str, Any]) -> Dict[str, Any]:
        """Echo the request body."""
        return {
            "extension": self.name,
            "echo": request_body,
        }

# Create an instance of the extension
extension = MyAPIExtension()
```

## Tool Extensions

Tool extensions add new tools that can be used by models or other extensions. Here's an example:

```python
from open_webui_extensions import ToolExtension, tool

class MyToolExtension(ToolExtension):
    # ... properties ...
    
    @property
    def tools(self) -> Dict[str, Callable]:
        # This is automatically populated from @tool decorators
        return {}
    
    @tool("calculator")
    def calculator(self, expression: str) -> Dict[str, Any]:
        """
        Evaluate a mathematical expression.
        
        Args:
            expression: The expression to evaluate.
            
        Returns:
            The result of the evaluation.
        """
        try:
            result = eval(expression)
            return {
                "result": result,
                "expression": expression,
            }
        except Exception as e:
            return {
                "error": str(e),
                "expression": expression,
            }

# Create an instance of the extension
extension = MyToolExtension()
```

## Extension Settings

You can define settings for your extension using the `@setting` decorator:

```python
from open_webui_extensions import Extension, setting

@setting(name="greeting", default="Hello!", description="The greeting to show")
@setting(name="color", default="#007bff", description="The color to use")
@setting(name="enabled", default=True, type_=bool, description="Whether the feature is enabled")
class MyExtension(Extension):
    # ... properties and methods ...

# Create an instance of the extension
extension = MyExtension()
```

Settings can then be accessed as properties on your extension instance:

```python
def some_method(self):
    print(f"Greeting: {self.greeting}")
    print(f"Color: {self.color}")
    print(f"Enabled: {self.enabled}")
```

## Using Hooks

Hooks allow your extension to integrate with Open WebUI at specific points in the application's lifecycle. You can register hook handlers using the `@hook` decorator:

```python
from open_webui_extensions import Extension, hook

class MyExtension(Extension):
    # ... properties ...
    
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

# Create an instance of the extension
extension = MyExtension()
```

## Packaging Your Extension

To package your extension for distribution, create a ZIP file containing your extension directory:

```bash
cd /path/to/my-extension-parent
zip -r my-extension.zip my-extension/
```

Users can then install your extension using the extension manager or the command-line tool:

```bash
webui-extensions install my-extension.zip
```

## Examples

For more detailed examples, see the `example_extensions` directory in this repository. It contains several example extensions that demonstrate different aspects of the extension system.
