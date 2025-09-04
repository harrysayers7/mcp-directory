#!/usr/bin/env python3
"""
Check server structure script for pre-commit hooks.

Validates that all MCP servers have the required files and structure.
"""

import os
import sys
from pathlib import Path


def check_server_structure() -> bool:
    """Check that all servers have required structure."""
    root_dir = Path(__file__).parent.parent
    servers_dir = root_dir / "servers"
    
    required_files = [
        "main.py",
        "pyproject.toml",
        "Dockerfile",
        "README.md",
    ]
    
    required_dirs = [
        "tests",
    ]
    
    errors = []
    
    for server_dir in servers_dir.iterdir():
        if not server_dir.is_dir() or server_dir.name == "template":
            continue
        
        server_name = server_dir.name
        print(f"Checking server: {server_name}")
        
        # Check required files
        for file_name in required_files:
            file_path = server_dir / file_name
            if not file_path.exists():
                errors.append(f"Missing file: {server_name}/{file_name}")
        
        # Check required directories
        for dir_name in required_dirs:
            dir_path = server_dir / dir_name
            if not dir_path.exists():
                errors.append(f"Missing directory: {server_name}/{dir_name}")
        
        # Check main.py has required functions
        main_py = server_dir / "main.py"
        if main_py.exists():
            content = main_py.read_text()
            if "def main()" not in content:
                errors.append(f"Missing main() function in {server_name}/main.py")
            if "FastMCP" not in content:
                errors.append(f"Missing FastMCP import in {server_name}/main.py")
    
    if errors:
        print("Structure validation failed:")
        for error in errors:
            print(f"  ❌ {error}")
        return False
    
    print("✅ All servers have required structure")
    return True


if __name__ == "__main__":
    success = check_server_structure()
    sys.exit(0 if success else 1)
