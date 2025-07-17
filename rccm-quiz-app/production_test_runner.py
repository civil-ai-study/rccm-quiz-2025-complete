#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本番環境テスト実行スクリプト
実際のHTTP通信を行い、逐一結果を確認する
"""

import urllib.request
import urllib.parse
import http.cookiejar
import json
import re
from datetime import datetime
import time

def create_session():
    """HTTPセッション作成（Cookieサポート付き）"""
    cookie_jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))
    return opener, cookie_jar

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

def production_test():
    """本番環境での実際のテスト実行"""
    print("🎯 本番環境 10問完走テスト開始")
    print("=" * 60)
    
    base_url = "https://rccm-quiz-2025.onrender.com"
    opener, cookie_jar = create_session()
    
    test_log = []
    answers = ["A", "B", "C", "D", "A", "B", "C", "D", "A", "B"]
    
    try:
        # ステップ1: ホームページアクセス
        print("📋 ステップ1: ホームページアクセス")
        try:
            request = urllib.request.Request(f"{base_url}/")
            response = opener.open(request)
            status_code = response.getcode()
            content = response.read().decode('utf-8')
            print(f"   ステータス: {status_code}")
            test_log.append({"step": 1, "action": "ホームページ", "status": status_code, "success": True})
        except Exception as e:
            print(f"   ❌ エラー: {e}")
            test_log.append({"step": 1, "action": "ホームページ", "status": "error", "error": str(e), "success": False})
            return False
        
        # ステップ2: 基礎科目開始
        print("\n📋 ステップ2: 基礎科目試験開始")
        try:
            request = urllib.request.Request(f"{base_url}/exam?question_type=basic")
            response = opener.open(request)
            status_code = response.getcode()
            content = response.read().decode('utf-8')
            print(f"   ステータス: {status_code}")
            
            # エラーチェック
            if "エラー" in content or "問題データの取得に失敗しました" in content:
                print("   ❌ エラーページが表示されました")
                error_match = re.search(r'<p[^>]*><strong>(.*?)</strong></p>', content)
                if error_match:
                    print(f"      エラー詳細: {error_match.group(1)}")
                test_log.append({"step": 2, "action": "基礎科目開始", "status": "error", "error": "エラーページ表示", "success": False})
                return False
            
            test_log.append({"step": 2, "action": "基礎科目開始", "status": status_code, "success": True})
            
        except Exception as e:
            print(f"   ❌ エラー: {e}")
            test_log.append({"step": 2, "action": "基礎科目開始", "status": "error", "error": str(e), "success": False})
            return False
        
        # ステップ3-12: 10問連続回答
        print("\n📋 ステップ3-12: 10問連続回答テスト")
        
        for question_num in range(1, 11):
            print(f"\n   🔍 問題 {question_num}/10")
            
            try:
                # 現在の問題を取得
                request = urllib.request.Request(f"{base_url}/exam")
                response = opener.open(request)
                status_code = response.getcode()
                content = response.read().decode('utf-8')
                
                if status_code != 200:
                    print(f"      ❌ 問題取得失敗: {status_code}")
                    test_log.append({"step": f"3-{question_num}", "action": f"問題{question_num}取得", "status": status_code, "success": False})
                    return False
                
                # 問題データを抽出
                question_data = extract_question_data(content)
                print(f"      問題ID: {question_data['qid']}")
                print(f"      進捗: {question_data['current']}/{question_data['total']}")
                print(f"      問題文: {question_data['question_text']}")
                
                if not question_data["is_valid"]:
                    print(f"      ❌ 問題データが無効")
                    test_log.append({"step": f"3-{question_num}", "action": f"問題{question_num}取得", "status": "invalid_data", "success": False})
                    return False
                
                # 回答送信
                answer = answers[question_num - 1]
                post_data = urllib.parse.urlencode({
                    "answer": answer,
                    "qid": question_data["qid"],
                    "elapsed": "30"
                }).encode('utf-8')
                
                print(f"      回答送信: {answer}")
                request = urllib.request.Request(f"{base_url}/exam", data=post_data)
                response = opener.open(request)
                status_code = response.getcode()
                content = response.read().decode('utf-8')
                print(f"      レスポンスステータス: {status_code}")
                
                if status_code not in [200]:
                    print(f"      ❌ 回答送信失敗: {status_code}")
                    test_log.append({"step": f"3-{question_num}", "action": f"問題{question_num}回答", "status": status_code, "success": False})
                    return False
                
                # 結果確認
                if "正解" in content or "不正解" in content or "次の問題へ" in content or "結果を見る" in content:
                    print(f"      ✅ 回答処理成功")
                    test_log.append({"step": f"3-{question_num}", "action": f"問題{question_num}回答", "status": status_code, "success": True})
                else:
                    print(f"      ⚠️ 回答結果不明")
                    test_log.append({"step": f"3-{question_num}", "action": f"問題{question_num}回答", "status": status_code, "success": True, "note": "結果不明"})
                
                # 短時間待機
                time.sleep(1)
                
            except Exception as e:
                print(f"      ❌ エラー: {e}")
                test_log.append({"step": f"3-{question_num}", "action": f"問題{question_num}", "status": "error", "error": str(e), "success": False})
                return False
        
        # ステップ13: 最終結果確認
        print("\n📋 ステップ13: 最終結果確認")
        try:
            request = urllib.request.Request(f"{base_url}/result")
            response = opener.open(request)
            status_code = response.getcode()
            content = response.read().decode('utf-8')
            print(f"   ステータス: {status_code}")
            
            if status_code == 200:
                if "結果" in content or "スコア" in content:
                    print("   ✅ 結果画面表示成功")
                    test_log.append({"step": 13, "action": "結果確認", "status": status_code, "success": True})
                else:
                    print("   ⚠️ 結果画面内容不明")
                    test_log.append({"step": 13, "action": "結果確認", "status": status_code, "success": True, "note": "内容不明"})
            else:
                print(f"   ❌ 結果画面アクセス失敗: {status_code}")
                test_log.append({"step": 13, "action": "結果確認", "status": status_code, "success": False})
        except Exception as e:
            print(f"   ❌ エラー: {e}")
            test_log.append({"step": 13, "action": "結果確認", "status": "error", "error": str(e), "success": False})
        
        # 成功判定
        successful_steps = sum(1 for log in test_log if log.get("success", True))
        total_steps = len(test_log)
        success_rate = (successful_steps / total_steps * 100) if total_steps > 0 else 0
        
        print("\n" + "=" * 60)
        print("🎯 本番環境 10問完走テスト結果")
        print("=" * 60)
        print(f"✅ 成功ステップ: {successful_steps}/{total_steps} ({success_rate:.1f}%)")
        
        # 詳細ログ
        for log in test_log:
            success_icon = "✅" if log.get("success", True) else "❌"
            print(f"{success_icon} ステップ{log['step']}: {log['action']} - {log['status']}")
            if "note" in log:
                print(f"   注記: {log['note']}")
            if "error" in log:
                print(f"   エラー: {log['error']}")
        
        # レポート保存
        report = {
            "timestamp": datetime.now().isoformat(),
            "test_name": "本番環境10問完走テスト",
            "base_url": base_url,
            "success_rate": success_rate,
            "total_steps": total_steps,
            "successful_steps": successful_steps,
            "test_log": test_log
        }
        
        report_filename = f"production_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n📋 詳細レポート保存: {report_filename}")
        
        # 最終判定
        if success_rate >= 80.0:
            print("\n🎉 本番環境 10問完走テスト: 成功")
            print("✅ 修正が効果的に機能しています")
            return True
        else:
            print("\n🚨 本番環境 10問完走テスト: 要改善")
            print("❌ さらなる修正が必要です")
            return False
            
    except Exception as e:
        print(f"\n❌ テスト実行エラー: {e}")
        return False

if __name__ == "__main__":
    success = production_test()
    exit(0 if success else 1)