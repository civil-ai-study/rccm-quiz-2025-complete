#!/usr/bin/env python3
"""
🚀 本番環境準拠 RCCM アプリケーション検証テスト
実際のHTTPリクエスト + 本番サーバーテスト
"""
import sys
import os
import ast
import subprocess
import json
import time
from datetime import datetime

class ProductionEquivalentTester:
    def __init__(self):
        self.base_path = '/mnt/c/Users/ABC/Desktop/rccm-quiz-app/rccm-quiz-app'
        self.production_url = 'https://rccm-quiz-2025.onrender.com'
        self.test_results = []
        
    def log_test(self, test_name, success, details=""):
        """テスト結果をログ"""
        result = {
            'test_name': test_name,
            'success': success,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = '✅' if success else '❌'
        print(f"{status} テスト{len(self.test_results)}/50: {test_name}")
        if details and not success:
            print(f"   詳細: {details}")
    
    def test_syntax_validation(self):
        """構文検証テスト（本番環境で最重要）"""
        files_to_check = ['app.py', 'utils.py', 'config.py', 'gamification.py']
        
        for file in files_to_check:
            file_path = os.path.join(self.base_path, file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                ast.parse(content, filename=file)
                self.log_test(f"{file}構文チェック", True)
            except SyntaxError as e:
                self.log_test(f"{file}構文チェック", False, f"行{e.lineno}: {e.msg}")
            except Exception as e:
                self.log_test(f"{file}構文チェック", False, str(e))
    
    def test_data_file_integrity(self):
        """データファイル整合性テスト（本番環境でのデータ読み込み）"""
        data_files = [
            'data/4-1.csv',
            'data/4-2_2016.csv',
            'data/4-2_2017.csv', 
            'data/4-2_2018.csv',
            'data/4-2_2019.csv'
        ]
        
        for file in data_files:
            file_path = os.path.join(self.base_path, file)
            try:
                # UTF-8で試行
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    if len(lines) > 10:  # 最低10行は必要
                        self.log_test(f"{file}データ整合性", True, f"{len(lines)}行")
                    else:
                        self.log_test(f"{file}データ整合性", False, f"データ不足: {len(lines)}行")
            except UnicodeDecodeError:
                try:
                    # Shift_JISで再試行
                    with open(file_path, 'r', encoding='shift_jis') as f:
                        lines = f.readlines()
                        self.log_test(f"{file}データ整合性", True, f"{len(lines)}行 (Shift_JIS)")
                except Exception as e:
                    self.log_test(f"{file}データ整合性", False, str(e))
            except Exception as e:
                self.log_test(f"{file}データ整合性", False, str(e))
    
    def test_production_server_status(self):
        """本番サーバー状態テスト"""
        try:
            # ホームページアクセス
            result = subprocess.run([
                'curl', '-s', '-w', '%{http_code}', '-o', '/dev/null', 
                '--max-time', '30', self.production_url
            ], capture_output=True, text=True, timeout=35)
            
            status_code = int(result.stdout.strip())
            if status_code == 200:
                self.log_test("本番サーバーアクセス", True, f"HTTP {status_code}")
            else:
                self.log_test("本番サーバーアクセス", False, f"HTTP {status_code}")
        except Exception as e:
            self.log_test("本番サーバーアクセス", False, str(e))
    
    def test_production_endpoints(self):
        """本番エンドポイントテスト（実際のHTTPリクエスト）"""
        endpoints = [
            {
                'name': '基礎科目試験開始',
                'method': 'POST',
                'path': '/start_exam/基礎科目',
                'data': 'questions=10&year=2024',
                'expected': [200, 302]
            },
            {
                'name': '専門科目道路部門',
                'method': 'POST', 
                'path': '/start_exam/道路',
                'data': 'questions=10&year=2024',
                'expected': [200, 302]
            },
            {
                'name': '専門科目河川部門',
                'method': 'POST',
                'path': '/start_exam/河川・砂防',
                'data': 'questions=10&year=2024', 
                'expected': [200, 302]
            }
        ]
        
        for endpoint in endpoints:
            try:
                url = f"{self.production_url}{endpoint['path']}"
                cmd = ['curl', '-s', '-w', '%{http_code}', '-o', '/dev/null', '--max-time', '30']
                
                if endpoint['method'] == 'POST':
                    cmd.extend(['-X', 'POST', '-d', endpoint['data']])
                
                cmd.append(url)
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=35)
                status_code = int(result.stdout.strip())
                
                if status_code in endpoint['expected']:
                    self.log_test(endpoint['name'], True, f"HTTP {status_code}")
                else:
                    self.log_test(endpoint['name'], False, f"HTTP {status_code} (期待値: {endpoint['expected']})")
                    
            except Exception as e:
                self.log_test(endpoint['name'], False, str(e))
    
    def test_critical_templates(self):
        """重要テンプレートの存在確認"""
        templates = ['base.html', 'index.html', 'exam.html', 'result.html']
        template_dir = os.path.join(self.base_path, 'templates')
        
        for template in templates:
            template_path = os.path.join(template_dir, template)
            try:
                if os.path.exists(template_path):
                    with open(template_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if len(content) > 100:  # 最低限のコンテンツ
                            self.log_test(f"テンプレート{template}", True, f"{len(content)}文字")
                        else:
                            self.log_test(f"テンプレート{template}", False, "コンテンツ不足")
                else:
                    self.log_test(f"テンプレート{template}", False, "ファイル未存在")
            except Exception as e:
                self.log_test(f"テンプレート{template}", False, str(e))
    
    def test_critical_functions(self):
        """重要関数の存在確認（app.py）"""
        try:
            app_path = os.path.join(self.base_path, 'app.py')
            with open(app_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
            
            critical_functions = ['index', 'exam', 'result', 'start_exam']
            
            for func in critical_functions:
                if func in functions:
                    self.log_test(f"関数{func}存在確認", True)
                else:
                    self.log_test(f"関数{func}存在確認", False, "関数未発見")
                    
        except Exception as e:
            self.log_test("関数存在確認", False, str(e))
    
    def test_production_response_content(self):
        """本番レスポンス内容テスト"""
        try:
            # HTMLレスポンスの取得
            result = subprocess.run([
                'curl', '-s', '--max-time', '30', self.production_url
            ], capture_output=True, text=True, timeout=35)
            
            html_content = result.stdout
            
            # 重要なHTMLエレメントの確認
            required_elements = ['<title>', '<form', '<button', 'RCCM']
            found_elements = []
            
            for element in required_elements:
                if element in html_content:
                    found_elements.append(element)
            
            if len(found_elements) >= 3:
                self.log_test("本番HTMLコンテンツ", True, f"要素{len(found_elements)}/4発見")
            else:
                self.log_test("本番HTMLコンテンツ", False, f"要素不足: {found_elements}")
                
        except Exception as e:
            self.log_test("本番HTMLコンテンツ", False, str(e))
    
    def test_session_functionality(self):
        """セッション機能テスト（Cookieベース）"""
        try:
            # Cookieファイルを使用したセッションテスト
            cookie_file = '/tmp/test_cookies.txt'
            
            # 1. ホームページアクセス（セッション開始）
            result1 = subprocess.run([
                'curl', '-s', '-c', cookie_file, '--max-time', '30',
                self.production_url
            ], capture_output=True, text=True, timeout=35)
            
            # 2. Cookieを使用して試験開始
            result2 = subprocess.run([
                'curl', '-s', '-b', cookie_file, '-w', '%{http_code}', '-o', '/dev/null',
                '-X', 'POST', '-d', 'questions=5&year=2024',
                '--max-time', '30', f"{self.production_url}/start_exam/基礎科目"
            ], capture_output=True, text=True, timeout=35)
            
            if os.path.exists(cookie_file):
                os.remove(cookie_file)  # クリーンアップ
            
            status_code = int(result2.stdout.strip())
            if status_code in [200, 302]:
                self.log_test("セッション機能", True, f"Cookie保持成功 HTTP {status_code}")
            else:
                self.log_test("セッション機能", False, f"HTTP {status_code}")
                
        except Exception as e:
            self.log_test("セッション機能", False, str(e))
    
    def run_all_tests(self):
        """全テスト実行"""
        print("🚀 本番環境準拠 RCCM アプリケーション検証テスト開始")
        print("=" * 60)
        print(f"テスト対象: {self.production_url}")
        print(f"ローカルパス: {self.base_path}")
        print("=" * 60)
        
        # テスト実行
        self.test_syntax_validation()
        self.test_data_file_integrity() 
        self.test_critical_templates()
        self.test_critical_functions()
        self.test_production_server_status()
        self.test_production_endpoints()
        self.test_production_response_content()
        self.test_session_functionality()
        
        # 結果サマリー
        print("\n" + "=" * 60)
        print("📊 テスト結果サマリー")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        successful_tests = sum(1 for r in self.test_results if r['success'])
        failure_rate = (total_tests - successful_tests) / total_tests * 100
        
        print(f"総テスト数: {total_tests}")
        print(f"成功: {successful_tests}")
        print(f"失敗: {total_tests - successful_tests}")
        print(f"成功率: {successful_tests/total_tests*100:.1f}%")
        
        # 失敗したテストの詳細
        if successful_tests < total_tests:
            print("\n❌ 失敗したテスト:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   • {result['test_name']}: {result['details']}")
        
        # 結果保存
        result_file = 'production_test_results.json'
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'summary': {
                    'total': total_tests,
                    'successful': successful_tests,
                    'failed': total_tests - successful_tests,
                    'success_rate': successful_tests/total_tests*100
                },
                'results': self.test_results
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\n📋 詳細結果: {result_file}")
        
        # 結論
        if successful_tests == total_tests:
            print("\n🎉 全テスト成功！アプリケーションは本番環境で正常動作しています。")
            return True
        elif successful_tests >= total_tests * 0.8:
            print(f"\n⚠️  80%以上成功。軽微な問題があります。")
            return False
        else:
            print(f"\n🚨 重大な問題が検出されました。本番環境での動作に問題があります。")
            return False

def main():
    tester = ProductionEquivalentTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()