#!/usr/bin/env python3
"""
RCCM試験問題集アプリ - 12専門分野混在検証スクリプト
各分野での問題選択フローでの混在を厳密にチェックします
"""

import random
import csv
import os
from collections import defaultdict

def main():
    print('=== RCCM 12専門分野混在検証 ===')
    print()

    # 部門マッピング
    DEPARTMENT_TO_CATEGORY_MAPPING = {
        'road': '道路',
        'tunnel': 'トンネル',
        'civil_planning': '河川、砂防及び海岸・海洋',
        'urban_planning': '都市計画及び地方計画',
        'landscape': '造園',
        'construction_env': '建設環境',
        'steel_concrete': '鋼構造及びコンクリート',
        'soil_foundation': '土質及び基礎',
        'construction_planning': '施工計画、施工設備及び積算',
        'water_supply': '上水道及び工業用水道',
        'forestry': '森林土木',
        'agriculture': '農業土木'
    }

    # 全問題データを読み込み
    all_questions = []
    for filename in os.listdir('data'):
        if filename.endswith('.csv') and filename != '4-1.csv':  # 共通問題を除外
            filepath = os.path.join('data', filename)
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if 'category' in row and row['category'].strip():
                            all_questions.append({
                                'id': row.get('id', ''),
                                'category': row['category'].strip(),
                                'year': row.get('year', ''),
                                'question': row.get('question', '')[:50] + '...',
                                'file': filename
                            })
            except Exception as e:
                print(f'Error reading {filename}: {e}')

    print(f'読み込み総問題数: {len(all_questions)}')

    # 各部門で問題選択テスト
    test_results = {}
    detailed_issues = []

    for dept_id, expected_category in DEPARTMENT_TO_CATEGORY_MAPPING.items():
        print(f'\n--- {dept_id} ({expected_category}) のテスト ---')
        
        # 指定部門の問題のみを抽出
        dept_questions = [q for q in all_questions if q['category'] == expected_category]
        
        if not dept_questions:
            print(f'❌ 問題なし: {expected_category}')
            test_results[dept_id] = {'status': 'NO_DATA', 'issues': ['問題データなし']}
            detailed_issues.append(f'{dept_id}: データ不足')
            continue
        
        print(f'該当問題数: {len(dept_questions)}問')
        
        # ランダムサンプリングテスト（20問）
        sample_size = min(20, len(dept_questions))
        random.seed(42)  # 再現可能な結果のため
        sample_questions = random.sample(dept_questions, sample_size)
        
        categories_found = set()
        mixed_categories = set()
        mixed_examples = []
        
        for q in sample_questions:
            categories_found.add(q['category'])
            if q['category'] != expected_category:
                mixed_categories.add(q['category'])
                mixed_examples.append(f"ID:{q['id']} [{q['category']}] {q['file']}")
        
        # 結果判定
        if len(categories_found) == 1 and expected_category in categories_found:
            print(f'✅ 正常: {expected_category} のみ')
            test_results[dept_id] = {'status': 'OK', 'issues': []}
        else:
            print(f'❌ 混在検出: {sorted(categories_found)}')
            test_results[dept_id] = {'status': 'MIXED', 'issues': list(mixed_categories)}
            detailed_issues.extend(mixed_examples)
        
        # サンプル問題表示（最初の3問）
        print('サンプル問題:')
        for i, q in enumerate(sample_questions[:3], 1):
            status_mark = '✅' if q['category'] == expected_category else '❌'
            print(f'  {i}. [{q["category"]}] {q["question"]} {status_mark}')

    print()
    print('=== 全体の混在検証結果 ===')
    ok_count = sum(1 for r in test_results.values() if r['status'] == 'OK')
    mixed_count = sum(1 for r in test_results.values() if r['status'] == 'MIXED')
    no_data_count = sum(1 for r in test_results.values() if r['status'] == 'NO_DATA')

    print(f'正常な部門: {ok_count}/12')
    print(f'混在のある部門: {mixed_count}/12')
    print(f'データ不足の部門: {no_data_count}/12')

    if mixed_count == 0 and no_data_count == 0:
        print('\n✅ 全12分野で混在問題なし - 完全に分離されています')
    else:
        print('\n❌ 問題が検出されました:')
        for dept_id, result in test_results.items():
            if result['status'] != 'OK':
                category = DEPARTMENT_TO_CATEGORY_MAPPING[dept_id]
                print(f'  - {dept_id} ({category}): {result["status"]} - {result["issues"]}')
    
    # 詳細な問題リスト
    if detailed_issues:
        print('\n=== 詳細な問題リスト ===')
        for issue in detailed_issues[:10]:  # 最初の10件を表示
            print(f'  {issue}')
        if len(detailed_issues) > 10:
            print(f'  ... 他{len(detailed_issues) - 10}件')

    # 分野別統計
    print('\n=== 分野別問題数統計 ===')
    category_counts = defaultdict(int)
    for q in all_questions:
        category_counts[q['category']] += 1
    
    for category in sorted(DEPARTMENT_TO_CATEGORY_MAPPING.values()):
        count = category_counts[category]
        print(f'{category}: {count}問')

if __name__ == '__main__':
    main()