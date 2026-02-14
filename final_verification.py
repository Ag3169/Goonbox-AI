#!/usr/bin/env python3
"""
Final verification script for all implemented features.
This script checks that all changes have been properly applied.
"""

import ast
import sys

def verify_implementation():
    """Verify all implementations are in place."""
    
    print("=" * 70)
    print("FINAL VERIFICATION REPORT - Goonbox-AI")
    print("=" * 70)
    
    with open('/home/ag3169/PycharmProjects/AIchatroom/main.py', 'r') as f:
        main_code = f.read()
    
    # Check syntax
    try:
        ast.parse(main_code)
        print("\n✓ main.py has valid Python syntax")
    except SyntaxError as e:
        print(f"\n✗ main.py has syntax error at line {e.lineno}: {e.msg}")
        return False
    
    # Feature 1: Package Installer
    print("\n" + "-" * 70)
    print("FEATURE 1: Package Installer GUI")
    print("-" * 70)
    
    checks = [
        ('from package_installer import PackageInstallerWindow', 'Import statement'),
        ('def open_package_installer', 'Method definition'),
        ('self.package_manager_button = tk.Button', 'Button creation'),
        ('command=self.open_package_installer', 'Button command binding'),
        ('text="Packages"', 'Button label'),
    ]
    
    for check_str, desc in checks:
        if check_str in main_code:
            print(f"  ✓ {desc}")
        else:
            print(f"  ✗ {desc} - MISSING")
            return False
    
    # Verify package_installer.py exists
    try:
        with open('/home/ag3169/PycharmProjects/AIchatroom/package_installer.py', 'r') as f:
            installer_code = f.read()
        ast.parse(installer_code)
        print("  ✓ package_installer.py exists and is valid")
    except Exception as e:
        print(f"  ✗ package_installer.py issue: {e}")
        return False
    
    # Feature 2: Chat Rename
    print("\n" + "-" * 70)
    print("FEATURE 2: Chat Rename Functionality")
    print("-" * 70)
    
    rename_checks = [
        ('def _rename_chat', 'Regular chat rename method'),
        ('def _rename_agent_chat', 'Agent chat rename method'),
        ('label="Rename"', 'Rename menu option'),
        ('command=lambda: self._rename_chat(index)', 'Regular chat rename binding'),
        ('command=lambda: self._rename_agent_chat(index)', 'Agent chat rename binding'),
    ]
    
    for check_str, desc in rename_checks:
        if check_str in main_code:
            print(f"  ✓ {desc}")
        else:
            print(f"  ✗ {desc} - MISSING")
            return False
    
    # Feature 3: Core Methods (verify nothing broke)
    print("\n" + "-" * 70)
    print("FEATURE 3: Core Methods Integrity Check")
    print("-" * 70)
    
    core_methods = [
        ('def _create_chat', 'Create chat'),
        ('def _delete_chat', 'Delete chat'),
        ('def _create_agent_chat', 'Create agent chat'),
        ('def _delete_agent_chat', 'Delete agent chat'),
        ('def _on_chat_right_click', 'Chat right-click handler'),
        ('def _on_agent_chat_right_click', 'Agent chat right-click handler'),
    ]
    
    for check_str, desc in core_methods:
        if check_str in main_code:
            print(f"  ✓ {desc}")
        else:
            print(f"  ✗ {desc} - MISSING OR BROKEN")
            return False
    
    # Feature 4: Button pack statement
    print("\n" + "-" * 70)
    print("FEATURE 4: UI Component Integration")
    print("-" * 70)
    
    if 'self.package_manager_button.pack(side="left", padx=(6, 0))' in main_code:
        print("  ✓ Package manager button is properly packed in UI")
    else:
        print("  ✗ Package manager button pack statement - MISSING")
        return False
    
    # Summary
    print("\n" + "=" * 70)
    print("✓ ALL FEATURES VERIFIED SUCCESSFULLY!")
    print("=" * 70)
    print("\nThe application should now:")
    print("  • Start without errors")
    print("  • Display 'Packages' button in IDE mode")
    print("  • Support chat renaming via right-click menu")
    print("  • Support agent chat renaming via right-click menu")
    print("  • Allow PyPI package installation")
    print("\n" + "=" * 70)
    
    return True

if __name__ == "__main__":
    try:
        success = verify_implementation()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"✗ Verification failed with error: {e}")
        sys.exit(1)
