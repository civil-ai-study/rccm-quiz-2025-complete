from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import os
import random
from datetime import datetime, timedelta
from collections import defaultdict
import logging

# 新しいファイルからインポート
from config import Config, QuizConfig, SRSConfig, DataConfig
from utils import load_questions_improved, DataLoadError, DataValidationError, get_sample_data_improved
from data_manager import DataManager, SessionDataManager

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('rccm_app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Flask アプリケーション初期化
app = Flask(__name__)

# 設定適用（改善版）
app.config.from_object(Config)

# データ管理初期化
data_manager = DataManager()
session_data_manager = SessionDataManager(data_manager)

# 問題データのキャッシュ
_questions_cache = None
_cache_timestamp = None

def load_questions():
    """
    問題データの読み込み（改善版統合）
    キャッシュ機能と詳細エラーハンドリング
    """
    global _questions_cache, _cache_timestamp
    
    current_time = datetime.now()
    
    # キャッシュが有効かチェック
    if (_questions_cache is not None and 
        _cache_timestamp is not None and 
        (current_time - _cache_timestamp).seconds < DataConfig.CACHE_TIMEOUT):
        logger.debug("キャッシュからデータを返却")
        return _questions_cache
    
    logger.info("問題データの読み込み開始")
    
    try:
        # 改善版データ読み込み
        questions = load_questions_improved(DataConfig.QUESTIONS_CSV)
        _questions_cache = questions
        _cache_timestamp = current_time
        logger.info(f"問題データ読み込み完了: {len(questions)}問")
        return questions
        
    except FileNotFoundError:
        logger.warning("CSVファイルが見つからないため、サンプルデータを使用")
        questions = get_sample_data_improved()
        _questions_cache = questions
        _cache_timestamp = current_time
        return questions
        
    except (DataLoadError, DataValidationError) as e:
        logger.error(f"データ読み込みエラー: {e}")
        logger.warning("サンプルデータを使用")
        questions = get_sample_data_improved()
        _questions_cache = questions
        _cache_timestamp = current_time
        return questions
        
    except Exception as e:
        logger.error(f"予期しないエラー: {e}")
        logger.warning("サンプルデータを使用")
        questions = get_sample_data_improved()
        _questions_cache = questions
        _cache_timestamp = current_time
        return questions

def clear_questions_cache():
    """問題データキャッシュのクリア"""
    global _questions_cache, _cache_timestamp
    _questions_cache = None
    _cache_timestamp = None
    logger.info("問題データキャッシュをクリア")

def update_srs_data(question_id, is_correct, user_session):
    """間隔反復学習データの更新（設定統合版）"""
    if 'srs_data' not in user_session:
        user_session['srs_data'] = {}
    
    srs_data = user_session['srs_data']
    today = datetime.now().date()
    
    if str(question_id) not in srs_data:
        srs_data[str(question_id)] = {
            'level': 0,
            'last_review': today.isoformat(),
            'next_review': today.isoformat(),
            'correct_count': 0,
            'total_attempts': 0
        }
    
    question_data = srs_data[str(question_id)]
    question_data['total_attempts'] += 1
    question_data['last_review'] = today.isoformat()
    
    if is_correct:
        question_data['correct_count'] += 1
        question_data['level'] = min(question_data['level'] + 1, 5)
    else:
        question_data['level'] = max(question_data['level'] - 1, 0)
    
    # 設定から間隔を取得
    interval_days = SRSConfig.INTERVALS[question_data['level']]
    next_review_date = today + timedelta(days=interval_days)
    question_data['next_review'] = next_review_date.isoformat()
    
    user_session['srs_data'] = srs_data
    return question_data

def get_due_questions(user_session, all_questions):
    """復習が必要な問題を取得"""
    if 'srs_data' not in user_session:
        return []
    
    srs_data = user_session['srs_data']
    today = datetime.now().date()
    due_questions = []
    
    for question_id, data in srs_data.items():
        try:
            next_review = datetime.fromisoformat(data['next_review']).date()
            if next_review <= today:
                question = next((q for q in all_questions if str(q.get('id', 0)) == question_id), None)
                if question:
                    due_questions.append({
                        'question': question,
                        'srs_data': data,
                        'days_overdue': (today - next_review).days
                    })
        except (ValueError, KeyError) as e:
            logger.warning(f"SRSデータ解析エラー (ID: {question_id}): {e}")
            continue
    
    due_questions.sort(key=lambda x: x['days_overdue'], reverse=True)
    return due_questions

def get_mixed_questions(user_session, all_questions, requested_category='全体', session_size=None):
    """新問題と復習問題をミックスした出題（設定統合版）"""
    if session_size is None:
        session_size = QuizConfig.QUESTIONS_PER_SESSION
    
    due_questions = get_due_questions(user_session, all_questions)
    
    # 設定から復習問題の比率を取得
    max_review_count = min(len(due_questions), 
                          int(session_size * SRSConfig.MAX_REVIEW_RATIO))
    selected_questions = []
    
    # 復習問題を追加
    for i in range(max_review_count):
        selected_questions.append(due_questions[i]['question'])
    
    # 残りを新問題で埋める
    remaining_count = session_size - len(selected_questions)
    
    if requested_category != '全体':
        available_questions = [q for q in all_questions if q.get('category') == requested_category]
    else:
        available_questions = all_questions
    
    # 既に選択済みの問題を除外
    selected_ids = [int(q.get('id', 0)) for q in selected_questions]
    new_questions = [q for q in available_questions if int(q.get('id', 0)) not in selected_ids]
    
    random.shuffle(new_questions)
    selected_questions.extend(new_questions[:remaining_count])
    
    random.shuffle(selected_questions)
    logger.info(f"問題選択完了: 復習{max_review_count}問, 新規{remaining_count}問")
    
    return selected_questions

@app.before_request
def before_request():
    """リクエスト前の処理（改善版）"""
    session.permanent = True
    
    # セッションIDの取得
    session_id = session.get('session_id')
    if not session_id:
        session['session_id'] = os.urandom(16).hex()
        session_id = session['session_id']
    
    # 初回アクセス時にデータを復元
    if 'data_loaded' not in session:
        session_data_manager.load_session_data(session, session_id)
        session['data_loaded'] = True

@app.after_request
def after_request(response):
    """リクエスト後の処理（自動保存）"""
    session_id = session.get('session_id')
    if session_id and session.get('history'):
        # 自動保存のトリガー
        session_data_manager.auto_save_trigger(session, session_id)
    
    return response

@app.route('/')
def index():
    """ホーム画面"""
    if 'history' not in session:
        session['history'] = []
    if 'category_stats' not in session:
        session['category_stats'] = {}
    
    session.modified = True
    return render_template('index.html')

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    """SRS対応のquiz関数（統合版）"""
    try:
        all_questions = load_questions()
        if not all_questions:
            logger.error("問題データが空")
            return render_template('error.html', error="問題データが存在しません。")

        # POST処理（回答送信）
        if request.method == 'POST':
            answer = request.form.get('answer')
            qid = request.form.get('qid')
            elapsed = request.form.get('elapsed', '0')

            if not answer or not qid:
                logger.warning("不完全な回答データ")
                return render_template('error.html', error="回答データが不完全です。ですが、ここではエラー画面ではなく、問題一覧に戻るか、最初に戻るか、アプリを終了するかを聞く画面に飛ばすべき）")

            try:
                qid = int(qid)
            except ValueError:
                logger.error(f"無効な問題ID: {qid}")
                return render_template('error.html', error="問題IDが無効です。")

            # 問題を検索
            question = next((q for q in all_questions if int(q.get('id', 0)) == qid), None)
            if not question:
                logger.error(f"問題が見つからない: ID {qid}")
                return render_template('error.html', error=f"問題が見つかりません (ID: {qid})。")

            # 正誤判定
            is_correct = (str(answer).strip() == str(question.get('correct_answer', '').strip()))

            # SRSデータを更新
            srs_info = update_srs_data(qid, is_correct, session)

            # 履歴に追加
            if 'history' not in session:
                session['history'] = []

            history_item = {
                'id': qid,
                'category': question.get('category', '不明'),
                'is_correct': is_correct,
                'user_answer': answer,
                'correct_answer': question.get('correct_answer', ''),
                'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'elapsed': float(elapsed),
                'srs_level': srs_info['level'],
                'is_review': srs_info['total_attempts'] > 1
            }

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

            # セッション進行管理
            current_no = session.get('quiz_current', 0)
            quiz_question_ids = session.get('quiz_question_ids', [])

            next_no = current_no + 1
            session['quiz_current'] = next_no
            session.modified = True

            logger.info(f"回答処理完了: 問題{qid}, 正答{is_correct}, レベル{srs_info['level']}")

            # 次の問題の準備
            next_question_index = current_no + 1
            is_last_question = next_question_index >= len(quiz_question_ids)

            # *** Add this line: Update session for the next question ***
            session['quiz_current'] = next_no
            session['quiz_category'] = question.get('category', '全体')
            session['quiz_question_ids'] = quiz_question_ids
            session['current_question_index'] = next_question_index
            session['quiz_session'] = session.get('quiz_session', {})
            session['quiz_session']['current_question_index'] = next_question_index
            session['quiz_session']['total_questions'] = len(quiz_question_ids)
            session['quiz_session']['current_question_number'] = current_no + 1
            session.modified = True

            # フィードバック画面に渡すデータを準備
            feedback_data = {
                'question': question,
                'user_answer': answer,
                'is_correct': is_correct,
                'is_last_question': is_last_question,
                'next_question_index': next_question_index,
                'total_questions': len(quiz_question_ids),
                'current_question_number': current_no + 1,
                'category': session.get('quiz_category', '全体'),
                'srs_info': srs_info,
                'is_review_question': srs_info['total_attempts'] > 1,
                'user_answer_text': question.get(f'option_{answer.lower()}', '不明な回答'),
                'correct_answer_text': question.get(f'option_{question.get("correct_answer", "").lower()}', '不明な正解')
            }

            return render_template('quiz_feedback.html', **feedback_data)

        # GET処理（問題表示）
        requested_category = request.args.get('category', '全体')
        session_size = request.args.get('size', QuizConfig.QUESTIONS_PER_SESSION)
        specific_qid = request.args.get('qid')

        try:
            session_size = int(session_size)
        except (ValueError, TypeError):
            session_size = QuizConfig.QUESTIONS_PER_SESSION

        # セッション管理
        quiz_question_ids = session.get('quiz_question_ids', [])
        current_no = session.get('quiz_current', 0)
        session_category = session.get('quiz_category', '全体')

        # ★追加: 特定の問題表示の場合
        if specific_qid:
            try:
                specific_qid = int(specific_qid)
                question = next((q for q in all_questions if int(q.get('id', 0)) == specific_qid), None)
                if not question:
                    logger.error(f"指定された問題が見つからない: ID {specific_qid}")
                    return render_template('error.html', error=f"指定された問題が見つかりません (ID: {specific_qid})。")

                # この問題を単独セッションとして設定
                session['quiz_question_ids'] = [specific_qid]
                session['quiz_current'] = 0
                session['quiz_category'] = question.get('category', '全体')
                session.modified = True

                # SRS情報を取得
                srs_data = session.get('srs_data', {})
                question_srs = srs_data.get(str(specific_qid), {})

                return render_template(
                    'quiz.html',
                    question=question,
                    total_questions=1,
                    current_no=1,
                    srs_info=question_srs,
                    is_review_question=question_srs.get('total_attempts', 0) > 0
                )

            except ValueError:
                logger.error(f"無効な問題IDが指定されました: {specific_qid}")
                return render_template('error.html', error="無効な問題IDが指定されました。")

        # セッション初期化判定 (qid指定がない場合)
        need_reset = (not quiz_question_ids or
                    request.args.get('reset') == '1' or
                    requested_category != session_category or
                    current_no >= len(quiz_question_ids))

        if need_reset:
            # SRSを考慮した問題選択
            selected_questions = get_mixed_questions(session, all_questions, requested_category, session_size)
            question_ids = [int(q.get('id', 0)) for q in selected_questions]

            session['quiz_question_ids'] = question_ids
            session['quiz_current'] = 0
            session['quiz_category'] = requested_category
            session.modified = True

            quiz_question_ids = question_ids
            current_no = 0

            logger.info(f"新しいクイズセッション開始: {len(question_ids)}問, カテゴリ: {requested_category}")

        # 範囲チェック
        if current_no >= len(quiz_question_ids):
            return redirect(url_for('result'))

        # 現在の問題を取得
        current_question_id = quiz_question_ids[current_no]
        question = next((q for q in all_questions if int(q.get('id', 0)) == current_question_id), None)

        if not question:
            logger.error(f"問題データ取得失敗: ID {current_question_id}")
            return render_template('error.html', error="問題データの取得に失敗しました。")

        # SRS情報を取得
        srs_data = session.get('srs_data', {})
        question_srs = srs_data.get(str(current_question_id), {})

        return render_template(
            'quiz.html',
            question=question,
            total_questions=len(quiz_question_ids),
            current_no=current_no + 1,
            srs_info=question_srs,
            is_review_question=question_srs.get('total_attempts', 0) > 0
        )
    except Exception as e:
        logger.error(f"quiz関数でエラー: {e}")
        return render_template('error.html', error="問題表示中にエラーが発生しました。")

@app.route('/quiz/next')
def quiz_next():
    """次の問題に進む"""
    current_no = session.get('quiz_current', 0)
    quiz_question_ids = session.get('quiz_question_ids', [])
    
    if current_no >= len(quiz_question_ids):
        return redirect(url_for('result'))
    
    category = session.get('quiz_category', '全体')
    return redirect(url_for('quiz', category=category))

@app.route('/result')
def result():
    """結果画面"""
    try:
        history = session.get('history', [])
        if not history:
            return redirect(url_for('quiz'))
        
        quiz_question_ids = session.get('quiz_question_ids', [])
        session_size = len(quiz_question_ids) if quiz_question_ids else QuizConfig.QUESTIONS_PER_SESSION
        
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
        
        return render_template(
            'result.html',
            correct_count=correct_count,
            total_questions=total_questions,
            elapsed_time=elapsed_time,
            category_scores=category_scores
        )
        
    except Exception as e:
        logger.error(f"result関数でエラー: {e}")
        return render_template('error.html', error="結果表示中にエラーが発生しました。")

@app.route('/statistics')
def statistics():
    """統計画面"""
    try:
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
        
    except Exception as e:
        logger.error(f"statistics関数でエラー: {e}")
        return render_template('error.html', error="統計表示中にエラーが発生しました。")

@app.route('/categories')
def categories():
    """カテゴリ画面"""
    try:
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
        
    except Exception as e:
        logger.error(f"categories関数でエラー: {e}")
        return render_template('error.html', error="カテゴリ表示中にエラーが発生しました。")

@app.route('/review')
def review_list():
    """復習リスト表示"""
    return render_template('review.html')

@app.route('/api/review/questions', methods=['POST'])
def get_review_questions():
    """復習リストの問題詳細を一括取得"""
    try:
        data = request.get_json()
        question_ids = data.get('question_ids', [])
        
        if not question_ids:
            return jsonify({'questions': []})
        
        questions = load_questions()
        review_questions = []
        
        for qid in question_ids:
            question = next((q for q in questions if int(q.get('id', 0)) == int(qid)), None)
            if question:
                review_questions.append({
                    'id': question.get('id'),
                    'category': question.get('category'),
                    'question': question.get('question')[:100] + '...' if len(question.get('question', '')) > 100 else question.get('question'),
                    'difficulty': question.get('difficulty', '標準')
                })
        
        return jsonify({'questions': review_questions})
        
    except Exception as e:
        logger.error(f"復習問題取得エラー: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/srs_stats')
def srs_statistics():
    """SRS学習統計の表示"""
    try:
        srs_data = session.get('srs_data', {})
        
        stats = {
            'total_learned': len(srs_data),
            'mastered': 0,
            'review_needed': 0,
            'learning': 0
        }
        
        today = datetime.now().date()
        
        for question_id, data in srs_data.items():
            level = data.get('level', 0)
            try:
                next_review = datetime.fromisoformat(data['next_review']).date()
                
                if level >= 5:
                    stats['mastered'] += 1
                elif next_review <= today:
                    stats['review_needed'] += 1
                else:
                    stats['learning'] += 1
                    
            except (ValueError, KeyError):
                logger.warning(f"SRS統計データ解析エラー: ID {question_id}")
                stats['learning'] += 1
        
        return render_template('srs_stats.html', stats=stats, srs_data=srs_data)
        
    except Exception as e:
        logger.error(f"SRS統計表示エラー: {e}")
        return render_template('error.html', error="学習統計表示中にエラーが発生しました。")

@app.route('/api/data/export')
def export_data():
    """学習データのエクスポート"""
    try:
        session_id = session.get('session_id')
        if not session_id:
            return jsonify({'error': 'セッションが見つかりません'}), 400
        
        export_data = data_manager.get_data_export(session_id)
        if export_data:
            return jsonify(export_data)
        else:
            return jsonify({'error': 'エクスポートデータがありません'}), 404
            
    except Exception as e:
        logger.error(f"データエクスポートエラー: {e}")
        return jsonify({'error': 'エクスポートに失敗しました'}), 500

@app.route('/api/cache/clear', methods=['POST'])
def clear_cache():
    """問題データキャッシュのクリア"""
    try:
        clear_questions_cache()
        return jsonify({'message': 'キャッシュをクリアしました'})
    except Exception as e:
        logger.error(f"キャッシュクリアエラー: {e}")
        return jsonify({'error': 'キャッシュクリアに失敗しました'}), 500

@app.route('/reset', methods=['GET', 'POST'])
def reset():
    """リセット画面"""
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
    """ヘルプページ"""
    return render_template('help.html', total_questions=QuizConfig.QUESTIONS_PER_SESSION)

@app.route('/api/bookmark', methods=['POST'])
def bookmark_question():
    """問題のブックマーク機能"""
    try:
        data = request.get_json()
        question_id = data.get('question_id')

        if not question_id:
            return jsonify({'success': False, 'error': '問題IDが指定されていません'}), 400

        # セッションにブックマークリストがなければ作成
        if 'bookmarks' not in session:
            session['bookmarks'] = []

        # 問題IDがリストになければ追加
        if question_id not in session['bookmarks']:
            session['bookmarks'].append(question_id)
            session.modified = True # セッションの変更を保存するために必要
            logger.info(f"問題ID {question_id} をブックマークに追加しました")

        return jsonify({'success': True, 'message': '問題をブックマークしました'})

    except Exception as e:
        logger.error(f"ブックマーク機能でエラー: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/bookmarks', methods=['GET'])
def get_bookmarks():
    """ブックマークされた問題IDのリストを返却"""
    try:
        # セッションからブックマークリストを取得。なければ空のリストを返す。
        bookmarks = session.get('bookmarks', [])
        return jsonify({'bookmark_ids': bookmarks})

    except Exception as e:
        logger.error(f"ブックマークリスト取得エラー: {e}")
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def page_not_found(e):
    logger.warning(f"404エラー: {request.url}")
    return render_template('error.html', error="ページが見つかりません"), 404

@app.errorhandler(500)
def internal_error(e):
    logger.error(f"500エラー: {e}")
    return render_template('error.html', error="サーバーエラーが発生しました"), 500

# 初期化
try:
    initial_questions = load_questions()
    logger.info(f"アプリケーション初期化完了: {len(initial_questions)}問読み込み")
except Exception as e:
    logger.error(f"アプリケーション初期化エラー: {e}")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)