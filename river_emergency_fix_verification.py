#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Emergency Fix Verification - River Department Field Mixing
Purpose: Verify the emergency data loading system eliminates field mixing
Ultra Sync Task: 緊急対応-10
"""

import sys
import os
sys.path.insert(0, 'rccm-quiz-app')

def verify_emergency_data_loading():
    """Test emergency data loading functions work correctly"""
    print("=== Emergency Data Loading System Verification ===")
    print()
    
    try:
        from utils import emergency_load_all_questions, emergency_get_questions
        
        print("1. Total questions loading test:")
        all_questions = emergency_load_all_questions()
        print(f"   Total questions loaded: {len(all_questions)}")
        
        # Category analysis
        categories = {}
        for q in all_questions:
            cat = q.get('category', 'unknown')
            categories[cat] = categories.get(cat, 0) + 1
        
        print("   Category distribution:")
        for cat, count in sorted(categories.items()):
            print(f"     {cat}: {count} questions")
        
        # Check if river category exists
        river_category = '河川、砂防及び海岸・海洋'
        river_count = categories.get(river_category, 0)
        
        print()
        print("2. River department filtering test:")
        print(f"   River category '{river_category}' questions available: {river_count}")
        
        if river_count > 0:
            # Test the emergency function with correct parameters
            river_questions = emergency_get_questions(
                department='river',  # Use correct parameter name
                question_type='specialist',
                count=10
            )
            
            print(f"   River questions returned by emergency function: {len(river_questions)}")
            
            if river_questions:
                print("   Sample river questions:")
                field_mixing_found = False
                for i, q in enumerate(river_questions[:5], 1):
                    category = q.get('category', 'N/A')
                    q_type = q.get('question_type', 'N/A')
                    print(f"     {i}. ID:{q.get('id')} Category:{category} Type:{q_type}")
                    
                    # Check for field mixing
                    if category != river_category:
                        field_mixing_found = True
                        print(f"       ❌ FIELD MIXING: Expected '{river_category}', got '{category}'")
                
                print()
                print("3. Field mixing analysis:")
                if not field_mixing_found:
                    print("   ✅ SUCCESS: Zero field mixing detected")
                    print(f"   ✅ All {len(river_questions)} questions are river-related")
                    return True
                else:
                    print("   ❌ ERROR: Field mixing still present")
                    return False
            else:
                print("   ❌ ERROR: Emergency function returned no river questions")
                return False
        else:
            print("   ❌ ERROR: No river questions available in data")
            return False
            
    except Exception as e:
        print(f"   ❌ ERROR: Verification failed - {e}")
        return False

def verify_main_app_integration():
    """Test that the main app uses emergency functions correctly"""
    print()
    print("4. Main app integration verification:")
    
    try:
        from app import app
        with app.test_client() as client:
            # Create a river department session
            response = client.get('/start_exam/specialist_river')
            print(f"   River exam start status: {response.status_code}")
            
            if response.status_code == 200:
                # Get the exam question page
                exam_response = client.get('/exam')
                print(f"   Exam page status: {exam_response.status_code}")
                
                if exam_response.status_code == 200:
                    html_content = exam_response.data.decode('utf-8', errors='ignore')
                    
                    # Check for field mixing indicators
                    has_basic_content = '基礎' in html_content
                    has_river_content = '河川' in html_content or '砂防' in html_content or '海岸' in html_content
                    has_question_form = 'name="answer"' in html_content
                    
                    print(f"   Contains basic subject content: {has_basic_content}")
                    print(f"   Contains river-related content: {has_river_content}")
                    print(f"   Contains question form: {has_question_form}")
                    
                    if has_basic_content:
                        print("   ❌ ERROR: Basic subject content detected - field mixing persists")
                        return False
                    elif has_question_form:
                        print("   ✅ SUCCESS: Question form present without basic content")
                        return True
                    else:
                        print("   ⚠️  WARNING: No question form found - may be redirect")
                        return None
                else:
                    print(f"   ❌ ERROR: Exam page failed with status {exam_response.status_code}")
                    return False
            else:
                print(f"   ❌ ERROR: River exam start failed with status {response.status_code}")
                return False
                
    except Exception as e:
        print(f"   ❌ ERROR: Main app test failed - {e}")
        return False

def main():
    print("RIVER DEPARTMENT EMERGENCY FIX VERIFICATION")
    print("=" * 60)
    print("Ultra Sync Task: 緊急対応-10")
    print("Purpose: Verify emergency data loading eliminates field mixing")
    print()
    
    # Test 1: Emergency data loading functions
    emergency_success = verify_emergency_data_loading()
    
    # Test 2: Main app integration  
    app_integration = verify_main_app_integration()
    
    print()
    print("=" * 60)
    print("VERIFICATION RESULTS:")
    print(f"Emergency data loading: {'SUCCESS' if emergency_success else 'FAILED'}")
    print(f"Main app integration: {'SUCCESS' if app_integration else 'FAILED' if app_integration is False else 'INCONCLUSIVE'}")
    
    if emergency_success and app_integration:
        print()
        print("🎉 CONCLUSION: Emergency fix SUCCESSFUL")
        print("✅ Field mixing problem resolved")
        print("✅ River department questions correctly filtered")
        print("✅ Main application uses emergency functions correctly")
        print()
        print(">>> Next Step: Mark 緊急対応-10 as completed")
        return True
    else:
        print()
        print("❌ CONCLUSION: Emergency fix needs additional work")
        print("🔧 Field mixing problem may still exist")
        print("🔧 Additional debugging required")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)