from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import pandas as pd
import os
import random
from datetime import datetime
from collections import defaultdict

app = Flask(__name__)
app.config['SECRET_KEY'] = 'rccm-quiz-secret-key-2024'
app.config['SESSION_COOKIE_NAME'] = 'rccm_session'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = 3600

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
QUESTIONS_CSV = os.path.join(BASE_DIR, 'data', 'questions.csv')
QUESTIONS_PER_SESSION = 10

# 問題データのキャッシュ
_questions_cache = None

def load_questions():
    """問題データの読み込み"""
    global _questions_cache
    
    if _questions_cache is not None:
        return _questions_cache
    
    try:
        if not os.path.exists(QUESTIONS_CSV):
            print(f"CSVファイルが見つかりません: {QUESTIONS_CSV}")
            return []
        
        df = pd.read_csv(QUESTIONS_CSV)
        if df.empty:
            return []
        
        questions = df.to_dict(orient='records')
        _questions_cache = questions
        print(f"問題データ読み込み完了: {len(questions)}問")
        return questions
        
    except Exception as e:
        print(f"エラー: {str(e)}")
        return []

# 起動時に問題データを読み込む
print("アプリケーション起動中...")
initial_questions = load_questions()
print(f"初期読み込み: {len(initial_questions)}問")

