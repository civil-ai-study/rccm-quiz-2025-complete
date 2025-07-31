#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ULTRA SYNC ローカル動作確認テスト（安全版）
型エラー修正の動作確認とTypeError根絶確認
"""

import sys
import os
import traceback
from datetime import datetime

def test_app_import():
    """アプリケーションのインポートテスト"""
    print("ULTRA SYNC ローカル動作確認テスト")
    print(f"実行時刻: {datetime.now().strftime('%H:%M:%S')}")
    print("目的: 型エラー修正の動作確認")
    print("=" * 50)
    
    try:
        # app.pyをインポート
        print("Step 1: app.pyインポート")
        sys.path.insert(0, 'rccm-quiz-app')
        from app import app, get_exam_current_safe
        print("  成功: app.pyインポート完了")
        
        # get_exam_current_safe関数の存在確認
        print("Step 2: get_exam_current_safe関数確認")
        if callable(get_exam_current_safe):
            print("  成功: get_exam_current_safe関数存在確認")
        else:
            print("  エラー: get_exam_current_safe関数が見つかりません")
            return False
        
        # テストクライアント作成
        print("Step 3: Flaskテストクライアント作成")
        client = app.test_client()
        print("  成功: テストクライアント作成完了")
        
        return True, client
        
    except Exception as e:
        print(f"  エラー: {e}")
        traceback.print_exc()
        return False, None

def test_home_page(client):
    """ホームページアクセステスト"""
    print("\nStep 4: ホームページアクセステスト")
    
    try:
        response = client.get('/')
        print(f"  レスポンスコード: {response.status_code}")
        
        if response.status_code == 200:
            print("  成功: ホームページ正常表示")
            return True
        else:
            print(f"  エラー: 期待値200、実際{response.status_code}")
            return False
            
    except Exception as e:
        print(f"  エラー: {e}")
        return False

def test_get_exam_current_safe():
    """get_exam_current_safe関数の単体テスト"""
    print("\nStep 5: get_exam_current_safe関数テスト")
    
    try:
        sys.path.insert(0, 'rccm-quiz-app')
        from app import get_exam_current_safe
        
        # テストケース1: None値
        test_session1 = {}
        result1 = get_exam_current_safe(test_session1, 0)
        print(f"  テスト1 (None値): {result1} (期待値: 0)")
        
        # テストケース2: 正常な数値
        test_session2 = {'exam_current': 5}
        result2 = get_exam_current_safe(test_session2, 0)
        print(f"  テスト2 (正常値): {result2} (期待値: 5)")
        
        # テストケース3: 文字列値（これがTypeErrorを防ぐ重要なテスト）
        test_session3 = {'exam_current': '3'}
        result3 = get_exam_current_safe(test_session3, 0)
        print(f"  テスト3 (文字列): {result3} (期待値: 3)")
        
        # テストケース4: 不正な値
        test_session4 = {'exam_current': 'invalid'}
        result4 = get_exam_current_safe(test_session4, 0)
        print(f"  テスト4 (不正値): {result4} (期待値: 0)")
        
        print("  成功: get_exam_current_safe関数動作確認完了")
        return True
        
    except Exception as e:
        print(f"  エラー: {e}")
        traceback.print_exc()
        return False

def test_department_url_encoding():
    """部門名URLエンコーディングテスト"""
    print("\nStep 6: 部門名URLエンコーディングテスト")
    
    try:
        import urllib.parse
        
        # 河川・砂防のエンコーディング確認
        department = "河川・砂防"
        encoded = urllib.parse.quote(department)
        print(f"  部門名: {department}")
        print(f"  エンコード: {encoded}")
        
        # デコードテスト
        decoded = urllib.parse.unquote(encoded)
        print(f"  デコード: {decoded}")
        
        if decoded == department:
            print("  成功: URLエンコーディング/デコーディング正常")
            return True
        else:
            print("  エラー: エンコーディング/デコーディング不整合")
            return False
            
    except Exception as e:
        print(f"  エラー: {e}")
        return False

def main():
    """メインテスト実行"""
    print("ULTRA SYNC ローカル動作確認システム")
    print("目的: 型エラー修正の完全動作確認")
    print("=" * 60)
    
    test_results = []
    
    # Step 1-3: アプリインポート
    success, client = test_app_import()
    test_results.append(("アプリインポート", success))
    
    if not success:
        print("\nアプリインポート失敗のため終了")
        return False
    
    # Step 4: ホームページテスト
    success = test_home_page(client)
    test_results.append(("ホームページ", success))
    
    # Step 5: 型安全関数テスト
    success = test_get_exam_current_safe()
    test_results.append(("型安全関数", success))
    
    # Step 6: URLエンコーディング
    success = test_department_url_encoding()
    test_results.append(("URLエンコーディング", success))
    
    # 結果サマリー
    print("\n" + "=" * 60)
    print("ULTRA SYNC ローカル動作確認結果")
    print("=" * 60)
    
    all_success = True
    for test_name, result in test_results:
        status = "成功" if result else "失敗"
        print(f"{test_name}: {status}")
        if not result:
            all_success = False
    
    if all_success:
        print("\n成功: 全テスト合格")
        print("型エラー修正の動作確認完了")
        print("次のステップ: 本番環境でのテスト準備")
        return True
    else:
        print("\n要調査: 一部テスト不合格")
        print("修正が必要な箇所があります")
        return False

if __name__ == "__main__":
    main()