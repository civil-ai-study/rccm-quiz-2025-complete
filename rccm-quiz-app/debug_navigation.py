#!/usr/bin/env python3
"""
Navigation Bug Debug Script
Tests the exact user flow: Home → 4-1 Basic Questions → Answer → Check Navigation
"""

import requests
import re
import sys
from urllib.parse import urlparse, parse_qs

BASE_URL = "http://172.18.44.152:5003"

class NavigationDebugger:
    def __init__(self):
        self.session = requests.Session()
        
    def extract_csrf_token(self, html_content):
        """HTMLからCSRFトークンを抽出"""
        match = re.search(r'name="csrf_token".*?value="([^"]+)"', html_content)
        return match.group(1) if match else None
        
    def extract_qid(self, html_content):
        """HTMLから問題IDを抽出"""
        match = re.search(r'name="qid"\s+value="([^"]+)"', html_content)
        return match.group(1) if match else None
        
    def check_error_message(self, html_content):
        """エラーメッセージをチェック"""
        # エラー関連のテキストを検索
        error_patterns = [
            r'エラーです',
            r'error',
            r'alert-danger',
            r'class="alert[^"]*alert-danger',
            r'text-danger',
            r'エラー'
        ]
        
        errors_found = []
        for pattern in error_patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            if matches:
                errors_found.extend(matches)
                
        return errors_found
        
    def check_navigation_buttons(self, html_content):
        """ナビゲーションボタンの存在をチェック"""
        next_button = re.search(r'次の問題へ', html_content)
        result_button = re.search(r'結果を見る', html_content)
        
        return {
            'has_next_button': bool(next_button),
            'has_result_button': bool(result_button),
            'next_button_text': next_button.group(0) if next_button else None,
            'result_button_text': result_button.group(0) if result_button else None
        }
        
    def extract_debug_info(self, html_content):
        """デバッグ情報を抽出"""
        debug_pattern = r'is_last_question=([^,]+).*?next_question_index=([^,]+).*?current_question_number=([^,]+).*?total_questions=([^}]+)'
        match = re.search(debug_pattern, html_content)
        
        if match:
            return {
                'is_last_question': match.group(1).strip(),
                'next_question_index': match.group(2).strip(),
                'current_question_number': match.group(3).strip(),
                'total_questions': match.group(4).strip()
            }
        return None
        
    def test_navigation_flow(self):
        """ナビゲーション全体をテスト"""
        print("🔍 RCCM Navigation Bug Debug Test")
        print("=" * 50)
        
        try:
            # Step 1: ホーム画面アクセス
            print("\n📋 Step 1: ホーム画面アクセス")
            response = self.session.get(f"{BASE_URL}/")
            if response.status_code != 200:
                print(f"❌ ホーム画面アクセス失敗: {response.status_code}")
                return False
            print(f"✅ ホーム画面アクセス成功: {response.status_code}")
            
            # Step 2: 4-1基礎問題開始
            print("\n📋 Step 2: 4-1基礎問題開始")
            response = self.session.get(f"{BASE_URL}/exam?department=road&type=basic")
            if response.status_code != 200:
                print(f"❌ 基礎問題開始失敗: {response.status_code}")
                return False
            print(f"✅ 基礎問題開始成功: {response.status_code}")
            
            # 問題内容確認
            if "4-1 基礎科目" not in response.text:
                print("❌ 基礎科目の問題が表示されていない")
                return False
            print("✅ 基礎科目の問題が正しく表示")
            
            # Step 3: 最初の問題に回答
            print("\n📋 Step 3: 最初の問題に回答")
            
            # 問題ID取得（CSRFトークンは使用されていない）
            qid = self.extract_qid(response.text)
            
            if not qid:
                print("❌ 問題IDが見つからない")
                return False
                
            print(f"✅ 問題ID取得: {qid}")
            print("ℹ️  CSRFトークンは使用されていません")
            
            # 回答データ準備（Aを選択）
            answer_data = {
                'qid': qid,
                'answer': 'A',
                'elapsed': '15.0'
            }
            
            # 回答送信
            answer_response = self.session.post(f"{BASE_URL}/exam", data=answer_data)
            print(f"✅ 回答送信: {answer_response.status_code}")
            
            # Step 4: フィードバック画面分析
            print("\n📋 Step 4: フィードバック画面分析")
            
            # エラーメッセージチェック
            errors = self.check_error_message(answer_response.text)
            if errors:
                print(f"🚨 エラーメッセージ検出: {errors}")
            else:
                print("✅ エラーメッセージなし")
            
            # ナビゲーションボタンチェック
            nav_buttons = self.check_navigation_buttons(answer_response.text)
            print(f"📊 ナビゲーションボタン状態:")
            print(f"   次の問題へボタン: {'✅ 存在' if nav_buttons['has_next_button'] else '❌ なし'}")
            print(f"   結果を見るボタン: {'✅ 存在' if nav_buttons['has_result_button'] else '❌ なし'}")
            
            # デバッグ情報抽出
            debug_info = self.extract_debug_info(answer_response.text)
            if debug_info:
                print(f"📊 デバッグ情報:")
                for key, value in debug_info.items():
                    print(f"   {key}: {value}")
            else:
                print("❌ デバッグ情報が見つからない")
                
            # 正解・不正解表示チェック
            if "正解" in answer_response.text:
                print("✅ 正解フィードバック表示")
            elif "不正解" in answer_response.text:
                print("✅ 不正解フィードバック表示")
            else:
                print("❌ 正解・不正解フィードバックが見つからない")
                
            # Step 5: 結果分析
            print("\n📋 Step 5: 問題診断結果")
            
            # 主要な問題を特定
            issues = []
            
            if errors:
                issues.append(f"エラーメッセージが表示されている: {', '.join(errors)}")
                
            if not nav_buttons['has_next_button'] and not nav_buttons['has_result_button']:
                issues.append("ナビゲーションボタンが全く表示されていない")
            elif not nav_buttons['has_next_button']:
                issues.append("「次の問題へ」ボタンが表示されていない")
                
            if debug_info and debug_info.get('is_last_question') == 'True':
                issues.append(f"1問目なのに is_last_question=True になっている")
                
            if issues:
                print("🚨 検出された問題:")
                for i, issue in enumerate(issues, 1):
                    print(f"   {i}. {issue}")
            else:
                print("✅ 明確な問題は検出されませんでした")
                
            # HTMLの一部を出力（デバッグ用）
            print("\n📋 HTMLスニペット（デバッグ用）:")
            
            # ナビゲーション部分を抽出
            nav_section = re.search(r'<div class="main-navigation-section".*?</div>', answer_response.text, re.DOTALL)
            if nav_section:
                print("--- Navigation Section ---")
                print(nav_section.group(0)[:500] + "..." if len(nav_section.group(0)) > 500 else nav_section.group(0))
            
            return len(issues) == 0
            
        except Exception as e:
            print(f"❌ テスト実行エラー: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    debugger = NavigationDebugger()
    success = debugger.test_navigation_flow()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 ナビゲーションテスト合格")
    else:
        print("🚨 ナビゲーションテスト失敗 - 修正が必要")
    print("=" * 50)
    
    sys.exit(0 if success else 1)