#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RCCM分野混在問題の詳細診断ツール
実際の問題取得ロジックをテストして根本原因を特定
"""

import sys
import os
import csv
import random
import json
from datetime import datetime

# app.pyから必要な関数をインポートするためのパス設定
sys.path.append(os.path.join(os.path.dirname(__file__), 'rccm-quiz-app'))

def test_department_question_extraction():
    """
    各部門の問題取得をテストして混在問題を検出
    """
    print("RCCM分野混在問題の詳細診断")
    print("=" * 60)
    
    # テスト対象部門
    departments_to_test = [
        '建設環境',
        '森林土木', 
        '農業土木',
        'トンネル'
    ]
    
    # CSV_JAPANESE_CATEGORIESマッピング（app.pyから抽出）
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
    
    # 他分野キーワード検出用
    other_field_keywords = {
        '道路': ['道路', '舗装', '路面', '歩道'],
        '河川・砂防': ['河川', '砂防', '治水', '防災'],
        'トンネル': ['トンネル', '掘削', '覆工'],
        '森林土木': ['森林', '治山', '林道'],
        '農業土木': ['農業', '灌漑', '排水'],
        '建設環境': ['環境', '騒音', '振動', '大気汚染']
    }
    
    def load_questions_from_csv(file_path):
        """CSVファイルから問題を直接読み込み"""
        questions = []
        if not os.path.exists(file_path):
            return questions
            
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                questions.append(dict(row))
        return questions
    
    def extract_department_questions(department_name, question_count=10):
        """
        部門別問題抽出をシミュレート（app.pyのget_department_questions_ultrasyncをベース）
        """
        print(f"\\nテスト開始: {department_name}")
        print("-" * 40)
        
        if department_name not in CSV_JAPANESE_CATEGORIES:
            print(f"ERROR: 未対応部門 - {department_name}")
            return []
        
        target_category = CSV_JAPANESE_CATEGORIES[department_name]
        print(f"期待カテゴリ: {target_category}")
        
        # 専門科目データ読み込み（2019年のみをテスト）
        specialist_questions = []
        year = 2019
        csv_path = f"rccm-quiz-app/data/4-2_{year}.csv"
        
        if os.path.exists(csv_path):
            print(f"CSVファイル読み込み: {csv_path}")
            year_data = load_questions_from_csv(csv_path)
            print(f"読み込み問題数: {len(year_data)}")
            
            # カテゴリフィルタリング
            for row in year_data:
                row_category = row.get('category', '').strip()
                if row_category == target_category:
                    specialist_questions.append({
                        'id': row.get('id', ''),
                        'question': row.get('question', ''),
                        'category': row_category,
                        'year': year
                    })
            
            print(f"フィルタ後問題数: {len(specialist_questions)}")
            
            # カテゴリ統一性確認
            categories_found = set(q.get('category') for q in specialist_questions)
            print(f"発見されたカテゴリ: {categories_found}")
            
            if len(categories_found) != 1 or target_category not in categories_found:
                print(f"ERROR: カテゴリ混在検出 - 期待:{target_category}, 実際:{categories_found}")
                # 不正な問題を除外
                specialist_questions = [q for q in specialist_questions if q.get('category') == target_category]
                print(f"修正後問題数: {len(specialist_questions)}")
            
            # 10問選択をシミュレート
            if len(specialist_questions) >= question_count:
                selected = random.sample(specialist_questions, question_count)
                print(f"選択問題数: {len(selected)}")
                
                # 他分野キーワード検出テスト
                mixing_detected = 0
                for i, q in enumerate(selected, 1):
                    question_text = q.get('question', '')
                    detected_fields = []
                    
                    for field, keywords in other_field_keywords.items():
                        if field != department_name:  # 自分の分野以外をチェック
                            for keyword in keywords:
                                if keyword in question_text:
                                    detected_fields.append(field)
                                    break
                    
                    if detected_fields:
                        mixing_detected += 1
                        print(f"  問題{i}: 他分野キーワード検出 {detected_fields}")
                        print(f"    問題文先頭: {question_text[:100]}...")
                
                print(f"混在問題検出数: {mixing_detected}/{question_count}")
                return selected
            else:
                print(f"WARNING: 問題不足 - {len(specialist_questions)}/{question_count}")
                return specialist_questions
        else:
            print(f"ERROR: CSVファイルが見つからない - {csv_path}")
            return []
    
    # 各部門をテスト
    test_results = {}
    for dept in departments_to_test:
        questions = extract_department_questions(dept, 10)
        test_results[dept] = {
            'questions_found': len(questions),
            'categories': list(set(q.get('category', '') for q in questions))
        }
    
    # 結果サマリー
    print("\\n" + "=" * 60)
    print("テスト結果サマリー")
    print("=" * 60)
    
    for dept, result in test_results.items():
        print(f"{dept}: {result['questions_found']}問, カテゴリ: {result['categories']}")
    
    return test_results

def main():
    """メイン診断処理"""
    # カレントディレクトリ確認
    print(f"カレントディレクトリ: {os.getcwd()}")
    
    # 必要なファイルの存在確認
    data_dir = "rccm-quiz-app/data"
    if not os.path.exists(data_dir):
        print(f"ERROR: データディレクトリが見つかりません - {data_dir}")
        return
    
    # テスト実行
    results = test_department_question_extraction()
    
    # 結果をJSONファイルに保存
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result_file = f"department_mixing_diagnosis_{timestamp}.json"
    
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\\n診断結果をファイルに保存: {result_file}")

if __name__ == "__main__":
    main()