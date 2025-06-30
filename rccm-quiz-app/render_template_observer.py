#!/usr/bin/env python3
"""
🔍 render_template変数渡し観察 - 専門家推奨手法
Flask専門家推奨：既存機能肯定→render_template呼び出し確認→安全修正
"""

import sys
import os
import subprocess
import time
import re

# Add the current directory to Python path
sys.path.insert(0, '/mnt/c/Users/z285/Desktop/rccm-quiz-app/rccm-quiz-app')

def analyze_render_template_calls():
    """render_template呼び出しの観察分析"""
    print("🔍 render_template変数渡し観察開始")
    print("専門家推奨：既存機能肯定→呼び出し確認→安全修正")
    print("=" * 70)
    
    # app.pyからrender_template呼び出しを抽出
    app_file = "/mnt/c/Users/z285/Desktop/rccm-quiz-app/rccm-quiz-app/app.py"
    
    try:
        with open(app_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print("✅ app.py読み込み成功")
        
        # render_template('exam.html'の呼び出しを検索
        print(f"\n📋 render_template('exam.html'呼び出し検索")
        
        # パターン1: exam.html呼び出し
        exam_pattern = r"render_template\(\s*['\"]exam\.html['\"][^)]*\)"
        exam_calls = re.findall(exam_pattern, content, re.MULTILINE | re.DOTALL)
        
        if exam_calls:
            print(f"  🔍 exam.html呼び出し発見数: {len(exam_calls)}")
            for i, call in enumerate(exam_calls, 1):
                print(f"  {i}. {call[:100]}...")
        else:
            print(f"  ⚠️ exam.html呼び出しなし")
        
        # パターン2: 行番号付きで詳細検索
        lines = content.split('\n')
        exam_lines = []
        
        for line_no, line in enumerate(lines, 1):
            if "render_template" in line and "exam.html" in line:
                exam_lines.append((line_no, line.strip()))
        
        if exam_lines:
            print(f"\n📊 exam.html render_template詳細:")
            for line_no, line in exam_lines:
                print(f"  行{line_no}: {line}")
                
                # 前後の行も確認（変数設定確認）
                start_line = max(0, line_no - 10)
                end_line = min(len(lines), line_no + 5)
                
                print(f"    前後コンテキスト:")
                for ctx_line_no in range(start_line, end_line):
                    if ctx_line_no == line_no - 1:
                        marker = ">>> "
                    else:
                        marker = "    "
                    ctx_line = lines[ctx_line_no].strip()
                    if ctx_line:
                        print(f"    {marker}{ctx_line_no+1}: {ctx_line}")
                print(f"")
        
        # パターン3: current_no, total_questionsの設定箇所確認
        print(f"\n🔍 progress変数設定箇所確認")
        
        progress_keywords = ['current_no', 'total_questions', 'display_current', 'display_total']
        progress_lines = []
        
        for keyword in progress_keywords:
            for line_no, line in enumerate(lines, 1):
                if keyword in line and ('=' in line or keyword + ':' in line):
                    progress_lines.append((line_no, keyword, line.strip()))
        
        if progress_lines:
            print(f"  📝 進捗変数設定箇所({len(progress_lines)}箇所):")
            for line_no, keyword, line in progress_lines[-10:]:  # 最新10箇所
                print(f"    行{line_no}({keyword}): {line}")
        else:
            print(f"  ⚠️ 進捗変数設定箇所なし")
        
        # パターン4: template_vars辞書の確認
        print(f"\n🔍 template_vars辞書設定確認")
        
        template_vars_pattern = r"template_vars\s*=\s*\{[^}]*\}"
        template_vars_matches = re.findall(template_vars_pattern, content, re.MULTILINE | re.DOTALL)
        
        if template_vars_matches:
            print(f"  📊 template_vars設定発見({len(template_vars_matches)}箇所):")
            for i, match in enumerate(template_vars_matches, 1):
                # 改行を整理して表示
                clean_match = re.sub(r'\s+', ' ', match)
                print(f"    {i}. {clean_match[:150]}...")
        else:
            print(f"  ⚠️ template_vars設定なし")
        
        # パターン5: **template_vars使用箇所確認
        print(f"\n🔍 **template_vars使用箇所確認")
        
        for line_no, line in enumerate(lines, 1):
            if "**template_vars" in line and "render_template" in line:
                print(f"  行{line_no}: {line.strip()}")
                
                # この行の前後でtemplate_varsがどう設定されているか確認
                context_start = max(0, line_no - 20)
                context_end = min(len(lines), line_no)
                
                print(f"    template_vars設定コンテキスト:")
                for ctx_line_no in range(context_start, context_end):
                    ctx_line = lines[ctx_line_no].strip()
                    if 'template_vars' in ctx_line or 'current_no' in ctx_line or 'total_questions' in ctx_line:
                        print(f"      {ctx_line_no+1}: {ctx_line}")
                print("")
    
    except Exception as e:
        print(f"❌ ファイル分析エラー: {e}")
    
    print(f"\n" + "=" * 70)
    print("✅ render_template変数渡し観察完了")
    print("\n📊 観察結果:")
    print("  - 既存機能維持: コード変更なし")
    print("  - Flask専門家手法: render_template呼び出し分析")
    print("  - 次ステップ: 特定された問題箇所の安全修正")

if __name__ == "__main__":
    analyze_render_template_calls()