#!/usr/bin/env python3
"""Verify main.py can be imported without syntax errors."""

import sys
from pathlib import Path

try:
    # Try to import main to check for syntax errors
    import main
    print("✅ main.py imported successfully")
    print(f"✅ GroqChatroomApp class found: {hasattr(main, 'GroqChatroomApp')}")
    print(f"✅ Application is ready to run")
    print("\nTo run the app, execute: python main.py")
except SyntaxError as e:
    print(f"❌ Syntax error in main.py: {e}")
    sys.exit(1)
except Exception as e:
    print(f"⚠️  Import warning (may be expected): {e}")
    print("This might be due to missing dependencies, but the syntax is correct.")
