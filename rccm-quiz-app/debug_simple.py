#!/usr/bin/env python3
"""
Simple debug script for investigating department mapping
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import csv

# Test department mapping from app.py (copied)
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

LEGACY_DEPARTMENT_ALIASES = {
    'river_sabo': 'civil_planning',
    'river': 'civil_planning',
    'construction_environment': 'construction_env',
    'construction_management': 'construction_planning',
    'water_supply_sewerage': 'water_supply',
    'forest_civil': 'forestry',
    'agricultural_civil': 'agriculture',
    'common': 'basic'
}

def resolve_department_alias(department):
    """部門IDのエイリアスを解決して正式な部門IDを返す"""
    if department in LEGACY_DEPARTMENT_ALIASES:
        resolved = LEGACY_DEPARTMENT_ALIASES[department]
        print(f"部門エイリアス変換: {department} → {resolved}")
        return resolved
    return department

def normalize_department_name(department_name):
    """部門名正規化"""
    if not department_name:
        return None
    
    # 既に正規化済みの場合
    if department_name in DEPARTMENT_TO_CATEGORY_MAPPING:
        return department_name
    
    # 旧名称の場合は新名称に変換
    if department_name in LEGACY_DEPARTMENT_ALIASES:
        return LEGACY_DEPARTMENT_ALIASES[department_name]
    
    # 不明な部門名
    return None

def get_department_category(department_name):
    """安全な部門→カテゴリ変換"""
    normalized = normalize_department_name(department_name)
    if normalized:
        return DEPARTMENT_TO_CATEGORY_MAPPING.get(normalized)
    return None

print("=== DEPARTMENT MAPPING TEST ===")
print(f"DEPARTMENT_TO_CATEGORY_MAPPING:")
for dept, cat in DEPARTMENT_TO_CATEGORY_MAPPING.items():
    print(f"  {dept} -> {cat}")

print(f"\nLEGACY_DEPARTMENT_ALIASES:")
for alias, dept in LEGACY_DEPARTMENT_ALIASES.items():
    print(f"  {alias} -> {dept}")

print(f"\n=== FLOW TEST ===")
test_flow = [
    'soil_foundation',
    'urban_planning',
    'soil',
    'urban'
]

for input_dept in test_flow:
    print(f"\nTesting department: {input_dept}")
    
    # Step 1: Resolve alias
    resolved = resolve_department_alias(input_dept)
    print(f"  1. Alias resolution: {input_dept} -> {resolved}")
    
    # Step 2: Normalize
    normalized = normalize_department_name(resolved)
    print(f"  2. Normalization: {resolved} -> {normalized}")
    
    # Step 3: Get category
    category = get_department_category(normalized)
    print(f"  3. Category mapping: {normalized} -> {category}")

print(f"\n=== DATA ANALYSIS ===")
# Check what's in the actual CSV files
data_dir = "/mnt/c/Users/ABC/Desktop/rccm-quiz-app/rccm-quiz-app/data"
csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv') and f.startswith('4-2')]

total_questions = 0
categories = {}

for csv_file in csv_files:
    try:
        with open(os.path.join(data_dir, csv_file), 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                total_questions += 1
                cat = row.get('category', 'unknown')
                if cat not in categories:
                    categories[cat] = 0
                categories[cat] += 1
    except Exception as e:
        print(f"Error reading {csv_file}: {e}")

print(f"Total specialist questions: {total_questions}")
print(f"Categories found:")
for cat, count in sorted(categories.items()):
    print(f"  {cat}: {count}")

# Check specific departments
target_departments = ['土質及び基礎', '都市計画及び地方計画']
for target_cat in target_departments:
    count = categories.get(target_cat, 0)
    print(f"\n{target_cat}: {count} questions")
    
    # Check which years have this category
    years_with_questions = []
    for csv_file in csv_files:
        try:
            with open(os.path.join(data_dir, csv_file), 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get('category') == target_cat:
                        year = csv_file.split('_')[1].split('.')[0]
                        if year not in years_with_questions:
                            years_with_questions.append(year)
                        break
        except Exception as e:
            print(f"Error checking {csv_file}: {e}")
    
    print(f"  Years with {target_cat}: {sorted(years_with_questions)}")