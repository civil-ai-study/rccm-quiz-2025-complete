#!/usr/bin/env python3
"""
🛡️ ULTRA SAFE 関数呼び出し詳細検証
関数呼び出し数の詳細分析（定義と呼び出しを分離）
"""

import re
from datetime import datetime

def detailed_function_call_verification():
    """関数呼び出しの詳細検証"""
    print("🛡️ ULTRA SAFE 関数呼び出し詳細検証")
    print("=" * 60)
    print(f"検証時刻: {datetime.now()}")
    
    with open('app.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"✅ ファイル読み込み: {len(lines)}行")
    
    # 1. 関数定義の検索
    print("\n🔍 関数定義の検索:")
    function_definitions = []
    
    for i, line in enumerate(lines):
        if re.search(r'def\s+safe_exam_session_reset\s*\(', line):
            function_definitions.append((i + 1, line.strip()))
    
    print(f"関数定義: {len(function_definitions)}箇所")
    for line_no, line_content in function_definitions:
        print(f"  行{line_no}: {line_content}")
    
    # 2. 関数呼び出しの検索
    print("\n🔍 関数呼び出しの検索:")
    function_calls = []
    
    for i, line in enumerate(lines):
        # 関数定義行は除外し、実際の呼び出しのみ検索
        if ('safe_exam_session_reset()' in line and 
            'def safe_exam_session_reset' not in line and
            line.strip() != '' and
            not line.strip().startswith('#')):
            function_calls.append((i + 1, line.strip()))
    
    print(f"関数呼び出し: {len(function_calls)}箇所")
    for line_no, line_content in function_calls:
        print(f"  行{line_no}: {line_content}")
        
        # 呼び出しのコンテキストを表示
        if i > 0:
            print(f"    前行: {lines[line_no - 2].strip()}")
        print(f"    当行: {line_content}")
        if line_no < len(lines):
            print(f"    次行: {lines[line_no].strip()}")
    
    # 3. session.pop残存確認
    print("\n🔍 session.pop残存確認:")
    session_pops = []
    
    for i, line in enumerate(lines):
        if "session.pop('exam_question_ids'" in line:
            session_pops.append((i + 1, line.strip()))
    
    print(f"session.pop残存: {len(session_pops)}箇所")
    for line_no, line_content in session_pops[:3]:  # 最初の3箇所を表示
        print(f"  行{line_no}: {line_content}")
    
    if len(session_pops) > 3:
        print(f"  ... 他{len(session_pops) - 3}箇所")
    
    # 4. 期待値との比較
    print("\n📊 期待値との比較:")
    
    expected_definitions = 1
    expected_calls = 1
    expected_remaining_pops = 5
    
    definition_ok = len(function_definitions) == expected_definitions
    calls_ok = len(function_calls) == expected_calls
    pops_ok = len(session_pops) == expected_remaining_pops
    
    print(f"関数定義: {len(function_definitions)}/{expected_definitions} {'✅' if definition_ok else '❌'}")
    print(f"関数呼び出し: {len(function_calls)}/{expected_calls} {'✅' if calls_ok else '❌'}")
    print(f"残存session.pop: {len(session_pops)}/{expected_remaining_pops} {'✅' if pops_ok else '❌'}")
    
    # 5. 総合判定
    print("\n📋 詳細総合判定:")
    
    all_checks = [definition_ok, calls_ok, pops_ok]
    success_rate = sum(all_checks) / len(all_checks) * 100
    
    print(f"成功率: {success_rate:.1f}% ({sum(all_checks)}/{len(all_checks)})")
    
    if all(all_checks):
        print("✅ 第1段階置換: 完全成功（詳細検証）")
        print("✅ 先ほどの検出は誤判定でした")
        print("✅ 実際は期待通りの状態です")
        status = "SUCCESS"
    else:
        print("❌ 問題あり")
        if not definition_ok:
            print(f"  - 関数定義数異常: {len(function_definitions)}")
        if not calls_ok:
            print(f"  - 関数呼び出し数異常: {len(function_calls)}")
        if not pops_ok:
            print(f"  - 残存session.pop数異常: {len(session_pops)}")
        status = "FAILED"
    
    # 6. 次のステップ
    print("\n🚀 次のステップ:")
    
    if status == "SUCCESS":
        print("  1. 動作確認テスト実行")
        print("  2. 第2段階置換の準備")
        print("  3. バックアップポイント作成")
    else:
        print("  1. 問題の詳細分析")
        print("  2. 必要に応じてロールバック")
    
    print(f"\n✅ 詳細検証完了 - ステータス: {status}")
    
    return {
        'definitions': len(function_definitions),
        'calls': len(function_calls),
        'remaining_pops': len(session_pops),
        'status': status
    }

if __name__ == "__main__":
    detailed_function_call_verification()