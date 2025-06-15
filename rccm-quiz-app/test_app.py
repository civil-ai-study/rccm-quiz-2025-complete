#!/usr/bin/env python3
"""
RCCM Quiz App Comprehensive Test Script
Tests all major features of the application
"""

import os
import sys
import time
import json
import random
from datetime import datetime

# Flask test client setup
os.environ['TESTING'] = 'true'
from app import app

def test_homepage():
    """Test the homepage loads correctly"""
    print("\n1. Testing Homepage...")
    with app.test_client() as client:
        response = client.get('/')
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✓ Homepage loads successfully")
        else:
            print(f"   ✗ Homepage error: {response.data}")
        return response.status_code == 200

def test_categories():
    """Test categories page"""
    print("\n2. Testing Categories Page...")
    with app.test_client() as client:
        response = client.get('/categories')
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✓ Categories page loads successfully")
        else:
            print(f"   ✗ Categories error: {response.data}")
        return response.status_code == 200

def test_exam_flow():
    """Test complete exam flow with 10 questions"""
    print("\n3. Testing Exam Flow (10 questions)...")
    with app.test_client() as client:
        # Start a exam
        print("   Starting exam...")
        response = client.get('/exam?size=10', follow_redirects=True)
        
        if response.status_code != 200:
            print(f"   ✗ Failed to start exam: {response.status_code}")
            return False
        
        print("   ✓ Exam started successfully")
        
        # Answer 10 questions
        for i in range(10):
            print(f"   Answering question {i+1}/10...")
            
            # Get current question
            response = client.get('/exam')
            if response.status_code != 200:
                print(f"   ✗ Failed to get question {i+1}: {response.status_code}")
                return False
            
            # Submit answer (randomly choose an option)
            answer = random.choice(['A', 'B', 'C', 'D'])
            
            # Get question ID from current page
            exam_response = client.get('/exam')
            if exam_response.status_code == 200:
                # Extract question ID from response - just use a simple approach
                response = client.post('/exam', data={
                    'answer': answer,
                    'qid': str(i + 1),  # Simple ID for testing
                    'elapsed': '10'
                }, follow_redirects=False)
            
            if response.status_code not in [200, 302]:
                print(f"   ✗ Failed to submit answer for question {i+1}: {response.status_code}")
                return False
            
            # Navigate to next question if not last
            if i < 9:
                response = client.get(f'/exam?next=1&current={i+1}', follow_redirects=True)
                if response.status_code != 200:
                    print(f"   ✗ Failed to navigate to question {i+2}: {response.status_code}")
                    return False
        
        # Check results page
        print("   Checking results page...")
        response = client.get('/result')
        if response.status_code == 200:
            print("   ✓ Exam completed successfully - Results page loaded")
            return True
        else:
            print(f"   ✗ Failed to load results: {response.status_code}")
            return False

def test_statistics():
    """Test statistics page"""
    print("\n4. Testing Statistics Page...")
    with app.test_client() as client:
        response = client.get('/statistics')
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✓ Statistics page loads successfully")
        else:
            print(f"   ✗ Statistics error: {response.data}")
        return response.status_code == 200

def test_exam_simulator():
    """Test exam simulator"""
    print("\n5. Testing Exam Simulator...")
    with app.test_client() as client:
        response = client.get('/exam_simulator')
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✓ Exam simulator page loads successfully")
        else:
            print(f"   ✗ Exam simulator error: {response.data}")
        return response.status_code == 200

def test_department_study():
    """Test department study page"""
    print("\n6. Testing Department Study...")
    with app.test_client() as client:
        response = client.get('/department_study')
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✓ Department study page loads successfully")
        else:
            print(f"   ✗ Department study error: {response.data}")
        return response.status_code == 200

def test_api_endpoints():
    """Test API endpoints"""
    print("\n7. Testing API Endpoints...")
    with app.test_client() as client:
        # Test cache clear
        response = client.post('/api/cache/clear')
        print(f"   Cache clear status: {response.status_code}")
        if response.status_code == 200:
            print("   ✓ Cache clear API works successfully")
        else:
            print(f"   ✗ Cache clear API error: {response.status_code}")
        
        return response.status_code == 200

def test_mobile_features():
    """Test mobile/PWA features"""
    print("\n8. Testing Mobile Features...")
    with app.test_client() as client:
        response = client.get('/mobile_settings')
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✓ Mobile settings page loads successfully")
        else:
            print(f"   ✗ Mobile settings error: {response.data}")
        return response.status_code == 200

def test_help_page():
    """Test help page"""
    print("\n9. Testing Help Page...")
    with app.test_client() as client:
        response = client.get('/help')
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✓ Help page loads successfully")
        else:
            print(f"   ✗ Help error: {response.data}")
        return response.status_code == 200

def main():
    """Run all tests"""
    print("="*60)
    print("RCCM Exam App Comprehensive Test Suite")
    print("="*60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        test_homepage,
        test_categories,
        test_exam_flow,
        test_statistics,
        test_exam_simulator,
        test_department_study,
        test_api_endpoints,
        test_mobile_features,
        test_help_page
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"   ✗ Exception in {test.__name__}: {str(e)}")
            failed += 1
    
    print("\n" + "="*60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("="*60)
    
    if failed == 0:
        print("\n✓ All tests passed successfully!")
    else:
        print(f"\n✗ {failed} tests failed. Please check the errors above.")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)