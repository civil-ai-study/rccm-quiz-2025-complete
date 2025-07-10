#!/usr/bin/env python3
"""
🛡️ ウルトラシンク - 本番環境画面内容詳細検証
実際の画面表示内容を慎重に確認
"""
import subprocess
import json
import time
from datetime import datetime
import re

class UltraCarefulScreenVerifier:
    def __init__(self):
        self.base_url = 'https://rccm-quiz-2025.onrender.com'
        self.session_file = '/tmp/ultra_careful_session.txt'
        self.test_results = []
        
    def log_test(self, test_name, success, details="", content_sample=""):
        """テスト結果を詳細にログ"""
        result = {
            'test_name': test_name,
            'success': success,
            'details': details,
            'content_sample': content_sample[:200] if content_sample else "",
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = '✅' if success else '❌'
        print(f"{status} {test_name}")
        if details:
            print(f"   詳細: {details}")
        if content_sample and len(content_sample) > 100:
            print(f"   内容確認: {content_sample[:100]}...")
    
    def initialize_session_carefully(self):
        """慎重なセッション初期化"""
        print("🔐 セッション初期化開始")
        try:
            # ホームページアクセスでセッション開始
            result = subprocess.run([
                'curl', '-s', '-c', self.session_file,
                '--max-time', '15', 
                '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                self.base_url
            ], capture_output=True, text=True, timeout=20)
            
            homepage_content = result.stdout
            
            # ホームページ内容の基本検証
            if homepage_content and len(homepage_content) > 5000:
                self.log_test("セッション初期化_ホームページ取得", True, 
                             f"コンテンツサイズ: {len(homepage_content)}文字",
                             homepage_content[:200])
                return True
            else:
                self.log_test("セッション初期化_ホームページ取得", False, 
                             f"コンテンツ不足: {len(homepage_content) if homepage_content else 0}文字")
                return False
                
        except Exception as e:
            self.log_test("セッション初期化_ホームページ取得", False, f"エラー: {str(e)}")
            return False
    
    def verify_screen_content_detailed(self, department, question_count, year):
        """画面内容の詳細検証"""
        print(f"\n🔍 詳細画面検証: {department} {question_count}問 {year}年度")
        
        try:
            # 試験開始リクエスト（実際のHTMLを取得）
            result = subprocess.run([
                'curl', '-s', '-L', 
                '-b', self.session_file, '-c', self.session_file,
                '--max-time', '30',
                '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                '-X', 'POST', '-d', f'questions={question_count}&year={year}',
                f"{self.base_url}/start_exam/{department}"
            ], capture_output=True, text=True, timeout=35)
            
            content = result.stdout
            
            if not content or len(content) < 1000:
                self.log_test(f"画面取得_{department}_{question_count}問_{year}年度", False, 
                             f"コンテンツ不足: {len(content) if content else 0}文字")
                return False
            
            # 詳細な画面要素分析
            analysis = self.analyze_exam_screen(content, department, question_count, year)
            
            # 成功判定
            success = (
                analysis['has_question_content'] and
                analysis['has_answer_options'] and
                analysis['has_navigation'] and
                analysis['department_matches']
            )
            
            details = f"問題内容: {'有' if analysis['has_question_content'] else '無'}, " \
                     f"選択肢: {'有' if analysis['has_answer_options'] else '無'}, " \
                     f"ナビゲーション: {'有' if analysis['has_navigation'] else '無'}, " \
                     f"部門一致: {'有' if analysis['department_matches'] else '無'}"
            
            self.log_test(f"画面内容検証_{department}_{question_count}問_{year}年度", 
                         success, details, analysis['sample_content'])
            
            return success
            
        except Exception as e:
            self.log_test(f"画面内容検証_{department}_{question_count}問_{year}年度", 
                         False, f"エラー: {str(e)}")
            return False
    
    def analyze_exam_screen(self, content, department, question_count, year):
        """試験画面の詳細分析"""
        analysis = {
            'has_question_content': False,
            'has_answer_options': False,
            'has_navigation': False,
            'department_matches': False,
            'content_length': len(content),
            'sample_content': content[:300] if content else "",
            'found_elements': []
        }
        
        if not content:
            return analysis
        
        # 問題内容の確認
        question_indicators = [
            '問題', 'Question', '次の', '以下の', '下記の',
            '正しい', '適切な', '誤っている', '間違っている'
        ]
        for indicator in question_indicators:
            if indicator in content:
                analysis['has_question_content'] = True
                analysis['found_elements'].append(f"問題指標:{indicator}")
                break
        
        # 選択肢の確認
        option_patterns = [
            r'<input[^>]+type=["\']radio["\']',
            r'<input[^>]+name=["\']answer["\']',
            r'value=["\'][1-5]["\']',
            r'（[1-5]）',
            r'\([1-5]\)',
            r'[①②③④⑤]'
        ]
        for pattern in option_patterns:
            if re.search(pattern, content):
                analysis['has_answer_options'] = True
                analysis['found_elements'].append(f"選択肢パターン:{pattern}")
                break
        
        # ナビゲーションの確認
        navigation_indicators = [
            '次へ', '送信', 'submit', '回答', '進む', 'button', 'form'
        ]
        for indicator in navigation_indicators:
            if indicator in content:
                analysis['has_navigation'] = True
                analysis['found_elements'].append(f"ナビゲーション:{indicator}")
                break
        
        # 部門名の確認
        if department in content:
            analysis['department_matches'] = True
            analysis['found_elements'].append(f"部門名確認:{department}")
        
        return analysis
    
    def test_critical_screen_samples(self):
        """重要な画面サンプルテスト"""
        print("\n🎯 重要画面サンプル検証")
        print("=" * 50)
        
        # セッション初期化
        if not self.initialize_session_carefully():
            print("❌ セッション初期化失敗 - テスト中止")
            return False
        
        # 重要な組み合わせをテスト
        critical_cases = [
            ('基礎科目', 10, 2024),  # 最も重要
            ('道路', 10, 2024),      # 人気部門
            ('河川・砂防', 10, 2019), # 過去年度
            ('都市計画', 20, 2024),   # 20問設定
            ('造園', 30, 2024)       # 30問設定
        ]
        
        successful_verifications = 0
        total_verifications = len(critical_cases)
        
        for department, count, year in critical_cases:
            success = self.verify_screen_content_detailed(department, count, year)
            if success:
                successful_verifications += 1
            time.sleep(2)  # サーバー負荷軽減
        
        print(f"\n📊 重要画面検証結果: {successful_verifications}/{total_verifications}")
        return successful_verifications == total_verifications
    
    def verify_homepage_content(self):
        """ホームページ内容の詳細確認"""
        print("\n🏠 ホームページ詳細確認")
        print("=" * 30)
        
        try:
            result = subprocess.run([
                'curl', '-s', '--max-time', '15',
                '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                self.base_url
            ], capture_output=True, text=True, timeout=20)
            
            content = result.stdout
            
            if not content:
                self.log_test("ホームページ内容確認", False, "コンテンツが空")
                return False
            
            # ホームページ要素の確認
            homepage_elements = [
                ('タイトル', 'RCCM'),
                ('部門選択', '部門'),
                ('フォーム', 'form'),
                ('ボタン', 'button'),
                ('リンク', 'href')
            ]
            
            found_elements = []
            for element_name, element_indicator in homepage_elements:
                if element_indicator in content:
                    found_elements.append(element_name)
            
            success = len(found_elements) >= 3
            details = f"発見要素: {found_elements}, コンテンツサイズ: {len(content)}文字"
            
            self.log_test("ホームページ内容確認", success, details, content[:200])
            return success
            
        except Exception as e:
            self.log_test("ホームページ内容確認", False, f"エラー: {str(e)}")
            return False
    
    def run_ultra_careful_verification(self):
        """ウルトラ慎重検証の実行"""
        print("🛡️ ウルトラシンク - 本番環境画面内容詳細検証開始")
        print("=" * 70)
        print(f"テスト対象: {self.base_url}")
        print("=" * 70)
        
        # 1. ホームページ内容確認
        homepage_success = self.verify_homepage_content()
        
        # 2. 重要画面サンプル検証
        critical_success = self.test_critical_screen_samples()
        
        # 結果サマリー
        print("\n" + "=" * 70)
        print("📊 ウルトラ慎重検証結果")
        print("=" * 70)
        
        all_tests = len(self.test_results)
        all_successful = sum(1 for r in self.test_results if r['success'])
        
        print(f"総検証数: {all_tests}")
        print(f"成功: {all_successful}")
        print(f"失敗: {all_tests - all_successful}")
        print(f"成功率: {all_successful/all_tests*100:.1f}%")
        
        # 失敗した検証の詳細
        failed_tests = [r for r in self.test_results if not r['success']]
        if failed_tests:
            print(f"\n❌ 失敗した検証 ({len(failed_tests)}件):")
            for test in failed_tests:
                print(f"   • {test['test_name']}")
                print(f"     詳細: {test['details']}")
                if test['content_sample']:
                    print(f"     内容: {test['content_sample'][:100]}...")
        else:
            print("\n🎉 全検証成功！")
        
        # 結果保存
        with open('ultra_careful_screen_verification_results.json', 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'summary': {
                    'total': all_tests,
                    'successful': all_successful,
                    'failed': all_tests - all_successful,
                    'success_rate': all_successful/all_tests*100
                },
                'verification_results': {
                    'homepage_success': homepage_success,
                    'critical_screens_success': critical_success
                },
                'results': self.test_results
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\n📋 詳細結果: ultra_careful_screen_verification_results.json")
        
        # 成功判定
        overall_success = homepage_success and critical_success and (all_successful == all_tests)
        
        if overall_success:
            print("\n🎉 ウルトラ慎重検証完全成功！")
            print("   実際の画面表示が正常に確認されました。")
        else:
            print("\n⚠️ 検証で問題が検出されました。")
            print("   詳細な調査が必要です。")
        
        return overall_success

def main():
    verifier = UltraCarefulScreenVerifier()
    success = verifier.run_ultra_careful_verification()
    
    return success

if __name__ == '__main__':
    main()