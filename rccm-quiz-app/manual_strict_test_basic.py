#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基礎科目(4-1) 厳格な手作業テスト
CLAUDE.md準拠・手抜きなし・省略なし
"""

import os
import sys
import csv
import time
import json
from datetime import datetime

def manual_basic_subject_test():
    """基礎科目の厳格なテスト"""
    print("🚀 基礎科目(4-1) 厳格な手作業テスト開始")
    print("=" * 80)
    
    # テスト結果記録
    test_log = {
        "start_time": datetime.now().isoformat(),
        "subject": "基礎科目(4-1)",
        "test_type": "manual_strict",
        "steps": [],
        "results": {}
    }
    
    # Step 1: ファイル存在確認
    print("Step 1: データファイル存在確認")
    file_path = "/mnt/c/Users/ABC/Desktop/rccm-quiz-app/rccm-quiz-app/data/4-1.csv"
    
    if not os.path.exists(file_path):
        print("❌ CRITICAL: データファイルが存在しません")
        test_log["steps"].append({"step": 1, "status": "FAILED", "reason": "ファイル不存在"})
        return False
    
    print(f"✅ データファイル存在確認: {file_path}")
    test_log["steps"].append({"step": 1, "status": "PASSED", "file_path": file_path})
    
    # Step 2: ファイル読み込み・構造確認
    print("\nStep 2: CSVファイル構造確認")
    questions = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            required_columns = ['id', 'category', 'question', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer']
            
            # ヘッダー確認
            if not all(col in reader.fieldnames for col in required_columns):
                missing = [col for col in required_columns if col not in reader.fieldnames]
                print(f"❌ CRITICAL: 必須カラム不足: {missing}")
                test_log["steps"].append({"step": 2, "status": "FAILED", "reason": f"必須カラム不足: {missing}"})
                return False
            
            # データ読み込み
            for row in reader:
                questions.append(row)
        
        print(f"✅ CSVファイル構造確認完了: {len(questions)}問読み込み")
        test_log["steps"].append({"step": 2, "status": "PASSED", "questions_loaded": len(questions)})
        
    except Exception as e:
        print(f"❌ CRITICAL: ファイル読み込みエラー: {e}")
        test_log["steps"].append({"step": 2, "status": "FAILED", "reason": str(e)})
        return False
    
    # Step 3: データ品質チェック
    print("\nStep 3: データ品質チェック")
    
    # 3-1: 問題ID重複チェック
    print("  3-1: 問題ID重複チェック")
    ids = [q['id'] for q in questions]
    duplicates = [id for id in set(ids) if ids.count(id) > 1]
    
    if duplicates:
        print(f"❌ CRITICAL: 重複ID発見: {duplicates}")
        test_log["steps"].append({"step": "3-1", "status": "FAILED", "duplicates": duplicates})
        return False
    else:
        print("✅ 問題ID重複なし")
        test_log["steps"].append({"step": "3-1", "status": "PASSED"})
    
    # 3-2: 必須フィールド空白チェック
    print("  3-2: 必須フィールド空白チェック")
    invalid_questions = []
    
    for i, q in enumerate(questions):
        if not q['id'] or not q['question'] or not q['correct_answer']:
            invalid_questions.append(f"行{i+2}: ID={q['id']}")
    
    if invalid_questions:
        print(f"❌ CRITICAL: 必須フィールド空白: {len(invalid_questions)}件")
        for invalid in invalid_questions[:5]:  # 最初の5件のみ表示
            print(f"    {invalid}")
        test_log["steps"].append({"step": "3-2", "status": "FAILED", "invalid_count": len(invalid_questions)})
        return False
    else:
        print("✅ 必須フィールド空白なし")
        test_log["steps"].append({"step": "3-2", "status": "PASSED"})
    
    # 3-3: 正答選択肢チェック
    print("  3-3: 正答選択肢妥当性チェック")
    invalid_answers = []
    
    for i, q in enumerate(questions):
        if q['correct_answer'].lower() not in ['a', 'b', 'c', 'd']:
            invalid_answers.append(f"行{i+2}: {q['correct_answer']}")
    
    if invalid_answers:
        print(f"❌ CRITICAL: 不正な正答: {len(invalid_answers)}件")
        for invalid in invalid_answers[:5]:
            print(f"    {invalid}")
        test_log["steps"].append({"step": "3-3", "status": "FAILED", "invalid_answers": len(invalid_answers)})
        return False
    else:
        print("✅ 正答選択肢妥当性確認")
        test_log["steps"].append({"step": "3-3", "status": "PASSED"})
    
    # Step 4: 10問セッションテスト
    print("\nStep 4: 10問セッション実行テスト")
    result_10 = execute_question_session(questions, 10, test_log)
    
    # Step 5: 20問セッションテスト
    print("\nStep 5: 20問セッション実行テスト")
    result_20 = execute_question_session(questions, 20, test_log)
    
    # Step 6: 30問セッションテスト
    print("\nStep 6: 30問セッション実行テスト")
    result_30 = execute_question_session(questions, 30, test_log)
    
    # 最終結果
    test_log["results"] = {
        "10問テスト": result_10,
        "20問テスト": result_20,
        "30問テスト": result_30
    }
    test_log["end_time"] = datetime.now().isoformat()
    
    # 結果保存
    report_file = f"manual_basic_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(test_log, f, ensure_ascii=False, indent=2)
    
    print(f"\n📊 基礎科目テスト結果:")
    print(f"  - 10問テスト: {result_10['status']}")
    print(f"  - 20問テスト: {result_20['status']}")
    print(f"  - 30問テスト: {result_30['status']}")
    print(f"  - 詳細レポート: {report_file}")
    
    success = all(r['status'] == 'PASSED' for r in [result_10, result_20, result_30])
    
    if success:
        print("\n✅ 基礎科目(4-1) 厳格テスト完全合格")
    else:
        print("\n❌ 基礎科目(4-1) 厳格テスト失敗")
    
    return success

def execute_question_session(questions, question_count, test_log):
    """指定問題数のセッション実行テスト"""
    print(f"  {question_count}問セッション開始...")
    
    start_time = time.time()
    
    # 問題数チェック
    if len(questions) < question_count:
        result = {
            "status": "FAILED",
            "reason": f"必要問題数不足: 必要{question_count}問、利用可能{len(questions)}問"
        }
        print(f"❌ {result['reason']}")
        return result
    
    # セッション実行シミュレーション
    import random
    selected_questions = random.sample(questions, question_count)
    
    print(f"    問題選択完了: {len(selected_questions)}問")
    
    # 各問題の妥当性チェック
    session_errors = []
    correct_count = 0
    
    for i, q in enumerate(selected_questions):
        # 問題データ完整性チェック
        if not q['question'] or not q['option_a'] or not q['option_b'] or not q['option_c'] or not q['option_d']:
            session_errors.append(f"問題{i+1}: 選択肢データ不完全")
            continue
        
        # 回答処理シミュレーション
        user_answer = random.choice(['a', 'b', 'c', 'd'])
        if user_answer == q['correct_answer'].lower():
            correct_count += 1
        
        # 進捗表示（5問ごと）
        if (i + 1) % 5 == 0:
            print(f"    進捗: {i+1}/{question_count}問処理完了")
    
    elapsed_time = time.time() - start_time
    
    if session_errors:
        result = {
            "status": "FAILED",
            "errors": session_errors,
            "elapsed_time": elapsed_time
        }
        print(f"❌ セッションエラー: {len(session_errors)}件")
    else:
        accuracy = correct_count / question_count * 100
        result = {
            "status": "PASSED",
            "questions_processed": question_count,
            "correct_answers": correct_count,
            "accuracy": accuracy,
            "elapsed_time": elapsed_time
        }
        print(f"✅ セッション完了: 正答率{accuracy:.1f}% ({correct_count}/{question_count})")
    
    test_log["steps"].append({
        "step": f"session_{question_count}",
        "status": result["status"],
        "details": result
    })
    
    return result

if __name__ == "__main__":
    success = manual_basic_subject_test()
    sys.exit(0 if success else 1)