#!/usr/bin/env python3
"""
実際のアプリテストスクリプト
現在の問題を正確に特定する
"""

import sys
import os
import traceback

# 現在のディレクトリを確認
print(f"現在のディレクトリ: {os.getcwd()}")
print(f"app.py存在: {os.path.exists('app.py')}")

try:
    # アプリのインポートテスト
    print("アプリのインポート中...")
    from app import app
    print("✅ アプリインポート成功")
    
    # 実際のテスト実行
    with app.test_client() as client:
        print("\n=== 実際のアプリテスト開始 ===")
        
        # 1. ホーム画面テスト
        print("1. ホーム画面テスト...")
        try:
            home_response = client.get('/')
            print(f"   ホーム画面: ステータス={home_response.status_code}")
        except Exception as e:
            print(f"   ❌ ホーム画面エラー: {e}")
        
        # 2. 基礎科目テスト
        print("2. 基礎科目テスト...")
        try:
            basic_response = client.get('/exam?question_type=basic')
            print(f"   基礎科目: ステータス={basic_response.status_code}")
            if basic_response.status_code != 200:
                data = basic_response.get_data(as_text=True)
                print(f"   ❌ 基礎科目エラー内容:\n{data[:1000]}")
            else:
                print("   ✅ 基礎科目: 正常応答")
        except Exception as e:
            print(f"   ❌ 基礎科目例外: {e}")
            traceback.print_exc()
        
        # 3. 専門科目テスト
        print("3. 専門科目(道路)テスト...")
        try:
            specialist_response = client.get('/exam?question_type=specialist&department=road')
            print(f"   専門科目: ステータス={specialist_response.status_code}")
            if specialist_response.status_code != 200:
                data = specialist_response.get_data(as_text=True)
                print(f"   ❌ 専門科目エラー内容:\n{data[:1000]}")
            else:
                print("   ✅ 専門科目: 正常応答")
        except Exception as e:
            print(f"   ❌ 専門科目例外: {e}")
            traceback.print_exc()
        
        # 4. データ読み込みテスト
        print("4. データ読み込みテスト...")
        try:
            from utils import load_rccm_data_files
            questions = load_rccm_data_files('data')
            print(f"   ✅ 問題データ: {len(questions)}問読み込み成功")
            
            basic_count = sum(1 for q in questions if q.get('question_type') == 'basic')
            specialist_count = sum(1 for q in questions if q.get('question_type') == 'specialist')
            print(f"   基礎科目: {basic_count}問")
            print(f"   専門科目: {specialist_count}問")
            
        except Exception as e:
            print(f"   ❌ データ読み込みエラー: {e}")
            traceback.print_exc()

        print("\n=== テスト完了 ===")

except ImportError as e:
    print(f"❌ インポートエラー: {e}")
    print("必要なパッケージがインストールされていない可能性があります")
except Exception as e:
    print(f"❌ 予期しないエラー: {e}")
    traceback.print_exc()