#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
実際のアプリの問題取得フローを再現テスト
start_exam -> get_department_questions_ultrasync の完全シミュレーション
"""

import sys
import os
import csv
import random
import json
import logging
from datetime import datetime

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def simulate_get_department_questions_ultrasync(department_name, question_count=10):
    """
    app.pyのget_department_questions_ultrasync関数を完全再現
    """
    print(f"\\n=== get_department_questions_ultrasync シミュレーション ===")
    print(f"部門: {department_name}, 問題数: {question_count}")
    
    # Step 1: CSV_JAPANESE_CATEGORIESマッピング確認
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
    
    if department_name not in CSV_JAPANESE_CATEGORIES:
        logger.error(f"ERROR: 未対応部門 - {department_name}")
        return []
    
    target_category = CSV_JAPANESE_CATEGORIES[department_name]
    logger.info(f"期待カテゴリ: {target_category}")
    
    # Step 2: 基礎科目の特別処理
    if target_category == "共通":
        print("基礎科目処理（スキップ）")
        return []
    
    # Step 3: 専門科目の厳密処理
    VALID_YEARS = [2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019]
    specialist_questions = []
    
    def load_questions_improved(csv_path):
        """utils.pyのload_questions_improved簡易版"""
        questions = []
        if not os.path.exists(csv_path):
            return questions
            
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                questions.append(dict(row))
        return questions
    
    # 年度別にデータを読み込み
    for year in VALID_YEARS:
        csv_path = f'rccm-quiz-app/data/4-2_{year}.csv'
        print(f"年度ファイル確認: {csv_path}")
        
        if not os.path.exists(csv_path):
            print(f"  ファイル不存在: {csv_path}")
            continue
            
        try:
            year_data = load_questions_improved(csv_path)
            print(f"  読み込み成功: {len(year_data)}問")
            
            for row in year_data:
                row_category = row.get('category', '').strip()
                
                # カテゴリマッチング
                if row_category == target_category:
                    specialist_questions.append({
                        'id': 20000 + int(row.get('id', 0)),
                        'question': row.get('question', ''),
                        'option_a': row.get('option_a', ''),
                        'option_b': row.get('option_b', ''),
                        'option_c': row.get('option_c', ''),
                        'option_d': row.get('option_d', ''),
                        'correct_answer': row.get('correct_answer', ''),
                        'category': target_category,
                        'question_type': 'specialist',
                        'year': year
                    })
            
            matched_count = sum(1 for row in year_data if row.get('category', '').strip() == target_category)
            print(f"  マッチング: {matched_count}問 (カテゴリ: {target_category})")
                    
        except Exception as year_error:
            logger.warning(f"  年度読み込み失敗: {csv_path} - {year_error}")
            continue
    
    print(f"\\n全体の収集結果: {len(specialist_questions)}問")
    
    # Step 4: 厳密な結果検証
    if specialist_questions:
        # カテゴリ統一性の最終確認
        categories_found = set(q.get('category') for q in specialist_questions)
        print(f"発見されたカテゴリ: {categories_found}")
        
        if len(categories_found) != 1 or target_category not in categories_found:
            logger.error(f"ERROR: カテゴリ混在検出 - 期待:{target_category}, 実際:{categories_found}")
            # 不正な問題を除外
            before_count = len(specialist_questions)
            specialist_questions = [q for q in specialist_questions if q.get('category') == target_category]
            print(f"除外処理: {before_count} -> {len(specialist_questions)}問")
        
        if len(specialist_questions) >= question_count:
            selected = random.sample(specialist_questions, question_count)
            logger.info(f"選択成功: {len(selected)}問 (全{len(specialist_questions)}問中)")
            
            # 最終検証: 選択された問題が全て正しいカテゴリか確認
            for q in selected:
                if q.get('category') != target_category:
                    logger.error(f"ERROR: 混在問題検出 ID:{q.get('id')} 期待:{target_category} 実際:{q.get('category')}")
            
            return selected
        else:
            logger.warning(f"WARNING: 問題不足 - {len(specialist_questions)}/{question_count}")
            return specialist_questions
    else:
        logger.error(f"ERROR: {department_name}で問題が見つからない")
        return []

def analyze_question_mixing(questions, department_name):
    """問題の分野混在を詳細分析"""
    print(f"\\n=== 分野混在分析: {department_name} ===")
    
    # 全分野のキーワード
    field_keywords = {
        '道路': ['道路', '舗装', '路面', '歩道', '交差点', '交通'],
        '河川・砂防': ['河川', '砂防', '治水', '防災', '堤防', '流域'],
        'トンネル': ['トンネル', '掘削', '覆工', '坑道', '支保'],
        '森林土木': ['森林', '治山', '林道', '森林整備', '木材'],
        '農業土木': ['農業', '灌漑', '排水', '農地', '用水'],
        '建設環境': ['環境', '騒音', '振動', '大気汚染', '環境影響', '生態系'],
        '造園': ['造園', '植栽', '緑地', '公園', '景観'],
        '都市計画': ['都市計画', '地域計画', '土地利用', '開発'],
        '鋼構造・コンクリート': ['鋼構造', 'コンクリート', '構造設計', '耐震'],
        '土質・基礎': ['土質', '基礎', '地盤', '支持力', '沈下'],
        '施工計画': ['施工', '工程', '品質管理', '安全管理', '積算'],
        '上下水道': ['上水道', '下水道', '浄水', '配水', '水処理']
    }
    
    mixing_analysis = {
        'total_questions': len(questions),
        'mixing_detected': 0,
        'details': []
    }
    
    for i, q in enumerate(questions, 1):
        question_text = q.get('question', '')
        detected_fields = []
        
        for field, keywords in field_keywords.items():
            if field != department_name:  # 自分の分野以外をチェック
                for keyword in keywords:
                    if keyword in question_text:
                        detected_fields.append(field)
                        break
        
        if detected_fields:
            mixing_analysis['mixing_detected'] += 1
            detail = {
                'question_number': i,
                'question_id': q.get('id'),
                'detected_fields': detected_fields,
                'question_preview': question_text[:150] + '...' if len(question_text) > 150 else question_text
            }
            mixing_analysis['details'].append(detail)
            print(f"問題{i}: 他分野キーワード検出 {detected_fields}")
            print(f"  ID: {q.get('id')}, カテゴリ: {q.get('category')}")
            print(f"  問題文: {question_text[:100]}...")
    
    mixing_rate = (mixing_analysis['mixing_detected'] / mixing_analysis['total_questions']) * 100
    print(f"\\n混在検出率: {mixing_analysis['mixing_detected']}/{mixing_analysis['total_questions']} ({mixing_rate:.1f}%)")
    
    return mixing_analysis

def main():
    """メイン診断処理"""
    print("実際のアプリの問題取得フロー再現テスト")
    print("=" * 60)
    
    # テスト対象部門
    departments_to_test = [
        '建設環境',
        '森林土木', 
        '農業土木',
        'トンネル'
    ]
    
    all_results = {}
    
    for department in departments_to_test:
        print(f"\\n{'='*80}")
        print(f"部門テスト: {department}")
        print('='*80)
        
        # 問題取得シミュレーション
        questions = simulate_get_department_questions_ultrasync(department, 10) 
        
        if questions:
            # 分野混在分析
            mixing_analysis = analyze_question_mixing(questions, department)
            all_results[department] = mixing_analysis
        else:
            print(f"ERROR: {department}の問題取得に失敗")
            all_results[department] = {'error': '問題取得失敗'}
    
    # 結果サマリー
    print(f"\\n{'='*80}")
    print("最終結果サマリー")  
    print('='*80)
    
    for dept, result in all_results.items():
        if 'error' in result:
            print(f"{dept}: {result['error']}")
        else:
            mixing_rate = (result['mixing_detected'] / result['total_questions']) * 100
            print(f"{dept}: {result['mixing_detected']}/{result['total_questions']}問で混在検出 ({mixing_rate:.1f}%)")
    
    # 結果をファイルに保存
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result_file = f"real_app_flow_test_results_{timestamp}.json"
    
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    
    print(f"\\n詳細結果をファイルに保存: {result_file}")

if __name__ == "__main__":
    main()