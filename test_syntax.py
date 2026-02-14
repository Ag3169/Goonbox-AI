#!/usr/bin/env python3
"""Quick syntax check for main.py"""
import sys
try:
    import main
    print("✓ main.py syntax is valid")
    print("✓ GroqChatroomApp class exists:", hasattr(main, 'GroqChatroomApp'))
    # Check that new methods exist
    app_class = main.GroqChatroomApp
    print("✓ _parse_agent_commands method exists:", hasattr(app_class, '_parse_agent_commands'))
    print("✓ _validate_and_resolve_path_for_agent method exists:", hasattr(app_class, '_validate_and_resolve_path_for_agent'))
    print("✓ _execute_agent_command method exists:", hasattr(app_class, '_execute_agent_command'))
    print("\nAll checks passed!")
except SyntaxError as e:
    print(f"✗ Syntax error in main.py: {e}", file=sys.stderr)
    sys.exit(1)
except Exception as e:
    print(f"✗ Error: {e}", file=sys.stderr)
    sys.exit(1)
