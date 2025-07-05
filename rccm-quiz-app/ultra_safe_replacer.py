#!/usr/bin/env python3
"""
🛡️ ULTRA SAFE 置換実行ツール
副作用ゼロで段階的にsession.pop呼び出しを置換
"""

import re
import os
from datetime import datetime

def create_replacement_preview():
    """置換のプレビューを作成"""
    print("🛡️ ULTRA SAFE 置換プレビュー")
    print("=" * 60)
    print(f"実行時刻: {datetime.now()}")
    
    # app.pyの読み込み
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            lines = f.readlines()
        print(f"✅ app.py読み込み成功: {len(lines)}行")
    except Exception as e:
        print(f"❌ ファイル読み込みエラー: {e}")
        return None
    
    # 置換対象の行を特定
    replacements = []
    
    # パターン1: 連続する3行のsession.pop
    i = 0
    while i < len(lines):
        if i + 2 < len(lines):
            if ("session.pop('exam_question_ids'" in lines[i] and
                "session.pop('exam_current'" in lines[i + 1] and
                "session.pop('exam_category'" in lines[i + 2]):
                
                replacements.append({
                    'type': 'triple_pop',
                    'start_line': i,
                    'end_line': i + 2,
                    'original': [lines[i].rstrip(), lines[i+1].rstrip(), lines[i+2].rstrip()],
                    'replacement': ['safe_exam_session_reset()']
                })
                i += 3
                continue
        i += 1
    
    print(f"\n📍 置換対象: {len(replacements)}箇所")
    
    # プレビュー表示
    for idx, rep in enumerate(replacements, 1):
        print(f"\n置換箇所 {idx}:")
        print(f"  行 {rep['start_line'] + 1}-{rep['end_line'] + 1}:")
        for line in rep['original']:
            print(f"    - {line}")
        print(f"  置換後:")
        for line in rep['replacement']:
            print(f"    + {line}")
    
    return replacements, lines

def apply_single_replacement(replacements, lines, index):
    """1つの置換を適用"""
    if index >= len(replacements):
        print(f"❌ インデックス {index} は範囲外です")
        return None
    
    rep = replacements[index]
    print(f"\n🔧 置換 {index + 1}/{len(replacements)} を適用中...")
    
    # 新しい行リストを作成
    new_lines = []
    i = 0
    
    while i < len(lines):
        if i == rep['start_line']:
            # インデントを保持
            indent = len(lines[i]) - len(lines[i].lstrip())
            replacement_line = ' ' * indent + rep['replacement'][0] + '\n'
            new_lines.append(replacement_line)
            # 元の行をスキップ
            i = rep['end_line'] + 1
        else:
            new_lines.append(lines[i])
            i += 1
    
    return new_lines

def save_with_backup(new_lines, suffix=""):
    """バックアップを作成してから保存"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"app.py.backup_replace_{timestamp}{suffix}"
    
    # バックアップ作成
    os.rename('app.py', backup_name)
    print(f"✅ バックアップ作成: {backup_name}")
    
    # 新しい内容を保存
    try:
        with open('app.py', 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        print("✅ app.py更新完了")
        return True
    except Exception as e:
        print(f"❌ 保存エラー: {e}")
        # ロールバック
        os.rename(backup_name, 'app.py')
        print("🔄 ロールバック実行")
        return False

def main():
    """メイン実行"""
    print("🛡️ ULTRA SAFE 段階的置換実行")
    print("=" * 60)
    
    # 1. プレビュー作成
    result = create_replacement_preview()
    if not result:
        return
    
    replacements, lines = result
    
    if not replacements:
        print("\n✅ 置換対象なし - 既に修正済みの可能性")
        return
    
    # 2. 段階的置換の提案
    print("\n📋 段階的置換計画:")
    print("  1. 最初の1箇所のみ置換してテスト")
    print("  2. 構文チェック実行")
    print("  3. 動作確認")
    print("  4. 問題なければ残りを置換")
    
    # 3. 最初の置換のみ実行
    print("\n🔧 第1段階: 最初の置換を実行")
    
    new_lines = apply_single_replacement(replacements, lines, 0)
    if not new_lines:
        return
    
    # 一時ファイルに保存
    temp_file = 'app.py.temp_first_replace'
    try:
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        print(f"✅ 一時ファイル作成: {temp_file}")
    except Exception as e:
        print(f"❌ 一時ファイル作成エラー: {e}")
        return
    
    # 構文チェック
    print("\n🔍 構文チェック実行中...")
    import subprocess
    result = subprocess.run(['python3', '-m', 'py_compile', temp_file], 
                          capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ 構文エラー検出: {result.stderr}")
        os.remove(temp_file)
        return
    
    print("✅ 構文チェック成功")
    
    # 4. 適用確認
    print(f"\n✅ 第1段階準備完了")
    print(f"📁 一時ファイル: {temp_file}")
    print("\n次のステップ:")
    print(f"  1. {temp_file}の内容を確認")
    print(f"  2. 問題なければ: mv {temp_file} app.py")
    print(f"  3. アプリケーションの動作確認")
    print(f"  4. 成功したら残り{len(replacements) - 1}箇所を置換")
    
    print("\n🛡️ 副作用: 最小限（一時ファイルのみ作成）")
    print("✅ ULTRA SAFE置換準備完了")

if __name__ == "__main__":
    main()