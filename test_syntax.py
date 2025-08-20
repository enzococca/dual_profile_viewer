#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test syntax of all Python files in the plugin
"""

import ast
import os
import sys

def check_syntax(filepath):
    """Check if a Python file has valid syntax"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        ast.parse(content)
        return True, "OK"
    except SyntaxError as e:
        return False, f"Line {e.lineno}: {e.msg}"
    except Exception as e:
        return False, str(e)

# Get all Python files
plugin_dir = os.path.dirname(os.path.abspath(__file__))
python_files = []

for root, dirs, files in os.walk(plugin_dir):
    for file in files:
        if file.endswith('.py'):
            python_files.append(os.path.join(root, file))

# Check each file
print("Checking Python syntax in all files...\n")
errors_found = False

for filepath in python_files:
    rel_path = os.path.relpath(filepath, plugin_dir)
    valid, message = check_syntax(filepath)
    
    if valid:
        print(f"✓ {rel_path}")
    else:
        print(f"✗ {rel_path}: {message}")
        errors_found = True

if errors_found:
    print("\n❌ Syntax errors found!")
    sys.exit(1)
else:
    print("\n✅ All files have valid syntax!")
    sys.exit(0)