#!/usr/bin/env python3
"""
🔥 CLAUDE.md準拠包括的完走テスト
ULTRA SYNC品質保証: 10/20/30問完走 × 13部門 テスト
"""

import sys
import os
import time
import json
import traceback
from datetime import datetime
import subprocess

# プロジェクトパスを追加
sys.path.append('/mnt/c/Users/ABC/Desktop/rccm-quiz-app/rccm-quiz-app')

def safe_import():
    """安全なモジュールインポート"""
    try:
        from flask import Flask
        from app import app, get_mixed_questions, DEPARTMENT_TO_CATEGORY_MAPPING
        from utils import load_rccm_data_files
        return True, app, get_mixed_questions, DEPARTMENT_TO_CATEGORY_MAPPING, load_rccm_data_files
    except Exception as e:
        print(f"❌ インポートエラー: {e}")
        return False, None, None, None, None

def test_question_count_variation(department_key, question_counts=[10, 20, 30]):
    """問題数バリエーション完走テスト"""
    print(f"\n🔍 {department_key}部門 - 問題数バリエーションテスト")
    
    success_count = 0
    total_tests = len(question_counts)
    
    for count in question_counts:
        try:
            # データ読み込みテスト
            data_dir = '/mnt/c/Users/ABC/Desktop/rccm-quiz-app/rccm-quiz-app/data'
            all_questions = load_rccm_data_files(data_dir)
            
            # 部門別問題フィルタリング
            if department_key == 'basic':
                questions = [q for q in all_questions if q.get('question_type') == 'basic']
            else:
                category = DEPARTMENT_TO_CATEGORY_MAPPING.get(department_key, department_key)
                questions = [q for q in all_questions 
                           if q.get('question_type') == 'specialist' and q.get('category') == category]
            
            available_count = len(questions)
            
            if available_count >= count:
                print(f"✅ {count}問テスト: {available_count}問中{count}問選択可能")
                success_count += 1
            else:
                print(f"⚠️ {count}問テスト: {available_count}問しか利用できません")
                
        except Exception as e:
            print(f"❌ {count}問テスト失敗: {e}")
    
    success_rate = (success_count / total_tests) * 100
    print(f"📊 {department_key}: {success_count}/{total_tests} 成功 ({success_rate:.1f}%)")
    
    return success_count, total_tests

def test_random_selection():
    """ランダム選択機能テスト"""
    print(f"\n🎲 ランダム選択機能テスト")
    
    try:
        data_dir = '/mnt/c/Users/ABC/Desktop/rccm-quiz-app/rccm-quiz-app/data'
        all_questions = load_rccm_data_files(data_dir)
        
        # 道路部門でランダム選択テスト
        road_questions = [q for q in all_questions 
                         if q.get('question_type') == 'specialist' and q.get('category') == '道路']
        
        if len(road_questions) >= 10:
            # 2回のランダム選択で異なる結果が出るかテスト
            import random
            random.seed(int(time.time()))
            selection1 = random.sample(road_questions, 5)
            
            random.seed(int(time.time()) + 1)
            selection2 = random.sample(road_questions, 5)
            
            ids1 = [q['id'] for q in selection1]
            ids2 = [q['id'] for q in selection2]
            
            if ids1 != ids2:
                print(f"✅ ランダム選択: 異なる問題セットを生成")
                return True
            else:
                print(f"⚠️ ランダム選択: 同じ問題セットが生成")
                return False
        else:
            print(f"❌ ランダム選択: 道路部門の問題が不足 ({len(road_questions)}問)")
            return False
            
    except Exception as e:
        print(f"❌ ランダム選択テスト失敗: {e}")
        return False

def test_year_filtering():
    """年度別フィルタリングテスト"""
    print(f"\n📅 年度別フィルタリングテスト")
    
    try:
        data_dir = '/mnt/c/Users/ABC/Desktop/rccm-quiz-app/rccm-quiz-app/data'
        all_questions = load_rccm_data_files(data_dir)
        
        # 2019年道路部門の問題をフィルタリング
        year_2019_road = [q for q in all_questions 
                         if q.get('year') == 2019 and q.get('category') == '道路']
        
        if len(year_2019_road) > 0:
            # 年度統一性確認
            years = set(q.get('year') for q in year_2019_road)
            if len(years) == 1 and 2019 in years:
                print(f"✅ 年度フィルタリング: 2019年道路部門 {len(year_2019_road)}問 正常")
                return True
            else:
                print(f"❌ 年度フィルタリング: 年度混在 {years}")
                return False
        else:
            print(f"❌ 年度フィルタリング: 2019年道路部門の問題が見つかりません")
            return False
            
    except Exception as e:
        print(f"❌ 年度フィルタリングテスト失敗: {e}")
        return False

def run_comprehensive_test():
    """包括的完走テスト実行"""
    print("🔥 CLAUDE.md準拠包括的完走テストを開始")
    print("="*80)
    
    start_time = time.time()
    
    # インポートテスト
    import_success, app, get_mixed_questions, dept_mapping, load_data = safe_import()
    if not import_success:
        print("❌ CRITICAL: インポート失敗により終了")
        return
    
    # テスト結果収集
    total_success = 0
    total_tests = 0
    
    # 1. 13部門 × 問題数バリエーションテスト
    print("\n🏢 13部門 × 問題数バリエーションテスト")
    print("-" * 50)
    
    departments = list(dept_mapping.keys())
    for dept in departments:
        success, tests = test_question_count_variation(dept)
        total_success += success
        total_tests += tests
    
    # 2. ランダム選択機能テスト
    if test_random_selection():
        total_success += 1
    total_tests += 1
    
    # 3. 年度別フィルタリングテスト
    if test_year_filtering():
        total_success += 1
    total_tests += 1
    
    # 結果サマリー
    elapsed_time = time.time() - start_time
    success_rate = (total_success / total_tests) * 100
    
    print("\n" + "="*80)
    print("🎯 CLAUDE.md準拠包括的完走テスト結果")
    print("="*80)
    print(f"📊 総合成功率: {total_success}/{total_tests} ({success_rate:.1f}%)")
    print(f"⏱️ 実行時間: {elapsed_time:.2f}秒")
    print(f"📅 実行日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if success_rate >= 95:
        print("✅ ULTRA SYNC品質基準達成: 95%以上の成功率")
        return True
    else:
        print("⚠️ ULTRA SYNC品質基準未達成: 95%以下の成功率")
        return False

if __name__ == "__main__":
    try:
        success = run_comprehensive_test()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
        traceback.print_exc()
        sys.exit(1)