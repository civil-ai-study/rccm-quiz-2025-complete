#!/usr/bin/env python3
"""
🔥 ULTRA SYNC直接検証システム
CLAUDE.md準拠: データファイル直接分析による完走テスト
"""

import os
import csv
import json
import time
from datetime import datetime
from collections import defaultdict, Counter

def load_csv_safe(file_path):
    """安全なCSV読み込み"""
    try:
        questions = []
        encodings = ['shift_jis', 'utf-8', 'cp932']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    reader = csv.DictReader(f)
                    questions = list(reader)
                    break
            except UnicodeDecodeError:
                continue
        
        return questions
    except Exception as e:
        print(f"❌ CSVファイル読み込みエラー {file_path}: {e}")
        return []

def verify_data_integrity():
    """データ整合性検証"""
    print("🔍 データ整合性検証開始")
    
    data_dir = '/mnt/c/Users/ABC/Desktop/rccm-quiz-app/rccm-quiz-app/data'
    
    # 基礎科目データ検証
    basic_file = os.path.join(data_dir, '4-1.csv')
    basic_questions = load_csv_safe(basic_file)
    print(f"📋 基礎科目: {len(basic_questions)}問")
    
    # 年度別専門科目データ検証
    specialist_questions = []
    year_stats = {}
    
    for year in range(2008, 2020):
        year_file = os.path.join(data_dir, f'4-2_{year}.csv')
        if os.path.exists(year_file):
            year_questions = load_csv_safe(year_file)
            year_stats[year] = len(year_questions)
            specialist_questions.extend(year_questions)
            print(f"📅 {year}年: {len(year_questions)}問")
    
    print(f"📊 専門科目総計: {len(specialist_questions)}問")
    
    return basic_questions, specialist_questions, year_stats

def test_category_distribution(specialist_questions):
    """カテゴリー分布テスト"""
    print("\n🏢 部門別問題分布分析")
    
    category_counts = Counter()
    for q in specialist_questions:
        category = q.get('category', '不明')
        category_counts[category] += 1
    
    # 13部門マッピング確認
    expected_categories = [
        '道路', 'トンネル', '河川、砂防及び海岸・海洋', '都市計画及び地方計画',
        '造園', '建設環境', '鋼構造及びコンクリート', '土質及び基礎',
        '施工計画、施工設備及び積算', '上水道及び工業用水道', 
        '森林土木', '農業土木'
    ]
    
    available_categories = 0
    for category in expected_categories:
        count = category_counts.get(category, 0)
        if count > 0:
            available_categories += 1
            print(f"✅ {category}: {count}問")
        else:
            # 類似カテゴリーを検索
            similar = [cat for cat in category_counts.keys() if category[:3] in cat]
            if similar:
                print(f"🔄 {category}: 類似カテゴリー {similar} で代替可能")
                available_categories += 1
            else:
                print(f"❌ {category}: 問題なし")
    
    coverage = (available_categories / len(expected_categories)) * 100
    print(f"📊 部門カバレッジ: {available_categories}/{len(expected_categories)} ({coverage:.1f}%)")
    
    return category_counts, coverage

def test_question_count_variations(category_counts):
    """問題数バリエーション完走テスト"""
    print("\n🔢 問題数バリエーション完走テスト")
    
    question_counts = [10, 20, 30]
    results = {}
    
    for category, available in category_counts.items():
        results[category] = {}
        for count in question_counts:
            if available >= count:
                results[category][count] = "✅ 可能"
            else:
                results[category][count] = f"❌ 不足({available}問)"
    
    # サマリー表示
    for count in question_counts:
        successful = sum(1 for cat_results in results.values() 
                        if cat_results.get(count, "").startswith("✅"))
        total = len(results)
        success_rate = (successful / total) * 100 if total > 0 else 0
        print(f"📊 {count}問テスト: {successful}/{total}部門対応 ({success_rate:.1f}%)")
    
    return results

