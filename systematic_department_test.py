#!/usr/bin/env python3
"""
Systematic Department Mixing Test for RCCM Quiz App
Tests the critical department mixing issue that was unresolved for 1+ month
"""

import requests
import re
import time
import json
from bs4 import BeautifulSoup

# Department mapping from the app (as found in app.py)
DEPARTMENT_TO_CATEGORY_MAPPING = {
    'basic': '共通',
    'road': '道路', 
    'river': '河川、砂防及び海岸・海洋',
    'urban': '都市計画及び地方計画',
    'garden': '造園',
    'env': '建設環境',
    'steel': '鋼構造及びコンクリート',
    'soil': '土質及び基礎',
    'construction': '施工計画、施工設備及び積算',
    'water': '上水道及び工業用水道',
    'forest': '森林土木',
    'agri': '農業土木',
    'tunnel': 'トンネル'
}

BASE_URL = 'http://localhost:5005'

class DepartmentMixingTester:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.results = {}
        
    def test_homepage_access(self):
        """Test basic homepage access"""
        try:
            response = self.session.get(BASE_URL, timeout=10)
            if response.status_code == 200:
                print("SUCCESS: Homepage accessible")
                return True
            else:
                print(f"FAIL: Homepage failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"ERROR: Homepage connection error: {e}")
            return False
    
    def start_department_exam(self, dept_id):
        """Start exam for a specific department"""
        try:
            # Access the exam start endpoint for the department
            url = f"{BASE_URL}/exam?question_type=specialist&department={dept_id}"
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 200:
                return response.text
            else:
                print(f"FAIL: Failed to start {dept_id} exam: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"ERROR: Error starting {dept_id} exam: {e}")
            return None
    
    def extract_question_info(self, html_content):
        """Extract question information from HTML"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Look for question text
        question_element = soup.find(['h2', 'h3', 'p'], text=re.compile(r'問\s*\d+|Question'))
        if not question_element:
            # Try to find any element containing question-like content
            question_element = soup.find(text=re.compile(r'[。？]'))
            if question_element:
                question_element = question_element.parent
        
        if question_element:
            question_text = question_element.get_text(strip=True)
            
            # Extract surrounding context for analysis
            context = ""
            for sibling in question_element.find_next_siblings()[:3]:
                context += sibling.get_text(strip=True) + " "
            
            return {
                'question_text': question_text,
                'context': context,
                'raw_html': html_content[:1000]  # First 1KB for debugging
            }
        
        return {
            'question_text': 'No question found',
            'context': '',
            'raw_html': html_content[:1000]
        }
    
    def analyze_question_relevance(self, question_info, expected_department):
        """Analyze if question is relevant to the expected department"""
        expected_category = DEPARTMENT_TO_CATEGORY_MAPPING[expected_department]
        question_text = question_info['question_text'].lower()
        context = question_info['context'].lower()
        combined_text = question_text + " " + context
        
        # Department-specific keywords for detection
        department_keywords = {
            'road': ['道路', '舗装', 'アスファルト', '交通', '路面', '車道', '歩道'],
            'river': ['河川', '砂防', '海岸', '海洋', '治水', '堤防', '洪水'],
            'urban': ['都市計画', '地方計画', '区画整理', '開発許可', '用途地域'],
            'garden': ['造園', '公園', '緑地', '植栽', '景観'],
            'env': ['建設環境', '環境影響', '騒音', '振動', '大気汚染'],
            'steel': ['鋼構造', 'コンクリート', '鉄筋', '鋼材', '構造設計'],
            'soil': ['土質', '基礎', '地盤', '支持力', 'N値'],
            'construction': ['施工計画', '積算', '工程', '品質管理'],
            'water': ['上水道', '工業用水', '浄水', '配水', '水道'],
            'forest': ['森林土木', '治山', '林道', '森林'],
            'agri': ['農業土木', '農地', '用排水', '圃場'],
            'tunnel': ['トンネル', '掘削', 'NATM', 'シールド']
        }
        
        # Count keyword matches
        expected_keywords = department_keywords.get(expected_department, [])
        matches = sum(1 for keyword in expected_keywords if keyword in combined_text)
        
        # Check for other department keywords (mixing detection)
        other_matches = {}
        for dept, keywords in department_keywords.items():
            if dept != expected_department:
                count = sum(1 for keyword in keywords if keyword in combined_text)
                if count > 0:
                    other_matches[dept] = count
        
        return {
            'expected_matches': matches,
            'other_department_matches': other_matches,
            'likely_correct_department': matches > 0,
            'potential_mixing': len(other_matches) > 0
        }
    
    def test_department(self, dept_id):
        """Test a single department for mixing issues"""
        print(f"\nTesting department: {dept_id} ({DEPARTMENT_TO_CATEGORY_MAPPING[dept_id]})")
        
        html_content = self.start_department_exam(dept_id)
        if not html_content:
            return {
                'status': 'failed',
                'error': 'Could not start exam'
            }
        
        question_info = self.extract_question_info(html_content)
        analysis = self.analyze_question_relevance(question_info, dept_id)
        
        result = {
            'department_id': dept_id,
            'expected_category': DEPARTMENT_TO_CATEGORY_MAPPING[dept_id],
            'question_info': question_info,
            'analysis': analysis,
            'status': 'success'
        }
        
        # Report findings
        if analysis['likely_correct_department']:
            print(f"SUCCESS: Questions appear relevant to {dept_id}")
        else:
            print(f"WARNING: Questions may not be relevant to {dept_id}")
            
        if analysis['potential_mixing']:
            print(f"ALERT: POTENTIAL MIXING DETECTED: {analysis['other_department_matches']}")
        else:
            print(f"SUCCESS: No obvious mixing detected")
            
        return result
    
    def run_comprehensive_test(self):
        """Run comprehensive test on all departments"""
        print("Starting Comprehensive Department Mixing Test")
        print("=" * 60)
        
        # Test homepage first
        if not self.test_homepage_access():
            return
        
        # Test each specialist department (skip 'basic')
        specialist_departments = [dept for dept in DEPARTMENT_TO_CATEGORY_MAPPING.keys() if dept != 'basic']
        
        for dept_id in specialist_departments:
            try:
                result = self.test_department(dept_id)
                self.results[dept_id] = result
                time.sleep(1)  # Brief pause between tests
            except Exception as e:
                print(f"ERROR: Error testing {dept_id}: {e}")
                self.results[dept_id] = {
                    'status': 'error',
                    'error': str(e)
                }
        
        self.generate_report()
    
    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 60)
        print("COMPREHENSIVE TEST REPORT")
        print("=" * 60)
        
        total_departments = len(self.results)
        successful_tests = sum(1 for r in self.results.values() if r.get('status') == 'success')
        departments_with_mixing = sum(1 for r in self.results.values() 
                                    if r.get('analysis', {}).get('potential_mixing', False))
        departments_with_correct_questions = sum(1 for r in self.results.values() 
                                               if r.get('analysis', {}).get('likely_correct_department', False))
        
        print(f"Total departments tested: {total_departments}")
        print(f"Successful tests: {successful_tests}")
        print(f"Departments with correct questions: {departments_with_correct_questions}")
        print(f"Departments with potential mixing: {departments_with_mixing}")
        
        print("\nDETAILED RESULTS:")
        print("-" * 40)
        
        for dept_id, result in self.results.items():
            status = result.get('status', 'unknown')
            category = DEPARTMENT_TO_CATEGORY_MAPPING[dept_id]
            
            if status == 'success':
                analysis = result.get('analysis', {})
                correct = "OK" if analysis.get('likely_correct_department') else "WARN"
                mixing = "ALERT" if analysis.get('potential_mixing') else "OK"
                print(f"{dept_id:12} ({category:20}) | Relevant: {correct} | Mixing: {mixing}")
            else:
                print(f"{dept_id:12} ({category:20}) | FAILED: {result.get('error', 'Unknown error')}")
        
        # Overall assessment
        print("\nFINAL ASSESSMENT:")
        print("-" * 40)
        
        if departments_with_mixing == 0:
            print("NO DEPARTMENT MIXING DETECTED - The fix appears successful!")
        else:
            print(f"MIXING ISSUES FOUND in {departments_with_mixing} departments")
            
        if departments_with_correct_questions == successful_tests:
            print("ALL departments show relevant questions")
        else:
            print(f"{successful_tests - departments_with_correct_questions} departments may have irrelevant questions")
        
        # Save detailed results
        with open('department_test_results.json', 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        print(f"\nDetailed results saved to: department_test_results.json")


if __name__ == "__main__":
    tester = DepartmentMixingTester()
    tester.run_comprehensive_test()