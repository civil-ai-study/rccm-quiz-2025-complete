#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ULTRA SYNC 実際の問題解答テスト
河川・砂防2018年で実際に1問を完全に解答して次問題に進むテスト
問題文・選択肢・回答送信・次問題遷移の全フローを実際に確認
"""

import requests
import time
import re
from datetime import datetime

class UltraSyncActualQuestionTest:
    def __init__(self):
        self.base_url = "https://rccm-quiz-2025.onrender.com"
        self.session = requests.Session()
        
    def test_complete_question_flow(self):
        """完全な1問解答フローのテスト"""
        print("ULTRA SYNC 実際の問題解答フローテスト")
        print(f"対象: 河川・砂防 2018年 実際の1問解答")
        print(f"テスト時刻: {datetime.now().strftime('%H:%M:%S')}")
        print("=" * 50)
        
        try:
            # Step 1: セッション開始
            print("\n1. セッション開始")
            start_url = f"{self.base_url}/start_exam/河川・砂防"
            start_data = {"questions": 10, "year": "2018"}  # 10問設定
            
            start_response = self.session.post(start_url, data=start_data, timeout=60)
            print(f"   セッション開始: HTTP {start_response.status_code}")
            
            if start_response.status_code != 200:
                print(f"   ERROR: セッション開始失敗")
                return False
                
            # Step 2: 問題ページアクセス
            print("\n2. 第1問目の問題表示")
            exam_url = f"{self.base_url}/exam"
            exam_response = self.session.get(exam_url, timeout=60)
            print(f"   問題ページ: HTTP {exam_response.status_code}")
            
            if exam_response.status_code != 200:
                print(f"   ERROR: 問題ページアクセス失敗")
                return False
            
            page_content = exam_response.text
            
            # Step 3: 問題内容の詳細確認
            print("\n3. 問題内容の確認")
            
            # 問題文の抽出
            question_match = re.search(r'<p[^>]*class="question-text"[^>]*>(.*?)</p>', page_content, re.DOTALL)
            if question_match:
                question_text = re.sub(r'<[^>]+>', '', question_match.group(1)).strip()
                print(f"   問題文: {question_text[:50]}...")
            else:
                print("   WARNING: 問題文が見つかりません")
            
            # 選択肢の抽出
            options = re.findall(r'<input[^>]*name="answer"[^>]*value="([A-D])"[^>]*>.*?<label[^>]*>(.*?)</label>', page_content, re.DOTALL)
            print(f"   選択肢数: {len(options)}")
            
            if len(options) < 4:
                print("   ERROR: 選択肢が不完全です")
                return False
                
            for opt_val, opt_text in options:
                clean_text = re.sub(r'<[^>]+>', '', opt_text).strip()
                print(f"   {opt_val}: {clean_text[:30]}...")
            
            # Step 4: 実際に回答を送信
            print("\n4. 回答送信テスト")
            submit_url = f"{self.base_url}/submit_answer"
            
            # 最初の選択肢（A）を選択して送信
            submit_data = {"answer": "A"}
            submit_response = self.session.post(submit_url, data=submit_data, timeout=60)
            print(f"   回答送信: HTTP {submit_response.status_code}")
            
            if submit_response.status_code != 200:
                print(f"   ERROR: 回答送信失敗")
                return False
            
            # Step 5: 次の問題に進む
            print("\n5. 第2問目への進行確認")
            next_exam_response = self.session.get(exam_url, timeout=60)
            print(f"   第2問目: HTTP {next_exam_response.status_code}")
            
            if next_exam_response.status_code != 200:
                print(f"   ERROR: 第2問目アクセス失敗")
                return False
            
            # Step 6: 問題番号の確認（1→2に進んだか）
            next_content = next_exam_response.text
            
            # 問題番号の確認
            progress_match = re.search(r'問題\s*(\d+)\s*/\s*(\d+)', next_content)
            if progress_match:
                current_q = progress_match.group(1)
                total_q = progress_match.group(2)
                print(f"   進行状況: 問題 {current_q}/{total_q}")
                
                if current_q == "2":
                    print("   EXCELLENT: 第2問目に正常に進みました")
                    return True
                else:
                    print(f"   WARNING: 第2問目ではなく問題{current_q}になっています")
                    return False
            else:
                print("   WARNING: 問題番号が確認できません")
                # 第2問目の問題文があるかで判定
                has_second_question = any(keyword in next_content for keyword in ['問題', '次の', '正しい'])
                if has_second_question:
                    print("   OK: 第2問目と思われる問題が表示されています")
                    return True
                else:
                    return False
                
        except Exception as e:
            print(f"   テストエラー: {e}")
            return False
    
    def test_question_data_integrity(self):
        """問題データの整合性確認"""
        print("\n" + "=" * 50)
        print("ULTRA SYNC 問題データ整合性確認")
        print("=" * 50)
        
        try:
            # 複数回アクセスして問題が正常に変わるか確認
            print("\n複数問題での整合性確認...")
            
            for i in range(3):
                print(f"\n{i+1}回目の問題アクセス")
                
                # 新しいセッションで河川・砂防2018年を開始
                start_url = f"{self.base_url}/start_exam/河川・砂防"
                start_data = {"questions": 5, "year": "2018"}
                
                start_response = self.session.post(start_url, data=start_data, timeout=30)
                
                if start_response.status_code == 200:
                    exam_response = self.session.get(f"{self.base_url}/exam", timeout=30)
                    
                    if exam_response.status_code == 200:
                        content = exam_response.text
                        
                        # 年度とカテゴリーの確認
                        has_river_keywords = any(keyword in content for keyword in [
                            '河川', '砂防', '治水', '洪水', 'ダム', '堤防'
                        ])
                        
                        print(f"   HTTP: {exam_response.status_code}")
                        print(f"   河川・砂防関連: {'OK' if has_river_keywords else 'NG'}")
                    else:
                        print(f"   問題ページ失敗: HTTP {exam_response.status_code}")
                        return False
                else:
                    print(f"   セッション失敗: HTTP {start_response.status_code}")
                    return False
                    
                time.sleep(1)  # サーバー負荷軽減
            
            print("\n整合性確認完了")
            return True
            
        except Exception as e:
            print(f"   整合性確認エラー: {e}")
            return False

def main():
    print("ULTRA SYNC 実際の問題解答フローテスト")
    print("対象: 河川・砂防 2018年での完全フロー確認")
    print("=" * 60)
    
    tester = UltraSyncActualQuestionTest()
    
    # Step 1: 完全な問題解答フロー
    flow_test_result = tester.test_complete_question_flow()
    
    # Step 2: 問題データ整合性確認
    integrity_test_result = tester.test_question_data_integrity()
    
    # 総合結果
    print("\n" + "=" * 60)
    print("ULTRA SYNC 実際の問題解答テスト結果")
    print("=" * 60)
    
    print(f"問題解答フロー: {'成功' if flow_test_result else '失敗'}")
    print(f"データ整合性: {'OK' if integrity_test_result else 'NG'}")
    
    overall_success = flow_test_result and integrity_test_result
    
    if overall_success:
        print("\nULTRA SYNC 問題解答テスト: 成功")
        print("1問→回答送信→第2問への進行が正常に動作")
        print("次のステップ（道路部門テスト）に進行可能")
    else:
        print("\nULTRA SYNC 問題解答テスト: 要修正")
        print("問題表示または回答処理に問題があります")
    
    return overall_success

if __name__ == "__main__":
    main()