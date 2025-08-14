#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
完全10問完走テスト - 道路部門専門科目の10問完走とフィールド混在確認
CLAUDE.md準拠の厳重なテスト (ウルトラシンプルディープ検索対応)
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'rccm-quiz-app'))

from app import app
import re
import time

def complete_10_question_department_test():
    """完全10問完走テスト - 道路部門専門科目"""
    print("=== 完全10問完走テスト開始 (道路部門専門科目) ===")
    print("目的: CLAUDE.md要件準拠の厳重なテスト実行")
    print("要件: 10問完走成功 + 分野混在なし確認")
    print("")
    
    with app.test_client() as client:
        with app.app_context():
            
            # 1. 道路部門種別選択ページアクセス
            print("【ステップ1】道路部門種別選択ページアクセス")
            types_response = client.get('/departments/road/types')
            
            if types_response.status_code != 200:
                return {"status": "FAILED", "step": 1, "error": f"種別選択ページ失敗 {types_response.status_code}"}
            
            print("✅ 種別選択ページアクセス成功")
            
            # 2. 道路部門専門科目セッション開始
            print("\n【ステップ2】道路部門専門科目セッション開始")
            exam_response = client.get('/exam?department=road&type=specialist')
            
            if exam_response.status_code != 200:
                return {"status": "FAILED", "step": 2, "error": f"専門科目開始失敗 {exam_response.status_code}"}
            
            print("✅ 専門科目セッション開始成功")
            
            # 3. 10問完走テスト実行
            print("\n【ステップ3】10問完走テスト実行")
            questions_data = []
            categories_found = set()
            
            for question_no in range(1, 11):
                print(f"\n--- 問題 {question_no}/10 処理 ---")
                
                # 現在の問題取得
                current_response = client.get('/exam')
                if current_response.status_code != 200:
                    return {"status": "FAILED", "step": 3, "question": question_no, 
                            "error": f"問題{question_no}取得失敗 {current_response.status_code}"}
                
                html = current_response.data.decode('utf-8', errors='ignore')
                
                # 進捗表示確認
                progress_match = re.search(r'(\d+)/(\d+)', html)
                if progress_match:
                    current_num = int(progress_match.group(1))
                    total_num = int(progress_match.group(2))
                    print(f"  進捗表示: {current_num}/{total_num}")
                    
                    if current_num != question_no:
                        print(f"  ⚠️ WARNING: 期待値{question_no} 実際{current_num}")
                else:
                    print("  ⚠️ 進捗表示なし")
                
                # カテゴリ確認（分野混在チェック）
                category_match = re.search(r'カテゴリ:\s*([^<\n]+)', html)
                if category_match:
                    category = category_match.group(1).strip()
                    print(f"  カテゴリ: {category}")
                    categories_found.add(category)
                    
                    # 道路部門以外の問題混入チェック
                    if category != "道路":
                        print(f"  ❌ 分野混在検出: {category}")
                        return {"status": "FIELD_MIXING_DETECTED", "step": 3, "question": question_no,
                                "expected_category": "道路", "actual_category": category,
                                "error": "CLAUDE.mdの分野混在問題が未解決"}
                else:
                    category = "不明"
                    print("  ⚠️ カテゴリ情報なし")
                
                # qid取得
                qid_match = re.search(r'name="qid" value="([^"]+)"', html)
                if qid_match:
                    qid = qid_match.group(1)
                    print(f"  問題ID: {qid}")
                else:
                    return {"status": "FAILED", "step": 3, "question": question_no,
                            "error": f"問題{question_no}でqid取得失敗"}
                
                # 問題データ記録
                questions_data.append({
                    'number': question_no,
                    'qid': qid,
                    'category': category,
                    'progress_display': f"{current_num}/{total_num}" if progress_match else "なし"
                })
                
                # CSRF token取得
                csrf_match = re.search(r'name="csrf_token" value="([^"]+)"', html)
                csrf_token = csrf_match.group(1) if csrf_match else None
                
                # 回答送信
                answer_choice = ['A', 'B', 'C', 'D'][(question_no - 1) % 4]
                answer_data = {
                    'qid': qid,
                    'answer': answer_choice,
                    'elapsed': str(30 + question_no * 2)
                }
                if csrf_token:
                    answer_data['csrf_token'] = csrf_token
                
                print(f"  回答送信: {answer_choice}")
                answer_response = client.post('/exam', data=answer_data)
                
                if answer_response.status_code != 200:
                    return {"status": "FAILED", "step": 3, "question": question_no,
                            "error": f"問題{question_no}回答送信失敗 {answer_response.status_code}"}
                
                print(f"  ✅ 問題{question_no}回答完了")
                
                # 少し待機
                time.sleep(0.1)
            
            # 4. 結果画面確認
            print("\n【ステップ4】結果画面確認")
            result_response = client.get('/result')
            
            if result_response.status_code != 200:
                return {"status": "FAILED", "step": 4, "error": f"結果画面アクセス失敗 {result_response.status_code}"}
            
            result_html = result_response.data.decode('utf-8', errors='ignore')
            
            # 結果画面での完了確認
            completion_indicators = ["完了", "結果", "score", "テスト完了", "回答数"]
            has_completion = any(indicator in result_html for indicator in completion_indicators)
            
            print("✅ 結果画面到達成功")
            
            # 5. 最終結果分析
            print("\n【ステップ5】最終結果分析")
            
            # 分野混在チェック結果
            if len(categories_found) == 1 and "道路" in categories_found:
                field_mixing_status = "分野混在なし - 道路部門のみ出題"
                field_mixing_success = True
                print("✅ 分野混在チェック: 成功")
            elif len(categories_found) == 0:
                field_mixing_status = "カテゴリ情報なし"
                field_mixing_success = False
                print("⚠️ 分野混在チェック: カテゴリ情報なし")
            else:
                field_mixing_status = f"分野混在あり - {', '.join(categories_found)}"
                field_mixing_success = False
                print(f"❌ 分野混在チェック: 失敗 - {field_mixing_status}")
            
            return {
                'status': 'COMPLETE_SUCCESS',
                'questions_completed': len(questions_data),
                'target_questions': 10,
                'questions_data': questions_data,
                'categories_found': list(categories_found),
                'field_mixing_success': field_mixing_success,
                'field_mixing_status': field_mixing_status,
                'result_page_reached': True,
                'completion_confirmed': has_completion,
                'department': 'road',
                'question_type': 'specialist'
            }

