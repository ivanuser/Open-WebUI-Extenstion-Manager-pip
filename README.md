# Open WebUI Extensions

A comprehensive extension system for pip-installed Open WebUI.

## Overview

Open WebUI Extensions provides a framework for developing, installing, and managing extensions for Open WebUI. The system is specifically designed to work with pip-installed instances of Open WebUI, making it easy to enhance Open WebUI without modifying its core code.

## Features

- **Extension Manager**: Admin interface for managing extensions
- **Extension Framework**: Core libraries and interfaces for extension development
- **Extension Registry**: System for discovering and loading extensions
- **Command-line Tools**: Tools for managing extensions from the command line
- **Example Extensions**: Example extensions to get you started

## Installation

```bash
pip install open-webui-extensions
```

After installation, you can set up the extension system:

```bash
webui-extensions setup
```

## Using Extensions

Once the extension system is set up, you can:

1. **Install extensions** from various sources:
   ```bash
   webui-extensions install https://example.com/extension.zip
   ```

2. **Enable and disable extensions**:
   ```bash
   webui-extensions enable extension-name
   webui-extensions disable extension-name
   ```

3. **View installed extensions**:
   ```bash
   webui-extensions list
   ```

4. **Access the web-based Extension Manager** at `/admin/extensions` in your Open WebUI instance

## Creating Extensions

Creating extensions is simple. Here's a minimal example:

```python
from open_webui_extensions import Extension

class HelloWorldExtension(Extension):
    @property
    def name(self) -> str:
        return "hello-world"
    
    @property
    def version(self) -> str:
        return "0.1.0"
    
    @property
    def description(self) -> str:
        return "A simple Hello World extension."
    
    @property
    def author(self) -> str:
        return "Your Name"
    
    def initialize(self, context: Dict[str, Any]) -> bool:
        return True
    
    def activate(self) -> bool:
        return True
    
    def deactivate(self) -> bool:
        return True

# Create an instance of the extension
extension = HelloWorldExtension()
```

For more detailed examples, see the [example_extensions](example_extensions) directory.

## Documentation

- [Getting Started](docs/getting_started.md): Getting started with the extension system
- [Creating Extensions](docs/creating_extensions.md): How to create extensions
- [API Reference](docs/api_reference.md): Detailed API documentation

## Extension Types

Open WebUI Extensions supports several types of extensions:

- **UI Extensions**: Add new UI components to Open WebUI
- **API Extensions**: Add new API endpoints
- **Model Extensions**: Integrate new AI models
- **Tool Extensions**: Add new tools or capabilities
- **Theme Extensions**: Customize the appearance

## Community and Support

- **GitHub Issues**: For bug reports and feature requests
- **Discussions**: For questions and general discussion

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
