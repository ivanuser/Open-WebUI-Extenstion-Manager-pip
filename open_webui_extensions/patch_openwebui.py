#!/usr/bin/env python3
"""
Script to patch Open WebUI with the extension system.
"""

import os
import sys
import re
import logging
import shutil
from pathlib import Path
from typing import Optional, List, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("webui-extensions.patcher")

def find_openwebui_main_path() -> Optional[str]:
    """
    Find the path to Open WebUI's main.py file.
    
    Returns:
        The path to the main.py file, or None if not found.
    """
    # Method 1: Check common installation paths
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
                return matching_paths[0]
        except Exception as e:
            logger.error(f"Error checking {path_pattern}: {e}")
    
    # Method 2: Try to find Open WebUI package
    try:
        import importlib.util
        openwebui_spec = importlib.util.find_spec("open_webui")
        if openwebui_spec:
            logger.info(f"Found Open WebUI package at {openwebui_spec.origin}")
            
            # Look for main.py
            main_path = os.path.join(os.path.dirname(openwebui_spec.origin), "main.py")
            if os.path.exists(main_path):
                return main_path
    except Exception as e:
        logger.error(f"Error finding Open WebUI package: {e}")
    
    # Method 3: Ask the user
    user_path = input("Enter the path to Open WebUI's main.py file: ")
    if os.path.isfile(user_path) and os.path.basename(user_path) == "main.py":
        return user_path
    
    logger.error("Could not find Open WebUI's main.py file")
    return None

def backup_file(file_path: str) -> Optional[str]:
    """
    Create a backup of a file.
    
    Args:
        file_path: The path to the file to backup.
        
    Returns:
        The path to the backup file, or None if backup failed.
    """
    try:
        backup_path = f"{file_path}.bak"
        shutil.copyfile(file_path, backup_path)
        logger.info(f"Created backup at {backup_path}")
        return backup_path
    except Exception as e:
        logger.error(f"Error creating backup: {e}")
        return None

def find_app_creation(content: str) -> Optional[Tuple[int, int]]:
    """
    Find where the FastAPI app is created in the file.
    
    Args:
        content: The content of the file.
        
    Returns:
        A tuple of (start_line, end_line), or None if not found.
    """
    # Look for app = FastAPI(...) pattern
    lines = content.splitlines()
    app_pattern = re.compile(r'app\s*=\s*FastAPI\s*\(')
    
    for i, line in enumerate(lines):
        if app_pattern.search(line):
            # Find the end of the statement (might be multi-line)
            end_line = i
            parentheses_count = line.count('(') - line.count(')')
            while parentheses_count > 0 and end_line < len(lines) - 1:
                end_line += 1
                parentheses_count += lines[end_line].count('(') - lines[end_line].count(')')
            
            return (i, end_line)
    
    return None

def patch_main_file(main_path: str) -> bool:
    """
    Patch the Open WebUI main.py file to include the extension system.
    
    Args:
        main_path: The path to the main.py file.
        
    Returns:
        True if patching was successful, False otherwise.
    """
    try:
        # Read the file
        with open(main_path, 'r') as f:
            content = f.read()
        
        # Check if already patched
        if "open_webui_extensions.plugin" in content:
            logger.info("File already contains extension system imports")
            return True
        
        # Backup the file
        backup_path = backup_file(main_path)
        if not backup_path:
            return False
        
        # Find the import section to add our import
        lines = content.splitlines()
        
        # Find the last import line
        last_import_line = 0
        for i, line in enumerate(lines):
            if line.strip().startswith(('import ', 'from ')):
                last_import_line = i
        
        # Add our import after the last import
        lines.insert(last_import_line + 1, "# Extension system import")
        lines.insert(last_import_line + 2, "from open_webui_extensions.plugin import initialize_extension_system")
        lines.insert(last_import_line + 3, "")
        
        # Find where the app is created
        app_lines = find_app_creation(content)
        if not app_lines:
            logger.error("Could not find FastAPI app creation in the file")
            return False
        
        # Add our initialization after the app creation
        end_line = app_lines[1]
        lines.insert(end_line + 1, "# Initialize extension system")
        lines.insert(end_line + 2, "app = initialize_extension_system(app)")
        lines.insert(end_line + 3, "")
        
        # Write the modified content back to the file
        with open(main_path, 'w') as f:
            f.write('\n'.join(lines))
        
        logger.info(f"Successfully patched {main_path}")
        print(f"\nSuccessfully patched {main_path}")
        print("The extension system has been integrated into Open WebUI.")
        print("You'll need to restart Open WebUI for the changes to take effect.")
        
        return True
    except Exception as e:
        logger.error(f"Error patching main file: {e}")
        return False

def restore_backup(main_path: str) -> bool:
    """
    Restore the backup of the main.py file.
    
    Args:
        main_path: The path to the main.py file.
        
    Returns:
        True if restoration was successful, False otherwise.
    """
    backup_path = f"{main_path}.bak"
    if not os.path.exists(backup_path):
        logger.error(f"Backup file {backup_path} not found")
        return False
    
    try:
        shutil.copyfile(backup_path, main_path)
        logger.info(f"Restored {main_path} from backup")
        return True
    except Exception as e:
        logger.error(f"Error restoring backup: {e}")
        return False

def main():
    """Main entry point for the patcher."""
    print("Open WebUI Extensions Patcher")
    print("=============================")
    print("This script will patch your Open WebUI installation to include the extension system.")
    print("A backup of the original file will be created before making any changes.")
    print("")
    
    # Find the main.py file
    main_path = find_openwebui_main_path()
    if not main_path:
        print("Could not find Open WebUI's main.py file.")
        print("Please specify the path manually using the --path option.")
        return 1
    
    # Ask for confirmation
    print(f"Found Open WebUI main.py at: {main_path}")
    confirmation = input("Do you want to patch this file? (y/n): ")
    if confirmation.lower() != 'y':
        print("Patching cancelled.")
        return 0
    
    # Patch the file
    if patch_main_file(main_path):
        return 0
    
    # Ask if we should restore the backup
    print("Patching failed.")
    restore = input("Do you want to restore the backup? (y/n): ")
    if restore.lower() == 'y':
        if restore_backup(main_path):
            print("Backup restored successfully.")
        else:
            print("Failed to restore backup.")
    
    return 1

if __name__ == "__main__":
    sys.exit(main())
