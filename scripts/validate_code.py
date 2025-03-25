#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script to validate code formatting and conventions.
"""

import os
import sys
import importlib.util
import re
from pathlib import Path

def check_file_executable(file_path):
    """Check if a Python file is executable."""
    is_executable = os.access(file_path, os.X_OK)
    if not is_executable:
        print(f"⚠️  Warning: {file_path} is not executable. Consider running: chmod +x {file_path}")
    return is_executable

def check_shebang(file_contents):
    """Check if file has proper shebang."""
    first_line = file_contents.split('\n')[0] if file_contents else ""
    has_shebang = first_line.startswith("#!/usr/bin/env python3")
    if not has_shebang:
        print(f"⚠️  Warning: File does not have proper shebang (#!/usr/bin/env python3)")
    return has_shebang

def check_docstring(file_contents):
    """Check if file has a docstring."""
    # Simple check for triple quotes after imports
    lines = file_contents.split('\n')
    has_docstring = False
    import_section_passed = False
    
    for i, line in enumerate(lines):
        if re.match(r'^import |^from ', line):
            import_section_passed = True
        elif import_section_passed and line.strip() and not line.startswith('#'):
            if '"""' in line or "'''" in line:
                has_docstring = True
            break
    
    if not has_docstring:
        print(f"⚠️  Warning: File may be missing a module docstring")
    return has_docstring

def check_type_hints(file_contents):
    """Check for the presence of type hints."""
    has_type_hints = 'typing' in file_contents or re.search(r'def [a-zA-Z0-9_]+\(.+: [a-zA-Z]+[\[\],\s]*\)', file_contents)
    if not has_type_hints:
        print(f"⚠️  Warning: File may be missing type hints")
    return has_type_hints

def validate_python_file(file_path):
    """Validate a Python file for best practices."""
    print(f"\nValidating {file_path}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        contents = f.read()
    
    # Run checks
    executable = check_file_executable(file_path)
    shebang = check_shebang(contents)
    docstring = check_docstring(contents)
    type_hints = check_type_hints(contents)
    
    # Try to import the file to check for syntax errors
    try:
        spec = importlib.util.spec_from_file_location("module.name", file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        print("✅ File imports successfully without syntax errors")
    except Exception as e:
        print(f"❌ Error importing file: {e}")
        return False
    
    # Calculate score
    checks = [executable, shebang, docstring, type_hints]
    score = sum(1 for check in checks if check) / len(checks) * 100
    print(f"Overall score: {score:.1f}%")
    
    return score > 75

def main():
    """Main function to validate all Python files."""
    repo_dir = Path(__file__).parent.parent
    python_files = list(repo_dir.glob('*.py')) + list(repo_dir.glob('tests/*.py'))
    
    print(f"Found {len(python_files)} Python files to validate")
    
    all_valid = True
    for file_path in python_files:
        if not validate_python_file(str(file_path)):
            all_valid = False
    
    if all_valid:
        print("\n✅ All files meet basic standards")
        return 0
    else:
        print("\n⚠️  Some files need improvement")
        return 1

if __name__ == "__main__":
    sys.exit(main())