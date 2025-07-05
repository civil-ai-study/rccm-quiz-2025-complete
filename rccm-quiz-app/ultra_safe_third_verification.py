#!/usr/bin/env python3
"""
🛡️ ULTRA SAFE 第3段階検証
リスクレベルHIGH対応の最高レベル検証
"""

import os
import subprocess
import ast
import shutil
from datetime import datetime

def ultra_safe_third_verification():
    """第3段階の最高レベル検証"""
    print("🛡️ ULTRA SAFE 第3段階検証")
    print("=" * 60)
    print(f"検証時刻: {datetime.now()}")
    print("⚠️ リスクレベル: HIGH - 最高レベル検証実行")
    
    verification_results = {
        'file_integrity': False,
        'syntax_validation': False,
        'ast_analysis': False,
        'function_count_correct': False,
        'remaining_count_correct': False,
        'numerical_integrity': False,
        'progress_tracking': False
    }
    
    # 1. ファイル整合性の詳細確認
    print("\n📊 ファイル整合性詳細確認:")
    
    if not os.path.exists('app.py'):
        print("❌ app.pyが存在しません")
        return verification_results
    
    current_size = os.path.getsize('app.py')
    
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
        lines = content.split('\n')
    
    print(f"✅ ファイルアクセス: 正常")
    print(f"  サイズ: {current_size:,} bytes")
    print(f"  行数: {len(lines):,} 行")
    
    verification_results['file_integrity'] = True
    
    # 2. 構文検証（複数回実行で確実性向上）
    print("\n🔍 構文検証（厳格モード）:")
    
    syntax_checks = []
    for i in range(2):  # 2回実行で確実性向上
        result = subprocess.run(['python3', '-m', 'py_compile', 'app.py'], 
                              capture_output=True, text=True)
        syntax_checks.append(result.returncode == 0)
        
        if result.returncode == 0:
            print(f"  ✅ 構文チェック{i+1}: 合格")
        else:
            print(f"  ❌ 構文チェック{i+1}: エラー - {result.stderr}")
            return verification_results
    
    verification_results['syntax_validation'] = all(syntax_checks)
    
    # 3. AST解析による詳細構造確認
    print("\n🔍 AST解析詳細構造確認:")
    
    try:
        tree = ast.parse(content)
        print("✅ AST解析: 成功")
        
        # 関数定義の確認
        function_definitions = {}
        function_calls = {}
        
        for node in ast.walk(tree):
            # 関数定義をカウント
            if isinstance(node, ast.FunctionDef):
                if node.name in ['safe_exam_session_reset', 'safe_session_check']:
                    function_definitions[node.name] = function_definitions.get(node.name, 0) + 1
            
            # 関数呼び出しをカウント
            elif isinstance(node, ast.Call):
                if (isinstance(node.func, ast.Name) and 
                    node.func.id == 'safe_exam_session_reset'):
                    function_calls['safe_exam_session_reset'] = function_calls.get('safe_exam_session_reset', 0) + 1
        
        print("  関数定義:")
        for func_name, count in function_definitions.items():
            print(f"    {func_name}: {count}個")
        
        print("  関数呼び出し:")
        reset_calls = function_calls.get('safe_exam_session_reset', 0)
        print(f"    safe_exam_session_reset(): {reset_calls}箇所")
        
        verification_results['ast_analysis'] = True
        
    except Exception as e:
        print(f"❌ AST解析エラー: {e}")
        return verification_results
    
    # 4. 関数呼び出し数の厳密検証
    print("\n📊 関数呼び出し数厳密検証:")
    
    expected_calls = 3  # 第1+第2+第3段階
    actual_calls = reset_calls
    
    print(f"期待値: {expected_calls}箇所")
    print(f"実際値: {actual_calls}箇所")
    
    if actual_calls == expected_calls:
        print("✅ 関数呼び出し数: 正確")
        verification_results['function_count_correct'] = True
    else:
        print(f"❌ 関数呼び出し数: 不一致")
    
    # 5. 残存session.pop数の厳密検証
    print("\n📊 残存session.pop数厳密検証:")
    
    remaining_pops = content.count("session.pop('exam_question_ids'")
    expected_remaining = 3  # 6箇所から3箇所置換済み
    
    print(f"期待値: {expected_remaining}箇所")
    print(f"実際値: {remaining_pops}箇所")
    
    if remaining_pops == expected_remaining:
        print("✅ 残存session.pop数: 正確")
        verification_results['remaining_count_correct'] = True
    else:
        print(f"❌ 残存session.pop数: 不一致")
    
    # 6. 数値整合性の完全確認
    print("\n📊 数値整合性完全確認:")
    
    total_original = 6
    current_replaced = actual_calls
    current_remaining = remaining_pops
    total_current = current_replaced + current_remaining
    
    print(f"元の総数: {total_original}")
    print(f"置換済み: {current_replaced}")
    print(f"残存: {current_remaining}")
    print(f"現在の総数: {total_current}")
    
    if total_current == total_original:
        print("✅ 数値整合性: 完全")
        verification_results['numerical_integrity'] = True
    else:
        print(f"❌ 数値整合性: 破損 ({total_current} ≠ {total_original})")
    
    # 7. 進捗追跡
    print("\n📊 進捗追跡:")
    
    if verification_results['numerical_integrity']:
        progress_percentage = (current_replaced / total_original) * 100
        print(f"置換進捗: {progress_percentage:.1f}% ({current_replaced}/{total_original})")
        print(f"残り作業: {current_remaining}箇所")
        
        verification_results['progress_tracking'] = True
    else:
        print("❌ 進捗計算不可（数値整合性問題）")
    
    # 8. 変更箇所の詳細確認
    print("\n📍 変更箇所詳細確認:")
    
    call_locations = []
    for i, line in enumerate(lines):
        if 'safe_exam_session_reset()' in line and 'def safe_exam_session_reset' not in line:
            call_locations.append((i + 1, line.strip()))
    
    print(f"関数呼び出し箇所:")
    for line_no, line_content in call_locations:
        print(f"  行{line_no}: {line_content}")
    
    # 9. バックアップ整合性確認
    print("\n📁 バックアップ整合性確認:")
    
    backup_files = [
        'app.py.backup_before_third_replace_20250705_112106',
        'app.py.backup_third_stage_safety_20250705_112106'
    ]
    
    backup_status = {}
    for backup in backup_files:
        if os.path.exists(backup):
            backup_size = os.path.getsize(backup)
            backup_status[backup] = backup_size
            print(f"✅ {backup}: {backup_size:,} bytes")
        else:
            print(f"❌ {backup}: 見つかりません")
    
    # 10. 総合判定
    print("\n📋 総合判定:")
    
    all_checks = list(verification_results.values())
    success_count = sum(all_checks)
    total_checks = len(all_checks)
    success_rate = (success_count / total_checks) * 100
    
    print(f"成功率: {success_rate:.1f}% ({success_count}/{total_checks})")
    
    check_names = [
        'ファイル整合性',
        '構文検証',
        'AST解析',
        '関数呼び出し数',
        '残存session.pop数',
        '数値整合性',
        '進捗追跡'
    ]
    
    for i, (check_name, result) in enumerate(zip(check_names, all_checks)):
        status = "✅ 合格" if result else "❌ 不合格"
        print(f"  {check_name}: {status}")
    
    # 11. ステータス判定
    if success_rate >= 100:
        status = "SUCCESS"
        print("\n✅ 第3段階: 完全成功")
    elif success_rate >= 85:
        status = "PARTIAL"
        print("\n⚠️ 第3段階: 部分的成功")
    else:
        status = "FAILED"
        print("\n❌ 第3段階: 失敗")
    
    # 12. チェックポイント作成
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    checkpoint_name = f"app.py.checkpoint_after_third_replace_{timestamp}"
    
    try:
        shutil.copy2('app.py', checkpoint_name)
        checkpoint_size = os.path.getsize(checkpoint_name)
        print(f"\n📁 チェックポイント作成: {checkpoint_name}")
        print(f"  サイズ: {checkpoint_size:,} bytes")
    except Exception as e:
        print(f"\n❌ チェックポイント作成エラー: {e}")
    
    # 13. 次のステップ推奨
    print("\n🚀 次のステップ推奨:")
    
    if status == "SUCCESS":
        if current_remaining > 0:
            print(f"  1. 第4段階置換の準備（残り{current_remaining}箇所）")
            print("  2. リスクレベル再評価")
            print("  3. 継続的な段階的置換")
        else:
            print("  1. 全置換完了確認")
            print("  2. 最終動作テスト")
            print("  3. 完了宣言")
    elif status == "PARTIAL":
        print("  1. 問題箇所の詳細分析")
        print("  2. 軽微であれば継続")
        print("  3. 重大であればロールバック")
    else:
        print("  1. 即座にロールバック")
        print("  2. 根本原因分析")
        print("  3. 修正後再実行")
    
    print(f"\n✅ 第3段階検証完了 - ステータス: {status}")
    print(f"📊 最終進捗: {progress_percentage:.1f}% (3/6箇所完了)" if 'progress_percentage' in locals() else "")
    
    return verification_results, status

if __name__ == "__main__":
    results, status = ultra_safe_third_verification()
    print(f"\n最終判定: {status}")