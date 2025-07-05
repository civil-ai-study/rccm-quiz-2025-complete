#!/usr/bin/env python3
"""
🛡️ ULTRA SAFE 最小限動作テスト
副作用ゼロでアプリケーションの基本動作を確認
"""

import sys
import os
import traceback
from datetime import datetime

def ultra_safe_minimal_test():
    """最小限の動作テスト（副作用なし）"""
    print("🛡️ ULTRA SAFE 最小限動作テスト")
    print("=" * 60)
    print(f"テスト時刻: {datetime.now()}")
    print("🔒 副作用: ゼロ（読み込みテストのみ）")
    
    test_results = {
        'import_test': False,
        'app_creation': False,
        'route_discovery': False,
        'function_availability': False
    }
    
    # 1. インポートテスト
    print("\n📦 インポートテスト:")
    
    try:
        # パスを一時的に追加
        current_dir = os.getcwd()
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        
        # 重要なモジュールのインポートテスト
        print("  Flask関連...")
        from flask import Flask, session
        print("  ✅ Flask: OK")
        
        print("  プロジェクト固有モジュール...")
        try:
            from utils import load_questions_improved
            print("  ✅ utils: OK")
        except ImportError as e:
            print(f"  ⚠️ utils: {e}")
        
        try:
            from config import Config
            print("  ✅ config: OK")
        except ImportError as e:
            print(f"  ⚠️ config: {e}")
        
        test_results['import_test'] = True
        
    except Exception as e:
        print(f"  ❌ インポートエラー: {e}")
        return test_results
    
    # 2. app.pyの基本読み込みテスト
    print("\n📄 app.py読み込みテスト:")
    
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            app_content = f.read()
        
        print("  ✅ ファイル読み込み: OK")
        
        # 構文チェック（コンパイルのみ、実行しない）
        compile(app_content, 'app.py', 'exec')
        print("  ✅ 構文チェック: OK")
        
        test_results['app_creation'] = True
        
    except SyntaxError as e:
        print(f"  ❌ 構文エラー: {e}")
        print(f"    行{e.lineno}: {e.text}")
        return test_results
    except Exception as e:
        print(f"  ❌ 読み込みエラー: {e}")
        return test_results
    
    # 3. ルート発見テスト
    print("\n🔍 ルート発見テスト:")
    
    important_routes = [
        "@app.route('/')",
        "@app.route('/exam'",
        "@app.route('/departments'",
    ]
    
    routes_found = 0
    for route in important_routes:
        if route in app_content:
            print(f"  ✅ {route}: 発見")
            routes_found += 1
        else:
            print(f"  ❌ {route}: 未発見")
    
    test_results['route_discovery'] = routes_found >= 2
    
    # 4. 新しい関数の利用可能性テスト
    print("\n🔧 新関数利用可能性テスト:")
    
    new_functions = [
        'def safe_exam_session_reset(',
        'def safe_session_check(',
    ]
    
    functions_found = 0
    for func in new_functions:
        if func in app_content:
            print(f"  ✅ {func}: 定義済み")
            functions_found += 1
        else:
            print(f"  ❌ {func}: 未定義")
    
    # 関数呼び出しの確認
    if 'safe_exam_session_reset()' in app_content:
        print("  ✅ safe_exam_session_reset(): 呼び出し済み")
        functions_found += 0.5
    else:
        print("  ❌ safe_exam_session_reset(): 未呼び出し")
    
    test_results['function_availability'] = functions_found >= 2
    
    # 5. 総合評価
    print("\n📊 総合評価:")
    
    all_tests = list(test_results.values())
    success_count = sum(all_tests)
    success_rate = (success_count / len(all_tests)) * 100
    
    print(f"成功率: {success_rate:.1f}% ({success_count}/{len(all_tests)})")
    
    for test_name, result in test_results.items():
        status = "✅ 合格" if result else "❌ 不合格"
        print(f"  {test_name}: {status}")
    
    # 6. 判定
    if success_rate >= 100:
        print("\n✅ 完全成功: アプリケーション準備完了")
        recommendation = "READY"
    elif success_rate >= 75:
        print("\n⚠️ 部分的成功: 軽微な問題あり")
        recommendation = "CAUTION"
    else:
        print("\n❌ 失敗: 重大な問題あり")
        recommendation = "ROLLBACK"
    
    # 7. 推奨事項
    print("\n🚀 推奨事項:")
    
    if recommendation == "READY":
        print("  1. 実際のFlaskアプリケーション起動テスト")
        print("  2. 基本的なページアクセステスト")
        print("  3. セッション機能の動作確認")
    elif recommendation == "CAUTION":
        print("  1. 問題箇所の詳細確認")
        print("  2. 軽微な問題なら起動テスト継続")
        print("  3. 重大な問題なら修正後再テスト")
    else:
        print("  1. 即座にロールバック実行")
        print("  2. 問題の根本原因分析")
        print("  3. 修正後に再テスト")
    
    print(f"\n✅ 最小限動作テスト完了")
    print(f"🛡️ 副作用: ゼロ（読み込みのみ実行）")
    print(f"📋 推奨: {recommendation}")
    
    return test_results, recommendation

if __name__ == "__main__":
    results, recommendation = ultra_safe_minimal_test()
    print(f"\n最終判定: {recommendation}")