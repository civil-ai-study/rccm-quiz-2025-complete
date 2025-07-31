#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ULTRA SYNC 単純型エラー修正
app.py内でsession.get('exam_current')が関わる型エラーを個別に修正
"""

import re
from datetime import datetime

def find_exam_current_usage():
    """app.py内のexam_current使用箇所を検索"""
    print("ULTRA SYNC 型エラー箇所の特定")
    print(f"検索時刻: {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 50)
    
    try:
        with open('rccm-quiz-app/app.py', 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        print(f"総行数: {len(lines)}")
        
        # exam_currentが使用されている行を検索
        exam_current_lines = []
        
        for i, line in enumerate(lines, 1):
            if "session.get('exam_current'" in line or 'session.get("exam_current"' in line:
                # 型チェックが既にある行はスキップ
                if 'isinstance' not in line and 'int(' not in line:
                    # 比較演算子や算術演算子がある行のみ対象
                    if any(op in line for op in ['>=', '<=', '>', '<', '==', '!=', '+', '-', '*', '/']):
                        exam_current_lines.append((i, line.strip()))
        
        print(f"\n修正対象行: {len(exam_current_lines)}行")
        
        for line_no, line_content in exam_current_lines[:10]:  # 最初の10行のみ表示
            print(f"  行{line_no}: {line_content}")
        
        return exam_current_lines
        
    except Exception as e:
        print(f"検索エラー: {e}")
        return []

def create_safe_type_function():
    """型安全変換関数をapp.pyに追加"""
    print("\n型安全変換関数の追加")
    
    try:
        with open('rccm-quiz-app/app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 型安全変換関数の定義
        safe_function = '''
def get_exam_current_safe(session, default=0):
    """セッションからexam_currentを型安全に取得"""
    try:
        raw_value = session.get('exam_current', default)
        if isinstance(raw_value, int):
            return raw_value
        elif isinstance(raw_value, str) and raw_value.isdigit():
            return int(raw_value)
        else:
            return default
    except (ValueError, TypeError):
        return default

'''
        
        # 関数が既に存在するかチェック
        if 'def get_exam_current_safe(' in content:
            print("  型安全関数は既に存在します")
            return True
        
        # Flask(__name__)の直後に関数を挿入
        flask_pattern = r'(app = Flask\(__name__\)\n)'
        if re.search(flask_pattern, content):
            new_content = re.sub(flask_pattern, r'\1' + safe_function, content)
            
            with open('rccm-quiz-app/app.py', 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print("  型安全関数を追加しました")
            return True
        else:
            print("  Flask app定義箇所が見つかりません")
            return False
            
    except Exception as e:
        print(f"  関数追加エラー: {e}")
        return False

def apply_targeted_fixes():
    """対象箇所のみの修正"""
    print("\n対象箇所の修正実行")
    
    try:
        with open('rccm-quiz-app/app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # バックアップ作成
        backup_path = f"rccm-quiz-app/app.py.backup_simple_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  バックアップ: {backup_path}")
        
        # 単純な置換修正
        fixes_applied = 0
        
        # 修正1: session.get('exam_current', 0) >= を安全に修正
        pattern1 = r"session\.get\('exam_current',\s*0\)\s*(>=|<=|>|<|==|!=)\s*(\w+)"
        replacement1 = r"get_exam_current_safe(session, 0) \1 \2"
        
        new_content, count1 = re.subn(pattern1, replacement1, content)
        fixes_applied += count1
        print(f"  修正1 (比較演算): {count1}箇所")
        
        # 修正2: session.get('exam_current') >= を安全に修正
        pattern2 = r"session\.get\('exam_current'\)\s*(>=|<=|>|<|==|!=)\s*(\w+)"
        replacement2 = r"get_exam_current_safe(session) \1 \2"
        
        new_content, count2 = re.subn(pattern2, replacement2, new_content)
        fixes_applied += count2
        print(f"  修正2 (デフォルトなし比較): {count2}箇所")
        
        # 修正3: session.get('exam_current', 0) + 算術演算
        pattern3 = r"session\.get\('exam_current',\s*0\)\s*([+\-*/])\s*(\d+)"
        replacement3 = r"get_exam_current_safe(session, 0) \1 \2"
        
        new_content, count3 = re.subn(pattern3, replacement3, new_content)
        fixes_applied += count3
        print(f"  修正3 (算術演算): {count3}箇所")
        
        # ファイルに書き戻し
        if fixes_applied > 0:
            with open('rccm-quiz-app/app.py', 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"  合計修正: {fixes_applied}箇所")
            return True
        else:
            print("  修正対象なし")
            return True
            
    except Exception as e:
        print(f"  修正エラー: {e}")
        return False

def main():
    print("ULTRA SYNC 単純型エラー修正")
    print("目的: 最小限の修正で型エラーを解決")
    print("=" * 60)
    
    # Step 1: 使用箇所の特定
    problem_lines = find_exam_current_usage()
    
    # Step 2: 型安全関数の追加
    function_added = create_safe_type_function()
    
    # Step 3: 対象修正の実行
    fixes_applied = apply_targeted_fixes() if function_added else False
    
    # 総合結果
    print("\n" + "=" * 60)
    print("ULTRA SYNC 単純修正結果")
    print("=" * 60)
    
    print(f"問題箇所特定: {len(problem_lines)}行")
    print(f"関数追加: {'成功' if function_added else '失敗'}")
    print(f"修正実行: {'成功' if fixes_applied else '失敗'}")
    
    if function_added and fixes_applied:
        print("\nULTRA SYNC 修正: 完了")
        print("型安全関数による修正が完了しました")
    else:
        print("\nULTRA SYNC 修正: 要再実行")
    
    return function_added and fixes_applied

if __name__ == "__main__":
    main()