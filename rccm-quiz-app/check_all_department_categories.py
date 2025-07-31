#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ULTRA SYNC: 全部門のCSVカテゴリー名確認
残り11部門のカテゴリー名問題を特定
"""

import csv
import os
from collections import defaultdict

def check_department_categories():
    """全部門のCSVカテゴリー名を調査"""
    print("ULTRA SYNC: All department CSV category analysis")
    print("=" * 60)
    
    data_dir = 'data'
    all_categories = set()
    category_counts = defaultdict(int)
    
    # 専門科目CSVファイルを全て確認
    for year in range(2008, 2020):
        filepath = os.path.join(data_dir, f'4-2_{year}.csv')
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8-sig') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        category = row.get('category', '').strip()
                        if category:
                            all_categories.add(category)
                            category_counts[category] += 1
            except Exception as e:
                print(f"   Error reading {year}: {e}")
    
    print(f"\nFound {len(all_categories)} unique categories:")
    print("-" * 40)
    
    # カテゴリー名を問題数とともに表示
    for category in sorted(all_categories):
        count = category_counts[category]
        print(f"{category:<30} ({count:3d} questions)")
    
    # 部門マッピング確認
    print(f"\nDepartment mapping analysis:")
    print("-" * 40)
    
    department_list = [
        '基礎科目', '道路', '河川・砂防', '都市計画', '造園',
        '建設環境', '鋼構造・コンクリート', '土質・基礎', 
        '施工計画', '上下水道', '森林土木', '農業土木', 'トンネル'
    ]
    
    # 各部門に対応するCSVカテゴリーを推定
    for dept in department_list:
        if dept == '基礎科目':
            print(f"{dept:<15} -> 共通 (4-1.csv)")
        else:
            # 部分文字列マッチングで候補を探す
            candidates = [cat for cat in all_categories if dept in cat or any(word in cat for word in dept.split('・'))]
            if candidates:
                print(f"{dept:<15} -> {candidates[0]}")
            else:
                print(f"{dept:<15} -> NO MATCH FOUND!")
    
    return all_categories, category_counts

if __name__ == "__main__":
    categories, counts = check_department_categories()
    
    print(f"\nSummary:")
    print(f"Total categories: {len(categories)}")
    print(f"Total questions: {sum(counts.values())}")
    print(f"Categories requiring investigation:")
    
    problem_categories = [cat for cat in categories if '上下水道' in cat or '工業用水' in cat]
    for cat in problem_categories:
        print(f"  - {cat}")