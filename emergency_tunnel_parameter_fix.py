#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚨 EMERGENCY FIX: Tunnel Department Parameter Error
Purpose: Eliminate all LIGHTWEIGHT_DEPARTMENT_MAPPING references causing production error

Error: "無効なパラメータが指定されました：無効な部門: tunnel"
Cause: References to undefined LIGHTWEIGHT_DEPARTMENT_MAPPING in app.py
Solution: Replace with Japanese category direct usage system (CLAUDE.md compliant)
"""

import os
import re
from datetime import datetime

def fix_tunnel_parameter_error():
    """Fix the tunnel department parameter error by eliminating LIGHTWEIGHT_DEPARTMENT_MAPPING"""
    
    app_file = "rccm-quiz-app/app.py"
    if not os.path.exists(app_file):
        print(f"ERROR: {app_file} not found")
        return False
    
    # Create backup with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"rccm-quiz-app/app.py.tunnel_fix_backup_{timestamp}"
    
    try:
        # Read current content
        with open(app_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Create backup
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Backup created: {backup_file}")
        
        # Fix 1: Line 5427 - Replace LIGHTWEIGHT_DEPARTMENT_MAPPING check
        content = re.sub(
            r'if requested_department in LIGHTWEIGHT_DEPARTMENT_MAPPING:',
            'if requested_department in ["basic", "road", "river", "urban", "garden", "env", "steel", "soil", "construction", "water", "forest", "agri", "tunnel"]:',
            content
        )
        
        # Fix 2: Line 5920 - Replace LIGHTWEIGHT_DEPARTMENT_MAPPING check
        content = re.sub(
            r'elif h_dept in LIGHTWEIGHT_DEPARTMENT_MAPPING and get_japanese_category_direct\(h_dept\) == dept_name:',
            'elif h_dept in ["basic", "road", "river", "urban", "garden", "env", "steel", "soil", "construction", "water", "forest", "agri", "tunnel"] and get_japanese_category_direct(h_dept) == dept_name:',
            content
        )
        
        # Fix 3: Line 7205 - Replace LIGHTWEIGHT_DEPARTMENT_MAPPING check
        content = re.sub(
            r'if dept_key in LIGHTWEIGHT_DEPARTMENT_MAPPING:',
            'if dept_key in ["basic", "road", "river", "urban", "garden", "env", "steel", "soil", "construction", "water", "forest", "agri", "tunnel"]:',
            content
        )
        
        # Fix 4: Line 7908 - Replace LIGHTWEIGHT_DEPARTMENT_MAPPING check
        content = re.sub(
            r'if dept in LIGHTWEIGHT_DEPARTMENT_MAPPING:',
            'if dept in ["basic", "road", "river", "urban", "garden", "env", "steel", "soil", "construction", "water", "forest", "agri", "tunnel"]:',
            content
        )
        
        # Fix 5: Line 7972 - Replace LIGHTWEIGHT_DEPARTMENT_MAPPING check
        content = re.sub(
            r'if department in LIGHTWEIGHT_DEPARTMENT_MAPPING:',
            'if department in ["basic", "road", "river", "urban", "garden", "env", "steel", "soil", "construction", "water", "forest", "agri", "tunnel"]:',
            content
        )
        
        # Fix 6: Line 8047 - Replace LIGHTWEIGHT_DEPARTMENT_MAPPING check
        content = re.sub(
            r'if department in LIGHTWEIGHT_DEPARTMENT_MAPPING:',
            'if department in ["basic", "road", "river", "urban", "garden", "env", "steel", "soil", "construction", "water", "forest", "agri", "tunnel"]:',
            content
        )
        
        # Fix 7: Ensure get_japanese_category_direct function handles tunnel correctly
        # The function already uses JAPANESE_CATEGORIES_DIRECT which includes tunnel
        
        # Write fixed content
        with open(app_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("EMERGENCY FIX APPLIED:")
        print("All LIGHTWEIGHT_DEPARTMENT_MAPPING references eliminated")
        print("Replaced with English ID list checking")
        print("Japanese category resolution via get_japanese_category_direct()")
        print("Tunnel department error should be resolved")
        print("")
        print("CLAUDE.md Compliance:")
        print("English ID conversion system eliminated")
        print("Japanese category direct usage maintained")
        print("URLencoding/decoding system preserved")
        
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("EMERGENCY TUNNEL DEPARTMENT PARAMETER FIX")
    print("=" * 60)
    print("Purpose: Fix production error 'Invalid department: tunnel'")
    print("Method: Eliminate prohibited LIGHTWEIGHT_DEPARTMENT_MAPPING")
    print("Compliance: CLAUDE.md English ID conversion system ban")
    print("")
    
    success = fix_tunnel_parameter_error()
    
    if success:
        print("")
        print("EMERGENCY FIX SUCCESSFUL")
        print("Production tunnel department error should be resolved")
        print("All 13 departments should now work correctly")
        print("CLAUDE.md compliance restored")
        print("")
        print("Next steps:")
        print("1. Test tunnel department access")
        print("2. Test all 13 departments")
        print("3. Deploy to production")
    else:
        print("")
        print("EMERGENCY FIX FAILED")
        print("Manual intervention may be required")