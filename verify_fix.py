#!/usr/bin/env python3
"""Quick syntax check for main.py after fix."""
import ast
import sys

try:
    with open('main.py', 'r') as f:
        code = f.read()
    
    ast.parse(code)
    print("✓ main.py syntax is valid!")
    
    # Check that _create_chat is defined
    if 'def _create_chat' in code:
        print("✓ _create_chat method is properly defined")
    else:
        print("✗ _create_chat method NOT found")
        sys.exit(1)
    
    print("\n✓ Application should start successfully!")
    sys.exit(0)
    
except SyntaxError as e:
    print(f"✗ Syntax error: {e}")
    print(f"  Line {e.lineno}: {e.text}")
    sys.exit(1)
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)
