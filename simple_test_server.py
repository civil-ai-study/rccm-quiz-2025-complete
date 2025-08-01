#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
シンプルテストサーバー - 専門分野分離確認用
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
        <title>軽量版テスト - 専門分野分離確認</title>
        <meta charset="utf-8">
    </head>
    <body>
        <h1>軽量版テスト - 専門分野分離確認</h1>
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
        <p>部門別問題抽出テスト:</p>
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
        csv_files = [f for f in os.listdir(data_dir) if f.startswith('4-2_') and f.endswith('.csv')]
        
        for csv_file in csv_files:
            file_path = os.path.join(data_dir, csv_file)
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['category'] == department:
                        department_questions.append(f"{csv_file}: {row['question'][:30]}...")
            
            question_info.append(f"選択部門: {department}")
            question_info.append(f"該当問題数: {len(department_questions)}")
            
            if department_questions:
                question_info.append("\n最初の3問:")
                for i, q in enumerate(department_questions[:3]):
                    question_info.append(f"{i+1}. {q['question'][:50]}...")
            else:
                question_info.append("⚠️ この部門の問題が見つかりません")
                
        except Exception as e:
            question_info.append(f"エラー: {e}")
    else:
        question_info.append("データファイルが見つかりません")
    
    question_info_text = "\n".join(question_info)
    
    return render_template_string(html, department=department, question_info=question_info_text)

if __name__ == '__main__':
    print("シンプルテストサーバー起動中...")
    print("URL: http://127.0.0.1:5010")
    app.run(host='0.0.0.0', port=5010, debug=True)