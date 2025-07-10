#!/usr/bin/env python3
"""
Comprehensive Production Verification: 2008-2019 Years Testing
Tests ALL departments with ALL historical years (2008-2019) and ALL question counts
to verify category mixing issue has been resolved completely.
"""

import requests
import json
import time
from datetime import datetime
import traceback
from bs4 import BeautifulSoup
import re

class ComprehensiveYearsVerification:
    def __init__(self):
        self.base_url = "https://rccm-quiz-2025.onrender.com"
        self.session = requests.Session()
        
        # All specialist departments (excluding 基礎科目)
        self.specialist_departments = [
            "道路", "河川・砂防", "都市計画", "造園", "建設環境",
            "鋼構造・コンクリート", "土質・基礎", "施工計画", "上下水道",
            "森林土木", "農業土木", "トンネル"
        ]
        
        # All historical years to test (2008-2019)
        self.years = [f"{year}年度" for year in range(2008, 2020)]
        
        # All question counts
        self.question_counts = ["10問", "20問", "30問"]
        
        self.verification_results = {
            "timestamp": datetime.now().isoformat(),
            "verification_mode": "COMPREHENSIVE_YEARS_2008_2019_VERIFICATION",
            "target_url": self.base_url,
            "years_tested": self.years,
            "departments_tested": self.specialist_departments,
            "question_counts_tested": self.question_counts,
            "detailed_results": {},
            "errors": [],
            "success_statistics": {}
        }
        
    def safe_request(self, method, url, **kwargs):
        """Make safe HTTP request with error handling"""
        try:
            response = self.session.request(method, url, timeout=30, **kwargs)
            return response
        except Exception as e:
            print(f"Request failed: {e}")
            return None
    
    def verify_department_year_combination(self, department, year, count):
        """Verify specific department-year-count combination"""
        print(f"Testing: {department} - {year} - {count}")
        
        result = {
            "department": department,
            "year": year,
            "count": count,
            "access_success": False,
            "quiz_start_success": False,
            "content_verification": {
                "specialist_content_found": False,
                "basic_contamination_found": False,
                "content_quality_score": 0,
                "sample_questions": []
            },
            "errors": []
        }
        
        try:
            # Step 1: Access home page
            home_response = self.safe_request("GET", self.base_url)
            if not home_response or home_response.status_code != 200:
                result["errors"].append(f"Failed to access home page: {home_response.status_code if home_response else 'No response'}")
                return result
                
            # Step 2: Select department
            dept_data = {
                "department": department,
                "category": "専門"
            }
            dept_response = self.safe_request("POST", f"{self.base_url}/select_department", data=dept_data)
            if not dept_response or dept_response.status_code != 200:
                result["errors"].append(f"Failed to select department: {dept_response.status_code if dept_response else 'No response'}")
                return result
                
            # Step 3: Select year
            year_data = {"year": year}
            year_response = self.safe_request("POST", f"{self.base_url}/select_year", data=year_data)
            if not year_response or year_response.status_code != 200:
                result["errors"].append(f"Failed to select year: {year_response.status_code if year_response else 'No response'}")
                return result
                
            # Step 4: Select question count
            count_data = {"count": count}
            count_response = self.safe_request("POST", f"{self.base_url}/select_count", data=count_data)
            if not count_response or count_response.status_code != 200:
                result["errors"].append(f"Failed to select count: {count_response.status_code if count_response else 'No response'}")
                return result
                
            result["access_success"] = True
            
            # Step 5: Start exam
            exam_response = self.safe_request("POST", f"{self.base_url}/start_exam")
            if not exam_response or exam_response.status_code != 200:
                result["errors"].append(f"Failed to start exam: {exam_response.status_code if exam_response else 'No response'}")
                return result
                
            result["quiz_start_success"] = True
            
            # Step 6: Analyze content
            soup = BeautifulSoup(exam_response.text, 'html.parser')
            
            # Look for question content
            question_elements = soup.find_all(['p', 'div', 'span'], class_=re.compile(r'question|problem'))
            if not question_elements:
                # Try broader search
                question_elements = soup.find_all(text=re.compile(r'問題|問\d+'))
            
            # Check for specialist content indicators
            specialist_keywords = {
                "道路": ["道路", "舗装", "交通", "路面", "車道"],
                "河川・砂防": ["河川", "砂防", "治水", "堤防", "流域"],
                "都市計画": ["都市計画", "市街地", "区域", "地区", "都市"],
                "造園": ["造園", "緑地", "公園", "植栽", "景観"],
                "建設環境": ["環境", "騒音", "振動", "大気", "水質"],
                "鋼構造・コンクリート": ["鋼構造", "コンクリート", "鉄筋", "構造", "材料"],
                "土質・基礎": ["土質", "基礎", "地盤", "支持力", "沈下"],
                "施工計画": ["施工", "工程", "管理", "計画", "品質"],
                "上下水道": ["上水道", "下水道", "給水", "排水", "浄水"],
                "森林土木": ["森林", "林道", "治山", "木材", "森林"],
                "農業土木": ["農業", "灌漑", "排水", "農地", "水利"],
                "トンネル": ["トンネル", "掘削", "支保", "覆工", "地山"]
            }
            
            # Check for basic subjects contamination
            basic_keywords = ["基礎科目", "数学", "物理", "化学", "力学の基礎"]
            
            page_text = soup.get_text()
            
            # Check for specialist content
            dept_keywords = specialist_keywords.get(department, [])
            specialist_found = any(keyword in page_text for keyword in dept_keywords)
            result["content_verification"]["specialist_content_found"] = specialist_found
            
            # Check for basic contamination
            basic_found = any(keyword in page_text for keyword in basic_keywords)
            result["content_verification"]["basic_contamination_found"] = basic_found
            
            # Calculate content quality score
            if specialist_found and not basic_found:
                result["content_verification"]["content_quality_score"] = 1.0
            elif specialist_found and basic_found:
                result["content_verification"]["content_quality_score"] = 0.5
            else:
                result["content_verification"]["content_quality_score"] = 0.0
            
            # Extract sample questions
            sample_questions = []
            for elem in question_elements[:3]:  # Get first 3 questions
                text = elem.get_text().strip()
                if text and len(text) > 10:
                    sample_questions.append(text[:200])  # First 200 chars
            result["content_verification"]["sample_questions"] = sample_questions
            
            print(f"✓ {department} - {year} - {count}: Content Quality = {result['content_verification']['content_quality_score']}")
            
        except Exception as e:
            error_msg = f"Exception in verification: {str(e)}"
            result["errors"].append(error_msg)
            print(f"✗ {department} - {year} - {count}: {error_msg}")
            
        return result
    
    def run_comprehensive_verification(self):
        """Run comprehensive verification for all combinations"""
        print("Starting Comprehensive Years Verification (2008-2019)")
        print(f"Testing {len(self.specialist_departments)} departments × {len(self.years)} years × {len(self.question_counts)} counts")
        print(f"Total combinations: {len(self.specialist_departments) * len(self.years) * len(self.question_counts)}")
        
        start_time = time.time()
        
        total_tests = 0
        successful_tests = 0
        high_quality_tests = 0
        
        for department in self.specialist_departments:
            self.verification_results["detailed_results"][department] = {}
            
            for year in self.years:
                self.verification_results["detailed_results"][department][year] = {}
                
                for count in self.question_counts:
                    result = self.verify_department_year_combination(department, year, count)
                    self.verification_results["detailed_results"][department][year][count] = result
                    
                    total_tests += 1
                    if result["access_success"] and result["quiz_start_success"]:
                        successful_tests += 1
                    if result["content_verification"]["content_quality_score"] >= 0.8:
                        high_quality_tests += 1
                    
                    # Small delay to avoid overwhelming the server
                    time.sleep(0.5)
        
        end_time = time.time()
        
        # Calculate statistics
        self.verification_results["success_statistics"] = {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "high_quality_tests": high_quality_tests,
            "success_rate": (successful_tests / total_tests) * 100 if total_tests > 0 else 0,
            "quality_rate": (high_quality_tests / total_tests) * 100 if total_tests > 0 else 0,
            "verification_duration": end_time - start_time
        }
        
        self.verification_results["final_assessment"] = {
            "overall_success": successful_tests == total_tests,
            "category_mixing_resolved": high_quality_tests > (total_tests * 0.8),
            "critical_issues": self.identify_critical_issues()
        }
        
        # Save results
        filename = f"comprehensive_years_verification_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.verification_results, f, ensure_ascii=False, indent=2)
        
        print(f"\n=== Comprehensive Years Verification Complete ===")
        print(f"Total tests: {total_tests}")
        print(f"Successful tests: {successful_tests}")
        print(f"High quality tests: {high_quality_tests}")
        print(f"Success rate: {self.verification_results['success_statistics']['success_rate']:.1f}%")
        print(f"Quality rate: {self.verification_results['success_statistics']['quality_rate']:.1f}%")
        print(f"Duration: {self.verification_results['success_statistics']['verification_duration']:.1f}s")
        print(f"Results saved to: {filename}")
        
        return self.verification_results
    
    def identify_critical_issues(self):
        """Identify critical issues from verification results"""
        issues = []
        
        for department, dept_results in self.verification_results["detailed_results"].items():
            dept_issues = []
            
            for year, year_results in dept_results.items():
                for count, result in year_results.items():
                    if not result["access_success"]:
                        dept_issues.append(f"{year}-{count}: アクセス失敗")
                    elif not result["quiz_start_success"]:
                        dept_issues.append(f"{year}-{count}: クイズ開始失敗")
                    elif result["content_verification"]["basic_contamination_found"]:
                        dept_issues.append(f"{year}-{count}: 基礎科目混入検出")
                    elif result["content_verification"]["content_quality_score"] < 0.5:
                        dept_issues.append(f"{year}-{count}: 専門内容不足")
            
            if dept_issues:
                issues.append(f"{department}: {', '.join(dept_issues[:5])}")  # Limit to 5 issues per dept
        
        return issues

def main():
    """Main execution function"""
    print("RCCM Quiz App - Comprehensive Years Verification (2008-2019)")
    print("=" * 60)
    
    verifier = ComprehensiveYearsVerification()
    results = verifier.run_comprehensive_verification()
    
    return results

if __name__ == "__main__":
    main()