#!/usr/bin/env python3
"""
RCCM試験問題集アプリ - 年度混在チェック
年度選択時の問題フィルタリング処理を詳細に検証する
"""

import sys
import os
sys.path.append('.')

from utils import load_rccm_data_files
from app import validate_exam_parameters, get_mixed_questions
import random

def test_year_filtering():
    """年度フィルタリング機能の詳細テスト"""
    print("=== RCCM年度混在チェック - 詳細検証 ===")
    print()
    
    # データ読み込み
    print("1. データ読み込み")
    data_dir = 'data'
    all_questions = load_rccm_data_files(data_dir)
    print(f"総問題数: {len(all_questions)}問")
    print()
    
    # 年度別統計
    print("2. 年度別統計")
    year_stats = {}
    for q in all_questions:
        year = q.get('year')
        if year not in year_stats:
            year_stats[year] = []
        year_stats[year].append(q)
    
    print("年度別問題数:")
    for year in sorted(year_stats.keys(), key=lambda x: x if x is not None else 0):
        count = len(year_stats[year])
        if year is None:
            print(f"  年度なし（基礎科目）: {count}問")
        else:
            print(f"  {year}年度: {count}問")
    print()
    
    # 年度指定フィルタリングテスト
    print("3. 年度指定フィルタリングテスト")
    test_years = [2019, 2018, 2017, 2008]
    
    for test_year in test_years:
        print(f"\n--- {test_year}年度の問題取得テスト ---")
        
        # 直接フィルタリング
        direct_filtered = [q for q in all_questions if str(q.get('year', '')) == str(test_year)]
        print(f"直接フィルタリング結果: {len(direct_filtered)}問")
        
        # 部門別確認
        departments = set()
        for q in direct_filtered:
            dept = q.get('department', q.get('category', '不明'))
            departments.add(dept)
        print(f"含まれる部門: {sorted(departments)}")
        
        # 年度混在チェック
        mixed_years = set()
        for q in direct_filtered:
            year = q.get('year')
            if year is not None:
                mixed_years.add(year)
        
        if len(mixed_years) == 1 and test_year in mixed_years:
            print(f"✅ 年度混在チェック: 正常 - {test_year}年度のみ")
        else:
            print(f"❌ 年度混在検出: {mixed_years}")
            
        # get_mixed_questions関数でのテスト
        print(f"\nget_mixed_questions関数テスト:")
        session_mock = {}
        try:
            filtered_questions = get_mixed_questions(
                session_mock, all_questions, '全体', 10, '', 'specialist', test_year
            )
            print(f"get_mixed_questions結果: {len(filtered_questions)}問")
            
            # 年度チェック
            question_years = set()
            for q in filtered_questions:
                year = q.get('year')
                if year is not None:
                    question_years.add(year)
            
            if len(question_years) == 1 and test_year in question_years:
                print(f"✅ get_mixed_questions年度チェック: 正常 - {test_year}年度のみ")
            else:
                print(f"❌ get_mixed_questions年度混在: {question_years}")
                
        except Exception as e:
            print(f"❌ get_mixed_questions関数エラー: {e}")
    
    print("\n4. 年度ランダム選択テスト")
    print("--- 年度指定なし（ランダム）の場合 ---")
    session_mock = {}
    try:
        random_questions = get_mixed_questions(
            session_mock, all_questions, '全体', 20, '', 'specialist', None
        )
        print(f"ランダム選択結果: {len(random_questions)}問")
        
        # 年度分布確認
        year_distribution = {}
        for q in random_questions:
            year = q.get('year')
            year_distribution[year] = year_distribution.get(year, 0) + 1
        
        print("年度分布:")
        for year in sorted(year_distribution.keys(), key=lambda x: x if x is not None else 0):
            count = year_distribution[year]
            if year is None:
                print(f"  年度なし（基礎科目）: {count}問")
            else:
                print(f"  {year}年度: {count}問")
        
        # 年度バランス確認
        specialist_years = [y for y in year_distribution.keys() if y is not None]
        if len(specialist_years) >= 3:
            print("✅ 年度ランダム選択: 正常 - 複数年度から選択されています")
        else:
            print(f"⚠️ 年度ランダム選択: 年度バリエーションが少ない - {specialist_years}")
            
    except Exception as e:
        print(f"❌ 年度ランダム選択エラー: {e}")
    
    print("\n5. 年度パラメータ検証テスト")
    print("--- validate_exam_parameters関数での年度検証 ---")
    
    # 有効な年度のテスト
    valid_years = [2008, 2010, 2015, 2019]
    for year in valid_years:
        errors = validate_exam_parameters(year=year)
        if not errors:
            print(f"✅ {year}年度: 有効")
        else:
            print(f"❌ {year}年度: エラー - {errors}")
    
    # 無効な年度のテスト
    invalid_years = [2007, 2020, 2021, 1999]
    for year in invalid_years:
        errors = validate_exam_parameters(year=year)
        if errors:
            print(f"✅ {year}年度: 正常に無効と判定 - {errors}")
        else:
            print(f"❌ {year}年度: 無効年度が通ってしまいました")
    
    print("\n=== 年度混在チェック完了 ===")

if __name__ == "__main__":
    test_year_filtering()