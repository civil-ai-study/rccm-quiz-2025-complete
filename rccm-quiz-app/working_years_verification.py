#!/usr/bin/env python3
"""
Working Years Production Verification
Tests ALL departments with the currently working years (2022-2024) and ALL question counts
to verify category mixing issue has been resolved completely.
"""

import urllib.request
import urllib.parse
import json
import time
from datetime import datetime
import re
import html

class WorkingYearsVerification:
    def __init__(self):
        self.base_url = "https://rccm-quiz-2025.onrender.com"
        
        # All specialist departments (excluding 基礎科目)
        self.specialist_departments = [
            "道路", "河川・砂防", "都市計画", "造園", "建設環境",
            "鋼構造・コンクリート", "土質・基礎", "施工計画", "上下水道",
            "森林土木", "農業土木", "トンネル"
        ]
        
        # Working years based on previous verification
        self.years = ["2022年度", "2023年度", "2024年度"]
        
        # All question counts
        self.question_counts = ["10問", "20問", "30問"]
        
        self.verification_results = {
            "timestamp": datetime.now().isoformat(),
            "verification_mode": "WORKING_YEARS_COMPREHENSIVE_VERIFICATION",
            "target_url": self.base_url,
            "years_tested": self.years,
            "departments_tested": self.specialist_departments,
            "question_counts_tested": self.question_counts,
            "detailed_results": {},
            "errors": [],
            "success_statistics": {}
        }
        
        # Initialize cookie jar for session management
        self.cookie_jar = {}
        
    def safe_request(self, method, url, data=None):
        """Make safe HTTP request with error handling"""
        try:
            if data:
                data = urllib.parse.urlencode(data).encode('utf-8')
            
            req = urllib.request.Request(url, data=data)
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            # Add cookies
            if self.cookie_jar:
                cookie_string = '; '.join([f'{k}={v}' for k, v in self.cookie_jar.items()])
                req.add_header('Cookie', cookie_string)
            
            response = urllib.request.urlopen(req, timeout=30)
            
            # Extract cookies from response
            if 'Set-Cookie' in response.headers:
                cookies = response.headers['Set-Cookie'].split(';')
                for cookie in cookies:
                    if '=' in cookie:
                        key, value = cookie.strip().split('=', 1)
                        self.cookie_jar[key] = value
            
            return response
            
        except Exception as e:
            print(f"Request failed: {e}")
            return None
    
    def analyze_content_quality(self, content, department):
        """Analyze content quality for category mixing"""
        specialist_keywords = {
            "道路": ["道路", "舗装", "交通", "路面", "車道", "アスファルト", "交差点"],
            "河川・砂防": ["河川", "砂防", "治水", "堤防", "流域", "洪水", "土砂災害"],
            "都市計画": ["都市計画", "市街地", "区域", "地区", "都市", "土地利用", "建ぺい率"],
            "造園": ["造園", "緑地", "公園", "植栽", "景観", "樹木", "芝生"],
            "建設環境": ["環境", "騒音", "振動", "大気", "水質", "環境影響", "公害"],
            "鋼構造・コンクリート": ["鋼構造", "コンクリート", "鉄筋", "構造", "材料", "強度", "耐久性"],
            "土質・基礎": ["土質", "基礎", "地盤", "支持力", "沈下", "液状化", "圧密"],
            "施工計画": ["施工", "工程", "管理", "計画", "品質", "工事", "建設"],
            "上下水道": ["上水道", "下水道", "給水", "排水", "浄水", "配水", "水道"],
            "森林土木": ["森林", "林道", "治山", "木材", "森林", "林業", "山地"],
            "農業土木": ["農業", "灌漑", "排水", "農地", "水利", "農業用水", "圃場"],
            "トンネル": ["トンネル", "掘削", "支保", "覆工", "地山", "NATM", "シールド"]
        }
        
        # Check for basic subjects contamination
        basic_keywords = ["基礎科目", "数学", "物理", "化学", "力学の基礎", "材料力学", "構造力学"]
        
        # Check for specialist content
        dept_keywords = specialist_keywords.get(department, [])
        specialist_matches = sum(1 for keyword in dept_keywords if keyword in content)
        
        # Check for basic contamination
        basic_matches = sum(1 for keyword in basic_keywords if keyword in content)
        
        # Calculate scores
        specialist_score = min(specialist_matches / 3, 1.0)  # Up to 1.0 for 3+ matches
        contamination_penalty = min(basic_matches * 0.3, 0.8)  # Up to 0.8 penalty
        
        content_quality_score = max(0, specialist_score - contamination_penalty)
        
        return {
            "specialist_content_found": specialist_matches > 0,
            "basic_contamination_found": basic_matches > 0,
            "specialist_matches": specialist_matches,
            "basic_matches": basic_matches,
            "content_quality_score": content_quality_score
        }
    
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
                "specialist_matches": 0,
                "basic_matches": 0,
                "sample_questions": []
            },
            "errors": []
        }
        
        try:
            # Clear session for each test
            self.cookie_jar = {}
            
            # Step 1: Access home page
            home_response = self.safe_request("GET", self.base_url)
            if not home_response or home_response.getcode() != 200:
                result["errors"].append(f"Failed to access home page: {home_response.getcode() if home_response else 'No response'}")
                return result
                
            # Step 2: Select department
            dept_data = {
                "department": department,
                "category": "専門"
            }
            dept_response = self.safe_request("POST", f"{self.base_url}/select_department", data=dept_data)
            if not dept_response or dept_response.getcode() != 200:
                result["errors"].append(f"Failed to select department: {dept_response.getcode() if dept_response else 'No response'}")
                return result
                
            # Step 3: Select year
            year_data = {"year": year}
            year_response = self.safe_request("POST", f"{self.base_url}/select_year", data=year_data)
            if not year_response or year_response.getcode() != 200:
                result["errors"].append(f"Failed to select year: {year_response.getcode() if year_response else 'No response'}")
                return result
                
            # Step 4: Select question count
            count_data = {"count": count}
            count_response = self.safe_request("POST", f"{self.base_url}/select_count", data=count_data)
            if not count_response or count_response.getcode() != 200:
                result["errors"].append(f"Failed to select count: {count_response.getcode() if count_response else 'No response'}")
                return result
                
            result["access_success"] = True
            
            # Step 5: Start exam
            exam_response = self.safe_request("POST", f"{self.base_url}/start_exam")
            if not exam_response or exam_response.getcode() != 200:
                result["errors"].append(f"Failed to start exam: {exam_response.getcode() if exam_response else 'No response'}")
                return result
                
            result["quiz_start_success"] = True
            
            # Step 6: Analyze content
            content = exam_response.read().decode('utf-8')
            
            # Analyze content quality
            content_analysis = self.analyze_content_quality(content, department)
            result["content_verification"].update(content_analysis)
            
            # Extract sample questions using regex
            question_patterns = [
                r'問\d+[：:]\s*([^<\n]{20,200})',
                r'問題\d+[：:]\s*([^<\n]{20,200})',
                r'<[^>]*>([^<]{50,200}問[^<]{10,100})<'
            ]
            
            sample_questions = []
            for pattern in question_patterns:
                matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
                for match in matches[:3]:  # Get first 3 matches
                    clean_text = html.unescape(match).strip()
                    if clean_text and len(clean_text) > 20:
                        sample_questions.append(clean_text[:200])
                if sample_questions:
                    break
            
            result["content_verification"]["sample_questions"] = sample_questions
            
            # Quality assessment
            quality_score = result["content_verification"]["content_quality_score"]
            if quality_score >= 0.8:
                print(f"✅ {department} - {year} - {count}: EXCELLENT (Quality = {quality_score:.2f})")
            elif quality_score >= 0.5:
                print(f"⚠️ {department} - {year} - {count}: GOOD (Quality = {quality_score:.2f})")
            else:
                print(f"❌ {department} - {year} - {count}: POOR (Quality = {quality_score:.2f})")
            
        except Exception as e:
            error_msg = f"Exception in verification: {str(e)}"
            result["errors"].append(error_msg)
            print(f"💥 {department} - {year} - {count}: {error_msg}")
            
        return result
    
    def run_comprehensive_verification(self):
        """Run comprehensive verification for all combinations"""
        print("=== Working Years Comprehensive Verification ===")
        print(f"Testing {len(self.specialist_departments)} departments × {len(self.years)} years × {len(self.question_counts)} counts")
        print(f"Total combinations: {len(self.specialist_departments) * len(self.years) * len(self.question_counts)}")
        print()
        
        start_time = time.time()
        
        total_tests = 0
        successful_tests = 0
        high_quality_tests = 0
        excellent_tests = 0
        
        for department in self.specialist_departments:
            print(f"\n🔍 Testing Department: {department}")
            self.verification_results["detailed_results"][department] = {}
            
            for year in self.years:
                self.verification_results["detailed_results"][department][year] = {}
                
                for count in self.question_counts:
                    result = self.verify_department_year_combination(department, year, count)
                    self.verification_results["detailed_results"][department][year][count] = result
                    
                    total_tests += 1
                    if result["access_success"] and result["quiz_start_success"]:
                        successful_tests += 1
                    if result["content_verification"]["content_quality_score"] >= 0.5:
                        high_quality_tests += 1
                    if result["content_verification"]["content_quality_score"] >= 0.8:
                        excellent_tests += 1
                    
                    # Small delay to avoid overwhelming the server
                    time.sleep(0.3)
        
        end_time = time.time()
        
        # Calculate statistics
        self.verification_results["success_statistics"] = {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "high_quality_tests": high_quality_tests,
            "excellent_tests": excellent_tests,
            "success_rate": (successful_tests / total_tests) * 100 if total_tests > 0 else 0,
            "quality_rate": (high_quality_tests / total_tests) * 100 if total_tests > 0 else 0,
            "excellence_rate": (excellent_tests / total_tests) * 100 if total_tests > 0 else 0,
            "verification_duration": end_time - start_time
        }
        
        self.verification_results["final_assessment"] = {
            "overall_success": successful_tests == total_tests,
            "category_mixing_resolved": high_quality_tests > (total_tests * 0.8),
            "production_ready": excellent_tests > (total_tests * 0.6),
            "critical_issues": self.identify_critical_issues()
        }
        
        # Save results
        filename = f"working_years_verification_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.verification_results, f, ensure_ascii=False, indent=2)
        
        print(f"\n" + "="*60)
        print(f"🎯 WORKING YEARS VERIFICATION COMPLETE")
        print(f"="*60)
        print(f"📊 Total tests: {total_tests}")
        print(f"✅ Successful tests: {successful_tests}")
        print(f"⭐ High quality tests: {high_quality_tests}")
        print(f"🌟 Excellent tests: {excellent_tests}")
        print(f"📈 Success rate: {self.verification_results['success_statistics']['success_rate']:.1f}%")
        print(f"🎯 Quality rate: {self.verification_results['success_statistics']['quality_rate']:.1f}%")
        print(f"🏆 Excellence rate: {self.verification_results['success_statistics']['excellence_rate']:.1f}%")
        print(f"⏱️ Duration: {self.verification_results['success_statistics']['verification_duration']:.1f}s")
        print(f"💾 Results saved to: {filename}")
        
        # Category mixing assessment
        if self.verification_results["final_assessment"]["category_mixing_resolved"]:
            print(f"✅ CATEGORY MIXING ISSUE: RESOLVED")
        else:
            print(f"❌ CATEGORY MIXING ISSUE: NOT FULLY RESOLVED")
        
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
                    elif result["content_verification"]["content_quality_score"] < 0.3:
                        dept_issues.append(f"{year}-{count}: 専門内容極度不足")
            
            if dept_issues:
                issues.append(f"{department}: {', '.join(dept_issues[:3])}")  # Limit to 3 issues per dept
        
        return issues

def main():
    """Main execution function"""
    print("RCCM Quiz App - Working Years Comprehensive Verification")
    print("Testing category mixing resolution for years 2022-2024")
    print()
    
    verifier = WorkingYearsVerification()
    results = verifier.run_comprehensive_verification()
    
    return results

if __name__ == "__main__":
    main()