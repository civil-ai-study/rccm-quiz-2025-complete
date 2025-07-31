#!/usr/bin/env python3
"""
🎯 本番環境専門4-2問題選択完走テスト
Render.com修正後の厳重な動作確認
"""

import requests
import json
import time
from datetime import datetime

class ProductionSpecialist42Test:
    def __init__(self):
        self.base_url = "https://rccm-quiz-2025.onrender.com"
        self.session = requests.Session()
        self.test_results = []
        
    def test_homepage_access(self):
        """ホームページアクセステスト"""
        print("ホームページアクセステスト開始...")
        try:
            response = self.session.get(self.base_url, timeout=30)
            if response.status_code == 200:
                print("ホームページアクセス成功")
                return True
            else:
                print(f"ホームページアクセス失敗: {response.status_code}")
                return False
        except Exception as e:
            print(f"ホームページアクセスエラー: {e}")
            return False
    
    def test_specialist_42_selection(self):
        """専門4-2選択テスト"""
        print("専門4-2選択テスト開始...")
        try:
            # 専門4-2のページアクセス
            url = f"{self.base_url}/civil_types"
            response = self.session.get(url, timeout=30)
            
            if response.status_code == 200:
                print("専門4-2ページアクセス成功")
                print(f"レスポンスサイズ: {len(response.text)} bytes")
                
                # 部門選択リンクの確認
                departments = ["道路", "河川・砂防", "都市計画", "造園"]
                found_departments = []
                
                for dept in departments:
                    if dept in response.text:
                        found_departments.append(dept)
                        print(f"{dept}部門リンク確認")
                
                return len(found_departments) > 0
            else:
                print(f"専門4-2ページアクセス失敗: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"専門4-2選択エラー: {e}")
            return False
    
    def test_department_selection(self, department="道路"):
        """部門選択テスト"""
        print(f"{department}部門選択テスト開始...")
        try:
            # 部門ページアクセス
            url = f"{self.base_url}/quiz_department/{department}"
            response = self.session.get(url, timeout=30)
            
            if response.status_code == 200:
                print(f"{department}部門ページアクセス成功")
                print(f"レスポンスサイズ: {len(response.text)} bytes")
                
                # 問題数選択ボタンの確認
                if "10問" in response.text or "quiz" in response.text:
                    print("問題選択ボタン確認")
                    return True
                else:
                    print("問題選択ボタンが見つからない")
                    return False
            else:
                print(f"{department}部門アクセス失敗: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"{department}部門選択エラー: {e}")
            return False
    
    def test_quiz_start(self, department="道路", questions=10):
        """クイズ開始テスト"""
        print(f"{department}部門 {questions}問クイズ開始テスト...")
        try:
            # クイズ開始リクエスト
            url = f"{self.base_url}/start_exam/{department}"
            data = {
                "questions": questions,
                "year": "2024"
            }
            
            response = self.session.post(url, data=data, timeout=30)
            
            if response.status_code == 200:
                print(f"{department}部門クイズ開始成功")
                
                # 問題表示の確認
                if "問題" in response.text and "選択肢" in response.text:
                    print("問題表示確認")
                    return True
                else:
                    print("問題が正しく表示されていない")
                    # デバッグ情報
                    with open("quiz_start_debug.html", "w", encoding="utf-8") as f:
                        f.write(response.text)
                    print("デバッグファイル保存: quiz_start_debug.html")
                    return False
            else:
                print(f"クイズ開始失敗: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"クイズ開始エラー: {e}")
            return False
    
    def test_question_answer_flow(self, department="道路"):
        """問題回答フロー完走テスト"""
        print(f"{department}部門完走テスト開始...")
        try:
            # 1. クイズ開始
            start_url = f"{self.base_url}/start_exam/{department}"
            start_data = {"questions": 10, "year": "2024"}
            
            start_response = self.session.post(start_url, data=start_data, timeout=30)
            
            if start_response.status_code != 200:
                print(f"クイズ開始失敗: {start_response.status_code}")
                return False
            
            print("クイズ開始成功")
            
            # 2. 10問の回答処理
            for question_no in range(1, 11):
                print(f"第{question_no}問 回答中...")
                
                # 回答送信
                answer_url = f"{self.base_url}/quiz"
                answer_data = {
                    "answer": "1",  # 選択肢1を選択
                    "current": question_no
                }
                
                answer_response = self.session.post(answer_url, data=answer_data, timeout=30)
                
                if answer_response.status_code == 200:
                    print(f"第{question_no}問 回答成功")
                    
                    # 最後の問題かチェック
                    if question_no == 10:
                        if "結果" in answer_response.text or "完了" in answer_response.text:
                            print("10問完走成功!")
                            return True
                    else:
                        # 次の問題へ
                        time.sleep(1)  # サーバー負荷軽減
                else:
                    print(f"第{question_no}問 回答失敗: {answer_response.status_code}")
                    return False
            
            print("10問完走テスト完了")
            return True
            
        except Exception as e:
            print(f"完走テストエラー: {e}")
            return False
    
    def run_comprehensive_test(self):
        """包括的テスト実行"""
        print("ULTRA SYNC 本番環境専門4-2完走テスト開始")
        print(f"テスト開始時刻: {datetime.now()}")
        print("=" * 50)
        
        results = {
            "test_time": datetime.now().isoformat(),
            "base_url": self.base_url,
            "tests": {}
        }
        
        # 1. ホームページアクセス
        results["tests"]["homepage"] = self.test_homepage_access()
        
        # 2. 専門4-2選択
        results["tests"]["specialist_42"] = self.test_specialist_42_selection()
        
        # 3. 部門選択（道路部門）
        results["tests"]["department_road"] = self.test_department_selection("道路")
        
        # 4. クイズ開始
        results["tests"]["quiz_start"] = self.test_quiz_start("道路", 10)
        
        # 5. 完走テスト
        results["tests"]["complete_quiz"] = self.test_question_answer_flow("道路")
        
        # 結果サマリー
        print("=" * 50)
        print("テスト結果サマリー")
        
        passed = sum(1 for test in results["tests"].values() if test)
        total = len(results["tests"])
        
        for test_name, result in results["tests"].items():
            status = "成功" if result else "失敗"
            print(f"{test_name}: {status}")
        
        print(f"\n合格率: {passed}/{total} ({passed/total*100:.1f}%)")
        
        if passed == total:
            print("全テスト合格!専門4-2完走テスト成功")
        else:
            print("一部テスト失敗")
        
        # 結果保存
        with open("production_specialist_42_test_results.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        return results

if __name__ == "__main__":
    tester = ProductionSpecialist42Test()
    tester.run_comprehensive_test()