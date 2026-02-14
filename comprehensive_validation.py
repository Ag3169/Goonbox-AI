#!/usr/bin/env python3
"""Comprehensive syntax and import validation."""
import ast
import sys

def check_syntax(filepath):
    """Check if a Python file has valid syntax."""
    try:
        with open(filepath, 'r') as f:
            code = f.read()
        ast.parse(code)
        return True, "Syntax valid"
    except SyntaxError as e:
        return False, f"Syntax Error at line {e.lineno}: {e.msg}"
    except Exception as e:
        return False, str(e)

files_to_check = [
    '/home/ag3169/PycharmProjects/AIchatroom/main.py',
    '/home/ag3169/PycharmProjects/AIchatroom/package_installer.py',
]

print("=" * 60)
print("SYNTAX VALIDATION REPORT")
print("=" * 60)

all_valid = True
for filepath in files_to_check:
    valid, message = check_syntax(filepath)
    status = "✓ PASS" if valid else "✗ FAIL"
    print(f"\n{status}: {filepath}")
    if not valid:
        print(f"       {message}")
        all_valid = False
    else:
        print(f"       {message}")

print("\n" + "=" * 60)

# Check for critical methods in main.py
print("\nCRITICAL METHOD VERIFICATION:")
print("=" * 60)

with open('/home/ag3169/PycharmProjects/AIchatroom/main.py', 'r') as f:
    main_code = f.read()

critical_methods = [
    '_create_chat',
    '_delete_chat',
    '_rename_chat',
    '_create_agent_chat',
    '_delete_agent_chat',
    '_rename_agent_chat',
    'open_package_installer',
    '_append_ide_output',
]

for method in critical_methods:
    if f'def {method}' in main_code:
        print(f"✓ {method}")
    else:
        print(f"✗ {method} - NOT FOUND")
        all_valid = False

print("\n" + "=" * 60)

if all_valid:
    print("✓ ALL CHECKS PASSED - Application should start successfully!")
    sys.exit(0)
else:
    print("✗ SOME CHECKS FAILED - Please review the errors above")
    sys.exit(1)
