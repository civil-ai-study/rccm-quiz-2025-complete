#!/usr/bin/env python3
"""
Stress test for navigation and error conditions
"""

import requests
import time
import threading

BASE_URL = "http://localhost:5003"

def test_concurrent_access():
    """Test concurrent access to avoid race conditions"""
    print("🔍 Testing concurrent access...")
    
    def worker(worker_id):
        session = requests.Session()
        for i in range(5):
            try:
                response = session.get(f"{BASE_URL}/exam?department=civil_planning&type=specialist")
                if response.status_code == 200:
                    print(f"Worker {worker_id} - Request {i+1}: ✅")
                else:
                    print(f"Worker {worker_id} - Request {i+1}: ❌ {response.status_code}")
                time.sleep(0.1)
            except Exception as e:
                print(f"Worker {worker_id} - Request {i+1}: ❌ Exception: {e}")
    
    threads = []
    for i in range(3):
        t = threading.Thread(target=worker, args=(i,))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    print("✅ Concurrent access test completed")

def test_department_switching():
    """Test rapid department switching"""
    print("\n🔍 Testing rapid department switching...")
    
    session = requests.Session()
    departments = ['civil_planning', 'road', 'tunnel', 'forestry']
    
    for dept in departments:
        response = session.get(f"{BASE_URL}/exam?department={dept}&type=specialist")
        if response.status_code == 200:
            print(f"✅ Department {dept} accessible")
        else:
            print(f"❌ Department {dept} failed: {response.status_code}")
    
    print("✅ Department switching test completed")

def test_invalid_inputs():
    """Test invalid input handling"""
    print("\n🔍 Testing invalid input handling...")
    
    session = requests.Session()
    
    # Test invalid department
    response = session.get(f"{BASE_URL}/exam?department=invalid_dept&type=specialist")
    if response.status_code in [200, 404]:
        print("✅ Invalid department handled gracefully")
    else:
        print(f"❌ Invalid department not handled: {response.status_code}")
    
    # Test invalid answer submission
    invalid_data = {
        'qid': 'invalid',
        'answer': 'Z',
        'elapsed': 'invalid'
    }
    
    response = session.post(f"{BASE_URL}/exam", data=invalid_data)
    if response.status_code in [200, 400, 422]:
        print("✅ Invalid answer data handled gracefully")
    else:
        print(f"❌ Invalid answer data not handled: {response.status_code}")
    
    print("✅ Invalid input test completed")

def test_session_management():
    """Test session management and persistence"""
    print("\n🔍 Testing session management...")
    
    session = requests.Session()
    
    # Start exam
    response1 = session.get(f"{BASE_URL}/exam?department=civil_planning&type=specialist")
    if response1.status_code != 200:
        print("❌ Failed to start session")
        return
    
    # Continue with same session
    response2 = session.get(f"{BASE_URL}/exam")
    if response2.status_code == 200:
        print("✅ Session persistence working")
    else:
        print(f"❌ Session persistence failed: {response2.status_code}")
    
    # Test review list access
    response3 = session.get(f"{BASE_URL}/review")
    if response3.status_code == 200:
        print("✅ Review list accessible")
    else:
        print(f"❌ Review list access failed: {response3.status_code}")
    
    print("✅ Session management test completed")

def main():
    print("=" * 60)
    print("STRESS TEST AND ERROR CONDITIONS")
    print("=" * 60)
    
    test_concurrent_access()
    test_department_switching()
    test_invalid_inputs()
    test_session_management()
    
    print("\n" + "=" * 60)
    print("🎉 Stress testing completed!")
    print("If no critical errors above, the application is stable.")

if __name__ == "__main__":
    main()