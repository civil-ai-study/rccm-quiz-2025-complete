#!/usr/bin/env python3
"""
Comprehensive Navigation Test for RCCM Exam Application
Tests question navigation, answer submission, and SRS functionality.
"""

import requests
import json
import sys
from urllib.parse import urljoin

BASE_URL = "http://localhost:5003"

def test_navigation_flow():
    """Test complete navigation flow through questions"""
    print("🔍 Starting comprehensive navigation test...")
    
    session = requests.Session()
    results = []
    
    try:
        # Test 1: Start 河川砂防 specialist exam
        print("\n1. Testing 河川砂防 specialist exam start...")
        response = session.get(f"{BASE_URL}/exam?department=civil_planning&type=specialist")
        if response.status_code == 200:
            print("✅ Successfully started 河川砂防 specialist exam")
            results.append(("Start civil_planning exam", "PASS", ""))
        else:
            print("❌ Failed to start exam")
            results.append(("Start civil_planning exam", "FAIL", f"Status: {response.status_code}"))
            return results
        
        # Extract question info from the page
        content = response.text
        if "河川" in content or "砂防" in content or "海岸" in content:
            print("✅ Confirmed showing 河川砂防 related questions")
            results.append(("Department filtering", "PASS", "Shows correct department questions"))
        else:
            print("❌ Department filtering issue - not showing expected questions")
            results.append(("Department filtering", "FAIL", "Not showing department-specific questions"))
        
        # Test 2: Check for year display in specialist questions
        if "年度" in content:
            print("✅ Year information displayed correctly")
            results.append(("Year display", "PASS", "Year badges shown"))
        else:
            print("⚠️ Year information not clearly visible")
            results.append(("Year display", "PARTIAL", "Year display unclear"))
        
        # Test 3: Try to submit an answer (simulate incorrect answer to test review list)
        print("\n2. Testing answer submission...")
        
        # Look for form data in the page
        import re
        question_id_match = re.search(r'name="question_id" value="([^"]+)"', content)
        if not question_id_match:
            print("❌ Could not find question_id in form")
            results.append(("Answer submission", "FAIL", "No question_id found"))
            return results
        
        question_id = question_id_match.group(1)
        print(f"Found question_id: {question_id}")
        
        # Submit an incorrect answer (option 1, assuming it's wrong)
        answer_data = {
            'question_id': question_id,
            'selected_answer': '1'
        }
        
        submit_response = session.post(f"{BASE_URL}/submit_answer", data=answer_data)
        if submit_response.status_code == 200:
            print("✅ Answer submission successful")
            results.append(("Answer submission", "PASS", ""))
            
            # Check if navigation to next question works
            if "次の問題" in submit_response.text or "continue" in submit_response.text.lower():
                print("✅ Navigation to next question available")
                results.append(("Question navigation", "PASS", ""))
            else:
                print("⚠️ Navigation unclear - checking content...")
                results.append(("Question navigation", "PARTIAL", "Navigation not clearly visible"))
        else:
            print(f"❌ Answer submission failed: {submit_response.status_code}")
            results.append(("Answer submission", "FAIL", f"Status: {submit_response.status_code}"))
        
        # Test 4: Check if KeyError issues exist by trying to continue
        print("\n3. Testing continuation without KeyError...")
        try:
            continue_response = session.get(f"{BASE_URL}/exam?department=civil_planning&type=specialist")
            if continue_response.status_code == 200:
                print("✅ Continuation successful - no KeyError")
                results.append(("No KeyError", "PASS", ""))
            else:
                print(f"❌ Continuation failed: {continue_response.status_code}")
                results.append(("No KeyError", "FAIL", f"Status: {continue_response.status_code}"))
        except Exception as e:
            print(f"❌ Exception during continuation: {e}")
            results.append(("No KeyError", "FAIL", f"Exception: {str(e)}"))
        
        # Test 5: Test review list functionality
        print("\n4. Testing review list...")
        review_response = session.get(f"{BASE_URL}/review")
        if review_response.status_code == 200:
            if "問題が見つかりません" in review_response.text:
                print("⚠️ Review list empty (may be expected if no incorrect answers yet)")
                results.append(("Review list", "PARTIAL", "Empty review list"))
            else:
                print("✅ Review list accessible")
                results.append(("Review list", "PASS", ""))
        else:
            print(f"❌ Review list access failed: {review_response.status_code}")
            results.append(("Review list", "FAIL", f"Status: {review_response.status_code}"))
        
        # Test 6: Test other departments for comparison
        print("\n5. Testing other departments...")
        
        # Test forestry department
        forestry_response = session.get(f"{BASE_URL}/exam?department=forestry&type=specialist")
        if forestry_response.status_code == 200:
            forestry_content = forestry_response.text
            if "森林" in forestry_content and "河川" not in forestry_content:
                print("✅ Forestry department shows correct filtering")
                results.append(("Cross-department filtering", "PASS", ""))
            else:
                print("⚠️ Forestry department filtering unclear")
                results.append(("Cross-department filtering", "PARTIAL", ""))
        else:
            print("❌ Forestry department access failed")
            results.append(("Cross-department filtering", "FAIL", ""))
        
    except Exception as e:
        print(f"❌ Critical error during testing: {e}")
        results.append(("Critical error", "FAIL", str(e)))
    
    return results

def main():
    """Main test execution"""
    print("=" * 60)
    print("RCCM EXAM APPLICATION - COMPREHENSIVE END-TO-END TEST")
    print("=" * 60)
    
    results = test_navigation_flow()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = failed = partial = 0
    
    for test_name, status, details in results:
        if status == "PASS":
            print(f"✅ {test_name}")
            passed += 1
        elif status == "FAIL":
            print(f"❌ {test_name}: {details}")
            failed += 1
        else:
            print(f"⚠️ {test_name}: {details}")
            partial += 1
    
    print(f"\nRESULTS: ✅ {passed} PASSED | ❌ {failed} FAILED | ⚠️ {partial} PARTIAL")
    
    if failed > 0:
        print("\n🚨 CRITICAL ISSUES FOUND - Requires immediate attention")
        sys.exit(1)
    elif partial > 0:
        print("\n⚠️ Some issues detected - Review recommended")
        sys.exit(2)
    else:
        print("\n🎉 All tests passed successfully!")
        sys.exit(0)

if __name__ == "__main__":
    main()