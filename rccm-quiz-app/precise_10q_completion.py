#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
【ULTRASYNC精密10問完走テスト】
正確なセッション管理で10問完走→結果画面までを精密検証
"""

import requests
import json
import re
from datetime import datetime
import time

def precise_10question_completion():
    """精密な10問完走テスト"""
    print("🎯 【ULTRASYNC精密】10問完走→結果画面まで精密検証")
    print("=" * 60)
    
    base_url = "https://rccm-quiz-2025.onrender.com"
    session = requests.Session()
    
    # 回答パターン
    answers = ["A", "B", "C", "D", "A", "B", "C", "D", "A", "B"]
    completion_log = []
    
    try:
        # セッション初期化
        print("📋 ステップ1: セッション初期化")
        session.get(f"{base_url}/")
        
        # 試験開始
        print("📋 ステップ2: 試験開始")
        response = session.get(f"{base_url}/exam?question_type=basic")
        if response.status_code != 200:
            print(f"❌ 試験開始失敗: {response.status_code}")
            return False
        
        print("📋 ステップ3: 10問連続実行")
        
        for question_num in range(1, 11):
            print(f"\n   🔍 問題 {question_num}/10 開始")
            
            # 現在の問題取得
            response = session.get(f"{base_url}/exam")
            if response.status_code != 200:
                print(f"      ❌ 問題取得失敗: {response.status_code}")
                return False
            
            # 問題IDと進捗を抽出
            qid_match = re.search(r'name="qid" value="(\d+)"', response.text)
            progress_match = re.search(r'(\d+)/(\d+)', response.text)
            
            if not qid_match:
                print(f"      ❌ 問題ID抽出失敗")
                return False
            
            qid = qid_match.group(1)
            if progress_match:
                current_progress = progress_match.group(1)
                total_progress = progress_match.group(2)
                print(f"      問題ID: {qid}, 進捗: {current_progress}/{total_progress}")
            else:
                print(f"      問題ID: {qid}, 進捗: 不明")
            
            # 回答送信
            answer = answers[question_num - 1]
            post_data = {
                "answer": answer,
                "qid": qid,
                "elapsed": "30"
            }
            
            print(f"      回答送信: {answer}")
            response = session.post(f"{base_url}/exam", data=post_data)
            print(f"      POST応答: {response.status_code}")
            
            if response.status_code not in [200, 302]:
                print(f"      ❌ 回答送信失敗: {response.status_code}")
                return False
            
            # 回答後の状態確認
            if response.status_code == 200:
                if "正解" in response.text or "不正解" in response.text:
                    print(f"      ✅ 回答処理成功")
                    
                    # 10問目の特別処理
                    if question_num == 10:
                        print(f"      🎯 10問目完了！")
                        if "結果を見る" in response.text:
                            print(f"      ✅ 結果ボタン確認")
                        elif "result" in response.text.lower():
                            print(f"      ✅ 結果リンク確認")
                        else:
                            print(f"      ⚠️ 結果への導線確認中...")
                            # 結果画面へ手動アクセス
                            result_response = session.get(f"{base_url}/result")
                            if result_response.status_code == 200:
                                print(f"      ✅ 結果画面へ直接アクセス成功")
                            else:
                                print(f"      ❌ 結果画面アクセス失敗: {result_response.status_code}")
                else:
                    print(f"      ⚠️ 回答結果内容不明")
            
            completion_log.append({
                "question_num": question_num,
                "qid": qid,
                "answer": answer,
                "status": response.status_code,
                "success": True
            })
            
            # 短時間待機
            time.sleep(0.5)
        
        # 最終結果画面確認
        print("\n📋 ステップ4: 最終結果画面詳細確認")
        result_response = session.get(f"{base_url}/result")
        print(f"   結果画面アクセス: {result_response.status_code}")
        
        if result_response.status_code == 200:
            print("   📊 結果画面内容分析:")
            
            # 詳細内容チェック
            content_checks = {
                "ページタイトル": "結果" in result_response.text or "Result" in result_response.text,
                "10問情報": "10" in result_response.text,
                "スコア情報": any(word in result_response.text for word in ["点", "正解", "得点", "score"]),
                "結果詳細": len(result_response.text) > 5000,  # 十分な内容量
                "試験終了": any(word in result_response.text for word in ["完了", "終了", "結果"]),
            }
            
            for check_name, check_result in content_checks.items():
                status_icon = "✅" if check_result else "❌"
                print(f"      {status_icon} {check_name}: {check_result}")
            
            # 具体的な数値を探す
            score_patterns = [
                r'(\d+)\s*[/点]\s*(\d+)',
                r'(\d+)\s*問中\s*(\d+)',
                r'正解数[:\s]*(\d+)',
                r'(\d+)\s*/\s*10'
            ]
            
            print("   🔍 スコア情報抽出:")
            for i, pattern in enumerate(score_patterns):
                matches = re.findall(pattern, result_response.text)
                if matches:
                    print(f"      パターン{i+1}: {matches}")
            
            # HTMLの特定部分を保存（デバッグ用）
            with open('result_page_debug.html', 'w', encoding='utf-8') as f:
                f.write(result_response.text)
            print("   📄 結果画面HTML保存: result_page_debug.html")
            
            success_checks = sum(1 for result in content_checks.values() if result)
            result_success = success_checks >= 3
            
        else:
            print(f"   ❌ 結果画面アクセス失敗: {result_response.status_code}")
            result_success = False
        
        # 最終判定
        questions_completed = len(completion_log)
        all_questions_success = questions_completed == 10
        
        print("\n" + "=" * 60)
        print("🎯 【ULTRASYNC精密】10問完走テスト最終結果")
        print("=" * 60)
        print(f"✅ 完走問題数: {questions_completed}/10")
        print(f"✅ 結果画面確認: {result_success}")
        
        # 詳細ログ
        print("\n📋 問題別実行ログ:")
        for log in completion_log:
            print(f"   問題{log['question_num']:2d}: QID={log['qid']:3s}, 回答={log['answer']}, ステータス={log['status']}")
        
        # 総合判定
        overall_success = all_questions_success and result_success
        
        if overall_success:
            print(f"\n🎉 【ULTRASYNC精密】完全成功")
            print(f"✅ 10問完全完走")
            print(f"✅ 結果画面到達")
            print(f"✅ セッション管理正常動作")
        else:
            print(f"\n🚨 【ULTRASYNC精密】部分成功")
            if not all_questions_success:
                print(f"❌ 10問完走に問題: {questions_completed}/10")
            if not result_success:
                print(f"❌ 結果画面に問題")
        
        # レポート保存
        report = {
            "timestamp": datetime.now().isoformat(),
            "questions_completed": questions_completed,
            "all_questions_success": all_questions_success,
            "result_screen_success": result_success,
            "overall_success": overall_success,
            "completion_log": completion_log
        }
        
        with open(f"precise_10q_completion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        return overall_success
        
    except Exception as e:
        print(f"\n❌ テスト実行エラー: {e}")
        return False

if __name__ == "__main__":
    success = precise_10question_completion()
    exit(0 if success else 1)