#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Direct Department Mixing Check
Created: 2025-07-26
Purpose: Direct check of department content mixing using Flask test client
"""

import sys
import os
import json
from datetime import datetime

# Add app path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class DirectMixingCheck:
    """Direct mixing check using Flask test client"""
    
    def __init__(self):
        self.test_results = []
        
        # Key departments to check for mixing
        self.critical_checks = {
            "トンネル vs 建設環境": {
                "department": "トンネル",
                "should_have": ["トンネル", "掘削", "シールド", "坑道"],
                "should_not_have": ["建設環境", "環境保全", "騒音", "振動", "大気汚染"]
            },
            "道路 vs 河川": {
                "department": "道路", 
                "should_have": ["道路", "舗装", "交通"],
                "should_not_have": ["河川", "砂防", "治水", "ダム"]
            },
            "河川 vs トンネル": {
                "department": "河川・砂防",
                "should_have": ["河川", "砂防", "治水"],
                "should_not_have": ["トンネル", "掘削", "シールド"]
            },
            "建設環境 vs トンネル": {
                "department": "建設環境",
                "should_have": ["建設環境", "環境保全", "騒音"],
                "should_not_have": ["トンネル", "掘削", "坑道"]
            }
        }
        
    def log_result(self, test_name, status, details):
        """Test result logging"""
        result = {
            'timestamp': datetime.now().isoformat(),
            'test': test_name,
            'status': status,
            'details': details
        }
        self.test_results.append(result)
        print(f"[{status}] {test_name}: {details}")
    
    def check_department_mixing(self, check_name, check_info):
        """Check specific department for content mixing"""
        try:
            print(f"\n=== {check_name} Mixing Check ===")
            
            # Set testing environment
            os.environ['TESTING'] = 'true'
            
            from app import app
            
            with app.test_client() as client:
                dept_name = check_info["department"]
                
                # Start exam session
                form_data = {
                    'questions': '10',
                    'category': dept_name,
                    'exam_config': 'mixing_check',
                    'difficulty': '',
                    'year': ''
                }
                
                if dept_name == "基礎科目":
                    url = '/start_exam/basic'
                else:
                    url = f'/start_exam/{dept_name}'
                
                response = client.post(url, data=form_data)
                
                if response.status_code not in [200, 302]:
                    self.log_result(check_name, "ERROR", f"Session start failed: {response.status_code}")
                    return False
                
                # Get exam content
                exam_response = client.get('/exam')
                if exam_response.status_code != 200:
                    self.log_result(check_name, "ERROR", f"Exam page failed: {exam_response.status_code}")
                    return False
                
                content = exam_response.get_data(as_text=True)
                
                # Content analysis
                should_have_found = []
                should_not_have_found = []
                
                # Check for required content
                for keyword in check_info["should_have"]:
                    if keyword in content:
                        should_have_found.append(keyword)
                
                # Check for prohibited content (mixing detection)
                for keyword in check_info["should_not_have"]:
                    if keyword in content:
                        should_not_have_found.append(keyword)
                
                # Analysis result
                if len(should_have_found) > 0 and len(should_not_have_found) == 0:
                    self.log_result(check_name, "SUCCESS", 
                        f"No mixing - Found: {should_have_found}, Avoided: All prohibited content")
                    return True
                elif len(should_not_have_found) > 0:
                    self.log_result(check_name, "CRITICAL", 
                        f"MIXING DETECTED! Prohibited content: {should_not_have_found}")
                    return False
                else:
                    # No specific keywords found
                    if len(content) > 500:  # Has content but no specific keywords
                        self.log_result(check_name, "WARNING", 
                            "Content exists but no specific keywords detected")
                        return True
                    else:
                        self.log_result(check_name, "ERROR", "No substantial content found")
                        return False
                        
        except Exception as e:
            self.log_result(check_name, "ERROR", f"Check failed: {str(e)}")
            return False
    
    def run_critical_mixing_checks(self):
        """Run critical mixing checks"""
        print("DIRECT DEPARTMENT MIXING CHECK")
        print("Checking critical department combinations for content mixing")
        
        try:
            successful_checks = 0
            failed_checks = []
            
            for check_name, check_info in self.critical_checks.items():
                result = self.check_department_mixing(check_name, check_info)
                if result:
                    successful_checks += 1
                else:
                    failed_checks.append(check_name)
            
            # Results summary
            total_checks = len(self.critical_checks)
            success_rate = (successful_checks / total_checks) * 100
            
            print("\n" + "="*70)
            print("DIRECT MIXING CHECK RESULTS")
            print("="*70)
            
            print(f"Total Critical Checks: {total_checks}")
            print(f"Successful (No Mixing): {successful_checks}")
            print(f"Failed (Mixing Detected): {len(failed_checks)}")
            print(f"Success Rate: {success_rate:.1f}%")
            
            if success_rate == 100.0:
                print("EXCELLENT: No content mixing detected in any critical combination")
                final_status = "NO_MIXING_DETECTED"
            elif success_rate >= 75.0:
                print("ACCEPTABLE: Minor mixing issues detected")
                final_status = "MINOR_MIXING"
            else:
                print("CRITICAL: Significant content mixing detected")
                final_status = "SIGNIFICANT_MIXING"
            
            if failed_checks:
                print(f"\nFailed Checks (Mixing Detected):")
                for check in failed_checks:
                    print(f"  - {check}")
            
            # Save report
            report = {
                'timestamp': datetime.now().isoformat(),
                'total_checks': total_checks,
                'successful_checks': successful_checks,
                'failed_checks': failed_checks,
                'success_rate': success_rate,
                'final_status': final_status,
                'detailed_results': self.test_results
            }
            
            report_file = f"direct_mixing_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            print(f"\nDetailed report: {report_file}")
            
            return len(failed_checks) == 0  # Success if no failed checks
            
        except Exception as e:
            print(f"Critical mixing check failed: {str(e)}")
            return False

def main():
    """Main execution"""
    print("Direct Department Mixing Check Tool")
    
    checker = DirectMixingCheck()
    success = checker.run_critical_mixing_checks()
    
    if success:
        print("\nSUCCESS: No critical content mixing detected")
        return 0
    else:
        print("\nFAILED: Content mixing detected in critical departments")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())