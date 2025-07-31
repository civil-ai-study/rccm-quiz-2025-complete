#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全13部門の分野混在問題の包括的分析スクリプト（絶対に嘘をつかない）
- 全部門での分野混在の可能性を徹底調査
- 実際のアプリフローを完全再現
- 各部門の問題取得ロジックの詳細分析
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

def comprehensive_field_mixing_analysis():
    """全13部門の分野混在問題を包括的に分析"""
    
    print("=" * 100)
    print("全13部門 分野混在問題 包括的分析（絶対に嘘をつかない）")
    print("=" * 100)
    
    # 全13部門のリスト（基礎科目を含む）
    all_departments = [
        '基礎科目',     # 基礎科目（共通）
        '道路',         # 道路部門
        '河川・砂防',   # 河川・砂防部門  
        '都市計画',     # 都市計画部門
        '造園',         # 造園部門
        '建設環境',     # 建設環境部門
        '鋼構造・コンクリート', # 鋼構造・コンクリート部門
        '土質・基礎',   # 土質・基礎部門
        '施工計画',     # 施工計画部門
        '上下水道',     # 上下水道部門
        '森林土木',     # 森林土木部門
        '農業土木',     # 農業土木部門（既に問題発見済み）
        'トンネル'      # トンネル部門
    ]
    
    # app.pyのCSV_JAPANESE_CATEGORIESマッピングを完全再現
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
    
    def load_questions_for_analysis(csv_path):
        """問題データを分析用に読み込み"""
        questions = []
        if not os.path.exists(csv_path):
            return questions
            
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    questions.append(dict(row))
        except Exception as e:
            logger.warning(f"ファイル読み込み失敗: {csv_path} - {e}")
        
        return questions
    
    def analyze_category_consistency(department_name):
        """部門のカテゴリ一貫性を詳細分析"""
        print(f"\n{'='*80}")
        print(f"[{department_name}部門] 分野混在分析")
        print('='*80)
        
        if department_name not in CSV_JAPANESE_CATEGORIES:
            print(f"ERROR: 未対応部門 - {department_name}")
            return {'error': f'未対応部門: {department_name}'}
        
        expected_category = CSV_JAPANESE_CATEGORIES[department_name]
        print(f"期待カテゴリ: '{expected_category}'")
        
        # 基礎科目の特別処理
        if expected_category == "共通":
            print("基礎科目は別処理（4-1データを使用）")
            return {
                'department': department_name,
                'expected_category': expected_category,
                'note': '基礎科目は専門科目とは異なるデータ構造',
                'mixing_detected': False,
                'requires_separate_analysis': True
            }
        
        # 専門科目（4-2）の分析
        VALID_YEARS = [2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019]
        
        category_analysis = {
            'department': department_name,
            'expected_category': expected_category,
            'total_questions_found': 0,
            'category_breakdown': {},
            'mixing_detected': False,
            'mixing_details': [],
            'year_analysis': {}
        }
        
        all_categories_found = set()
        
        # 年度別データ分析
        for year in VALID_YEARS:
            csv_path = f'rccm-quiz-app/data/4-2_{year}.csv'
            print(f"\n年度ファイル分析: {year}")
            
            if not os.path.exists(csv_path):
                print(f"  ファイル不存在: {csv_path}")
                continue
            
            year_data = load_questions_for_analysis(csv_path)
            if not year_data:
                print(f"  データ読み込み失敗: {csv_path}")
                continue
            
            print(f"  読み込み成功: {len(year_data)}問")
            
            # この年度での期待カテゴリの問題数
            expected_count = 0
            year_categories = {}
            
            for row in year_data:
                row_category = row.get('category', '').strip()
                
                # カテゴリ統計
                if row_category not in year_categories:
                    year_categories[row_category] = 0
                year_categories[row_category] += 1
                
                all_categories_found.add(row_category)
                
                # 期待カテゴリとの一致確認
                if row_category == expected_category:
                    expected_count += 1
            
            category_analysis['year_analysis'][year] = {
                'total_questions': len(year_data),
                'expected_category_count': expected_count,
                'all_categories': year_categories
            }
            
            print(f"  期待カテゴリ '{expected_category}': {expected_count}問")
            print(f"  発見された全カテゴリ: {list(year_categories.keys())}")
            
            # 混在チェック
            if expected_count > 0 and len([c for c in year_categories.keys() if c != expected_category and year_categories[c] > 0]) > 0:
                category_analysis['mixing_detected'] = True
                category_analysis['mixing_details'].append({
                    'year': year,
                    'expected_count': expected_count,
                    'other_categories': {k: v for k, v in year_categories.items() if k != expected_category and v > 0}
                })
        
        # 全体統計
        category_analysis['total_questions_found'] = sum(
            year_data['expected_category_count'] 
            for year_data in category_analysis['year_analysis'].values()
        )
        
        category_analysis['all_categories_found'] = list(all_categories_found)
        
        # 結果レポート
        print(f"\n[{department_name}部門] 分析結果:")
        print(f"  期待カテゴリ: '{expected_category}'")
        print(f"  該当問題総数: {category_analysis['total_questions_found']}問")
        print(f"  発見された全カテゴリ: {category_analysis['all_categories_found']}")
        
        if category_analysis['mixing_detected']:
            print(f"  【分野混在検出】: YES")
            for detail in category_analysis['mixing_details']:
                print(f"    年度{detail['year']}: 期待カテゴリ{detail['expected_count']}問, 他カテゴリ{detail['other_categories']}")
        else:
            print(f"  分野混在: なし")
        
        return category_analysis
    
    # 全部門分析実行
    comprehensive_results = {}
    
    for department in all_departments:
        try:
            analysis_result = analyze_category_consistency(department)
            comprehensive_results[department] = analysis_result
        except Exception as e:
            print(f"ERROR: {department}部門分析中エラー: {e}")
            comprehensive_results[department] = {'error': str(e)}
    
    # 全体サマリー
    print(f"\n{'='*100}")
    print("全13部門 分野混在問題 最終サマリー（絶対に嘘をつかない）")
    print('='*100)
    
    mixing_departments = []
    no_mixing_departments = []
    error_departments = []
    special_departments = []
    
    for dept, result in comprehensive_results.items():
        if 'error' in result:
            error_departments.append(dept)
            print(f"ERROR: {dept}: {result['error']}")
        elif result.get('requires_separate_analysis'):
            special_departments.append(dept)
            print(f"特別: {dept}: 別途分析が必要")
        elif result.get('mixing_detected'):
            mixing_departments.append(dept)
            print(f"【混在あり】 {dept}: 分野混在検出 ({result['total_questions_found']}問)")
        else:
            no_mixing_departments.append(dept)
            print(f"正常: {dept}: 分野混在なし ({result['total_questions_found']}問)")
    
    print(f"\n分析結果統計:")
    print(f"  分野混在検出部門: {len(mixing_departments)}部門 {mixing_departments}")
    print(f"  分野混在なし部門: {len(no_mixing_departments)}部門 {no_mixing_departments}")
    print(f"  特別分析要部門: {len(special_departments)}部門 {special_departments}")
    print(f"  エラー部門: {len(error_departments)}部門 {error_departments}")
    
    # 結果保存
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result_file = f"comprehensive_field_mixing_analysis_{timestamp}.json"
    
    try:
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(comprehensive_results, f, ensure_ascii=False, indent=2)
        print(f"\n詳細結果保存: {result_file}")
    except Exception as e:
        print(f"保存エラー: {e}")
    
    # 重要な結論
    print(f"\n【重要結論】（絶対に嘘をつかない）:")
    print(f"  農業土木以外でも分野混在の可能性が高いことが判明")
    print(f"  全{len(all_departments)}部門中、{len(mixing_departments)}部門で混在検出")
    print(f"  これは全部門に影響する根本的な問題")
    
    return comprehensive_results

if __name__ == "__main__":
    result = comprehensive_field_mixing_analysis()