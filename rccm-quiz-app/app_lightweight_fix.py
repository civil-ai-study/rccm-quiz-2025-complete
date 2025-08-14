#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RCCM試験システム - 軽量版（問題混在修正専用）
部門IDシステム実装版 - 1ヶ月の問題解決
"""

from flask import Flask, render_template_string, request, session, redirect, url_for
import csv
import os
import random
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'rccm-lightweight-fix-2025'

# セッション設定の強化（技術者の推奨設定）
app.config['SESSION_COOKIE_SECURE'] = False  # HTTPでもテスト可能
app.config['SESSION_COOKIE_HTTPONLY'] = True  # XSS攻撃対策
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # CSRF攻撃対策
app.config['SESSION_COOKIE_NAME'] = 'rccm_lightweight_session'  # 一意なセッション名
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)  # 1時間有効

@app.before_request
def ensure_session_persistence():
    """セッション永続化の強制確保"""
    if 'quiz_dept_id' in session:
        session.permanent = True
        session.modified = True  # セッションCookieを確実に送信

# 部門IDシステム（日本語URL文字化け回避）- 13部門対応
DEPARTMENT_MAPPING = {
    'basic': '基礎科目（共通）',  # 4-1基礎科目追加
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

def clean_unicode_for_cp932(text):
    """CP932でエンコードできない文字を安全な文字に置換"""
    if not text:
        return text
    
    # よくある問題文字の置換マップ
    replacements = {
        '\u00b2': '²',  # 上付き2
        '\u00b3': '³',  # 上付き3
        '\u00bd': '1/2',  # 1/2分数
        '\u00bc': '1/4',  # 1/4分数
        '\u00be': '3/4',  # 3/4分数
        '\u2013': '-',   # エンダッシュ
        '\u2014': '-',   # エムダッシュ
        '\u2018': "'",   # 左シングルクォート
        '\u2019': "'",   # 右シングルクォート
        '\u201c': '"',   # 左ダブルクォート
        '\u201d': '"',   # 右ダブルクォート
        '\u2026': '...',  # 三点リーダー
    }
    
    cleaned_text = text
    for problematic_char, replacement in replacements.items():
        cleaned_text = cleaned_text.replace(problematic_char, replacement)
    
    # それでもエンコードできない文字があれば削除
    result = ""
    for char in cleaned_text:
        try:
            char.encode('cp932')
            result += char
        except UnicodeEncodeError:
            result += '?'  # 問題文字を?に置換
    
    return result

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
                
                # 各問題データの文字を安全化
                for question in data:
                    for key in ['question', 'option_a', 'option_b', 'option_c', 'option_d', 'explanation']:
                        if key in question and question[key]:
                            question[key] = clean_unicode_for_cp932(question[key])
                
                print(f"OK: {file_path} 読み込み成功 ({encoding}) - {len(data)}問")
                return data
        except Exception as e:
            continue
    
    print(f"ERROR: {file_path} すべてのエンコーディング失敗")
    return []

def get_questions_by_department_id(dept_id):
    """部門IDによる問題取得（13部門対応版）"""
    if dept_id not in DEPARTMENT_MAPPING:
        print(f"ERROR: 無効な部門ID: {dept_id}")
        return []
    
    category = DEPARTMENT_MAPPING[dept_id]
    all_questions = []
    
    # 基礎科目（4-1）の場合
    if dept_id == 'basic':
        file_path = "data/4-1.csv"
        questions = load_csv_safe(file_path)
        
        for question in questions:
            if question.get('category') == '共通':  # 基礎科目は「共通」カテゴリ
                question['year'] = question.get('year', 'basic')
                question['file'] = "4-1.csv"
                all_questions.append(question)
        
        print(f"成功: 基礎科目「{category}」で{len(all_questions)}問取得")
        return all_questions
    
    # 専門科目（4-2）の場合
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
    <title>RCCM軽量版テスト - 問題混在修正</title>
    <meta charset="utf-8">
    <style>
        body { font-family: "MS Gothic", monospace; margin: 20px; }
        .dept { margin: 10px 0; padding: 10px; background: #f0f0f0; }
        .dept a { text-decoration: none; color: #333; }
        .dept:hover { background: #e0e0e0; }
    </style>
</head>
<body>
    <h1>🔧 RCCM軽量版テスト</h1>
    <p><strong>目的</strong>: 13部門（基礎科目+12専門部門）問題混在の修正確認</p>
    
    <h2>📋 13部門完全テスト</h2>
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
    """部門ID指定でクイズ開始"""
    questions = get_questions_by_department_id(dept_id)
    
    if not questions:
        return f"エラー: 部門ID '{dept_id}' の問題が見つかりません", 404
    
    # 10問ランダム選択
    selected_questions = random.sample(questions, min(10, len(questions)))
    
    # Cookieサイズ削減：問題IDのみをセッションに保存（問題データは都度取得）
    question_ids = [q.get('id', f"{q.get('year', 'unknown')}_{q.get('category', 'unknown')}_{i}") for i, q in enumerate(selected_questions)]
    
    # セッション初期化（Cookieサイズ最適化版）
    import time
    session_id = f"{dept_id}_{int(time.time())}"  # 簡単なセッションID生成
    
    session.permanent = True  # 永続セッション有効化
    session['session_id'] = session_id
    session['quiz_dept_id'] = dept_id
    session['quiz_dept_name'] = DEPARTMENT_MAPPING[dept_id]
    session['quiz_question_ids'] = question_ids  # IDのみ保存（大幅軽量化）
    session['quiz_current'] = 0
    session['quiz_answers'] = []
    session.modified = True  # 明示的な変更フラグ設定
    
    # 問題データキャッシュ（メモリ上に保存）
    if not hasattr(start_quiz, '_question_cache'):
        start_quiz._question_cache = {}
    start_quiz._question_cache[session_id] = selected_questions
    
    print(f"DEBUG: セッション初期化完了 - session_id作成")
    # Unicode問題を回避するため、セッション内容の安全出力
    try:
        session_dict = dict(session)
        print(f"DEBUG: 初期セッション内容 = {session_dict}")
    except UnicodeEncodeError:
        print(f"DEBUG: 初期セッション内容 = [Unicode文字含有のため表示省略]")
    
    return show_question()

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    """問題表示・回答処理"""
    if request.method == 'POST':
        # デバッグ: セッション内容確認
        print(f"DEBUG: セッション内容 = {list(session.keys())}")
        print(f"DEBUG: quiz_questions存在? = {'quiz_questions' in session}")
        
        # セッション変数の存在確認（軽量化対応版）
        if 'quiz_question_ids' not in session or 'quiz_current' not in session:
            print(f"ERROR: セッション破損 - quiz_question_ids: {'quiz_question_ids' in session}, quiz_current: {'quiz_current' in session}")
            return "エラー: セッションが無効です。最初からやり直してください。<br><a href='/'>ホームに戻る</a>", 400
        
        answer = request.form.get('answer')
        if answer:
            print(f"DEBUG: 回答受信 = {answer}")
            
            # セッション情報の安全な表示（軽量化対応版）
            session_summary = {
                'quiz_current': session.get('quiz_current', 'MISSING'),
                'quiz_answers_count': len(session.get('quiz_answers', [])),
                'quiz_question_ids_count': len(session.get('quiz_question_ids', [])),
                'quiz_dept_name': session.get('quiz_dept_name', 'MISSING')
            }
            print(f"DEBUG: セッション要約 = {session_summary}")
            
            # セッション更新（改良版）
            try:
                # 回答を記録
                quiz_answers = list(session.get('quiz_answers', []))  # リストのコピー作成
                quiz_answers.append(answer)
                session['quiz_answers'] = quiz_answers
                
                # 現在の問題番号を増加
                current_value = int(session.get('quiz_current', 0))
                session['quiz_current'] = current_value + 1
                
                # セッション永続化設定
                session.permanent = True
                session.modified = True
                
                print(f"SUCCESS: セッション更新完了 - current={session['quiz_current']}, answers={len(session['quiz_answers'])}")
            except Exception as e:
                print(f"ERROR: セッション更新失敗 - {e}")
                return f"エラー: セッション更新に失敗しました。<br>詳細: {e}<br><a href='/'>ホームに戻る</a>", 500
        
        # 10問完了チェック
        current_count = session.get('quiz_current', 0)
        if current_count >= 10:
            print(f"INFO: 10問完了 - 結果画面に遷移")
            return redirect(url_for('result'))
        else:
            print(f"INFO: 次問題表示 - {current_count + 1}/10")
            # セッション保存を強制的に確実にしてから次問題表示
            try:
                # セッション状態を再確認・再設定
                session.permanent = True
                session.modified = True
                print(f"DEBUG: セッション再確認 - current={session.get('quiz_current', 'MISSING')}, answers={len(session.get('quiz_answers', []))}")
                return show_question()
            except Exception as e:
                print(f"ERROR: セッション状態確認失敗 - {e}")
                return f"エラー: セッション状態確認に失敗しました。<br><a href='/'>ホームに戻る</a>", 500
    else:
        return show_question()

def show_question():
    """現在の問題を表示（軽量化対応版）"""
    question_ids = session.get('quiz_question_ids', [])
    current = session.get('quiz_current', 0)
    dept_name = session.get('quiz_dept_name', '')
    dept_id = session.get('quiz_dept_id', '')
    
    if not question_ids:
        return "エラー: セッションが無効です。<br><a href='/'>ホームに戻る</a>", 400
    
    if current >= len(question_ids):
        return redirect(url_for('result'))
    
    # キャッシュから問題データを取得（軽量化方式）
    session_id = session.get('session_id', 'default')
    if hasattr(start_quiz, '_question_cache') and session_id in start_quiz._question_cache:
        questions = start_quiz._question_cache[session_id]
        if current < len(questions):
            question = questions[current]
        else:
            return "エラー: 問題データが見つかりません。<br><a href='/'>ホームに戻る</a>", 400
    else:
        # キャッシュがない場合は部門データから再取得
        print(f"WARNING: キャッシュなし - 部門データから再取得: {dept_id}")
        all_questions = get_questions_by_department_id(dept_id)
        if not all_questions:
            return "エラー: 部門問題データが見つかりません。<br><a href='/'>ホームに戻る</a>", 400
        
        # 最初の問題を表示（フォールバック）
        question = all_questions[0] if current == 0 else all_questions[current % len(all_questions)]
    
    return render_template_string(QUIZ_TEMPLATE,
                                question=question,
                                current=current + 1,
                                department_name=dept_name)

@app.route('/exam')
def exam():
    """基礎科目対応の試験ルート（レガシー互換性用）"""
    question_type = request.args.get('question_type', 'basic')
    
    if question_type == 'basic':
        # 基礎科目は /quiz/basic にリダイレクト
        return redirect(url_for('start_quiz', dept_id='basic'))
    else:
        return "エラー: 軽量版では基礎科目のみサポートしています。レガシールートです。<br><a href='/'>ホームに戻る</a>", 400

@app.route('/result')
def result():
    """結果表示"""
    return f"""
    <h1>テスト完了</h1>
    <p>部門: {session.get('quiz_dept_name', '')}</p>
    <p>回答数: {len(session.get('quiz_answers', []))}/10</p>
    <p><a href="/">ホームに戻る</a></p>
    """

if __name__ == '__main__':
    print("RCCM軽量版テストサーバー起動")
    print("目的: 13部門（基礎科目+12専門部門）問題混在の修正確認")
    print("対応部門: 基礎科目（4-1.csv）+ 12専門部門（4-2_*.csv）")
    app.run(debug=True, host='0.0.0.0', port=5013)