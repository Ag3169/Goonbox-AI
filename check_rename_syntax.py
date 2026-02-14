#!/usr/bin/env python3
"""Syntax validation for the rename chat feature."""
import sys
import ast

try:
    with open('main.py', 'r') as f:
        code = f.read()
    ast.parse(code)
    print("✓ main.py syntax is valid")
    
    # Check for the rename methods
    if '_rename_chat' in code and '_rename_agent_chat' in code:
        print("✓ Rename methods found in code")
    if 'label="Rename"' in code:
        print("✓ Rename menu options found")
    
    print("\n✓ All syntax checks passed!")
except SyntaxError as e:
    print(f"✗ Syntax error in main.py: {e}")
    sys.exit(1)
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)