@app.route('/')
def index():
    # セッション永続化の確認
    session.permanent = True
    
    # 初期化
    if 'history' not in session:
        session['history'] = []
    if 'category_stats' not in session:
        session['category_stats'] = {}
    
    # AI推奨カテゴリ
    stats = session.get('category_stats', {})
    recommended_category = '全体'
    min_acc = 1.0
    
    for cat, stat in stats.items():
        if stat.get('total', 0) > 0:
            acc = stat['correct'] / stat['total']
            if acc < min_acc:
                min_acc = acc
                recommended_category = cat
    
    return render_template('index.html', recommended_category=recommended_category)

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    # セッション永続化
    session.permanent = True
    
    # デバッグ情報
    print(f"\n=== /quiz アクセス (method={request.method}) ===")
    print(f"セッション内容: quiz_current={session.get('quiz_current')}, "
          f"quiz_question_ids={len(session.get('quiz_question_ids', []))}個")
    
    # 問題データ読み込み
    all_questions = load_questions()
    if not all_questions:
        return render_template('error.html', error="問題データが存在しません。")
    
    # POST処理（回答送信）を先に処理
    if request.method == 'POST':
        print("POST処理開始")
        
        # フォームデータ取得
        answer = request.form.get('answer')
        qid = request.form.get('qid')
        
        if not answer or not qid:
            return render_template('error.html', error="回答データが不完全です。")
        
        # 問題を検索
        question = next((q for q in all_questions if str(q.get('id')) == str(qid)), None)
        if not question:
            return render_template('error.html', error=f"問題が見つかりません (ID: {qid})。")
        
        # 正誤判定
        is_correct = (str(answer) == str(question.get('correct_answer')))
        
        # 履歴に追加
        if 'history' not in session:
            session['history'] = []
        
        session['history'].append({
            'id': qid,
            'category': question.get('category', '不明'),
            'is_correct': is_correct,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'elapsed': float(request.form.get('elapsed', 0))
        })
        
        # カテゴリ統計更新
        if 'category_stats' not in session:
            session['category_stats'] = {}
        
        cat = question.get('category', '不明')
        if cat not in session['category_stats']:
            session['category_stats'][cat] = {'total': 0, 'correct': 0}
        
        session['category_stats'][cat]['total'] += 1
        if is_correct:
            session['category_stats'][cat]['correct'] += 1
        
        # 現在の問題番号を取得して次へ進める
        current_no = session.get('quiz_current', 0)
        quiz_question_ids = session.get('quiz_question_ids', [])
        
        # 次の問題番号を設定
        next_no = current_no + 1
        session['quiz_current'] = next_no
        
        # 重要: modified フラグを設定
        session.modified = True
        
        print(f"現在: {current_no} → 次: {next_no} (全{len(quiz_question_ids)}問)")
        
        # クイズ終了判定
        if next_no >= len(quiz_question_ids):
            print("クイズ終了 → 結果画面へ")
            return redirect(url_for('result'))
        else:
            # 次の問題へ（カテゴリ情報を保持）
            category = session.get('quiz_category', '全体')
            print(f"次の問題へ → カテゴリ: {category}")
            return redirect(url_for('quiz', category=category))
    
    # GET処理（問題表示）
    print("GET処理開始")
    
    # カテゴリ取得
    requested_category = request.args.get('category', '全体')
    
    # カテゴリでフィルタリング
    if requested_category != '全体':
        filtered_questions = [q for q in all_questions if q.get('category') == requested_category]
    else:
        filtered_questions = all_questions
    
    if not filtered_questions:
        return render_template('error.html', error=f"カテゴリ「{requested_category}」に問題がありません。")
    
    # 現在のクイズセッション情報を取得
    quiz_question_ids = session.get('quiz_question_ids', [])
    current_no = session.get('quiz_current', 0)
    session_category = session.get('quiz_category', '全体')
    
    # クイズセッションの初期化が必要か判定
    need_reset = False
    
    if not quiz_question_ids:
        need_reset = True
        print("リセット理由: 問題リストが空")
    elif request.args.get('reset') == '1':
        need_reset = True
        print("リセット理由: リセット要求")
    elif requested_category != session_category:
        need_reset = True
        print(f"リセット理由: カテゴリ変更 ({session_category} → {requested_category})")
    elif current_no >= len(quiz_question_ids):
        need_reset = True
        print(f"リセット理由: 範囲外 ({current_no} >= {len(quiz_question_ids)})")
    
    # 新しいクイズセッションを開始
    if need_reset:
        print("新しいクイズセッションを開始")
        
        # ランダムに問題を選択
        question_ids = [str(q.get('id')) for q in filtered_questions if q.get('id') is not None]
        random.shuffle(question_ids)
        
        # セッションに保存
        session['quiz_question_ids'] = question_ids[:QUESTIONS_PER_SESSION]
        session['quiz_current'] = 0
        session['quiz_category'] = requested_category
        session.modified = True
        
        # 更新された値を使用
        quiz_question_ids = session['quiz_question_ids']
        current_no = 0
        
        print(f"新セッション: {len(quiz_question_ids)}問を出題")
    
    # 範囲チェック
    if current_no >= len(quiz_question_ids):
        print(f"エラー: 範囲外 (current={current_no}, total={len(quiz_question_ids)})")
        return redirect(url_for('result'))
    
    # 現在の問題を取得
    current_question_id = quiz_question_ids[current_no]
    question = next((q for q in all_questions if str(q.get('id')) == str(current_question_id)), None)
    
    if not question:
        return render_template('error.html', error="問題データの取得に失敗しました。")
    
    print(f"表示: 問題{current_no + 1}/{len(quiz_question_ids)} (ID={question.get('id')})")
    
    # テンプレートに渡すデータ
    return render_template(
        'quiz.html',
        question=question,
        total_questions=len(quiz_question_ids),
        current_no=current_no + 1  # 表示用は1始まり
    )

@app.route('/result')
def result():
    history = session.get('history', [])
    if not history:
        return redirect(url_for('quiz'))
    
    # 最新のセッション分の結果を計算
    quiz_question_ids = session.get('quiz_question_ids', [])
    session_size = len(quiz_question_ids) if quiz_question_ids else QUESTIONS_PER_SESSION
    
    # 最新のセッション分の履歴を取得
    recent_history = history[-session_size:] if len(history) >= session_size else history
    
    correct_count = sum(1 for h in recent_history if h['is_correct'])
    total_questions = len(recent_history)
    elapsed_time = sum(h.get('elapsed', 0) for h in recent_history)
    
    # 分野別成績
    category_scores = {}
    for h in recent_history:
        cat = h.get('category', '不明')
        if cat not in category_scores:
            category_scores[cat] = {'correct': 0, 'total': 0}
        category_scores[cat]['total'] += 1
        if h.get('is_correct'):
            category_scores[cat]['correct'] += 1
    
    # AI推奨
    ai_feedback = None
    stats = session.get('category_stats', {})
    min_acc = 1.0
    weak_category = None
    
    for cat, stat in stats.items():
        if stat.get('total', 0) > 0:
            acc = stat['correct'] / stat['total']
            if acc < min_acc:
                min_acc = acc
                weak_category = cat
    
    if weak_category and weak_category != '全体':
        ai_feedback = f"分野『{weak_category}』の正答率が低いため、集中的な学習をおすすめします。"
    
    return render_template(
        'result.html',
        correct_count=correct_count,
        total_questions=total_questions,
        elapsed_time=elapsed_time,
        category_scores=category_scores,
        ai_feedback=ai_feedback,
        recommended_category=weak_category
    )

