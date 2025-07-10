#!/usr/bin/env python3
"""
進捗表示の修正案2: 完了した問題数を表示
"""

def show_fix():
    print("=== 修正案2: 完了した問題数を表示 ===\n")
    
    print("【修正内容】")
    print("「次の問題へ (2/10)」→「次へ進む (1問完了/10問中)」")
    
    print("\n【必要な修正】")
    print("\n1. exam_feedback.htmlの修正（137行目付近）:")
    print("""
# 現在のコード:
<a href="/exam?next=1&current={{ next_display_number }}" 
   class="btn btn-primary btn-lg px-5 py-3 main-nav-btn"
   ...>
    <i class="fas fa-arrow-right me-2"></i>次の問題へ ({{ next_display_num }}/{{ total_num }})
</a>

# 修正後:
<a href="/exam?next=1&current={{ next_display_number }}" 
   class="btn btn-primary btn-lg px-5 py-3 main-nav-btn"
   ...>
    <i class="fas fa-arrow-right me-2"></i>次へ進む ({{ current_question_number }}問完了/{{ total_num }}問中)
</a>
""")
    
    print("\n【メリット】")
    print("- 完了した問題数が明確に分かる")
    print("- 進捗状況がより直感的")
    
    print("\n【デメリット】")
    print("- 文字数が増える")
    print("- モバイル画面で表示が長くなる可能性")

if __name__ == "__main__":
    show_fix()