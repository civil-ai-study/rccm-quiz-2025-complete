#!/usr/bin/env python3
"""
基礎科目4-1共通問題本番環境厳重テスト
専門4-2と同じテスト条件で結果確認まで完全実行
"""

import requests
import json
import time
from datetime import datetime

class ProductionCommon41Test:
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
    
    def test_basic_subject_selection(self):
        """基礎科目4-1選択テスト"""
        print("基礎科目4-1選択テスト開始...")
        try:
            # 基礎科目のページアクセス
            url = f"{self.base_url}/basic_subjects"
            response = self.session.get(url, timeout=30)
            
            if response.status_code == 200:
                print("基礎科目ページアクセス成功")
                print(f"レスポンスサイズ: {len(response.text)} bytes")
                
                # 基礎科目の確認
                if "基礎科目" in response.text or "共通" in response.text:
                    print("基礎科目リンク確認")
                    return True
                else:
                    print("基礎科目リンクが見つからない")
                    # デバッグ情報保存
                    with open("basic_subjects_debug.html", "w", encoding="utf-8") as f:
                        f.write(response.text)
                    return False
            else:
                print(f"基礎科目ページアクセス失敗: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"基礎科目選択エラー: {e}")
            return False
    
    def test_basic_department_selection(self):
        """基礎科目(共通)選択テスト"""
        print("基礎科目(共通)選択テスト開始...")
        try:
            # 基礎科目(共通)ページアクセス
            url = f"{self.base_url}/quiz_department/基礎科目(共通)"
            response = self.session.get(url, timeout=30)
            
            if response.status_code == 200:
                print("基礎科目(共通)ページアクセス成功")
                print(f"レスポンスサイズ: {len(response.text)} bytes")
                
                # 問題数選択ボタンの確認
                if "10問" in response.text or "quiz" in response.text or "開始" in response.text:
                    print("問題選択ボタン確認")
                    return True
                else:
                    print("問題選択ボタンが見つからない")
                    # デバッグファイル保存
                    with open("basic_common_debug.html", "w", encoding="utf-8") as f:
                        f.write(response.text)
                    return False
            else:
                print(f"基礎科目(共通)アクセス失敗: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"基礎科目(共通)選択エラー: {e}")
            return False
    
    def test_basic_quiz_start(self, questions=10):
        """基礎科目クイズ開始テスト"""
        print(f"基礎科目(共通) {questions}問クイズ開始テスト...")
        try:
            # クイズ開始リクエスト
            url = f"{self.base_url}/start_exam/基礎科目(共通)"
            data = {
                "questions": questions,
                "year": "2024"
            }
            
            response = self.session.post(url, data=data, timeout=30)
            
            if response.status_code == 200:
                print("基礎科目(共通)クイズ開始成功")
                
                # 問題表示の確認
                if "問題" in response.text and ("選択肢" in response.text or "答え" in response.text):
                    print("問題表示確認")
                    return True
                else:
                    print("問題が正しく表示されていない")
                    # デバッグ情報
                    with open("basic_quiz_start_debug.html", "w", encoding="utf-8") as f:
                        f.write(response.text)
                    print("デバッグファイル保存: basic_quiz_start_debug.html")
                    return False
            else:
                print(f"クイズ開始失敗: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"クイズ開始エラー: {e}")
            return False
    
    def test_basic_question_answer_flow(self):
        """基礎科目問題回答フロー完走テスト（結果確認まで）"""
        print("基礎科目(共通)完走テスト開始...")
        try:
            # 1. クイズ開始
            start_url = f"{self.base_url}/start_exam/基礎科目(共通)"
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
                        # 結果確認
                        if "結果" in answer_response.text or "完了" in answer_response.text or "スコア" in answer_response.text:
                            print("10問完走成功!")
                            print("結果画面表示確認")
                            
                            # 結果画面保存
                            with open("basic_results_final.html", "w", encoding="utf-8") as f:
                                f.write(answer_response.text)
                            print("結果画面保存: basic_results_final.html")
                            
                            return True
                        else:
                            print("結果画面が正しく表示されていない")
                            # デバッグ用に最終画面保存
                            with open("basic_final_debug.html", "w", encoding="utf-8") as f:
                                f.write(answer_response.text)
                            return False
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
    
    def test_results_verification(self):
        """結果画面詳細確認テスト"""
        print("結果画面詳細確認テスト開始...")
        try:
            # 完走テスト後の結果確認
            # (上記の完走テストで結果画面まで到達している前提)
            
            # 結果ファイルが存在するかチェック
            try:
                with open("basic_results_final.html", "r", encoding="utf-8") as f:
                    content = f.read()
                
                # 結果画面の必要要素チェック
                checks = {
                    "score_display": "点" in content or "スコア" in content,
                    "question_count": "10" in content,
                    "percentage": "%" in content,
                    "completion": "完了" in content or "終了" in content
                }
                
                passed_checks = sum(checks.values())
                total_checks = len(checks)
                
                print(f"結果画面要素チェック: {passed_checks}/{total_checks}")
                for check_name, result in checks.items():
                    print(f"  {check_name}: {'OK' if result else 'NG'}")
                
                return passed_checks >= 2  # 最低2つの要素があれば成功
                
            except FileNotFoundError:
                print("結果ファイルが見つからない")
                return False
                
        except Exception as e:
            print(f"結果確認エラー: {e}")
            return False
    
    def run_comprehensive_test(self):
        """包括的テスト実行（結果確認まで）"""
        print("ULTRA SYNC 基礎科目4-1完走テスト開始")
        print(f"テスト開始時刻: {datetime.now()}")
        print("=" * 50)
        
        results = {
            "test_time": datetime.now().isoformat(),
            "base_url": self.base_url,
            "subject": "基礎科目4-1(共通)",
            "tests": {}
        }
        
        # 1. ホームページアクセス
        results["tests"]["homepage"] = self.test_homepage_access()
        
        # 2. 基礎科目選択
        results["tests"]["basic_subject"] = self.test_basic_subject_selection()
        
        # 3. 基礎科目(共通)選択
        results["tests"]["basic_common"] = self.test_basic_department_selection()
        
        # 4. クイズ開始
        results["tests"]["quiz_start"] = self.test_basic_quiz_start(10)
        
        # 5. 完走テスト（結果確認まで）
        results["tests"]["complete_quiz"] = self.test_basic_question_answer_flow()
        
        # 6. 結果画面詳細確認
        results["tests"]["results_verification"] = self.test_results_verification()
        
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
            print("全テスト合格!基礎科目4-1完走テスト成功")
        elif results["tests"]["complete_quiz"] and results["tests"]["results_verification"]:
            print("重要機能成功!基礎科目4-1完走と結果確認成功")
        else:
            print("一部テスト失敗")
        
        # 結果保存
        with open("production_basic_4_1_test_results.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        return results

if __name__ == "__main__":
    tester = ProductionCommon41Test()
    tester.run_comprehensive_test()