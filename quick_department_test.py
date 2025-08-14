#!/usr/bin/env python3
"""
Quick Department Testing Script
Tests if department problem mixing has been resolved after CSRF fix
"""

import requests
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def create_session():
    """Create a session with timeout and retry configuration"""
    session = requests.Session()
    
    # Configure retries
    retry_strategy = Retry(
        total=2,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    return session

def test_department_question_content():
    """Test if departments show correct question types"""
    session = create_session()
    base_url = "http://127.0.0.1:5005"
    
    # Test departments
    departments = [
        ("road", "道路"),  # Should show road engineering questions
        ("river", "河川"),  # Should show river engineering questions  
        ("tunnel", "トンネル")  # Should show tunnel engineering questions
    ]
    
    results = {}
    
    for dept_id, dept_name in departments:
        print(f"\n=== Testing {dept_name} Department ===")
        
        try:
            # Test department question page with short timeout
            url = f"{base_url}/exam?department={dept_id}"
            response = session.get(url, timeout=10)
            
            if response.status_code == 200:
                content = response.text
                
                # Check if CSRF token is present (indicates template rendered properly)
                csrf_present = 'csrf_token' in content and 'value=' in content
                
                # Check for question content
                has_question = '<h3' in content and '問題' in content
                
                # Check for department-specific keywords
                if dept_id == "road":
                    relevant_keywords = ['道路', '舗装', '交通', '車道', '歩道']
                elif dept_id == "river": 
                    relevant_keywords = ['河川', '砂防', '海岸', '流域', '治水']
                elif dept_id == "tunnel":
                    relevant_keywords = ['トンネル', '掘削', '支保', '坑道', '地山']
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
                
                print(f"✅ {dept_name}: Response received ({len(content)} chars)")
                print(f"   CSRF Token: {'✅' if csrf_present else '❌'}")
                print(f"   Question Content: {'✅' if has_question else '❌'}")
                print(f"   Department Keywords: {'✅' if keyword_match else '❌'}")
                
            else:
                results[dept_id] = {
                    'status': 'error',
                    'status_code': response.status_code
                }
                print(f"❌ {dept_name}: HTTP {response.status_code}")
                
        except requests.exceptions.Timeout:
            results[dept_id] = {'status': 'timeout'}
            print(f"⏰ {dept_name}: Timeout")
            
        except requests.exceptions.RequestException as e:
            results[dept_id] = {'status': 'error', 'error': str(e)}
            print(f"❌ {dept_name}: Error - {e}")
            
        # Small delay between requests
        time.sleep(1)
    
    return results

def main():
    """Main test function"""
    print("🧪 Quick Department Test - Verifying Problem Mixing Fix")
    print("=" * 60)
    
    start_time = time.time()
    results = test_department_question_content()
    end_time = time.time()
    
    print(f"\n📊 Test Results Summary (Duration: {end_time - start_time:.1f}s)")
    print("=" * 60)
    
    success_count = 0
    total_count = len(results)
    
    for dept_id, result in results.items():
        if result.get('status') == 'success':
            success_count += 1
            csrf_ok = result.get('csrf_present', False)
            question_ok = result.get('has_question', False)  
            keyword_ok = result.get('keyword_match', False)
            
            overall_ok = csrf_ok and question_ok and keyword_ok
            print(f"✅ {dept_id}: {'PASS' if overall_ok else 'PARTIAL'}")
        else:
            print(f"❌ {dept_id}: {result.get('status', 'UNKNOWN')}")
    
    print(f"\n🎯 Overall Success Rate: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")
    
    if success_count == total_count:
        print("🎉 All departments responding correctly!")
        print("✅ CSRF issue appears to be resolved")
        print("✅ Department questions are displaying")
    elif success_count > 0:
        print("⚠️ Partial success - some departments working")
        print("🔍 Need further investigation for failed departments")
    else:
        print("❌ No departments responding correctly")
        print("🚨 Major issues still present")

if __name__ == "__main__":
    main()