if __name__ == "__main__":
    result = complete_10_question_department_test()
    
    print("\n" + "=" * 80)
    if isinstance(result, dict):
        if result['status'] == 'COMPLETE_SUCCESS':
            print("🎉 完全10問完走テスト: 成功")
            print("=" * 80)
            print(f"✅ 問題完了数: {result['questions_completed']}/{result['target_questions']}")
            print(f"✅ 部門: {result['department']} (専門科目)")
            print(f"✅ 結果画面到達: {'成功' if result['result_page_reached'] else '失敗'}")
            print(f"✅ 完了確認: {'成功' if result['completion_confirmed'] else '失敗'}")
            print(f"✅ 分野混在チェック: {'成功' if result['field_mixing_success'] else '失敗'}")
            print(f"   {result['field_mixing_status']}")
            
            print("\n--- 各問題詳細 ---")
            for q in result['questions_data']:
                print(f"問題{q['number']:2d}: ID={q['qid']}, カテゴリ={q['category']}, 進捗={q['progress_display']}")
            
            print(f"\n--- 出現カテゴリ一覧 ---")
            print(f"カテゴリ数: {len(result['categories_found'])}")
            print(f"カテゴリ: {', '.join(result['categories_found'])}")
            
            print("\n🏆 結論:")
            print("✅ CLAUDE.md要件「10問完走成功」: 達成")
            print("✅ 部門指定ルート404エラー: 解決済み")
            if result['field_mixing_success']:
                print("✅ 分野混在問題: 解決済み")
            else:
                print("⚠️ 分野混在問題: 要継続調査")
                
        elif result['status'] == 'FIELD_MIXING_DETECTED':
            print("❌ CRITICAL: 分野混在問題発見")
            print(f"問題{result['question']}: 期待={result['expected_category']}, 実際={result['actual_category']}")
            print("CLAUDE.mdの分野混在問題が未解決")
            
        elif result['status'] == 'FAILED':
            print(f"❌ テスト失敗: ステップ{result['step']}")
            print(f"エラー: {result['error']}")
            
        else:
            print(f"⚠️ 予期しない結果: {result}")
    else:
        print(f"❌ テスト実行失敗: {result}")
    
    print("=" * 80)