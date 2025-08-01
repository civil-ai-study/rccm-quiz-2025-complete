#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接的な部門別問題抽出テスト
"""

import os
import csv

def test_department_filtering():
    """部門別問題抽出テスト"""
    print("=== 部門別問題抽出テスト ===")
    
    data_dir = "rccm-quiz-app/data"
    department = "道路"
    
    print(f"検索部門: '{department}'")
    print(f"部門名長さ: {len(department)}")
    print()
    
    if os.path.exists(data_dir):
        csv_files = [f for f in os.listdir(data_dir) if f.startswith('4-2_') and f.endswith('.csv')]
        print(f"対象ファイル数: {len(csv_files)}")
        
        total_questions = 0
        
        for csv_file in csv_files:
            file_path = os.path.join(data_dir, csv_file)
            file_count = 0
            
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['category'] == department:
                        file_count += 1
                        if total_questions < 3:  # 最初の3問表示
                            print(f"[{csv_file}] {row['question'][:50]}...")
            
            if file_count > 0:
                print(f"{csv_file}: {file_count}問")
                total_questions += file_count
        
        print(f"\n総問題数: {total_questions}")
        
        if total_questions > 0:
            print("✅ 部門別問題抽出成功")
        else:
            print("❌ 部門別問題抽出失敗")
    else:
        print("❌ データディレクトリが見つかりません")

if __name__ == "__main__":
    test_department_filtering()