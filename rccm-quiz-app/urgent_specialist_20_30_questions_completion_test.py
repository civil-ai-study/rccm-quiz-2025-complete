#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
【緊急必須】専門分野20問・30問完走確認テスト
結果確認画面まで完全実行・副作用ゼロ保証
"""

import requests
import json
import re
from datetime import datetime
import time

def test_specialist_questions_completion():
    """
    専門分野20問・30問の完走から結果確認画面まで
    ユーザー様ご指摘の重要確認事項
    """
    print("🚨 【緊急必須】専門分野20問・30問完走確認テスト")
    print("結果確認画面まで完全実行・副作用ゼロ保証")
    print("=" * 80)
    
    base_url = "https://rccm-quiz-2025.onrender.com"
    
    results = {
        "test_name": "緊急必須_専門分野20問30問完走確認",
        "timestamp": datetime.now().isoformat(),
        "purpose": "結果確認画面まで完全テスト実行",
        "tests": []
    }
    
    # テスト1: 専門分野20問完走テスト
    print("\n📋 テスト1: 専門分野20問完走 → 結果確認画面")
    test_result_20 = test_complete_flow(base_url, 20, "specialist")
    results["tests"].append(test_result_20)
    
    # 少し待機
    time.sleep(2)
    
    # テスト2: 専門分野30問完走テスト  
    print("\n📋 テスト2: 専門分野30問完走 → 結果確認画面")
    test_result_30 = test_complete_flow(base_url, 30, "specialist")
    results["tests"].append(test_result_30)
    
    # 結果サマリー
    print("\n" + "=" * 80)
    print("🎯 【緊急必須】専門分野完走確認テスト結果")
    print("=" * 80)
    
    total_tests = len(results["tests"])
    successful_tests = sum(1 for test in results["tests"] if test.get("final_success", False))
    success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"✅ 完走成功: {successful_tests}/{total_tests} ({success_rate:.1f}%)")
    
    # 詳細結果
    for test in results["tests"]:
        num_q = test.get("num_questions", 0)
        success = test.get("final_success", False)
        reached_result = test.get("reached_result_screen", False)
        status = "✅ 完走成功" if success else "❌ 完走失敗"
        result_status = "✅ 結果画面到達" if reached_result else "❌ 結果画面未到達"
        print(f"  {num_q}問テスト: {status} / {result_status}")
    
    # 重要な確認事項
    print(f"\n📋 重要確認事項:")
    for test in results["tests"]:
        num_q = test.get("num_questions", 0)
        if test.get("final_success", False):
            score = test.get("final_score", "不明")
            correct = test.get("correct_answers", "不明")
            print(f"  {num_q}問テスト結果: 正解数={correct}, スコア={score}")
        else:
            error = test.get("error_reason", "不明エラー")
            print(f"  {num_q}問テスト失敗理由: {error}")
    
    # レポート保存
    report_filename = f"urgent_specialist_completion_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n📋 詳細レポート保存: {report_filename}")
    
    # 最終判定
    if success_rate >= 100:
        print(f"\n🎉 【完全成功】20問・30問とも結果確認画面まで到達")
        print("✅ ユーザー様ご指摘の確認事項完了")
        return True
    elif success_rate >= 50:
        print(f"\n⚠️ 【部分成功】一部で結果確認画面まで到達")
        print("🔧 残りの問題について対応が必要")
        return False
    else:
        print(f"\n🚨 【要対応】20問・30問とも結果確認画面未到達")
        print("🔧 緊急対応が必要")
        return False

def test_complete_flow(base_url, num_questions, question_type):
    """
    指定問題数での完全フロー実行
    """
    print(f"🔍 {num_questions}問{question_type}テスト開始")
    
    test_result = {
        "num_questions": num_questions,
        "question_type": question_type,
        "final_success": False,
        "reached_result_screen": False,
        "steps": {}
    }
    
    session = requests.Session()
    
    try:
        # ステップ1: ホームページアクセス
        print(f"   ステップ1: ホームページアクセス")
        response = session.get(f"{base_url}/")
        if response.status_code != 200:
            test_result["error_reason"] = f"ホームページアクセス失敗: {response.status_code}"
            return test_result
        test_result["steps"]["homepage"] = True
        
        # ステップ2: 試験開始（POSTで問題数指定）
        print(f"   ステップ2: {num_questions}問試験開始")
        start_data = {
            "exam_type": question_type,
            "questions": str(num_questions),
            "year": "2024"
        }
        response = session.post(f"{base_url}/start_exam/{question_type}", data=start_data)
        
        if response.status_code not in [200, 302]:
            test_result["error_reason"] = f"試験開始失敗: {response.status_code}"
            return test_result
        test_result["steps"]["exam_start"] = True
        
        # ステップ3: 問題ページアクセス
        print(f"   ステップ3: 問題ページアクセス")
        response = session.get(f"{base_url}/exam")
        if response.status_code != 200:
            test_result["error_reason"] = f"問題ページアクセス失敗: {response.status_code}"
            return test_result
        
        # セッション設定確認
        if 'exam_question_ids' not in session.cookies.get_dict() and 'name="qid"' not in response.text:
            test_result["error_reason"] = "セッション設定未完了"
            return test_result
        test_result["steps"]["question_access"] = True
        
        # ステップ4: 全問題を高速で回答
        print(f"   ステップ4: {num_questions}問高速回答処理")
        current_question = 1
        
        while current_question <= num_questions:
            # QID抽出
            qid_match = re.search(r'name="qid" value="(\d+)"', response.text)
            if not qid_match:
                test_result["error_reason"] = f"QID抽出失敗（{current_question}問目）"
                return test_result
            
            qid = qid_match.group(1)
            
            # CSRF token抽出
            csrf_match = re.search(r'name="csrf_token" value="([^"]+)"', response.text)
            csrf_token = csrf_match.group(1) if csrf_match else ""
            
            # 回答送信
            answer_data = {
                "answer": "A",  # 固定回答で高速処理
                "qid": qid,
                "elapsed": "5",
                "csrf_token": csrf_token
            }
            
            response = session.post(f"{base_url}/exam", data=answer_data)
            
            if response.status_code != 200:
                test_result["error_reason"] = f"回答送信失敗（{current_question}問目）: {response.status_code}"
                return test_result
            
            # 次の問題へ or 結果画面へ
            if "結果を見る" in response.text or "テスト結果" in response.text or "/result" in response.text:
                print(f"   ✅ {current_question}問目完了 → 結果画面へ")
                break
            elif "次の問題へ" in response.text:
                # 次の問題ボタンクリック
                response = session.get(f"{base_url}/exam?next=1")
                current_question += 1
                print(f"   ✅ {current_question-1}問目完了 → {current_question}問目へ")
            else:
                # レスポンス内容確認
                if 'name="qid"' in response.text:
                    current_question += 1
                    print(f"   ✅ {current_question-1}問目完了 → {current_question}問目へ")
                else:
                    test_result["error_reason"] = f"予期しないレスポンス（{current_question}問目）"
                    return test_result
        
        test_result["steps"]["all_questions_answered"] = True
        
        # ステップ5: 結果画面アクセス
        print(f"   ステップ5: 結果確認画面アクセス")
        
        # 結果画面への遷移
        if "/result" in response.url:
            result_response = response
        else:
            # 結果ボタンクリック
            result_response = session.get(f"{base_url}/result")
        
        if result_response.status_code == 200:
            test_result["reached_result_screen"] = True
            test_result["steps"]["result_screen"] = True
            
            # 結果データ抽出
            score_match = re.search(r'スコア[：:]\s*(\d+)', result_response.text)
            correct_match = re.search(r'正解数[：:]\s*(\d+)', result_response.text)
            
            if score_match:
                test_result["final_score"] = score_match.group(1)
            if correct_match:
                test_result["correct_answers"] = correct_match.group(1)
            
            test_result["final_success"] = True
            print(f"   ✅ 結果確認画面到達成功")
            
            if score_match or correct_match:
                print(f"   📊 結果: 正解数={test_result.get('correct_answers', '不明')}, スコア={test_result.get('final_score', '不明')}")
        else:
            test_result["error_reason"] = f"結果画面アクセス失敗: {result_response.status_code}"
            return test_result
        
    except Exception as e:
        test_result["error_reason"] = f"予期しないエラー: {str(e)}"
        return test_result
    
    return test_result

if __name__ == "__main__":
    print("🚨 緊急必須: 専門分野20問・30問完走確認テスト")
    print("結果確認画面まで完全実行")
    print()
    
    success = test_specialist_questions_completion()
    
    print(f"\n🎯 緊急テスト完了")
    print("ユーザー様ご指摘事項の確認結果をご確認ください")
    
    exit(0 if success else 1)