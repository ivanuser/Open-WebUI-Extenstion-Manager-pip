# Manually Integrating Extensions with Open WebUI

This guide provides detailed instructions for manually integrating the Open WebUI Extensions system with your pip-installed Open WebUI instance.

## Overview

When Open WebUI is installed via pip, integrating extensions can be challenging since you don't want to modify the installed package files directly. This guide provides several methods to integrate the extension system without changing the core Open WebUI files.

## Method 1: Using the Wrapper Script

This is the recommended approach as it doesn't require modifying any installed files.

1. **Create a wrapper script** called `run_openwebui_with_extensions.py`:

```python
#!/usr/bin/env python3
import sys
import importlib.util
import open_webui.main

# Import and apply extensions
try:
    from open_webui_extensions.plugin import initialize_extension_system
    open_webui.main.app = initialize_extension_system(open_webui.main.app)
    print('Open WebUI Extensions initialized successfully!')
except Exception as e:
    print(f'Error initializing Open WebUI Extensions: {e}')

# Start Open WebUI - find and call the main method if it exists
if hasattr(open_webui.main, 'main') and callable(open_webui.main.main):
    open_webui.main.main()
else:
    # Try to run using uvicorn directly
    import uvicorn
    import os
    
    # Get host and port
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 8080))
    
    print(f"Starting Open WebUI at http://{host}:{port}")
    uvicorn.run("open_webui.main:app", host=host, port=port, reload=False)
```

2. **Make the script executable**:

```bash
chmod +x run_openwebui_with_extensions.py
```

3. **Run Open WebUI using this wrapper script**:

```bash
./run_openwebui_with_extensions.py
```

## Method 2: Modifying the Main.py File

This method involves directly modifying the Open WebUI main.py file. This works, but the changes may be lost if you update Open WebUI.

1. **Locate your Open WebUI main.py file**:

```bash
# For pip installations, it's usually at:
/path/to/python/site-packages/open_webui/main.py

# For example:
# /home/username/venv/lib/python3.11/site-packages/open_webui/main.py
```

2. **Backup the original file**:

```bash
cp /path/to/site-packages/open_webui/main.py /path/to/site-packages/open_webui/main.py.bak
```

3. **Edit the main.py file** and add the following code:

At the top with other imports:
```python
# Try to import the extension system
try:
    from open_webui_extensions.plugin import initialize_extension_system
    EXTENSIONS_AVAILABLE = True
except ImportError:
    EXTENSIONS_AVAILABLE = False
    print("Open WebUI Extensions not installed. Install with: pip install open-webui-extensions")
```

After the FastAPI app is created (`app = FastAPI(...)`):
```python
# Initialize extension system if available
if EXTENSIONS_AVAILABLE:
    try:
        app = initialize_extension_system(app)
        print("Open WebUI Extensions initialized successfully!")
    except Exception as e:
        print(f"Error initializing Open WebUI Extensions: {e}")
```

4. **Save the file** and restart Open WebUI

## Method 3: Creating a Custom Entry Point

This method creates a new entry point script without modifying Open WebUI files.

1. **Create a directory** for your custom Open WebUI setup:

```bash
mkdir ~/my-open-webui
cd ~/my-open-webui
```

2. **Create an entry point script** called `app.py`:

```python
#!/usr/bin/env python3
"""
Custom entry point for Open WebUI with extensions.
"""

import sys
import importlib.util

# Import the original app
from open_webui.main import app as original_app

# Apply extensions
from open_webui_extensions.plugin import initialize_extension_system
app = initialize_extension_system(original_app)

# This allows running with 'uvicorn app:app'
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8080)
```

3. **Run using uvicorn**:

```bash
uvicorn app:app --host 0.0.0.0 --port 8080
```

## Method 4: Creating a systemd Service

If you're running Open WebUI as a service, you can create a custom service file:

1. **Create a wrapper script** as in Method 1

2. **Create a systemd service file** at `/etc/systemd/system/open-webui-with-extensions.service`:

```ini
[Unit]
Description=Open WebUI with Extensions
After=network.target

[Service]
User=yourusername
WorkingDirectory=/path/to/wrapper/script/directory
ExecStart=/path/to/python /path/to/wrapper/script/run_openwebui_with_extensions.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

3. **Enable and start the service**:

```bash
sudo systemctl daemon-reload
sudo systemctl enable open-webui-with-extensions.service
sudo systemctl start open-webui-with-extensions.service
```

## Troubleshooting

### Extension System Not Loading

If the extension system doesn't appear to be loading:

1. Check that open-webui-extensions is installed:
```bash
pip list | grep open-webui-extensions
```

2. Check for errors in the Open WebUI logs

3. Try running with debug logging:
```bash
export LOGLEVEL=DEBUG
./run_openwebui_with_extensions.py
```

### Cannot Access Extension Manager

If you can't access the extension manager at `/admin/extensions`:

1. Make sure you've set up the extension system:
```bash
webui-extensions setup
```

2. Check if the extension system is running separately:
```bash
python -m open_webui_extensions.dev_server
# Then access http://localhost:5000/admin/extensions
```

3. Try accessing directly through `/admin/extensions` in your Open WebUI URL

### Database Connection Errors

If you see database connection errors:

1. Make sure Open WebUI is properly configured and can access its database

2. Try using the wrapper script approach (Method 1) which doesn't interfere with Open WebUI initialization
