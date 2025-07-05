#!/usr/bin/env python3
"""
🛡️ ULTRA SAFE 差分チェッカー
置換前後の差分を詳細に確認
"""

import difflib
from datetime import datetime

def check_replacement_diff():
    """置換前後の差分を詳細チェック"""
    print("🛡️ ULTRA SAFE 差分チェック")
    print("=" * 60)
    print(f"チェック時刻: {datetime.now()}")
    
    # ファイル読み込み
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            original_lines = f.readlines()
        
        with open('app.py.temp_single_replace', 'r', encoding='utf-8') as f:
            modified_lines = f.readlines()
            
        print("✅ ファイル読み込み成功")
    except Exception as e:
        print(f"❌ ファイル読み込みエラー: {e}")
        return
    
    # 差分計算
    diff = list(difflib.unified_diff(
        original_lines, 
        modified_lines,
        fromfile='app.py (元)',
        tofile='app.py.temp_single_replace (変更後)',
        lineterm=''
    ))
    
    if not diff:
        print("⚠️ 差分なし - 変更が適用されていません")
        return
    
    print(f"\n📊 差分統計:")
    print(f"  元ファイル行数: {len(original_lines):,}")
    print(f"  変更後行数: {len(modified_lines):,}")
    print(f"  行数差: {len(modified_lines) - len(original_lines):+d}")
    
    # 変更箇所の詳細表示
    print("\n🔍 変更箇所の詳細:")
    print("-" * 60)
    
    change_count = 0
    for line in diff:
        if line.startswith('@@'):
            print(f"\n📍 {line}")
        elif line.startswith('-') and not line.startswith('---'):
            print(f"🔴 削除: {line[1:].rstrip()}")
            change_count += 1
        elif line.startswith('+') and not line.startswith('+++'):
            print(f"🟢 追加: {line[1:].rstrip()}")
        elif line.startswith(' '):
            # コンテキスト行（変更されていない行）
            if change_count > 0:  # 変更がある場合のみ表示
                print(f"⚪ 保持: {line[1:].rstrip()}")
    
    # 変更内容の安全性確認
    print(f"\n🔒 安全性確認:")
    
    # 危険なパターンをチェック
    dangerous_patterns = [
        'import ',
        'from ',
        'def ',
        'class ',
        'app.route',
        'session.clear()',
        'del session'
    ]
    
    safe = True
    for line in diff:
        if line.startswith('+') and not line.startswith('+++'):
            content = line[1:].strip()
            for pattern in dangerous_patterns:
                if pattern in content and 'safe_exam_session_reset()' not in content:
                    print(f"⚠️ 潜在的リスク: {content}")
                    safe = False
    
    if safe:
        print("✅ 危険なパターンなし")
    
    # 期待される変更パターンの確認
    print(f"\n🎯 期待される変更パターンの確認:")
    
    expected_removals = [
        "session.pop('exam_question_ids', None)",
        "session.pop('exam_current', None)", 
        "session.pop('exam_category', None)"
    ]
    
    expected_addition = "safe_exam_session_reset()"
    
    removals_found = []
    addition_found = False
    
    for line in diff:
        if line.startswith('-') and not line.startswith('---'):
            content = line[1:].strip()
            for expected in expected_removals:
                if expected in content:
                    removals_found.append(expected)
        elif line.startswith('+') and not line.startswith('+++'):
            content = line[1:].strip()
            if expected_addition in content:
                addition_found = True
    
    print(f"  期待される削除: {len(expected_removals)}箇所")
    print(f"  実際の削除: {len(removals_found)}箇所")
    
    for removal in removals_found:
        print(f"    ✅ {removal}")
    
    print(f"  期待される追加: {'✅ あり' if addition_found else '❌ なし'}")
    
    # 総合判定
    print(f"\n📋 総合判定:")
    
    if (len(removals_found) == 3 and addition_found and safe):
        print("✅ 変更内容は期待通りです")
        print("✅ 安全性に問題ありません")
        print("✅ 適用準備完了")
        
        print(f"\n🚀 適用コマンド:")
        print("  mv app.py.temp_single_replace app.py")
        
        return True
    else:
        print("❌ 期待される変更と一致しません")
        print("❌ 適用を見送ることを推奨します")
        
        return False

if __name__ == "__main__":
    success = check_replacement_diff()
    print(f"\n{'✅ 差分チェック完了' if success else '❌ 差分チェック失敗'}")