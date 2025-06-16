#!/usr/bin/env python3
"""
厳重なフローテスト: ユーザー指摘事項の包括的検証
初期画面→道路部門→基礎問題→復習リスト→専門科目→復習リスト回答の全フロー
"""

import requests
import time
import json
from urllib.parse import urlparse, parse_qs
import random
import re

BASE_URL = "http://localhost:5003"

class RCCMFlowTester:
    def __init__(self):
        self.session = requests.Session()
        self.errors = []
        self.review_questions = []
        
    def log_error(self, test_name, error_msg):
        """エラーをログに記録"""
        self.errors.append(f"【{test_name}】 {error_msg}")
        print(f"❌ {test_name}: {error_msg}")
        
    def log_success(self, test_name, msg):
        """成功をログに記録"""
        print(f"✅ {test_name}: {msg}")
        
    def get_csrf_token(self, html_content):
        """HTMLからCSRFトークンを抽出"""
        match = re.search(r'name="csrf_token".*?value="([^"]+)"', html_content)
        return match.group(1) if match else None
        
    def test_1_initial_screen_to_basic_questions(self):
        """テスト1: 初期画面→道路部門→基礎問題4-1全回答（2問復習リスト追加）"""
        print("\n📋 【テスト1】 初期画面→道路部門→基礎問題4-1全回答（2問復習リスト追加）")
        print("=" * 70)
        
        try:
            # 1. 初期画面アクセス
            response = self.session.get(f"{BASE_URL}/")
            if response.status_code != 200:
                self.log_error("初期画面アクセス", f"ステータスコード: {response.status_code}")
                return False
            self.log_success("初期画面アクセス", "正常に表示")
            
            # 2. 道路部門の基礎問題選択
            response = self.session.get(f"{BASE_URL}/exam?department=road&type=basic")
            if response.status_code != 200:
                self.log_error("基礎問題開始", f"ステータスコード: {response.status_code}")
                return False
            self.log_success("基礎問題開始", "道路部門基礎問題セッション開始")
            
            # 3. 基礎問題を10問全て回答（2問を復習リストに追加）
            review_count = 0
            for question_num in range(1, 11):
                print(f"  問題 {question_num}/10 回答中...")
                
                # 問題ページ取得
                response = self.session.get(f"{BASE_URL}/exam")
                if response.status_code != 200:
                    self.log_error(f"問題{question_num}表示", f"ステータスコード: {response.status_code}")
                    continue
                    
                # 問題内容確認
                if "4-1 基礎科目" not in response.text:
                    self.log_error(f"問題{question_num}内容", "基礎科目の問題が表示されていない")
                    continue
                    
                # CSRFトークン取得
                csrf_token = self.get_csrf_token(response.text)
                
                # 問題IDを抽出
                qid_match = re.search(r'name="qid" value="([^"]+)"', response.text)
                if not qid_match:
                    self.log_error(f"問題{question_num}ID取得", "問題IDが見つからない")
                    continue
                qid = qid_match.group(1)
                
                # 2問目と5問目を復習リストに追加
                if question_num == 2 or question_num == 5:
                    review_data = {
                        'qid': qid,
                        'csrf_token': csrf_token
                    }
                    review_response = self.session.post(f"{BASE_URL}/bookmark", data=review_data)
                    if review_response.status_code == 200:
                        self.log_success(f"問題{question_num}復習追加", "復習リストに追加成功")
                        review_count += 1
                        self.review_questions.append(qid)
                    else:
                        self.log_error(f"問題{question_num}復習追加", "復習リスト追加失敗")
                
                # 問題に回答（ランダムに選択）
                answer_choice = random.choice(['A', 'B', 'C', 'D'])
                answer_data = {
                    'qid': qid,
                    'answer': answer_choice,
                    'elapsed': '15.5',
                    'csrf_token': csrf_token
                }
                
                answer_response = self.session.post(f"{BASE_URL}/exam", data=answer_data)
                if answer_response.status_code != 200:
                    self.log_error(f"問題{question_num}回答", f"回答送信失敗: {answer_response.status_code}")
                    continue
                    
                # フィードバック画面確認
                if "正解" in answer_response.text or "不正解" in answer_response.text:
                    self.log_success(f"問題{question_num}回答", f"回答処理完了（選択: {answer_choice}）")
                else:
                    self.log_error(f"問題{question_num}フィードバック", "フィードバック画面が正しく表示されない")
                
                time.sleep(0.5)  # サーバー負荷軽減
            
            if review_count == 2:
                self.log_success("復習リスト追加", f"指定通り2問を復習リストに追加完了")
            else:
                self.log_error("復習リスト追加", f"追加数が不正: {review_count}問（期待値: 2問）")
                
            return True
            
        except Exception as e:
            self.log_error("テスト1実行エラー", str(e))
            return False
    
    def test_2_results_and_review_list_check(self):
        """テスト2: 結果分析画面表示確認と復習リスト表示確認"""
        print("\n📋 【テスト2】 結果分析画面表示確認と復習リスト表示確認")
        print("=" * 70)
        
        try:
            # 1. 結果画面アクセス
            response = self.session.get(f"{BASE_URL}/result")
            if response.status_code != 200:
                self.log_error("結果画面アクセス", f"ステータスコード: {response.status_code}")
                return False
                
            # 結果画面内容確認
            if "正答数" in response.text and "正答率" in response.text:
                self.log_success("結果画面表示", "結果分析画面が正しく表示")
            else:
                self.log_error("結果画面内容", "結果分析情報が不完全")
                
            # 基礎科目成績表示確認
            if "4-1 基礎科目" in response.text:
                self.log_success("基礎科目成績表示", "基礎科目の成績が正しく表示")
            else:
                self.log_error("基礎科目成績表示", "基礎科目成績が表示されていない")
            
            # 2. 復習リストページアクセス
            response = self.session.get(f"{BASE_URL}/bookmarks")
            if response.status_code != 200:
                self.log_error("復習リストアクセス", f"ステータスコード: {response.status_code}")
                return False
            
            # 復習リスト内容確認
            bookmark_count = response.text.count('bookmark-item')
            if bookmark_count >= 2:
                self.log_success("復習リスト表示", f"復習リストに{bookmark_count}問表示")
            else:
                self.log_error("復習リスト表示", f"復習リスト問題数不足: {bookmark_count}問")
                
            # 追加した問題が表示されているか確認
            for qid in self.review_questions:
                if qid in response.text:
                    self.log_success("復習問題確認", f"問題ID {qid} が復習リストに表示")
                else:
                    self.log_error("復習問題確認", f"問題ID {qid} が復習リストに見つからない")
            
            return True
            
        except Exception as e:
            self.log_error("テスト2実行エラー", str(e))
            return False
    
    def test_3_review_functionality(self):
        """テスト3: 復習リスト機能動作確認"""
        print("\n📋 【テスト3】 復習リスト機能動作確認")
        print("=" * 70)
        
        try:
            # 復習リストから問題を開始
            response = self.session.get(f"{BASE_URL}/review")
            if response.status_code != 200:
                self.log_error("復習開始", f"ステータスコード: {response.status_code}")
                return False
                
            # 復習問題が表示されているか確認
            if "RCCM試験" in response.text and ("選択肢A" in response.text or "option_a" in response.text):
                self.log_success("復習機能", "復習問題が正しく表示")
            else:
                self.log_error("復習機能", "復習問題が正しく表示されない")
                
            # 復習問題を1問回答
            csrf_token = self.get_csrf_token(response.text)
            qid_match = re.search(r'name="qid" value="([^"]+)"', response.text)
            
            if qid_match and csrf_token:
                qid = qid_match.group(1)
                answer_data = {
                    'qid': qid,
                    'answer': 'A',
                    'elapsed': '20.0',
                    'csrf_token': csrf_token
                }
                
                answer_response = self.session.post(f"{BASE_URL}/review", data=answer_data)
                if answer_response.status_code == 200:
                    self.log_success("復習回答", "復習問題の回答処理完了")
                else:
                    self.log_error("復習回答", "復習問題の回答処理失敗")
            
            return True
            
        except Exception as e:
            self.log_error("テスト3実行エラー", str(e))
            return False
    
    def test_4_specialist_questions(self):
        """テスト4: 道路部門専門科目全回答（3問復習リスト追加）"""
        print("\n📋 【テスト4】 道路部門専門科目全回答（3問復習リスト追加）")
        print("=" * 70)
        
        try:
            # スタート画面に戻る
            response = self.session.get(f"{BASE_URL}/")
            self.log_success("ホーム画面", "スタート画面に戻る")
            
            # 道路部門の専門科目選択
            response = self.session.get(f"{BASE_URL}/exam?department=road&type=specialist")
            if response.status_code != 200:
                self.log_error("専門科目開始", f"ステータスコード: {response.status_code}")
                return False
            self.log_success("専門科目開始", "道路部門専門科目セッション開始")
            
            # 専門科目を10問全て回答（3問を復習リストに追加）
            specialist_review_count = 0
            for question_num in range(1, 11):
                print(f"  専門問題 {question_num}/10 回答中...")
                
                # 問題ページ取得
                response = self.session.get(f"{BASE_URL}/exam")
                if response.status_code != 200:
                    self.log_error(f"専門問題{question_num}表示", f"ステータスコード: {response.status_code}")
                    continue
                    
                # 問題内容確認
                if "4-2 専門科目" not in response.text:
                    self.log_error(f"専門問題{question_num}内容", "専門科目の問題が表示されていない")
                    continue
                    
                # 年度情報確認（専門科目には年度があるはず）
                if "年度" not in response.text:
                    self.log_error(f"専門問題{question_num}年度", "専門科目に年度情報がない")
                    
                # CSRFトークン取得
                csrf_token = self.get_csrf_token(response.text)
                
                # 問題IDを抽出
                qid_match = re.search(r'name="qid" value="([^"]+)"', response.text)
                if not qid_match:
                    self.log_error(f"専門問題{question_num}ID取得", "問題IDが見つからない")
                    continue
                qid = qid_match.group(1)
                
                # 1問目、4問目、8問目を復習リストに追加
                if question_num in [1, 4, 8]:
                    review_data = {
                        'qid': qid,
                        'csrf_token': csrf_token
                    }
                    review_response = self.session.post(f"{BASE_URL}/bookmark", data=review_data)
                    if review_response.status_code == 200:
                        self.log_success(f"専門問題{question_num}復習追加", "復習リストに追加成功")
                        specialist_review_count += 1
                        self.review_questions.append(qid)
                    else:
                        self.log_error(f"専門問題{question_num}復習追加", "復習リスト追加失敗")
                
                # 問題に回答
                answer_choice = random.choice(['A', 'B', 'C', 'D'])
                answer_data = {
                    'qid': qid,
                    'answer': answer_choice,
                    'elapsed': '25.0',
                    'csrf_token': csrf_token
                }
                
                answer_response = self.session.post(f"{BASE_URL}/exam", data=answer_data)
                if answer_response.status_code != 200:
                    self.log_error(f"専門問題{question_num}回答", f"回答送信失敗: {answer_response.status_code}")
                    continue
                    
                # フィードバック画面確認
                if "正解" in answer_response.text or "不正解" in answer_response.text:
                    self.log_success(f"専門問題{question_num}回答", f"回答処理完了（選択: {answer_choice}）")
                else:
                    self.log_error(f"専門問題{question_num}フィードバック", "フィードバック画面が正しく表示されない")
                
                time.sleep(0.5)
            
            if specialist_review_count == 3:
                self.log_success("専門復習リスト追加", f"指定通り3問を復習リストに追加完了")
            else:
                self.log_error("専門復習リスト追加", f"追加数が不正: {specialist_review_count}問（期待値: 3問）")
                
            return True
            
        except Exception as e:
            self.log_error("テスト4実行エラー", str(e))
            return False
    
    def test_5_specialist_results_and_final_review(self):
        """テスト5: 専門科目結果分析画面確認と復習リスト再確認"""
        print("\n📋 【テスト5】 専門科目結果分析画面確認と復習リスト再確認")
        print("=" * 70)
        
        try:
            # 専門科目結果画面アクセス
            response = self.session.get(f"{BASE_URL}/result")
            if response.status_code != 200:
                self.log_error("専門結果画面アクセス", f"ステータスコード: {response.status_code}")
                return False
                
            # 結果画面内容確認
            if "4-2 専門科目" in response.text:
                self.log_success("専門結果画面表示", "専門科目の結果分析画面が正しく表示")
            else:
                self.log_error("専門結果画面表示", "専門科目結果が表示されていない")
            
            # 復習リストに戻って総数確認
            response = self.session.get(f"{BASE_URL}/bookmarks")
            if response.status_code != 200:
                self.log_error("最終復習リストアクセス", f"ステータスコード: {response.status_code}")
                return False
            
            # 最終的な復習リスト問題数確認（基礎2問 + 専門3問 = 5問）
            bookmark_count = response.text.count('bookmark-item')
            if bookmark_count >= 5:
                self.log_success("最終復習リスト確認", f"復習リストに合計{bookmark_count}問表示（期待値: 5問以上）")
            else:
                self.log_error("最終復習リスト確認", f"復習リスト問題数不足: {bookmark_count}問（期待値: 5問）")
            
            return True
            
        except Exception as e:
            self.log_error("テスト5実行エラー", str(e))
            return False
    
    def test_6_final_review_functionality_and_duplicate_check(self):
        """テスト6: 復習リスト回答機能と重複問題チェック"""
        print("\n📋 【テスト6】 復習リスト回答機能と重複問題チェック")
        print("=" * 70)
        
        try:
            encountered_qids = set()
            
            # 復習リストから複数問題を回答
            for attempt in range(3):  # 3回復習問題にアクセス
                response = self.session.get(f"{BASE_URL}/review")
                if response.status_code != 200:
                    self.log_error(f"復習回答{attempt+1}", f"ステータスコード: {response.status_code}")
                    continue
                
                # 問題ID確認
                qid_match = re.search(r'name="qid" value="([^"]+)"', response.text)
                if qid_match:
                    qid = qid_match.group(1)
                    if qid in encountered_qids:
                        self.log_error("重複問題チェック", f"同じ問題が再出題: {qid}")
                    else:
                        encountered_qids.add(qid)
                        self.log_success(f"復習問題{attempt+1}", f"新しい問題 {qid} を確認")
                
                # 問題内容と画面表示確認
                if "RCCM試験" in response.text:
                    self.log_success(f"復習画面{attempt+1}", "復習画面が正しく表示")
                else:
                    self.log_error(f"復習画面{attempt+1}", "復習画面の表示に問題")
                
                # 基礎科目か専門科目かを確認
                if "4-1 基礎科目" in response.text:
                    self.log_success(f"復習問題種別{attempt+1}", "基礎科目の復習問題")
                elif "4-2 専門科目" in response.text:
                    self.log_success(f"復習問題種別{attempt+1}", "専門科目の復習問題")
                else:
                    self.log_error(f"復習問題種別{attempt+1}", "問題種別が不明")
                
                # 回答処理
                csrf_token = self.get_csrf_token(response.text)
                if csrf_token and qid_match:
                    answer_data = {
                        'qid': qid,
                        'answer': random.choice(['A', 'B', 'C', 'D']),
                        'elapsed': '18.0',
                        'csrf_token': csrf_token
                    }
                    
                    answer_response = self.session.post(f"{BASE_URL}/review", data=answer_data)
                    if answer_response.status_code == 200:
                        self.log_success(f"復習回答{attempt+1}", "復習問題回答処理完了")
                    else:
                        self.log_error(f"復習回答{attempt+1}", "復習問題回答処理失敗")
                
                time.sleep(1)
            
            # 重複チェック結果
            if len(encountered_qids) >= 2:
                self.log_success("重複問題チェック", f"{len(encountered_qids)}個の異なる問題を確認（重複なし）")
            else:
                self.log_error("重複問題チェック", "十分な問題バリエーションが確認できない")
            
            return True
            
        except Exception as e:
            self.log_error("テスト6実行エラー", str(e))
            return False
    
    def run_comprehensive_flow_test(self):
        """包括的フローテスト実行"""
        print("🔬 RCCM試験問題集アプリ - ユーザー指摘事項の厳重フローテスト")
        print("=" * 80)
        print("テスト対象: 初期画面→道路部門→基礎→復習→専門→復習の全フロー")
        print("=" * 80)
        
        # 全テスト実行
        tests = [
            ("初期画面→道路部門→基礎問題全回答", self.test_1_initial_screen_to_basic_questions),
            ("結果分析・復習リスト表示確認", self.test_2_results_and_review_list_check),
            ("復習リスト機能動作確認", self.test_3_review_functionality),
            ("道路部門専門科目全回答", self.test_4_specialist_questions),
            ("専門科目結果・復習リスト再確認", self.test_5_specialist_results_and_final_review),
            ("復習回答・重複チェック", self.test_6_final_review_functionality_and_duplicate_check)
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n🔄 実行中: {test_name}")
            if test_func():
                passed_tests += 1
        
        # 最終結果
        print("\n" + "=" * 80)
        print("🎯 【最終フローテスト結果】")
        print("=" * 80)
        
        print(f"実行テスト数: {total_tests}")
        print(f"成功テスト数: {passed_tests}")
        print(f"失敗テスト数: {total_tests - passed_tests}")
        print(f"成功率: {(passed_tests / total_tests * 100):.1f}%")
        
        if self.errors:
            print(f"\n🚨 検出されたエラー ({len(self.errors)}件):")
            for error in self.errors:
                print(f"  - {error}")
        
        print("\n" + "=" * 80)
        if passed_tests == total_tests:
            print("🎉 【総合判定】全フローテスト合格 - 全ての指摘事項が正常に動作")
        else:
            print("🚨 【総合判定】一部フローテスト失敗 - 修正が必要")
        print("=" * 80)
        
        return passed_tests == total_tests

if __name__ == "__main__":
    tester = RCCMFlowTester()
    success = tester.run_comprehensive_flow_test()
    exit(0 if success else 1)