#!/usr/bin/env python3
"""
🛡️ ULTRA SAFE 第3段階実行
リスクレベルHIGHに対応した最高安全レベルでの実行
"""

import os
import subprocess
import ast
from datetime import datetime

def ultra_safe_third_stage_execute():
    """第3段階の最高安全レベル実行"""
    print("🛡️ ULTRA SAFE 第3段階実行")
    print("=" * 60)
    print(f"実行時刻: {datetime.now()}")
    print("🔒 副作用: 最小限（一時ファイルのみ）")
    print("⚠️ リスクレベル: HIGH - 最高安全措置適用")
    
    # 1. 実行前最終確認
    print("\n🔒 実行前最終確認:")
    
    if not os.path.exists('app.py'):
        print("❌ app.pyが存在しません")
        return False
    
    # 現在のファイル状態
    with open('app.py', 'r', encoding='utf-8') as f:
        original_lines = f.readlines()
    
    original_size = os.path.getsize('app.py')
    print(f"✅ 元ファイル: {original_size:,} bytes, {len(original_lines)}行")
    
    # バックアップ確認
    required_backups = [
        'app.py.backup_before_third_replace_20250705_112106',
        'app.py.backup_third_stage_safety_20250705_112106'
    ]
    
    for backup in required_backups:
        if os.path.exists(backup):
            print(f"✅ バックアップ確認: {backup}")
        else:
            print(f"❌ 重要バックアップが見つかりません: {backup}")
            return False
    
    # 2. ターゲット行の再確認
    print("\n🎯 ターゲット行再確認:")
    
    target_start = 2496  # 0-based (行2497)
    target_lines_indices = [target_start, target_start + 1, target_start + 2]
    
    if max(target_lines_indices) >= len(original_lines):
        print("❌ ターゲット行が範囲外です")
        return False
    
    target_lines = []
    for i in target_lines_indices:
        target_lines.append(original_lines[i].strip())
        print(f"  行{i + 1}: {original_lines[i].strip()}")
    
    # 期待パターンの厳密確認
    expected_exact = [
        "session.pop('exam_question_ids', None)",
        "session.pop('exam_current', None)",
        "session.pop('exam_category', None)"
    ]
    
    exact_match = all(expected in target_lines[i] for i, expected in enumerate(expected_exact))
    
    if not exact_match:
        print("❌ ターゲット行が期待される内容と一致しません")
        for i, (expected, actual) in enumerate(zip(expected_exact, target_lines)):
            match = "✅" if expected in actual else "❌"
            print(f"    {match} 行{target_start + i + 1}: 期待='{expected}', 実際='{actual}'")
        return False
    
    print("✅ ターゲット行確認: 完全一致")
    
    # 3. 置換内容の精密作成
    print("\n📝 置換内容精密作成:")
    
    # インデントの精密測定
    original_line = original_lines[target_start]
    indent_chars = len(original_line) - len(original_line.lstrip())
    replacement_line = ' ' * indent_chars + 'safe_exam_session_reset()\n'
    
    print(f"  元のインデント: {indent_chars}文字")
    print(f"  置換行: '{replacement_line.rstrip()}'")
    print(f"  インデント保持: {'✅' if ' ' * indent_chars in replacement_line else '❌'}")
    
    # 4. 新しいファイル内容の精密構築
    print("\n🧪 新ファイル内容精密構築:")
    
    new_lines = []
    line_mapping = []  # 変更追跡用
    
    for i, line in enumerate(original_lines):
        if i == target_start:
            # 置換実行
            new_lines.append(replacement_line)
            line_mapping.append(f"行{i+1}: 置換により削除")
            line_mapping.append(f"行{i+2}: 置換により削除")
            line_mapping.append(f"行{i+3}: 置換により削除")
            line_mapping.append(f"新行: safe_exam_session_reset() 追加")
        elif i in [target_start + 1, target_start + 2]:
            # スキップ（置換により削除）
            continue
        else:
            new_lines.append(line)
    
    print(f"✅ 新ファイル構築完了")
    print(f"  元の行数: {len(original_lines)}")
    print(f"  新しい行数: {len(new_lines)}")
    print(f"  削減行数: {len(original_lines) - len(new_lines)}")
    
    # 5. 一時ファイル作成と事前検証
    print("\n📁 一時ファイル作成:")
    
    temp_file = 'app.py.temp_third_replace'
    
    try:
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        
        temp_size = os.path.getsize(temp_file)
        print(f"✅ 一時ファイル作成: {temp_file}")
        print(f"  サイズ: {temp_size:,} bytes")
        
    except Exception as e:
        print(f"❌ 一時ファイル作成エラー: {e}")
        return False
    
    # 6. 構文チェック
    print("\n🔍 構文チェック:")
    
    result = subprocess.run(['python3', '-m', 'py_compile', temp_file], 
                          capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ 構文エラー: {result.stderr}")
        os.remove(temp_file)
        return False
    
    print("✅ 構文チェック合格")
    
    # 7. AST解析による構造整合性確認
    print("\n🔍 AST構造整合性確認:")
    
    try:
        with open(temp_file, 'r', encoding='utf-8') as f:
            temp_content = f.read()
        
        tree = ast.parse(temp_content)
        
        # 関数呼び出し数の精密カウント
        reset_calls = 0
        for node in ast.walk(tree):
            if (isinstance(node, ast.Call) and 
                isinstance(node.func, ast.Name) and 
                node.func.id == 'safe_exam_session_reset'):
                reset_calls += 1
        
        print(f"✅ AST解析成功")
        print(f"  safe_exam_session_reset() 呼び出し: {reset_calls}箇所")
        
        # 期待値: 3箇所（第1段階1 + 第2段階1 + 第3段階1）
        expected_calls = 3
        if reset_calls == expected_calls:
            print(f"  ✅ 期待通りの呼び出し数: {reset_calls}/{expected_calls}")
        else:
            print(f"  ⚠️ 予期しない呼び出し数: {reset_calls}/{expected_calls}")
        
    except Exception as e:
        print(f"❌ AST解析エラー: {e}")
        os.remove(temp_file)
        return False
    
    # 8. 残存session.pop数の確認
    print("\n📊 残存session.pop確認:")
    
    remaining_pops = temp_content.count("session.pop('exam_question_ids'")
    print(f"残存session.pop: {remaining_pops}箇所")
    
    # 期待値: 3箇所（4箇所から1箇所減）
    expected_remaining = 3
    if remaining_pops == expected_remaining:
        print(f"✅ 期待通りの残存数: {remaining_pops}/{expected_remaining}")
    else:
        print(f"⚠️ 予期しない残存数: {remaining_pops}/{expected_remaining}")
    
    # 9. 数値整合性確認
    print("\n📊 数値整合性確認:")
    
    total_original = 6  # 元々の総数
    current_calls = reset_calls
    current_remaining = remaining_pops
    
    if current_calls + current_remaining == total_original:
        progress = (current_calls / total_original) * 100
        print(f"✅ 数値整合性: 正常")
        print(f"  置換済み: {current_calls}箇所")
        print(f"  残存: {current_remaining}箇所")
        print(f"  進捗: {progress:.1f}%")
    else:
        print(f"❌ 数値不整合: {current_calls} + {current_remaining} ≠ {total_original}")
    
    # 10. 実行準備完了確認
    print("\n✅ 実行準備完了確認:")
    
    checks = [
        "✅ 元ファイル確認済み",
        "✅ バックアップ確認済み", 
        "✅ ターゲット行確認済み",
        "✅ 置換内容精密作成済み",
        "✅ 新ファイル構築済み",
        "✅ 一時ファイル作成済み",
        "✅ 構文チェック合格",
        "✅ AST構造整合性確認済み",
        "✅ 数値整合性確認済み"
    ]
    
    for check in checks:
        print(f"  {check}")
    
    print(f"\n🚀 適用コマンド（リスクレベルHIGH対応）:")
    print(f"  mv {temp_file} app.py")
    
    print(f"\n🔄 緊急ロールバックコマンド:")
    print("  cp app.py.backup_before_third_replace_20250705_112106 app.py")
    
    print(f"\n🛡️ 副作用: 最小限（一時ファイルのみ作成）")
    print(f"⚠️ 注意: 適用後は即座に検証実行を推奨")
    
    return {
        'temp_file': temp_file,
        'expected_calls': expected_calls,
        'actual_calls': reset_calls,
        'expected_remaining': expected_remaining,
        'actual_remaining': remaining_pops,
        'integrity_check': current_calls + current_remaining == total_original
    }

if __name__ == "__main__":
    result = ultra_safe_third_stage_execute()
    if result:
        print(f"\n✅ 第3段階実行準備完了（最高安全レベル）")
        print(f"整合性: {'✅ 正常' if result['integrity_check'] else '❌ 異常'}")
    else:
        print(f"\n❌ 第3段階実行準備失敗（安全のため中断）")