#!/usr/bin/env python3
"""
🛡️ ウルトラシンク修復後検証テスト
2024年度問題の修復を確認
"""
import subprocess
import json
import time
from datetime import datetime

class RepairVerificationTester:
    def __init__(self):
        self.base_url = 'https://rccm-quiz-2025.onrender.com'
        self.session_file = '/tmp/repair_verification_session.txt'
        self.test_results = []
        
    def log_test(self, test_name, success, details="", content_preview=""):
        """テスト結果をログ"""
        result = {
            'test_name': test_name,
            'success': success,
            'details': details,
            'content_preview': content_preview[:200] if content_preview else "",
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = '✅' if success else '❌'
        print(f"{status} {test_name}")
        if details:
            print(f"   詳細: {details}")
    
    def test_2024_year_fix(self):
        """2024年度修復テスト"""
        print("\n🛡️ 2024年度修復テスト")
        print("=" * 40)
        
        # セッション初期化
        try:
            subprocess.run([
                'curl', '-s', '-c', self.session_file, 
                '--max-time', '10', self.base_url
            ], capture_output=True, text=True, timeout=15)
            
            self.log_test("セッション初期化", True)
            
        except Exception as e:
            self.log_test("セッション初期化", False, f"エラー: {str(e)}")
            return False
        
        # 2024年度テストケース
        test_cases = [
            ('基礎科目', 10, 2024),
            ('道路', 10, 2024),
            ('河川・砂防', 5, 2024),
            ('都市計画', 15, 2024)
        ]
        
        success_count = 0
        total_count = len(test_cases)
        
        for department, questions, year in test_cases:
            try:
                result = subprocess.run([
                    'curl', '-s', '-L',
                    '-b', self.session_file, '-c', self.session_file,
                    '-X', 'POST', '-d', f'questions={questions}&year={year}',
                    '--max-time', '25', f"{self.base_url}/start_exam/{department}"
                ], capture_output=True, text=True, timeout=30)
                
                content = result.stdout
                
                # エラーページでないことを確認
                is_error_page = 'エラー | RCCM' in content
                has_good_content = len(content) > 5000 and not is_error_page
                
                # より詳細な内容確認
                has_question_elements = ('問題' in content or 'Question' in content)
                
                success = has_good_content and not is_error_page
                
                if success:
                    success_count += 1
                
                details = f"エラーページ: {'はい' if is_error_page else 'いいえ'}, " \
                         f"コンテンツ良好: {'はい' if has_good_content else 'いいえ'}, " \
                         f"問題要素: {'はい' if has_question_elements else 'いいえ'}"
                
                self.log_test(f"2024年度_{department}_{questions}問", 
                             success, details, content[:300])
                
                time.sleep(1)
                
            except Exception as e:
                self.log_test(f"2024年度_{department}_{questions}問", 
                             False, f"エラー: {str(e)}")
        
        print(f"\n📊 2024年度修復結果: {success_count}/{total_count}")
        return success_count == total_count
    
    def test_other_years(self):
        """他の年度の動作確認"""
        print("\n🔍 他年度動作確認")
        print("=" * 30)
        
        test_cases = [
            ('基礎科目', 10, 2019),
            ('道路', 10, 2018),
            ('河川・砂防', 10, 2017),
            ('都市計画', 10, 2016)
        ]
        
        success_count = 0
        total_count = len(test_cases)
        
        for department, questions, year in test_cases:
            try:
                result = subprocess.run([
                    'curl', '-s', '-w', '%{http_code}', '-o', '/dev/null',
                    '-b', self.session_file, '-c', self.session_file,
                    '-X', 'POST', '-d', f'questions={questions}&year={year}',
                    '--max-time', '20', f"{self.base_url}/start_exam/{department}"
                ], capture_output=True, text=True, timeout=25)
                
                status_code = int(result.stdout.strip())
                success = status_code in [200, 302]
                
                if success:
                    success_count += 1
                
                self.log_test(f"他年度_{department}_{year}年", 
                             success, f"HTTP {status_code}")
                
                time.sleep(0.5)
                
            except Exception as e:
                self.log_test(f"他年度_{department}_{year}年", 
                             False, f"エラー: {str(e)}")
        
        print(f"\n📊 他年度動作確認: {success_count}/{total_count}")
        return success_count == total_count
    
    def test_invalid_years(self):
        """無効年度のエラーハンドリング確認"""
        print("\n🚨 無効年度エラーハンドリング確認")
        print("=" * 45)
        
        invalid_years = [2025, 2026, 2000, 1999]
        
        success_count = 0
        total_count = len(invalid_years)
        
        for year in invalid_years:
            try:
                result = subprocess.run([
                    'curl', '-s', '-L',
                    '-b', self.session_file, '-c', self.session_file,
                    '-X', 'POST', '-d', f'questions=10&year={year}',
                    '--max-time', '20', f"{self.base_url}/start_exam/基礎科目"
                ], capture_output=True, text=True, timeout=25)
                
                content = result.stdout
                
                # エラーページが適切に表示されることを確認
                is_error_page = 'エラー | RCCM' in content
                has_year_error = f'{year}' in content and '利用できません' in content
                
                success = is_error_page and has_year_error
                
                details = f"エラーページ: {'はい' if is_error_page else 'いいえ'}, " \
                         f"年度エラー: {'はい' if has_year_error else 'いいえ'}"
                
                if success:
                    success_count += 1
                
                self.log_test(f"無効年度_{year}年", success, details)
                
                time.sleep(0.5)
                
            except Exception as e:
                self.log_test(f"無効年度_{year}年", False, f"エラー: {str(e)}")
        
        print(f"\n📊 無効年度エラーハンドリング: {success_count}/{total_count}")
        return success_count == total_count
    
    def run_repair_verification(self):
        """修復検証テストの実行"""
        print("🛡️ ウルトラシンク修復後検証テスト開始")
        print("=" * 60)
        print(f"検証対象: {self.base_url}")
        print("=" * 60)
        
        # 1. 2024年度修復テスト
        fix_2024_success = self.test_2024_year_fix()
        
        # 2. 他年度動作確認
        other_years_success = self.test_other_years()
        
        # 3. 無効年度エラーハンドリング確認
        invalid_years_success = self.test_invalid_years()
        
        # 結果サマリー
        print("\n" + "=" * 60)
        print("📊 修復検証結果サマリー")
        print("=" * 60)
        
        all_tests = len(self.test_results)
        all_successful = sum(1 for r in self.test_results if r['success'])
        
        print(f"総検証数: {all_tests}")
        print(f"成功: {all_successful}")
        print(f"失敗: {all_tests - all_successful}")
        print(f"成功率: {all_successful/all_tests*100:.1f}%")
        
        # カテゴリ別結果
        print(f"\n📋 カテゴリ別結果:")
        print(f"├── 2024年度修復: {'✅ 成功' if fix_2024_success else '❌ 失敗'}")
        print(f"├── 他年度動作: {'✅ 成功' if other_years_success else '❌ 失敗'}")
        print(f"└── 無効年度エラー: {'✅ 成功' if invalid_years_success else '❌ 失敗'}")
        
        # 失敗した検証の詳細
        failed_tests = [r for r in self.test_results if not r['success']]
        if failed_tests:
            print(f"\n❌ 失敗した検証 ({len(failed_tests)}件):")
            for test in failed_tests:
                print(f"   • {test['test_name']}: {test['details']}")
        else:
            print("\n🎉 全検証成功！修復が正常に完了しました！")
        
        # 結果保存
        with open('repair_verification_results.json', 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'summary': {
                    'total': all_tests,
                    'successful': all_successful,
                    'failed': all_tests - all_successful,
                    'success_rate': all_successful/all_tests*100
                },
                'category_results': {
                    '2024_year_fix': fix_2024_success,
                    'other_years': other_years_success,
                    'invalid_years': invalid_years_success
                },
                'repair_successful': fix_2024_success and other_years_success and invalid_years_success,
                'results': self.test_results
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\n📋 詳細結果: repair_verification_results.json")
        
        overall_success = fix_2024_success and other_years_success and invalid_years_success
        
        if overall_success:
            print("\n🎉 ウルトラシンク修復完全成功！")
            print("   2024年度問題が解決され、すべての年度が正常に動作しています。")
        else:
            print("\n⚠️ 修復に問題があります。追加の調査が必要です。")
        
        return overall_success

def main():
    tester = RepairVerificationTester()
    success = tester.run_repair_verification()
    
    return success

if __name__ == '__main__':
    main()