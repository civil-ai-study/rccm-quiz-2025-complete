#!/usr/bin/env python3
"""
アプリケーション機能テストスクリプト
問題の根本原因を特定するためのテスト
"""

import os
import sys

# 現在のディレクトリをパスに追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import app
    import logging
    
    # ログレベルを設定
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    print("=== RCCM Quiz App 機能テスト ===")
    
    with app.test_client() as client:
        print("\n1. ホーム画面テスト...")
        try:
            response = client.get('/')
            print(f"   ✓ ホーム画面: ステータス={response.status_code}")
            if response.status_code == 200:
                print("   ✓ ホーム画面正常")
            else:
                print(f"   ❌ ホーム画面エラー: {response.status_code}")
        except Exception as e:
            print(f"   ❌ ホーム画面例外: {e}")
        
        print("\n2. 基礎科目開始テスト...")
        try:
            response = client.get('/exam?question_type=basic')
            print(f"   ✓ 基礎科目: ステータス={response.status_code}")
            if response.status_code == 200:
                print("   ✓ 基礎科目開始正常")
            else:
                print(f"   ❌ 基礎科目開始失敗: {response.status_code}")
                print(f"   エラー内容: {response.get_data(as_text=True)[:300]}...")
        except Exception as e:
            print(f"   ❌ 基礎科目例外: {e}")
        
        print("\n3. 専門科目(道路)開始テスト...")
        try:
            response = client.get('/exam?question_type=specialist&department=road')
            print(f"   ✓ 専門科目(道路): ステータス={response.status_code}")
            if response.status_code == 200:
                print("   ✓ 専門科目(道路)開始正常")
            else:
                print(f"   ❌ 専門科目(道路)開始失敗: {response.status_code}")
                print(f"   エラー内容: {response.get_data(as_text=True)[:300]}...")
        except Exception as e:
            print(f"   ❌ 専門科目(道路)例外: {e}")
        
        print("\n4. ランダム問題開始テスト...")
        try:
            response = client.get('/exam')
            print(f"   ✓ ランダム問題: ステータス={response.status_code}")
            if response.status_code == 200:
                print("   ✓ ランダム問題開始正常")
            else:
                print(f"   ❌ ランダム問題開始失敗: {response.status_code}")
                print(f"   エラー内容: {response.get_data(as_text=True)[:300]}...")
        except Exception as e:
            print(f"   ❌ ランダム問題例外: {e}")
        
        print("\n5. データファイル確認...")
        try:
            from utils import load_rccm_data_files
            data_dir = 'data'
            questions = load_rccm_data_files(data_dir)
            print(f"   ✓ 問題データ読み込み: {len(questions)}問")
            
            # 基礎科目と専門科目の数を確認
            basic_count = sum(1 for q in questions if q.get('question_type') == 'basic')
            specialist_count = sum(1 for q in questions if q.get('question_type') == 'specialist')
            print(f"   ✓ 基礎科目: {basic_count}問")
            print(f"   ✓ 専門科目: {specialist_count}問")
            
        except Exception as e:
            print(f"   ❌ データファイル読み込みエラー: {e}")

    print("\n=== テスト完了 ===")
    
except ImportError as e:
    print(f"❌ アプリケーションのインポートに失敗: {e}")
except Exception as e:
    print(f"❌ 予期しないエラー: {e}")
    import traceback
    traceback.print_exc()