#!/usr/bin/env python3
"""
進捗カウンター表示問題のデバッグスクリプト
道路部門で「次の問題へ (2/10)」と表示される問題を調査
"""

import json
import sys
from datetime import datetime

def analyze_progress_logic():
    """進捗カウンターのロジックを分析"""
    
    print("=== 進捗カウンター表示ロジック分析 ===\n")
    
    # ケース1: 最初の問題を表示（exam_current = 0）
    print("【ケース1】最初の問題を表示")
    exam_current = 0
    total_questions = 10
    
    # exam.htmlでの表示
    current_no_display = exam_current + 1  # 0 + 1 = 1
    print(f"exam.html: 問題 {current_no_display}/{total_questions}")
    print(f"  - exam_current (0ベース): {exam_current}")
    print(f"  - 表示用番号 (1ベース): {current_no_display}")
    
    # ユーザーが回答後、POSTリクエストで処理
    print("\n【ユーザーが回答】")
    # POSTハンドラーでの処理
    safe_current_no = min(exam_current, total_questions - 1)  # min(0, 9) = 0
    safe_next_no = safe_current_no + 1  # 0 + 1 = 1
    
    # exam_feedback.htmlへ渡すデータ
    safe_current_number = max(1, exam_current + 1)  # max(1, 0+1) = 1
    next_question_index = safe_next_no  # 1
    next_question_number = next_question_index + 1 if next_question_index is not None else None  # 1 + 1 = 2
    
    print(f"exam_feedback.html用データ:")
    print(f"  - current_question_number: {safe_current_number} (回答した問題)")
    print(f"  - next_question_index: {next_question_index} (次の問題のインデックス)")
    print(f"  - next_question_number: {next_question_number} (次の問題の表示番号)")
    
    # exam_feedback.htmlでの表示
    next_display_num = next_question_number if next_question_number is not None else safe_current_number + 1
    print(f"\nexam_feedback.html: '次の問題へ ({next_display_num}/{total_questions})'")
    
    # URLパラメータ
    print(f"次へボタンのURL: /exam?next=1&current={next_question_number}")
    print(f"  → これは正しい（次の問題は2番目）")
    
    print("\n" + "="*50 + "\n")
    
    # ケース2: セッション更新後
    print("【ケース2】次の問題へ遷移後")
    exam_current = 1  # セッションが更新された
    
    # exam.htmlでの表示
    current_no_display = exam_current + 1  # 1 + 1 = 2
    print(f"exam.html: 問題 {current_no_display}/{total_questions}")
    print(f"  - exam_current (0ベース): {exam_current}")
    print(f"  - 表示用番号 (1ベース): {current_no_display}")
    
    print("\n【問題の原因】")
    print("1. exam_feedback.htmlで、next_question_numberが次の問題番号として表示される")
    print("2. next_question_numberは (next_question_index + 1) で計算される")
    print("3. next_question_indexは safe_next_no と同じ")
    print("4. safe_next_noは (safe_current_no + 1) で計算される")
    print("5. つまり、最初の問題(index=0)の後では:")
    print("   - safe_current_no = 0")
    print("   - safe_next_no = 1")
    print("   - next_question_index = 1")
    print("   - next_question_number = 2")
    print("   → 「次の問題へ (2/10)」と表示される（正しい）")
    
    print("\n【結論】")
    print("現在のロジックは正しく動作している。")
    print("「次の問題へ (2/10)」は正しい表示である。")
    print("なぜなら、1問目を回答した後、次は2問目に進むため。")

def propose_fix():
    """修正案を提示"""
    print("\n=== 修正案 ===\n")
    
    print("もし「次の問題へ」ボタンに現在の問題番号を表示したい場合:")
    print("（つまり、1問目の回答後に「次の問題へ (1/10)」と表示したい場合）")
    print("\n1. app.pyの修正:")
    print("""
# 現在のコード（4257行目付近）:
'next_question_number': (next_question_index + 1) if next_question_index is not None else None,

# 修正案:
'next_question_number': safe_current_number,  # 現在の問題番号を使用
""")
    
    print("\n2. exam_feedback.htmlの修正:")
    print("""
# 現在のコード（137行目）:
次の問題へ ({{ next_display_num }}/{{ total_num }})

# 修正案A（現在の問題番号を表示）:
次の問題へ ({{ current_question_number }}/{{ total_num }})

# 修正案B（次の問題番号を表示 - 現状維持）:
次の問題へ ({{ next_display_num }}/{{ total_num }})

# 修正案C（進捗を明確に表示）:
次へ進む ({{ current_question_number }}問完了/{{ total_num }}問中)
""")
    
    print("\n【推奨】")
    print("現在の実装は論理的に正しいため、修正は不要と考えられます。")
    print("「次の問題へ (2/10)」は「2問目へ進む」という意味で適切です。")
    
    print("\nもし別の表示方法を希望する場合は、上記の修正案を参考にしてください。")

if __name__ == "__main__":
    analyze_progress_logic()
    propose_fix()