def test_year_filtering(specialist_questions):
    """年度フィルタリング機能テスト"""
    print("\n📅 年度フィルタリング機能テスト")
    
    # 年度別統計
    year_category_stats = defaultdict(lambda: defaultdict(int))
    
    for q in specialist_questions:
        year = q.get('year', '不明')
        category = q.get('category', '不明')
        year_category_stats[year][category] += 1
    
    # 2019年道路部門テスト
    road_2019 = year_category_stats.get('2019', {}).get('道路', 0)
    if road_2019 > 0:
        print(f"✅ 2019年道路部門: {road_2019}問確認")
    else:
        print(f"❌ 2019年道路部門: 問題なし")
    
    # 年度別部門カバレッジ
    total_year_dept_combinations = 0
    covered_combinations = 0
    
    for year in range(2008, 2020):
        year_str = str(year)
        if year_str in year_category_stats:
            for category in year_category_stats[year_str]:
                total_year_dept_combinations += 1
                if year_category_stats[year_str][category] >= 10:
                    covered_combinations += 1
    
    coverage = (covered_combinations / total_year_dept_combinations * 100) if total_year_dept_combinations > 0 else 0
    print(f"📊 年度×部門10問以上カバレッジ: {covered_combinations}/{total_year_dept_combinations} ({coverage:.1f}%)")
    
    return year_category_stats, coverage

def test_random_capability(category_counts):
    """ランダム選択可能性テスト"""
    print("\n🎲 ランダム選択可能性テスト")
    
    random_capable_categories = 0
    total_categories = len(category_counts)
    
    for category, count in category_counts.items():
        if count >= 10:  # 最小10問でランダム選択可能
            random_capable_categories += 1
            print(f"✅ {category}: {count}問 (ランダム選択可能)")
        else:
            print(f"❌ {category}: {count}問 (ランダム選択不可)")
    
    random_coverage = (random_capable_categories / total_categories * 100) if total_categories > 0 else 0
    print(f"📊 ランダム選択対応: {random_capable_categories}/{total_categories}部門 ({random_coverage:.1f}%)")
    
    return random_coverage

def run_ultra_sync_verification():
    """ULTRA SYNC総合検証実行"""
    print("🔥 ULTRA SYNC総合検証開始")
    print("="*80)
    
    start_time = time.time()
    
    # 1. データ整合性検証
    basic_questions, specialist_questions, year_stats = verify_data_integrity()
    
    # 2. カテゴリー分布テスト
    category_counts, category_coverage = test_category_distribution(specialist_questions)
    
    # 3. 問題数バリエーションテスト
    variation_results = test_question_count_variations(category_counts)
    
    # 4. 年度フィルタリングテスト
    year_stats_detail, year_coverage = test_year_filtering(specialist_questions)
    
    # 5. ランダム選択可能性テスト
    random_coverage = test_random_capability(category_counts)
    
    # 総合評価
    elapsed_time = time.time() - start_time
    
    # CLAUDE.md基準評価
    scores = {
        'データ完備': 100 if len(basic_questions) > 0 and len(specialist_questions) > 0 else 0,
        '部門カバレッジ': category_coverage,
        '年度フィルタリング': year_coverage,
        'ランダム選択': random_coverage
    }
    
    total_score = sum(scores.values()) / len(scores)
    
    print("\n" + "="*80)
    print("🎯 ULTRA SYNC総合検証結果")
    print("="*80)
    print(f"📊 基礎科目: {len(basic_questions)}問")
    print(f"📊 専門科目: {len(specialist_questions)}問")
    print(f"📊 年度範囲: {min(year_stats.keys())}-{max(year_stats.keys())}")
    print(f"📊 総合スコア: {total_score:.1f}/100")
    
    for metric, score in scores.items():
        status = "✅" if score >= 80 else "⚠️" if score >= 60 else "❌"
        print(f"{status} {metric}: {score:.1f}%")
    
    print(f"⏱️ 実行時間: {elapsed_time:.2f}秒")
    print(f"📅 実行日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # CLAUDE.md基準判定
    if total_score >= 85:
        print("\n🏆 CLAUDE.md基準達成: ULTRA SYNC品質基準満足")
        return True
    else:
        print("\n⚠️ CLAUDE.md基準未達成: 改善が必要")
        return False

if __name__ == "__main__":
    try:
        success = run_ultra_sync_verification()
        exit(0 if success else 1)
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)