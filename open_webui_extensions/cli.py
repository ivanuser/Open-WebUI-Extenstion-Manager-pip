#!/usr/bin/env python3
"""
Command-line interface for Open WebUI Extensions.
"""

import os
import sys
import argparse
import logging
import importlib
import pkg_resources
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger("webui-extensions")

def get_parser():
    """Get the argument parser."""
    parser = argparse.ArgumentParser(description="Open WebUI Extensions CLI")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List installed extensions")
    
    # Install command
    install_parser = subparsers.add_parser("install", help="Install an extension")
    install_parser.add_argument("source", help="Extension source (path or URL)")
    
    # Uninstall command
    uninstall_parser = subparsers.add_parser("uninstall", help="Uninstall an extension")
    uninstall_parser.add_argument("name", help="Extension name")
    
    # Enable command
    enable_parser = subparsers.add_parser("enable", help="Enable an extension")
    enable_parser.add_argument("name", help="Extension name")
    
    # Disable command
    disable_parser = subparsers.add_parser("disable", help="Disable an extension")
    disable_parser.add_argument("name", help="Extension name")
    
    # Info command
    info_parser = subparsers.add_parser("info", help="Show extension information")
    info_parser.add_argument("name", help="Extension name")

    # Setup command
    setup_parser = subparsers.add_parser("setup", help="Set up extension system")
    setup_parser.add_argument("--dir", help="Extensions directory", default=None)
    
    return parser

def find_openwebui_config():
    """Find the Open WebUI configuration file."""
    # Places to look for Open WebUI config
    config_paths = [
        Path.home() / ".config" / "openwebui" / "config.json",
        Path.home() / ".openwebui" / "config.json",
        Path("/etc/openwebui/config.json"),
        Path("./config.json"),
    ]
    
    for path in config_paths:
        if path.exists():
            return path
    
    return None

def setup_extensions_dir(specified_dir=None):
    """Set up the extensions directory."""
    from .extension_system.utils import setup_extensions_directory
    
    # Find an appropriate directory for extensions
    if specified_dir:
        extensions_dir = Path(specified_dir)
    else:
        # Try to find Open WebUI's config to see if it specifies an extensions directory
        config_file = find_openwebui_config()
        if config_file:
            import json
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                if config.get('extensions', {}).get('directory'):
                    extensions_dir = Path(config['extensions']['directory'])
                else:
                    # Config exists but doesn't specify extensions directory
                    extensions_dir = config_file.parent / "extensions"
            except:
                # If there's any error reading the config, use a default
                extensions_dir = Path.home() / ".openwebui" / "extensions"
        else:
            # No config found, use a default location
            extensions_dir = Path.home() / ".openwebui" / "extensions"
    
    # Make sure the directory exists
    return setup_extensions_directory(extensions_dir)

def list_extensions():
    """List installed extensions."""
    from .extension_system.registry import get_registry
    
    try:
        registry = get_registry()
        extensions = registry.list_extensions()
        
        if not extensions:
            print("No extensions installed.")
            return
        
        print("Installed extensions:")
        for ext in extensions:
            status = "ACTIVE" if ext.active else "INACTIVE"
            print(f"- {ext.name} (v{ext.version}) [{status}]")
            print(f"  {ext.description}")
    except Exception as e:
        logger.error(f"Error listing extensions: {e}")
        sys.exit(1)

def install_extension(source):
    """Install an extension."""
    from .extension_system.registry import get_registry
    
    try:
        registry = get_registry()
        success, name, message = registry.install_extension(source)
        
        if success:
            print(f"Successfully installed extension '{name}'")
        else:
            print(f"Failed to install extension: {message}")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Error installing extension: {e}")
        sys.exit(1)

def uninstall_extension(name):
    """Uninstall an extension."""
    from .extension_system.registry import get_registry
    
    try:
        registry = get_registry()
        success, message = registry.uninstall_extension(name)
        
        if success:
            print(f"Successfully uninstalled extension '{name}'")
        else:
            print(f"Failed to uninstall extension: {message}")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Error uninstalling extension: {e}")
        sys.exit(1)

def enable_extension(name):
    """Enable an extension."""
    from .extension_system.registry import get_registry
    
    try:
        registry = get_registry()
        success, message = registry.enable_extension(name)
        
        if success:
            print(f"Successfully enabled extension '{name}'")
        else:
            print(f"Failed to enable extension: {message}")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Error enabling extension: {e}")
        sys.exit(1)

def disable_extension(name):
    """Disable an extension."""
    from .extension_system.registry import get_registry
    
    try:
        registry = get_registry()
        success, message = registry.disable_extension(name)
        
        if success:
            print(f"Successfully disabled extension '{name}'")
        else:
            print(f"Failed to disable extension: {message}")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Error disabling extension: {e}")
        sys.exit(1)

def show_extension_info(name):
    """Show extension information."""
    from .extension_system.registry import get_registry
    
    try:
        registry = get_registry()
        info = registry.get_extension_info(name)
        
        if not info:
            print(f"Extension '{name}' not found.")
            sys.exit(1)
        
        print(f"Extension: {info.name} (v{info.version})")
        print(f"Description: {info.description}")
        print(f"Author: {info.author}")
        print(f"Type: {info.type}")
        print(f"Status: {'ACTIVE' if info.active else 'INACTIVE'}")
        
        if info.dependencies:
            print("Dependencies:")
            for dep in info.dependencies:
                print(f"- {dep}")
        
        if hasattr(info, 'settings') and info.settings:
            print("Settings:")
            for key, setting in info.settings.items():
                value = setting.get('value', setting.get('default', 'None'))
                print(f"- {key}: {value}")
    except Exception as e:
        logger.error(f"Error showing extension info: {e}")
        sys.exit(1)

def main():
    """Main entry point."""
    parser = get_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    # Setup command is handled separately because it initializes the system
    if args.command == "setup":
        try:
            extensions_dir = setup_extensions_dir(args.dir)
            print(f"Extension system set up successfully at {extensions_dir}")
            return 0
        except Exception as e:
            logger.error(f"Error setting up extension system: {e}")
            return 1
    
    # For all other commands, we need to ensure the extension system is set up
    try:
        from .extension_system.registry import initialize_registry
        initialize_registry()
    except Exception as e:
        logger.error(f"Error initializing extension system: {e}")
        logger.error("Run 'webui-extensions setup' first to set up the extension system.")
        return 1
    
    # Handle commands
    if args.command == "list":
        list_extensions()
    elif args.command == "install":
        install_extension(args.source)
    elif args.command == "uninstall":
        uninstall_extension(args.name)
    elif args.command == "enable":
        enable_extension(args.name)
    elif args.command == "disable":
        disable_extension(args.name)
    elif args.command == "info":
        show_extension_info(args.name)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
