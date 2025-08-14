#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
River Department Field Mixing Analysis (Post Emergency Fix)
Purpose: Focused analysis of the emergency data fix effectiveness
"""

import sys
import os
sys.path.insert(0, 'rccm-quiz-app')

def analyze_emergency_fix_effectiveness():
    """Test if the emergency data loading fix resolved field mixing"""
    print("=== River Department Field Mixing Analysis (Post Emergency Fix) ===")
    print("Purpose: Verify emergency data loading system eliminates field mixing")
    print()
    
    try:
        # Import emergency functions
        from utils import emergency_load_all_questions, emergency_get_questions
        
        print("1. Emergency Data Loading Test:")
        all_questions = emergency_load_all_questions()
        print(f"   Total questions loaded: {len(all_questions)}")
        
        # Category distribution analysis
        categories = {}
        for q in all_questions:
            cat = q.get('category', 'unknown')
            categories[cat] = categories.get(cat, 0) + 1
        
        print("   Category distribution:")
        for cat, count in sorted(categories.items()):
            print(f"     {cat}: {count} questions")
        
        print()
        print("2. River Department Filtering Test:")
        river_questions = emergency_get_questions(
            department_category='河川、砂防及び海岸・海洋',
            question_type='specialist',
            count=10
        )
        
        print(f"   River questions returned: {len(river_questions)}")
        if river_questions:
            print("   Sample river questions:")
            for i, q in enumerate(river_questions[:3], 1):
                print(f"     {i}. ID:{q['id']} Category:{q['category']} Type:{q.get('question_type', 'N/A')}")
        
        print()
        print("3. Field Mixing Analysis:")
        if river_questions:
            river_categories = [q.get('category') for q in river_questions]
            unique_categories = set(river_categories)
            
            if len(unique_categories) == 1 and '河川、砂防及び海岸・海洋' in unique_categories:
                print("   SUCCESS: Zero field mixing - all questions are river-related")
                return True
            else:
                print(f"   ERROR: Field mixing detected - categories found: {unique_categories}")
                return False
        else:
            print("   ERROR: No river questions returned - filtering failed")
            return False
            
    except Exception as e:
        print(f"   ERROR: Analysis failed - {e}")
        return False

def analyze_app_question_selection():
    """Test how the main app selects questions after emergency fix"""
    print()
    print("4. Main App Question Selection Test:")
    
    try:
        from app import app
        with app.test_client() as client:
            # Test river department question access
            response = client.get('/exam')
            print(f"   /exam route status: {response.status_code}")
            
            if response.status_code == 200:
                html_content = response.data.decode('utf-8', errors='ignore')
                print(f"   Response length: {len(html_content)} chars")
                
                # Check for question content indicators
                has_question = 'question' in html_content.lower()
                has_category = '河川' in html_content or 'category' in html_content.lower()
                has_basic = '基礎' in html_content or 'basic' in html_content.lower()
                
                print(f"   Contains question content: {has_question}")
                print(f"   Contains category info: {has_category}")
                print(f"   Contains basic subject: {has_basic}")
                
                if has_basic:
                    print("   WARNING: Basic subject content detected - field mixing may continue")
                else:
                    print("   SUCCESS: No basic subject content - field mixing resolved")
            else:
                print(f"   ERROR: Non-200 status code: {response.status_code}")
                
    except Exception as e:
        print(f"   ERROR: Main app test failed - {e}")

def main():
    print("RIVER DEPARTMENT EMERGENCY FIX ANALYSIS")
    print("=" * 60)
    
    # Test 1: Emergency data loading effectiveness
    emergency_success = analyze_emergency_fix_effectiveness()
    
    # Test 2: Main app integration
    analyze_app_question_selection()
    
    print()
    print("=" * 60)
    if emergency_success:
        print("CONCLUSION: Emergency data loading fix SUCCESS")
        print("- Emergency functions correctly filter river questions")
        print("- Zero field mixing in emergency data loading system")
        print("- Next: Verify main app uses emergency functions consistently")
    else:
        print("CONCLUSION: Emergency data loading fix FAILED")
        print("- Emergency functions still show field mixing")
        print("- Additional fixes required")
    
    return emergency_success

if __name__ == "__main__":
    main()