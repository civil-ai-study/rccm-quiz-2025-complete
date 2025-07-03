#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Master Review Test Runner

Comprehensive test suite runner for all review list functionality tests:
1. comprehensive_review_test.py - Overall review functionality
2. review_session_execution_test.py - Session execution patterns
3. srs_graduation_test.py - SRS system and graduation mechanics

This runner executes all tests and provides consolidated reporting.
"""

import subprocess
import sys
import time
import json
from datetime import datetime
import os


class MasterReviewTestRunner:
    def __init__(self):
        self.test_scripts = [
            {
                'name': 'Comprehensive Review Test',
                'script': 'comprehensive_review_test.py',
                'description': 'Tests overall review functionality including addition, access, and basic operations'
            },
            {
                'name': 'Review Session Execution Test',
                'script': 'review_session_execution_test.py',
                'description': 'Tests review session execution patterns with different question counts'
            },
            {
                'name': 'SRS Graduation Test',
                'script': 'srs_graduation_test.py',
                'description': 'Tests SRS system functionality and question graduation mechanics'
            }
        ]
        
        self.results = []
        self.start_time = None
        self.end_time = None
    
    def check_prerequisites(self):
        """Check if all test scripts exist"""
        print("🔍 Checking prerequisites...")
        
        missing_scripts = []
        for test in self.test_scripts:
            if not os.path.exists(test['script']):
                missing_scripts.append(test['script'])
        
        if missing_scripts:
            print(f"❌ Missing test scripts: {', '.join(missing_scripts)}")
            return False
        
        print("✅ All test scripts found")
        return True
    
    def run_single_test(self, test_info):
        """Run a single test script"""
        print(f"\n🚀 Running: {test_info['name']}")
        print(f"📝 Description: {test_info['description']}")
        print("=" * 60)
        
        start_time = time.time()
        
        try:
            # Run the test script
            result = subprocess.run([
                sys.executable, test_info['script']
            ], capture_output=True, text=True, timeout=600)  # 10 minute timeout
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Parse result
            success = result.returncode == 0
            
            test_result = {
                'name': test_info['name'],
                'script': test_info['script'],
                'success': success,
                'return_code': result.returncode,
                'duration': duration,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'timestamp': datetime.now().isoformat()
            }
            
            self.results.append(test_result)
            
            # Print immediate results
            status = "✅ PASSED" if success else "❌ FAILED"
            print(f"\n{status} {test_info['name']} ({duration:.1f}s)")
            
            if result.stdout:
                print("📤 Output:")
                print(result.stdout[-1000:])  # Last 1000 characters
            
            if result.stderr and not success:
                print("⚠️ Errors:")
                print(result.stderr[-500:])  # Last 500 characters
            
            return success
            
        except subprocess.TimeoutExpired:
            print(f"⏰ Test {test_info['name']} timed out after 10 minutes")
            test_result = {
                'name': test_info['name'],
                'script': test_info['script'],
                'success': False,
                'return_code': -1,
                'duration': 600,
                'stdout': '',
                'stderr': 'Test timed out',
                'timestamp': datetime.now().isoformat()
            }
            self.results.append(test_result)
            return False
            
        except Exception as e:
            print(f"💥 Error running {test_info['name']}: {e}")
            test_result = {
                'name': test_info['name'],
                'script': test_info['script'],
                'success': False,
                'return_code': -2,
                'duration': time.time() - start_time,
                'stdout': '',
                'stderr': str(e),
                'timestamp': datetime.now().isoformat()
            }
            self.results.append(test_result)
            return False
    
    def generate_report(self):
        """Generate comprehensive test report"""
        total_tests = len(self.test_scripts)
        passed_tests = sum(1 for r in self.results if r['success'])
        failed_tests = total_tests - passed_tests
        
        total_duration = sum(r['duration'] for r in self.results)
        
        print("\n" + "=" * 70)
        print("📊 MASTER REVIEW TEST RESULTS SUMMARY")
        print("=" * 70)
        print(f"🕐 Total Execution Time: {total_duration:.1f} seconds ({total_duration/60:.1f} minutes)")
        print(f"📋 Total Test Suites: {total_tests}")
        print(f"✅ Passed Test Suites: {passed_tests}")
        print(f"❌ Failed Test Suites: {failed_tests}")
        print(f"📈 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Individual test results
        print(f"\n📝 Individual Test Suite Results:")
        for result in self.results:
            status = "✅ PASS" if result['success'] else "❌ FAIL"
            duration = result['duration']
            print(f"{status} {result['name']} ({duration:.1f}s)")
            
            if not result['success']:
                print(f"   Return Code: {result['return_code']}")
                if result['stderr']:
                    print(f"   Error: {result['stderr'][:200]}...")
        
        # Recommendations
        print(f"\n💡 Recommendations:")
        if passed_tests == total_tests:
            print("🎉 All review functionality tests passed! The review system is working correctly.")
        else:
            print(f"🔧 {failed_tests} test suite(s) failed. Review the detailed output above.")
            print("   Common issues:")
            print("   - Application not running on localhost:5003")
            print("   - Database/session issues")
            print("   - Network connectivity problems")
            print("   - Test data conflicts")
        
        return passed_tests == total_tests
    
    def save_detailed_report(self):
        """Save detailed report to file"""
        report_data = {
            'summary': {
                'total_tests': len(self.test_scripts),
                'passed_tests': sum(1 for r in self.results if r['success']),
                'failed_tests': sum(1 for r in self.results if not r['success']),
                'total_duration': sum(r['duration'] for r in self.results),
                'start_time': self.start_time,
                'end_time': self.end_time,
                'success_rate': (sum(1 for r in self.results if r['success']) / len(self.test_scripts)) * 100
            },
            'test_results': self.results,
            'test_scripts': self.test_scripts
        }
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = f"master_review_test_report_{timestamp}.json"
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Detailed report saved to: {report_file}")
        except Exception as e:
            print(f"\n⚠️ Could not save detailed report: {e}")
    
    def run_all_tests(self):
        """Run all review functionality tests"""
        print("🚀 MASTER REVIEW FUNCTIONALITY TEST SUITE")
        print("=" * 70)
        print("This comprehensive test suite verifies:")
        print("1. Questions can be added to review list by answering incorrectly")
        print("2. Review sessions can start with different question counts (10/20/30)")
        print("3. Review questions are properly selected and presented")
        print("4. Review sessions complete successfully")
        print("5. SRS system updates properly after review sessions")
        print("6. Review count updates correctly on home page")
        print("7. Questions graduate out of review list after 5 correct answers")
        print("=" * 70)
        
        if not self.check_prerequisites():
            return False
        
        self.start_time = datetime.now().isoformat()
        
        # Run each test suite
        all_passed = True
        for test_info in self.test_scripts:
            success = self.run_single_test(test_info)
            if not success:
                all_passed = False
            
            # Brief pause between test suites
            time.sleep(2)
        
        self.end_time = datetime.now().isoformat()
        
        # Generate and save reports
        final_success = self.generate_report()
        self.save_detailed_report()
        
        return final_success and all_passed
    
    def quick_health_check(self):
        """Quick health check of the application"""
        print("🏥 Performing quick health check...")
        
        try:
            import requests
            response = requests.get('http://localhost:5003/', timeout=5)
            
            if response.status_code == 200:
                print("✅ Application is responding on localhost:5003")
                return True
            else:
                print(f"⚠️ Application responded with status {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Application health check failed: {e}")
            print("   Make sure the application is running on localhost:5003")
            return False


def main():
    """Main execution function"""
    runner = MasterReviewTestRunner()
    
    try:
        # Health check first
        if not runner.quick_health_check():
            print("\n⚠️ Health check failed. Please ensure the application is running.")
            print("   You can continue anyway, but tests may fail.")
            
            response = input("\nContinue anyway? (y/N): ").strip().lower()
            if response not in ['y', 'yes']:
                return 1
        
        # Run all tests
        success = runner.run_all_tests()
        
        if success:
            print("\n🎉 ALL REVIEW FUNCTIONALITY TESTS COMPLETED SUCCESSFULLY!")
            print("The review list system is working correctly.")
            return 0
        else:
            print("\n💥 SOME REVIEW FUNCTIONALITY TESTS FAILED")
            print("Please review the detailed output above for specific issues.")
            return 1
            
    except KeyboardInterrupt:
        print("\n⚠️ Test suite interrupted by user")
        return 2
    except Exception as e:
        print(f"\n💥 Master test runner error: {e}")
        return 3


if __name__ == '__main__':
    exit(main())