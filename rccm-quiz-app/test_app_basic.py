#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
【直接修正】app.py基本動作テスト
基礎科目の最初の問題が表示されるかの確認
"""

import sys
import os

def test_app_basic():
    print("🔍 【直接修正】app.py基本動作テスト開始")
    print("=" * 50)
    
    try:
        # Flask app import
        from app import app
        print("✅ Flask app import成功")
        
        # Routes確認
        routes_count = len(app.url_map._rules)
        print(f"✅ ルート数: {routes_count}")
        
        # Test client作成
        with app.test_client() as client:
            print("\n🧪 基本エンドポイントテスト:")
            
            # Homepage test
            response = client.get('/')
            print(f"   - Homepage (/): {response.status_code}")
            
            # 基礎科目開始テスト
            response = client.get('/start_exam/基礎科目')
            print(f"   - 基礎科目開始: {response.status_code}")
            
            if response.status_code != 200:
                print(f"❌ エラー詳細:")
                error_data = response.data.decode('utf-8', errors='ignore')
                print(f"   {error_data[:300]}...")
                return False
            
            # 実際の問題表示テスト
            response = client.get('/quiz?current=1')
            print(f"   - 問題表示: {response.status_code}")
            
            if response.status_code != 200:
                print(f"❌ 問題表示エラー:")
                error_data = response.data.decode('utf-8', errors='ignore')
                print(f"   {error_data[:300]}...")
                return False
                
        print("\n✅ 基本動作テスト完了")
        return True
        
    except ImportError as e:
        print(f"❌ app.py import失敗: {e}")
        return False
        
    except Exception as e:
        print(f"❌ テスト実行エラー: {e}")
        return False

if __name__ == "__main__":
    success = test_app_basic()
    if success:
        print("\n🎯 結果: 基本動作正常")
        print("📋 次のステップ: より詳細なテストを実行")
    else:
        print("\n🚨 結果: 問題検出")
        print("📋 次のステップ: エラー内容を修正")