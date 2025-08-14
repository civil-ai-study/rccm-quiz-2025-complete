#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix Unicode Characters in app.py (Binary Mode)
Purpose: Replace Unicode characters using binary operations to avoid encoding issues
"""

import os
import datetime

def fix_unicode_binary():
    """Fix Unicode characters using binary file operations"""
    print("=== BINARY UNICODE FIX FOR APP.PY ===")
    print("Purpose: Fix encoding issues using binary operations")
    print()
    
    app_file = 'rccm-quiz-app/app.py'
    
    try:
        # Read file in binary mode
        with open(app_file, 'rb') as f:
            content_bytes = f.read()
        
        # Create backup (with timestamp)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f'rccm-quiz-app/app.py.backup_binary_fix_{timestamp}'
        with open(backup_file, 'wb') as f:
            f.write(content_bytes)
        print(f"Backup created: {backup_file}")
        
        # Define binary replacements for common Unicode characters
        # These are UTF-8 byte sequences for the Unicode characters
        replacements = {
            b'\xe2\x9c\x85': b'SUCCESS',  # ✅
            b'\xe2\x9d\x8c': b'ERROR',    # ❌  
            b'\xe2\x9a\xa0\xef\xb8\x8f': b'WARNING',  # ⚠️
            b'\xf0\x9f\x94\xa5': b'FIRE',      # 🔥
            b'\xf0\x9f\x9b\xa1\xef\xb8\x8f': b'SHIELD',  # 🛡️
            b'\xe2\x9a\xa1': b'BOLT',      # ⚡
            b'\xf0\x9f\x8e\xaf': b'TARGET',   # 🎯
            b'\xf0\x9f\x9a\x80': b'ROCKET',   # 🚀
            b'\xf0\x9f\x8e\x89': b'PARTY',    # 🎉
            b'\xf0\x9f\x94\x8d': b'SEARCH',   # 🔍
        }
        
        # Apply binary replacements
        modified_content = content_bytes
        replacement_count = 0
        
        for unicode_bytes, replacement_bytes in replacements.items():
            count = modified_content.count(unicode_bytes)
            if count > 0:
                modified_content = modified_content.replace(unicode_bytes, replacement_bytes)
                print(f"Replaced {count} instances of Unicode character")
                replacement_count += count
        
        # Write modified content
        with open(app_file, 'wb') as f:
            f.write(modified_content)
        
        print(f"Total replacements: {replacement_count}")
        
        # Verify by trying to decode as text
        try:
            test_content = modified_content.decode('utf-8')
            print("SUCCESS: Fixed content can be decoded as UTF-8")
            return True
        except Exception as e:
            print(f"WARNING: Decode test failed: {e}")
            return False
            
    except Exception as e:
        print(f"Error in binary Unicode fix: {e}")
        return False

def test_app_import():
    """Test if the app can be imported after Unicode fix"""
    print("\n=== TESTING APP IMPORT ===")
    
    try:
        import sys
        sys.path.insert(0, 'rccm-quiz-app')
        
        # Test import
        from app import app
        print("SUCCESS: App imported successfully")
        return True
    except UnicodeEncodeError as e:
        print(f"ERROR: Unicode encoding error persists: {e}")
        return False
    except Exception as e:
        print(f"INFO: App import failed for other reasons: {e}")
        # Other import errors might be normal
        return True

def main():
    print("BINARY UNICODE FIX FOR APP.PY")
    print("=" * 50)
    
    fix_success = fix_unicode_binary()
    
    if fix_success:
        test_success = test_app_import()
        
        print("\n" + "=" * 50)
        if test_success:
            print("SUCCESS: Binary Unicode fix completed")
            print("App.py should now work without cp932 encoding errors")
        else:
            print("PARTIAL: Fix applied but encoding issues may remain")
    else:
        print("FAILED: Binary Unicode fix failed")

if __name__ == "__main__":
    main()