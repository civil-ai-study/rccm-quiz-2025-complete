#!/usr/bin/env python3
"""
部門マッピング検証
"""

# app.pyからマッピングを取得
DEPARTMENT_TO_CATEGORY_MAPPING = {
    'road': '道路',
    'tunnel': 'トンネル', 
    'civil_planning': '河川、砂防及び海岸・海洋',
    'urban_planning': '都市計画及び地方計画',
    'landscape': '造園',
    'construction_env': '建設環境',
    'steel_concrete': '鋼構造及びコンクリート',
    'soil_foundation': '土質及び基礎',
    'construction_planning': '施工計画、施工設備及び積算',
    'water_supply': '上水道及び工業用水道',
    'forestry': '森林土木',
    'agriculture': '農業土木',
    'basic': '共通'
}

# CSVから実際のカテゴリを確認
import subprocess
import os

def verify_mapping():
    print("=" * 60)
    print("部門マッピング検証")
    print("=" * 60)
    
    # CSVファイルから実際のカテゴリを抽出
    csv_path = '/mnt/c/Users/ABC/Desktop/rccm-quiz-app/rccm-quiz-app/data/4-2_2019.csv'
    
    if os.path.exists(csv_path):
        cmd = ['tail', '-n', '+2', csv_path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.stdout:
            lines = result.stdout.strip().split('\n')
            csv_categories = set()
            
            for line in lines[:50]:  # 最初の50行をサンプル
                parts = line.split(',')
                if len(parts) > 1:
                    category = parts[1].strip('"')
                    csv_categories.add(category)
            
            print(f"CSVファイルの実際のカテゴリ:")
            for cat in sorted(csv_categories):
                print(f"  - '{cat}'")
            
            print(f"\nマッピング定義:")
            for dept_key, category in DEPARTMENT_TO_CATEGORY_MAPPING.items():
                if dept_key != 'basic':
                    match = category in csv_categories
                    status = "✅" if match else "❌"
                    print(f"  {status} {dept_key} -> '{category}' (一致: {match})")
            
            # 不一致の確認
            missing_in_csv = []
            for dept_key, category in DEPARTMENT_TO_CATEGORY_MAPPING.items():
                if dept_key != 'basic' and category not in csv_categories:
                    missing_in_csv.append((dept_key, category))
            
            if missing_in_csv:
                print(f"\n🚨 マッピングエラー検出:")
                for dept_key, category in missing_in_csv:
                    print(f"   {dept_key} -> '{category}' (CSVに存在しない)")
        else:
            print("CSVファイル読み込みエラー")
    else:
        print(f"CSVファイルが存在しません: {csv_path}")

if __name__ == '__main__':
    verify_mapping()