#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 RCCM Quiz App - Direct Flask Test Client Testing
===================================================
This script tests the application directly using Flask's test client,
ensuring comprehensive coverage without requiring a running server.

✅ Tests WITHOUT modifying any files
✅ Tests using Flask's built-in test client
✅ Provides detailed error diagnostics
✅ Follows CLAUDE.md testing requirements

Author: Claude Code
Date: 2025-07-03
"""

import sys
import os
import json
import time
import traceback
from datetime import datetime, timezone
from typing import Dict, List, Tuple, Optional, Any

# Add the app directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import app
    from config import RCCMConfig, ExamConfig
except ImportError as e:
    print(f"❌ Failed to import app modules: {e}")
    print("Make sure you're running this script from the RCCM quiz app directory")
    sys.exit(1)


class DirectFlaskTester:
    """Flask Test Client を使用した直接テスト"""
    
    def __init__(self):
        self.app = app
        self.client = None
        self.test_start_time = datetime.now(timezone.utc)
        self.test_results = []
        
        # テスト設定
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False  # テスト時はCSRF無効化
        
        # 部門定義（config.pyから取得）
        self.departments = RCCMConfig.DEPARTMENTS
        self.question_counts = [10, 20, 30]
        
    def setup_test_client(self):
        """テストクライアントのセットアップ"""
        self.client = self.app.test_client()
        self.client.testing = True
        
    def log(self, message: str, level: str = "INFO"):
        """統一ログ出力"""
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        icon = {
            "INFO": "ℹ️",
            "SUCCESS": "✅",
            "FAILED": "❌",
            "WARNING": "⚠️",
            "ERROR": "🚨"
        }.get(level, "📝")
        
        print(f"[{timestamp}] {icon} {message}")
        
    def test_home_page(self) -> bool:
        """ホームページアクセステスト"""
        self.log("ホームページアクセステスト開始")
        
        try:
            response = self.client.get('/')
            if response.status_code == 200:
                self.log("ホームページアクセス成功", "SUCCESS")
                return True
            else:
                self.log(f"ホームページアクセス失敗: Status {response.status_code}", "FAILED")
                return False
        except Exception as e:
            self.log(f"ホームページテスト中の例外: {str(e)}", "ERROR")
            return False
            
    def test_department_quiz_flow(self, dept_key: str, dept_info: Dict, question_count: int) -> Dict[str, Any]:
        """部門別クイズフローテスト"""
        test_name = f"{dept_info['name']} - {question_count}問テスト"
        
        result = {
            "test_name": test_name,
            "department": dept_key,
            "question_count": question_count,
            "status": "FAILED",
            "stages": {
                "initialization": False,
                "question_delivery": False,
                "answer_processing": False,
                "completion": False
            },
            "errors": [],
            "questions_answered": 0,
            "duration_seconds": 0
        }
        
        start_time = time.time()
        
        try:
            self.log(f"\n{'='*50}")
            self.log(f"{dept_info.get('icon', '📚')} {test_name} 開始")
            
            # 1. セッション初期化
            with self.client.session_transaction() as sess:
                sess.clear()  # セッションクリア
                
            # 2. クイズ開始
            if dept_info.get('category', 'specialist') == 'basic':
                # 基礎科目
                start_data = {
                    'category': 'basic',
                    'questions_per_session': str(question_count)
                }
            else:
                # 専門科目
                start_data = {
                    'category': 'specialist',
                    'department': dept_key,
                    'questions_per_session': str(question_count)
                }
                
            response = self.client.post('/start_quiz', data=start_data, follow_redirects=True)
            
            if response.status_code == 200:
                result["stages"]["initialization"] = True
                self.log("✅ セッション初期化成功", "SUCCESS")
            else:
                result["errors"].append(f"初期化失敗: Status {response.status_code}")
                self.log(f"❌ 初期化失敗: Status {response.status_code}", "FAILED")
                return result
                
            # 3. 問題回答ループ
            questions_answered = 0
            max_attempts = question_count + 5
            
            for attempt in range(max_attempts):
                # 現在のクイズページ取得
                response = self.client.get('/quiz')
                
                if response.status_code != 200:
                    result["errors"].append(f"問題取得失敗: Status {response.status_code}")
                    break
                    
                page_data = response.data.decode('utf-8')
                
                # エラーチェック
                if "エラー" in page_data and "問題がありません" not in page_data:
                    result["errors"].append("エラーページ検出")
                    break
                    
                # 結果画面チェック
                if any(keyword in page_data for keyword in ["結果", "スコア", "正解数"]):
                    if questions_answered >= question_count:
                        result["stages"]["completion"] = True
                        self.log(f"✅ {questions_answered}問完了 - 正常終了", "SUCCESS")
                        break
                    else:
                        result["errors"].append(f"早期終了: {questions_answered}問で終了")
                        break
                        
                # 問題画面確認
                if "問題" not in page_data:
                    result["errors"].append("問題画面未検出")
                    break
                    
                # 回答送信
                answer_choice = ["a", "b", "c", "d"][questions_answered % 4]
                response = self.client.post('/quiz', data={'answer': answer_choice})
                
                if response.status_code in [200, 302]:
                    questions_answered += 1
                    result["questions_answered"] = questions_answered
                    
                    if questions_answered == 1:
                        result["stages"]["question_delivery"] = True
                        
                    if questions_answered > 1:
                        result["stages"]["answer_processing"] = True
                        
                    # 進捗ログ
                    if questions_answered % 5 == 0:
                        self.log(f"  進捗: {questions_answered}/{question_count}問", "INFO")
                else:
                    result["errors"].append(f"回答送信失敗: Status {response.status_code}")
                    break
                    
            # 成功判定
            if (result["stages"]["initialization"] and 
                result["stages"]["question_delivery"] and
                result["stages"]["answer_processing"] and
                result["questions_answered"] >= question_count):
                result["status"] = "SUCCESS"
                self.log(f"✅ {test_name} 完了", "SUCCESS")
            else:
                self.log(f"❌ {test_name} 失敗", "FAILED")
                
        except Exception as e:
            result["errors"].append(f"例外発生: {str(e)}")
            self.log(f"🚨 テスト中の例外: {str(e)}", "ERROR")
            traceback.print_exc()
            
        finally:
            result["duration_seconds"] = round(time.time() - start_time, 2)
            
        return result
        
    def test_api_endpoints(self) -> Dict[str, Any]:
        """APIエンドポイントテスト"""
        self.log("\n📡 APIエンドポイントテスト開始")
        
        api_results = {
            "questions_count": {"status": "FAILED", "details": ""},
            "cache_clear": {"status": "FAILED", "details": ""},
            "force_reset": {"status": "FAILED", "details": ""}
        }
        
        # 1. 問題数カウントAPI
        try:
            response = self.client.get('/api/questions/count?department=road&category=specialist')
            if response.status_code == 200:
                data = response.get_json()
                if 'count' in data:
                    api_results["questions_count"]["status"] = "SUCCESS"
                    api_results["questions_count"]["details"] = f"道路部門: {data['count']}問"
                    self.log(f"✅ 問題数API正常: {data['count']}問", "SUCCESS")
        except Exception as e:
            api_results["questions_count"]["details"] = str(e)
            
        # 2. キャッシュクリアAPI
        try:
            response = self.client.post('/api/cache/clear')
            if response.status_code == 200:
                api_results["cache_clear"]["status"] = "SUCCESS"
                api_results["cache_clear"]["details"] = "キャッシュクリア成功"
                self.log("✅ キャッシュクリアAPI正常", "SUCCESS")
        except Exception as e:
            api_results["cache_clear"]["details"] = str(e)
            
        # 3. 強制リセットAPI
        try:
            response = self.client.get('/force_reset')
            if response.status_code in [200, 302]:
                api_results["force_reset"]["status"] = "SUCCESS"
                api_results["force_reset"]["details"] = "強制リセット成功"
                self.log("✅ 強制リセットAPI正常", "SUCCESS")
        except Exception as e:
            api_results["force_reset"]["details"] = str(e)
            
        return api_results
        
    def run_comprehensive_test(self):
        """包括的テスト実行"""
        self.log("\n" + "="*70)
        self.log("🧪 Flask Test Client による包括的テスト開始")
        self.log("📋 テスト内容: 13部門 × 3問題数 + API テスト")
        self.log("="*70 + "\n")
        
        # テストクライアント初期化
        self.setup_test_client()
        
        # 基本テスト
        if not self.test_home_page():
            self.log("🚨 基本的なアクセステストに失敗しました", "ERROR")
            return
            
        # APIテスト
        api_results = self.test_api_endpoints()
        
        # 統計初期化
        total_tests = len(self.departments) * len(self.question_counts)
        successful_tests = 0
        failed_tests = 0
        department_results = {}
        
        # 部門ごとのテスト
        for dept_key, dept_info in self.departments.items():
            dept_results = {}
            
            for question_count in self.question_counts:
                result = self.test_department_quiz_flow(dept_key, dept_info, question_count)
                dept_results[str(question_count)] = result
                
                if result["status"] == "SUCCESS":
                    successful_tests += 1
                else:
                    failed_tests += 1
                    
                # サーバー負荷軽減
                time.sleep(0.5)
                
            department_results[dept_key] = dept_results
            
        # 最終レポート生成
        self._generate_final_report(successful_tests, failed_tests, total_tests, 
                                   department_results, api_results)
        
    def _generate_final_report(self, successful: int, failed: int, total: int,
                              dept_results: Dict, api_results: Dict):
        """最終レポート生成"""
        duration = (datetime.now(timezone.utc) - self.test_start_time).total_seconds()
        
        print("\n" + "="*70)
        print("📊 テスト結果サマリー")
        print("="*70)
        print(f"実行時間: {duration:.1f}秒")
        print(f"総テスト数: {total}")
        print(f"成功: {successful} ({successful/total*100:.1f}%)")
        print(f"失敗: {failed} ({failed/total*100:.1f}%)")
        
        print("\n📡 API テスト結果:")
        for api_name, result in api_results.items():
            status_icon = "✅" if result["status"] == "SUCCESS" else "❌"
            print(f"  {status_icon} {api_name}: {result['details']}")
            
        print("\n🏢 部門別結果:")
        for dept_key, dept_info in self.departments.items():
            results = dept_results.get(dept_key, {})
            dept_name = dept_info['name']
            
            successes = sum(1 for r in results.values() if r["status"] == "SUCCESS")
            total_dept = len(self.question_counts)
            
            print(f"\n{dept_info.get('icon', '📚')} {dept_name}:")
            for q_count in self.question_counts:
                result = results.get(str(q_count))
                if result:
                    status_icon = "✅" if result["status"] == "SUCCESS" else "❌"
                    print(f"  {status_icon} {q_count}問: {result['status']}", end="")
                    if result["errors"]:
                        print(f" - {result['errors'][0]}")
                    else:
                        print(f" - {result['questions_answered']}問完了")
                        
        print("\n" + "="*70)
        print(f"✅ テスト完了: {'PASS' if failed == 0 else 'FAIL' if failed > total/2 else 'PARTIAL'}")
        print("="*70)


def main():
    """メイン実行関数"""
    print("""
╔════════════════════════════════════════════════════════════╗
║   🧪 RCCM Quiz App - Direct Flask Test Client Testing      ║
║                                                            ║
║  This test runs WITHOUT requiring a running server.        ║
║  It tests the app directly using Flask's test client.     ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    try:
        tester = DirectFlaskTester()
        tester.run_comprehensive_test()
    except KeyboardInterrupt:
        print("\n\n⚠️  テストが中断されました。")
    except Exception as e:
        print(f"\n\n🚨 予期しないエラー: {str(e)}")
        traceback.print_exc()


if __name__ == "__main__":
    main()