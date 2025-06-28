#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RCCM試験問題集CSVファイルのカテゴリー名統一化スクリプト
"""

import csv
import os
import glob
from datetime import datetime

# カテゴリー名の統一マッピング
CATEGORY_MAPPING = {
    # 河川・砂防関連
    "河川砂防": "河川、砂防及び海岸・海洋",
    "河川砂防海岸": "河川、砂防及び海岸・海洋",
    "河川砂防海岸海洋": "河川、砂防及び海岸・海洋",
    "河川砂防及び海岸・海洋": "河川、砂防及び海岸・海洋",
    "河川、砂防及び海岸･海洋": "河川、砂防及び海岸・海洋",
    "河川・砂防及び海岸・海洋": "河川、砂防及び海岸・海洋",
    "河川砂防海岸": "河川、砂防及び海岸・海洋",
    "未分類": "河川、砂防及び海岸・海洋",  # 河川関連問題として扱う
    
    # 鋼構造関連
    "鋼構造コンクリート": "鋼構造及びコンクリート",
    
    # 都市計画関連
    "都市計画地方計画": "都市計画及び地方計画",
    
    # 施工計画関連
    "施工計画・施工設備及び積算": "施工計画、施工設備及び積算",
    "施工計画施工設備積算": "施工計画、施工設備及び積算",
    "施工計画積算": "施工計画、施工設備及び積算",
    "施工計画": "施工計画、施工設備及び積算",
    
    # 上水道関連
    "上水道工業用水道": "上水道及び工業用水道",
}

def standardize_csv_categories(filename):
    """CSVファイルのカテゴリー名を統一化する"""
    
    print(f"\n処理開始: {filename}")
    
    # CSVファイルを読み込む
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)
    
    # ヘッダー行を確認
    if len(rows) == 0:
        print(f"  警告: {filename} は空のファイルです")
        return 0
    
    header = rows[0]
    if len(header) < 2 or header[1] != 'category':
        print(f"  警告: {filename} のフォーマットが想定と異なります")
        return 0
    
    # カテゴリー名を修正
    modified_count = 0
    category_changes = {}
    
    for i in range(1, len(rows)):
        if len(rows[i]) < 2:
            continue
            
        original_category = rows[i][1]
        
        # マッピングに基づいて変換
        if original_category in CATEGORY_MAPPING:
            new_category = CATEGORY_MAPPING[original_category]
            rows[i][1] = new_category
            modified_count += 1
            
            # 変更をログに記録
            if original_category not in category_changes:
                category_changes[original_category] = 0
            category_changes[original_category] += 1
    
    # 修正したファイルを書き出す
    if modified_count > 0:
        with open(filename, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(rows)
        
        print(f"  修正完了: {modified_count}行を変更")
        for old_cat, count in category_changes.items():
            print(f"    - '{old_cat}' → '{CATEGORY_MAPPING[old_cat]}' ({count}行)")
    else:
        print(f"  変更なし: 修正対象のカテゴリーが見つかりませんでした")
    
    return modified_count

def main():
    """メイン処理"""
    
    print("RCCM試験問題集CSVファイルのカテゴリー名統一化")
    print("=" * 50)
    
    # 処理対象のCSVファイルを取得
    csv_files = sorted(glob.glob("4-2_*.csv"))
    
    # backup や fixed などの特殊ファイルを除外
    csv_files = [f for f in csv_files if not ('backup' in f or 'fixed' in f)]
    
    print(f"対象ファイル数: {len(csv_files)}")
    
    total_modified = 0
    file_modified_count = 0
    
    # 各ファイルを処理
    for csv_file in csv_files:
        modified = standardize_csv_categories(csv_file)
        if modified > 0:
            file_modified_count += 1
            total_modified += modified
    
    # 結果サマリー
    print("\n" + "=" * 50)
    print("処理完了サマリー:")
    print(f"  処理ファイル数: {len(csv_files)}")
    print(f"  修正ファイル数: {file_modified_count}")
    print(f"  総修正行数: {total_modified}")
    
    # ログファイルに記録
    log_filename = f"category_standardization_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    with open(log_filename, 'w', encoding='utf-8') as f:
        f.write(f"カテゴリー名統一化処理ログ\n")
        f.write(f"処理日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"処理ファイル数: {len(csv_files)}\n")
        f.write(f"修正ファイル数: {file_modified_count}\n")
        f.write(f"総修正行数: {total_modified}\n")
    
    print(f"\nログファイル: {log_filename}")

if __name__ == "__main__":
    main()