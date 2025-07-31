#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RCCM分野混在問題の根本原因分析ツール
部門マッピングの不整合を診断する
"""

import csv
import os
import sys

# app.pyから抽出したマッピング情報
CSV_JAPANESE_CATEGORIES = {
    "基礎科目": "共通",
    "道路": "道路",
    "河川・砂防": "河川、砂防及び海岸・海洋", 
    "都市計画": "都市計画及び地方計画",
    "造園": "造園",
    "建設環境": "建設環境", 
    "鋼構造・コンクリート": "鋼構造及びコンクリート",
    "土質・基礎": "土質及び基礎",
    "施工計画": "施工計画、施工設備及び積算",
    "上下水道": "上水道及び工業用水道",
    "森林土木": "森林土木", 
    "農業土木": "農業土木",
    "トンネル": "トンネル"
}

MAP_DEPARTMENT_TO_CATEGORY = {
    # 基礎科目（4-1.csv）
    'basic': '基礎科目',
    'foundation': '基礎科目', 
    '基礎科目': '基礎科目',
    
    # 専門科目12部門（4-2_*.csv - 2019年実データ確認済み）
    'road': '道路',
    '道路': '道路',
    
    'river': '河川、砂防及び海岸・海洋',
    'sabo': '河川、砂防及び海岸・海洋', 
    '河川': '河川、砂防及び海岸・海洋',
    '砂防': '河川、砂防及び海岸・海洋',
    '河川・砂防': '河川、砂防及び海岸・海洋',
    
    'urban': '都市計画及び地方計画',
    '都市計画': '都市計画及び地方計画',
    
    'landscape': '造園',
    '造園': '造園',
    
    'environment': '建設環境',
    '建設環境': '建設環境',
    
    'steel': '鋼構造及びコンクリート',
    'concrete': '鋼構造及びコンクリート',
    '鋼構造': '鋼構造及びコンクリート',
    '鋼構造・コンクリート': '鋼構造及びコンクリート',
    
    'soil': '土質及び基礎',
    'foundation_eng': '土質及び基礎',
    '土質': '土質及び基礎',
    '基礎': '土質及び基礎',
    '土質・基礎': '土質及び基礎',
    
    'construction': '施工計画、施工設備及び積算',
    '施工': '施工計画、施工設備及び積算',
    '施工計画': '施工計画、施工設備及び積算',
    
    'water_supply': '上水道及び工業用水道',
    'water': '上水道及び工業用水道',
    '水道': '上水道及び工業用水道',
    '上下水道': '上水道及び工業用水道',
    
    'forest': '森林土木',
    '森林': '森林土木',
    '森林土木': '森林土木',
    
    'agriculture': '農業土木',
    '農業': '農業土木',
    '農業土木': '農業土木',
    
    'tunnel': 'トンネル',
    'トンネル': 'トンネル'
}

def analyze_mapping_inconsistencies():
    """マッピングの不整合を分析"""  
    print("RCCM分野混在問題 - マッピング不整合分析")
    print("=" * 60)
    
    print("\n1. CSV_JAPANESE_CATEGORIES:")
    for dept, category in CSV_JAPANESE_CATEGORIES.items():
        print(f"   {dept} -> {category}")
    
    print("\n2. MAP_DEPARTMENT_TO_CATEGORY (関連部分):")  
    relevant_mappings = {}
    for dept in CSV_JAPANESE_CATEGORIES.keys():
        if dept in MAP_DEPARTMENT_TO_CATEGORY:
            relevant_mappings[dept] = MAP_DEPARTMENT_TO_CATEGORY[dept]
    
    for dept, category in relevant_mappings.items():
        print(f"   {dept} -> {category}")
    
    print("\n3. 不整合の分析:")
    print("   NG 問題発見:")
    print("   - CSV_JAPANESE_CATEGORIES: '河川・砂防' -> '河川、砂防及び海岸・海洋'")
    print("   - MAP_DEPARTMENT_TO_CATEGORY: '河川・砂防' -> '河川、砂防及び海岸・海洋'")
    print("   - 両者は一致しているが、実際のCSVファイルのカテゴリ名が異なる可能性")
    
    return relevant_mappings

def check_csv_categories():
    """実際のCSVファイルのカテゴリを確認"""
    print("\n実際のCSVデータのカテゴリ確認")
    print("=" * 60)
    
    data_dir = "rccm-quiz-app/data"
    categories_found = set()
    
    # 4-1.csv (基礎科目)
    basic_file = os.path.join(data_dir, "4-1.csv")
    if os.path.exists(basic_file):
        with open(basic_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if 'category' in row:
                    categories_found.add(row['category'])
        print(f"4-1.csv カテゴリ: {list(categories_found)}")
    
    # 4-2_*.csv (専門科目)
    years = [2019, 2018, 2017]  # 最新の数年分をチェック
    for year in years:
        specialist_file = os.path.join(data_dir, f"4-2_{year}.csv")
        if os.path.exists(specialist_file):
            year_categories = set()
            with open(specialist_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if 'category' in row:
                        year_categories.add(row['category'])
            categories_found.update(year_categories)
            print(f"4-2_{year}.csv カテゴリ ({len(year_categories)}種類): {sorted(year_categories)}")
    
    print(f"\n全体で発見されたカテゴリ ({len(categories_found)}種類):")
    for category in sorted(categories_found):
        print(f"  - '{category}'")
    
    return categories_found

def analyze_department_matching():
    """部門選択時のマッチング問題を分析"""
    print("\n部門選択マッチング分析")
    print("=" * 60)
    
    print("問題のあるフロー:")
    print("1. ユーザーが '建設環境' を選択")  
    print("2. CSV_JAPANESE_CATEGORIES['建設環境'] = '建設環境'")
    print("3. CSVファイルで category == '建設環境' の問題を検索")
    print("4. しかし、実際のCSVデータに '建設環境' カテゴリが存在しない場合、他の問題が混入")
    
    print("\n推定される原因:")
    print("NG CSVファイルのcategoryフィールドと、アプリのマッピングが一致していない")
    print("NG フォールバック処理で他部門の問題がランダムに選択される")  
    print("NG 問題フィルタリングロジックが部分一致になっている")

def main():
    print("RCCM分野混在問題の根本原因分析")
    print("=" * 80)
    
    # マッピング不整合分析
    relevant_mappings = analyze_mapping_inconsistencies()
    
    # 実際のCSVカテゴリ確認
    csv_categories = check_csv_categories()
    
    # マッチング問題分析
    analyze_department_matching()
    
    print("\n分析結果サマリー")
    print("=" * 60)
    print("OK 両マッピング関数は基本的に一致")
    print("NG 実際のCSVデータのカテゴリ名要確認")
    print("NG 問題取得ロジックの厳密性要確認")
    print("次のステップ: get_department_questions_ultrasync関数の詳細分析")

if __name__ == "__main__":
    main()