from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_session import Session
import pandas as pd
import os
import random
from datetime import datetime
from collections import defaultdict

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
QUESTIONS_CSV = os.path.join(BASE_DIR, 'data', 'questions.csv')
QUESTIONS_PER_SESSION = 10  # 1回のクイズで出題する問題数

# 問題データの読み込み
def load_questions():
    df = pd.read_csv(QUESTIONS_CSV)
    return df.to_dict(orient='records')

# 学習履歴の初期化
def init_history():
    if 'history' not in session:
        session['history'] = []
    if 'category_stats' not in session:
        session['category_stats'] = {}
    if 'quiz_start_time' not in session:
        session['quiz_start_time'] = None

# AI学習推奨カテゴリの決定
def get_ai_recommendation():
    stats = session.get('category_stats', {})
    # 正答率が最も低いカテゴリを推奨
    min_acc = 1.1
    recommend = None
    for cat, stat in stats.items():
        if stat['total'] > 0:
            acc = stat['correct'] / stat['total']
            if acc < min_acc:
                min_acc = acc
                recommend = cat
    return recommend or '全体'

# ホーム画面
def get_overall_stats():
    history = session.get('history', [])
    if not history:
        return {'total_quizzes': 0, 'total_accuracy': 0.0, 'average_time_per_question': None}
    total = len(history)
    correct = sum(1 for h in history if h['is_correct'])
    total_time = sum(h.get('elapsed', 0) for h in history if h.get('elapsed'))
    avg_time = total_time / total if total > 0 else None
    acc = correct / total * 100 if total > 0 else 0.0
    return {'total_quizzes': total, 'total_accuracy': acc, 'average_time_per_question': round(avg_time, 1) if avg_time else None}

@app.route('/')
def index():
    init_history()
    recommended_category = get_ai_recommendation()
    return render_template('index.html', recommended_category=recommended_category)

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    init_history()
    questions = load_questions()
    if not questions:
        return render_template('error.html', error="問題データが存在しません。CSVファイルを確認してください。")
    category = request.args.get('category')
    prev_category = session.get('quiz_category')
    if category and category != '全体':
        questions = [q for q in questions if q['category'] == category]
    total_questions = len(questions)
    if total_questions == 0:
        return render_template('error.html', error="選択された分野に問題がありません。CSVファイルやカテゴリ名を確認してください。")
    # --- 10問ずつ分割 ---
    if 'quiz_indices' not in session or request.args.get('reset') == '1' or (category != prev_category):
        indices = list(range(total_questions))
        random.shuffle(indices)
        session['quiz_indices'] = indices[:QUESTIONS_PER_SESSION]
        session['quiz_current'] = 0
        session['quiz_category'] = category
        session.modified = True
    indices = session['quiz_indices']
    if not indices:
        return render_template('error.html', error="出題できる問題がありません。CSVファイルやカテゴリ名を確認してください。")
    current_no = session.get('quiz_current', 0)

    # POST処理（解答送信時の進行・履歴保存）
    if request.method == 'POST':
        answer = request.form.get('answer')
        qid = int(request.form.get('qid'))
        question = next(q for q in questions if int(q['id']) == qid)
        is_correct = (answer == question['correct_answer'])
        elapsed = float(request.form.get('elapsed', 0))
        # 履歴保存
        session['history'].append({
            'id': qid,
            'category': question['category'],
            'is_correct': is_correct,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'elapsed': elapsed
        })
        # 分野別統計
        cat_stats = session['category_stats']
        cat = question['category']
        if cat not in cat_stats:
            cat_stats[cat] = {'total': 0, 'correct': 0}
        cat_stats[cat]['total'] += 1
        if is_correct:
            cat_stats[cat]['correct'] += 1
        session.modified = True
        # 次の問題へ
        session['quiz_current'] = current_no + 1
        if session['quiz_current'] >= len(indices):
            return redirect(url_for('result', partial=1))
        else:
            return redirect(url_for('quiz'))

    if current_no >= len(indices):
        return redirect(url_for('result', partial=1))
    idx = indices[current_no]
    question = questions[idx]
    ai_recommend = get_ai_recommendation()
    return render_template('quiz.html', question=question, total_questions=QUESTIONS_PER_SESSION, current_no=current_no+1, ai_recommend=ai_recommend)

