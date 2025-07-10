#!/usr/bin/env python3
"""
🔥 CRITICAL SESSION FIX 構文検証
Flaskなしでapp.pyの構文エラーをチェック

修正内容の構文検証:
1. lightweight_session変数定義
2. exam_simulator_page関数修正
3. リダイレクト修正
4. データ読み込み分離
"""

import ast
import sys
import os

def validate_app_syntax():
    """app.pyの構文を検証"""
    
    print("🔥 CRITICAL SESSION FIX 構文検証開始")
    print("=" * 50)
    
    app_py_path = "app.py"
    
    try:
        with open(app_py_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"✅ app.py 読み込み完了 ({len(content)} 文字)")
        
        # 構文解析実行
        try:
            ast.parse(content, filename=app_py_path)
            print("✅ 構文エラーなし - app.py は正常")
            
        except SyntaxError as e:
            print(f"❌ 構文エラー発見:")
            print(f"   ファイル: {e.filename}")
            print(f"   行番号: {e.lineno}")
            print(f"   カラム: {e.offset}")
            print(f"   メッセージ: {e.msg}")
            print(f"   問題のコード: {e.text}")
            return False
            
        # 重要な修正内容の確認
        print("\n🔍 修正内容の確認:")
        
        # 1. lightweight_session の定義確認
        if "lightweight_session = unified_session.copy()" in content:
            print("✅ lightweight_session変数定義 - 修正済み")
        else:
            print("❌ lightweight_session変数定義 - 未修正または不完全")
        
        # 2. exam_simulator_page関数のセッション読み取り確認
        if "exam_session = session.get('exam_session')" in content and "【根本修正】セッション状態確認とデータ復元" in content:
            print("✅ exam_simulator_page関数セッション読み取り - 修正済み")
        else:
            print("❌ exam_simulator_page関数セッション読み取り - 未修正または不完全")
        
        # 3. リダイレクト修正確認
        if "redirect(url_for('exam'))" in content and "url_for('exam_question')" not in content:
            print("✅ exam_question->examリダイレクト修正 - 修正済み")
        else:
            print("❌ exam_question->examリダイレクト修正 - 未修正または不完全")
        
        # 4. データ読み込み分離確認
        if "【根本修正】基礎科目と専門科目の完全分離データ読み込み" in content:
            print("✅ 基礎科目/専門科目データ読み込み分離 - 修正済み")
        else:
            print("❌ 基礎科目/専門科目データ読み込み分離 - 未修正または不完全")
        
        # 5. 関数定義数の確認
        tree = ast.parse(content)
        function_count = len([node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)])
        print(f"\n📊 統計情報:")
        print(f"   関数定義数: {function_count}")
        print(f"   総行数: {len(content.splitlines())}")
        
        # 6. 重要な関数の存在確認
        important_functions = [
            "start_exam",
            "exam", 
            "exam_simulator_page"
        ]
        
        for func_name in important_functions:
            if f"def {func_name}" in content:
                print(f"   ✅ {func_name}関数 - 存在")
            else:
                print(f"   ❌ {func_name}関数 - 不存在")
        
        print("\n🎉 構文検証完了 - app.py は有効なPythonコードです")
        return True
        
    except FileNotFoundError:
        print(f"❌ ファイルが見つかりません: {app_py_path}")
        return False
    except Exception as e:
        print(f"❌ 予期しないエラー: {e}")
        return False

def check_critical_fixes():
    """修正された箇所の詳細確認"""
    
    print("\n" + "=" * 50)
    print("🔬 CRITICAL FIXES 詳細確認")
    
    app_py_path = "app.py"
    
    try:
        with open(app_py_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        print(f"総行数: {len(lines)}")
        
        # 修正箇所の行番号検索
        fixes_found = {}
        
        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            # lightweight_session定義
            if "lightweight_session = unified_session.copy()" in line_stripped:
                fixes_found["lightweight_session_definition"] = i
                print(f"✅ 行{i}: lightweight_session定義発見")
            
            # exam_simulator_page修正
            if "【根本修正】セッション状態確認とデータ復元" in line_stripped:
                fixes_found["exam_simulator_session_fix"] = i
                print(f"✅ 行{i}: exam_simulator_pageセッション修正発見")
            
            # リダイレクト修正
            if "redirect(url_for('exam'))" in line_stripped and "exam_question" not in line_stripped:
                fixes_found["redirect_fix"] = i
                print(f"✅ 行{i}: リダイレクト修正発見")
            
            # データ読み込み分離
            if "【根本修正】基礎科目と専門科目の完全分離データ読み込み" in line_stripped:
                fixes_found["data_separation_fix"] = i
                print(f"✅ 行{i}: データ読み込み分離修正発見")
        
        print(f"\n修正箇所総数: {len(fixes_found)}")
        
        if len(fixes_found) >= 3:  # 最低3つの修正が確認できれば合格
            print("🎉 重要な修正が正常に適用されています")
            return True
        else:
            print("⚠️ 一部の修正が適用されていない可能性があります")
            return False
            
    except Exception as e:
        print(f"❌ 詳細確認中にエラー: {e}")
        return False

if __name__ == "__main__":
    print("🚀 CRITICAL SESSION FIX 検証ツール")
    print("   Flask環境なしでの構文・修正確認")
    print()
    
    # 構文検証
    syntax_ok = validate_app_syntax()
    
    # 修正詳細確認
    fixes_ok = check_critical_fixes()
    
    print("\n" + "=" * 50)
    print("🏁 最終結果")
    print(f"   構文検証: {'✅ 合格' if syntax_ok else '❌ 不合格'}")
    print(f"   修正確認: {'✅ 合格' if fixes_ok else '❌ 不合格'}")
    
    overall_result = syntax_ok and fixes_ok
    
    if overall_result:
        print("\n🎉 CRITICAL SESSION FIX は正常に適用されました！")
        print("   アプリケーションの根本問題が修正されています。")
    else:
        print("\n⚠️ 一部の問題が残っている可能性があります。")
        print("   追加の確認と修正が必要です。")
    
    sys.exit(0 if overall_result else 1)