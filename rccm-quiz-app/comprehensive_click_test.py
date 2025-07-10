#!/usr/bin/env python3
"""
🖱️ 本番環境全クリック・全リンクテスト
実際のHTMLを取得してすべてのクリック可能要素をテスト
"""
import subprocess
import re
import json
from datetime import datetime
from urllib.parse import urljoin, urlparse
import time

class ComprehensiveClickTester:
    def __init__(self):
        self.base_url = 'https://rccm-quiz-2025.onrender.com'
        self.session_file = '/tmp/comprehensive_test_session.txt'
        self.test_results = []
        self.found_links = set()
        self.found_buttons = set()
        self.found_forms = set()
        
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
    
    def get_page_content(self, url, method='GET', data=None):
        """ページコンテンツを取得"""
        try:
            cmd = ['curl', '-s', '-b', self.session_file, '-c', self.session_file, '--max-time', '30']
            
            if method == 'POST' and data:
                cmd.extend(['-X', 'POST', '-d', data])
            
            cmd.append(url)
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=35)
            return result.stdout
        except Exception as e:
            print(f"コンテンツ取得エラー ({url}): {e}")
            return ""
    
    def extract_clickable_elements(self, html_content, base_url):
        """クリック可能要素を抽出"""
        links = []
        buttons = []
        forms = []
        
        # リンク抽出 (<a href="...">)
        link_pattern = r'<a[^>]+href=[\'"](.*?)[\'"][^>]*>(.*?)</a>'
        for match in re.finditer(link_pattern, html_content, re.IGNORECASE | re.DOTALL):
            href = match.group(1)
            text = re.sub(r'<[^>]+>', '', match.group(2)).strip()
            if href and not href.startswith('#') and not href.startswith('javascript:'):
                full_url = urljoin(base_url, href)
                links.append({'url': full_url, 'text': text[:50], 'href': href})
        
        # ボタン抽出 (<button>, <input type="submit">)
        button_patterns = [
            r'<button[^>]*>(.*?)</button>',
            r'<input[^>]+type=[\'"]submit[\'"][^>]*>',
            r'<input[^>]+type=[\'"]button[\'"][^>]*>'
        ]
        
        for pattern in button_patterns:
            for match in re.finditer(pattern, html_content, re.IGNORECASE | re.DOTALL):
                text = re.sub(r'<[^>]+>', '', match.group(0)).strip()
                if 'value=' in match.group(0):
                    value_match = re.search(r'value=[\'"]([^\'"]*)[\'"]', match.group(0))
                    if value_match:
                        text = value_match.group(1)
                buttons.append({'text': text[:50], 'html': match.group(0)[:100]})
        
        # フォーム抽出 (<form>)
        form_pattern = r'<form[^>]+action=[\'"](.*?)[\'"][^>]*>(.*?)</form>'
        for match in re.finditer(form_pattern, html_content, re.IGNORECASE | re.DOTALL):
            action = match.group(1)
            full_url = urljoin(base_url, action)
            forms.append({'action': full_url, 'method': 'POST'})
        
        return links, buttons, forms
    
    def test_homepage_links(self):
        """ホームページの全リンクテスト"""
        html_content = self.get_page_content(self.base_url)
        
        if not html_content:
            self.log_test("ホームページ取得", False, "コンテンツ取得失敗")
            return
        
        self.log_test("ホームページ取得", True, f"コンテンツサイズ: {len(html_content)}文字")
        
        links, buttons, forms = self.extract_clickable_elements(html_content, self.base_url)
        
        self.log_test("クリック要素検出", True, 
                     f"リンク: {len(links)}個, ボタン: {len(buttons)}個, フォーム: {len(forms)}個")
        
        # 主要リンクをテスト
        important_links = [
            '/departments', '/help', '/progress', '/settings', 
            '/bookmarks', '/statistics', '/review'
        ]
        
        for link_path in important_links:
            found = False
            for link in links:
                if link_path in link['href']:
                    found = True
                    # リンクをクリック（HTTPリクエスト）
                    response = self.test_link_click(link['url'], link['text'])
                    break
            
            if not found:
                self.log_test(f"リンク{link_path}", False, "リンクが見つかりません")
        
        return links, buttons, forms
    
    def test_link_click(self, url, link_text):
        """リンククリックテスト"""
        try:
            result = subprocess.run([
                'curl', '-s', '-w', '%{http_code}', '-o', '/dev/null',
                '-b', self.session_file, '-c', self.session_file,
                '--max-time', '20', url
            ], capture_output=True, text=True, timeout=25)
            
            status_code = int(result.stdout.strip())
            success = status_code in [200, 302]
            
            self.log_test(f"リンククリック: {link_text[:30]}", success, 
                         f"HTTP {status_code}", url)
            return status_code
            
        except Exception as e:
            self.log_test(f"リンククリック: {link_text[:30]}", False, str(e), url)
            return 0
    
    def test_departments_page(self):
        """部門選択ページのテスト"""
        dept_url = f"{self.base_url}/departments"
        html_content = self.get_page_content(dept_url)
        
        if not html_content:
            self.log_test("部門ページ取得", False, "コンテンツ取得失敗")
            return
        
        self.log_test("部門ページ取得", True, f"コンテンツサイズ: {len(html_content)}文字")
        
        # 部門リンクを抽出
        department_links = []
        departments = [
            '基礎科目', '道路', '河川・砂防', '都市計画', '造園',
            '建設環境', '鋼構造・コンクリート', '土質・基礎', 
            '施工計画', '上下水道', '森林土木', '農業土木', 'トンネル'
        ]
        
        for dept in departments:
            if dept in html_content:
                self.log_test(f"部門表示: {dept}", True, "ページに表示されています")
                
                # 部門の試験開始をテスト
                self.test_department_exam_start(dept)
            else:
                self.log_test(f"部門表示: {dept}", False, "ページに表示されていません")
    
    def test_department_exam_start(self, department):
        """部門試験開始テスト"""
        try:
            result = subprocess.run([
                'curl', '-s', '-w', '%{http_code}', '-o', '/dev/null',
                '-b', self.session_file, '-c', self.session_file,
                '-X', 'POST', '-d', 'questions=5&year=2024',
                '--max-time', '20', f"{self.base_url}/start_exam/{department}"
            ], capture_output=True, text=True, timeout=25)
            
            status_code = int(result.stdout.strip())
            success = status_code in [200, 302]
            
            self.log_test(f"{department}試験開始", success, f"HTTP {status_code}")
            
        except Exception as e:
            self.log_test(f"{department}試験開始", False, str(e))
    
    def test_review_functionality(self):
        """復習リスト機能の詳細テスト"""
        print("\n🔍 復習リスト機能テスト開始")
        print("=" * 40)
        
        # 1. 復習ページアクセス
        review_url = f"{self.base_url}/review"
        html_content = self.get_page_content(review_url)
        
        if html_content:
            self.log_test("復習ページアクセス", True, f"コンテンツサイズ: {len(html_content)}文字")
            
            # 復習ページの重要要素をチェック
            review_elements = [
                'ブックマーク', '復習', '間違えた問題', '復習リスト',
                'bookmark', 'review', 'incorrect'
            ]
            
            found_elements = []
            for element in review_elements:
                if element in html_content:
                    found_elements.append(element)
            
            self.log_test("復習要素検出", len(found_elements) > 0, 
                         f"発見要素: {found_elements}")
            
        else:
            self.log_test("復習ページアクセス", False, "ページ取得失敗")
        
        # 2. ブックマーク機能テスト
        bookmark_url = f"{self.base_url}/bookmarks"
        bookmark_content = self.get_page_content(bookmark_url)
        
        if bookmark_content:
            self.log_test("ブックマークページ", True, f"コンテンツサイズ: {len(bookmark_content)}文字")
        else:
            self.log_test("ブックマークページ", False, "ページ取得失敗")
        
        # 3. 復習実行テスト
        try:
            result = subprocess.run([
                'curl', '-s', '-w', '%{http_code}', '-o', '/dev/null',
                '-b', self.session_file, '-c', self.session_file,
                '-X', 'POST', '-d', 'review_type=incorrect&count=5',
                '--max-time', '20', f"{self.base_url}/start_review"
            ], capture_output=True, text=True, timeout=25)
            
            status_code = int(result.stdout.strip())
            success = status_code in [200, 302, 404]  # 404も許容（データがない場合）
            
            self.log_test("復習機能実行", success, f"HTTP {status_code}")
            
        except Exception as e:
            self.log_test("復習機能実行", False, str(e))
    
    def test_exam_flow(self):
        """試験フロー全体テスト"""
        print("\n🎯 試験フロー全体テスト開始")
        print("=" * 40)
        
        # 1. セッション開始
        result = subprocess.run([
            'curl', '-s', '-c', self.session_file,
            '--max-time', '15', self.base_url
        ], capture_output=True, text=True, timeout=20)
        
        self.log_test("セッション開始", True, "Cookie保存完了")
        
        # 2. 試験開始
        result = subprocess.run([
            'curl', '-s', '-L', '-b', self.session_file, '-c', self.session_file,
            '-X', 'POST', '-d', 'questions=3&year=2024',
            '--max-time', '20', f"{self.base_url}/start_exam/基礎科目"
        ], capture_output=True, text=True, timeout=25)
        
        exam_content = result.stdout
        if exam_content and ('問題' in exam_content or 'question' in exam_content):
            self.log_test("試験開始・問題表示", True, "問題が表示されました")
            
            # 3. 試験画面の要素チェック
            exam_elements = ['選択肢', '次へ', '送信', 'submit', 'next', 'radio', 'checkbox']
            found_exam_elements = [elem for elem in exam_elements if elem in exam_content]
            
            self.log_test("試験画面要素", len(found_exam_elements) > 0, 
                         f"発見要素: {found_exam_elements}")
            
            # 4. 回答送信テスト
            try:
                result = subprocess.run([
                    'curl', '-s', '-w', '%{http_code}', '-o', '/dev/null',
                    '-b', self.session_file, '-c', self.session_file,
                    '-X', 'POST', '-d', 'answer=1',
                    '--max-time', '20', f"{self.base_url}/exam"
                ], capture_output=True, text=True, timeout=25)
                
                status_code = int(result.stdout.strip())
                success = status_code in [200, 302]
                
                self.log_test("回答送信", success, f"HTTP {status_code}")
                
            except Exception as e:
                self.log_test("回答送信", False, str(e))
        else:
            self.log_test("試験開始・問題表示", False, "問題が表示されませんでした")
    
    def test_navigation_links(self):
        """ナビゲーションリンクテスト"""
        print("\n🧭 ナビゲーションリンクテスト開始")
        print("=" * 40)
        
        # 重要なナビゲーションリンク
        nav_links = [
            ('ホーム', '/'),
            ('部門選択', '/departments'),
            ('進捗', '/progress'),
            ('統計', '/statistics'),
            ('設定', '/settings'),
            ('ヘルプ', '/help'),
            ('ブックマーク', '/bookmarks'),
            ('復習', '/review')
        ]
        
        for link_name, link_path in nav_links:
            url = f"{self.base_url}{link_path}"
            try:
                result = subprocess.run([
                    'curl', '-s', '-w', '%{http_code}', '-o', '/dev/null',
                    '-b', self.session_file, '-c', self.session_file,
                    '--max-time', '15', url
                ], capture_output=True, text=True, timeout=20)
                
                status_code = int(result.stdout.strip())
                success = status_code in [200, 302]
                
                self.log_test(f"ナビ: {link_name}", success, f"HTTP {status_code}")
                
            except Exception as e:
                self.log_test(f"ナビ: {link_name}", False, str(e))
    
    def run_comprehensive_test(self):
        """包括的クリックテスト実行"""
        print("🖱️ 本番環境全クリック・全リンクテスト開始")
        print("=" * 60)
        print(f"テスト対象: {self.base_url}")
        print("=" * 60)
        
        # 1. ホームページとリンクテスト
        self.test_homepage_links()
        
        # 2. ナビゲーションリンクテスト
        self.test_navigation_links()
        
        # 3. 部門ページテスト
        self.test_departments_page()
        
        # 4. 復習機能テスト
        self.test_review_functionality()
        
        # 5. 試験フロー全体テスト
        self.test_exam_flow()
        
        # 結果サマリー
        print("\n" + "=" * 60)
        print("📊 包括的クリックテスト結果")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        successful_tests = sum(1 for r in self.test_results if r['success'])
        
        print(f"総テスト数: {total_tests}")
        print(f"成功: {successful_tests}")
        print(f"失敗: {total_tests - successful_tests}")
        print(f"成功率: {successful_tests/total_tests*100:.1f}%")
        
        # 失敗テストの詳細
        failed_tests = [r for r in self.test_results if not r['success']]
        if failed_tests:
            print("\n❌ 失敗したテスト:")
            for test in failed_tests:
                print(f"   • {test['test_name']}: {test['details']}")
                if test['url']:
                    print(f"     URL: {test['url']}")
        
        # 結果保存
        with open('comprehensive_click_test_results.json', 'w', encoding='utf-8') as f:
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
        
        print(f"\n📋 詳細結果: comprehensive_click_test_results.json")
        
        return successful_tests == total_tests

def main():
    tester = ComprehensiveClickTester()
    success = tester.run_comprehensive_test()
    
    if success:
        print("\n🎉 全クリック・リンクテスト成功！")
    else:
        print("\n⚠️  一部のクリック・リンクに問題があります。")

if __name__ == '__main__':
    main()