#!/usr/bin/env python3
"""
道路部門での問題データ読み込みエラーの詳細調査
"""

import os
import sys
import logging

# プロジェクトルートディレクトリをPythonパスに追加
sys.path.insert(0, '/mnt/c/Users/ABC/Desktop/rccm-quiz-app/rccm-quiz-app')

# ログ設定
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_road_department_processing():
    """道路部門の処理フローをテスト"""
    print("\n=== 道路部門問題データ読み込み調査 ===")
    
    # 1. 部門名正規化テスト
    print("\n1. 部門名正規化テスト")
    try:
        from app import normalize_department_name, get_department_category
        
        test_names = ['道路', 'road', 'Road', 'ROAD', '道路部門']
        for name in test_names:
            normalized = normalize_department_name(name)
            category = get_department_category(name)
            print(f"  {name} -> normalized: {normalized}, category: {category}")
    except Exception as e:
        print(f"  エラー: {e}")
        import traceback
        traceback.print_exc()
    
    # 2. 部門マッピング確認
    print("\n2. 部門マッピング確認")
    try:
        from app import DEPARTMENT_TO_CATEGORY_MAPPING, LEGACY_DEPARTMENT_ALIASES
        
        print(f"  DEPARTMENT_TO_CATEGORY_MAPPING の 'road' エントリ: {DEPARTMENT_TO_CATEGORY_MAPPING.get('road')}")
        print(f"  LEGACY_DEPARTMENT_ALIASES の道路関連エントリ:")
        for key, value in LEGACY_DEPARTMENT_ALIASES.items():
            if 'road' in key.lower() or value == 'road':
                print(f"    {key} -> {value}")
    except Exception as e:
        print(f"  エラー: {e}")
    
    # 3. データファイル存在確認
    print("\n3. データファイル存在確認")
    data_dir = '/mnt/c/Users/ABC/Desktop/rccm-quiz-app/rccm-quiz-app/data'
    year = 2016
    specialist_file = os.path.join(data_dir, f'4-2_{year}.csv')
    
    print(f"  データファイル: {specialist_file}")
    print(f"  ファイル存在: {os.path.exists(specialist_file)}")
    
    if os.path.exists(specialist_file):
        print(f"  ファイルサイズ: {os.path.getsize(specialist_file)} bytes")
    
    # 4. load_specialist_questions_only テスト
    print("\n4. load_specialist_questions_only テスト")
    try:
        from utils import load_specialist_questions_only
        
        # 道路部門のデータを読み込み
        department = '道路'  # データファイル内の実際のカテゴリ名
        questions = load_specialist_questions_only(department, year, data_dir)
        
        print(f"  読み込み結果: {len(questions)} 問")
        
        if questions:
            sample_q = questions[0]
            print(f"  サンプル問題:")
            print(f"    ID: {sample_q.get('id')}")
            print(f"    カテゴリ: {sample_q.get('category')}")
            print(f"    年度: {sample_q.get('year')}")
            print(f"    問題タイプ: {sample_q.get('question_type')}")
            print(f"    部門: {sample_q.get('department')}")
            print(f"    ソースファイル: {sample_q.get('source_file')}")
        else:
            print("  問題データが取得できませんでした")
    except Exception as e:
        print(f"  エラー: {e}")
        import traceback
        traceback.print_exc()
    
    # 5. URL パラメータから実際の処理までの流れ確認
    print("\n5. URL パラメータから実際の処理までの流れ確認")
    try:
        # URLパラメータとして来る可能性のある値
        url_params = ['道路', 'road', 'Road', 'ROAD']
        
        for param in url_params:
            print(f"  URL パラメータ: {param}")
            
            # 正規化
            normalized = normalize_department_name(param)
            print(f"    正規化後: {normalized}")
            
            # カテゴリ取得
            category = get_department_category(param)
            print(f"    カテゴリ: {category}")
            
            # 専門科目データ読み込み
            if category:
                questions = load_specialist_questions_only(category, year, data_dir)
                print(f"    問題数: {len(questions)}")
            else:
                print(f"    カテゴリが見つからないため、問題読み込みスキップ")
    except Exception as e:
        print(f"  エラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_road_department_processing()