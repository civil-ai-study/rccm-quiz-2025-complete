#!/usr/bin/env python3
"""
Detailed Error Analysis Script
Extracts and analyzes the specific error messages causing the navigation issue
"""

import requests
import re
import sys
from bs4 import BeautifulSoup

BASE_URL = "http://172.18.44.152:5003"

class ErrorAnalyzer:
    def __init__(self):
        self.session = requests.Session()
        
    def extract_qid(self, html_content):
        """HTMLから問題IDを抽出"""
        match = re.search(r'name="qid"\s+value="([^"]+)"', html_content)
        return match.group(1) if match else None
        
    def extract_error_elements(self, html_content):
        """エラー要素を詳細に分析"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 様々なエラーパターンを検索
        error_elements = []
        
        # 1. alert-danger クラス
        alerts = soup.find_all(attrs={'class': re.compile(r'alert-danger')})
        for alert in alerts:
            error_elements.append({
                'type': 'alert-danger',
                'text': alert.get_text().strip(),
                'visible': 'd-none' not in str(alert.get('class', [])),
                'html': str(alert)[:200] + '...' if len(str(alert)) > 200 else str(alert)
            })
            
        # 2. text-danger クラス
        text_dangers = soup.find_all(attrs={'class': re.compile(r'text-danger')})
        for td in text_dangers:
            error_elements.append({
                'type': 'text-danger',
                'text': td.get_text().strip(),
                'visible': 'd-none' not in str(td.get('class', [])),
                'html': str(td)[:200] + '...' if len(str(td)) > 200 else str(td)
            })
            
        # 3. error.html テンプレートの可能性
        error_divs = soup.find_all(attrs={'class': re.compile(r'error')})
        for ed in error_divs:
            error_elements.append({
                'type': 'error-div',
                'text': ed.get_text().strip(),
                'visible': 'd-none' not in str(ed.get('class', [])),
                'html': str(ed)[:200] + '...' if len(str(ed)) > 200 else str(ed)
            })
            
        # 4. JavaScript エラー表示
        js_errors = soup.find_all(id=re.compile(r'error'))
        for je in js_errors:
            error_elements.append({
                'type': 'js-error',
                'text': je.get_text().strip(),
                'visible': 'd-none' not in str(je.get('class', [])),
                'html': str(je)[:200] + '...' if len(str(je)) > 200 else str(je)
            })
            
        # 5. "エラー" を含むテキスト
        error_texts = soup.find_all(text=re.compile(r'エラー'))
        for et in error_texts:
            parent = et.parent
            error_elements.append({
                'type': 'error-text',
                'text': et.strip(),
                'visible': True,  # テキストは通常表示される
                'html': str(parent)[:200] + '...' if len(str(parent)) > 200 else str(parent)
            })
            
        return error_elements
        
    def analyze_session_state(self, html_content):
        """セッション状態を分析"""
        # デバッグ情報を抽出
        debug_pattern = r'DEBUG:.*?current_no=([^,]+).*?total=([^,]+).*?type=([^}]+)'
        debug_match = re.search(debug_pattern, html_content)
        
        session_info = {}
        if debug_match:
            session_info = {
                'current_no': debug_match.group(1).strip(),
                'total': debug_match.group(2).strip(),
                'type': debug_match.group(3).strip()
            }
            
        # 問題番号表示を確認
        progress_pattern = r'問題\s+(\d+)/(\d+)'
        progress_match = re.search(progress_pattern, html_content)
        if progress_match:
            session_info['displayed_current'] = progress_match.group(1)
            session_info['displayed_total'] = progress_match.group(2)
            
        return session_info
        
    def run_detailed_analysis(self):
        """詳細な分析を実行"""
        print("🔬 Detailed Error Analysis - RCCM Navigation Bug")
        print("=" * 60)
        
        try:
            # Step 1: ホーム画面
            print("\n📋 Step 1: ホーム画面アクセス")
            response = self.session.get(f"{BASE_URL}/")
            if response.status_code != 200:
                print(f"❌ ホーム画面失敗: {response.status_code}")
                return False
            print(f"✅ ホーム画面成功: {response.status_code}")
            
            # Step 2: 4-1基礎問題開始
            print("\n📋 Step 2: 4-1基礎問題開始")
            response = self.session.get(f"{BASE_URL}/exam?department=road&type=basic")
            if response.status_code != 200:
                print(f"❌ 基礎問題開始失敗: {response.status_code}")
                return False
            print(f"✅ 基礎問題開始成功: {response.status_code}")
            
            # セッション状態分析（問題画面）
            print("\n📊 問題画面のセッション状態:")
            session_info = self.analyze_session_state(response.text)
            for key, value in session_info.items():
                print(f"   {key}: {value}")
                
            # 問題画面のエラーチェック
            question_errors = self.extract_error_elements(response.text)
            if question_errors:
                print(f"\n🚨 問題画面でエラー検出 ({len(question_errors)}件):")
                for i, error in enumerate(question_errors, 1):
                    print(f"   {i}. [{error['type']}] {error['text'][:100]}...")
            else:
                print("\n✅ 問題画面にエラーなし")
            
            # Step 3: 回答送信
            print("\n📋 Step 3: 回答送信と分析")
            qid = self.extract_qid(response.text)
            if not qid:
                print("❌ 問題IDが見つからない")
                return False
                
            print(f"✅ 問題ID: {qid}")
            
            # 回答データ送信
            answer_data = {
                'qid': qid,
                'answer': 'A',  # 正解の可能性があるA
                'elapsed': '15.0'
            }
            
            answer_response = self.session.post(f"{BASE_URL}/exam", data=answer_data)
            print(f"✅ 回答送信結果: {answer_response.status_code}")
            
            # Step 4: フィードバック画面の詳細分析
            print("\n📋 Step 4: フィードバック画面の詳細エラー分析")
            
            # セッション状態分析（フィードバック画面）
            print("\n📊 フィードバック画面のセッション状態:")
            feedback_session_info = self.analyze_session_state(answer_response.text)
            for key, value in feedback_session_info.items():
                print(f"   {key}: {value}")
            
            # 詳細エラー分析
            error_elements = self.extract_error_elements(answer_response.text)
            
            print(f"\n🔍 検出されたエラー要素 ({len(error_elements)}件):")
            visible_errors = []
            hidden_errors = []
            
            for i, error in enumerate(error_elements, 1):
                if error['visible'] and error['text'].strip():
                    visible_errors.append(error)
                    print(f"\n   🚨 可視エラー {len(visible_errors)}:")
                    print(f"      タイプ: {error['type']}")
                    print(f"      テキスト: {error['text']}")
                    print(f"      HTML: {error['html']}")
                else:
                    hidden_errors.append(error)
                    
            print(f"\n📊 エラー要素サマリー:")
            print(f"   可視エラー: {len(visible_errors)}件")
            print(f"   非表示エラー: {len(hidden_errors)}件")
            
            # ナビゲーション状態分析
            print(f"\n📊 ナビゲーション状態分析:")
            has_next = "次の問題へ" in answer_response.text
            has_result = "結果を見る" in answer_response.text
            print(f"   次の問題へボタン: {'✅ 存在' if has_next else '❌ なし'}")
            print(f"   結果を見るボタン: {'✅ 存在' if has_result else '❌ なし'}")
            
            # 正解・不正解の確認
            is_correct_feedback = "正解" in answer_response.text
            is_incorrect_feedback = "不正解" in answer_response.text
            print(f"   正解フィードバック: {'✅ 表示' if is_correct_feedback else '❌ なし'}")
            print(f"   不正解フィードバック: {'✅ 表示' if is_incorrect_feedback else '❌ なし'}")
            
            # Step 5: 問題の特定と推奨対策
            print(f"\n📋 Step 5: 問題診断と対策案")
            
            issues = []
            solutions = []
            
            if visible_errors:
                issues.append(f"可視エラーメッセージが {len(visible_errors)} 件表示されている")
                solutions.append("エラーメッセージの原因を特定し、表示条件を修正する")
                
            if not has_next and not has_result:
                issues.append("ナビゲーションボタンが全く表示されていない")
                solutions.append("is_last_question の計算ロジックを確認する")
                
            if not is_correct_feedback and not is_incorrect_feedback:
                issues.append("正解・不正解のフィードバックが表示されていない")
                solutions.append("フィードバック画面のレンダリングロジックを確認する")
                
            if issues:
                print(f"🚨 特定された問題 ({len(issues)}件):")
                for i, issue in enumerate(issues, 1):
                    print(f"   {i}. {issue}")
                    
                print(f"\n💡 推奨対策 ({len(solutions)}件):")
                for i, solution in enumerate(solutions, 1):
                    print(f"   {i}. {solution}")
            else:
                print("✅ 明確な問題は特定されませんでした")
                
            # 最重要エラーメッセージの特定
            if visible_errors:
                print(f"\n🔥 最重要エラー（ユーザーに表示されているもの）:")
                for error in visible_errors[:3]:  # 上位3つ
                    if "エラー" in error['text'] or len(error['text']) > 5:  # 意味のあるエラーのみ
                        print(f"   ⚠️  {error['text']}")
                        
            return len(visible_errors) == 0
            
        except Exception as e:
            print(f"❌ 分析エラー: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    analyzer = ErrorAnalyzer()
    success = analyzer.run_detailed_analysis()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 エラー分析完了 - 問題なし")
    else:
        print("🚨 エラー分析完了 - 修正必要")
    print("=" * 60)
    
    sys.exit(0 if success else 1)