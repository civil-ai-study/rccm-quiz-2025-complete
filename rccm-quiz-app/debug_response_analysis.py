#!/usr/bin/env python3
"""
本番環境レスポンス詳細分析
問題数0の根本原因特定
"""

import subprocess
import re

def analyze_response():
    """レスポンス詳細分析"""
    
    # 道路部門のレスポンスを取得
    cmd = [
        'curl', '-s', '-c', '/tmp/debug_analysis.txt',
        '-H', 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'https://rccm-quiz-2025.onrender.com/department_study/road'
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=False)
    
    try:
        response = result.stdout.decode('utf-8', errors='replace')
    except:
        response = str(result.stdout)
    
    print("=" * 60)
    print("本番環境レスポンス詳細分析")
    print("=" * 60)
    
    # 問題数表示部分を抽出
    h3_sections = re.findall(r'<div class="h3[^"]*"[^>]*>([^<]+)</div>', response)
    print(f"h3セクション抽出: {h3_sections}")
    
    # specialist_stats 関連を検索
    specialist_matches = re.findall(r'specialist_stats\.[^}]+', response)
    print(f"specialist_stats参照: {specialist_matches}")
    
    # エラーメッセージ周辺を抽出
    error_context = re.findall(r'.{0,100}この部門の専門問題はまだ利用できません.{0,100}', response, re.DOTALL)
    if error_context:
        print(f"エラー表示コンテキスト:")
        for ctx in error_context:
            print(f"  {repr(ctx)}")
    
    # Jinjaテンプレート変数の確認
    template_vars = re.findall(r'\{\{\s*([^}]+)\s*\}\}', response)
    print(f"Jinjaテンプレート変数: {template_vars}")
    
    # JavaScriptエラーの確認
    js_errors = re.findall(r'error|Error|ERROR', response)
    print(f"エラー関連テキスト件数: {len(js_errors)}")
    
    # レスポンスサイズと構造
    print(f"レスポンスサイズ: {len(response)}バイト")
    print(f"HTMLタグ数: {len(re.findall(r'<[^>]+>', response))}")
    
    # specialist_stats.total_questions が 0 になっている原因を特定
    if 'specialist_stats.total_questions' in response:
        context = re.findall(r'.{0,200}specialist_stats\.total_questions.{0,200}', response, re.DOTALL)
        print(f"specialist_stats.total_questions コンテキスト:")
        for ctx in context:
            print(f"  {repr(ctx)}")
    
    return response

if __name__ == '__main__':
    analyze_response()