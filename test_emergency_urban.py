#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick test for emergency_get_questions function with urban department
"""

import sys
import os
sys.path.insert(0, 'rccm-quiz-app')

def test_emergency_urban():
    """Test emergency functions for urban department"""
    print("=== Emergency Urban Department Test ===")
    
    try:
        from utils import emergency_get_questions
        print("✅ emergency_get_questions imported successfully")
        
        # Test with urban department
        questions = emergency_get_questions(
            department='urban', 
            question_type='specialist', 
            count=5
        )
        
        print(f"Emergency function returned: {len(questions)} questions")
        
        if len(questions) > 0:
            print("\nSample questions:")
            for i, q in enumerate(questions[:3], 1):
                print(f"  {i}. ID:{q.get('id')} Category:{q.get('category')}")
            
            # Check for field mixing
            urban_category = '都市計画及び地方計画'
            field_mixing_count = 0
            for q in questions:
                if q.get('category') != urban_category:
                    field_mixing_count += 1
            
            if field_mixing_count == 0:
                print("✅ SUCCESS: Emergency filtering works - zero field mixing")
                return True
            else:
                print(f"❌ WARNING: Field mixing detected - {field_mixing_count}/{len(questions)} questions")
                return False
        else:
            print("❌ ERROR: No urban planning questions found")
            return False
            
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}")
        return False

if __name__ == "__main__":
    success = test_emergency_urban()
    print(f"\nTest result: {'PASS' if success else 'FAIL'}")
    sys.exit(0 if success else 1)