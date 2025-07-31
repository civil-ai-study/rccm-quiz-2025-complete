#!/usr/bin/env python3
"""
RCCMクイズアプリケーション年度問題調査スクリプト
有効年度(2015-2019)が無効年度として扱われる問題の根本原因特定
"""

import os
import sys
import csv
import json
from collections import defaultdict

def main():
    print("=== RCCM Quiz App Year Investigation ===")
    
    # データディレクトリパス
    data_dir = r"C:\Users\ABC\Desktop\rccm-quiz-app\rccm-quiz-app\data"
    if not os.path.exists(data_dir):
        print(f"Error: Data directory not found: {data_dir}")
        return
    
    print(f"Data directory: {data_dir}")
    
    # 1. 利用可能なCSVファイル確認
    print("\n1. 利用可能な年度ファイル確認:")
    csv_files = []
    for filename in os.listdir(data_dir):
        if filename.startswith('4-2_') and filename.endswith('.csv') and 'backup' not in filename:
            csv_files.append(filename)
    
    csv_files.sort()
    years_available = []
    
    for csv_file in csv_files:
        filepath = os.path.join(data_dir, csv_file)
        if os.path.exists(filepath):
            # 年度抽出
            year_str = csv_file.replace('4-2_', '').replace('.csv', '')
            try:
                year = int(year_str)
                years_available.append(year)
                
                # ファイルの行数カウント
                with open(filepath, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    problem_count = len(lines) - 1  # ヘッダー除く
                    
                print(f"  ✅ {csv_file}: {year}年度, {problem_count}問")
                
            except ValueError:
                print(f"  ⚠️  {csv_file}: 年度抽出エラー")
    
    print(f"\n📊 利用可能年度: {sorted(years_available)}")
    print(f"📊 総年度数: {len(years_available)}年度")
    
    # 2. 2015年と2016年のデータ詳細確認
    print("\n2. 問題となっている年度の詳細確認:")
    
    target_years = [2015, 2016, 2017, 2018, 2019]
    for year in target_years:
        csv_file = f"4-2_{year}.csv"
        filepath = os.path.join(data_dir, csv_file)
        
        if not os.path.exists(filepath):
            print(f"  ❌ {year}年度: ファイル未存在 ({csv_file})")
            continue
            
        print(f"\n  📋 {year}年度詳細分析:")
        try:
            departments = defaultdict(int)
            valid_records = 0
            error_records = 0
            
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for i, row in enumerate(reader, 1):
                    try:
                        # 必須フィールドチェック
                        if 'category' not in row or 'year' not in row:
                            error_records += 1
                            print(f"    ⚠️  行{i}: 必須フィールド不足 - {list(row.keys())}")
                            continue
                        
                        category = row['category'].strip()
                        year_in_data = row['year'].strip()
                        
                        # 年度データ検証
                        if not year_in_data or year_in_data != str(year):
                            error_records += 1
                            print(f"    ⚠️  行{i}: 年度不整合 - 期待:{year}, 実際:'{year_in_data}'")
                            continue
                        
                        departments[category] += 1
                        valid_records += 1
                        
                    except Exception as e:
                        error_records += 1
                        print(f"    ❌ 行{i}: 読み込みエラー - {e}")
            
            print(f"    📊 有効レコード: {valid_records}件")
            print(f"    📊 エラーレコード: {error_records}件")
            print(f"    📊 部門別問題数:")
            
            for dept, count in sorted(departments.items()):
                print(f"      - {dept}: {count}問")
                
        except Exception as e:
            print(f"    ❌ ファイル読み込みエラー: {e}")
    
    # 3. app.py内の年度バリデーション設定確認
    print("\n3. app.py内の年度バリデーション確認:")
    
    app_py_path = r"C:\Users\ABC\Desktop\rccm-quiz-app\rccm-quiz-app\app.py"
    if os.path.exists(app_py_path):
        try:
            with open(app_py_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # VALID_YEARS定数を探す
            if 'VALID_YEARS' in content:
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if 'VALID_YEARS' in line and ('=' in line or '[' in line):
                        print(f"  📝 行{i+1}: {line.strip()}")
                        # 次の数行も確認
                        for j in range(1, 5):
                            if i+j < len(lines) and (']' in lines[i+j] or ',' in lines[i+j]):
                                print(f"  📝 行{i+j+1}: {lines[i+j].strip()}")
                                if ']' in lines[i+j]:
                                    break
            else:
                print("  ⚠️  VALID_YEARS定数が見つかりません")
                
        except Exception as e:
            print(f"  ❌ app.py読み込みエラー: {e}")
    else:
        print(f"  ❌ app.py が見つかりません: {app_py_path}")
    
    # 4. 結果サマリー
    print("\n4. 調査結果サマリー:")
    print("=" * 50)
    
    print(f"📊 CSVファイルで利用可能な年度: {sorted(years_available)}")
    
    missing_years = []
    for year in range(2015, 2020):
        if year not in years_available:
            missing_years.append(year)
    
    if missing_years:
        print(f"❌ 不足している年度: {missing_years}")
    else:
        print("✅ 2015-2019年度は全て利用可能")
    
    # 造園部門2016年テスト
    print(f"\n5. 造園部門2016年問題テスト:")
    test_year = 2016
    test_dept = "造園"
    csv_file = f"4-2_{test_year}.csv"
    filepath = os.path.join(data_dir, csv_file)
    
    if os.path.exists(filepath):
        try:
            landscape_questions = 0
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get('category', '').strip() == test_dept:
                        landscape_questions += 1
            
            print(f"  📊 {test_dept}部門{test_year}年度: {landscape_questions}問")
            
            if landscape_questions > 0:
                print(f"  ✅ {test_dept}部門{test_year}年度の問題は存在します")
            else:
                print(f"  ❌ {test_dept}部門{test_year}年度の問題が見つかりません")
                
                # 利用可能な部門を確認
                with open(filepath, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    available_depts = set()
                    for row in reader:
                        dept = row.get('category', '').strip()
                        if dept:
                            available_depts.add(dept)
                    
                    print(f"  📋 {test_year}年度で利用可能な部門: {sorted(available_depts)}")
                    
        except Exception as e:
            print(f"  ❌ テストエラー: {e}")
    else:
        print(f"  ❌ {test_year}年度ファイルが存在しません")

if __name__ == "__main__":
    main()