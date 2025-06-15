#!/usr/bin/env python3
"""
詳細部門データ分析スクリプト
"""
import csv
import os
import re
from collections import defaultdict

def normalize_department(dept):
    """部門名を正規化"""
    if not dept:
        return dept
    
    normalization_rules = {
        '上水道工業用水道': '上水道及び工業用水道',
        '都市計画地方計画': '都市計画及び地方計画',
        '鋼構造コンクリート': '鋼構造及びコンクリート',
        '河川砂防海岸海洋': '河川、砂防及び海岸・海洋',
        '河川砂防海岸': '河川、砂防及び海岸・海洋',
        '河川砂防': '河川、砂防及び海岸・海洋',
        '河川・砂防及び海岸・海洋': '河川、砂防及び海岸・海洋',
        '河川、砂防及び海岸･海洋': '河川、砂防及び海岸・海洋',
        '河川砂防及び海岸・海洋': '河川、砂防及び海岸・海洋',
        '施工計画施工設備積算': '施工計画、施工設備及び積算',
        '施工計画・施工設備及び積算': '施工計画、施工設備及び積算',
        '施工計画積算': '施工計画、施工設備及び積算',
    }
    
    return normalization_rules.get(dept, dept)

def extract_year_from_filename(filename):
    """ファイル名から年度を抽出"""
    match = re.search(r'(\d{4})', filename)
    return int(match.group(1)) if match else None

def main():
    data_dir = '/mnt/c/Users/z285/Desktop/rccm-quiz-app/rccm-quiz-app/data'
    
    # 年度別部門データ
    year_departments = defaultdict(set)
    
    # 主要部門の定義（レガシーデータ、未分類、共通を除く）
    main_departments = set()
    
    # 年度別ファイルを処理
    for filename in os.listdir(data_dir):
        if not filename.endswith('.csv') or 'backup' in filename or 'fixed' in filename:
            continue
            
        year = extract_year_from_filename(filename)
        if not year:
            continue
            
        filepath = os.path.join(data_dir, filename)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if 'category' in row:
                        dept = normalize_department(row['category'])
                        if dept not in ['レガシーデータ', '未分類', '共通']:
                            year_departments[year].add(dept)
                            main_departments.add(dept)
        except Exception as e:
            print(f"エラー処理中 {filename}: {e}")
    
    # 結果表示
    print("=== 年度別部門データ分析 ===\n")
    
    print("【年度別利用可能部門】")
    for year in sorted(year_departments.keys()):
        depts = sorted(year_departments[year])
        print(f"{year}年: {len(depts)}部門")
        for dept in depts:
            print(f"  - {dept}")
        print()
    
    print("【主要部門一覧】（共通、未分類、レガシーデータを除く）")
    for i, dept in enumerate(sorted(main_departments), 1):
        years_available = [str(year) for year in sorted(year_departments.keys()) 
                         if dept in year_departments[year]]
        print(f"{i:2d}. {dept}")
        print(f"     利用可能年度: {', '.join(years_available)}")
        print()
    
    print(f"【統計情報】")
    print(f"主要部門数: {len(main_departments)}")
    print(f"対象年度数: {len(year_departments)}")
    print(f"年度範囲: {min(year_departments.keys())}-{max(year_departments.keys())}")

if __name__ == "__main__":
    main()