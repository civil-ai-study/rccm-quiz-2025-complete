#!/usr/bin/env python3
"""
🛡️ ULTRA SAFE 第2段階置換準備（修正版）
副作用ゼロで2箇所目の置換を慎重に準備
"""

import os
import shutil
from datetime import datetime

def ultra_safe_second_replacement_prep():
    """第2段階置換の安全な準備"""
    print("🛡️ ULTRA SAFE 第2段階置換準備")
    print("=" * 60)
    print(f"準備時刻: {datetime.now()}")
    print("🔒 副作用: ゼロ（準備と分析のみ）")
    
    # 1. 現在の状態確認
    print("\n📊 現在の状態確認:")
    
    if not os.path.exists('app.py'):
        print("❌ app.pyが存在しません")
        return False
    
    with open('app.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"✅ ファイル読み込み: {len(lines)}行")
    
    # 2. 残存するsession.pop箇所の特定
    print("\n🔍 残存session.pop箇所の特定:")
    
    session_pop_groups = []
    i = 0
    
    while i < len(lines) - 2:
        # 3行連続のsession.popパターンを探す
        if (i + 2 < len(lines) and
            "session.pop('exam_question_ids', None)" in lines[i] and
            "session.pop('exam_current', None)" in lines[i + 1] and
            "session.pop('exam_category', None)" in lines[i + 2]):
            
            session_pop_groups.append({
                'start_line': i + 1,  # 1-based
                'end_line': i + 3,    # 1-based
                'lines': [
                    lines[i].strip(),
                    lines[i + 1].strip(),
                    lines[i + 2].strip()
                ],
                'context_before': lines[max(0, i-1)].strip() if i > 0 else "",
                'context_after': lines[min(len(lines)-1, i+3)].strip() if i+3 < len(lines) else ""
            })
            i += 3  # スキップ
        else:
            i += 1
    
    print(f"発見された置換対象: {len(session_pop_groups)}箇所")
    
    if len(session_pop_groups) == 0:
        print("✅ 置換対象なし - 全て完了済み")
        return True
    
    # 3. 次の置換対象を選定
    print("\n🎯 次の置換対象選定:")
    
    next_target = session_pop_groups[0]
    print(f"選定: 行{next_target['start_line']}-{next_target['end_line']}")
    print(f"前後コンテキスト:")
    print(f"  前行: {next_target['context_before']}")
    print(f"  対象: {next_target['lines'][0]}")
    print(f"        {next_target['lines'][1]}")
    print(f"        {next_target['lines'][2]}")
    print(f"  後行: {next_target['context_after']}")
    
    # 4. 置換安全性の評価
    print("\n🔒 置換安全性評価:")
    
    # 各行の内容チェック
    has_exam_question_ids = 'exam_question_ids' in next_target['lines'][0]
    has_exam_current = 'exam_current' in next_target['lines'][1]
    has_exam_category = 'exam_category' in next_target['lines'][2]
    
    safety_checks = {
        'three_line_pattern': len(next_target['lines']) == 3,
        'correct_keys': has_exam_question_ids and has_exam_current and has_exam_category,
        'session_pop_pattern': all('session.pop(' in line for line in next_target['lines']),
        'no_dangerous_context': 'import' not in next_target['context_before'] and 
                               'def ' not in next_target['context_before']
    }
    
    for check, result in safety_checks.items():
        status = "✅" if result else "❌"
        print(f"  {check}: {status}")
    
    # 詳細チェック
    print("\n  詳細チェック:")
    print(f"    exam_question_ids: {'✅' if has_exam_question_ids else '❌'}")
    print(f"    exam_current: {'✅' if has_exam_current else '❌'}")
    print(f"    exam_category: {'✅' if has_exam_category else '❌'}")
    
    all_safe = all(safety_checks.values())
    print(f"\n総合安全性: {'✅ 安全' if all_safe else '❌ 危険'}")
    
    if not all_safe:
        print("⚠️ 安全性に問題があります - 置換を停止")
        return False
    
    # 5. バックアップ作成
    print("\n📁 バックアップ作成:")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"app.py.backup_before_second_replace_{timestamp}"
    
    try:
        shutil.copy2('app.py', backup_name)
        backup_size = os.path.getsize(backup_name)
        print(f"✅ バックアップ作成: {backup_name}")
        print(f"  サイズ: {backup_size:,} bytes")
    except Exception as e:
        print(f"❌ バックアップ作成エラー: {e}")
        return False
    
    # 6. 置換内容のプレビュー
    print("\n📝 置換プレビュー:")
    
    # インデントを保持
    start_line_index = next_target['start_line'] - 1  # 0-based
    indent = len(lines[start_line_index]) - len(lines[start_line_index].lstrip())
    replacement = ' ' * indent + 'safe_exam_session_reset()\n'
    
    print("変更内容:")
    print("  削除:")
    for line in next_target['lines']:
        print(f"    - {line}")
    print("  追加:")
    print(f"    + {replacement.strip()}")
    
    # 7. 新しいファイル内容の作成（メモリ上のみ）
    print("\n🧪 変更内容作成（メモリ上）:")
    
    new_lines = []
    i = 0
    
    while i < len(lines):
        if i + 1 == next_target['start_line']:  # 1-based to 0-based
            # 置換実行
            new_lines.append(replacement)
            # 3行スキップ
            i += 3
        else:
            new_lines.append(lines[i])
            i += 1
    
    print(f"✅ 新しい内容作成完了")
    print(f"  元の行数: {len(lines)}")
    print(f"  新しい行数: {len(new_lines)}")
    print(f"  削減行数: {len(lines) - len(new_lines)}")
    
    # 8. 準備完了確認
    print("\n📋 準備状況:")
    
    preparation_items = [
        f"✅ 置換対象特定: 行{next_target['start_line']}-{next_target['end_line']}",
        f"✅ 安全性確認: 全項目合格",
        f"✅ バックアップ作成: {backup_name}",
        f"✅ 変更内容準備: メモリ上で完成",
        f"✅ 副作用: ゼロ（ファイル未変更）"
    ]
    
    for item in preparation_items:
        print(f"  {item}")
    
    # 9. 次のステップ案内
    print("\n🚀 次のステップ:")
    print("  1. 一時ファイルへの書き込み")
    print("  2. 構文チェック実行")
    print("  3. 差分確認")
    print("  4. 適用実行")
    
    print(f"\n✅ 第2段階準備完了")
    
    # 準備データを返す
    return {
        'target': next_target,
        'backup_file': backup_name,
        'new_lines': new_lines,
        'replacement': replacement.strip(),
        'safe': all_safe,
        'remaining_targets': len(session_pop_groups) - 1
    }

if __name__ == "__main__":
    result = ultra_safe_second_replacement_prep()
    if result:
        if isinstance(result, dict):
            print(f"\n成功: 第2段階準備完了")
            print(f"残り置換対象: {result['remaining_targets']}箇所")
        else:
            print(f"\n完了: 全て置換済み")
    else:
        print(f"\n失敗: 準備を中断")