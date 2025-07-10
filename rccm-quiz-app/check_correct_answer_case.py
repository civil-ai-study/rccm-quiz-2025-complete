#!/usr/bin/env python3
"""
RCCM全CSVファイルの正解列（correct_answer）の大文字小文字状況を確認
"""

import os
import csv
import json
from datetime import datetime

def check_correct_answer_case():
    """全CSVファイルの正解列の大文字小文字状況を確認"""
    
    data_dir = "/mnt/c/Users/ABC/Desktop/rccm-quiz-app/rccm-quiz-app/data"
    
    # 対象ファイルのリスト
    target_files = [
        "4-1.csv",
        "4-2_2008.csv", "4-2_2009.csv", "4-2_2010.csv", "4-2_2011.csv",
        "4-2_2012.csv", "4-2_2013.csv", "4-2_2014.csv", "4-2_2015.csv",
        "4-2_2016.csv", "4-2_2017.csv", "4-2_2018.csv", "4-2_2019.csv"
    ]
    
    results = {}
    
    for filename in target_files:
        filepath = os.path.join(data_dir, filename)
        
        if not os.path.exists(filepath):
            results[filename] = {"status": "file_not_found"}
            continue
            
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                # 正解列の統計
                correct_answers = []
                lowercase_count = 0
                uppercase_count = 0
                invalid_count = 0
                
                for row in reader:
                    correct_answer = row.get('correct_answer', '').strip()
                    correct_answers.append(correct_answer)
                    
                    if correct_answer in ['a', 'b', 'c', 'd']:
                        lowercase_count += 1
                    elif correct_answer in ['A', 'B', 'C', 'D']:
                        uppercase_count += 1
                    else:
                        invalid_count += 1
                
                results[filename] = {
                    "status": "analyzed",
                    "total_questions": len(correct_answers),
                    "lowercase_count": lowercase_count,
                    "uppercase_count": uppercase_count,
                    "invalid_count": invalid_count,
                    "sample_answers": correct_answers[:10],  # 最初の10個をサンプル
                    "needs_fix": lowercase_count > 0 or invalid_count > 0
                }
                
        except Exception as e:
            results[filename] = {
                "status": "error",
                "error": str(e)
            }
    
    # 結果をJSON形式で保存
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"correct_answer_case_check_{timestamp}.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    # 結果を表示
    print("=== RCCM全CSVファイル正解列大文字小文字状況 ===")
    print(f"チェック日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    needs_fix_files = []
    
    for filename, result in results.items():
        print(f"ファイル: {filename}")
        
        if result["status"] == "file_not_found":
            print("  → ファイルが見つかりません")
        elif result["status"] == "error":
            print(f"  → エラー: {result['error']}")
        elif result["status"] == "analyzed":
            print(f"  → 総問題数: {result['total_questions']}")
            print(f"  → 小文字(a,b,c,d): {result['lowercase_count']}")
            print(f"  → 大文字(A,B,C,D): {result['uppercase_count']}")
            print(f"  → 不正値: {result['invalid_count']}")
            print(f"  → 修正必要: {'はい' if result['needs_fix'] else 'いいえ'}")
            print(f"  → サンプル: {result['sample_answers']}")
            
            if result['needs_fix']:
                needs_fix_files.append(filename)
        
        print()
    
    print("=== 修正が必要なファイル ===")
    if needs_fix_files:
        for filename in needs_fix_files:
            print(f"  - {filename}")
    else:
        print("  すべてのファイルが正常です（大文字のみ）")
    
    print(f"\n詳細結果は {output_file} に保存されました。")
    
    return results

if __name__ == "__main__":
    check_correct_answer_case()