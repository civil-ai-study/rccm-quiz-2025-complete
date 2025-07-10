#!/usr/bin/env python3
"""
🔍 詳細な試験フロー調査
なぜ試験開始リクエストが実際の試験画面に遷移しないのかを調査
"""
import subprocess
import json
import time
from datetime import datetime
import re

class DetailedExamFlowInvestigator:
    def __init__(self):
        self.base_url = 'https://rccm-quiz-2025.onrender.com'
        self.session_file = '/tmp/exam_flow_investigation.txt'
        self.results = []
        
    def log_investigation(self, step_name, success, details="", content_preview=""):
        """調査結果をログ"""
        result = {
            'step': step_name,
            'success': success,
            'details': details,
            'content_preview': content_preview[:500] if content_preview else "",
            'timestamp': datetime.now().isoformat()
        }
        self.results.append(result)
        status = '✅' if success else '❌'
        print(f"{status} {step_name}")
        if details:
            print(f"   詳細: {details}")
    
    def investigate_homepage_structure(self):
        """ホームページ構造の調査"""
        print("\n🏠 ホームページ構造調査")
        print("=" * 40)
        
        try:
            result = subprocess.run([
                'curl', '-s', '--max-time', '15', self.base_url
            ], capture_output=True, text=True, timeout=20)
            
            content = result.stdout
            
            if not content:
                self.log_investigation("ホームページ取得", False, "コンテンツが空")
                return False
            
            # フォーム構造の分析
            forms = re.findall(r'<form[^>]*>.*?</form>', content, re.DOTALL | re.IGNORECASE)
            
            # 部門選択要素の確認
            department_elements = []
            departments = ['基礎科目', '道路', '河川・砂防', '都市計画', '造園']
            for dept in departments:
                if dept in content:
                    department_elements.append(dept)
            
            # 試験開始関連のリンク・ボタンを探す
            start_exam_patterns = [
                r'start_exam',
                r'試験開始',
                r'開始',
                r'受験'
            ]
            
            found_patterns = []
            for pattern in start_exam_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    found_patterns.append(pattern)
            
            details = f"フォーム数: {len(forms)}, 部門要素: {len(department_elements)}, 開始パターン: {found_patterns}"
            
            self.log_investigation("ホームページ構造分析", True, details, content[:500])
            
            return {
                'forms': len(forms),
                'departments': department_elements,
                'start_patterns': found_patterns,
                'content': content
            }
            
        except Exception as e:
            self.log_investigation("ホームページ構造分析", False, f"エラー: {str(e)}")
            return None
    
    def investigate_departments_page(self):
        """部門ページの調査"""
        print("\n📂 部門ページ調査")
        print("=" * 30)
        
        try:
            result = subprocess.run([
                'curl', '-s', '--max-time', '15', f"{self.base_url}/departments"
            ], capture_output=True, text=True, timeout=20)
            
            content = result.stdout
            
            if not content:
                self.log_investigation("部門ページ取得", False, "コンテンツが空")
                return None
            
            # 部門リストの確認
            all_departments = [
                '基礎科目', '道路', '河川・砂防', '都市計画', '造園',
                '建設環境', '鋼構造・コンクリート', '土質・基礎', 
                '施工計画', '上下水道', '森林土木', '農業土木', 'トンネル'
            ]
            
            found_departments = []
            for dept in all_departments:
                if dept in content:
                    found_departments.append(dept)
            
            # フォーム構造の分析
            forms = re.findall(r'<form[^>]*action=["\']([^"\']*)["\'][^>]*>', content, re.IGNORECASE)
            
            # 設定オプションの確認
            question_options = re.findall(r'(\d+)問', content)
            year_options = re.findall(r'(20\d{2})年?', content)
            
            details = f"発見部門: {len(found_departments)}/{len(all_departments)}, フォーム: {forms}, 問題数: {question_options}, 年度: {year_options}"
            
            self.log_investigation("部門ページ構造分析", True, details, content[:500])
            
            return {
                'found_departments': found_departments,
                'forms': forms,
                'question_options': question_options,
                'year_options': year_options,
                'content': content
            }
            
        except Exception as e:
            self.log_investigation("部門ページ構造分析", False, f"エラー: {str(e)}")
            return None
    
    def test_exam_start_flow(self, department):
        """特定部門での試験開始フローテスト"""
        print(f"\n🎯 {department}部門 試験開始フローテスト")
        print("=" * 50)
        
        # セッション初期化
        try:
            result = subprocess.run([
                'curl', '-s', '-c', self.session_file, '--max-time', '15', self.base_url
            ], capture_output=True, text=True, timeout=20)
            
            self.log_investigation(f"{department}_セッション初期化", True, "Cookie保存")
            
        except Exception as e:
            self.log_investigation(f"{department}_セッション初期化", False, f"エラー: {str(e)}")
            return None
        
        # 試験開始リクエストの詳細テスト
        test_configs = [
            {'questions': 10, 'year': 2024},
            {'questions': 5, 'year': 2024},
            {'questions': 15, 'year': 2024}
        ]
        
        for config in test_configs:
            try:
                # 詳細なcurlリクエスト
                result = subprocess.run([
                    'curl', '-s', '-v', '-L',  # -v for verbose, -L for follow redirects
                    '-b', self.session_file, '-c', self.session_file,
                    '-X', 'POST', 
                    '-d', f"questions={config['questions']}&year={config['year']}",
                    '--max-time', '30',
                    f"{self.base_url}/start_exam/{department}"
                ], capture_output=True, text=True, timeout=35)
                
                response_content = result.stdout
                error_output = result.stderr
                
                # レスポンス解析
                is_redirect = 'Location:' in error_output
                has_html = '<html' in response_content.lower()
                has_question = '問題' in response_content or 'question' in response_content.lower()
                has_form = '<form' in response_content.lower()
                content_length = len(response_content)
                
                analysis = {
                    'is_redirect': is_redirect,
                    'has_html': has_html,
                    'has_question': has_question,
                    'has_form': has_form,
                    'content_length': content_length
                }
                
                success = has_html and content_length > 5000
                
                details = f"{config['questions']}問: リダイレクト:{is_redirect}, HTML:{has_html}, 問題:{has_question}, フォーム:{has_form}, サイズ:{content_length}"
                
                self.log_investigation(f"{department}_試験開始_{config['questions']}問", 
                                     success, details, response_content[:300])
                
                # 詳細なレスポンス分析
                if response_content:
                    self.analyze_response_content(response_content, department, config)
                
                time.sleep(1)
                
            except Exception as e:
                self.log_investigation(f"{department}_試験開始_{config['questions']}問", 
                                     False, f"エラー: {str(e)}")
    
    def analyze_response_content(self, content, department, config):
        """レスポンス内容の詳細分析"""
        
        # タイトルの確認
        title_match = re.search(r'<title[^>]*>(.*?)</title>', content, re.IGNORECASE | re.DOTALL)
        title = title_match.group(1).strip() if title_match else "タイトルなし"
        
        # エラーメッセージの確認
        error_patterns = [
            r'エラー', r'error', r'問題が発生', r'利用できません',
            r'not found', r'404', r'500', r'invalid'
        ]
        
        found_errors = []
        for pattern in error_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                found_errors.append(pattern)
        
        # 問題データの確認
        question_elements = [
            '選択肢', '回答', 'radio', 'checkbox', 'input', 'button'
        ]
        
        found_question_elements = []
        for element in question_elements:
            if element in content.lower():
                found_question_elements.append(element)
        
        analysis_result = {
            'title': title,
            'errors': found_errors,
            'question_elements': found_question_elements,
            'department': department,
            'config': config
        }
        
        details = f"タイトル: {title[:50]}, エラー: {found_errors}, 問題要素: {found_question_elements}"
        
        self.log_investigation(f"レスポンス詳細分析_{department}_{config['questions']}問", 
                              len(found_errors) == 0, details)
        
        return analysis_result
    
    def investigate_available_departments(self):
        """利用可能な部門の特定"""
        print("\n🔍 利用可能部門の特定")
        print("=" * 40)
        
        all_departments = [
            '基礎科目', '道路', '河川・砂防', '都市計画', '造園',
            '建設環境', '鋼構造・コンクリート', '土質・基礎', 
            '施工計画', '上下水道', '森林土木', '農業土木', 'トンネル'
        ]
        
        available_departments = []
        
        for department in all_departments:
            print(f"\n📋 {department}部門テスト")
            self.test_exam_start_flow(department)
            
            # 最新の結果を確認
            latest_results = [r for r in self.results if department in r['step'] and '試験開始' in r['step']]
            if latest_results and any(r['success'] for r in latest_results):
                available_departments.append(department)
                print(f"✅ {department}: 利用可能")
            else:
                print(f"❌ {department}: 利用不可")
            
            time.sleep(2)  # サーバー負荷軽減
        
        self.log_investigation("利用可能部門特定", True, 
                              f"利用可能: {available_departments} ({len(available_departments)}/{len(all_departments)})")
        
        return available_departments
    
    def run_detailed_investigation(self):
        """詳細調査の実行"""
        print("🔍 詳細な試験フロー調査開始")
        print("=" * 60)
        print(f"調査対象: {self.base_url}")
        print("=" * 60)
        
        # 1. ホームページ構造調査
        homepage_info = self.investigate_homepage_structure()
        
        # 2. 部門ページ調査
        departments_info = self.investigate_departments_page()
        
        # 3. 利用可能部門の特定
        available_departments = self.investigate_available_departments()
        
        # 結果サマリー
        print("\n" + "=" * 60)
        print("📊 詳細調査結果サマリー")
        print("=" * 60)
        
        total_steps = len(self.results)
        successful_steps = sum(1 for r in self.results if r['success'])
        
        print(f"総調査ステップ: {total_steps}")
        print(f"成功: {successful_steps}")
        print(f"失敗: {total_steps - successful_steps}")
        print(f"成功率: {successful_steps/total_steps*100:.1f}%")
        
        # 重要な発見
        print(f"\n🎯 重要な発見:")
        print(f"├── 利用可能部門: {len(available_departments)}/13部門")
        print(f"├── 利用可能部門リスト: {available_departments}")
        
        # 失敗した調査の詳細
        failed_investigations = [r for r in self.results if not r['success']]
        if failed_investigations:
            print(f"\n❌ 問題が検出された調査 ({len(failed_investigations)}件):")
            for investigation in failed_investigations[:10]:  # 最大10件表示
                print(f"   • {investigation['step']}")
                print(f"     詳細: {investigation['details']}")
        
        # 結果保存
        with open('detailed_exam_flow_investigation_results.json', 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'summary': {
                    'total_steps': total_steps,
                    'successful_steps': successful_steps,
                    'failed_steps': total_steps - successful_steps,
                    'success_rate': successful_steps/total_steps*100
                },
                'findings': {
                    'available_departments': available_departments,
                    'total_departments': 13,
                    'availability_rate': len(available_departments)/13*100
                },
                'investigation_results': self.results
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\n📋 詳細結果: detailed_exam_flow_investigation_results.json")
        
        return available_departments

def main():
    investigator = DetailedExamFlowInvestigator()
    available_departments = investigator.run_detailed_investigation()
    
    print(f"\n📈 調査完了: {len(available_departments)}部門が利用可能です")
    return available_departments

if __name__ == '__main__':
    main()