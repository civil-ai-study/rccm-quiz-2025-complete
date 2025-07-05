#!/usr/bin/env python3
"""
🛡️ ULTRA SAFE 構文のみテスト
Flask依存なしで構文とロジックのみを検証
"""

import ast
import os
from datetime import datetime

def ultra_safe_syntax_test():
    """構文のみの安全テスト"""
    print("🛡️ ULTRA SAFE 構文のみテスト")
    print("=" * 60)
    print(f"テスト時刻: {datetime.now()}")
    print("🔒 副作用: ゼロ（構文解析のみ）")
    
    test_results = {
        'file_readable': False,
        'syntax_valid': False,
        'functions_defined': False,
        'functions_called': False,
        'structure_intact': False
    }
    
    # 1. ファイル読み取りテスト
    print("\n📄 ファイル読み取りテスト:")
    
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"✅ ファイル読み取り成功: {len(content):,} 文字")
        test_results['file_readable'] = True
        
    except Exception as e:
        print(f"❌ ファイル読み取りエラー: {e}")
        return test_results
    
    # 2. 構文解析テスト
    print("\n🔍 構文解析テスト:")
    
    try:
        tree = ast.parse(content)
        print("✅ 構文解析成功: 有効なPythonコード")
        test_results['syntax_valid'] = True
        
    except SyntaxError as e:
        print(f"❌ 構文エラー: {e}")
        print(f"  行{e.lineno}: {e.text}")
        return test_results
    except Exception as e:
        print(f"❌ 解析エラー: {e}")
        return test_results
    
    # 3. 関数定義の確認
    print("\n🔧 関数定義確認:")
    
    target_functions = [
        'safe_exam_session_reset',
        'safe_session_check'
    ]
    
    defined_functions = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            if node.name in target_functions:
                defined_functions.append(node.name)
                print(f"✅ 関数定義: {node.name}")
    
    test_results['functions_defined'] = len(defined_functions) >= 2
    
    if len(defined_functions) < 2:
        missing = set(target_functions) - set(defined_functions)
        for func in missing:
            print(f"❌ 未定義: {func}")
    
    # 4. 関数呼び出しの確認
    print("\n📞 関数呼び出し確認:")
    
    function_calls = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if (isinstance(node.func, ast.Name) and 
                node.func.id == 'safe_exam_session_reset'):
                function_calls.append(node.func.id)
    
    print(f"safe_exam_session_reset() 呼び出し: {len(function_calls)}箇所")
    test_results['functions_called'] = len(function_calls) >= 1
    
    if len(function_calls) >= 1:
        print("✅ 関数呼び出し: あり")
    else:
        print("❌ 関数呼び出し: なし")
    
    # 5. 基本構造の確認
    print("\n🏗️ 基本構造確認:")
    
    has_flask_app = 'Flask(__name__)' in content
    has_routes = '@app.route' in content
    has_main_guard = 'if __name__' in content
    
    print(f"Flask app作成: {'✅' if has_flask_app else '❌'}")
    print(f"ルート定義: {'✅' if has_routes else '❌'}")
    print(f"メインガード: {'✅' if has_main_guard else '❌'}")
    
    structure_score = sum([has_flask_app, has_routes, has_main_guard])
    test_results['structure_intact'] = structure_score >= 2
    
    # 6. 変更箇所の影響範囲確認
    print("\n🎯 変更箇所影響範囲:")
    
    session_pop_count = content.count("session.pop('exam_question_ids'")
    reset_call_count = content.count("safe_exam_session_reset()")
    
    print(f"残存session.pop: {session_pop_count}箇所")
    print(f"新関数呼び出し: {reset_call_count}箇所")
    
    # 期待値: 5箇所のsession.pop + 1箇所の関数呼び出し
    if session_pop_count == 5 and reset_call_count == 1:
        print("✅ 期待通りの置換状態")
    else:
        print(f"⚠️ 予期しない状態: pop={session_pop_count}, reset={reset_call_count}")
    
    # 7. 総合評価
    print("\n📊 総合評価:")
    
    all_tests = list(test_results.values())
    success_count = sum(all_tests)
    success_rate = (success_count / len(all_tests)) * 100
    
    print(f"成功率: {success_rate:.1f}% ({success_count}/{len(all_tests)})")
    
    test_names = {
        'file_readable': 'ファイル読み取り',
        'syntax_valid': '構文有効性',
        'functions_defined': '関数定義',
        'functions_called': '関数呼び出し',
        'structure_intact': '基本構造'
    }
    
    for test_key, result in test_results.items():
        test_name = test_names.get(test_key, test_key)
        status = "✅ 合格" if result else "❌ 不合格"
        print(f"  {test_name}: {status}")
    
    # 8. 判定と推奨事項
    print("\n📋 判定:")
    
    if success_rate >= 100:
        status = "SUCCESS"
        print("✅ 完全成功: 構文レベルで問題なし")
    elif success_rate >= 80:
        status = "PARTIAL"
        print("⚠️ 部分的成功: 軽微な問題あり")
    else:
        status = "FAILED"
        print("❌ 失敗: 重大な問題あり")
    
    print(f"\n🚀 推奨事項:")
    if status == "SUCCESS":
        print("  1. 第1段階置換: 完全成功")
        print("  2. 第2段階置換の準備開始")
        print("  3. バックアップポイント作成")
    elif status == "PARTIAL":
        print("  1. 問題箇所の詳細確認")
        print("  2. 軽微であれば次段階継続")
    else:
        print("  1. 即座にロールバック")
        print("  2. 問題の根本分析")
    
    print(f"\n✅ 構文テスト完了")
    print(f"🛡️ 副作用: ゼロ（構文解析のみ）")
    print(f"📋 ステータス: {status}")
    
    return test_results, status

if __name__ == "__main__":
    results, status = ultra_safe_syntax_test()
    print(f"\n最終判定: {status}")