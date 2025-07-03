#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 RCCM試験アプリ - 河川・砂防部門手動テストスクリプト
修正対象部門の詳細検証（TC-002: 河川・砂防部門完走テスト）

実行方法: python3 manual_test_river.py
"""

import requests
import json
import time
from datetime import datetime

class RCCMRiverManualTest:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        self.test_start_time = datetime.now()
        
    def log_result(self, test_name, status, details, error_details=None):
        """テスト結果をログに記録"""
        result = {
            "test_name": test_name,
            "status": status,  # "SUCCESS", "FAILED", "INVESTIGATING" 
            "details": details,
            "error_details": error_details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        # リアルタイム表示
        status_icon = "✅" if status == "SUCCESS" else "❌" if status == "FAILED" else "🔍"
        print(f"{status_icon} {test_name}: {details}")
        if error_details:
            print(f"   エラー詳細: {error_details}")
    
    def test_river_department_access(self):
        """TC-002-1: 河川・砂防部門アクセステスト"""
        test_name = "河川・砂防部門アクセステスト"
        
        try:
            # 1. ホーム画面アクセス
            response = self.session.get(f"{self.base_url}/")
            if response.status_code != 200:
                self.log_result(test_name, "FAILED", "ホーム画面アクセス失敗", f"Status: {response.status_code}")
                return False
            
            # 2. 河川部門URL直接アクセステスト（civil_planning）
            dept_url = f"{self.base_url}/department_study/civil_planning"
            response = self.session.get(dept_url)
            
            if response.status_code != 200:
                self.log_result(test_name, "FAILED", "河川部門アクセス失敗", f"Status: {response.status_code}")
                return False
            
            # 3. レスポンス内容確認
            if "河川" in response.text or "砂防" in response.text or "海岸" in response.text:
                self.log_result(test_name, "SUCCESS", "河川・砂防部門画面正常表示確認")
                return True
            else:
                self.log_result(test_name, "FAILED", "河川部門内容が表示されない", "ページ内容に河川関連テキストなし")
                return False
                
        except Exception as e:
            self.log_result(test_name, "FAILED", "例外発生", str(e))
            return False
    
    def test_river_alias_access(self):
        """TC-002-2: 河川部門エイリアス（river）アクセステスト"""
        test_name = "河川部門エイリアス（river）アクセステスト"
        
        try:
            # river エイリアスでのアクセステスト
            dept_url = f"{self.base_url}/department_study/river"
            response = self.session.get(dept_url)
            
            if response.status_code == 200:
                self.log_result(test_name, "SUCCESS", "riverエイリアスアクセス成功")
                return True
            elif response.status_code == 302:
                self.log_result(test_name, "SUCCESS", "riverエイリアス正常リダイレクト")
                return True
            else:
                self.log_result(test_name, "FAILED", "riverエイリアスアクセス失敗", f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result(test_name, "FAILED", "例外発生", str(e))
            return False
    
    def test_river_quiz_initialization(self):
        """TC-002-3: 河川部門クイズ初期化テスト"""
        test_name = "河川部門クイズ初期化テスト"
        
        try:
            # セッション初期化リクエスト
            quiz_start_url = f"{self.base_url}/start_quiz"
            data = {
                "category": "specialist",
                "department": "civil_planning",
                "questions_per_session": 10
            }
            
            response = self.session.post(quiz_start_url, data=data)
            
            if response.status_code == 302:  # リダイレクト期待
                self.log_result(test_name, "SUCCESS", "クイズ初期化成功（リダイレクト確認）")
                return True
            elif response.status_code == 200:
                # エラーページかどうか確認
                if "エラー" in response.text or "error" in response.text.lower():
                    self.log_result(test_name, "FAILED", "クイズ初期化時エラー発生", "エラーページが表示された")
                    return False
                else:
                    self.log_result(test_name, "SUCCESS", "クイズ初期化成功（200レスポンス）")
                    return True
            else:
                self.log_result(test_name, "FAILED", f"予期しないステータスコード", f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result(test_name, "FAILED", "例外発生", str(e))
            return False
    
    def test_river_first_question(self):
        """TC-002-4: 河川部門1問目表示テスト（最重要）"""
        test_name = "河川部門1問目表示テスト"
        
        try:
            # クイズ画面にアクセス
            quiz_url = f"{self.base_url}/quiz"
            response = self.session.get(quiz_url)
            
            if response.status_code != 200:
                self.log_result(test_name, "FAILED", "クイズ画面アクセス失敗", f"Status: {response.status_code}")
                return False
            
            # エラー画面チェック（最重要）
            response_text = response.text.lower()
            error_indicators = ["エラー", "error", "exception", "traceback", "500", "404", "問題が見つかりません"]
            
            for indicator in error_indicators:
                if indicator in response_text:
                    self.log_result(test_name, "FAILED", "1問目でエラー画面表示", f"エラー指標: {indicator}")
                    return False
            
            # 問題表示要素チェック
            required_elements = ["問題", "選択肢", "option_a", "option_b", "option_c", "option_d"]
            missing_elements = []
            
            for element in required_elements:
                if element not in response.text:
                    missing_elements.append(element)
            
            if missing_elements:
                self.log_result(test_name, "FAILED", "必須要素が不足", f"不足要素: {', '.join(missing_elements)}")
                return False
            
            # 河川関連問題かチェック
            river_keywords = ["河川", "砂防", "海岸", "海洋", "治水", "防災", "流域", "ダム", "堤防"]
            river_related = any(keyword in response.text for keyword in river_keywords)
            
            if river_related:
                self.log_result(test_name, "SUCCESS", "河川部門1問目正常表示確認（河川関連問題）")
            else:
                self.log_result(test_name, "SUCCESS", "1問目正常表示確認（問題分野要確認）", "河川関連キーワード未検出")
            
            return True
                
        except Exception as e:
            self.log_result(test_name, "FAILED", "例外発生", str(e))
            return False
    
    def test_river_category_mapping(self):
        """TC-002-5: 河川部門カテゴリマッピング確認テスト"""
        test_name = "河川部門カテゴリマッピング確認テスト"
        
        try:
            # APIエンドポイントで問題数確認
            api_url = f"{self.base_url}/api/questions/count"
            params = {"department": "civil_planning", "category": "specialist"}
            
            response = self.session.get(api_url, params=params)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    question_count = data.get("count", 0)
                    
                    if question_count >= 10:
                        self.log_result(test_name, "SUCCESS", f"河川部門問題数確認: {question_count}問（10問以上）")
                        return True
                    elif question_count > 0:
                        self.log_result(test_name, "FAILED", f"河川部門問題数不足: {question_count}問（10問未満）")
                        return False
                    else:
                        self.log_result(test_name, "FAILED", "河川部門問題数0件", "該当問題が見つからない - カテゴリマッピングエラーの可能性")
                        return False
                        
                except json.JSONDecodeError:
                    self.log_result(test_name, "FAILED", "APIレスポンス解析失敗", "JSONパースエラー")
                    return False
            else:
                self.log_result(test_name, "INVESTIGATING", f"API呼び出し失敗", f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result(test_name, "FAILED", "例外発生", str(e))
            return False
    
    def test_river_10_question_session(self):
        """TC-002-6: 河川部門10問完走テスト"""
        test_name = "河川部門10問完走テスト"
        
        try:
            question_count = 0
            max_questions = 10
            
            while question_count < max_questions:
                # 現在の問題取得
                quiz_url = f"{self.base_url}/quiz"
                response = self.session.get(quiz_url)
                
                if response.status_code != 200:
                    self.log_result(test_name, "FAILED", f"{question_count+1}問目取得失敗", f"Status: {response.status_code}")
                    return False
                
                # 問題画面かチェック
                if "問題" not in response.text:
                    if "結果" in response.text or "スコア" in response.text:
                        # 結果画面に到達
                        if question_count == max_questions:
                            self.log_result(test_name, "SUCCESS", f"河川部門{max_questions}問完走成功")
                            return True
                        else:
                            self.log_result(test_name, "FAILED", f"予期しない早期終了", f"{question_count}問で終了")
                            return False
                    else:
                        self.log_result(test_name, "FAILED", f"{question_count+1}問目表示異常", "問題画面が表示されない")
                        return False
                
                # 回答送信（選択肢aを選択）
                answer_data = {"answer": "a"}
                response = self.session.post(quiz_url, data=answer_data)
                
                if response.status_code not in [200, 302]:
                    self.log_result(test_name, "FAILED", f"{question_count+1}問目回答送信失敗", f"Status: {response.status_code}")
                    return False
                
                question_count += 1
                time.sleep(0.5)  # サーバー負荷軽減
            
            # 10問完了後、結果画面確認
            result_response = self.session.get(f"{self.base_url}/quiz")
            if "結果" in result_response.text or "スコア" in result_response.text:
                self.log_result(test_name, "SUCCESS", f"河川部門{max_questions}問完走成功")
                return True
            else:
                self.log_result(test_name, "FAILED", "結果画面未表示", "10問完了後に結果画面が表示されない")
                return False
                
        except Exception as e:
            self.log_result(test_name, "FAILED", "例外発生", str(e))
            return False
    
    def run_comprehensive_test(self):
        """包括的テスト実行"""
        print("=" * 60)
        print("🧪 RCCM河川・砂防部門 包括的手動テスト開始")
        print(f"📅 実行開始時刻: {self.test_start_time}")
        print("=" * 60)
        
        # テスト実行順序
        tests = [
            self.test_river_department_access,
            self.test_river_alias_access,
            self.test_river_quiz_initialization,
            self.test_river_first_question,
            self.test_river_category_mapping,
            self.test_river_10_question_session
        ]
        
        success_count = 0
        total_tests = len(tests)
        
        for test_func in tests:
            print("-" * 40)
            success = test_func()
            if success:
                success_count += 1
            time.sleep(1)  # テスト間隔
        
        # 結果サマリー
        print("=" * 60)
        print("📊 テスト結果サマリー")
        print(f"✅ 成功: {success_count}/{total_tests}")
        print(f"❌ 失敗: {total_tests - success_count}/{total_tests}")
        print(f"📈 成功率: {success_count/total_tests*100:.1f}%")
        
        if success_count == total_tests:
            print("🎉 河川・砂防部門: 全テスト成功！")
        else:
            print("⚠️ 河川・砂防部門: 一部テスト失敗 - 詳細確認が必要")
        
        print("=" * 60)
        
        # 詳細結果出力
        self.save_detailed_results()
        
        return success_count == total_tests
    
    def save_detailed_results(self):
        """詳細テスト結果をファイルに保存"""
        result_data = {
            "test_session": {
                "start_time": self.test_start_time.isoformat(),
                "end_time": datetime.now().isoformat(),
                "target_department": "civil_planning (河川、砂防及び海岸・海洋)",
                "test_purpose": "部門マッピング修正後の動作確認"
            },
            "results": self.test_results
        }
        
        filename = f"river_test_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result_data, f, ensure_ascii=False, indent=2)
        
        print(f"📄 詳細結果: {filename} に保存")

if __name__ == "__main__":
    # テスト実行
    tester = RCCMRiverManualTest()
    success = tester.run_comprehensive_test()
    
    exit(0 if success else 1)