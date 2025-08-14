#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RCCM試験システム - ULTRATHIN軽量版（Cookie size limit解決版）
技術者推奨のセッション軽量化実装
"""

from flask import Flask, render_template_string, request, session, redirect, url_for
import csv
import os
import random
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'rccm-ultrathin-cookie-fix-2025'

# セッション設定の強化（技術者の推奨設定）
app.config['SESSION_COOKIE_SECURE'] = False  # HTTPでもテスト可能
app.config['SESSION_COOKIE_HTTPONLY'] = True  # XSS攻撃対策
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # CSRF攻撃対策
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)  # 1時間有効

# 部門IDシステム（日本語URL文字化け回避）
DEPARTMENT_MAPPING = {
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

# 確実に存在する年度リスト
AVAILABLE_YEARS = [2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019]

# サーバーサイド問題キャッシュ（Cookie size limit回避）
questions_cache = {}

def load_csv_safe(file_path):
    """安全なCSV読み込み（pandas不使用版）"""
    if not os.path.exists(file_path):
        print(f"ERROR: ファイルが存在しません: {file_path}")
        return []
    
    encodings_to_try = ['utf-8', 'utf-8-sig', 'cp932', 'shift_jis']
    
    for encoding in encodings_to_try:
        try:
            with open(file_path, 'r', encoding=encoding, newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                data = list(reader)
                print(f"OK: {file_path} 読み込み成功 ({encoding}) - {len(data)}問")
                return data
        except Exception as e:
            continue
    
    print(f"ERROR: {file_path} すべてのエンコーディング失敗")
    return []

def get_questions_by_department_id(dept_id):
    """部門IDによる問題取得（確実版）"""
    if dept_id not in DEPARTMENT_MAPPING:
        print(f"ERROR: 無効な部門ID: {dept_id}")
        return []
    
    category = DEPARTMENT_MAPPING[dept_id]
    all_questions = []
    
    # 全年度の4-2ファイルから該当部門問題を収集
    for year in AVAILABLE_YEARS:
        file_path = f"data/4-2_{year}.csv"
        questions = load_csv_safe(file_path)
        
        for question in questions:
            if question.get('category') == category:
                question['year'] = year
                question['file'] = f"4-2_{year}.csv"
                all_questions.append(question)
    
    print(f"成功: 部門'{category}'で{len(all_questions)}問取得")
    return all_questions

# 簡単なHTMLテンプレート
HOME_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>RCCM ULTRATHIN軽量版 - Cookie Size Fix</title>
    <meta charset="utf-8">
    <style>
        body { font-family: "MS Gothic", monospace; margin: 20px; }
        .dept { margin: 10px 0; padding: 10px; background: #f0f0f0; }
        .dept a { text-decoration: none; color: #333; }
        .dept:hover { background: #e0e0e0; }
    </style>
</head>
<body>
    <h1>🔧 RCCM ULTRATHIN軽量版テスト</h1>
    <p><strong>目的</strong>: Cookie size limit解決 + セッション管理修正</p>
    
    <h2>📋 12専門部門テスト</h2>
    {% for dept_id, dept_name in departments.items() %}
    <div class="dept">
        <a href="/quiz/{{ dept_id }}">{{ dept_name }} (ID: {{ dept_id }})</a>
    </div>
    {% endfor %}
    
    <hr>
    <p><small>作成時刻: {{ timestamp }}</small></p>
</body>
</html>
'''

QUIZ_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>{{ department_name }} - 問題{{ current }}/10</title>
    <meta charset="utf-8">
    <style>
        body { font-family: "MS Gothic", monospace; margin: 20px; }
        .question { background: #f9f9f9; padding: 15px; margin: 10px 0; }
        .options { margin: 10px 0; }
        .option { margin: 5px 0; }
    </style>
</head>
<body>
    <h1>{{ department_name }}</h1>
    <p>問題 {{ current }}/10</p>
    
    <div class="question">
        <h3>{{ question.question }}</h3>
    </div>
    
    <form method="POST" action="/quiz">
        <div class="options">
            <div class="option">
                <input type="radio" name="answer" value="A" id="a">
                <label for="a">A. {{ question.option_a }}</label>
            </div>
            <div class="option">
                <input type="radio" name="answer" value="B" id="b">
                <label for="b">B. {{ question.option_b }}</label>
            </div>
            <div class="option">
                <input type="radio" name="answer" value="C" id="c">
                <label for="c">C. {{ question.option_c }}</label>
            </div>
            <div class="option">
                <input type="radio" name="answer" value="D" id="d">
                <label for="d">D. {{ question.option_d }}</label>
            </div>
        </div>
        <button type="submit">回答する</button>
    </form>
    
    <hr>
    <p><small>
        出典: {{ question.file }} ({{ question.year }}年)<br>
        カテゴリ: {{ question.category }}
    </small></p>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HOME_TEMPLATE,
                                departments=DEPARTMENT_MAPPING,
                                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

@app.route('/quiz/<dept_id>')
def start_quiz(dept_id):
    """部門ID指定でクイズ開始（ULTRATHIN Cookie size fix版）"""
    questions = get_questions_by_department_id(dept_id)
    
    if not questions:
        return f"エラー: 部門ID '{dept_id}' の問題が見つかりません", 404
    
    # 10問ランダム選択
    selected_questions = random.sample(questions, min(10, len(questions)))
    
    # Cookie size limit回避：軽量セッション初期化
    session.permanent = True
    session['quiz_dept_id'] = dept_id
    session['quiz_dept_name'] = DEPARTMENT_MAPPING[dept_id]
    session['quiz_current'] = 0
    session['quiz_answers'] = []
    
    # 問題データはサーバーサイドキャッシュに保存
    cache_key = f"{dept_id}_{int(datetime.now().timestamp())}"
    questions_cache[cache_key] = selected_questions
    session['cache_key'] = cache_key
    
    session.modified = True
    
    print(f"DEBUG: ULTRATHIN セッション初期化完了")
    print(f"DEBUG: Cache key: {cache_key}")
    print(f"DEBUG: セッションサイズ: {len(str(dict(session)))} bytes")
    
    return show_question()

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    """問題表示・回答処理（ULTRATHIN版）"""
    if request.method == 'POST':
        # セッション変数の存在確認
        if 'cache_key' not in session:
            return "エラー: セッションが無効です。最初からやり直してください。<br><a href='/'>ホームに戻る</a>", 400
        
        answer = request.form.get('answer')
        if answer:
            print(f"DEBUG: 回答受信 = {answer}")
            print(f"DEBUG: 修正前セッション = {dict(session)}")
            
            # 技術者推奨の確実な初期化チェック + セッション更新
            if 'quiz_answers' not in session:
                session['quiz_answers'] = []
            if 'quiz_current' not in session:
                session['quiz_current'] = 0
                
            # 確実な更新（技術者推奨パターン）
            quiz_answers = session['quiz_answers']
            quiz_answers.append(answer)
            session['quiz_answers'] = quiz_answers  # 再代入で確実に更新
            
            # カウンター更新（技術者推奨パターン）
            session['quiz_current'] += 1  # 直接インクリメント
            
            session.permanent = True
            session.modified = True
            
            print(f"DEBUG: 修正後セッション = {dict(session)}")
            print(f"DEBUG: quiz_current更新: {session['quiz_current']}")
        
        if session['quiz_current'] >= 10:
            return redirect(url_for('result'))
        else:
            return show_question()
    else:
        return show_question()

def show_question():
    """現在の問題を表示（ULTRATHIN版 - Cache失効対応）"""
    cache_key = session.get('cache_key')
    current = session.get('quiz_current', 0)
    dept_name = session.get('quiz_dept_name', '')
    dept_id = session.get('quiz_dept_id', '')
    
    # 技術者推奨：Cache失効時の自動回復
    if not cache_key or cache_key not in questions_cache:
        print(f"DEBUG: Cache miss detected - Rebuilding for dept_id: {dept_id}")
        if dept_id:
            # Cache失効時は同じ部門の問題を再取得
            questions = get_questions_by_department_id(dept_id)
            selected_questions = random.sample(questions, min(10, len(questions)))
            
            # 新しいCache key生成
            new_cache_key = f"{dept_id}_{int(datetime.now().timestamp())}"
            questions_cache[new_cache_key] = selected_questions
            session['cache_key'] = new_cache_key
            session.modified = True
            
            print(f"DEBUG: Cache rebuilt with key: {new_cache_key}")
        else:
            return "エラー: セッションが無効です。<br><a href='/'>ホームに戻る</a>", 400
    
    questions = questions_cache[session['cache_key']]
    
    if current >= len(questions):
        return redirect(url_for('result'))
    
    question = questions[current]
    
    return render_template_string(QUIZ_TEMPLATE,
                                question=question,
                                current=current + 1,
                                department_name=dept_name)

@app.route('/result')
def result():
    """結果表示"""
    return f"""
    <h1>テスト完了（ULTRATHIN版）</h1>
    <p>部門: {session.get('quiz_dept_name', '')}</p>
    <p>回答数: {len(session.get('quiz_answers', []))}/10</p>
    <p><a href="/">ホームに戻る</a></p>
    """

if __name__ == '__main__':
    print("RCCM ULTRATHIN軽量版テストサーバー起動")
    print("目的: Cookie size limit解決 + セッション管理修正")
    app.run(debug=True, host='0.0.0.0', port=5014)