#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修正版テストサーバー - 部門別問題抽出確認用
"""

from flask import Flask, render_template_string, request
import os
import csv
import urllib.parse

app = Flask(__name__)
app.secret_key = 'test-key'

# 13部門定義
DEPARTMENTS = [
    '共通', '道路', '河川・砂防', '都市計画', '造園',
    '建設環境', '鋼構造・コンクリート', '土質・基礎', '施工計画',
    '上水道', '森林土木', '農業土木', 'トンネル'
]

@app.route('/')
def index():
    """メインページ"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>修正版テスト - 部門別問題抽出確認</title>
        <meta charset="utf-8">
    </head>
    <body>
        <h1>修正版テスト - 部門別問題抽出確認</h1>
        <h2>13部門リスト</h2>
        <ul>
        {% for dept in departments %}
            <li><a href="/quiz/{{ dept }}">{{ dept }}</a></li>
        {% endfor %}
        </ul>
    </body>
    </html>
    """
    return render_template_string(html, departments=DEPARTMENTS)

@app.route('/quiz/<department>')
def quiz(department):
    """部門別クイズページ"""
    # URLデコード処理
    try:
        department = urllib.parse.unquote(department, encoding='utf-8')
    except:
        pass
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>{{ department }}部門テスト</title>
        <meta charset="utf-8">
    </head>
    <body>
        <h1>{{ department }}部門</h1>
        <p>部門: {{ department }}</p>
        <p>全年度から部門別問題抽出テスト:</p>
        <pre>{{ question_info }}</pre>
        <a href="/">戻る</a>
    </body>
    </html>
    """
    
    # 全年度4-2ファイルから部門別問題抽出
    question_info = []
    data_dir = "rccm-quiz-app/data"
    
    try:
        department_questions = []
        if os.path.exists(data_dir):
            csv_files = [f for f in os.listdir(data_dir) if f.startswith('4-2_') and f.endswith('.csv')]
            question_info.append(f"検索対象ファイル数: {len(csv_files)}")
            
            for csv_file in csv_files:
                file_path = os.path.join(data_dir, csv_file)
                file_count = 0
                all_categories = set()
                with open(file_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        all_categories.add(row['category'])
                        if row['category'] == department:
                            department_questions.append({
                                'file': csv_file,
                                'question': row['question']
                            })
                            file_count += 1
                
                # デバッグ情報追加
                if csv_file == '4-2_2019.csv':
                    question_info.append(f"[DEBUG] {csv_file}のカテゴリー一覧:")
                    for cat in sorted(all_categories):
                        question_info.append(f"  - '{cat}' (len={len(cat)})")
                    question_info.append(f"[DEBUG] 検索部門: '{department}' (len={len(department)})")
                
                if file_count > 0:
                    question_info.append(f"{csv_file}: {file_count}問")
            
            question_info.append(f"\n選択部門: {department}")
            question_info.append(f"部門名バイト: {department.encode('utf-8')}")
            question_info.append(f"総該当問題数: {len(department_questions)}")
            
            if department_questions:
                question_info.append("\n最初の5問:")
                for i, q in enumerate(department_questions[:5]):
                    question_info.append(f"{i+1}. [{q['file']}] {q['question'][:60]}...")
            else:
                question_info.append("⚠️ この部門の問題が見つかりません")
        else:
            question_info.append("データディレクトリが見つかりません")
                
    except Exception as e:
        question_info.append(f"エラー: {e}")
    
    question_info_text = "\n".join(question_info)
    
    return render_template_string(html, department=department, question_info=question_info_text)

if __name__ == '__main__':
    print("修正版テストサーバー起動中...")
    print("URL: http://127.0.0.1:5011")
    app.run(host='0.0.0.0', port=5011, debug=True)