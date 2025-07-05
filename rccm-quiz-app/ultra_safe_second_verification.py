#!/usr/bin/env python3
"""
🛡️ ULTRA SAFE 第2段階検証
第2段階置換後の状態を完全検証
"""

import os
import subprocess
import ast
from datetime import datetime

def ultra_safe_second_verification():
    """第2段階置換後の完全検証"""
    print("🛡️ ULTRA SAFE 第2段階検証")
    print("=" * 60)
    print(f"検証時刻: {datetime.now()}")
    
    verification_results = {
        'file_integrity': False,
        'syntax_check': False,
        'function_calls_count': 0,
        'remaining_pops_count': 0,
        'expected_progress': False,
        'ast_validation': False
    }
    
    # 1. ファイル整合性チェック
    print("\n📊 ファイル整合性チェック:")
    
    if not os.path.exists('app.py'):
        print("❌ app.pyが存在しません")
        return verification_results
    
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
        lines = content.split('\n')
    
    file_size = os.path.getsize('app.py')
    print(f"✅ ファイルサイズ: {file_size:,} bytes")
    print(f"✅ 行数: {len(lines):,} 行")
    verification_results['file_integrity'] = True
    
    # 2. 構文チェック
    print("\n🔍 構文チェック:")
    result = subprocess.run(['python3', '-m', 'py_compile', 'app.py'], 
                          capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ 構文エラーなし")
        verification_results['syntax_check'] = True
    else:
        print(f"❌ 構文エラー: {result.stderr}")
        return verification_results
    
    # 3. AST解析による正確な関数呼び出し数確認
    print("\n🔍 AST解析による正確な検証:")
    
    try:
        tree = ast.parse(content)
        
        # 関数呼び出しを正確にカウント
        function_calls = 0
        for node in ast.walk(tree):
            if (isinstance(node, ast.Call) and 
                isinstance(node.func, ast.Name) and 
                node.func.id == 'safe_exam_session_reset'):
                function_calls += 1
        
        verification_results['function_calls_count'] = function_calls
        print(f"safe_exam_session_reset() 実際の呼び出し: {function_calls}箇所")
        
        verification_results['ast_validation'] = True
        print("✅ AST解析成功")
        
    except Exception as e:
        print(f"❌ AST解析エラー: {e}")
        return verification_results
    
    # 4. 残存session.pop確認
    print("\n📍 残存session.pop確認:")
    
    remaining_pops = content.count("session.pop('exam_question_ids'")
    verification_results['remaining_pops_count'] = remaining_pops
    print(f"session.pop('exam_question_ids') 残存: {remaining_pops}箇所")
    
    # 5. 進捗確認
    print("\n📊 進捗確認:")
    
    # 期待値: 2箇所の関数呼び出し、4箇所の残存session.pop
    expected_calls = 2
    expected_remaining = 4
    
    calls_correct = function_calls == expected_calls
    pops_correct = remaining_pops == expected_remaining
    
    print(f"関数呼び出し: {function_calls}/{expected_calls} {'✅' if calls_correct else '❌'}")
    print(f"残存session.pop: {remaining_pops}/{expected_remaining} {'✅' if pops_correct else '❌'}")
    
    verification_results['expected_progress'] = calls_correct and pops_correct
    
    # 進捗計算
    total_original = 6  # 元々6箇所のsession.pop
    replaced = function_calls
    remaining = remaining_pops
    
    if replaced + remaining == total_original:
        progress = (replaced / total_original) * 100
        print(f"置換進捗: {progress:.1f}% ({replaced}/{total_original})")
        print("✅ 数値整合性: 正常")
    else:
        print(f"⚠️ 数値に不整合があります: 置換{replaced} + 残存{remaining} ≠ 元の{total_original}")
    
    # 6. バックアップ確認
    print("\n📁 バックアップ確認:")
    
    backup_files = [
        'app.py.backup_before_second_replace_20250705_111158',
        'app.py.backup_before_first_replace_20250705_110139'
    ]
    
    for backup in backup_files:
        if os.path.exists(backup):
            backup_size = os.path.getsize(backup)
            print(f"✅ {backup}: {backup_size:,} bytes")
        else:
            print(f"❌ {backup}: 見つかりません")
    
    # 7. 変更箇所の詳細確認
    print("\n📍 変更箇所詳細:")
    
    # 関数呼び出し箇所を特定
    call_lines = []
    for i, line in enumerate(lines):
        if 'safe_exam_session_reset()' in line and 'def safe_exam_session_reset' not in line:
            call_lines.append((i + 1, line.strip()))
    
    print(f"関数呼び出し箇所:")
    for line_no, line_content in call_lines:
        print(f"  行{line_no}: {line_content}")
    
    # 8. 総合判定
    print("\n📋 総合判定:")
    
    all_checks = [
        verification_results['file_integrity'],
        verification_results['syntax_check'],
        verification_results['ast_validation'],
        verification_results['expected_progress']
    ]
    
    success_rate = sum(all_checks) / len(all_checks) * 100
    print(f"成功率: {success_rate:.1f}% ({sum(all_checks)}/{len(all_checks)})")
    
    if success_rate >= 100:
        status = "SUCCESS"
        print("✅ 第2段階置換: 完全成功")
    elif success_rate >= 75:
        status = "PARTIAL"
        print("⚠️ 第2段階置換: 部分的成功")
    else:
        status = "FAILED"
        print("❌ 第2段階置換: 失敗")
    
    # 9. 次のステップ推奨
    print("\n🚀 次のステップ推奨:")
    
    if status == "SUCCESS":
        remaining_targets = remaining_pops
        if remaining_targets > 0:
            print(f"  1. 第3段階置換の準備（残り{remaining_targets}箇所）")
            print("  2. チェックポイント作成")
            print("  3. 段階的に残りを置換")
        else:
            print("  1. 全置換完了確認")
            print("  2. 最終動作テスト")
            print("  3. 完了チェックポイント作成")
    elif status == "PARTIAL":
        print("  1. 問題箇所の詳細確認")
        print("  2. 軽微な問題なら継続")
        print("  3. 重大な問題ならロールバック")
    else:
        print("  1. 即座にロールバック実行")
        print("  2. 問題の根本分析")
    
    # 10. チェックポイント作成
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    checkpoint_name = f"app.py.checkpoint_after_second_replace_{timestamp}"
    
    try:
        import shutil
        shutil.copy2('app.py', checkpoint_name)
        print(f"\n📁 チェックポイント作成: {checkpoint_name}")
    except Exception as e:
        print(f"\n❌ チェックポイント作成エラー: {e}")
    
    print(f"\n✅ 第2段階検証完了 - ステータス: {status}")
    
    return verification_results, status

if __name__ == "__main__":
    results, status = ultra_safe_second_verification()
    print(f"\n最終判定: {status}")