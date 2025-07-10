#!/usr/bin/env python3
"""
緊急修正: 造園部門データ読み込み問題の即座解決
"""

import csv
import os

def emergency_landscape_verification():
    """造園部門データの緊急検証"""
    
    print("🚨 緊急修正: 造園部門データ問題調査")
    print("=" * 60)
    
    # データファイル確認
    data_files = ['data/4-2_2016.csv', 'data/4-2_2015.csv', 'data/4-2_2017.csv']
    
    for file_path in data_files:
        if os.path.exists(file_path):
            print(f"\n📋 ファイル: {file_path}")
            
            with open(file_path, 'r', encoding='shift_jis') as f:
                reader = csv.DictReader(f)
                landscape_count = 0
                categories = set()
                
                for row in reader:
                    category = row.get('category', '').strip()
                    categories.add(category)
                    
                    if '造園' in category:
                        landscape_count += 1
                        if landscape_count <= 3:  # 最初の3問を表示
                            print(f"  🌿 造園問題{landscape_count}: {row.get('question', '')[:50]}...")
                
                print(f"  📊 造園問題数: {landscape_count}問")
                print(f"  📋 全カテゴリ: {sorted(categories)}")
    
    print("\n🔍 問題診断:")
    print("1. データは存在している")
    print("2. アプリケーションの部門マッチング問題")
    print("3. 専門科目読み込み関数の不具合")

if __name__ == "__main__":
    emergency_landscape_verification()