#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第三者レビュー: RCCM Quiz App 実用最小版
元コードから核心機能のみを抽出した動作可能バージョン
"""

import os
import csv
import random
import json
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, jsonify

# 基本設定
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'rccm-quiz-secret-key-2025')

# データディレクトリ
DATA_DIR = 'data'

def load_questions():
    """問題データ読み込み（簡略版）"""
    questions = []
    
    # 基礎科目（4-1.csv）
    try:
        csv_path = os.path.join(DATA_DIR, '4-1.csv')
        if os.path.exists(csv_path):
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    questions.append({
                        'id': row.get('id', ''),
                        'question': row.get('question', ''),
                        'option_a': row.get('option_a', ''),
                        'option_b': row.get('option_b', ''),
                        'option_c': row.get('option_c', ''),
                        'option_d': row.get('option_d', ''),
                        'correct_answer': row.get('correct_answer', ''),
                        'explanation': row.get('explanation', ''),
                        'department': '基礎科目',
                        'year': '2024'
                    })
    except Exception as e:
        print(f"データ読み込みエラー: {e}")
    
    # サンプルデータ（ファイルが無い場合）
    if not questions:
        questions = [
            {
                'id': '1',
                'question': 'RCCMとは何の略称ですか？',
                'option_a': '登録建設機械施工技術者',
                'option_b': '登録土木コンサルティング技師',
                'option_c': '登録建設コンサルタント管理技術者',
                'option_d': '登録建設機械管理技術者',
                'correct_answer': 'a',
                'explanation': 'RCCMは「登録建設機械施工技術者」の略称です。',
                'department': '基礎科目',
                'year': '2024'
            },
            {
                'id': '2', 
                'question': '建設機械の安全点検で最も重要なことは？',
                'option_a': '作業前点検',
                'option_b': '作業後点検',
                'option_c': '定期点検',
                'option_d': '日常点検',
                'correct_answer': 'd',
                'explanation': '建設機械の安全確保には日常点検が最も重要です。',
                'department': '基礎科目',
                'year': '2024'
            }
        ]
    
    return questions

@app.route('/')
def index():
    """ホーム画面"""
    return '''
    <html>
    <head><title>RCCM Quiz App</title></head>
    <body>
        <h1>RCCM試験問題集</h1>
        <p>実用最小版（第三者レビュー対応）</p>
        <form action="/start_exam" method="post">
            <label>部門：
                <select name="department">
                    <option value="基礎科目">基礎科目</option>
                    <option value="道路">道路</option>
                    <option value="河川・砂防">河川・砂防</option>
                </select>
            </label><br><br>
            <label>問題数：
                <select name="questions">
                    <option value="2">2問（テスト）</option>
                    <option value="10">10問</option>
                    <option value="20">20問</option>
                </select>
            </label><br><br>
            <button type="submit">試験開始</button>
        </form>
    </body>
    </html>
    '''

@app.route('/start_exam', methods=['POST'])
def start_exam():
    """試験開始"""
    department = request.form.get('department', '基礎科目')
    num_questions = int(request.form.get('questions', 2))
    
    # 問題読み込み
    all_questions = load_questions()
    
    # ランダム選択
    selected_questions = random.sample(all_questions, min(num_questions, len(all_questions)))
    
    # セッション初期化
    session['questions'] = selected_questions
    session['current'] = 0
    session['answers'] = {}
    session['department'] = department
    
    return redirect(url_for('exam'))

@app.route('/exam')
def exam():
    """問題表示"""
    current = session.get('current', 0)
    questions = session.get('questions', [])
    
    if current >= len(questions):
        return redirect(url_for('result'))
    
    question = questions[current]
    
    return f'''
    <html>
    <head><title>問題 {current + 1}</title></head>
    <body>
        <h2>問題 {current + 1} / {len(questions)}</h2>
        <div>
            <p><strong>{question['question']}</strong></p>
            <form action="/answer" method="post">
                <input type="radio" name="answer" value="a" id="a">
                <label for="a">A. {question['option_a']}</label><br>
                <input type="radio" name="answer" value="b" id="b">
                <label for="b">B. {question['option_b']}</label><br>
                <input type="radio" name="answer" value="c" id="c">
                <label for="c">C. {question['option_c']}</label><br>
                <input type="radio" name="answer" value="d" id="d">
                <label for="d">D. {question['option_d']}</label><br><br>
                <button type="submit">回答</button>
            </form>
        </div>
    </body>
    </html>
    '''

@app.route('/answer', methods=['POST'])
def answer():
    """回答処理"""
    current = session.get('current', 0)
    answer = request.form.get('answer')
    
    if 'answers' not in session:
        session['answers'] = {}
    
    # ウルトラシンク: 副作用を防ぐ安全なセッション更新
    answers = session.get('answers', {})
    answers[str(current)] = answer
    session['answers'] = answers
    
    # 次の問題へ進む（安全に更新）
    session['current'] = current + 1
    session.modified = True
    
    print(f"Debug: Current={current}, Answer={answer}, Next={current+1}")  # デバッグ用
    
    return redirect(url_for('exam'))

@app.route('/result')
def result():
    """結果表示"""
    questions = session.get('questions', [])
    answers = session.get('answers', {})
    department = session.get('department', '基礎科目')
    
    correct_count = 0
    results = []
    
    for i, question in enumerate(questions):
        user_answer = answers.get(str(i), '')
        correct_answer = question['correct_answer']
        is_correct = user_answer.lower() == correct_answer.lower()
        
        if is_correct:
            correct_count += 1
        
        results.append({
            'question': question['question'],
            'user_answer': user_answer,
            'correct_answer': correct_answer,
            'is_correct': is_correct,
            'explanation': question['explanation']
        })
    
    score = (correct_count / len(questions)) * 100 if questions else 0
    
    html = f'''
    <html>
    <head><title>試験結果</title></head>
    <body>
        <h1>試験結果</h1>
        <h2>{department}</h2>
        <p><strong>得点: {correct_count}/{len(questions)} ({score:.1f}%)</strong></p>
        
        <h3>詳細結果</h3>
    '''
    
    for i, result in enumerate(results):
        status = "✅ 正解" if result['is_correct'] else "❌ 不正解"
        html += f'''
        <div style="border: 1px solid #ccc; margin: 10px; padding: 10px;">
            <h4>問題 {i + 1} - {status}</h4>
            <p><strong>問題:</strong> {result['question']}</p>
            <p><strong>あなたの回答:</strong> {result['user_answer'].upper()}</p>
            <p><strong>正解:</strong> {result['correct_answer'].upper()}</p>
            <p><strong>解説:</strong> {result['explanation']}</p>
        </div>
        '''
    
    html += '''
        <p><a href="/">ホームに戻る</a></p>
    </body>
    </html>
    '''
    
    return html

@app.route('/health')
def health():
    """ヘルスチェック"""
    return "OK"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5007))
    app.run(host='0.0.0.0', port=port, debug=True, threaded=True)