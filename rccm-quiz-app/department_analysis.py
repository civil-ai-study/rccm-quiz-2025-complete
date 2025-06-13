#!/usr/bin/env python3
"""
CSVファイルの部門データ分析スクリプト
"""
import csv
import os
from collections import defaultdict

def normalize_department(dept):
    """部門名を正規化"""
    if not dept:
        return dept
    
    # 基本的な正規化ルール
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
        '河川砂防海岸': '河川、砂防及び海岸・海洋',
    }
    
    return normalization_rules.get(dept, dept)

def analyze_csv_files():
    """CSVファイルを分析して部門統計を作成"""
    data_dir = '/mnt/c/Users/z285/Desktop/rccm-quiz-app/rccm-quiz-app/data'
    department_counts = defaultdict(int)
    file_departments = {}
    
    # CSVファイルのリストを取得
    csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
    
    print("=== CSVファイル分析結果 ===\n")
    
    for csv_file in sorted(csv_files):
        file_path = os.path.join(data_dir, csv_file)
        file_deps = set()
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if 'category' in row:
                        original_dept = row['category']
                        normalized_dept = normalize_department(original_dept)
                        department_counts[normalized_dept] += 1
                        file_deps.add(normalized_dept)
        except Exception as e:
            print(f"エラー {csv_file}: {e}")
            continue
        
        file_departments[csv_file] = sorted(list(file_deps))
        print(f"【{csv_file}】")
        print(f"  部門数: {len(file_deps)}")
        print(f"  部門: {', '.join(sorted(list(file_deps)))}")
        print()
    
    # 全体統計
    print("=== 全体統計 ===")
    print(f"総ファイル数: {len(csv_files)}")
    print(f"総部門数: {len(department_counts)}")
    print(f"総問題数: {sum(department_counts.values())}")
    print()
    
    print("=== 部門別問題数 ===")
    for dept, count in sorted(department_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"{dept}: {count}問")
    print()
    
    print("=== 正規化された部門一覧 ===")
    for i, dept in enumerate(sorted(department_counts.keys()), 1):
        print(f"{i:2d}. {dept}")

if __name__ == "__main__":
    analyze_csv_files()