#!/usr/bin/env python3
"""
🛡️ ULTRA SAFE 第2段階置換実行
準備済みの内容を安全に適用
"""

import os
import subprocess
from datetime import datetime

def ultra_safe_second_replacement_execute():
    """第2段階置換の安全な実行"""
    print("🛡️ ULTRA SAFE 第2段階置換実行")
    print("=" * 60)
    print(f"実行時刻: {datetime.now()}")
    print("🔒 副作用: 最小限（一時ファイルのみ）")
    
    # 1. 現在の状態確認
    print("\n📊 実行前状態確認:")
    
    if not os.path.exists('app.py'):
        print("❌ app.pyが存在しません")
        return False
    
    with open('app.py', 'r', encoding='utf-8') as f:
        original_lines = f.readlines()
    
    print(f"✅ 元ファイル: {len(original_lines)}行")
    
    # 2. 置換対象の再確認
    print("\n🔍 置換対象再確認:")
    
    # 2494-2496行の確認
    target_start = 2493  # 0-based
    target_end = 2496    # 0-based
    
    if target_end >= len(original_lines):
        print("❌ 対象行が範囲外です")
        return False
    
    target_lines = [
        original_lines[target_start].strip(),
        original_lines[target_start + 1].strip(),
        original_lines[target_start + 2].strip()
    ]
    
    print("対象行:")
    for i, line in enumerate(target_lines):
        print(f"  行{target_start + i + 1}: {line}")
    
    # 期待される内容の確認
    expected_patterns = [
        "session.pop('exam_question_ids', None)",
        "session.pop('exam_current', None)",
        "session.pop('exam_category', None)"
    ]
    
    patterns_match = all(pattern in target_lines[i] for i, pattern in enumerate(expected_patterns))
    
    if not patterns_match:
        print("❌ 期待される内容と一致しません")
        print("期待:")
        for pattern in expected_patterns:
            print(f"  {pattern}")
        return False
    
    print("✅ 対象行確認: 期待通り")
    
    # 3. 新しい内容の作成
    print("\n📝 新しい内容作成:")
    
    # インデントを保持
    indent = len(original_lines[target_start]) - len(original_lines[target_start].lstrip())
    replacement = ' ' * indent + 'safe_exam_session_reset()\n'
    
    print(f"置換内容: {replacement.strip()}")
    print(f"インデント: {indent}文字")
    
    # 新しい行リストを作成
    new_lines = []
    for i, line in enumerate(original_lines):
        if i == target_start:
            # 置換実行
            new_lines.append(replacement)
            # 3行スキップするため、i+1, i+2はスキップ
        elif i in [target_start + 1, target_start + 2]:
            # スキップ（置換により削除）
            continue
        else:
            new_lines.append(line)
    
    print(f"✅ 新しい内容作成完了")
    print(f"  元の行数: {len(original_lines)}")
    print(f"  新しい行数: {len(new_lines)}")
    print(f"  削減行数: {len(original_lines) - len(new_lines)}")
    
    # 4. 一時ファイル作成
    print("\n📁 一時ファイル作成:")
    
    temp_file = 'app.py.temp_second_replace'
    
    try:
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        
        temp_size = os.path.getsize(temp_file)
        print(f"✅ 一時ファイル作成: {temp_file}")
        print(f"  サイズ: {temp_size:,} bytes")
        
    except Exception as e:
        print(f"❌ 一時ファイル作成エラー: {e}")
        return False
    
    # 5. 構文チェック
    print("\n🔍 構文チェック:")
    
    result = subprocess.run(['python3', '-m', 'py_compile', temp_file], 
                          capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ 構文エラー: {result.stderr}")
        # 一時ファイルを削除
        os.remove(temp_file)
        return False
    
    print("✅ 構文チェック合格")
    
    # 6. 変更内容の確認
    print("\n📊 変更内容確認:")
    
    # 置換された関数呼び出しの数を確認
    with open(temp_file, 'r', encoding='utf-8') as f:
        new_content = f.read()
    
    reset_calls = new_content.count('safe_exam_session_reset()')
    remaining_pops = new_content.count("session.pop('exam_question_ids'")
    
    print(f"safe_exam_session_reset() 呼び出し: {reset_calls}箇所")
    print(f"残存session.pop: {remaining_pops}箇所")
    
    # 期待値: 2箇所の関数呼び出し、4箇所の残存session.pop
    if reset_calls == 2 and remaining_pops == 4:
        print("✅ 期待通りの変更")
    else:
        print(f"⚠️ 予期しない変更: reset={reset_calls}, pop={remaining_pops}")
    
    # 7. 実行準備完了
    print("\n✅ 実行準備完了")
    print(f"📁 一時ファイル: {temp_file}")
    print(f"📁 バックアップ: app.py.backup_before_second_replace_20250705_111158")
    
    print("\n🚀 適用コマンド:")
    print(f"  mv {temp_file} app.py")
    
    print("\n🔄 ロールバックコマンド:")
    print("  cp app.py.backup_before_second_replace_20250705_111158 app.py")
    
    print(f"\n🛡️ 副作用: 最小限（一時ファイルのみ作成）")
    
    return True

if __name__ == "__main__":
    success = ultra_safe_second_replacement_execute()
    if success:
        print("\n✅ 第2段階置換実行準備完了")
    else:
        print("\n❌ 第2段階置換実行準備失敗")