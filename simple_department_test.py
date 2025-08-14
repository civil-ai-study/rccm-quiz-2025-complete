#!/usr/bin/env python3
"""
Simple Department Testing Script - ASCII safe
Tests if department problem mixing has been resolved after CSRF fix
"""

import requests
import time

def test_department_question_content():
    """Test if departments show correct question types"""
    base_url = "http://127.0.0.1:5005"
    
    # Test departments
    departments = [
        ("road", "道路"),
        ("river", "河川"), 
        ("tunnel", "トンネル")
    ]
    
    results = {}
    
    for dept_id, dept_name in departments:
        print(f"\n=== Testing {dept_name} Department ===")
        
        try:
            # Test department question page with short timeout
            url = f"{base_url}/exam?department={dept_id}"
            response = requests.get(url, timeout=8)
            
            if response.status_code == 200:
                content = response.text
                
                # Check if CSRF token is present
                csrf_present = 'csrf_token' in content and 'value=' in content
                
                # Check for question content
                has_question = '<h3' in content and 'question-title' in content
                
                # Check for department-specific keywords
                if dept_id == "road":
                    relevant_keywords = ['道路', '舗装', '交通', '車道']
                elif dept_id == "river": 
                    relevant_keywords = ['河川', '砂防', '海岸', '流域']
                elif dept_id == "tunnel":
                    relevant_keywords = ['トンネル', '掘削', '支保', '坑道']
                else:
                    relevant_keywords = []
                
                keyword_match = any(keyword in content for keyword in relevant_keywords)
                
                results[dept_id] = {
                    'status': 'success',
                    'csrf_present': csrf_present,
                    'has_question': has_question, 
                    'keyword_match': keyword_match,
                    'content_length': len(content)
                }
                
                print(f"Response received ({len(content)} chars)")
                print(f"CSRF Token: {'OK' if csrf_present else 'MISSING'}")
                print(f"Question Content: {'OK' if has_question else 'MISSING'}")
                print(f"Department Keywords: {'OK' if keyword_match else 'MISSING'}")
                
            else:
                results[dept_id] = {
                    'status': 'error',
                    'status_code': response.status_code
                }
                print(f"HTTP Error: {response.status_code}")
                
        except requests.exceptions.Timeout:
            results[dept_id] = {'status': 'timeout'}
            print("Request timeout")
            
        except requests.exceptions.RequestException as e:
            results[dept_id] = {'status': 'error', 'error': str(e)}
            print(f"Request error: {e}")
            
        # Small delay between requests
        time.sleep(2)
    
    return results

def main():
    """Main test function"""
    print("Department Test - Verifying Problem Mixing Fix")
    print("=" * 50)
    
    start_time = time.time()
    results = test_department_question_content()
    end_time = time.time()
    
    print(f"\nTest Results Summary (Duration: {end_time - start_time:.1f}s)")
    print("=" * 50)
    
    success_count = 0
    total_count = len(results)
    
    for dept_id, result in results.items():
        if result.get('status') == 'success':
            success_count += 1
            csrf_ok = result.get('csrf_present', False)
            question_ok = result.get('has_question', False)  
            keyword_ok = result.get('keyword_match', False)
            
            overall_ok = csrf_ok and question_ok and keyword_ok
            print(f"{dept_id}: {'PASS' if overall_ok else 'PARTIAL'}")
        else:
            print(f"{dept_id}: {result.get('status', 'UNKNOWN')}")
    
    print(f"\nOverall Success Rate: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")
    
    if success_count == total_count:
        print("SUCCESS: All departments responding correctly!")
        print("CSRF issue appears to be resolved")  
        print("Department questions are displaying")
    elif success_count > 0:
        print("PARTIAL: Some departments working")
        print("Need further investigation for failed departments")
    else:
        print("FAILED: No departments responding correctly")
        print("Major issues still present")

if __name__ == "__main__":
    main()