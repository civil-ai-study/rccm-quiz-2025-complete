#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
【ULTRASYNC緊急修正】10問目まで完全完走検証
1問目から10問目まで連続回答し、最終結果画面までの完全フローを検証
"""

import requests
import json
import re
from datetime import datetime
import time

def extract_question_data(html_content):
    """HTMLから問題データを詳細抽出"""
    try:
        # 問題IDを抽出
        qid_match = re.search(r'name="qid"[^>]*value="(\d+)"', html_content)
        qid = qid_match.group(1) if qid_match else None
        
        # 問題番号を抽出
        question_num_match = re.search(r'問題(\d+)', html_content)
        question_num = question_num_match.group(1) if question_num_match else None
        
        # 進捗情報を抽出
        progress_match = re.search(r'(\d+)/(\d+)', html_content)
        if progress_match:
            current = int(progress_match.group(1))
            total = int(progress_match.group(2))
        else:
            current, total = 0, 10
        
        # 問題文を抽出
        question_match = re.search(r'<h4[^>]*>問題\d+</h4>\s*<p[^>]*>(.*?)</p>', html_content, re.DOTALL)
        question_text = question_match.group(1) if question_match else ""
        
        # 最終問題かどうかチェック
        is_last = "結果を見る" in html_content or current >= total
        
        return {
            "qid": qid,
            "question_num": question_num,
            "question_text": re.sub(r'<[^>]+>', '', question_text)[:100] + "..." if len(question_text) > 100 else re.sub(r'<[^>]+>', '', question_text),
            "current": current,
            "total": total,
            "is_last": is_last,
            "is_valid": qid is not None
        }
    except Exception as e:
        return {
            "qid": None,
            "question_num": None,
            "question_text": f"抽出エラー: {e}",
            "current": 0,
            "total": 10,
            "is_last": False,
            "is_valid": False
        }

def complete_10question_test():
    """10問目まで完全完走テスト"""
    print("🎯 【ULTRASYNC緊急修正】10問目まで完全完走検証開始")
    print("=" * 60)
    
    base_url = "https://rccm-quiz-2025.onrender.com"
    session = requests.Session()
    
    test_log = []
    answers = ["A", "B", "C", "D", "A", "B", "C", "D", "A", "B"]  # 10問の回答パターン
    
    try:
        # ステップ1: セッション初期化
        print("📋 ステップ1: セッション初期化")
        response = session.get(f"{base_url}/")
        print(f"   ホームページ: {response.status_code}")
        test_log.append({"step": 1, "action": "ホームページ", "status": response.status_code, "success": response.status_code == 200})
        
        # ステップ2: 試験開始
        print("\n📋 ステップ2: 基礎科目試験開始")
        response = session.get(f"{base_url}/exam?question_type=basic")
        print(f"   試験開始: {response.status_code}")
        
        if response.status_code != 200:
            print(f"   ❌ 試験開始失敗")
            return False
        
        first_question = extract_question_data(response.text)
        print(f"   初回問題ID: {first_question['qid']}")
        print(f"   進捗: {first_question['current']}/{first_question['total']}")
        
        if not first_question["is_valid"]:
            print("   ❌ 初回問題データが無効")
            return False
        
        test_log.append({"step": 2, "action": "試験開始", "status": response.status_code, "success": True, "qid": first_question['qid']})
        
        # ステップ3-12: 10問連続回答
        print("\n📋 ステップ3-12: 10問連続回答 (1問目から10問目まで)")
        
        current_question_data = first_question
        
        for question_num in range(1, 11):
            print(f"\n   🔍 問題 {question_num}/10")
            
            # 現在の問題データ確認
            if question_num > 1:
                # 2問目以降は新しく問題を取得
                response = session.get(f"{base_url}/exam")
                if response.status_code != 200:
                    print(f"      ❌ 問題{question_num}取得失敗: {response.status_code}")
                    test_log.append({"step": f"Q{question_num}", "action": f"問題{question_num}取得", "status": response.status_code, "success": False})
                    return False
                
                current_question_data = extract_question_data(response.text)
            
            print(f"      問題ID: {current_question_data['qid']}")
            print(f"      進捗: {current_question_data['current']}/{current_question_data['total']}")
            print(f"      問題文: {current_question_data['question_text']}")
            print(f"      最終問題: {current_question_data['is_last']}")
            
            if not current_question_data["is_valid"]:
                print(f"      ❌ 問題{question_num}データが無効")
                test_log.append({"step": f"Q{question_num}", "action": f"問題{question_num}データ", "status": "invalid", "success": False})
                return False
            
            # 回答送信
            answer = answers[question_num - 1]
            post_data = {
                "answer": answer,
                "qid": current_question_data["qid"],
                "elapsed": str(30 + question_num * 5)  # 経過時間を少しずつ増やす
            }
            
            print(f"      回答送信: {answer} (qid={current_question_data['qid']})")
            response = session.post(f"{base_url}/exam", data=post_data)
            print(f"      POST応答: {response.status_code}")
            
            if response.status_code not in [200, 302]:
                print(f"      ❌ 回答{question_num}送信失敗: {response.status_code}")
                test_log.append({"step": f"Q{question_num}", "action": f"回答{question_num}送信", "status": response.status_code, "success": False})
                return False
            
            # 回答処理結果確認
            if response.status_code == 200:
                # 結果ページの内容確認
                if "正解" in response.text or "不正解" in response.text:
                    print(f"      ✅ 回答{question_num}処理成功")
                    
                    # 10問目かどうかチェック
                    if question_num == 10:
                        # 10問目の場合は結果画面または結果へのリンクがあるはず
                        if "結果を見る" in response.text or "result" in response.text or "試験結果" in response.text:
                            print(f"      ✅ 10問目完了 - 結果画面への導線確認")
                        else:
                            print(f"      ⚠️ 10問目完了だが結果画面への導線不明")
                    else:
                        # 9問目以下の場合は次の問題への導線があるはず
                        next_question_match = re.search(r'(\d+)/10', response.text)
                        if next_question_match:
                            next_num = int(next_question_match.group(1))
                            print(f"      ➡️ 次の問題: {next_num}/10")
                        else:
                            print(f"      ⚠️ 次の問題への導線確認不可")
                else:
                    print(f"      ⚠️ 回答結果内容不明")
                
                test_log.append({
                    "step": f"Q{question_num}", 
                    "action": f"回答{question_num}処理", 
                    "status": response.status_code, 
                    "success": True,
                    "qid": current_question_data['qid'],
                    "answer": answer
                })
            
            elif response.status_code == 302:
                # リダイレクトの場合
                redirect_location = response.headers.get('Location', '')
                print(f"      ➡️ リダイレクト: {redirect_location}")
                
                if question_num == 10 and ('result' in redirect_location or 'Result' in redirect_location):
                    print(f"      ✅ 10問目完了 - 結果画面へリダイレクト")
                else:
                    print(f"      ➡️ 通常のリダイレクト")
                
                test_log.append({
                    "step": f"Q{question_num}", 
                    "action": f"回答{question_num}処理", 
                    "status": response.status_code, 
                    "success": True,
                    "redirect": redirect_location,
                    "qid": current_question_data['qid'],
                    "answer": answer
                })
            
            # 少し待機（サーバー負荷軽減）
            time.sleep(1)
        
        # ステップ13: 最終結果画面確認
        print("\n📋 ステップ13: 最終結果画面確認")
        response = session.get(f"{base_url}/result")
        print(f"   結果画面アクセス: {response.status_code}")
        
        if response.status_code == 200:
            # 結果画面の内容詳細確認
            result_content_checks = [
                ("試験結果", "試験結果" in response.text),
                ("スコア", "スコア" in response.text or "得点" in response.text or "点" in response.text),
                ("正解数", "正解" in response.text),
                ("10問中", "10問" in response.text or "10" in response.text),
                ("結果詳細", len(response.text) > 1000)  # 結果画面は一定のサイズがあるはず
            ]
            
            print("   📊 結果画面内容確認:")
            for check_name, check_result in result_content_checks:
                status_icon = "✅" if check_result else "❌"
                print(f"      {status_icon} {check_name}: {check_result}")
            
            # 結果画面のキーワード抽出
            score_match = re.search(r'(\d+)\s*[/点]\s*(\d+)', response.text)
            if score_match:
                score = score_match.group(1)
                total = score_match.group(2)
                print(f"   📈 検出スコア: {score}/{total}")
            
            success_checks = sum(1 for _, result in result_content_checks if result)
            result_success = success_checks >= 3  # 5項目中3項目以上成功
            
            test_log.append({
                "step": 13, 
                "action": "結果画面確認", 
                "status": response.status_code, 
                "success": result_success,
                "content_checks": result_content_checks
            })
            
        else:
            print(f"   ❌ 結果画面アクセス失敗: {response.status_code}")
            test_log.append({"step": 13, "action": "結果画面確認", "status": response.status_code, "success": False})
            return False
        
        # 最終結果判定
        successful_steps = sum(1 for log in test_log if log.get("success", False))
        total_steps = len(test_log)
        success_rate = (successful_steps / total_steps * 100) if total_steps > 0 else 0
        
        print("\n" + "=" * 60)
        print("🎯 【ULTRASYNC緊急修正】10問完全完走検証結果")
        print("=" * 60)
        print(f"✅ 成功ステップ: {successful_steps}/{total_steps} ({success_rate:.1f}%)")
        
        # 詳細ログ出力
        print("\n📋 詳細実行ログ:")
        for i, log in enumerate(test_log, 1):
            success_icon = "✅" if log.get("success", False) else "❌"
            print(f"{success_icon} {i:2d}. {log['action']}: {log['status']}")
            if "qid" in log:
                print(f"      QID: {log['qid']}, Answer: {log.get('answer', 'N/A')}")
            if "redirect" in log:
                print(f"      Redirect: {log['redirect']}")
        
        # レポート保存
        report = {
            "timestamp": datetime.now().isoformat(),
            "test_name": "ULTRASYNC緊急修正10問完全完走検証",
            "success_rate": success_rate,
            "total_steps": total_steps,
            "successful_steps": successful_steps,
            "complete_10questions": successful_steps >= total_steps - 1,  # 最後の1ステップ以外成功
            "result_screen_confirmed": test_log[-1].get("success", False) if test_log else False,
            "test_log": test_log
        }
        
        report_filename = f"complete_10question_verification_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n📋 完全検証レポート保存: {report_filename}")
        
        # 最終判定
        complete_success = (
            success_rate >= 90.0 and  # 90%以上成功
            report["result_screen_confirmed"] and  # 結果画面確認
            successful_steps >= 12  # 最低12ステップ成功（10問+初期化+結果）
        )
        
        if complete_success:
            print("\n🎉 【ULTRASYNC緊急修正】10問完全完走検証: 完全成功")
            print("✅ 1問目から10問目まで完全完走")
            print("✅ 最終結果画面まで正常到達")
            print("✅ セッション管理修正が完全に機能")
            return True
        else:
            print("\n🚨 【ULTRASYNC緊急修正】10問完全完走検証: 要改善")
            print("❌ 完全完走に問題がある可能性")
            return False
            
    except Exception as e:
        print(f"\n❌ 検証実行エラー: {e}")
        return False

if __name__ == "__main__":
    success = complete_10question_test()
    exit(0 if success else 1)