#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 RCCM試験アプリ - 全12部門包括的手動テストスクリプト
CLAUDE.md準拠：12部門 × 3問題数（10/20/30問）= 36テストケース完全実行

実行方法: python3 comprehensive_12_departments_test.py
"""

import requests
import json
import time
from datetime import datetime
import sys

class RCCM12DepartmentsComprehensiveTest:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        self.test_start_time = datetime.now()
        
        # 12部門定義（CLAUDE.md準拠）
        self.departments = {
            "road": {"name": "道路部門", "category": "道路"},
            "civil_planning": {"name": "河川・砂防部門", "category": "河川、砂防及び海岸・海洋"},
            "urban_planning": {"name": "都市計画部門", "category": "都市計画及び地方計画"},
            "landscape": {"name": "造園部門", "category": "造園"},
            "construction_env": {"name": "建設環境部門", "category": "建設環境"},
            "steel_concrete": {"name": "鋼構造・コンクリート部門", "category": "鋼構造及びコンクリート"},
            "soil_foundation": {"name": "土質・基礎部門", "category": "土質及び基礎"},
            "construction_planning": {"name": "施工計画部門", "category": "施工計画、施工設備及び積算"},
            "water_supply": {"name": "上水道部門", "category": "上水道及び工業用水道"},
            "forestry": {"name": "森林土木部門", "category": "森林土木"},
            "agriculture": {"name": "農業土木部門", "category": "農業土木"},
            "tunnel": {"name": "トンネル部門", "category": "トンネル"}
        }
        
        # 3段階の問題数テスト
        self.question_counts = [10, 20, 30]
        
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
    
    def test_department_question_availability(self, dept_key, dept_info):
        """部門の問題データ可用性テスト"""
        test_name = f"{dept_info['name']}問題データ可用性確認"
        
        try:
            # APIエンドポイントで問題数確認
            api_url = f"{self.base_url}/api/questions/count"
            params = {"department": dept_key, "category": "specialist"}
            
            response = self.session.get(api_url, params=params)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    question_count = data.get("count", 0)
                    
                    if question_count >= 30:
                        self.log_result(test_name, "SUCCESS", f"十分な問題数: {question_count}問（30問テスト可能）")
                        return question_count
                    elif question_count >= 20:
                        self.log_result(test_name, "SUCCESS", f"中程度問題数: {question_count}問（20問まで可能）", "30問テストは不可")
                        return question_count
                    elif question_count >= 10:
                        self.log_result(test_name, "SUCCESS", f"最小問題数: {question_count}問（10問のみ可能）", "20/30問テストは不可")
                        return question_count
                    else:
                        self.log_result(test_name, "FAILED", f"問題数不足: {question_count}問", "テスト実行不可")
                        return 0
                        
                except json.JSONDecodeError:
                    self.log_result(test_name, "FAILED", "APIレスポンス解析失敗", "JSONパースエラー")
                    return 0
            else:
                self.log_result(test_name, "FAILED", f"API呼び出し失敗", f"Status: {response.status_code}")
                return 0
                
        except Exception as e:
            self.log_result(test_name, "FAILED", "例外発生", str(e))
            return 0
    
    def test_department_session_complete(self, dept_key, dept_info, question_count_target):
        """部門別セッション完走テスト"""
        test_name = f"{dept_info['name']}{question_count_target}問完走テスト"
        
        try:
            # 1. セッション初期化
            self.reset_session()
            
            # 2. クイズ開始
            quiz_start_url = f"{self.base_url}/start_quiz"
            data = {
                "category": "specialist",
                "department": dept_key,
                "questions_per_session": question_count_target
            }
            
            response = self.session.post(quiz_start_url, data=data)
            
            if response.status_code not in [200, 302]:
                self.log_result(test_name, "FAILED", "セッション初期化失敗", f"Status: {response.status_code}")
                return False
            
            # 3. 問題完走ループ
            question_count = 0
            max_attempts = question_count_target + 5  # 安全マージン
            
            for attempt in range(max_attempts):
                # 現在の問題取得
                quiz_url = f"{self.base_url}/quiz"
                response = self.session.get(quiz_url)
                
                if response.status_code != 200:
                    self.log_result(test_name, "FAILED", f"問題取得失敗（{attempt+1}回目）", f"Status: {response.status_code}")
                    return False
                
                # エラー画面チェック
                if "エラー" in response.text or "error" in response.text.lower():
                    self.log_result(test_name, "FAILED", f"{question_count+1}問目でエラー発生", "エラー画面表示")
                    return False
                
                # 結果画面チェック
                if "結果" in response.text or "スコア" in response.text or "点数" in response.text:
                    if question_count >= question_count_target:
                        self.log_result(test_name, "SUCCESS", f"{question_count_target}問完走成功（実際: {question_count}問）")
                        return True
                    else:
                        self.log_result(test_name, "FAILED", f"予期しない早期終了", f"{question_count}問で終了（目標: {question_count_target}問）")
                        return False
                
                # 問題画面であることを確認
                if "問題" not in response.text:
                    self.log_result(test_name, "FAILED", f"問題画面未表示（{attempt+1}回目）", "予期しないページ内容")
                    return False
                
                # 回答送信（選択肢aを選択）
                answer_data = {"answer": "a"}
                response = self.session.post(quiz_url, data=answer_data)
                
                if response.status_code not in [200, 302]:
                    self.log_result(test_name, "FAILED", f"回答送信失敗（{question_count+1}問目）", f"Status: {response.status_code}")
                    return False
                
                question_count += 1
                
                # 進捗確認
                if question_count % 5 == 0:
                    print(f"    進捗: {question_count}/{question_count_target}問完了")
                
                time.sleep(0.3)  # サーバー負荷軽減
            
            # 最大試行回数に達した場合
            self.log_result(test_name, "FAILED", "最大試行回数超過", f"目標{question_count_target}問に到達せず")
            return False
                
        except Exception as e:
            self.log_result(test_name, "FAILED", "例外発生", str(e))
            return False
    
    def reset_session(self):
        """セッションリセット"""
        try:
            reset_url = f"{self.base_url}/force_reset"
            self.session.get(reset_url)
            time.sleep(1)
        except:
            pass  # リセット失敗は無視
    
    def test_single_department_all_counts(self, dept_key, dept_info):
        """単一部門の全問題数テスト"""
        print(f"\n{'='*50}")
        print(f"🎯 {dept_info['name']} 包括テスト開始")
        print(f"📊 予定テスト: 10問/20問/30問")
        print(f"{'='*50}")
        
        # 1. 問題可用性確認
        available_questions = self.test_department_question_availability(dept_key, dept_info)
        
        if available_questions == 0:
            print(f"❌ {dept_info['name']}: 問題データなし - スキップ")
            return {"dept": dept_info['name'], "10q": False, "20q": False, "30q": False}
        
        # 2. 各問題数でのテスト実行
        results = {"dept": dept_info['name']}
        
        for count in self.question_counts:
            if available_questions >= count:
                print(f"\n📝 {count}問テスト実行中...")
                success = self.test_department_session_complete(dept_key, dept_info, count)
                results[f"{count}q"] = success
                
                if success:
                    print(f"✅ {dept_info['name']} {count}問: 成功")
                else:
                    print(f"❌ {dept_info['name']} {count}問: 失敗")
                
                time.sleep(2)  # テスト間隔
            else:
                print(f"⏭️ {count}問テスト: スキップ（問題数不足: {available_questions}問）")
                results[f"{count}q"] = "SKIPPED"
        
        return results
    
    def run_comprehensive_test(self):
        """12部門包括的テスト実行"""
        print("=" * 80)
        print("🧪 RCCM試験アプリ - 全12部門包括的手動テスト")
        print(f"📅 実行開始時刻: {self.test_start_time}")
        print(f"🎯 テスト範囲: 12部門 × 3問題数 = 36テストケース")
        print("=" * 80)
        
        all_results = []
        total_tests = 0
        successful_tests = 0
        
        # 各部門でテスト実行
        for i, (dept_key, dept_info) in enumerate(self.departments.items(), 1):
            print(f"\n🏢 [{i}/12] {dept_info['name']} テスト開始")
            
            dept_results = self.test_single_department_all_counts(dept_key, dept_info)
            all_results.append(dept_results)
            
            # 統計更新
            for count in self.question_counts:
                result = dept_results.get(f"{count}q", False)
                total_tests += 1
                if result is True:
                    successful_tests += 1
        
        # 最終結果サマリー
        self.print_final_summary(all_results, successful_tests, total_tests)
        
        # 詳細結果保存
        self.save_comprehensive_results(all_results)
        
        return successful_tests == total_tests
    
    def print_final_summary(self, all_results, successful_tests, total_tests):
        """最終結果サマリー表示"""
        print("\n" + "=" * 80)
        print("📊 全12部門包括テスト結果サマリー")
        print("=" * 80)
        
        print(f"✅ 成功テスト: {successful_tests}/{total_tests}")
        print(f"❌ 失敗テスト: {total_tests - successful_tests}/{total_tests}")
        print(f"📈 成功率: {successful_tests/total_tests*100:.1f}%")
        
        print("\n📋 部門別詳細結果:")
        print("-" * 60)
        
        for result in all_results:
            dept = result["dept"]
            q10 = "✅" if result.get("10q") is True else "❌" if result.get("10q") is False else "⏭️"
            q20 = "✅" if result.get("20q") is True else "❌" if result.get("20q") is False else "⏭️"
            q30 = "✅" if result.get("30q") is True else "❌" if result.get("30q") is False else "⏭️"
            
            print(f"{dept:20} | 10問:{q10} 20問:{q20} 30問:{q30}")
        
        print("-" * 60)
        
        if successful_tests == total_tests:
            print("🎉 全テスト成功！RCCM試験アプリは正常に動作しています。")
        elif successful_tests >= total_tests * 0.9:
            print("✅ ほぼ成功！軽微な問題があります。")
        else:
            print("⚠️ 重要な問題が検出されました。詳細確認が必要です。")
        
        print("=" * 80)
    
    def save_comprehensive_results(self, all_results):
        """包括的テスト結果をファイルに保存"""
        result_data = {
            "test_session": {
                "start_time": self.test_start_time.isoformat(),
                "end_time": datetime.now().isoformat(),
                "test_scope": "12部門 × 3問題数 = 36テストケース",
                "test_purpose": "4-2選択科目修正後の全部門動作確認"
            },
            "summary": all_results,
            "detailed_results": self.test_results
        }
        
        filename = f"comprehensive_12_dept_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result_data, f, ensure_ascii=False, indent=2)
        
        print(f"📄 詳細結果: {filename} に保存")

if __name__ == "__main__":
    # テスト実行
    print("🚀 RCCM試験アプリ包括的テスト開始")
    print("⚠️ このテストには時間がかかります（推定: 30-60分）")
    
    response = input("続行しますか？ [y/N]: ")
    if response.lower() != 'y':
        print("テスト中止")
        sys.exit(0)
    
    tester = RCCM12DepartmentsComprehensiveTest()
    success = tester.run_comprehensive_test()
    
    exit(0 if success else 1)