@app.route('/statistics')
def statistics():
    history = session.get('history', [])
    
    # 全体統計
    overall_stats = {
        'total_quizzes': len(history),
        'total_accuracy': 0.0,
        'average_time_per_question': None
    }
    
    if history:
        total = len(history)
        correct = sum(1 for h in history if h['is_correct'])
        total_time = sum(h.get('elapsed', 0) for h in history)
        overall_stats['total_accuracy'] = correct / total * 100 if total > 0 else 0.0
        overall_stats['average_time_per_question'] = round(total_time / total, 1) if total > 0 else None
    
    # カテゴリ別詳細
    category_details = {}
    cat_stats = session.get('category_stats', {})
    
    for cat, stat in cat_stats.items():
        total = stat.get('total', 0)
        correct = stat.get('correct', 0)
        category_details[cat] = {
            'total_answered': total,
            'correct_count': correct,
            'accuracy': (correct / total * 100) if total > 0 else 0.0
        }
    
    # 最近の履歴
    quiz_history = history[-30:] if history else []
    
    # 日付別統計
    daily_stats = defaultdict(lambda: {'total': 0, 'correct': 0})
    for h in history:
        date = h.get('date', '')[:10]
        if date:
            daily_stats[date]['total'] += 1
            if h.get('is_correct'):
                daily_stats[date]['correct'] += 1
    
    daily_accuracy_list = []
    for date in sorted(daily_stats.keys()):
        total = daily_stats[date]['total']
        correct = daily_stats[date]['correct']
        accuracy = (correct / total * 100) if total > 0 else 0.0
        daily_accuracy_list.append({'date': date, 'accuracy': round(accuracy, 1)})
    
    return render_template(
        'statistics.html',
        overall_stats=overall_stats,
        category_details=category_details,
        quiz_history=quiz_history,
        daily_accuracy_list=daily_accuracy_list
    )

@app.route('/categories')
def categories():
    questions = load_questions()
    cat_stats = session.get('category_stats', {})
    
    # カテゴリ情報を集計
    category_details = {}
    for q in questions:
        cat = q.get('category')
        if cat:
            if cat not in category_details:
                category_details[cat] = {
                    'total_questions': 0,
                    'total_answered': 0,
                    'correct_count': 0,
                    'accuracy': 0.0
                }
            category_details[cat]['total_questions'] += 1
    
    # 統計情報を追加
    for cat, stat in cat_stats.items():
        if cat in category_details:
            total = stat.get('total', 0)
            correct = stat.get('correct', 0)
            category_details[cat]['total_answered'] = total
            category_details[cat]['correct_count'] = correct
            category_details[cat]['accuracy'] = (correct / total * 100) if total > 0 else 0.0
    
    # 進捗率計算
    progresses = {}
    for cat, detail in category_details.items():
        total_q = detail.get('total_questions', 0)
        answered = detail.get('total_answered', 0)
        progresses[cat] = round((answered / total_q) * 100, 1) if total_q > 0 else 0.0
    
    return render_template(
        'categories.html',
        category_details=category_details,
        progresses=progresses
    )

@app.route('/reset', methods=['GET', 'POST'])
def reset():
    if request.method == 'POST':
        session.clear()
        return redirect(url_for('index'))
    return render_template('reset_confirm.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error="ページが見つかりません"), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template('error.html', error="サーバーエラーが発生しました"), 500

if __name__ == '__main__':
    print("=" * 50)
    print("RCCM試験問題集アプリを起動します")
    print(f"URL: http://localhost:5000")
    print("=" * 50)
    app.run(debug=True) 