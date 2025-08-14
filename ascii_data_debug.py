#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ASCII互換 Ultra Simple Deep Search: データ読み込み完全失敗の根本原因特定
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'rccm-quiz-app'))

from app import app
from utils import load_rccm_data_files
import glob

def ascii_data_debug():
    """ASCII互換 データ読み込み完全失敗の根本原因を特定"""
    print("=== ASCII Ultra Simple Deep Search: Data Load Failure Debug ===")
    
    with app.app_context():
        # 1. all_questionsの読み込み
        data_dir = os.path.join('rccm-quiz-app', 'data')
        all_questions = load_rccm_data_files(data_dir)
        
        print(f"1. all_questions load result: {len(all_questions)} questions")
        
        # 2. data dirのファイル存在確認
        print(f"\n2. Data directory check:")
        print(f"   Directory exists: {os.path.exists(data_dir)}")
        
        if os.path.exists(data_dir):
            csv_files = glob.glob(os.path.join(data_dir, '*.csv'))
            print(f"   CSV files found: {len(csv_files)}")
            for csv_file in sorted(csv_files):
                filename = os.path.basename(csv_file)
                size = os.path.getsize(csv_file)
                print(f"     {filename}: {size} bytes")
        
        # 3. load_rccm_data_files内部処理確認
        print(f"\n3. load_rccm_data_files internal check:")
        try:
            # utils.pyから実際の処理を再実行
            import csv
            combined_data = []
            
            csv_files = glob.glob(os.path.join(data_dir, '*.csv'))
            print(f"   Files to process: {len(csv_files)}")
            
            for csv_file in sorted(csv_files):
                filename = os.path.basename(csv_file)
                print(f"   Processing: {filename}")
                
                try:
                    with open(csv_file, 'r', encoding='utf-8', errors='ignore') as f:
                        reader = csv.DictReader(f)
                        data = list(reader)
                        combined_data.extend(data)
                        print(f"     Loaded: {len(data)} rows")
                except Exception as e:
                    print(f"     ERROR loading {filename}: {e}")
            
            print(f"   Total combined data: {len(combined_data)} rows")
            
            # 4. 最初の数行を確認
            if combined_data:
                print(f"\n4. Sample data check:")
                sample = combined_data[0]
                print(f"   First row keys: {list(sample.keys())}")
                print(f"   First row id: {sample.get('id', 'NO_ID')}")
                print(f"   First row category: {sample.get('category', 'NO_CATEGORY')}")
            
        except Exception as e:
            print(f"   ERROR in manual processing: {e}")
        
        # 5. extract_department_questions_from_csvの結果確認
        from app import extract_department_questions_from_csv
        
        print(f"\n5. extract_department_questions_from_csv test:")
        road_questions = extract_department_questions_from_csv('道路', 10)
        
        if road_questions:
            print(f"   Road department extraction: {len(road_questions)} questions")
            road_ids = [int(q.get('id', 0)) for q in road_questions if q.get('id')]
            print(f"   Road question IDs: {road_ids[:10]}")
            
            # 6. 重要: なぜall_questionsは0なのに、extractは成功するのか？
            print(f"\n6. CRITICAL: Why all_questions=0 but extract=success?")
            print(f"   load_rccm_data_files result: {len(all_questions)} questions")
            print(f"   extract_department_questions_from_csv result: {len(road_questions)} questions")
            print(f"   -> CONCLUSION: load_rccm_data_files has CRITICAL BUG")
            print(f"   -> extract_department_questions_from_csv works independently")
            print(f"   -> Session initialization fails because all_questions is empty")
        else:
            print(f"   Road department extraction FAILED")
        
        print(f"\n=== DEBUG COMPLETE ===")

if __name__ == "__main__":
    ascii_data_debug()