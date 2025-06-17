#!/usr/bin/env python3
"""
問題IDと年度データの整合性確認
"""

import csv
import os
import sys

def find_question_by_id(question_id):
    """問題IDでCSVファイルから問題を検索"""
    data_dir = "data"
    
    # すべてのCSVファイルを検索
    csv_files = [
        "4-1.csv",
        "4-2_2008.csv", "4-2_2009.csv", "4-2_2010.csv", "4-2_2011.csv", "4-2_2012.csv",
        "4-2_2013.csv", "4-2_2014.csv", "4-2_2015.csv", "4-2_2016.csv", "4-2_2017.csv", "4-2_2018.csv"
    ]
    
    for csv_file in csv_files:
        filepath = os.path.join(data_dir, csv_file)
        if not os.path.exists(filepath):
            continue
            
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get('id') == str(question_id):
                        return {
                            'file': csv_file,
                            'id': row.get('id'),
                            'year': row.get('year'),
                            'category': row.get('category'),
                            'question': row.get('question', '')[:100] + '...'
                        }
        except Exception as e:
            print(f"❌ {csv_file}読み込みエラー: {e}")
            
    return None

def analyze_id_range():
    """各年度のID範囲を分析"""
    data_dir = "data"
    
    year_files = {
        2008: "4-2_2008.csv",
        2009: "4-2_2009.csv", 
        2010: "4-2_2010.csv",
        2011: "4-2_2011.csv",
        2012: "4-2_2012.csv",
        2013: "4-2_2013.csv",
        2014: "4-2_2014.csv",
        2015: "4-2_2015.csv",
        2016: "4-2_2016.csv",
        2017: "4-2_2017.csv",
        2018: "4-2_2018.csv"
    }
    
    print("📊 各年度のID範囲分析:")
    print("-" * 60)
    
    for year, filename in year_files.items():
        filepath = os.path.join(data_dir, filename)
        if not os.path.exists(filepath):
            continue
            
        try:
            ids = []
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        ids.append(int(row.get('id', 0)))
                    except ValueError:
                        pass
                        
            if ids:
                min_id = min(ids)
                max_id = max(ids)
                count = len(ids)
                print(f"{year}年: {min_id:4d} - {max_id:4d} ({count:3d}問)")
                
                # 特定のIDをチェック
                test_ids = [3885, 3901, 3904, 4342, 3542, 3168, 4138]
                for test_id in test_ids:
                    if min_id <= test_id <= max_id:
                        print(f"       ID {test_id} は{year}年の範囲内")
                        
        except Exception as e:
            print(f"❌ {filename}エラー: {e}")

def main():
    print("🔍 問題IDと年度データの整合性確認")
    print("=" * 60)
    
    # テストで見つかった問題IDを確認
    test_ids = [3885, 3901, 3904, 4342, 3542, 3168, 4138]
    
    print("📋 テスト問題IDの確認:")
    for qid in test_ids:
        result = find_question_by_id(qid)
        if result:
            print(f"ID {qid}: {result['file']} - {result['year']}年 - {result['category']}")
        else:
            print(f"ID {qid}: ❌ 見つからない")
            
    print("\n")
    analyze_id_range()

if __name__ == "__main__":
    main()