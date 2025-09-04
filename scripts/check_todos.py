#!/usr/bin/env python3
"""
Check for TODO/FIXME comments script for pre-commit hooks.

Ensures no TODO/FIXME comments are left in production code.
"""

import os
import sys
import re
from pathlib import Path


def check_todos() -> bool:
    """Check for TODO/FIXME comments in code."""
    root_dir = Path(__file__).parent.parent
    
    # Patterns to search for
    patterns = [
        r'#\s*TODO:?\s*(.+)',
        r'#\s*FIXME:?\s*(.+)',
        r'#\s*XXX:?\s*(.+)',
        r'#\s*HACK:?\s*(.+)',
    ]
    
    # Files to exclude
    exclude_patterns = [
        r'.*\.pyc$',
        r'.*__pycache__.*',
        r'.*\.git.*',
        r'.*node_modules.*',
        r'.*\.venv.*',
        r'.*venv.*',
        r'.*\.env.*',
        r'.*tests.*',
        r'.*test_.*',
        r'.*_test\.py$',
    ]
    
    errors = []
    
    for file_path in root_dir.rglob("*"):
        if not file_path.is_file():
            continue
        
        # Skip excluded files
        if any(re.match(pattern, str(file_path)) for pattern in exclude_patterns):
            continue
        
        # Only check Python files
        if file_path.suffix != '.py':
            continue
        
        try:
            content = file_path.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            for line_num, line in enumerate(lines, 1):
                for pattern in patterns:
                    match = re.search(pattern, line, re.IGNORECASE)
                    if match:
                        relative_path = file_path.relative_to(root_dir)
                        errors.append(
                            f"{relative_path}:{line_num}: {match.group(0).strip()}"
                        )
        
        except (UnicodeDecodeError, PermissionError):
            # Skip files that can't be read
            continue
    
    if errors:
        print("Found TODO/FIXME comments:")
        for error in errors:
            print(f"  ❌ {error}")
        print("\nPlease resolve these comments before committing.")
        return False
    
    print("✅ No TODO/FIXME comments found")
    return True


if __name__ == "__main__":
    success = check_todos()
    sys.exit(0 if success else 1)
