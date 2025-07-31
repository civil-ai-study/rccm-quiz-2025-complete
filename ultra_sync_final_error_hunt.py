#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ULTRA SYNC 最終エラー狩り（安全版）
残存する型エラー箇所を完全特定し、次の修正対象を決定
"""

import re
from datetime import datetime

def hunt_remaining_type_errors():
    """残存型エラーの精密捜索"""
    print("ULTRA SYNC 最終エラー狩り")
    print(f"実行時刻: {datetime.now().strftime('%H:%M:%S')}")
    print("目的: 型エラー根絶のための最終捜索")
    print("=" * 50)
    
    try:
        with open('rccm-quiz-app/app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        print(f"ファイル解析: {len(lines)}行")
        
        # 危険パターンの検索
        dangerous_lines = []
        
        # パターン1: session.get('exam_current')の直接比較
        print("\nパターン1: 直接比較の検索")
        for i, line in enumerate(lines, 1):
            if "session.get('exam_current'" in line:
                # 比較演算子があるかチェック
                if any(op in line for op in [' >= ', ' <= ', ' > ', ' < ', ' == ', ' != ']):
                    # 型安全化されているかチェック
                    if not any(safe in line for safe in ['isinstance', 'get_exam_current_safe', 'int(']):
                        # 前後3行で型安全化されているかもチェック
                        context_start = max(0, i-3)
                        context_end = min(len(lines), i+3)
                        context = '\n'.join(lines[context_start:context_end])
                        
                        if not any(safe in context for safe in ['isinstance', 'try:', 'except:', 'get_exam_current_safe']):
                            dangerous_lines.append({
                                'line': i,
                                'content': line.strip(),
                                'type': 'direct_comparison',
                                'risk': 'high'
                            })
        
        print(f"  発見: {len([d for d in dangerous_lines if d['type'] == 'direct_comparison'])}箇所")
        
        # パターン2: len()との比較（特に危険）
        print("\nパターン2: len()比較の検索")
        for i, line in enumerate(lines, 1):
            if "session.get('exam_current'" in line and 'len(' in line:
                if any(op in line for op in [' >= len(', ' < len(', ' > len(']):
                    if not any(safe in line for safe in ['isinstance', 'get_exam_current_safe', 'int(']):
                        dangerous_lines.append({
                            'line': i,
                            'content': line.strip(),
                            'type': 'len_comparison',
                            'risk': 'critical'
                        })
        
        print(f"  発見: {len([d for d in dangerous_lines if d['type'] == 'len_comparison'])}箇所")
        
        # パターン3: 算術演算
        print("\nパターン3: 算術演算の検索")
        for i, line in enumerate(lines, 1):
            if "session.get('exam_current'" in line:
                if any(op in line for op in [' + ', ' - ', ' * ', ' / ']):
                    if not any(safe in line for safe in ['isinstance', 'get_exam_current_safe', 'int(']):
                        dangerous_lines.append({
                            'line': i,
                            'content': line.strip(),
                            'type': 'arithmetic',
                            'risk': 'medium'
                        })
        
        print(f"  発見: {len([d for d in dangerous_lines if d['type'] == 'arithmetic'])}箇所")
        
        return dangerous_lines
        
    except Exception as e:
        print(f"捜索エラー: {e}")
        return []

def select_next_target(dangerous_lines):
    """次修正対象の選択"""
    print(f"\n次修正対象の選択")
    
    if not dangerous_lines:
        print("  修正対象なし")
        return None
    
    # リスクレベル順にソート
    risk_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
    dangerous_lines.sort(key=lambda x: risk_order[x['risk']])
    
    # 最優先を選択
    target = dangerous_lines[0]
    
    print(f"  選択: 行{target['line']} ({target['risk']}リスク)")
    print(f"  内容: {target['content']}")
    print(f"  種類: {target['type']}")
    
    return target

def create_targeted_fix(target):
    """対象箇所の修正実行"""
    print(f"\n対象箇所の安全修正")
    
    if not target:
        print("  修正対象なし")
        return True
    
    try:
        # バックアップ作成
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = f"rccm-quiz-app/app.py.backup_final_{timestamp}"
        
        with open('rccm-quiz-app/app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"  バックアップ: {backup_path}")
        
        # 修正実行
        lines = content.split('\n')
        target_line_index = target['line'] - 1
        original_line = lines[target_line_index]
        
        print(f"  修正前: {original_line.strip()}")
        
        # 修正パターンの適用
        modified_line = original_line
        
        # session.get('exam_current', 0) >= を修正
        if " >= " in original_line or " <= " in original_line or " > " in original_line or " < " in original_line:
            modified_line = re.sub(
                r"session\.get\('exam_current',?\s*(\d*)\)",
                lambda m: f"get_exam_current_safe(session, {m.group(1) if m.group(1) else '0'})",
                original_line
            )
        
        # session.get('exam_current') + 1 を修正
        if " + " in original_line or " - " in original_line:
            modified_line = re.sub(
                r"session\.get\('exam_current',?\s*(\d*)\)",
                lambda m: f"get_exam_current_safe(session, {m.group(1) if m.group(1) else '0'})",
                original_line
            )
        
        if modified_line != original_line:
            print(f"  修正後: {modified_line.strip()}")
            lines[target_line_index] = modified_line
            
            # ファイル更新
            new_content = '\n'.join(lines)
            with open('rccm-quiz-app/app.py', 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"  修正完了: 行{target['line']}")
            return True
        else:
            print(f"  修正不要: パターン該当なし")
            return True
            
    except Exception as e:
        print(f"  修正エラー: {e}")
        return False

def main():
    print("ULTRA SYNC 最終エラー狩りシステム")
    print("目的: 型エラー根絶のための段階的修正")
    print("=" * 60)
    
    # Step 1: 残存エラー捜索
    dangerous_lines = hunt_remaining_type_errors()
    
    # Step 2: 次対象選択
    target = select_next_target(dangerous_lines)
    
    # Step 3: 修正実行
    fix_success = create_targeted_fix(target)
    
    # 結果
    print("\n" + "=" * 60)
    print("ULTRA SYNC 最終狩り結果")
    print("=" * 60)
    
    print(f"発見箇所: {len(dangerous_lines)}箇所")
    print(f"修正実行: {'成功' if fix_success else '失敗'}")
    
    if target and fix_success:
        print(f"修正完了: 行{target['line']}")
        print("次のステップ: 修正後動作確認テスト")
    elif not dangerous_lines:
        print("修正対象なし: 型エラー根絶完了の可能性")
    else:
        print("追加修正が必要")
    
    return fix_success

if __name__ == "__main__":
    main()