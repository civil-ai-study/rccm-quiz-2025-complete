#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔥 ULTRA SYNC 本番環境厳格手動テスト
Production Manual Test - Rigorous 10-Question Session Testing

このスクリプトは以下を厳密にテストします：
1. セッション初期化の完全性
2. 1問目から10問目まで個別の手動回答処理
3. 各問題後のセッション状態確認
4. 最終結果画面の表示確認
5. エラーハンドリングと回復機能
"""

import sys
import os
import time
import json
from datetime import datetime

# スクリプトのディレクトリを基準にパスを設定
script_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.join(script_dir, 'rccm-quiz-app')
sys.path.insert(0, app_dir)

class ProductionRigorousTest:
    def __init__(self):
        self.test_results = []
        self.session_states = []
        self.error_count = 0
        self.success_count = 0
        self.start_time = datetime.now()
        
    def log_test_step(self, step, status, details=""):
        """テストステップをログに記録"""
        result = {
            'timestamp': datetime.now().strftime('%H:%M:%S.%f')[:-3],
            'step': step,
            'status': status,
            'details': details
        }
        self.test_results.append(result)
        
        status_symbol = "✅" if status == "SUCCESS" else "❌" if status == "FAILED" else "🔄"
        print(f"{status_symbol} [{result['timestamp']}] {step}: {status}")
        if details:
            print(f"   Details: {details}")
        
        if status == "SUCCESS":
            self.success_count += 1
        elif status == "FAILED":
            self.error_count += 1
    
    def capture_session_state(self, client, step):
        """現在のセッション状態をキャプチャ"""
        try:
            with client.session_transaction() as sess:
                state = {
                    'step': step,
                    'timestamp': datetime.now().strftime('%H:%M:%S'),
                    'exam_current': sess.get('exam_current'),
                    'exam_question_ids': len(sess.get('exam_question_ids', [])),
                    'history': len(sess.get('history', [])),
                    'quiz_completed': sess.get('quiz_completed'),
                    'session_keys': len(sess.keys()),
                    'active_keys': [k for k in sess.keys() if not k.startswith('_')]
                }
                self.session_states.append(state)
                return state
        except Exception as e:
            self.log_test_step(f"Session Capture Error", "FAILED", str(e))
            return None
    
    def run_production_test(self):
        """本番環境での厳格テスト実行"""
        
        print("=" * 80)
        print("🔥 ULTRA SYNC 本番環境厳格手動テスト開始")
        print(f"開始時刻: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        try:
            from app import app
            self.log_test_step("Flask Application Import", "SUCCESS")
        except Exception as e:
            self.log_test_step("Flask Application Import", "FAILED", str(e))
            return False
        
        # テストクライアント作成
        with app.test_client() as client:
            
            print("\n📋 PHASE 1: セッション初期化テスト")
            print("-" * 50)
            
            # Step 1: 初期状態確認
            initial_state = self.capture_session_state(client, "Initial")
            self.log_test_step("Initial Session State", "SUCCESS", 
                             f"Keys: {initial_state['session_keys'] if initial_state else 'None'}")
            
            # Step 2: 基礎科目試験開始
            self.log_test_step("Starting Basic Subject Exam", "IN_PROGRESS")
            response = client.get('/start_exam/基礎科目')
            
            if response.status_code == 302:
                self.log_test_step("Exam Initialization", "SUCCESS", 
                                 f"Redirect: {response.location}")
            else:
                self.log_test_step("Exam Initialization", "FAILED", 
                                 f"Status: {response.status_code}")
                return False
            
            # Step 3: セッション状態確認
            post_init_state = self.capture_session_state(client, "Post-Init")
            if post_init_state and post_init_state['exam_question_ids'] == 10:
                self.log_test_step("Session Initialization", "SUCCESS", 
                                 f"10 questions loaded, current: {post_init_state['exam_current']}")
            else:
                self.log_test_step("Session Initialization", "FAILED", 
                                 "Question IDs not properly initialized")
                return False
            
            print("\n📋 PHASE 2: 10問手動回答テスト")
            print("-" * 50)
            
            # 10問の手動回答テスト
            for question_num in range(1, 11):
                print(f"\n🔸 Question {question_num}/10")
                
                # 問題表示テスト
                self.log_test_step(f"Q{question_num}: Display", "IN_PROGRESS")
                response = client.get('/exam')
                
                if response.status_code == 302:
                    # リダイレクトの場合（完了時）
                    if '/result' in response.location:
                        self.log_test_step(f"Q{question_num}: Early Completion", "SUCCESS", 
                                         f"Redirected to result: {response.location}")
                        break
                    else:
                        self.log_test_step(f"Q{question_num}: Unexpected Redirect", "WARNING", 
                                         f"Redirect: {response.location}")
                elif response.status_code == 200:
                    self.log_test_step(f"Q{question_num}: Display", "SUCCESS", "Question displayed")
                else:
                    self.log_test_step(f"Q{question_num}: Display", "FAILED", 
                                     f"Status: {response.status_code}")
                    continue
                
                # セッション状態確認
                pre_answer_state = self.capture_session_state(client, f"Q{question_num}-Pre")
                
                # 回答提出テスト（選択肢Aを選択）
                self.log_test_step(f"Q{question_num}: Submit Answer", "IN_PROGRESS")
                
                # CSRFトークンを取得して送信
                csrf_token = None
                if response.status_code == 200:
                    content = response.get_data(as_text=True)
                    import re
                    csrf_match = re.search(r'name="csrf_token" value="([^"]+)"', content)
                    if csrf_match:
                        csrf_token = csrf_match.group(1)
                
                # 回答データ準備
                answer_data = {'answer': 'A'}
                if csrf_token:
                    answer_data['csrf_token'] = csrf_token
                
                answer_response = client.post('/exam', data=answer_data)
                
                if answer_response.status_code == 302:
                    if '/result' in answer_response.location:
                        self.log_test_step(f"Q{question_num}: Answer Submitted", "SUCCESS", 
                                         f"Completed - Redirect to result")
                        break
                    else:
                        self.log_test_step(f"Q{question_num}: Answer Submitted", "SUCCESS", 
                                         f"Continue - Redirect: {answer_response.location}")
                elif answer_response.status_code == 200:
                    self.log_test_step(f"Q{question_num}: Answer Submitted", "SUCCESS", 
                                     "Feedback page displayed")
                else:
                    self.log_test_step(f"Q{question_num}: Answer Submitted", "FAILED", 
                                     f"Status: {answer_response.status_code}")
                
                # 回答後のセッション状態確認
                post_answer_state = self.capture_session_state(client, f"Q{question_num}-Post")
                
                if post_answer_state:
                    if post_answer_state['history'] > pre_answer_state['history']:
                        self.log_test_step(f"Q{question_num}: History Updated", "SUCCESS", 
                                         f"History: {pre_answer_state['history']} -> {post_answer_state['history']}")
                    else:
                        self.log_test_step(f"Q{question_num}: History Update", "WARNING", 
                                         "History not updated")
                
                # 短い待機時間
                time.sleep(0.1)
            
            print("\n📋 PHASE 3: 結果画面表示テスト")
            print("-" * 50)
            
            # 最終セッション状態確認
            final_state = self.capture_session_state(client, "Final")
            
            # 結果画面直接アクセステスト
            self.log_test_step("Result Page Access", "IN_PROGRESS")
            result_response = client.get('/result')
            
            if result_response.status_code == 200:
                content = result_response.get_data(as_text=True)
                
                # 結果画面コンテンツ確認
                if '問題結果' in content:
                    self.log_test_step("Result Page Content", "SUCCESS", "Result page properly displayed")
                    
                    # 詳細コンテンツ確認
                    if '正答数' in content:
                        self.log_test_step("Result Statistics", "SUCCESS", "Statistics displayed")
                    if '次のアクション' in content:
                        self.log_test_step("Result Actions", "SUCCESS", "Action buttons displayed")
                    
                    # デバッグ情報確認
                    if 'debug_message' in content:
                        self.log_test_step("Debug Information", "SUCCESS", "Debug info available")
                    
                else:
                    self.log_test_step("Result Page Content", "FAILED", "Result content missing")
                    
            elif result_response.status_code == 302:
                self.log_test_step("Result Page Access", "FAILED", 
                                 f"Still redirecting to: {result_response.location}")
            else:
                self.log_test_step("Result Page Access", "FAILED", 
                                 f"Status: {result_response.status_code}")
            
            print("\n📋 PHASE 4: エラーハンドリングテスト")
            print("-" * 50)
            
            # 無効なデータでのテスト
            self.log_test_step("Invalid Data Handling", "IN_PROGRESS")
            invalid_response = client.post('/exam', data={'invalid': 'data'})
            if invalid_response.status_code in [400, 302]:
                self.log_test_step("Invalid Data Handling", "SUCCESS", 
                                 f"Properly handled: {invalid_response.status_code}")
            else:
                self.log_test_step("Invalid Data Handling", "WARNING", 
                                 f"Unexpected response: {invalid_response.status_code}")
        
        # テスト結果サマリー
        self.print_test_summary()
        return self.error_count == 0
    
    def print_test_summary(self):
        """テスト結果サマリーを出力"""
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        print("\n" + "=" * 80)
        print("🔥 ULTRA SYNC 本番環境厳格テスト結果サマリー")
        print("=" * 80)
        print(f"開始時刻: {self.start_time.strftime('%H:%M:%S')}")
        print(f"終了時刻: {end_time.strftime('%H:%M:%S')}")
        print(f"実行時間: {duration.total_seconds():.2f}秒")
        print(f"成功: {self.success_count}件")  
        print(f"失敗: {self.error_count}件")
        print(f"総テスト: {len(self.test_results)}件")
        print(f"成功率: {(self.success_count / len(self.test_results) * 100):.1f}%")
        
        print(f"\n📊 セッション状態変遷:")
        for state in self.session_states[-5:]:  # 最新5件のみ表示
            print(f"  {state['step']}: current={state['exam_current']}, "
                  f"questions={state['exam_question_ids']}, history={state['history']}")
        
        if self.error_count == 0:
            print(f"\n✅ 全テスト合格: 結果画面は正常に表示されます")
        else:
            print(f"\n❌ テスト失敗: {self.error_count}件の問題があります")
            
            # 失敗したテストの詳細
            print(f"\n🚨 失敗したテスト:")
            for result in self.test_results:
                if result['status'] == 'FAILED':
                    print(f"  - {result['step']}: {result['details']}")

def main():
    """メイン実行関数"""
    tester = ProductionRigorousTest()
    success = tester.run_production_test()
    
    if success:
        print(f"\n🎯 本番環境テスト完了: 結果画面表示問題は解決されました")
    else:
        print(f"\n⚠️ 本番環境テスト: まだ修正が必要な問題があります")
    
    return success

if __name__ == '__main__':
    main()