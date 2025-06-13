#!/usr/bin/env python3
"""
CSVデータとconfig.pyの部門設定のマッピング分析
"""
import csv
import os
from collections import defaultdict
from config import RCCMConfig

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

def create_csv_to_config_mapping():
    """CSVカテゴリからconfig部門IDへのマッピングを作成"""
    
    # CSVの実際の部門名からconfig.pyの部門IDへのマッピング
    csv_to_config_mapping = {
        # 完全一致するもの
        '道路': 'road',
        '河川、砂防及び海岸・海洋': 'civil_planning',
        '建設環境': 'construction_env', 
        '都市計画及び地方計画': 'urban_planning',
        '森林土木': 'forestry',
        '農業土木': 'agriculture',
        
        # 近い意味のもの
        '鋼構造及びコンクリート': 'construction_mgmt',  # 建設マネジメントの一部
        '土質及び基礎': 'construction_mgmt',  # 建設マネジメントの一部
        '施工計画、施工設備及び積算': 'construction_mgmt',  # 建設マネジメント
        '施工計画': 'construction_mgmt',  # 建設マネジメント
        '上水道及び工業用水道': 'civil_planning',  # 河川砂防に近い分野
        'トンネル': 'road',  # 道路の一部
        '造園': 'urban_planning',  # 都市計画に関連
        
        # 特別なカテゴリ
        '共通': 'basic_common',  # 基礎科目
        '未分類': 'uncategorized',
        'レガシーデータ': 'legacy'
    }
    
    return csv_to_config_mapping

def analyze_mapping():
    """マッピング分析実行"""
    data_dir = '/mnt/c/Users/z285/Desktop/rccm-quiz-app/rccm-quiz-app/data'
    department_counts = defaultdict(int)
    
    # CSVファイル分析
    for filename in os.listdir(data_dir):
        if not filename.endswith('.csv') or 'backup' in filename or 'fixed' in filename:
            continue
            
        filepath = os.path.join(data_dir, filename)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if 'category' in row:
                        dept = normalize_department(row['category'])
                        department_counts[dept] += 1
        except Exception as e:
            print(f"エラー処理中 {filename}: {e}")
            continue
    
    # マッピング作成
    csv_to_config = create_csv_to_config_mapping()
    
    print("=== CSVデータと設定のマッピング分析 ===\n")
    
    print("【CSVファイル内の実際の部門（正規化済み）】")
    for dept, count in sorted(department_counts.items(), key=lambda x: x[1], reverse=True):
        config_id = csv_to_config.get(dept, '未マッピング')
        config_name = ''
        if config_id in RCCMConfig.DEPARTMENTS:
            config_name = f" → {RCCMConfig.DEPARTMENTS[config_id]['name']}"
        elif config_id not in ['basic_common', 'uncategorized', 'legacy', '未マッピング']:
            config_name = f" → {config_id}"
        
        print(f"{dept:30s} : {count:4d}問 {config_name}")
    
    print(f"\n【統計】")
    print(f"CSV内部門数: {len(department_counts)}")
    print(f"Config定義部門数: {len(RCCMConfig.DEPARTMENTS)}")
    print(f"マッピング済み部門数: {len([d for d in department_counts.keys() if d in csv_to_config])}")
    
    print(f"\n【未マッピング部門】")
    unmapped = [dept for dept in department_counts.keys() if dept not in csv_to_config]
    if unmapped:
        for dept in unmapped:
            print(f"  - {dept}")
    else:
        print("  なし（全てマッピング済み）")
    
    print(f"\n【config.pyで定義されているがCSVにない部門】")
    config_only = []
    csv_mapped_configs = set(csv_to_config.values())
    for config_id, config_info in RCCMConfig.DEPARTMENTS.items():
        if config_id not in csv_mapped_configs:
            config_only.append(f"  - {config_id}: {config_info['name']}")
    
    if config_only:
        for item in config_only:
            print(item)
    else:
        print("  なし（全てCSVにマッピング済み）")
    
    print(f"\n【推奨マッピング辞書（Pythonコード）】")
    print("CSV_TO_CONFIG_DEPARTMENT_MAPPING = {")
    for csv_dept in sorted(department_counts.keys()):
        config_id = csv_to_config.get(csv_dept, '未マッピング')
        print(f"    '{csv_dept}': '{config_id}',")
    print("}")
    
    return csv_to_config, department_counts

if __name__ == "__main__":
    analyze_mapping()