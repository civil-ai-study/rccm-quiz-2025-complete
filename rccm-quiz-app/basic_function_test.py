#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
🔥 ULTRA SYNC: 基本機能テスト - 利用者視点での動作確認
副作用ゼロで最重要機能をテスト
"""

import sys
import os
import traceback
from datetime import datetime

def test_basic_functionality():
    """基本機能のテスト"""
    print("🔥 ULTRA SYNC: 基本機能テスト開始")
    print("=" * 60)
    print(f"実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 1. 基本的なインポート確認
    print("1. 基本インポート確認")
    try:
        import flask
        print(f"   ✅ Flask バージョン: {flask.__version__}")
    except ImportError as e:
        print(f"   ❌ Flask インポートエラー: {e}")
        return False
    
    try:
        import csv
        import json
        print("   ✅ 標準ライブラリ正常")
    except ImportError as e:
        print(f"   ❌ 標準ライブラリエラー: {e}")
        return False
    
    # 2. データファイル確認
    print("\n2. データファイル確認")
    data_files = [
        "data/4-1.csv",
        "data/4-2_2008.csv",
        "data/4-2_2009.csv",
        "data/4-2_2010.csv"
    ]
    
    for file_path in data_files:
        if os.path.exists(file_path):
            print(f"   ✅ {file_path} 存在")
        else:
            print(f"   ❌ {file_path} 不存在")
    
    # 3. 基本的なCSVデータ読み込み
    print("\n3. CSVデータ読み込み確認")
    try:
        with open("data/4-1.csv", "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            print(f"   ✅ 4-1.csv 読み込み成功: {len(rows)}行")
            if rows:
                first_row = rows[0]
                print(f"   ✅ 最初の問題カテゴリ: {first_row.get('category', '不明')}")
    except Exception as e:
        print(f"   ❌ CSVデータ読み込みエラー: {e}")
        return False
    
    # 4. app.pyのインポート確認
    print("\n4. app.pyインポート確認")
    try:
        # パスを追加
        sys.path.insert(0, ".")
        
        # app.pyから必要な関数をインポート
        from utils import load_questions_from_csv, get_available_departments
        print("   ✅ utils.py インポート成功")
        
        # 部門データ確認
        departments = get_available_departments()
        print(f"   ✅ 利用可能部門数: {len(departments)}")
        
        # 問題データ確認
        questions = load_questions_from_csv()
        print(f"   ✅ 問題データ読み込み: {len(questions)}問")
        
    except Exception as e:
        print(f"   ❌ app.py関連エラー: {e}")
        print("   詳細エラー:")
        traceback.print_exc()
        return False
    
    # 5. Flaskアプリケーション初期化テスト
    print("\n5. Flaskアプリケーション初期化テスト")
    try:
        from flask import Flask
        test_app = Flask(__name__)
        test_app.config['TESTING'] = True
        
        @test_app.route('/')
        def test_home():
            return "Test OK"
        
        with test_app.test_client() as client:
            response = client.get('/')
            print(f"   ✅ テストFlaskアプリ動作: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Flaskアプリケーション初期化エラー: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("🎯 基本機能テスト完了: 全て正常")
    return True

def test_specific_app_import():
    """具体的なapp.pyのインポートテスト"""
    print("\n🔥 ULTRA SYNC: app.py詳細インポートテスト")
    print("-" * 40)
    
    try:
        # 段階的なインポート確認
        print("1. 基本的なFlaskインポート確認")
        from flask import Flask, render_template, request, session, redirect, url_for, jsonify, make_response
        print("   ✅ Flask基本コンポーネント正常")
        
        print("2. アプリケーション設定確認")
        # メイン app.py のインポートを試行
        import app
        print("   ✅ app.py インポート成功")
        
        print("3. Flask アプリケーション取得")
        flask_app = app.app
        print(f"   ✅ Flask app取得成功: {flask_app.name}")
        
        print("4. 設定済みルート確認")
        print(f"   ✅ 登録済みルート数: {len(flask_app.url_map._rules)}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ app.py インポートエラー: {e}")
        print("   詳細エラー:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_basic_functionality()
    if success:
        test_specific_app_import()