#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分野混在問題の直接実証（シンプル版）
"""

import csv
import random
import os
from collections import defaultdict

def load_csv_data(file_path):
    """CSVデータを読み込み"""
    try:
        with open(file_path, 'r', encoding='utf-8', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            data = list(reader)
            print(f"データ読み込み成功: {len(data)}問")
            return data
    except Exception as e:
        print(f"データ読み込み失敗: {e}")
        return []

def main():
    print("=== 分野混在問題実証テスト ===")
    
    # CSVファイル読み込み
    csv_file = "data/4-2_2019.csv"
    questions = load_csv_data(csv_file)
    
    if not questions:
        return
    
    # カテゴリ分布確認
    category_counts = defaultdict(int)
    for q in questions:
        category = q.get('category', '不明')
        category_counts[category] += 1
    
    print("カテゴリ分布:")
    for category, count in sorted(category_counts.items()):
        print(f"  {category}: {count}問")
    print(f"合計: {len(questions)}問")
    print()
    
    # 道路部門問題のみ抽出
    road_questions = [q for q in questions if q.get('category') == '道路']
    print(f"道路カテゴリ問題数: {len(road_questions)}問")
    
    # 分野混在シミュレーション
    print("分野混在シミュレーション（全問題からランダム10問選択）:")
    if len(questions) >= 10:
        random_10 = random.sample(questions, 10)
        mixing_count = 0
        
        for i, q in enumerate(random_10, 1):
            category = q.get('category', '不明')
            if category != '道路':
                mixing_count += 1
                print(f"  問題{i}: 混在 - {category}")
            else:
                print(f"  問題{i}: 正常 - {category}")
        
        print(f"混在問題数: {mixing_count}/10")
        if mixing_count > 0:
            print("分野混在問題確認！")
        print()
    
    # 正しいフィルタリング
    print("正しいフィルタリング（道路問題のみから10問選択）:")
    if road_questions and len(road_questions) >= 10:
        road_10 = random.sample(road_questions, 10)
        
        for i, q in enumerate(road_10, 1):
            category = q.get('category', '不明')
            print(f"  問題{i}: {category}")
        
        print("全問題が道路カテゴリ - 分野混在なし")

if __name__ == "__main__":
    main()