#!/usr/bin/env python3
"""
🛡️ 現在の状態検証ツール
app.pyの現在の状態を詳細に確認
"""

import os
import re
from datetime import datetime

def verify_current_state():
    """現在のapp.pyの状態を詳細に検証"""
    print("🛡️ 現在の状態検証")
    print("=" * 60)
    print(f"検証時刻: {datetime.now()}")
    
    if not os.path.exists('app.py'):
        print("❌ app.pyが存在しません")
        return
    
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
        lines = content.split('\n')
    
    print(f"\n📊 ファイル情報:")
    print(f"  サイズ: {os.path.getsize('app.py'):,} bytes")
    print(f"  行数: {len(lines):,} 行")
    
    # 1. 追加された関数の確認
    print(f"\n🔍 追加された関数:")
    
    # safe_exam_session_reset関数の確認
    reset_func_found = False
    reset_func_line = None
    for i, line in enumerate(lines):
        if 'def safe_exam_session_reset(' in line:
            reset_func_found = True
            reset_func_line = i + 1
            break
    
    print(f"  safe_exam_session_reset: {'✅ あり' if reset_func_found else '❌ なし'}")
    if reset_func_found:
        print(f"    位置: 行{reset_func_line}")
    
    # safe_session_check関数の確認
    check_func_found = False
    check_func_line = None
    for i, line in enumerate(lines):
        if 'def safe_session_check(' in line:
            check_func_found = True
            check_func_line = i + 1
            break
    
    print(f"  safe_session_check: {'✅ あり' if check_func_found else '❌ なし'}")
    if check_func_found:
        print(f"    位置: 行{check_func_line}")
    
    # 2. 関数呼び出しの確認
    print(f"\n🔍 関数呼び出し箇所:")
    
    # safe_exam_session_reset()の呼び出し
    reset_calls = []
    for i, line in enumerate(lines):
        if 'safe_exam_session_reset()' in line and 'def safe_exam_session_reset' not in line:
            reset_calls.append(i + 1)
    
    print(f"  safe_exam_session_reset() 呼び出し: {len(reset_calls)}箇所")
    for call_line in reset_calls[:5]:  # 最初の5つを表示
        print(f"    行{call_line}: {lines[call_line-1].strip()}")
    
    # 3. 残っているsession.pop呼び出しの確認
    print(f"\n🔍 残存するsession.pop呼び出し:")
    
    session_pops = []
    for i, line in enumerate(lines):
        if "session.pop('exam_question_ids'" in line:
            session_pops.append((i + 1, line.strip()))
    
    print(f"  session.pop('exam_question_ids'): {len(session_pops)}箇所")
    for line_no, line_content in session_pops[:3]:
        print(f"    行{line_no}: {line_content}")
    
    # 4. 構文チェック
    print(f"\n🔍 構文チェック:")
    import subprocess
    result = subprocess.run(['python3', '-m', 'py_compile', 'app.py'], 
                          capture_output=True, text=True)
    
    if result.returncode == 0:
        print("  ✅ 構文エラーなし")
    else:
        print(f"  ❌ 構文エラーあり: {result.stderr}")
    
    # 5. 変更サマリー
    print(f"\n📋 変更サマリー:")
    print(f"  関数追加: {'✅ 完了' if reset_func_found and check_func_found else '❌ 未完了'}")
    print(f"  置換実施: {len(reset_calls)}箇所")
    print(f"  未置換: {len(session_pops)}箇所")
    
    total_replacements = len(reset_calls) + len(session_pops)
    if total_replacements > 0:
        progress = (len(reset_calls) / total_replacements) * 100
        print(f"  進捗: {progress:.1f}% ({len(reset_calls)}/{total_replacements})")
    
    # 6. 推奨事項
    print(f"\n🎯 推奨事項:")
    if len(reset_calls) == 0:
        print("  ⚠️ 関数は追加されていますが、まだ使用されていません")
        print("  → 動作に影響なし、そのままテスト可能")
    elif len(reset_calls) == 1:
        print("  ✅ 1箇所のみ置換済み - 最小限の変更")
        print("  → 動作確認に最適な状態")
    else:
        print(f"  ⚠️ {len(reset_calls)}箇所が既に置換済み")
        print("  → 慎重な動作確認が必要")
    
    # 7. テスト推奨項目
    print(f"\n🧪 動作確認チェックリスト:")
    print("  [ ] Flaskアプリケーションの起動")
    print("  [ ] トップページの表示")
    print("  [ ] 部門選択画面の表示")
    print("  [ ] 問題開始（セッション作成）")
    print("  [ ] 1問目の表示")
    print("  [ ] 回答送信")
    print("  [ ] 2問目への遷移")
    
    print(f"\n✅ 検証完了")

if __name__ == "__main__":
    verify_current_state()