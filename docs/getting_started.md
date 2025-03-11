# Getting Started with Open WebUI Extensions

This guide will help you get started with the Open WebUI Extensions system.

## Installation

The Open WebUI Extensions system can be installed via pip:

```bash
pip install open-webui-extensions
```

This will install the extension system and its dependencies, as well as a command-line tool called `webui-extensions` that you can use to manage extensions.

## Setting Up the Extension System

After installation, you need to set up the extension system by running:

```bash
webui-extensions setup
```

This will create the necessary directories and configuration files for the extension system. By default, extensions will be stored in `~/.openwebui/extensions`.

If you want to specify a different location for your extensions, you can use the `--dir` option:

```bash
webui-extensions setup --dir /path/to/extensions
```

## Installing Extensions

You can install extensions from various sources:

### From a URL:

```bash
webui-extensions install https://example.com/my-extension.zip
```

### From a Local Directory:

```bash
webui-extensions install /path/to/my-extension
```

### From a ZIP File:

```bash
webui-extensions install /path/to/my-extension.zip
```

## Managing Extensions

### Listing Installed Extensions

```bash
webui-extensions list
```

### Getting Extension Information

```bash
webui-extensions info extension-name
```

### Enabling Extensions

```bash
webui-extensions enable extension-name
```

### Disabling Extensions

```bash
webui-extensions disable extension-name
```

### Uninstalling Extensions

```bash
webui-extensions uninstall extension-name
```

## Using the Extension Manager UI

The extension system also provides a web-based UI for managing extensions. After installing the extension system, you can access the Extension Manager UI at:

```
http://localhost:8000/admin/extensions
```

(Replace `localhost:8000` with the URL where your Open WebUI is running.)

## Integration with Open WebUI

The extension system integrates with Open WebUI through a plugin system. When you install the `open-webui-extensions` package, it registers a plugin with Open WebUI that adds extension capabilities.

If you're developing Open WebUI or want to manually integrate the extension system, you can use the following code:

```python
from open_webui_extensions.plugin import OpenWebUIExtensionsPlugin

# Initialize the plugin with your FastAPI app
plugin = OpenWebUIExtensionsPlugin()
plugin.initialize(app)
```

## Next Steps

- [Creating Extensions](creating_extensions.md): Learn how to create your own extensions
- [Extension API Reference](api_reference.md): Detailed documentation of the extension API
- [Example Extensions](example_extensions.md): Examples of extensions to learn from
