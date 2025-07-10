#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
【直接修正】基礎科目問題「一問目からできない」の解決
最小限のテストで問題を特定
"""

import sys
import os
import time

def test_basic_exam_access():
    """基礎科目アクセステスト"""
    print("🔍 【直接修正】基礎科目アクセステスト開始")
    print("=" * 60)
    
    # Flaskアプリのインポート確認
    try:
        print("1️⃣ Flaskアプリインポート...")
        from app import app
        print("   ✅ app.py正常インポート")
        
        # 基礎科目データ確認
        print("2️⃣ 基礎科目データ確認...")
        data_file = "data/4-1.csv"
        if os.path.exists(data_file):
            print(f"   ✅ {data_file} 存在確認")
            
            # ファイル内容の簡単な確認
            with open(data_file, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                print(f"   ✅ データ行数: {len(lines)}行")
                if len(lines) > 1:
                    print(f"   ✅ サンプル行: {lines[1][:100]}...")
        else:
            print(f"   ❌ {data_file} が見つかりません")
            return False
            
        # テストクライアントでの基礎科目試験開始テスト
        print("3️⃣ 基礎科目試験開始テスト...")
        with app.test_client() as client:
            
            # ホームページアクセス
            print("   - ホームページアクセス...")
            response = client.get('/')
            print(f"     ステータス: {response.status_code}")
            
            # 基礎科目試験開始（GET）
            print("   - 基礎科目試験開始（GET）...")
            response = client.get('/start_exam/基礎科目')
            print(f"     ステータス: {response.status_code}")
            
            if response.status_code != 200:
                print(f"     ❌ GET失敗: {response.data.decode('utf-8', errors='ignore')[:200]}")
                
                # 基礎科目専用ルートでテスト
                print("   - 基礎科目専用ルート（/start_exam/basic）テスト...")
                response = client.get('/start_exam/basic')
                print(f"     ステータス: {response.status_code}")
                
                if response.status_code != 200:
                    print(f"     ❌ 基礎科目専用ルート失敗: {response.data.decode('utf-8', errors='ignore')[:200]}")
                    return False
            
            # 基礎科目試験開始（POST）
            print("   - 基礎科目試験開始（POST）...")
            response = client.post('/start_exam/基礎科目', data={'questions': '10'})
            print(f"     ステータス: {response.status_code}")
            
            if response.status_code == 302:  # リダイレクト
                print("     ✅ 正常リダイレクト（試験開始成功）")
                location = response.headers.get('Location', '')
                print(f"     リダイレクト先: {location}")
                
                # リダイレクト先をフォロー
                if location:
                    print("   - リダイレクト先アクセス...")
                    if location.startswith('/'):
                        response = client.get(location)
                        print(f"     ステータス: {response.status_code}")
                        
                        if response.status_code == 200:
                            print("     ✅ 最初の問題表示成功")
                            
                            # 問題内容の確認
                            content = response.data.decode('utf-8', errors='ignore')
                            if '問題' in content or 'option_' in content:
                                print("     ✅ 問題コンテンツ確認")
                                return True
                            else:
                                print("     ❌ 問題コンテンツなし")
                                print(f"     レスポンス内容: {content[:300]}...")
                                return False
                        else:
                            print(f"     ❌ リダイレクト先エラー: {response.data.decode('utf-8', errors='ignore')[:200]}")
                            return False
            
            elif response.status_code == 200:
                print("     ✅ 直接表示成功")
                return True
            else:
                print(f"     ❌ POST失敗: {response.data.decode('utf-8', errors='ignore')[:200]}")
                return False
                
    except ImportError as e:
        print(f"❌ インポートエラー: {e}")
        print("💡 解決策: pip install flask")
        return False
        
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """メイン実行"""
    print("🎯 【直接修正】基礎科目「一問目からできない」問題の解決")
    print("📋 目標: 最小限の確認で具体的問題を特定")
    
    success = test_basic_exam_access()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ テスト成功: 基礎科目の最初の問題が正常表示")
        print("📋 結果: 「一問目からできない」問題は解決済み")
        print("💡 確認: ブラウザで http://localhost:5000 からテスト")
    else:
        print("❌ テスト失敗: 具体的な問題を発見")
        print("📋 次のステップ: 上記エラー内容に基づいて修正")
        print("💡 対策: エラーメッセージを確認して該当箇所を修正")

if __name__ == "__main__":
    main()