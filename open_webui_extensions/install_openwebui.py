#!/usr/bin/env python3
"""
Script to install the extension system into Open WebUI.
"""

import os
import sys
import importlib.util
import logging
from pathlib import Path
from typing import Optional, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("webui-extensions.installer")

def find_openwebui_app() -> Optional[Any]:
    """
    Find the Open WebUI FastAPI application.
    
    Returns:
        The FastAPI app object, or None if not found.
    """
    # Method 1: Try to find Open WebUI package
    try:
        openwebui_spec = importlib.util.find_spec("open_webui")
        if openwebui_spec:
            logger.info(f"Found Open WebUI package at {openwebui_spec.origin}")
            
            # Load the main module
            main_path = os.path.join(os.path.dirname(openwebui_spec.origin), "main.py")
            if os.path.exists(main_path):
                logger.info(f"Found Open WebUI main module at {main_path}")
                
                # Import the main module
                spec = importlib.util.spec_from_file_location("open_webui.main", main_path)
                main = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(main)
                
                # Get the FastAPI app
                if hasattr(main, "app"):
                    logger.info("Found FastAPI app in Open WebUI main module")
                    return main.app
                else:
                    logger.warning("FastAPI app not found in Open WebUI main module")
    except Exception as e:
        logger.error(f"Error finding Open WebUI package: {e}")
    
    # Method 2: Try to find common Open WebUI installation paths
    common_paths = [
        "/usr/local/lib/python3.*/site-packages/open_webui/main.py",
        "/usr/lib/python3.*/site-packages/open_webui/main.py",
        os.path.expanduser("~/.local/lib/python3.*/site-packages/open_webui/main.py"),
        os.path.expanduser("~/venv/lib/python3.*/site-packages/open_webui/main.py"),
    ]
    
    for path_pattern in common_paths:
        try:
            import glob
            matching_paths = glob.glob(path_pattern)
            if matching_paths:
                main_path = matching_paths[0]
                logger.info(f"Found Open WebUI main module at {main_path}")
                
                # Import the main module
                spec = importlib.util.spec_from_file_location("open_webui.main", main_path)
                main = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(main)
                
                # Get the FastAPI app
                if hasattr(main, "app"):
                    logger.info("Found FastAPI app in Open WebUI main module")
                    return main.app
                else:
                    logger.warning("FastAPI app not found in Open WebUI main module")
        except Exception as e:
            logger.error(f"Error checking {path_pattern}: {e}")
    
    logger.error("Could not find Open WebUI FastAPI app")
    return None

def install_extension_system() -> bool:
    """
    Install the extension system into Open WebUI.
    
    Returns:
        True if installation was successful, False otherwise.
    """
    # Find the Open WebUI app
    app = find_openwebui_app()
    if app is None:
        logger.error("Could not find Open WebUI FastAPI app. Make sure Open WebUI is installed.")
        print("\nManual installation instructions:")
        print("1. Add the following line to your Open WebUI startup file:")
        print("   from open_webui_extensions.plugin import initialize_extension_system")
        print("2. Add the following line after the FastAPI app is created:")
        print("   app = initialize_extension_system(app)")
        return False
    
    # Import and initialize the extension system
    try:
        from open_webui_extensions.plugin import initialize_extension_system
        
        # Initialize the extension system
        initialize_extension_system(app)
        
        logger.info("Extension system installed successfully!")
        print("\nThe extension system has been installed into Open WebUI.")
        print("To access the extension manager, go to: http://your-openwebui-url/admin/extensions")
        print("\nNOTE: You'll need to restart Open WebUI for the changes to take effect.")
        return True
    except Exception as e:
        logger.error(f"Error installing extension system: {e}")
        print("\nManual installation instructions:")
        print("1. Add the following line to your Open WebUI startup file:")
        print("   from open_webui_extensions.plugin import initialize_extension_system")
        print("2. Add the following line after the FastAPI app is created:")
        print("   app = initialize_extension_system(app)")
        return False

def create_patch_file() -> bool:
    """
    Create a patch file that can be used to manually integrate the extension system.
    
    Returns:
        True if the patch file was created successfully, False otherwise.
    """
    try:
        patch_content = """# Open WebUI Extensions System Patch
# Add this to your Open WebUI startup script or main.py file

# Add this import at the top
from open_webui_extensions.plugin import initialize_extension_system

# Add this line after the FastAPI app is created
# Look for something like "app = FastAPI(...)" and add the next line after it:
app = initialize_extension_system(app)
"""
        
        # Write the patch file
        patch_path = os.path.join(os.getcwd(), "openwebui_extensions_patch.py")
        with open(patch_path, "w") as f:
            f.write(patch_content)
        
        logger.info(f"Patch file created at {patch_path}")
        print(f"\nA patch file has been created at {patch_path}")
        print("You can use this file as a reference for manual integration.")
        return True
    except Exception as e:
        logger.error(f"Error creating patch file: {e}")
        return False

def main():
    """Main entry point for the installer."""
    print("Open WebUI Extensions Installer")
    print("===============================")
    print("This script will install the extension system into your Open WebUI installation.")
    print("")
    
    # Try to install automatically
    if install_extension_system():
        # Create a patch file for reference
        create_patch_file()
        return 0
    
    # If automatic installation fails, create a patch file
    if create_patch_file():
        return 1
    
    return 2

if __name__ == "__main__":
    sys.exit(main())
