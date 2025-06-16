#!/usr/bin/env python3
"""
🚀 RCCM試験アプリ - 最終デプロイテスト
12部門全機能完全テスト・Windows環境対応確認
"""

import requests
import time
import json
import sys
from datetime import datetime
import random

class RCCMFinalTest:
    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = {}
        self.error_count = 0
        
        # RCCM 12部門定義
        self.departments = {
            'road': '道路',
            'civil_planning': '河川、砂防及び海岸・海洋', 
            'tunnel': 'トンネル',
            'urban_planning': '都市計画及び地方計画',
            'landscape': '造園',
            'construction_env': '建設環境',
            'steel_concrete': '鋼構造及びコンクリート',
            'soil_foundation': '土質及び基礎',
            'construction_planning': '施工計画、施工設備及び積算',
            'water_supply': '上水道及び工業用水道',
            'forestry': '森林土木',
            'agriculture': '農業土木'
        }
        
    def log_test(self, test_name, status, details=""):
        """テスト結果ログ"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        status_icon = "✅" if status == "PASS" else "❌"
        print(f"[{timestamp}] {status_icon} {test_name}: {status}")
        if details:
            print(f"    💡 {details}")
        
        self.test_results[test_name] = {
            'status': status,
            'timestamp': timestamp,
            'details': details
        }
        
        if status == "FAIL":
            self.error_count += 1

    def test_homepage(self):
        """ホームページアクセステスト"""
        try:
            response = self.session.get(self.base_url)
            if response.status_code == 200 and "RCCM試験問題集" in response.text:
                self.log_test("ホームページアクセス", "PASS", "正常にアクセス可能")
                return True
            else:
                self.log_test("ホームページアクセス", "FAIL", f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("ホームページアクセス", "FAIL", f"例外: {str(e)}")
            return False

    def test_basic_exam(self):
        """基礎科目テスト"""
        try:
            # 基礎科目開始
            response = self.session.get(f"{self.base_url}/exam?question_type=basic")
            if response.status_code == 200:
                if "問題" in response.text and "選択肢" in response.text:
                    self.log_test("基礎科目問題表示", "PASS", "問題・選択肢正常表示")
                    
                    # 回答テスト
                    answer_data = {
                        'answer': 'A',
                        'question_id': '1'  # 仮のID
                    }
                    answer_response = self.session.post(f"{self.base_url}/exam", data=answer_data)
                    if answer_response.status_code == 200:
                        self.log_test("基礎科目回答処理", "PASS", "回答正常処理")
                        return True
                    else:
                        self.log_test("基礎科目回答処理", "FAIL", f"Status: {answer_response.status_code}")
                        return False
                else:
                    self.log_test("基礎科目問題表示", "FAIL", "問題または選択肢が表示されない")
                    return False
            else:
                self.log_test("基礎科目アクセス", "FAIL", f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("基礎科目テスト", "FAIL", f"例外: {str(e)}")
            return False

    def test_department_exam(self, dept_key, dept_name):
        """部門別専門科目テスト"""
        try:
            # 部門学習ページアクセス
            response = self.session.get(f"{self.base_url}/department_study/{dept_key}")
            if response.status_code == 200 and dept_name in response.text:
                self.log_test(f"{dept_name}部門ページ", "PASS", "正常アクセス")
                
                # 専門科目問題開始
                exam_response = self.session.get(f"{self.base_url}/exam?department={dept_key}&type=specialist")
                if exam_response.status_code == 200:
                    if "問題" in exam_response.text:
                        self.log_test(f"{dept_name}専門科目", "PASS", "問題正常表示")
                        return True
                    else:
                        self.log_test(f"{dept_name}専門科目", "FAIL", "問題表示エラー")
                        return False
                else:
                    self.log_test(f"{dept_name}専門科目", "FAIL", f"Status: {exam_response.status_code}")
                    return False
            else:
                self.log_test(f"{dept_name}部門ページ", "FAIL", f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test(f"{dept_name}部門テスト", "FAIL", f"例外: {str(e)}")
            return False

    def test_review_function(self):
        """復習機能テスト"""
        try:
            # 復習リストアクセス
            response = self.session.get(f"{self.base_url}/review")
            if response.status_code == 200:
                self.log_test("復習リストアクセス", "PASS", "正常アクセス")
                
                # 復習問題実行テスト
                review_exam = self.session.get(f"{self.base_url}/exam/review")
                if review_exam.status_code == 200:
                    self.log_test("復習問題実行", "PASS", "正常実行")
                    return True
                else:
                    # 復習リストが空の場合は正常
                    if "復習リストが空" in review_exam.text:
                        self.log_test("復習問題実行", "PASS", "復習リスト空（正常）")
                        return True
                    else:
                        self.log_test("復習問題実行", "FAIL", f"Status: {review_exam.status_code}")
                        return False
            else:
                self.log_test("復習リストアクセス", "FAIL", f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("復習機能テスト", "FAIL", f"例外: {str(e)}")
            return False

    def test_analytics(self):
        """解答結果分析テスト"""
        try:
            response = self.session.get(f"{self.base_url}/statistics")
            if response.status_code == 200:
                if "解答結果分析" in response.text or "統計" in response.text:
                    self.log_test("解答結果分析", "PASS", "正常表示")
                    return True
                else:
                    self.log_test("解答結果分析", "FAIL", "分析画面表示エラー")
                    return False
            else:
                self.log_test("解答結果分析", "FAIL", f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("解答結果分析テスト", "FAIL", f"例外: {str(e)}")
            return False

    def test_help_page(self):
        """ヘルプページテスト"""
        try:
            response = self.session.get(f"{self.base_url}/help")
            if response.status_code == 200 and "ヘルプ" in response.text:
                self.log_test("ヘルプページ", "PASS", "正常表示")
                return True
            else:
                self.log_test("ヘルプページ", "FAIL", f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("ヘルプページテスト", "FAIL", f"例外: {str(e)}")
            return False

    def test_categories_page(self):
        """部門別ページテスト"""
        try:
            response = self.session.get(f"{self.base_url}/categories")
            if response.status_code == 200:
                self.log_test("部門別ページ", "PASS", "正常アクセス")
                return True
            else:
                self.log_test("部門別ページ", "FAIL", f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("部門別ページテスト", "FAIL", f"例外: {str(e)}")
            return False

    def run_comprehensive_test(self):
        """包括的テスト実行"""
        print("🚀 RCCM試験アプリ - 最終デプロイテスト開始")
        print("=" * 60)
        
        start_time = time.time()
        
        # 1. ホームページテスト
        self.test_homepage()
        
        # 2. 基礎科目テスト
        self.test_basic_exam()
        
        # 3. 12部門全テスト
        print("\n📚 12部門専門科目テスト開始...")
        for dept_key, dept_name in self.departments.items():
            self.test_department_exam(dept_key, dept_name)
            time.sleep(0.5)  # サーバー負荷軽減
        
        # 4. 復習機能テスト
        self.test_review_function()
        
        # 5. 解答結果分析テスト
        self.test_analytics()
        
        # 6. ヘルプページテスト
        self.test_help_page()
        
        # 7. 部門別ページテスト
        self.test_categories_page()
        
        # テスト結果集計
        end_time = time.time()
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result['status'] == 'PASS')
        
        print("\n" + "=" * 60)
        print("🎯 最終デプロイテスト結果")
        print("=" * 60)
        print(f"⏱️  実行時間: {end_time - start_time:.2f}秒")
        print(f"📊 テスト総数: {total_tests}")
        print(f"✅ 成功: {passed_tests}")
        print(f"❌ 失敗: {self.error_count}")
        print(f"📈 成功率: {(passed_tests/total_tests)*100:.1f}%")
        
        if self.error_count == 0:
            print("\n🎉 全機能テスト完全成功！デプロイ準備完了！")
            return True
        else:
            print(f"\n⚠️  {self.error_count}個のエラーが検出されました。修正が必要です。")
            print("\n❌ 失敗テスト詳細:")
            for test_name, result in self.test_results.items():
                if result['status'] == 'FAIL':
                    print(f"  • {test_name}: {result['details']}")
            return False

if __name__ == "__main__":
    print("🔧 サーバー起動確認中...")
    time.sleep(2)  # サーバー安定化待機
    
    tester = RCCMFinalTest()
    success = tester.run_comprehensive_test()
    
    if success:
        print("\n✅ 最終デプロイテスト完了 - 本番リリース可能")
        sys.exit(0)
    else:
        print("\n❌ テスト失敗 - 修正後再テスト要")
        sys.exit(1)