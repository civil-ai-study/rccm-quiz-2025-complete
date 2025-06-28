#!/usr/bin/env python3
"""
自動10問回答テスト（連続POSTリクエスト版）

10問を自動で回答して最終問題判定をテストします。
"""

import requests
import json
import time
import re
import sys
from bs4 import BeautifulSoup

class Auto10QuestionTest:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        
    def print_status(self, message):
        """ステータス表示"""
        print(f"[{time.strftime('%H:%M:%S')}] {message}")
        
    def extract_question_info(self, html_content):
        """HTMLから問題情報を抽出"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 問題ID抽出（formのactionまたはhidden input）
            form = soup.find('form')
            if form:
                # hidden inputでqidを探す
                qid_input = form.find('input', {'name': 'qid', 'type': 'hidden'})
                if qid_input:
                    question_id = qid_input.get('value')
                else:
                    # URLパラメータから抽出を試行
                    action = form.get('action', '')
                    qid_match = re.search(r'qid=(\d+)', action)
                    question_id = qid_match.group(1) if qid_match else None
            else:
                question_id = None
            
            # 進捗情報抽出
            progress_text = soup.get_text()
            progress_match = re.search(r'(\d+)\s*/\s*(\d+)', progress_text)
            if progress_match:
                current_num = int(progress_match.group(1))
                total_num = int(progress_match.group(2))
            else:
                current_num = None
                total_num = None
            
            # 問題文抽出
            question_text = None
            question_div = soup.find('div', class_='question-text') or soup.find('div', string=re.compile(r'問題\d+'))
            if question_div:
                question_text = question_div.get_text(strip=True)[:100] + "..."
            
            return {
                'question_id': question_id,
                'current_num': current_num,
                'total_num': total_num,
                'question_text': question_text
            }
            
        except Exception as e:
            self.print_status(f"HTML解析エラー: {e}")
            return {}
    
    def extract_feedback_info(self, html_content):
        """フィードバックページから情報を抽出"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 最終問題判定
            text_content = soup.get_text()
            is_last_question = any(keyword in text_content for keyword in [
                "最終問題です", "お疲れ様でした", "全ての問題が完了", "試験終了",
                "これで全ての問題が", "全問完了"
            ])
            
            # 次の問題ボタンの存在確認
            next_button = soup.find('a', string=re.compile(r'次の問題')) or soup.find('button', string=re.compile(r'次の問題'))
            has_next_button = next_button is not None
            
            # 正解/不正解の判定
            is_correct = "正解" in text_content and "不正解" not in text_content
            
            # 進捗情報
            progress_match = re.search(r'(\d+)\s*/\s*(\d+)', text_content)
            if progress_match:
                current_num = int(progress_match.group(1))
                total_num = int(progress_match.group(2))
            else:
                current_num = None
                total_num = None
            
            return {
                'is_last_question': is_last_question,
                'has_next_button': has_next_button,
                'is_correct': is_correct,
                'current_num': current_num,
                'total_num': total_num
            }
            
        except Exception as e:
            self.print_status(f"フィードバック解析エラー: {e}")
            return {}
    
    def start_quiz_session(self, question_type='basic', session_size=10):
        """クイズセッションを開始"""
        self.print_status(f"セッション開始: {question_type}, {session_size}問")
        
        params = {
            'question_type': question_type,
            'count': session_size
        }
        response = self.session.get(f"{self.base_url}/exam", params=params)
        
        if response.status_code == 200:
            self.print_status("✓ セッション開始成功")
            # 最初の問題情報を抽出
            info = self.extract_question_info(response.text)
            if info.get('question_id'):
                self.print_status(f"  最初の問題ID: {info['question_id']}")
                self.print_status(f"  進捗: {info['current_num']}/{info['total_num']}")
            return response.text
        else:
            self.print_status(f"✗ セッション開始失敗: {response.status_code}")
            return None
    
    def submit_answer(self, question_id, answer='A'):
        """回答を送信"""
        self.print_status(f"問題 {question_id} に回答 '{answer}' を送信中...")
        
        data = {
            'qid': question_id,
            'answer': answer
        }
        response = self.session.post(f"{self.base_url}/exam", data=data)
        
        if response.status_code == 200:
            feedback_info = self.extract_feedback_info(response.text)
            
            self.print_status(f"✓ 回答送信成功")
            self.print_status(f"  正解: {feedback_info.get('is_correct', 'Unknown')}")
            self.print_status(f"  最終問題: {feedback_info.get('is_last_question', False)}")
            self.print_status(f"  次の問題ボタン: {feedback_info.get('has_next_button', False)}")
            
            return feedback_info
        else:
            self.print_status(f"✗ 回答送信失敗: {response.status_code}")
            return None
    
    def get_next_question(self):
        """次の問題を取得"""
        response = self.session.get(f"{self.base_url}/exam", params={'next': '1'})
        
        if response.status_code == 200:
            info = self.extract_question_info(response.text)
            if info.get('question_id'):
                self.print_status(f"次の問題取得成功: ID={info['question_id']}, 進捗={info['current_num']}/{info['total_num']}")
            return info
        else:
            self.print_status(f"✗ 次の問題取得失敗: {response.status_code}")
            return None
    
    def run_auto_10_questions(self):
        """自動10問回答テスト"""
        self.print_status("=== 自動10問回答テスト開始 ===")
        
        # セッション開始
        first_page = self.start_quiz_session('basic', 10)
        if not first_page:
            return False
        
        # 最初の問題情報を抽出
        current_info = self.extract_question_info(first_page)
        if not current_info.get('question_id'):
            self.print_status("✗ 最初の問題ID取得失敗")
            return False
        
        question_count = 0
        max_questions = 10
        
        while question_count < max_questions:
            question_count += 1
            question_id = current_info['question_id']
            current_num = current_info.get('current_num', question_count)
            total_num = current_info.get('total_num', 10)
            
            self.print_status(f"\n--- {question_count}問目 (問題ID: {question_id}, 進捗: {current_num}/{total_num}) ---")
            
            # 回答送信（Aで固定）
            feedback_info = self.submit_answer(question_id, 'A')
            if not feedback_info:
                self.print_status("✗ 回答送信失敗でテスト中断")
                return False
            
            # 最終問題かチェック
            if feedback_info.get('is_last_question', False):
                self.print_status(f"🎯 最終問題検出: {question_count}問目")
                
                # 期待される結果と比較
                if question_count == 10:
                    self.print_status("✓ 正常: 10問目で最終問題と判定されました")
                    
                    # 次の問題ボタンがないことを確認
                    if not feedback_info.get('has_next_button', False):
                        self.print_status("✓ 正常: 次の問題ボタンが表示されていません")
                        return True
                    else:
                        self.print_status("✗ 異常: 最終問題なのに次の問題ボタンがあります")
                        return False
                else:
                    self.print_status(f"✗ 異常: {question_count}問目で最終問題と判定されました（期待: 10問目）")
                    return False
            
            # まだ最終問題でない場合、次の問題を取得
            if question_count < max_questions:
                next_info = self.get_next_question()
                if not next_info or not next_info.get('question_id'):
                    self.print_status("✗ 次の問題取得失敗でテスト中断")
                    return False
                
                current_info = next_info
                time.sleep(0.5)  # レート制限回避
        
        # 10問完了したが最終問題と判定されなかった場合
        self.print_status("✗ 異常: 10問完了したが最終問題と判定されませんでした")
        return False

def main():
    """メイン実行関数"""
    print("自動10問回答テスト")
    print("サーバーがhttp://localhost:5000で起動していることを確認してください。")
    
    tester = Auto10QuestionTest()
    
    try:
        # 接続テスト
        response = tester.session.get(f"{tester.base_url}/debug/session")
        if response.status_code != 200:
            print(f"✗ サーバーに接続できません: {response.status_code}")
            print("app.pyを起動してから再実行してください。")
            sys.exit(1)
        
        print("✓ サーバー接続確認完了")
        
        # セッションクリア
        tester.session.get(f"{tester.base_url}/debug/clear_session")
        time.sleep(1)
        
        # 自動テスト実行
        success = tester.run_auto_10_questions()
        
        if success:
            print("\n🎉 テスト合格: 10問目の最終問題判定が正常に動作しています")
            sys.exit(0)
        else:
            print("\n❌ テスト失敗: 10問目の最終問題判定に問題があります")
            sys.exit(1)
            
    except requests.exceptions.ConnectionError:
        print("✗ サーバーに接続できません。app.pyを起動してから再実行してください。")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n✗ ユーザーによる中断")
        sys.exit(1)
    except Exception as e:
        print(f"✗ 予期しないエラー: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()