#!/usr/bin/env python3
"""
Browser-like Production Verification
Mimics actual browser interaction to test category mixing resolution
"""

import urllib.request
import urllib.parse
import json
import time
from datetime import datetime
import re

class BrowserLikeVerification:
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
            "verification_mode": "BROWSER_LIKE_VERIFICATION",
            "target_url": self.base_url,
            "years_tested": self.years,
            "departments_tested": self.specialist_departments,
            "question_counts_tested": self.question_counts,
            "detailed_results": {},
            "errors": [],
            "success_statistics": {}
        }
        
    def safe_request(self, url, data=None, method="GET"):
        """Make safe HTTP request"""
        try:
            if data and method == "POST":
                data = urllib.parse.urlencode(data).encode('utf-8')
                req = urllib.request.Request(url, data=data, method="POST")
                req.add_header('Content-Type', 'application/x-www-form-urlencoded')
            else:
                req = urllib.request.Request(url, method=method)
            
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            req.add_header('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')
            
            response = urllib.request.urlopen(req, timeout=30)
            return response
            
        except Exception as e:
            print(f"Request failed: {e}")
            return None
    
    def test_url_direct_access(self, department, year, count):
        """Test direct URL access like browser navigation"""
        print(f"Testing: {department} - {year} - {count}")
        
        result = {
            "department": department,
            "year": year,
            "count": count,
            "url_access_success": False,
            "contains_questions": False,
            "specialist_content_found": False,
            "basic_contamination_found": False,
            "content_quality_score": 0.0,
            "errors": []
        }
        
        try:
            # Try direct URL approach
            url_params = {
                "department": department,
                "category": "専門",
                "year": year,
                "count": count
            }
            
            # Try the start_exam endpoint directly with all parameters
            test_url = f"{self.base_url}/start_exam?" + urllib.parse.urlencode(url_params)
            
            response = self.safe_request(test_url)
            
            if response and response.getcode() == 200:
                result["url_access_success"] = True
                content = response.read().decode('utf-8')
                
                # Check for question content
                question_indicators = ["問題", "問1", "問2", "問3", "選択肢", "回答"]
                result["contains_questions"] = any(indicator in content for indicator in question_indicators)
                
                # Check for specialist content
                specialist_keywords = {
                    "道路": ["道路", "舗装", "交通", "アスファルト"],
                    "河川・砂防": ["河川", "砂防", "治水", "堤防"],
                    "都市計画": ["都市計画", "市街地", "区域"],
                    "造園": ["造園", "緑地", "公園", "植栽"],
                    "建設環境": ["環境", "騒音", "振動", "大気"],
                    "鋼構造・コンクリート": ["鋼構造", "コンクリート", "鉄筋"],
                    "土質・基礎": ["土質", "基礎", "地盤", "支持力"],
                    "施工計画": ["施工", "工程", "管理", "計画"],
                    "上下水道": ["上水道", "下水道", "給水", "排水"],
                    "森林土木": ["森林", "林道", "治山"],
                    "農業土木": ["農業", "灌漑", "農地", "水利"],
                    "トンネル": ["トンネル", "掘削", "支保", "覆工"]
                }
                
                basic_keywords = ["基礎科目", "数学", "物理", "化学", "力学の基礎"]
                
                dept_keywords = specialist_keywords.get(department, [])
                specialist_found = any(keyword in content for keyword in dept_keywords)
                basic_found = any(keyword in content for keyword in basic_keywords)
                
                result["specialist_content_found"] = specialist_found
                result["basic_contamination_found"] = basic_found
                
                # Calculate quality score
                if specialist_found and not basic_found:
                    result["content_quality_score"] = 1.0
                elif specialist_found and basic_found:
                    result["content_quality_score"] = 0.5
                elif not specialist_found and not basic_found:
                    result["content_quality_score"] = 0.2  # Neutral
                else:
                    result["content_quality_score"] = 0.0  # Basic only
                
                status = "✅ PASS" if result["content_quality_score"] >= 0.5 else "❌ FAIL"
                print(f"   {status} - Questions: {result['contains_questions']}, Quality: {result['content_quality_score']:.1f}")
                
            else:
                error_code = response.getcode() if response else "No response"
                result["errors"].append(f"URL access failed: {error_code}")
                print(f"   ❌ FAIL - URL access failed: {error_code}")
                
        except Exception as e:
            error_msg = f"Exception: {str(e)}"
            result["errors"].append(error_msg)
            print(f"   💥 ERROR - {error_msg}")
        
        return result
    
    def run_verification(self):
        """Run browser-like verification"""
        print("=== Browser-like Production Verification ===")
        print(f"Testing {len(self.specialist_departments)} departments × {len(self.years)} years × {len(self.question_counts)} counts")
        print(f"Total combinations: {len(self.specialist_departments) * len(self.years) * len(self.question_counts)}")
        print()
        
        start_time = time.time()
        
        total_tests = 0
        successful_tests = 0
        high_quality_tests = 0
        
        for department in self.specialist_departments:
            print(f"\n🔍 Testing Department: {department}")
            self.verification_results["detailed_results"][department] = {}
            
            for year in self.years:
                self.verification_results["detailed_results"][department][year] = {}
                
                for count in self.question_counts:
                    result = self.test_url_direct_access(department, year, count)
                    self.verification_results["detailed_results"][department][year][count] = result
                    
                    total_tests += 1
                    if result["url_access_success"] and result["contains_questions"]:
                        successful_tests += 1
                    if result["content_quality_score"] >= 0.5:
                        high_quality_tests += 1
                    
                    time.sleep(0.2)  # Small delay
        
        end_time = time.time()
        
        # Calculate final statistics
        self.verification_results["success_statistics"] = {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "high_quality_tests": high_quality_tests,
            "success_rate": (successful_tests / total_tests) * 100 if total_tests > 0 else 0,
            "quality_rate": (high_quality_tests / total_tests) * 100 if total_tests > 0 else 0,
            "verification_duration": end_time - start_time
        }
        
        # Final assessment
        category_mixing_resolved = high_quality_tests > (total_tests * 0.8)
        
        # Save results
        filename = f"browser_like_verification_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.verification_results, f, ensure_ascii=False, indent=2)
        
        print(f"\n" + "="*60)
        print(f"🎯 BROWSER-LIKE VERIFICATION COMPLETE")
        print(f"="*60)
        print(f"📊 Total tests: {total_tests}")
        print(f"✅ Successful tests: {successful_tests}")
        print(f"⭐ High quality tests: {high_quality_tests}")
        print(f"📈 Success rate: {self.verification_results['success_statistics']['success_rate']:.1f}%")
        print(f"🎯 Quality rate: {self.verification_results['success_statistics']['quality_rate']:.1f}%")
        print(f"⏱️ Duration: {self.verification_results['success_statistics']['verification_duration']:.1f}s")
        print(f"💾 Results saved to: {filename}")
        
        # Category mixing assessment
        if category_mixing_resolved:
            print(f"✅ CATEGORY MIXING ISSUE: RESOLVED")
        else:
            print(f"❌ CATEGORY MIXING ISSUE: NEEDS ATTENTION")
        
        return self.verification_results

def main():
    """Main execution function"""
    print("RCCM Quiz App - Browser-like Verification")
    print("Testing category mixing resolution with browser-like requests")
    print()
    
    verifier = BrowserLikeVerification()
    results = verifier.run_verification()
    
    return results

if __name__ == "__main__":
    main()