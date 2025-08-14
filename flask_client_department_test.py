#!/usr/bin/env python3
"""
Flask Test Client Department Mixing Test
Tests the critical department mixing issue using Flask's built-in test client
This bypasses connection timeout issues while thoroughly testing the department ID system.
"""

import sys
import os

# Add the app directory to Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.join(script_dir, 'rccm-quiz-app')
sys.path.insert(0, app_dir)

try:
    from app import app, DEPARTMENT_TO_CATEGORY_MAPPING
    print("SUCCESS: App imported successfully")
except Exception as e:
    print(f"ERROR: Failed to import app: {e}")
    sys.exit(1)

import re
import json
from datetime import datetime

class DepartmentMixingTester:
    def __init__(self):
        self.app = app
        self.client = app.test_client()
        self.results = {}
        
    def extract_question_content(self, html_content):
        """Extract question text from HTML response"""
        # Look for question patterns
        question_patterns = [
            r'<h2[^>]*>.*?問題.*?(\d+).*?</h2>',
            r'<h3[^>]*>.*?問.*?(\d+).*?</h3>',
            r'問題\s*\d+[.:：]?(.*?)(?=選択肢|$)',
            r'問\s*\d+[.:：]?(.*?)(?=\(|選択肢|$)'
        ]
        
        for pattern in question_patterns:
            match = re.search(pattern, html_content, re.DOTALL | re.IGNORECASE)
            if match:
                return match.group(0)
        
        # Fallback: look for any text that seems like a question
        soup_like = re.sub(r'<[^>]+>', ' ', html_content)
        if '。' in soup_like or '？' in soup_like:
            lines = soup_like.split('\n')
            for line in lines:
                if any(char in line for char in ['。', '？']) and len(line.strip()) > 20:
                    return line.strip()[:200]
        
        return "No question content found"
    
    def analyze_question_relevance(self, question_content, dept_id):
        """Analyze if question content matches expected department"""
        expected_category = DEPARTMENT_TO_CATEGORY_MAPPING[dept_id]
        
        # Department-specific keywords for detection
        department_keywords = {
            'road': ['道路', '舗装', 'アスファルト', '交通', '路面', '車道', '歩道', 'コンクリート舗装', 'アスファルト舗装'],
            'river': ['河川', '砂防', '海岸', '海洋', '治水', '堤防', '洪水', '流量', '水位', '河道'],
            'urban': ['都市計画', '地方計画', '区画整理', '開発許可', '用途地域', '都市', '計画'],
            'garden': ['造園', '公園', '緑地', '植栽', '景観', '庭園', '樹木'],
            'env': ['建設環境', '環境影響', '騒音', '振動', '大気汚染', '環境', '公害'],
            'steel': ['鋼構造', 'コンクリート', '鉄筋', '鋼材', '構造設計', '鉄骨', '構造'],
            'soil': ['土質', '基礎', '地盤', '支持力', 'N値', '土', '地下水', '圧密'],
            'construction': ['施工計画', '積算', '工程', '品質管理', '安全管理', '施工'],
            'water': ['上水道', '工業用水', '浄水', '配水', '水道', '給水', '取水'],
            'forest': ['森林土木', '治山', '林道', '森林', '山地', '木材'],
            'agri': ['農業土木', '農地', '用排水', '圃場', '農業', '灌漑', '排水'],
            'tunnel': ['トンネル', '掘削', 'NATM', 'シールド', '坑道', '地下']
        }
        
        keywords = department_keywords.get(dept_id, [])
        matches = sum(1 for keyword in keywords if keyword in question_content)
        
        # Check for other department keywords (mixing detection)
        other_matches = {}
        for other_dept, other_keywords in department_keywords.items():
            if other_dept != dept_id:
                count = sum(1 for keyword in other_keywords if keyword in question_content)
                if count > 0:
                    other_matches[other_dept] = count
        
        return {
            'expected_matches': matches,
            'other_department_matches': other_matches,
            'likely_correct_department': matches > 0,
            'potential_mixing': len(other_matches) > 0 and matches == 0
        }
    
    def test_department_exam_start(self, dept_id):
        """Test starting exam for a specific department"""
        try:
            # Test the department exam start route
            url = f'/exam?question_type=specialist&department={dept_id}'
            
            with self.client as c:
                response = c.get(url)
                
                if response.status_code == 200:
                    # Successfully got a question page
                    html_content = response.get_data(as_text=True)
                    question_content = self.extract_question_content(html_content)
                    analysis = self.analyze_question_relevance(question_content, dept_id)
                    
                    # Check session for proper department setup
                    with c.session_transaction() as sess:
                        session_dept = sess.get('selected_department')
                        session_category = sess.get('exam_category')
                        question_ids = sess.get('exam_question_ids', [])
                    
                    return {
                        'status': 'success',
                        'question_content': question_content[:200],  # Truncate for readability
                        'analysis': analysis,
                        'session_info': {
                            'department': session_dept,
                            'category': session_category,
                            'question_count': len(question_ids)
                        }
                    }
                    
                elif response.status_code == 302:
                    # Redirect, probably to exam page - follow it
                    location = response.location
                    if '/exam' in location:
                        follow_response = c.get('/exam')
                        if follow_response.status_code == 200:
                            html_content = follow_response.get_data(as_text=True)
                            question_content = self.extract_question_content(html_content)
                            analysis = self.analyze_question_relevance(question_content, dept_id)
                            
                            return {
                                'status': 'success',
                                'question_content': question_content[:200],
                                'analysis': analysis,
                                'redirect_followed': True
                            }
                    
                    return {
                        'status': 'redirect',
                        'location': location
                    }
                else:
                    return {
                        'status': 'http_error',
                        'status_code': response.status_code
                    }
                    
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def test_all_departments(self):
        """Test all specialist departments"""
        print("Starting Flask Client Department Mixing Test")
        print("=" * 60)
        
        specialist_departments = [dept for dept in DEPARTMENT_TO_CATEGORY_MAPPING.keys() if dept != 'basic']
        
        for dept_id in specialist_departments:
            expected_category = DEPARTMENT_TO_CATEGORY_MAPPING[dept_id]
            print(f"\nTesting: {dept_id} -> {expected_category}")
            
            result = self.test_department_exam_start(dept_id)
            self.results[dept_id] = result
            
            # Report immediate results
            if result['status'] == 'success':
                analysis = result.get('analysis', {})
                if analysis.get('likely_correct_department'):
                    print("  SUCCESS: Questions appear relevant to department")
                else:
                    print("  WARNING: Questions may not be relevant to department")
                
                if analysis.get('potential_mixing'):
                    print(f"  ALERT: Potential mixing detected: {analysis['other_department_matches']}")
                else:
                    print("  SUCCESS: No obvious mixing detected")
                    
                # Show sample question content
                if 'question_content' in result:
                    print(f"  Sample: {result['question_content'][:100]}...")
                    
            else:
                print(f"  ERROR: {result.get('error', 'Unknown error')}")
        
        self.generate_report()
    
    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "=" * 60)
        print("DEPARTMENT MIXING TEST REPORT")
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
            category = DEPARTMENT_TO_CATEGORY_MAPPING[dept_id]
            status = result.get('status', 'unknown')
            
            if status == 'success':
                analysis = result.get('analysis', {})
                correct = "OK" if analysis.get('likely_correct_department') else "WARN"
                mixing = "ALERT" if analysis.get('potential_mixing') else "OK"
                print(f"{dept_id:12} ({category:20}) | Relevant: {correct:4} | Mixing: {mixing:5}")
            else:
                print(f"{dept_id:12} ({category:20}) | FAILED: {result.get('error', 'Unknown')}")
        
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
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'department_test_results_{timestamp}.json'
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        print(f"\nDetailed results saved to: {filename}")
        
        return departments_with_mixing == 0 and departments_with_correct_questions == successful_tests


def main():
    """Main test execution"""
    tester = DepartmentMixingTester()
    success = tester.test_all_departments()
    
    if success:
        print("\nCONCLUSION: Department mixing issue appears to be RESOLVED!")
    else:
        print("\nCONCLUSION: Department mixing issues still exist.")
    
    return success


if __name__ == "__main__":
    main()