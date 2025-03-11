# Example Extensions

This repository contains several example extensions to help you get started developing your own extensions for Open WebUI.

## Hello World Extension

The Hello World extension is a simple UI extension that adds components to the sidebar and chat interface. It demonstrates the basic structure of an extension and the use of settings.

**Path**: [`example_extensions/hello_world`](../example_extensions/hello_world)

**Key Features**:
- Basic UI Extension structure
- UI components for sidebar and chat
- Custom settings with different types
- Hook usage

**Code Snippet**:
```python
@setting(name="greeting", default="Hello from Open WebUI Extensions!", description="The greeting to display")
@setting(name="greeting_color", default="#007bff", description="The color of the greeting")
@setting(name="show_in_chat", default=True, type_=bool, description="Whether to show the greeting in chat")
class HelloWorldExtension(UIExtension):
    # ...
    
    @ui_component("hello_sidebar", mount_points=["sidebar"])
    def render_sidebar(self) -> Dict[str, Any]:
        """Render the sidebar component."""
        return {
            "html": f"""
            <div style="padding: 1rem; text-align: center; color: {self.greeting_color};">
                <h3>{self.greeting}</h3>
                <p>This component is rendered in the sidebar.</p>
            </div>
            """
        }
```

## Weather Tool Extension

The Weather Tool extension demonstrates how to create a more complex extension that implements both UI components and API endpoints. It also shows how to create tools that can be used by models or other extensions.

**Path**: [`example_extensions/weather_tool`](../example_extensions/weather_tool)

**Key Features**:
- UI components with interactive JavaScript
- API endpoints
- Tool implementation
- Advanced settings

**Code Snippet**:
```python
@api_route("/weather/{location}", methods=["GET"])
async def get_weather_api(self, location: str) -> Dict[str, Any]:
    """API endpoint to get weather data."""
    weather_data = self._get_weather_data(location)
    
    if weather_data:
        return {
            "success": True,
            "location": location,
            "weather": weather_data,
        }
    else:
        return {
            "success": False,
            "message": f"Failed to get weather data for {location}",
        }
```

## Creating Your Own Examples

If you've created an extension that you think would be useful for others to learn from, consider contributing it to the `example_extensions` directory. Here's how:

1. Create a new directory under `example_extensions/`
2. Implement your extension following best practices
3. Add documentation to explain what the extension does and how it works
4. Submit a pull request with your example extension

## Running Examples

To run any of these examples, you can install them using the extension manager:

```bash
# From the repository root
webui-extensions install example_extensions/hello_world
webui-extensions install example_extensions/weather_tool
```

Or you can install them directly from their directories:

```bash
cd example_extensions
webui-extensions install hello_world
webui-extensions install weather_tool
```

## Next Steps

After exploring these examples, you should be ready to create your own extensions. See the [Creating Extensions](creating_extensions.md) guide for detailed instructions on how to build your own extensions.
