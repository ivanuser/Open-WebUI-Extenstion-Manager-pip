#!/usr/bin/env python3
"""
Script to generate a manual patch file for Open WebUI.
"""

import os
import sys
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("webui-extensions.manual-patch")

def generate_patch_file():
    """Generate a patch file to integrate extensions into Open WebUI."""
    patch_content = """
# Open WebUI Extensions Integration
# Add this code to your Open WebUI main.py file

# Add these imports at the top of the file with other imports
import os
import sys
import importlib.util

# Try to import the extension system
try:
    from open_webui_extensions.plugin import initialize_extension_system
    EXTENSIONS_AVAILABLE = True
except ImportError:
    EXTENSIONS_AVAILABLE = False
    print("Open WebUI Extensions not installed. Install with: pip install open-webui-extensions")

# Add this code after the FastAPI app is created (after the 'app = FastAPI(...)' line)
if EXTENSIONS_AVAILABLE:
    try:
        # Initialize the extension system
        app = initialize_extension_system(app)
        print("Open WebUI Extensions initialized successfully!")
    except Exception as e:
        print(f"Error initializing Open WebUI Extensions: {e}")
"""

    # Write the patch file
    try:
        patch_path = os.path.join(os.getcwd(), "openwebui_extensions_patch.txt")
        with open(patch_path, "w") as f:
            f.write(patch_content)
        
        logger.info(f"Patch file created at: {patch_path}")
        print(f"\nPatch file created at: {patch_path}")
        print("\nManual Integration Instructions:")
        print("--------------------------------")
        print("1. Open your Open WebUI main.py file at:")
        print("   /home/ihoner/ai_dev/venv/lib/python3.11/site-packages/open_webui/main.py")
        print("\n2. Add the imports from the patch file at the top with other imports")
        print("\n3. Find the line where the FastAPI app is created (app = FastAPI(...))")
        print("\n4. Add the extension initialization code after this line")
        print("\n5. Save the file and restart Open WebUI")
        print("\nAlternative Method:")
        print("-------------------")
        print("If you're not comfortable modifying the main.py file directly, you can create a")
        print("wrapper script that runs Open WebUI with the extensions enabled:")
        print("\n1. Create a file called 'run_openwebui.py' with the following content:")
        print("\n```python")
        print("#!/usr/bin/env python3")
        print("import sys")
        print("import importlib.util")
        print("import open_webui.main")
        print("")
        print("# Import and apply extensions")
        print("try:")
        print("    from open_webui_extensions.plugin import initialize_extension_system")
        print("    open_webui.main.app = initialize_extension_system(open_webui.main.app)")
        print("    print('Open WebUI Extensions initialized successfully!')")
        print("except Exception as e:")
        print("    print(f'Error initializing Open WebUI Extensions: {e}')")
        print("")
        print("# Start Open WebUI - find and call the main method if it exists")
        print("if hasattr(open_webui.main, 'main') and callable(open_webui.main.main):")
        print("    open_webui.main.main()")
        print("```")
        print("\n2. Make the script executable: chmod +x run_openwebui.py")
        print("\n3. Run Open WebUI with this script: ./run_openwebui.py")
        
        return True
    except Exception as e:
        logger.error(f"Error creating patch file: {e}")
        return False

def main():
    """Main entry point for the script."""
    print("Open WebUI Extensions Manual Patch Generator")
    print("===========================================")
    print("This script will generate a patch file with instructions to manually")
    print("integrate the extensions system into Open WebUI.")
    print("")
    
    return 0 if generate_patch_file() else 1

if __name__ == "__main__":
    sys.exit(main())
