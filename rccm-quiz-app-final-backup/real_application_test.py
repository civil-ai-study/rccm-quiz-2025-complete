#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLAUDE.md準拠 実アプリケーション動作テスト
Flaskアプリケーションを実際に起動してHTTPリクエストでテスト
"""

import os
import sys
import json
import time
import requests
import subprocess
import threading
from datetime import datetime

class RealApplicationTester:
    def __init__(self):
        self.base_url = "http://localhost:5000"
        self.app_process = None
        self.session = requests.Session()
        self.test_results = {
            "start_time": datetime.now().isoformat(),
            "test_type": "real_application",
            "departments": {},
            "errors": [],
            "performance": {}
        }
    
    def start_flask_app(self):
        """Flaskアプリケーションを実際に起動"""
        print("🚀 Flaskアプリケーション起動中...")
        
        # 環境変数設定
        env = os.environ.copy()
        env['FLASK_APP'] = 'app.py'
        env['FLASK_ENV'] = 'development'
        
        try:
            self.app_process = subprocess.Popen(
                ['python3', 'app.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                cwd='/mnt/c/Users/ABC/Desktop/rccm-quiz-app/rccm-quiz-app'
            )
            
            # 起動確認のため少し待機
            time.sleep(10)
            
            # ヘルスチェック
            try:
                response = self.session.get(f"{self.base_url}/", timeout=30)
                if response.status_code == 200:
                    print("✅ Flaskアプリケーション起動成功")
                    return True
                else:
                    print(f"❌ アプリケーション応答異常: {response.status_code}")
                    return False
            except requests.exceptions.RequestException as e:
                print(f"❌ アプリケーション接続失敗: {e}")
                return False
                
        except Exception as e:
            print(f"❌ アプリケーション起動失敗: {e}")
            return False
    
    def stop_flask_app(self):
        """Flaskアプリケーション停止"""
        if self.app_process:
            print("🛑 Flaskアプリケーション停止中...")
            self.app_process.terminate()
            self.app_process.wait()
            print("✅ アプリケーション停止完了")
    
    def test_department_exam_flow(self, dept_name, dept_id, question_type, question_count):
        """実際のHTTPリクエストで部門試験フローをテスト"""
        print(f"\n{'='*80}")
        print(f"🎯 {dept_name}部門 {question_count}問テスト開始")
        print(f"{'='*80}")
        
        start_time = time.time()
        
        try:
            # 1. ホームページアクセス
            print("1. ホームページアクセス...")
            response = self.session.get(f"{self.base_url}/")
            if response.status_code != 200:
                raise Exception(f"ホームページエラー: {response.status_code}")
            print("   ✅ ホームページ正常")
            
            # 2. 部門選択ページアクセス
            print("2. 部門選択ページアクセス...")
            response = self.session.get(f"{self.base_url}/departments")
            if response.status_code != 200:
                raise Exception(f"部門選択ページエラー: {response.status_code}")
            print("   ✅ 部門選択ページ正常")
            
            # 3. 問題種別選択ページアクセス
            print("3. 問題種別選択ページアクセス...")
            response = self.session.get(f"{self.base_url}/question_types?department={dept_id}")
            if response.status_code != 200:
                raise Exception(f"問題種別選択ページエラー: {response.status_code}")
            print("   ✅ 問題種別選択ページ正常")
            
            # 4. 試験開始（実際のPOSTリクエスト）
            print("4. 試験セッション開始...")
            exam_data = {
                'department': dept_id,
                'question_type': question_type,
                'category': 'all',
                'question_count': question_count
            }
            response = self.session.get(f"{self.base_url}/exam", params=exam_data)
            if response.status_code != 200:
                raise Exception(f"試験開始エラー: {response.status_code}")
            print("   ✅ 試験セッション開始成功")
            
            # 5. 各問題への回答処理
            print(f"5. {question_count}問への回答処理...")
            for question_no in range(1, question_count + 1):
                # 問題表示確認
                response = self.session.get(f"{self.base_url}/exam")
                if response.status_code != 200:
                    raise Exception(f"問題{question_no}表示エラー: {response.status_code}")
                
                # HTMLから問題IDを抽出（簡易）
                if 'name="qid"' not in response.text:
                    raise Exception(f"問題{question_no}: 問題ID取得失敗")
                
                # 回答送信（ランダム回答）
                import re
                qid_match = re.search(r'name="qid" value="(\d+)"', response.text)
                if not qid_match:
                    raise Exception(f"問題{question_no}: 問題ID解析失敗")
                
                qid = qid_match.group(1)
                answer_data = {
                    'qid': qid,
                    'answer': ['a', 'b', 'c', 'd'][question_no % 4],
                    'elapsed': '30'
                }
                
                response = self.session.post(f"{self.base_url}/exam", data=answer_data)
                if response.status_code not in [200, 302]:
                    raise Exception(f"問題{question_no}回答エラー: {response.status_code}")
                
                print(f"   問題{question_no}/{question_count}: ✅")
                
                # 進行状況確認のため少し待機
                time.sleep(0.5)
            
            # 6. 結果画面確認
            print("6. 結果画面表示確認...")
            response = self.session.get(f"{self.base_url}/exam")
            if response.status_code != 200:
                raise Exception(f"結果画面エラー: {response.status_code}")
            
            # 結果画面かどうか確認
            if '結果' in response.text or '完了' in response.text or 'score' in response.text.lower():
                print("   ✅ 結果画面正常表示")
            else:
                print("   ⚠️ 結果画面の詳細確認が必要")
            
            elapsed_time = time.time() - start_time
            print(f"\n✅ {dept_name}部門 {question_count}問テスト完了")
            print(f"   実行時間: {elapsed_time:.1f}秒")
            
            return {
                "status": "PASSED",
                "elapsed_time": elapsed_time,
                "questions_completed": question_count
            }
            
        except Exception as e:
            elapsed_time = time.time() - start_time
            print(f"\n❌ {dept_name}部門 {question_count}問テスト失敗")
            print(f"   エラー: {str(e)}")
            print(f"   実行時間: {elapsed_time:.1f}秒")
            
            self.test_results["errors"].append({
                "department": dept_name,
                "question_count": question_count,
                "error": str(e),
                "elapsed_time": elapsed_time
            })
            
            return {
                "status": "FAILED",
                "error": str(e),
                "elapsed_time": elapsed_time
            }
    
    def run_comprehensive_test(self):
        """包括的テスト実行"""
        print("🚀 CLAUDE.md準拠 実アプリケーション動作テスト開始")
        print(f"🕐 開始時刻: {self.test_results['start_time']}")
        
        # Flaskアプリ起動
        if not self.start_flask_app():
            print("❌ アプリケーション起動失敗 - テスト中止")
            return False
        
        try:
            # 1. 基礎科目テスト
            print("\n" + "="*100)
            print("基礎科目(4-1)実動作テスト")
            print("="*100)
            
            basic_results = {}
            for question_count in [10, 20, 30]:
                result = self.test_department_exam_flow("基礎科目", "basic", "basic", question_count)
                basic_results[f"{question_count}問"] = result
                time.sleep(2)  # テスト間隔
            
            self.test_results["departments"]["基礎科目"] = basic_results
            
            # 2. 専門科目12部門テスト
            departments = [
                ("道路", "road", "specialist"),
                ("河川・砂防", "river", "specialist"),
                ("都市計画", "urban", "specialist"),
                ("造園", "landscape", "specialist"),
                ("建設環境", "environment", "specialist"),
                ("鋼構造・コンクリート", "steel_concrete", "specialist"),
                ("土質・基礎", "soil", "specialist"),
                ("施工計画", "construction", "specialist"),
                ("上水道", "water", "specialist"),
                ("森林土木", "forest", "specialist"),
                ("農業土木", "agriculture", "specialist"),
                ("トンネル", "tunnel", "specialist")
            ]
            
            for dept_name, dept_id, question_type in departments:
                print(f"\n" + "="*100)
                print(f"{dept_name}部門 実動作テスト")
                print("="*100)
                
                dept_results = {}
                for question_count in [10, 20, 30]:
                    result = self.test_department_exam_flow(dept_name, dept_id, question_type, question_count)
                    dept_results[f"{question_count}問"] = result
                    time.sleep(2)  # テスト間隔
                
                self.test_results["departments"][dept_name] = dept_results
            
            # 最終結果
            self.generate_final_report()
            
        finally:
            # アプリケーション停止
            self.stop_flask_app()
    
    def generate_final_report(self):
        """最終レポート生成"""
        print("\n" + "="*100)
        print("📊 実アプリケーション動作テスト 最終結果")
        print("="*100)
        
        total_tests = 0
        passed_tests = 0
        total_time = 0
        
        for dept_name, results in self.test_results["departments"].items():
            print(f"\n{dept_name}:")
            for test_type, result in results.items():
                status = result["status"]
                elapsed = result.get("elapsed_time", 0)
                total_time += elapsed
                
                print(f"  - {test_type}: {status} ({elapsed:.1f}秒)")
                total_tests += 1
                if status == "PASSED":
                    passed_tests += 1
        
        success_rate = passed_tests / total_tests * 100 if total_tests > 0 else 0
        
        print(f"\n総合結果:")
        print(f"  - 総テスト数: {total_tests}")
        print(f"  - 成功: {passed_tests}")
        print(f"  - 失敗: {total_tests - passed_tests}")
        print(f"  - 成功率: {success_rate:.1f}%")
        print(f"  - 総実行時間: {total_time:.1f}秒")
        
        # エラーサマリー
        if self.test_results["errors"]:
            print(f"\n🚨 エラー詳細:")
            for error in self.test_results["errors"]:
                print(f"  - {error['department']}: {error['error']}")
        
        self.test_results["summary"] = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "success_rate": success_rate,
            "total_execution_time": total_time
        }
        self.test_results["end_time"] = datetime.now().isoformat()
        
        # 結果保存
        report_file = f"real_app_test_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 詳細レポート保存: {report_file}")
        
        # CLAUDE.md準拠判定
        if success_rate >= 95.0:
            print("\n✅ CLAUDE.md準拠要件満足 - 実アプリケーション動作確認")
            return True
        else:
            print("\n❌ CLAUDE.md準拠要件未満足 - 実アプリケーション動作問題あり")
            return False

def main():
    """メイン実行"""
    tester = RealApplicationTester()
    return tester.run_comprehensive_test()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)