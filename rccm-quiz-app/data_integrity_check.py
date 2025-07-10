#!/usr/bin/env python3
"""
RCCM全CSVファイルのデータ整合性チェック
- 問題ID重複チェック
- 不正な正解値チェック
- 必須フィールドチェック
"""

import os
import csv
import json
from datetime import datetime
from collections import defaultdict

def check_data_integrity():
    """全CSVファイルのデータ整合性を確認"""
    
    data_dir = "/mnt/c/Users/ABC/Desktop/rccm-quiz-app/rccm-quiz-app/data"
    
    # 対象ファイルのリスト
    target_files = [
        "4-1.csv",
        "4-2_2008.csv", "4-2_2009.csv", "4-2_2010.csv", "4-2_2011.csv",
        "4-2_2012.csv", "4-2_2013.csv", "4-2_2014.csv", "4-2_2015.csv",
        "4-2_2016.csv", "4-2_2017.csv", "4-2_2018.csv", "4-2_2019.csv"
    ]
    
    results = {}
    global_id_tracker = defaultdict(list)  # グローバル ID 重複チェック用
    
    for filename in target_files:
        filepath = os.path.join(data_dir, filename)
        
        if not os.path.exists(filepath):
            results[filename] = {"status": "file_not_found"}
            continue
            
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                # ファイル内のチェック結果
                local_ids = set()
                duplicate_ids = []
                invalid_correct_answers = []
                missing_fields = []
                
                required_fields = ['id', 'category', 'question', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer']
                
                row_count = 0
                for row_idx, row in enumerate(reader, 1):
                    row_count += 1
                    
                    # 必須フィールドチェック
                    for field in required_fields:
                        if not row.get(field, '').strip():
                            missing_fields.append(f"行{row_idx}: {field}フィールドが空")
                    
                    # ID重複チェック（ファイル内）
                    question_id = row.get('id', '').strip()
                    if question_id:
                        if question_id in local_ids:
                            duplicate_ids.append(question_id)
                        local_ids.add(question_id)
                        
                        # グローバル ID チェック用
                        global_id_tracker[question_id].append(filename)
                    
                    # 正解値チェック
                    correct_answer = row.get('correct_answer', '').strip()
                    if correct_answer not in ['A', 'B', 'C', 'D']:
                        invalid_correct_answers.append(f"行{row_idx}: '{correct_answer}'")
                
                results[filename] = {
                    "status": "analyzed",
                    "total_questions": row_count,
                    "local_duplicate_ids": duplicate_ids,
                    "invalid_correct_answers": invalid_correct_answers,
                    "missing_fields": missing_fields,
                    "has_issues": bool(duplicate_ids or invalid_correct_answers or missing_fields)
                }
                
        except Exception as e:
            results[filename] = {
                "status": "error",
                "error": str(e)
            }
    
    # グローバル ID 重複チェック
    global_duplicates = {qid: files for qid, files in global_id_tracker.items() if len(files) > 1}
    
    # 結果をJSON形式で保存
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"data_integrity_check_{timestamp}.json"
    
    full_results = {
        "check_timestamp": datetime.now().isoformat(),
        "file_results": results,
        "global_duplicate_ids": global_duplicates,
        "summary": {
            "total_files": len(target_files),
            "analyzed_files": len([r for r in results.values() if r.get("status") == "analyzed"]),
            "files_with_issues": len([r for r in results.values() if r.get("has_issues")]),
            "global_duplicates_count": len(global_duplicates)
        }
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(full_results, f, ensure_ascii=False, indent=2)
    
    # 結果を表示
    print("=== RCCM全CSVファイル データ整合性チェック ===")
    print(f"チェック日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # ファイル別結果
    issues_found = False
    for filename, result in results.items():
        print(f"ファイル: {filename}")
        
        if result["status"] == "file_not_found":
            print("  → ファイルが見つかりません")
            issues_found = True
        elif result["status"] == "error":
            print(f"  → エラー: {result['error']}")
            issues_found = True
        elif result["status"] == "analyzed":
            print(f"  → 総問題数: {result['total_questions']}")
            
            if result["local_duplicate_ids"]:
                print(f"  → 重複ID: {result['local_duplicate_ids']}")
                issues_found = True
            
            if result["invalid_correct_answers"]:
                print(f"  → 不正な正解値: {result['invalid_correct_answers'][:5]}...")  # 最初の5個まで表示
                issues_found = True
                
            if result["missing_fields"]:
                print(f"  → 必須フィールド不足: {len(result['missing_fields'])}件")
                issues_found = True
                
            if not result["has_issues"]:
                print("  → 問題なし")
        
        print()
    
    # グローバル重複チェック結果
    print("=== グローバル ID 重複チェック ===")
    if global_duplicates:
        print("以下のIDが複数ファイルで重複しています:")
        for qid, files in global_duplicates.items():
            print(f"  ID {qid}: {', '.join(files)}")
        issues_found = True
    else:
        print("グローバル ID 重複は見つかりませんでした")
    
    print()
    print("=== 総合結果 ===")
    if issues_found:
        print("⚠️  問題が見つかりました。上記の詳細を確認してください。")
    else:
        print("✅ すべてのファイルが正常です！")
    
    print(f"\n詳細結果は {output_file} に保存されました。")
    
    return full_results

if __name__ == "__main__":
    check_data_integrity()