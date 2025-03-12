"""
Hello World extension for Open WebUI.

This is a simple example extension that demonstrates the basic structure
and functionality of Open WebUI extensions.
"""

import logging
from typing import Dict, List, Any

# Import the necessary classes and decorators
# Note: These imports may need adjustment based on your final package structure
try:
    from open_webui_extensions import (
        UIExtension,
        hook,
        ui_component,
        setting,
    )
except ImportError:
    # Fallback for development
    print("Warning: Couldn't import from open_webui_extensions package")
    # Create dummy classes for development
    class UIExtension:
        pass
    def hook(*args, **kwargs):
        def decorator(func): return func
        return decorator
    def ui_component(*args, **kwargs):
        def decorator(func): return func
        return decorator
    def setting(*args, **kwargs):
        def decorator(cls): return cls
        return decorator

logger = logging.getLogger("hello-world-extension")

@setting(name="greeting", default="Hello from Open WebUI Extensions!", description="The greeting to display")
@setting(name="greeting_color", default="#007bff", description="The color of the greeting")
@setting(name="show_in_chat", default=True, type_=bool, description="Whether to show the greeting in chat")
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
    def components(self) -> Dict[str, Any]:
        return {
            "hello_sidebar": self.render_sidebar,
            "hello_chat": self.render_chat,
        }
    
    @property
    def mount_points(self) -> Dict[str, List[str]]:
        return {
            "sidebar": ["hello_sidebar"],
            "chat": ["hello_chat"] if self.show_in_chat else [],
        }
    
    def initialize(self, context: Dict[str, Any]) -> bool:
        """Initialize the extension."""
        logger.info("Initializing Hello World extension")
        return True
    
    def activate(self) -> bool:
        """Activate the extension."""
        logger.info("Activating Hello World extension")
        return True
    
    def deactivate(self) -> bool:
        """Deactivate the extension."""
        logger.info("Deactivating Hello World extension")
        return True
    
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
    
    @ui_component("hello_chat", mount_points=["chat"])
    def render_chat(self) -> Dict[str, Any]:
        """Render the chat component."""
        return {
            "html": f"""
            <div style="margin: 0.5rem 0; padding: 0.5rem; background-color: #f8f9fa; border-radius: 0.25rem;">
                <p style="color: {self.greeting_color};">{self.greeting}</p>
                <p>This component is rendered in the chat interface.</p>
            </div>
            """
        }
    
    @hook("ui_init")
    def on_ui_init(self) -> None:
        """Hook called when the UI is initialized."""
        logger.info("UI initialized - Hello World extension is ready!")

# Create an instance of the extension
extension = HelloWorldExtension()