@app.route('/result')
def result():
    history = session.get('history', [])
    if not history:
        return redirect(url_for('quiz'))
    correct_count = sum(1 for h in history if h['is_correct'])
    total_questions = len(history)
    elapsed_time = sum(h.get('elapsed', 0) for h in history)
    # 分野別成績
    category_scores = {}
    for h in history:
        cat = h['category']
        if cat not in category_scores:
            category_scores[cat] = {'correct': 0, 'total': 0}
        category_scores[cat]['total'] += 1
        if h['is_correct']:
            category_scores[cat]['correct'] += 1
    # AIフィードバック
    ai_feedback = None
    recommended_category = get_ai_recommendation()
    if recommended_category and recommended_category != '全体':
        ai_feedback = f"分野『{recommended_category}』の正答率が低いため、集中的な学習をおすすめします。"
    partial = request.args.get('partial')
    return render_template('result.html', correct_count=correct_count, total_questions=total_questions, elapsed_time=elapsed_time, category_scores=category_scores, ai_feedback=ai_feedback, recommended_category=recommended_category, partial=partial)

@app.route('/statistics')
def statistics():
    overall_stats = get_overall_stats()
    category_details = {}
    cat_stats = session.get('category_stats', {})
    if not isinstance(cat_stats, dict):
        cat_stats = {}
    for cat, stat in cat_stats.items():
        acc = stat.get('correct', 0) / stat.get('total', 1) * 100 if stat.get('total', 0) > 0 else 0.0
        category_details[cat] = {
            'total_answered': stat.get('total', 0),
            'correct_count': stat.get('correct', 0),
            'accuracy': acc
        }
    quiz_history = session.get('history', [])
    if not isinstance(quiz_history, list):
        quiz_history = []
    quiz_history = quiz_history[-30:]  # 直近30件
    # 日付ごとに正答率を集計
    daily_stats = defaultdict(lambda: {'total': 0, 'correct': 0})
    for q in quiz_history:
        date = q.get('date', '')[:10]  # 'YYYY-MM-DD'形式
        daily_stats[date]['total'] += 1
        if q.get('is_correct'):
            daily_stats[date]['correct'] += 1
    daily_accuracy_list = []
    for date in sorted(daily_stats.keys()):
        total = daily_stats[date]['total']
        correct = daily_stats[date]['correct']
        accuracy = (correct / total * 100) if total > 0 else 0.0
        daily_accuracy_list.append({'date': date, 'accuracy': round(accuracy, 1)})
    return render_template('statistics.html', overall_stats=overall_stats, category_details=category_details, quiz_history=quiz_history, daily_accuracy_list=daily_accuracy_list)

@app.route('/categories')
def categories():
    questions = load_questions()
    cat_stats = session.get('category_stats', {})
    category_details = {}
    for q in questions:
        cat = q['category']
        if cat not in category_details:
            category_details[cat] = {'total_questions': 0, 'total_answered': 0, 'correct_count': 0, 'accuracy': 0.0}
        category_details[cat]['total_questions'] += 1
    for cat, stat in cat_stats.items():
        if cat in category_details:
            category_details[cat]['total_answered'] = stat['total']
            category_details[cat]['correct_count'] = stat['correct']
            category_details[cat]['accuracy'] = stat['correct'] / stat['total'] * 100 if stat['total'] > 0 else 0.0
    # 進捗率
    progresses = {cat: round((detail['total_answered'] / detail['total_questions']) * 100, 1) if detail['total_questions'] > 0 else 0.0 for cat, detail in category_details.items()}
    return render_template('categories.html', category_details=category_details, progresses=progresses)

@app.route('/reset', methods=['GET', 'POST'])
def reset():
    if request.method == 'POST':
        session.clear()
        return redirect(url_for('index'))
    return render_template('reset_confirm.html')

# PWA/バックグラウンド同期用API（例: /api/sync）
@app.route('/api/sync', methods=['POST'])
def api_sync():
    data = request.get_json()
    # ここで受信データをサーバー側DBやファイルに保存する処理を実装可能
    # 今回はセッションに追記
    if data and isinstance(data, list):
        for entry in data:
            session['history'].append(entry)
    session.modified = True
    return jsonify({'status': 'ok'})

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error="ページが見つかりません"), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template('error.html', error="サーバーエラーが発生しました"), 500

if __name__ == '__main__':
    app.run(debug=True) 