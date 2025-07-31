#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RCCM試験システム データ検証スクリプト
各CSVファイルの具体的な内容確認
"""

import os
import csv
from collections import defaultdict

def verify_csv_files():
    """CSVファイルの詳細検証"""
    data_dir = r"C:\Users\ABC\Desktop\rccm-quiz-app\rccm-quiz-app\data"
    
    print("RCCM データファイル詳細検証")
    print("=" * 50)
    
    # 基礎科目の確認
    basic_file = os.path.join(data_dir, "4-1.csv")
    if os.path.exists(basic_file):
        print("\n[基礎科目] 4-1.csv")
        with open(basic_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            categories = defaultdict(int)
            total = 0
            for row in reader:
                categories[row.get('category', '')] += 1
                total += 1
            
            print(f"  総問題数: {total}問")
            for cat, count in categories.items():
                print(f"  {cat}: {count}問")
    
    # 専門科目の年度別確認
    specialist_files = []
    for f in os.listdir(data_dir):
        if f.startswith("4-2_") and f.endswith(".csv") and not ".backup" in f:
            specialist_files.append(f)
    
    specialist_files.sort()
    
    print(f"\n[専門科目] 年度別ファイル ({len(specialist_files)}個)")
    
    all_categories = set()
    year_summary = {}
    
    for file_name in specialist_files:
        year = file_name.replace("4-2_", "").replace(".csv", "")
        file_path = os.path.join(data_dir, file_name)
        
        print(f"\n  {year}年 ({file_name})")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                categories = defaultdict(int)
                total = 0
                
                for row in reader:
                    category = row.get('category', '').strip()
                    if category:
                        categories[category] += 1
                        all_categories.add(category)
                    total += 1
                
                year_summary[year] = {"total": total, "categories": dict(categories)}
                print(f"    総問題数: {total}問")
                
                # カテゴリ別問題数を表示
                for cat in sorted(categories.keys()):
                    print(f"    {cat}: {categories[cat]}問")
                    
        except Exception as e:
            print(f"    エラー: {e}")
    
    # 全カテゴリのサマリー
    print(f"\n[カテゴリ一覧] 全{len(all_categories)}カテゴリ")
    for i, cat in enumerate(sorted(all_categories), 1):
        print(f"  {i:2d}. {cat}")
    
    # 年度別総問題数の比較
    print(f"\n[年度別総問題数]")
    for year in sorted(year_summary.keys()):
        total = year_summary[year]["total"]
        print(f"  {year}年: {total:3d}問")
    
    # 各カテゴリの年度別問題数
    print(f"\n[カテゴリ別年度分布]")
    for cat in sorted(all_categories):
        print(f"\n  {cat}:")
        year_counts = []
        for year in sorted(year_summary.keys()):
            count = year_summary[year]["categories"].get(cat, 0)
            if count > 0:
                print(f"    {year}年: {count}問")
                year_counts.append(count)
        
        if year_counts:
            min_q = min(year_counts)
            max_q = max(year_counts)
            avg_q = sum(year_counts) / len(year_counts)
            print(f"    範囲: {min_q}-{max_q}問 (平均: {avg_q:.1f}問)")

if __name__ == "__main__":
    verify_csv_files()