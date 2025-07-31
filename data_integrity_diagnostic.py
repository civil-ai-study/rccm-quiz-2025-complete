#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
データ整合性診断スクリプト（ウルトラシンク・絶対に嘘をつかない）
専門家のベストプラクティスに基づく包括的データ診断
"""

import sys
import os
import csv
import json
import logging
from datetime import datetime
from collections import defaultdict, Counter

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def comprehensive_data_integrity_diagnostic():
    """
    専門家推奨のベストプラクティスに基づく包括的データ整合性診断
    - 各CSVファイルの構造分析
    - カテゴリ分布の詳細調査
    - データ品質指標の測定
    - 混在パターンの特定
    """
    
    print("=" * 100)
    print("データ整合性診断スクリプト（ウルトラシンク・絶対に嘘をつかない）")
    print("専門家のベストプラクティスに基づく包括的診断")
    print("=" * 100)
    
    # 対象年度とファイル
    VALID_YEARS = [2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019]
    
    # 期待される部門カテゴリマッピング（app.pyより）
    EXPECTED_CATEGORIES = {
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
    
    diagnostic_results = {
        'timestamp': datetime.now().isoformat(),
        'files_analyzed': 0,
        'total_records': 0,
        'data_quality_metrics': {},
        'category_distribution': {},
        'mixing_patterns': {},
        'field_validation': {},
        'recommendations': []
    }
    
    def safe_load_csv(file_path):
        """安全なCSV読み込み（専門家推奨のベストプラクティス）"""
        records = []
        field_issues = []
        
        if not os.path.exists(file_path):
            return records, ['file_not_found']
        
        try:
            # UTF-8エンコーディングで読み込み（2025年推奨）
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                # フィールド名の検証
                fieldnames = reader.fieldnames
                if not fieldnames:
                    field_issues.append('no_headers')
                    return records, field_issues
                
                # 必須フィールドの確認
                required_fields = ['id', 'category', 'question']
                missing_fields = [field for field in required_fields if field not in fieldnames]
                if missing_fields:
                    field_issues.append(f'missing_required_fields: {missing_fields}')
                
                # レコード読み込みと品質チェック
                row_number = 0
                for row in reader:
                    row_number += 1
                    
                    # データ品質チェック
                    if not row.get('category', '').strip():
                        field_issues.append(f'empty_category_row_{row_number}')
                    
                    if not row.get('question', '').strip():
                        field_issues.append(f'empty_question_row_{row_number}')
                    
                    # 前後の空白除去（2025年ベストプラクティス）
                    cleaned_row = {k: v.strip() if isinstance(v, str) else v for k, v in row.items()}
                    records.append(cleaned_row)
                    
        except UnicodeDecodeError:
            # Shift_JISエンコーディングでリトライ
            try:
                with open(file_path, 'r', encoding='shift_jis') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        cleaned_row = {k: v.strip() if isinstance(v, str) else v for k, v in row.items()}
                        records.append(cleaned_row)
                field_issues.append('encoding_shift_jis')
            except Exception as e:
                field_issues.append(f'encoding_error: {str(e)}')
                
        except Exception as e:
            field_issues.append(f'read_error: {str(e)}')
        
        return records, field_issues
    
    # 年度別ファイル診断
    for year in VALID_YEARS:
        csv_path = f'rccm-quiz-app/data/4-2_{year}.csv'
        print(f"\n{'='*80}")
        print(f"年度 {year} データ診断")
        print(f"ファイル: {csv_path}")
        print('='*80)
        
        records, issues = safe_load_csv(csv_path)
        
        if not records:
            print(f"ERROR: {year}年度データの読み込みに失敗")
            for issue in issues:
                print(f"  問題: {issue}")
            continue
        
        diagnostic_results['files_analyzed'] += 1
        diagnostic_results['total_records'] += len(records)
        
        print(f"読み込み成功: {len(records)}レコード")
        if issues:
            print(f"警告: {issues}")
        
        # カテゴリ分布分析
        category_counter = Counter()
        for record in records:
            category = record.get('category', '').strip()
            if category:
                category_counter[category] += 1
        
        year_key = f'year_{year}'
        diagnostic_results['category_distribution'][year_key] = dict(category_counter)
        
        print(f"\nカテゴリ分布 ({year}年度):")
        for category, count in category_counter.most_common():
            print(f"  {category}: {count}問")
        
        # データ品質指標
        total_records = len(records)
        empty_categories = sum(1 for r in records if not r.get('category', '').strip())
        empty_questions = sum(1 for r in records if not r.get('question', '').strip())
        
        quality_metrics = {
            'total_records': total_records,
            'empty_categories': empty_categories,
            'empty_questions': empty_questions,
            'category_completeness': (total_records - empty_categories) / total_records * 100,
            'question_completeness': (total_records - empty_questions) / total_records * 100,
            'unique_categories': len(category_counter),
            'issues_found': len(issues)
        }
        
        diagnostic_results['data_quality_metrics'][year_key] = quality_metrics
        
        print(f"\nデータ品質指標 ({year}年度):")
        print(f"  総レコード数: {quality_metrics['total_records']}")
        print(f"  空カテゴリ: {quality_metrics['empty_categories']}")
        print(f"  空問題文: {quality_metrics['empty_questions']}")
        print(f"  カテゴリ完全性: {quality_metrics['category_completeness']:.1f}%")
        print(f"  問題文完全性: {quality_metrics['question_completeness']:.1f}%")
        print(f"  ユニークカテゴリ数: {quality_metrics['unique_categories']}")
    
    # 全体分析とパターン検出
    print(f"\n{'='*100}")
    print("全体データ分析結果（ウルトラシンク・絶対に嘘をつかない）")
    print('='*100)
    
    print(f"分析ファイル数: {diagnostic_results['files_analyzed']}/{len(VALID_YEARS)}")
    print(f"総レコード数: {diagnostic_results['total_records']}")
    
    # カテゴリ混在パターン分析
    all_categories = set()
    for year_data in diagnostic_results['category_distribution'].values():
        all_categories.update(year_data.keys())
    
    print(f"\n発見された全カテゴリ ({len(all_categories)}個):")
    for category in sorted(all_categories):
        print(f"  - {category}")
    
    # 期待カテゴリとの照合
    expected_set = set(EXPECTED_CATEGORIES.values())
    found_set = all_categories
    
    print(f"\n期待カテゴリとの照合:")
    print(f"  期待カテゴリ数: {len(expected_set)}")
    print(f"  発見カテゴリ数: {len(found_set)}")
    
    missing_categories = expected_set - found_set
    extra_categories = found_set - expected_set
    
    if missing_categories:
        print(f"  欠落カテゴリ: {missing_categories}")
    
    if extra_categories:
        print(f"  予期しないカテゴリ: {extra_categories}")
    
    # 混在検出（各年度で12分野すべてが存在するかチェック）
    mixing_detected = False
    for year_key, categories in diagnostic_results['category_distribution'].items():
        if len(categories) >= 10:  # 10分野以上存在する場合は混在の可能性
            mixing_detected = True
            print(f"  {year_key}: {len(categories)}カテゴリ検出（混在の可能性）")
    
    diagnostic_results['mixing_patterns']['global_mixing_detected'] = mixing_detected
    
    # 推奨事項生成（専門家のベストプラクティスに基づく）
    recommendations = []
    
    if mixing_detected:
        recommendations.append("データ分離: 各カテゴリを個別ファイルに分離することを推奨")
        recommendations.append("フィルタリング強化: カテゴリ別データ取得ロジックの厳密化が必要")
    
    if any(metrics.get('category_completeness', 0) < 100 for metrics in diagnostic_results['data_quality_metrics'].values()):
        recommendations.append("データ品質向上: 空カテゴリレコードの修正が必要")
    
    recommendations.append("データ検証自動化: 継続的品質監視システムの導入を推奨")
    recommendations.append("バックアップ作成: 修正前の全データバックアップを推奨")
    
    diagnostic_results['recommendations'] = recommendations
    
    print(f"\n推奨事項:")
    for i, rec in enumerate(recommendations, 1):
        print(f"  {i}. {rec}")
    
    # 結果保存
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result_file = f"data_integrity_diagnostic_{timestamp}.json"
    
    try:
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(diagnostic_results, f, ensure_ascii=False, indent=2)
        print(f"\n診断結果保存: {result_file}")
    except Exception as e:
        print(f"保存エラー: {e}")
    
    return diagnostic_results

if __name__ == "__main__":
    result = comprehensive_data_integrity_diagnostic()