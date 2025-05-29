from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import pandas as pd
import os
import random
from datetime import datetime
from collections import defaultdict, Counter
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'rccm-quiz-secret-key-2024-ultra-secure'
app.config['SESSION_COOKIE_NAME'] = 'rccm_session'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = 3600

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
QUESTIONS_CSV = os.path.join(BASE_DIR, 'data', 'questions.csv')
QUESTIONS_PER_SESSION = 10

# 問題データのキャッシュ
_questions_cache = None

def load_questions():
    """問題データの読み込み - 複数エンコーディング対応"""
    global _questions_cache
    
    if _questions_cache is not None:
        return _questions_cache
    
    try:
        if not os.path.exists(QUESTIONS_CSV):
            return get_sample_data()
        
        # 複数のエンコーディングを試行
        encodings = ['utf-8', 'shift_jis', 'cp932', 'utf-8-sig', 'iso-2022-jp']
        df = None
        
        for encoding in encodings:
            try:
                df = pd.read_csv(QUESTIONS_CSV, encoding=encoding)
                break
            except UnicodeDecodeError:
                continue
            except Exception as e:
                continue
        
        if df is None or df.empty:
            return get_sample_data()
        
        # 必要な列の存在確認
        required_columns = ['id', 'category', 'question', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return get_sample_data()
        
        questions = df.to_dict(orient='records')
        
        # データ検証とクリーニング
        valid_questions = []
        for i, q in enumerate(questions):
            try:
                if pd.isna(q.get('id')) or q.get('id') == '':
                    continue
                
                q['id'] = int(float(q['id']))
                
                # 必須フィールドの検証
                if not q.get('question') or not q.get('correct_answer'):
                    continue
                
                # 文字列フィールドの空白除去
                string_fields = ['question', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer', 'explanation', 'reference', 'difficulty', 'keywords', 'practical_tip']
                for field in string_fields:
                    if isinstance(q.get(field), str):
                        q[field] = q[field].strip()
                    elif pd.isna(q.get(field)):
                        q[field] = ''  # NaNを空文字に変換
                
                valid_questions.append(q)
                
            except (ValueError, TypeError) as e:
                continue
        
        if not valid_questions:
            return get_sample_data()
        
        _questions_cache = valid_questions
        return valid_questions
        
    except Exception as e:
        return get_sample_data()

def get_sample_data():
    """拡張されたサンプル問題データ"""
    return [
        {
            'id': 1,
            'category': 'コンクリート',
            'question': '普通ポルトランドセメントの凝結時間に関する記述で最も適切なものはどれか。',
            'option_a': '始発凝結時間は45分以上',
            'option_b': '終結凝結時間は8時間以内',
            'option_c': '始発凝結時間は60分以内',
            'option_d': '終結凝結時間は12時間以内',
            'correct_answer': 'C',
            'explanation': 'JIS R 5210では普通ポルトランドセメントの始発凝結時間は60分以内、終結凝結時間は10時間以内と規定されています。これは現場での打設計画や品質管理において重要な基準値です。',
            'reference': 'JIS R 5210（ポルトランドセメント）',
            'difficulty': '基本',
            'keywords': 'セメント,凝結時間,品質管理',
            'practical_tip': '現場では気温や湿度によって凝結時間が変化するため、季節に応じた施工計画の調整が必要です。'
        },
        {
            'id': 2,
            'category': '土質',
            'question': 'N値と土の相対密度の関係で正しいものはどれか。',
            'option_a': 'N=0-4で相対密度は非常に緩い',
            'option_b': 'N=4-10で相対密度は緩い',
            'option_c': 'N=10-30で相対密度は中程度',
            'option_d': '上記すべて正しい',
            'correct_answer': 'D',
            'explanation': '標準貫入試験のN値による砂質土の相対密度判定基準として、N=0-4（非常に緩い）、N=4-10（緩い）、N=10-30（中程度）、N=30-50（密）、N>50（非常に密）に分類されます。',
            'reference': 'JGS基準・地盤調査法',
            'difficulty': '基本',
            'keywords': 'N値,相対密度,地盤調査,標準貫入試験',
            'practical_tip': '実際の現場では、N値だけでなく土質や地下水の状況も総合的に判断することが重要です。'
        },
        {
            'id': 3,
            'category': '河川',
            'question': '河川砂防技術基準における計画高水流量の設定に関して正しいものはどれか。',
            'option_a': '30年確率の洪水流量を基準とする',
            'option_b': '50年確率の洪水流量を基準とする',
            'option_c': '100年確率の洪水流量を基準とする',
            'option_d': '200年確率の洪水流量を基準とする',
            'correct_answer': 'C',
            'explanation': '河川砂防技術基準では、計画高水流量は原則として100年確率（1/100）の洪水流量を基準として設定されます。ただし、河川の重要度や流域特性により200年確率を採用する場合もあります。',
            'reference': '河川砂防技術基準（計画編）',
            'difficulty': '標準',
            'keywords': '確率流量,計画高水,治水計画',
            'practical_tip': '東日本大震災後、想定を超える災害への対応として、設計外力を超える洪水への対策も重要視されています。'
        }
    ]

def analyze_recent_performance(history, question_count=10):
    """直近の学習パフォーマンスを分析"""
    if not history:
        return None
    
    recent = history[-question_count:] if len(history) >= question_count else history
    
    total = len(recent)
    correct = sum(1 for h in recent if h.get('is_correct', False))
    accuracy = (correct / total * 100) if total > 0 else 0
    
    # カテゴリ別分析
    category_stats = {}
    weak_categories = []
    
    for h in recent:
        cat = h.get('category', '不明')
        if cat not in category_stats:
            category_stats[cat] = {'total': 0, 'correct': 0, 'wrong_ids': []}
        
        category_stats[cat]['total'] += 1
        if h.get('is_correct'):
            category_stats[cat]['correct'] += 1
        else:
            category_stats[cat]['wrong_ids'].append(h.get('id'))
    
    # 苦手分野の特定（正答率60%未満）
    for cat, stats in category_stats.items():
        if stats['total'] >= 2:  # 最低2問以上解答している分野
            cat_accuracy = (stats['correct'] / stats['total']) * 100
            if cat_accuracy < 60:
                weak_categories.append({
                    'category': cat,
                    'accuracy': cat_accuracy,
                    'wrong_count': stats['total'] - stats['correct']
                })
    
    return {
        'total_questions': total,
        'correct_answers': correct,
        'accuracy': accuracy,
        'category_stats': category_stats,
        'weak_categories': weak_categories
    }

def generate_recommendations(analysis):
    """学習推奨を生成"""
    if not analysis:
        return []
    
    recommendations = []
    accuracy = analysis.get('accuracy', 0)
    
    if accuracy < 50:
        recommendations.append({
            'type': 'foundation',
            'message': '基礎知識の強化が必要です。各分野の基本概念から復習しましょう。',
            'action': 'categories'
        })
    elif accuracy < 70:
        recommendations.append({
            'type': 'improvement',
            'message': '理解は進んでいます。苦手分野を集中的に学習しましょう。',
            'action': 'weak_focus'
        })
    else:
        recommendations.append({
            'type': 'excellent',
            'message': '良好な成績です！継続学習で更なる向上を目指しましょう。',
            'action': 'continue'
        })
    
    # 苦手分野の推奨
    weak_categories = analysis.get('weak_categories', [])
    if weak_categories:
        top_weak = weak_categories[0]
        recommendations.append({
            'type': 'weakness',
            'message': f'「{top_weak["category"]}」分野の正答率が{top_weak["accuracy"]:.1f}%です。重点的な復習をお勧めします。',
            'action': f'category_{top_weak["category"]}'
        })
    
    return recommendations[:3]  # 最大3つまで

@app.before_request
def before_request():
    """リクエスト前の処理"""
    session.permanent = True

@app.route('/')
def index():
    """ホーム画面 - 既存デザインを維持"""
    if 'history' not in session:
        session['history'] = []
    if 'category_stats' not in session:
        session['category_stats'] = {}
    
    session.modified = True
    
    # 最近の学習分析
    analysis = analyze_recent_performance(session.get('history', []))
    recommended_category = '全体'
    
    if analysis and analysis.get('weak_categories'):
        recommended_category = analysis['weak_categories'][0]['category']
    
    return render_template('index.html', 
                         analysis=analysis,
                         recommended_category=recommended_category)

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    """問題画面 - 既存の実装を基本的に維持しつつフィードバック強化"""
    all_questions = load_questions()
    if not all_questions:
        return render_template('error.html', error="問題データが存在しません。")
    
    # POST処理（回答送信） - フィードバック用データを拡張
    if request.method == 'POST':
        answer = request.form.get('answer')
        qid = request.form.get('qid')
        elapsed = request.form.get('elapsed', '0')
        
        if not answer or not qid:
            return render_template('error.html', error="回答データが不完全です。")
        
        try:
            qid = int(qid)
        except ValueError:
            return render_template('error.html', error="問題IDが無効です。")
        
        # 問題を検索
        question = next((q for q in all_questions if int(q.get('id', 0)) == qid), None)
        if not question:
            return render_template('error.html', error=f"問題が見つかりません (ID: {qid})。")
        
        # 正誤判定
        is_correct = (str(answer).strip() == str(question.get('correct_answer', '').strip()))
        
        # 履歴に追加（フィードバック用に情報を拡張）
        if 'history' not in session:
            session['history'] = []
        
        # 拡張された履歴データ
        history_item = {
            'id': qid,
            'category': question.get('category', '不明'),
            'is_correct': is_correct,
            'user_answer': answer,
            'correct_answer': question.get('correct_answer', ''),
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'elapsed': float(elapsed)
        }
        
        # フィードバック用の詳細情報（必要時のみ保存）
        if not is_correct:
            history_item.update({
                'question_text': question.get('question', ''),
                'options': {
                    'A': question.get('option_a', ''),
                    'B': question.get('option_b', ''),
                    'C': question.get('option_c', ''),
                    'D': question.get('option_d', '')
                },
                'explanation': question.get('explanation', ''),
                'reference': question.get('reference', ''),
                'practical_tip': question.get('practical_tip', '')
            })
        
        session['history'].append(history_item)
        
        # カテゴリ統計更新
        if 'category_stats' not in session:
            session['category_stats'] = {}
        
        cat = question.get('category', '不明')
        if cat not in session['category_stats']:
            session['category_stats'][cat] = {'total': 0, 'correct': 0}
        
        session['category_stats'][cat]['total'] += 1
        if is_correct:
            session['category_stats'][cat]['correct'] += 1
        
        # 現在の問題番号を取得して更新
        current_no = session.get('quiz_current', 0)
        quiz_question_ids = session.get('quiz_question_ids', [])
        
        # 次の問題番号を設定
        next_no = current_no + 1
        session['quiz_current'] = next_no
        session.modified = True
        
        # 問題終了判定
        if next_no >= len(quiz_question_ids):
            return redirect(url_for('result'))
        else:
            category = session.get('quiz_category', '全体')
            return redirect(url_for('quiz', category=category))
    
    # GET処理（問題表示） - 既存の実装を維持
    requested_category = request.args.get('category', '全体')
    
    # カテゴリでフィルタリング
    if requested_category != '全体':
        filtered_questions = [q for q in all_questions if q.get('category') == requested_category]
    else:
        filtered_questions = all_questions
    
    if not filtered_questions:
        return render_template('error.html', error=f"カテゴリ「{requested_category}」に問題がありません。")
    
    # セッション情報取得
    quiz_question_ids = session.get('quiz_question_ids', [])
    current_no = session.get('quiz_current', 0)
    session_category = session.get('quiz_category', '全体')
    
    # セッション初期化判定
    need_reset = False
    
    if not quiz_question_ids or request.args.get('reset') == '1' or requested_category != session_category or current_no >= len(quiz_question_ids):
        need_reset = True
    
    # 新しい問題セッション開始
    if need_reset:
        question_ids = [int(q.get('id', 0)) for q in filtered_questions if q.get('id') is not None]
        random.shuffle(question_ids)
        
        session['quiz_question_ids'] = question_ids[:QUESTIONS_PER_SESSION]
        session['quiz_current'] = 0
        session['quiz_category'] = requested_category
        session.modified = True
        
        quiz_question_ids = session['quiz_question_ids']
        current_no = 0
    
    # 範囲チェック
    if current_no >= len(quiz_question_ids):
        return redirect(url_for('result'))
    
    # 現在の問題を取得
    current_question_id = quiz_question_ids[current_no]
    question = next((q for q in all_questions if int(q.get('id', 0)) == current_question_id), None)
    
    if not question:
        return render_template('error.html', error="問題データの取得に失敗しました。")
    
    return render_template(
        'quiz.html',
        question=question,
        total_questions=len(quiz_question_ids),
        current_no=current_no + 1
    )

@app.route('/result')
def result():
    """結果画面 - 既存デザインを維持しつつフィードバック機能を強化"""
    history = session.get('history', [])
    if not history:
        return redirect(url_for('quiz'))
    
    quiz_question_ids = session.get('quiz_question_ids', [])
    session_size = len(quiz_question_ids) if quiz_question_ids else QUESTIONS_PER_SESSION
    
    # 今回のセッションの問題のみを抽出
    recent_history = history[-session_size:] if len(history) >= session_size else history
    
    # 基本統計
    correct_count = sum(1 for h in recent_history if h['is_correct'])
    total_questions = len(recent_history)
    elapsed_time = sum(h.get('elapsed', 0) for h in recent_history)
    
    # カテゴリ別成績
    category_scores = {}
    for h in recent_history:
        cat = h.get('category', '不明')
        if cat not in category_scores:
            category_scores[cat] = {'correct': 0, 'total': 0}
        category_scores[cat]['total'] += 1
        if h.get('is_correct'):
            category_scores[cat]['correct'] += 1
    
    # 学習分析と推奨
    analysis = analyze_recent_performance(history)
    recommendations = generate_recommendations(analysis)
    
    # 間違い問題の詳細（フィードバック強化）
    wrong_questions = []
    for h in recent_history:
        if not h.get('is_correct') and h.get('question_text'):
            wrong_questions.append({
                'id': h.get('id'),
                'category': h.get('category'),
                'question': h.get('question_text'),
                'user_answer': h.get('user_answer'),
                'correct_answer': h.get('correct_answer'),
                'options': h.get('options', {}),
                'explanation': h.get('explanation', ''),
                'reference': h.get('reference', ''),
                'practical_tip': h.get('practical_tip', '')
            })
    
    # 推奨カテゴリ
    recommended_category = '全体'
    if analysis and analysis.get('weak_categories'):
        recommended_category = analysis['weak_categories'][0]['category']
    
    return render_template(
        'result.html',
        correct_count=correct_count,
        total_questions=total_questions,
        elapsed_time=elapsed_time,
        category_scores=category_scores,
        recommended_category=recommended_category,
        analysis=analysis,
        recommendations=recommendations,
        wrong_questions=wrong_questions
    )

@app.route('/statistics')
def statistics():
    """統計画面 - 既存の実装を維持"""
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
    """カテゴリ画面 - 既存の実装を維持"""
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
    """リセット画面 - 既存の実装を維持しつつ確認画面を改善"""
    if request.method == 'POST':
        session.clear()
        return redirect(url_for('index'))
    
    # 現在のデータ分析
    history = session.get('history', [])
    analytics = {
        'total_questions': len(history),
        'accuracy': 0
    }
    
    if history:
        correct = sum(1 for h in history if h.get('is_correct'))
        analytics['accuracy'] = round((correct / len(history)) * 100, 1)
    
    return render_template('reset_confirm.html', analytics=analytics)

@app.route('/help')
def help_page():
    """ヘルプページ - 機能説明を更新"""
    return render_template('help.html', total_questions=QUESTIONS_PER_SESSION)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error="ページが見つかりません"), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template('error.html', error="サーバーエラーが発生しました"), 500

# 初期化
initial_questions = load_questions()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 