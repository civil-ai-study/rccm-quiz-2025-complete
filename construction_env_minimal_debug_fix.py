#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Construction Environment Minimal Debug Fix
建設環境部門最小限デバッグ修正
Purpose: Add minimal debug logging to Emergency Fix 17 to understand why it's not triggered
"""

import os
import re
import shutil
from datetime import datetime

def add_minimal_debug_to_emergency_fix_17():
    """Add minimal debug logging to understand Emergency Fix 17 execution"""
    print("=== Emergency Fix 17 Minimal Debug: Adding Essential Logging ===")
    print("Purpose: Add minimal debug to understand why Emergency Fix 17 is not triggered")
    print()
    
    app_path = 'rccm-quiz-app/app.py'
    
    try:
        # Read current app.py
        with open(app_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("1. Creating backup...")
        timestamp = int(datetime.now().timestamp())
        backup_path = f'{app_path}.minimal_debug_{timestamp}'
        shutil.copy2(app_path, backup_path)
        print(f"   Backup created: {backup_path}")
        
        print("2. Finding Emergency Fix 17 Improved location...")
        
        # Find Emergency Fix 17 Improved section
        lines = content.split('\\n')
        fix17_start = None
        
        for i, line in enumerate(lines):
            if 'EMERGENCY FIX 17 IMPROVED: Construction Environment Session Preservation' in line:
                fix17_start = i
                break
        
        if fix17_start is None:
            print("   ❌ Emergency Fix 17 Improved not found")
            return False
        
        print(f"   Found Emergency Fix 17 Improved at line {fix17_start + 1}")
        
        # Add minimal debug logging right before Emergency Fix 17
        debug_code = '''            # DEBUG: Emergency Fix 17 execution check
            logger.info("DEBUG: Checking Emergency Fix 17 conditions")
            logger.info(f"DEBUG: 'questions' in session: {'questions' in session}")
            if 'questions' in session:
                q_list = session.get('questions', [])
                logger.info(f"DEBUG: questions count: {len(q_list)}")
                if q_list and len(q_list) > 0:
                    cat = q_list[0].get('category', '')
                    logger.info(f"DEBUG: first question category: '{cat}'")
                    logger.info(f"DEBUG: is construction env: {cat == '建設環境'}")
                else:
                    logger.info("DEBUG: questions list empty")
            else:
                logger.info("DEBUG: no 'questions' key")
'''
        
        # Get the indentation of the Emergency Fix line for proper alignment
        emergency_fix_line = lines[fix17_start]
        indentation = len(emergency_fix_line) - len(emergency_fix_line.lstrip())
        
        # Adjust the debug code indentation to match
        debug_lines = debug_code.strip().split('\\n')
        # The debug code already has proper indentation, just insert it
        
        # Insert debug logging before Emergency Fix 17
        new_lines = lines[:fix17_start] + debug_lines + [''] + lines[fix17_start:]
        new_content = '\\n'.join(new_lines)
        
        print("3. Validating syntax...")
        try:
            compile(new_content, app_path, 'exec')
            print("   ✅ Syntax validation successful")
        except SyntaxError as e:
            print(f"   ❌ Syntax error: {e}")
            return False
        
        # Write the updated content
        with open(app_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("\\n=== Emergency Fix 17 Minimal Debug Summary ===")
        print("✅ Added minimal debug logging before Emergency Fix 17")
        print("✅ Debug will show session state and category checks")
        print("✅ Safe minimal approach to avoid indentation issues")
        
        return True
        
    except Exception as e:
        print(f"Minimal debug fix failed: {e}")
        return False

def main():
    """Main function"""
    if add_minimal_debug_to_emergency_fix_17():
        print("\\n🎉 Emergency Fix 17 Minimal Debug applied successfully!")
        print("🔍 Essential debug logging added")
        print("📝 Ready for testing construction environment department")
    else:
        print("\\n❌ Emergency Fix 17 Minimal Debug failed")

if __name__ == "__main__":
    main()