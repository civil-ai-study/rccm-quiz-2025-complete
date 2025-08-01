#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
動作確認版テストサーバー - 部門ID使用
"""

from flask import Flask, render_template_string, request
import os
import csv
import random

app = Flask(__name__)
app.secret_key = 'test-key'

# 部門ID→日本語名マッピング
DEPARTMENT_MAP = {
    'basic': '共通',
    'road': '道路', 
    'river': '河川、砂防及び海岸・海洋',
    'urban': '都市計画及び地方計画',
    'garden': '造園',
    'env': '建設環境',
    'steel': '鋼構造及びコンクリート',
    'soil': '土質及び基礎',
    'construction': '施工計画、施工設備及び積算',
    'water': '上水道及び工業用水道',
    'forest': '森林土木',
    'agri': '農業土木',
    'tunnel': 'トンネル'
}

@app.route('/')
def index():
    """メインページ"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>動作確認版 - 部門別問題抽出</title>
        <meta charset="utf-8">
    </head>
    <body>
        <h1>動作確認版 - 部門別問題抽出</h1>
        <h2>13部門リスト</h2>
        <ul>
        {% for dept_id, dept_name in departments.items() %}
            <li><a href="/quiz/{{ dept_id }}">{{ dept_name }}</a> (ID: {{ dept_id }})</li>
        {% endfor %}
        </ul>
    </body>
    </html>
    """
    return render_template_string(html, departments=DEPARTMENT_MAP)

@app.route('/quiz/<dept_id>')
def quiz(dept_id):
    """部門別クイズページ"""
    if dept_id not in DEPARTMENT_MAP:
        return "無効な部門IDです", 400
    
    department_name = DEPARTMENT_MAP[dept_id]
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>{{ department_name }}部門 - 問題抽出テスト</title>
        <meta charset="utf-8">
    </head>
    <body>
        <h1>{{ department_name }}部門</h1>
        <p>部門ID: {{ dept_id }}</p>
        <p>部門名: {{ department_name }}</p>
        <div>{{ result_info | safe }}</div>
        <a href="/">戻る</a>
    </body>
    </html>
    """
    
    # 部門別問題抽出実行
    result_info = extract_department_questions(department_name)
    
    return render_template_string(html, 
                                dept_id=dept_id, 
                                department_name=department_name,
                                result_info=result_info)

def extract_department_questions(department_name):
    """部門別問題抽出処理"""
    data_dir = "rccm-quiz-app/data"
    result = []
    
    try:
        if not os.path.exists(data_dir):
            return "<p>❌ データディレクトリが見つかりません</p>"
        
        csv_files = [f for f in os.listdir(data_dir) if f.startswith('4-2_') and f.endswith('.csv')]
        all_questions = []
        
        result.append(f"<h3>抽出結果</h3>")
        result.append(f"<p>対象ファイル数: {len(csv_files)}</p>")
        
        for csv_file in csv_files:
            file_path = os.path.join(data_dir, csv_file)
            file_questions = []
            
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['category'] == department_name:
                        file_questions.append(row)
            
            if file_questions:
                all_questions.extend(file_questions)
                result.append(f"<p>{csv_file}: {len(file_questions)}問</p>")
        
        result.append(f"<h4>総問題数: {len(all_questions)}問</h4>")
        
        if all_questions:
            # ランダムで5問表示
            sample_questions = random.sample(all_questions, min(5, len(all_questions)))
            result.append("<h4>サンプル問題 (ランダム5問):</h4>")
            result.append("<ol>")
            for i, q in enumerate(sample_questions):
                year = q.get('year', '不明')
                question_text = q['question'][:100] + "..." if len(q['question']) > 100 else q['question']
                result.append(f"<li>[{year}年] {question_text}</li>")
            result.append("</ol>")
            
            result.append("<p>✅ 部門別問題抽出成功！</p>")
        else:
            result.append("<p>❌ この部門の問題が見つかりませんでした</p>")
            
    except Exception as e:
        result.append(f"<p>❌ エラー: {e}</p>")
    
    return "".join(result)

if __name__ == '__main__':
    print("動作確認版テストサーバー起動中...")
    print("URL: http://127.0.0.1:5012")
    app.run(host='0.0.0.0', port=5012, debug=True)