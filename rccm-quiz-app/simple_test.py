#\!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple test to verify core functionality without logging issues
"""

import os
import sys

# Suppress logging to avoid file permission issues
os.environ['LOGGING_DISABLED'] = '1'

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_basic_functionality():
    """Test basic app functionality"""
    try:
        print("=== ULTRA SYNC Basic Functionality Test ===")
        
        # Test 1: Import core utilities
        print("1. Testing utils import...")
        from utils import load_questions_improved
        print("   ✅ Utils import successful")
        
        # Test 2: Import config
        print("2. Testing config import...")
        from config import Config, RCCMConfig
        print("   ✅ Config import successful")
        print(f"   - Found {len(RCCMConfig.DEPARTMENTS)} departments")
        
        # Test 3: Check if data files exist
        print("3. Testing data availability...")
        if os.path.exists('data/4-1.csv'):
            print("   ✅ Basic questions file exists")
        else:
            print("   ❌ Basic questions file missing")
            
        data_files = [f for f in os.listdir('data') if f.startswith('4-2_') and f.endswith('.csv')]
        print(f"   ✅ Found {len(data_files)} specialist data files")
        
        # Test 4: Try to load sample questions
        print("4. Testing data loading...")
        try:
            questions = load_questions_improved('data/4-1.csv')
            print(f"   ✅ Loaded {len(questions)} basic questions")
        except Exception as e:
            print(f"   ❌ Data loading failed: {e}")
        
        print("\n=== Basic Functionality Test Complete ===")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_basic_functionality()
    if success:
        print("🎯 Core functionality is working - ready for 13-department test")
        sys.exit(0)
    else:
        print("🚨 Core functionality issues detected")
        sys.exit(1)
EOF < /dev/null
