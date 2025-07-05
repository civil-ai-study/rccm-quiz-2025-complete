#!/usr/bin/env python3
"""
🛡️ ULTRA SAFE 置換後検証
第1段階置換後の状態を完全検証
"""

import os
import subprocess
from datetime import datetime

def post_replacement_verification():
    """置換後の完全検証"""
    print("🛡️ ULTRA SAFE 置換後検証")
    print("=" * 60)
    print(f"検証時刻: {datetime.now()}")
    
    verification_results = {
        'file_integrity': False,
        'syntax_check': False,
        'function_calls': 0,
        'remaining_pops': 0,
        'backup_exists': False
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
    
    # 3. 関数呼び出し数確認
    print("\n📍 関数呼び出し確認:")
    
    # safe_exam_session_reset()の呼び出し数
    reset_calls = content.count('safe_exam_session_reset()')
    print(f"safe_exam_session_reset() 呼び出し: {reset_calls}箇所")
    verification_results['function_calls'] = reset_calls
    
    if reset_calls == 1:
        print("✅ 期待通り1箇所のみ")
    elif reset_calls == 0:
        print("⚠️ 呼び出しなし - 置換が適用されていない可能性")
    else:
        print(f"⚠️ 予期しない数: {reset_calls}箇所")
    
    # 4. 残存するsession.pop確認
    print("\n📍 残存session.pop確認:")
    
    remaining_pops = content.count("session.pop('exam_question_ids'")
    print(f"session.pop('exam_question_ids') 残存: {remaining_pops}箇所")
    verification_results['remaining_pops'] = remaining_pops
    
    expected_remaining = 5  # 6箇所中1箇所置換済み
    if remaining_pops == expected_remaining:
        print(f"✅ 期待通り{expected_remaining}箇所残存")
    else:
        print(f"⚠️ 予期しない数: {remaining_pops}箇所")
    
    # 5. バックアップ確認
    print("\n📁 バックアップ確認:")
    
    backup_file = 'app.py.backup_before_first_replace_20250705_110139'
    if os.path.exists(backup_file):
        backup_size = os.path.getsize(backup_file)
        print(f"✅ バックアップ存在: {backup_file}")
        print(f"  サイズ: {backup_size:,} bytes")
        verification_results['backup_exists'] = True
    else:
        print("❌ バックアップファイルが見つかりません")
    
    # 6. 追加された関数の存在確認
    print("\n🔍 追加関数確認:")
    
    has_reset_func = 'def safe_exam_session_reset(' in content
    has_check_func = 'def safe_session_check(' in content
    
    print(f"safe_exam_session_reset関数: {'✅ あり' if has_reset_func else '❌ なし'}")
    print(f"safe_session_check関数: {'✅ あり' if has_check_func else '❌ なし'}")
    
    # 7. 変更箇所の詳細確認
    print("\n📍 変更箇所詳細:")
    
    lines_with_reset = []
    for i, line in enumerate(lines):
        if 'safe_exam_session_reset()' in line:
            lines_with_reset.append((i + 1, line.strip()))
    
    for line_no, line_content in lines_with_reset:
        print(f"  行{line_no}: {line_content}")
    
    # 8. 総合判定
    print("\n📋 総合判定:")
    
    all_checks = [
        verification_results['file_integrity'],
        verification_results['syntax_check'],
        verification_results['function_calls'] == 1,
        verification_results['remaining_pops'] == 5,
        verification_results['backup_exists'],
        has_reset_func,
        has_check_func
    ]
    
    success_rate = sum(all_checks) / len(all_checks) * 100
    
    print(f"成功率: {success_rate:.1f}% ({sum(all_checks)}/{len(all_checks)})")
    
    if all(all_checks):
        print("✅ 第1段階置換: 完全成功")
        print("✅ 次のステップ: 動作確認")
        status = "SUCCESS"
    elif success_rate >= 80:
        print("⚠️ 第1段階置換: 部分的成功")
        print("⚠️ 要注意点あり")
        status = "PARTIAL"
    else:
        print("❌ 第1段階置換: 失敗")
        print("❌ ロールバック推奨")
        status = "FAILED"
    
    # 9. 次のステップ推奨
    print("\n🚀 次のステップ推奨:")
    
    if status == "SUCCESS":
        print("  1. 簡単な動作確認（Flaskアプリ起動）")
        print("  2. 一問目の表示テスト")
        print("  3. セッション初期化の動作確認")
        print("  4. 成功したら第2段階へ")
    elif status == "PARTIAL":
        print("  1. 問題点の詳細確認")
        print("  2. 軽微な問題なら動作確認継続")
        print("  3. 重大な問題ならロールバック")
    else:
        print("  1. 即座にロールバック実行")
        print(f"  2. cp {backup_file} app.py")
        print("  3. 問題原因の分析")
    
    # 10. ロールバックコマンド
    print("\n🔄 緊急ロールバックコマンド:")
    print(f"  cp {backup_file} app.py")
    
    print(f"\n✅ 検証完了 - ステータス: {status}")
    
    return verification_results

if __name__ == "__main__":
    post_replacement_verification()