#!/usr/bin/env python3
"""
Wrapper script to run Open WebUI with extensions enabled.

This script imports the Open WebUI main module, applies the extension system,
and then runs Open WebUI. This approach avoids modifying the original files.
"""

import os
import sys
import importlib
import importlib.util
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("webui-extensions-wrapper")

def main():
    """Main entry point."""
    print("Open WebUI Extensions Wrapper")
    print("===========================")
    print("This script runs Open WebUI with the extensions system enabled.")
    print("")
    
    # Try to import Open WebUI
    try:
        logger.info("Importing Open WebUI...")
        import open_webui
        import open_webui.main
        
        # Check if the app exists
        if not hasattr(open_webui.main, "app"):
            logger.error("Could not find the FastAPI app in Open WebUI.")
            print("Error: Could not find the FastAPI app in Open WebUI.")
            return 1
        
        # Import and apply extensions
        try:
            logger.info("Importing extension system...")
            from open_webui_extensions.plugin import initialize_extension_system
            
            logger.info("Initializing extension system...")
            open_webui.main.app = initialize_extension_system(open_webui.main.app)
            
            logger.info("Extension system initialized successfully!")
            print("Open WebUI Extensions initialized successfully!")
        except Exception as e:
            logger.error(f"Error initializing extensions: {e}")
            print(f"Error initializing extensions: {e}")
            return 1
        
        # Find a way to run Open WebUI
        if hasattr(open_webui.main, "main") and callable(open_webui.main.main):
            logger.info("Starting Open WebUI...")
            print("Starting Open WebUI...")
            open_webui.main.main()
            return 0
        else:
            # Try to run using uvicorn directly
            logger.info("No 'main' function found, trying to run with uvicorn...")
            import uvicorn
            
            # Get app info
            app_module = "open_webui.main"
            app_attr = "app"
            
            # Get host and port
            host = os.environ.get("HOST", "0.0.0.0")
            port = int(os.environ.get("PORT", 8080))
            
            print(f"Starting Open WebUI at http://{host}:{port}")
            uvicorn.run(f"{app_module}:{app_attr}", host=host, port=port, reload=False)
            return 0
        
    except ImportError as e:
        logger.error(f"Error importing Open WebUI: {e}")
        print(f"Error: {e}")
        print("Make sure Open WebUI is installed with: pip install open-webui")
        return 1
    except Exception as e:
        logger.error(f"Error running Open WebUI: {e}")
        print(f"Error running Open WebUI: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
