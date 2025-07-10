#!/usr/bin/env python3
"""
進捗表示の修正案3: シンプルな表示
"""

def show_fix():
    print("=== 修正案3: シンプルな表示 ===\n")
    
    print("【修正内容】")
    print("「次の問題へ (2/10)」→「次の問題へ」")
    print("進捗はページ上部のバッジでのみ表示")
    
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
    <i class="fas fa-arrow-right me-2"></i>次の問題へ
</a>
""")
    
    print("\n【メリット】")
    print("- シンプルで分かりやすい")
    print("- モバイル画面でも表示が崩れない")
    print("- 進捗はページ上部で既に表示されているため重複を避ける")
    
    print("\n【デメリット】")
    print("- ボタンから直接進捗が分からない")

if __name__ == "__main__":
    show_fix()