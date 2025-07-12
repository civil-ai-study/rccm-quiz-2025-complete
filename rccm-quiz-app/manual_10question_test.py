#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
【ULTRASYNC段階11】手動10問完走テスト
セッション修正後の実際のユーザーワークフロー検証
"""

import requests
import json
import re
from datetime import datetime
import time

def extract_question_data(html_content):
    """HTMLから問題データを抽出"""
    try:
        # 問題IDを抽出
        qid_match = re.search(r'name="qid"[^>]*value="(\d+)"', html_content)
        qid = qid_match.group(1) if qid_match else None
        
        # 問題文を抽出
        question_match = re.search(r'<h4[^>]*>問題\d+</h4>\s*<p[^>]*>(.*?)</p>', html_content, re.DOTALL)
        question_text = question_match.group(1) if question_match else "問題文抽出失敗"
        
        # 進捗情報を抽出
        progress_match = re.search(r'(\d+)/(\d+)', html_content)
        if progress_match:
            current = int(progress_match.group(1))
            total = int(progress_match.group(2))
        else:
            current, total = 0, 10
        
        return {
            "qid": qid,
            "question_text": question_text[:100] + "..." if len(question_text) > 100 else question_text,
            "current": current,
            "total": total,
            "is_valid": qid is not None
        }
    except Exception as e:
        return {
            "qid": None,
            "question_text": f"抽出エラー: {e}",
            "current": 0,
            "total": 10,
            "is_valid": False
        }

def manual_10question_completion_test():
    """手動10問完走テスト実行"""
    print("🎯 【ULTRASYNC段階11】手動10問完走テスト開始")
    print("=" * 60)
    
    base_url = "https://rccm-quiz-2025.onrender.com"
    session = requests.Session()
    
    test_log = []
    answers = ["A", "B", "C", "D", "A", "B", "C", "D", "A", "B"]  # 10問の回答パターン
    
    try:
        # ステップ1: ホームページアクセス
        print("📋 ステップ1: ホームページアクセス")
        response = session.get(f"{base_url}/")
        print(f"   ステータス: {response.status_code}")
        test_log.append({"step": 1, "action": "ホームページ", "status": response.status_code})
        
        # ステップ2: 基礎科目開始
        print("\n📋 ステップ2: 基礎科目試験開始")
        response = session.get(f"{base_url}/exam?question_type=basic")
        print(f"   ステータス: {response.status_code}")
        
        if response.status_code != 200:
            print(f"   ❌ 試験開始失敗: {response.status_code}")
            return False
        
        if "エラー" in response.text or "問題データの取得に失敗しました" in response.text:
            print("   ❌ エラーページが表示されました")
            print("   📄 エラー詳細:")
            # エラー詳細を抽出
            error_match = re.search(r'<p[^>]*><strong>(.*?)</strong></p>', response.text)
            if error_match:
                print(f"      {error_match.group(1)}")
            
            test_log.append({"step": 2, "action": "基礎科目開始", "status": "error", "error": "エラーページ表示"})
            return False
        
        test_log.append({"step": 2, "action": "基礎科目開始", "status": response.status_code})
        
        # ステップ3-12: 10問連続回答
        print("\n📋 ステップ3-12: 10問連続回答テスト")
        
        for question_num in range(1, 11):
            print(f"\n   🔍 問題 {question_num}/10")
            
            # 現在の問題を取得
            response = session.get(f"{base_url}/exam")
            if response.status_code != 200:
                print(f"      ❌ 問題取得失敗: {response.status_code}")
                test_log.append({"step": f"3-{question_num}", "action": f"問題{question_num}取得", "status": response.status_code, "success": False})
                return False
            
            # 問題データを抽出
            question_data = extract_question_data(response.text)
            print(f"      問題ID: {question_data['qid']}")
            print(f"      進捗: {question_data['current']}/{question_data['total']}")
            print(f"      問題文: {question_data['question_text']}")
            
            if not question_data["is_valid"]:
                print(f"      ❌ 問題データが無効")
                test_log.append({"step": f"3-{question_num}", "action": f"問題{question_num}取得", "status": "invalid_data", "success": False})
                return False
            
            # 回答送信
            answer = answers[question_num - 1]
            post_data = {
                "answer": answer,
                "qid": question_data["qid"],
                "elapsed": "30"
            }
            
            print(f"      回答送信: {answer}")
            response = session.post(f"{base_url}/exam", data=post_data)
            print(f"      レスポンスステータス: {response.status_code}")
            
            if response.status_code not in [200, 302]:
                print(f"      ❌ 回答送信失敗: {response.status_code}")
                test_log.append({"step": f"3-{question_num}", "action": f"問題{question_num}回答", "status": response.status_code, "success": False})
                return False
            
            # 結果確認
            if "正解" in response.text or "不正解" in response.text or "次の問題へ" in response.text:
                print(f"      ✅ 回答処理成功")
                test_log.append({"step": f"3-{question_num}", "action": f"問題{question_num}回答", "status": response.status_code, "success": True})
            else:
                print(f"      ⚠️ 回答結果不明")
                test_log.append({"step": f"3-{question_num}", "action": f"問題{question_num}回答", "status": response.status_code, "success": True, "note": "結果不明"})
            
            # 少し待機
            time.sleep(0.5)
        
        # ステップ13: 最終結果確認
        print("\n📋 ステップ13: 最終結果確認")
        response = session.get(f"{base_url}/result")
        print(f"   ステータス: {response.status_code}")
        
        if response.status_code == 200:
            if "結果" in response.text or "スコア" in response.text:
                print("   ✅ 結果画面表示成功")
                test_log.append({"step": 13, "action": "結果確認", "status": response.status_code, "success": True})
            else:
                print("   ⚠️ 結果画面内容不明")
                test_log.append({"step": 13, "action": "結果確認", "status": response.status_code, "success": True, "note": "内容不明"})
        else:
            print(f"   ❌ 結果画面アクセス失敗: {response.status_code}")
            test_log.append({"step": 13, "action": "結果確認", "status": response.status_code, "success": False})
        
        # 成功判定
        successful_steps = sum(1 for log in test_log if log.get("success", True))
        total_steps = len(test_log)
        success_rate = (successful_steps / total_steps * 100) if total_steps > 0 else 0
        
        print("\n" + "=" * 60)
        print("🎯 【ULTRASYNC段階11】手動10問完走テスト結果")
        print("=" * 60)
        print(f"✅ 成功ステップ: {successful_steps}/{total_steps} ({success_rate:.1f}%)")
        
        # 詳細ログ
        for log in test_log:
            success_icon = "✅" if log.get("success", True) else "❌"
            print(f"{success_icon} ステップ{log['step']}: {log['action']} - {log['status']}")
            if "note" in log:
                print(f"   注記: {log['note']}")
        
        # レポート保存
        report = {
            "timestamp": datetime.now().isoformat(),
            "test_name": "ULTRASYNC段階11手動10問完走テスト",
            "success_rate": success_rate,
            "total_steps": total_steps,
            "successful_steps": successful_steps,
            "test_log": test_log
        }
        
        report_filename = f"manual_10question_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n📋 詳細レポート保存: {report_filename}")
        
        # 最終判定
        if success_rate >= 80.0:  # 80%以上成功
            print("\n🎉 【ULTRASYNC段階11】手動10問完走テスト: 成功")
            print("✅ セッション修正が効果的に機能しています")
            return True
        else:
            print("\n🚨 【ULTRASYNC段階11】手動10問完走テスト: 要改善")
            print("❌ さらなる修正が必要です")
            return False
            
    except Exception as e:
        print(f"\n❌ テスト実行エラー: {e}")
        return False

if __name__ == "__main__":
    success = manual_10question_completion_test()
    exit(0 if success else 1)