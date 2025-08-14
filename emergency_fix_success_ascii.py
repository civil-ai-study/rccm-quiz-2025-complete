#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Emergency Fix Success Verification (ASCII Safe)
"""

import sys
import os
sys.path.insert(0, 'rccm-quiz-app')

def main():
    print("EMERGENCY FIX SUCCESS VERIFICATION")
    print("=" * 50)
    print()
    
    try:
        from utils import emergency_load_all_questions, emergency_get_questions
        
        # Test 1: Data loading
        all_questions = emergency_load_all_questions()
        print(f"1. Emergency data loading: {len(all_questions)} questions loaded")
        
        # Test 2: River filtering
        river_questions = emergency_get_questions(
            department='river',
            question_type='specialist', 
            count=10
        )
        print(f"2. River filtering: {len(river_questions)} questions returned")
        
        # Test 3: Field mixing check
        if river_questions:
            river_category = '\u6cb3\u5ddd\u3001\u7802\u9632\u53ca\u3073\u6d77\u5cb8\u30fb\u6d77\u6d0b'  # 河川、砂防及び海岸・海洋
            field_mixing = False
            
            for q in river_questions:
                if q.get('category') != river_category:
                    field_mixing = True
                    break
            
            print(f"3. Field mixing check: {'FAILED - mixing detected' if field_mixing else 'SUCCESS - zero mixing'}")
            
            if not field_mixing:
                print()
                print("SUCCESS: Emergency fix verification complete")
                print("- Emergency data loading: WORKING")
                print("- River question filtering: WORKING")
                print("- Field mixing eliminated: CONFIRMED")
                return True
        
        print("FAILED: Emergency fix verification failed")
        return False
        
    except Exception as e:
        print(f"ERROR: Verification failed - {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)