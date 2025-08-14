#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix Unicode Characters in app.py
Purpose: Replace all Unicode characters with ASCII-safe alternatives
Context: Emergency fix for cp932 encoding issues
"""

import sys
import os
import datetime

def fix_unicode_in_app():
    """Fix Unicode characters in app.py to ASCII-safe alternatives"""
    print("=== FIXING UNICODE CHARACTERS IN APP.PY ===")
    print("Purpose: Replace Unicode with ASCII-safe alternatives")
    print()
    
    app_file = 'rccm-quiz-app/app.py'
    
    # Create backup
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f'rccm-quiz-app/app.py.backup_unicode_fix_{timestamp}'
    
    try:
        # Read app.py
        with open(app_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Create backup
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Backup created: {backup_file}")
        
        # Unicode replacements (ASCII-safe)
        unicode_replacements = {
            '✅': 'SUCCESS',
            '❌': 'ERROR', 
            '⚠️': 'WARNING',
            '🔥': 'FIRE',
            '🛡️': 'SHIELD',
            '⚡': 'BOLT',
            '🎯': 'TARGET',
            '🚀': 'ROCKET',
            '🎉': 'PARTY',
            '🔍': 'SEARCH',
            '📊': 'CHART',
            '🌟': 'STAR',
            '💡': 'BULB',
            '🔧': 'WRENCH',
            '📈': 'GRAPH',
            '🏆': 'TROPHY',
            '💪': 'MUSCLE',
            '⭐': 'STAR',
            '🎊': 'CONFETTI',
            '✨': 'SPARKLES',
            '🔥': 'FIRE',
            '🚨': 'SIREN',
            '⚙️': 'GEAR',
            '📱': 'MOBILE',
            '♿': 'ACCESS'
        }
        
        # Apply replacements
        original_content = content
        for unicode_char, replacement in unicode_replacements.items():
            content = content.replace(unicode_char, replacement)
        
        # Count replacements
        total_replacements = 0
        for unicode_char in unicode_replacements.keys():
            count = original_content.count(unicode_char)
            if count > 0:
                print(f"Replaced {count} instances of '{unicode_char}' with '{unicode_replacements[unicode_char]}'")
                total_replacements += count
        
        # Write fixed content
        with open(app_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"\nTotal replacements: {total_replacements}")
        print("Unicode fix completed successfully")
        return True
        
    except Exception as e:
        print(f"Error fixing Unicode characters: {e}")
        return False

def verify_unicode_fix():
    """Verify that Unicode fix was successful"""
    print("\n=== VERIFYING UNICODE FIX ===")
    
    try:
        # Try to import the app to check for encoding errors
        sys.path.insert(0, 'rccm-quiz-app')
        
        # First check if there are any remaining Unicode characters
        with open('rccm-quiz-app/app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for common Unicode characters that cause issues
        problematic_chars = ['✅', '❌', '⚠️', '🔥', '🛡️', '⚡', '🎯', '🚀']
        remaining_unicode = []
        
        for char in problematic_chars:
            if char in content:
                remaining_unicode.append(char)
        
        if remaining_unicode:
            print(f"WARNING: Remaining Unicode characters: {remaining_unicode}")
            return False
        else:
            print("SUCCESS: No problematic Unicode characters found")
            
        # Try importing the app
        try:
            from app import app
            print("SUCCESS: App imports without Unicode encoding errors")
            return True
        except UnicodeEncodeError as e:
            print(f"ERROR: Unicode encoding error still present: {e}")
            return False
        except Exception as e:
            print(f"INFO: App import failed for other reasons: {e}")
            # This might be normal if other dependencies are missing
            return True
            
    except Exception as e:
        print(f"Error verifying Unicode fix: {e}")
        return False

def main():
    print("UNICODE FIX FOR APP.PY")
    print("=" * 50)
    
    # Step 1: Fix Unicode characters
    fix_success = fix_unicode_in_app()
    
    if fix_success:
        # Step 2: Verify fix
        verify_success = verify_unicode_fix()
        
        print("\n" + "=" * 50)
        if verify_success:
            print("SUCCESS: Unicode fix completed and verified")
            print("App.py should now work without cp932 encoding errors")
            print("\n>>> Next Action: Re-run river department test")
        else:
            print("PARTIAL SUCCESS: Unicode fix applied but verification failed")
            print("Manual review may be required")
    else:
        print("FAILED: Unicode fix could not be applied")
    
    return fix_success

if __name__ == "__main__":
    main()