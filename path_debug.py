#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Ultra Simple Deep Search: パス問題の根本原因特定
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'rccm-quiz-app'))

from app import app
import glob

def path_debug():
    """パス問題の根本原因を特定"""
    print("=== Ultra Simple Deep Search: Path Debug ===")
    
    with app.app_context():
        # 1. 現在の作業ディレクトリ
        print(f"1. Current working directory: {os.getcwd()}")
        
        # 2. debug scriptからの相対パス
        debug_script_dir = os.path.dirname(os.path.abspath(__file__))
        print(f"2. Debug script directory: {debug_script_dir}")
        
        # 3. load_rccm_data_filesが参照しているパス
        data_dir_from_load = os.path.join('rccm-quiz-app', 'data')
        print(f"3. load_rccm_data_files target path: {data_dir_from_load}")
        print(f"   Absolute path: {os.path.abspath(data_dir_from_load)}")
        print(f"   Exists: {os.path.exists(data_dir_from_load)}")
        
        # 4. 正しいパス（デバッグスクリプトから見た）
        correct_data_path = os.path.join(debug_script_dir, 'rccm-quiz-app', 'data')
        print(f"4. Correct path (from debug script): {correct_data_path}")
        print(f"   Exists: {os.path.exists(correct_data_path)}")
        
        # 5. extract_department_questions_from_csvが使用している実際のパス確認
        print(f"\n5. extract_department_questions_from_csv path check:")
        
        # CSVファイル検索パターンを直接確認
        search_patterns = [
            os.path.join('rccm-quiz-app', 'data', '*.csv'),
            os.path.join(debug_script_dir, 'rccm-quiz-app', 'data', '*.csv'),
        ]
        
        for i, pattern in enumerate(search_patterns):
            csv_files = glob.glob(pattern)
            print(f"   Pattern {i+1}: {pattern}")
            print(f"   Found files: {len(csv_files)}")
            if csv_files:
                for csv_file in sorted(csv_files)[:3]:
                    print(f"     {os.path.basename(csv_file)}")
        
        # 6. app.pyの実行コンテキストでのパス確認
        print(f"\n6. App execution context path check:")
        app_script_dir = os.path.dirname(os.path.abspath(os.path.join(debug_script_dir, 'rccm-quiz-app', 'app.py')))
        print(f"   App script directory: {app_script_dir}")
        app_data_path = os.path.join(app_script_dir, 'data')
        print(f"   App relative data path: {app_data_path}")
        print(f"   Exists: {os.path.exists(app_data_path)}")
        
        if os.path.exists(app_data_path):
            csv_files = glob.glob(os.path.join(app_data_path, '*.csv'))
            print(f"   CSV files in correct path: {len(csv_files)}")
        
        print(f"\n=== PATH DEBUG COMPLETE ===")

if __name__ == "__main__":
    path_debug()