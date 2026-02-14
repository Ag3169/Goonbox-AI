#!/usr/bin/env python3
"""Syntax validation script."""
import ast
import sys

try:
    with open('/home/ag3169/PycharmProjects/AIchatroom/main.py', 'r') as f:
        code = f.read()
    
    ast.parse(code)
    print("✓ main.py syntax is valid")
    
    # Check for key methods
    checks = [
        ('_create_chat', 'Chat creation method'),
        ('_rename_chat', 'Chat rename method'),
        ('_rename_agent_chat', 'Agent chat rename method'),
        ('open_package_installer', 'Package installer opener'),
        ('PackageInstallerWindow', 'Package installer class import'),
    ]
    
    for check_str, description in checks:
        if check_str in code:
            print(f"✓ {description} found")
        else:
            print(f"✗ {description} NOT found")
    
    print("\n✓ All syntax checks passed!")
    sys.exit(0)
    
except SyntaxError as e:
    print(f"✗ Syntax Error: {e}")
    print(f"  Line {e.lineno}: {e.text}")
    sys.exit(1)
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)
