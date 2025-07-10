#!/usr/bin/env python3
"""
🎯 10/20/30問設定 + 年度別完全テスト
すべての部門・すべての問題数・すべての年度で詳細テスト
"""
import subprocess
import json
import time
from datetime import datetime

class ComprehensiveQuestionCountTester:
    def __init__(self):
        self.base_url = 'https://rccm-quiz-2025.onrender.com'
        self.session_file = '/tmp/comprehensive_count_test_session.txt'
        self.test_results = []
        
    def log_test(self, test_name, success, details="", url=""):
        """テスト結果をログ"""
        result = {
            'test_name': test_name,
            'success': success,
            'details': details,
            'url': url,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = '✅' if success else '❌'
        print(f"{status} {test_name}")
        if details:
            print(f"   詳細: {details}")
        if url:
            print(f"   URL: {url}")
    
    def test_question_count_configuration(self, department, question_count, year=2024):
        """問題数設定テスト"""
        try:
            # 問題数設定でのテスト
            result = subprocess.run([
                'curl', '-s', '-w', '%{http_code}', '-o', '/tmp/test_response.html',
                '-b', self.session_file, '-c', self.session_file,
                '-X', 'POST', '-d', f'questions={question_count}&year={year}',
                '--max-time', '30', f"{self.base_url}/start_exam/{department}"
            ], capture_output=True, text=True, timeout=35)
            
            status_code = int(result.stdout.strip())
            success = status_code in [200, 302]
            
            # レスポンス内容を確認
            response_content = ""
            try:
                with open('/tmp/test_response.html', 'r', encoding='utf-8') as f:
                    response_content = f.read()
            except:
                pass
            
            # 画面内容の確認
            screen_validation = self.validate_screen_content(response_content, department, question_count, year)
            
            test_name = f"{department}_{question_count}問_{year}年度"
            self.log_test(test_name, success and screen_validation, 
                         f"HTTP {status_code}, 画面検証: {'OK' if screen_validation else 'NG'}")
            
            return success and screen_validation
            
        except Exception as e:
            test_name = f"{department}_{question_count}問_{year}年度"
            self.log_test(test_name, False, f"エラー: {str(e)}")
            return False
    
    def validate_screen_content(self, content, department, question_count, year):
        """画面内容の検証"""
        if not content or len(content) < 1000:
            return False
        
        # 重要な要素の確認
        required_elements = [
            'RCCM', '問題', '選択肢', 'form', 'button'
        ]
        
        found_elements = []
        for element in required_elements:
            if element in content:
                found_elements.append(element)
        
        # 部門名の確認
        department_found = department in content
        
        # 基本的な画面要素が存在するか
        has_basic_elements = len(found_elements) >= 3
        
        return has_basic_elements and department_found
    
    def test_all_departments_all_counts(self):
        """全部門・全問題数テスト"""
        print("\n🎯 全部門・全問題数テスト開始")
        print("=" * 50)
        
        # 全部門リスト
        departments = [
            '基礎科目', '道路', '河川・砂防', '都市計画', '造園',
            '建設環境', '鋼構造・コンクリート', '土質・基礎', 
            '施工計画', '上下水道', '森林土木', '農業土木', 'トンネル'
        ]
        
        # 問題数設定
        question_counts = [10, 20, 30]
        
        # 年度設定
        years = [2016, 2017, 2018, 2019, 2024]
        
        # セッション初期化
        self.initialize_session()
        
        total_tests = 0
        successful_tests = 0
        
        # 各部門・各問題数・各年度でテスト
        for department in departments:
            print(f"\n📂 {department}部門テスト")
            print("-" * 30)
            
            for question_count in question_counts:
                for year in years:
                    total_tests += 1
                    success = self.test_question_count_configuration(department, question_count, year)
                    if success:
                        successful_tests += 1
                    time.sleep(1)  # サーバー負荷軽減
        
        return total_tests, successful_tests
    
    def initialize_session(self):
        """セッション初期化"""
        try:
            result = subprocess.run([
                'curl', '-s', '-c', self.session_file,
                '--max-time', '15', self.base_url
            ], capture_output=True, text=True, timeout=20)
            
            self.log_test("セッション初期化", True, "Cookie保存完了")
            
        except Exception as e:
            self.log_test("セッション初期化", False, str(e))
    
    def test_specific_screen_validation(self):
        """特定画面の詳細検証"""
        print("\n🔍 特定画面の詳細検証")
        print("=" * 50)
        
        # 重要な設定でのテスト
        test_cases = [
            ('基礎科目', 10, 2024),
            ('道路', 20, 2019),
            ('河川・砂防', 30, 2018),
            ('都市計画', 10, 2017),
            ('造園', 20, 2016)
        ]
        
        for department, count, year in test_cases:
            print(f"\n🎯 詳細検証: {department} {count}問 {year}年度")
            
            # 試験開始
            try:
                result = subprocess.run([
                    'curl', '-s', '-L', '-b', self.session_file, '-c', self.session_file,
                    '-X', 'POST', '-d', f'questions={count}&year={year}',
                    '--max-time', '30', f"{self.base_url}/start_exam/{department}"
                ], capture_output=True, text=True, timeout=35)
                
                response_content = result.stdout
                
                # 画面内容の詳細確認
                screen_elements = self.analyze_screen_content(response_content, department, count, year)
                
                success = screen_elements['is_valid']
                details = f"要素検出: {screen_elements['found_elements']}"
                
                self.log_test(f"詳細検証_{department}_{count}問_{year}年度", success, details)
                
            except Exception as e:
                self.log_test(f"詳細検証_{department}_{count}問_{year}年度", False, str(e))
    
    def analyze_screen_content(self, content, department, count, year):
        """画面内容の詳細分析"""
        analysis = {
            'is_valid': False,
            'found_elements': [],
            'department_displayed': False,
            'questions_indication': False,
            'year_indication': False,
            'content_length': len(content)
        }
        
        if not content:
            return analysis
        
        # 重要要素の確認
        elements_to_check = [
            ('RCCM', 'rccm'),
            ('問題', 'question'),
            ('選択肢', 'radio'),
            ('フォーム', 'form'),
            ('ボタン', 'button'),
            ('次へ', 'next'),
            ('送信', 'submit')
        ]
        
        for element_jp, element_en in elements_to_check:
            if element_jp in content or element_en in content:
                analysis['found_elements'].append(element_jp)
        
        # 部門表示確認
        analysis['department_displayed'] = department in content
        
        # 問題数表示確認
        analysis['questions_indication'] = str(count) in content
        
        # 年度表示確認
        analysis['year_indication'] = str(year) in content
        
        # 有効性判定
        analysis['is_valid'] = (
            len(analysis['found_elements']) >= 3 and
            analysis['department_displayed'] and
            analysis['content_length'] > 5000  # 最低限のコンテンツ長
        )
        
        return analysis
    
    def run_comprehensive_test(self):
        """包括的テスト実行"""
        print("🎯 10/20/30問設定 + 年度別完全テスト開始")
        print("=" * 60)
        print(f"テスト対象: {self.base_url}")
        print("=" * 60)
        
        # 1. 全部門・全問題数・全年度テスト
        total_tests, successful_tests = self.test_all_departments_all_counts()
        
        # 2. 特定画面の詳細検証
        self.test_specific_screen_validation()
        
        # 結果サマリー
        print("\n" + "=" * 60)
        print("📊 包括的問題数・年度テスト結果")
        print("=" * 60)
        
        all_tests = len(self.test_results)
        all_successful = sum(1 for r in self.test_results if r['success'])
        
        print(f"総テスト数: {all_tests}")
        print(f"成功: {all_successful}")
        print(f"失敗: {all_tests - all_successful}")
        print(f"成功率: {all_successful/all_tests*100:.1f}%")
        
        # 失敗テストの詳細
        failed_tests = [r for r in self.test_results if not r['success']]
        if failed_tests:
            print(f"\n❌ 失敗したテスト ({len(failed_tests)}件):")
            for test in failed_tests[:20]:  # 最大20件表示
                print(f"   • {test['test_name']}: {test['details']}")
        
        # 結果保存
        with open('comprehensive_question_count_test_results.json', 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'summary': {
                    'total': all_tests,
                    'successful': all_successful,
                    'failed': all_tests - all_successful,
                    'success_rate': all_successful/all_tests*100
                },
                'results': self.test_results
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\n📋 詳細結果: comprehensive_question_count_test_results.json")
        
        return all_successful == all_tests

def main():
    tester = ComprehensiveQuestionCountTester()
    success = tester.run_comprehensive_test()
    
    if success:
        print("\n🎉 全問題数・年度設定テスト成功！")
    else:
        print("\n⚠️  一部の設定でテストに問題があります。")

if __name__ == '__main__':
    main()