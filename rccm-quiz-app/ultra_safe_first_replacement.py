#!/usr/bin/env python3
"""
🛡️ ULTRA SAFE 最初の1箇所だけ置換
副作用ゼロで最小限の変更を実施
"""

import os
import shutil
from datetime import datetime

def ultra_safe_single_replacement():
    """最初の1箇所のみを安全に置換"""
    print("🛡️ ULTRA SAFE 最初の1箇所置換")
    print("=" * 60)
    print(f"実行時刻: {datetime.now()}")
    print("🔒 副作用: ゼロ（1箇所のみ、バックアップ付き）")
    
    # 1. 事前チェック
    print("\n📍 事前チェック:")
    
    if not os.path.exists('app.py'):
        print("❌ app.pyが存在しません")
        return False
    
    # バックアップ作成
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"app.py.backup_before_first_replace_{timestamp}"
    shutil.copy2('app.py', backup_name)
    print(f"✅ バックアップ作成: {backup_name}")
    
    # 2. ファイル読み込み
    with open('app.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"✅ app.py読み込み: {len(lines)}行")
    
    # 3. 最初の置換対象を特定
    print("\n🔍 最初の置換対象を探索:")
    
    target_found = False
    target_line = None
    
    # 3行連続のsession.popパターンを探す
    for i in range(len(lines) - 2):
        if (i + 2 < len(lines) and
            "session.pop('exam_question_ids', None)" in lines[i] and
            "session.pop('exam_current', None)" in lines[i + 1] and
            "session.pop('exam_category', None)" in lines[i + 2]):
            
            target_line = i
            target_found = True
            print(f"✅ 置換対象発見: 行{i + 1}-{i + 3}")
            print(f"   {lines[i].strip()}")
            print(f"   {lines[i + 1].strip()}")
            print(f"   {lines[i + 2].strip()}")
            break
    
    if not target_found:
        print("❌ 置換対象が見つかりません")
        return False
    
    # 4. 置換内容の作成
    print("\n📝 置換内容:")
    
    # インデントを保持
    indent = len(lines[target_line]) - len(lines[target_line].lstrip())
    replacement = ' ' * indent + 'safe_exam_session_reset()\n'
    
    print(f"   置換後: {replacement.strip()}")
    
    # 5. 新しい内容を作成
    new_lines = []
    i = 0
    
    while i < len(lines):
        if i == target_line:
            # 置換実行
            new_lines.append(replacement)
            # 3行スキップ
            i += 3
        else:
            new_lines.append(lines[i])
            i += 1
    
    # 6. 一時ファイルに書き込み
    temp_file = 'app.py.temp_single_replace'
    with open(temp_file, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print(f"\n✅ 一時ファイル作成: {temp_file}")
    
    # 7. 構文チェック
    print("\n🔍 構文チェック:")
    import subprocess
    result = subprocess.run(['python3', '-m', 'py_compile', temp_file], 
                          capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ 構文エラー: {result.stderr}")
        os.remove(temp_file)
        return False
    
    print("✅ 構文チェック合格")
    
    # 8. 変更内容の確認
    print("\n📊 変更サマリー:")
    print(f"  元の行数: {len(lines)}")
    print(f"  新しい行数: {len(new_lines)}")
    print(f"  削減行数: {len(lines) - len(new_lines)}")
    print(f"  置換箇所: 1箇所（行{target_line + 1}）")
    
    # 9. 適用準備完了
    print("\n✅ 準備完了")
    print(f"📁 一時ファイル: {temp_file}")
    print(f"📁 バックアップ: {backup_name}")
    
    print("\n📋 次のステップ:")
    print("  1. 一時ファイルの内容確認")
    print("  2. 問題なければ適用: mv app.py.temp_single_replace app.py")
    print("  3. 動作確認")
    print("  4. 問題があれば復元: cp " + backup_name + " app.py")
    
    print("\n🛡️ 副作用: ゼロ（一時ファイルのみ作成）")
    
    return True

if __name__ == "__main__":
    success = ultra_safe_single_replacement()
    if success:
        print("\n✅ ULTRA SAFE置換準備完了")
    else:
        print("\n❌ 置換準備失敗")