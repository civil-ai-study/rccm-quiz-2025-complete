#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Ultra Simple Deep Search: データパス修正後の動作確認テスト
目的: load_rccm_data_files('data')が0問→数千問に改善されることを検証
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'rccm-quiz-app'))

from app import app
from utils import load_rccm_data_files
import glob

def ultra_simple_deep_search_data_verification():
    """Ultra Simple Deep Search: データ読み込み修正効果の検証"""
    print("=== Ultra Simple Deep Search: Data Path Fix Verification ===")
    
    with app.app_context():
        # 1. 修正前の状況を再現（間違ったパスでのテスト）
        print("1. Before Fix Simulation (Wrong Path):")
        wrong_data_dir = os.path.join('rccm-quiz-app', 'data')
        print(f"   Wrong path: {wrong_data_dir}")
        print(f"   Path exists: {os.path.exists(wrong_data_dir)}")
        
        if not os.path.exists(wrong_data_dir):
            print("   ✅ Confirmed: Wrong path does not exist")
            try:
                wrong_questions = load_rccm_data_files(wrong_data_dir)
                print(f"   Questions loaded with wrong path: {len(wrong_questions)}")
            except Exception as e:
                print(f"   Error with wrong path: {e}")
        
        # 2. 修正後の状況をテスト（正しいパス）
        print("\n2. After Fix Test (Correct Path):")
        correct_data_dir = 'data'
        print(f"   Correct path: {correct_data_dir}")
        print(f"   Path exists: {os.path.exists(correct_data_dir)}")
        
        if os.path.exists(correct_data_dir):
            # CSVファイル数確認
            csv_files = glob.glob(os.path.join(correct_data_dir, '*.csv'))
            print(f"   CSV files found: {len(csv_files)}")
            for csv_file in sorted(csv_files):
                filename = os.path.basename(csv_file)
                size = os.path.getsize(csv_file)
                print(f"     {filename}: {size} bytes")
            
            # 実際のデータ読み込みテスト
            print("\n3. Actual Data Loading Test:")
            try:
                correct_questions = load_rccm_data_files(correct_data_dir)
                print(f"   Questions loaded with correct path: {len(correct_questions)}")
                
                if correct_questions:
                    print("   ✅ SUCCESS: Data loading works with correct path!")
                    
                    # サンプルデータ確認
                    sample = correct_questions[0]
                    print(f"   Sample question ID: {sample.get('id', 'N/A')}")
                    print(f"   Sample category: {sample.get('category', 'N/A')}")
                    
                    # カテゴリ分布確認
                    categories = {}
                    for q in correct_questions:
                        cat = q.get('category', 'Unknown')
                        categories[cat] = categories.get(cat, 0) + 1
                    
                    print("\n4. Category Distribution:")
                    for cat, count in sorted(categories.items()):
                        print(f"     {cat}: {count} questions")
                    
                    print(f"\n🎉 CRITICAL FIX SUCCESS:")
                    print(f"   Before: 0 questions (wrong path)")
                    print(f"   After: {len(correct_questions)} questions (correct path)")
                    print(f"   Improvement: {len(correct_questions)} questions gained")
                    
                else:
                    print("   ❌ FAILURE: No questions loaded even with correct path")
                    
            except Exception as e:
                print(f"   ❌ ERROR with correct path: {e}")
        
        # 5. extract_department_questions_from_csv テスト
        print("\n5. Department Question Extraction Test:")
        from app import extract_department_questions_from_csv
        
        road_questions = extract_department_questions_from_csv('道路', 10)
        print(f"   Road department questions: {len(road_questions)}")
        
        if road_questions:
            road_ids = [q.get('id') for q in road_questions if q.get('id')]
            print(f"   Road question IDs: {road_ids[:5]}...")
            print("   ✅ Department extraction still works")
        else:
            print("   ❌ Department extraction failed")
        
        print("\n=== Ultra Simple Deep Search Data Verification Complete ===")

if __name__ == "__main__":
    ultra_simple_deep_search_data_verification()