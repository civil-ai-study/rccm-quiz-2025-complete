from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_from_directory
import os
import random
from datetime import datetime, timedelta
from collections import defaultdict
import logging
from typing import Dict, List

# 新しいファイルからインポート
from config import Config, QuizConfig, SRSConfig, DataConfig
from utils import load_questions_improved, DataLoadError, DataValidationError, get_sample_data_improved
from data_manager import DataManager, SessionDataManager
from gamification import gamification_manager
from ai_analyzer import ai_analyzer
from adaptive_learning import adaptive_engine
from exam_simulator import exam_simulator
from advanced_analytics import advanced_analytics
from mobile_features import mobile_manager

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

# セッション設定を明示的に追加
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True

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
                return render_template('error.html', error="回答データが不完全です。")

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

            # 正解時は復習リストから除外
            if is_correct:
                bookmarks = session.get('bookmarks', [])
                if str(qid) in bookmarks:
                    bookmarks.remove(str(qid))
                    session['bookmarks'] = bookmarks
                    session.modified = True
                    logger.info(f"正解により復習リストから除外: 問題ID {qid}")

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

            # セッション履歴の保存（競合回避）
            # 一時的に履歴をローカル変数に保存
            current_history = session.get('history', [])
            current_history.append(history_item)
            
            # 一括でセッションを更新
            session_updates = {
                'history': current_history,
                'last_history_update': datetime.now().isoformat()
            }
            
            for key, value in session_updates.items():
                session[key] = value
            
            session.permanent = True  
            session.modified = True
            
            # 保存確認
            saved_history_count = len(session.get('history', []))
            logger.info(f"履歴保存: 問題{qid}, 合計履歴{saved_history_count}件, 直後確認{len(current_history)}件")

            # カテゴリ統計更新
            if 'category_stats' not in session:
                session['category_stats'] = {}

            cat = question.get('category', '不明')
            if cat not in session['category_stats']:
                session['category_stats'][cat] = {'total': 0, 'correct': 0}

            session['category_stats'][cat]['total'] += 1
            if is_correct:
                session['category_stats'][cat]['correct'] += 1
            session.modified = True  # カテゴリ統計変更も保存

            # ゲーミフィケーション更新
            current_streak, streak_badges = gamification_manager.update_streak(session)
            session_performance = {
                'accuracy': 1.0 if is_correct else 0.0,
                'questions': 1
            }
            new_badges = gamification_manager.check_badges(session, session_performance)
            new_badges.extend(streak_badges)
            
            # セッション進行管理
            # POST処理でも現在の問題番号を正確に取得
            current_no = session.get('quiz_current', 0)
            quiz_question_ids = session.get('quiz_question_ids', [])
            
            # 現在の問題番号をより正確に特定
            for i, q_id in enumerate(quiz_question_ids):
                if str(q_id) == str(qid):
                    current_no = i
                    break

            # 次の問題へ進む準備
            next_no = current_no + 1
            
            # セッションの一括更新（競合回避）
            session_final_updates = {
                'quiz_current': next_no,
                'last_update': datetime.now().isoformat(),
                'history': session.get('history', [])  # 履歴を明示的に保持
            }
            
            for key, value in session_final_updates.items():
                session[key] = value
            session.permanent = True
            session.modified = True
            
            # セッション保存の確認
            saved_current = session.get('quiz_current', 'NOT_FOUND')
            logger.info(f"セッション保存確認: quiz_current = {saved_current}")

            logger.info(f"回答処理完了: 問題{qid}, 正答{is_correct}, レベル{srs_info['level']}, ストリーク{current_streak}日")
            logger.info(f"セッション更新: 現在{current_no} -> 次{next_no}, 総問題数{len(quiz_question_ids)}")

            # 次の問題の準備
            is_last_question = (current_no + 1) >= len(quiz_question_ids)
            next_question_index = current_no + 1 if not is_last_question else None
            
            # デバッグログ追加
            logger.info(f"ボタン表示判定: current_no={current_no}, total={len(quiz_question_ids)}, is_last={is_last_question}, next_index={next_question_index}")

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
                'correct_answer_text': question.get(f'option_{question.get("correct_answer", "").lower()}', '不明な正解'),
                'new_badges': new_badges,
                'current_streak': current_streak,
                'badge_info': [gamification_manager.get_badge_info(badge) for badge in new_badges]
            }

            return render_template('quiz_feedback.html', **feedback_data)

        # GET処理（問題表示）
        # 次の問題への遷移の場合は現在のセッションカテゴリを使用
        is_next_request = request.args.get('next') == '1'  # 次の問題へのリクエスト
        if is_next_request:
            requested_category = session.get('quiz_category', '全体')
        else:
            requested_category = request.args.get('category', '全体')
        session_size = request.args.get('size', QuizConfig.QUESTIONS_PER_SESSION)
        specific_qid = request.args.get('qid')

        try:
            session_size = int(session_size)
        except (ValueError, TypeError):
            session_size = QuizConfig.QUESTIONS_PER_SESSION

        # セッション管理
        quiz_question_ids = session.get('quiz_question_ids', [])
        # URLパラメータから現在の問題番号を取得（競合回避）
        url_current = request.args.get('current')
        if is_next_request and url_current:
            try:
                current_no = int(url_current)
                # セッションも同期
                session['quiz_current'] = current_no
                session.modified = True
            except ValueError:
                current_no = session.get('quiz_current', 0)
        else:
            current_no = session.get('quiz_current', 0)
        session_category = session.get('quiz_category', '全体')
        
        # デバッグログ
        logger.info(f"GET処理: current_no={current_no}, quiz_question_ids={quiz_question_ids[:5] if quiz_question_ids else []}, is_next={is_next_request}, total_ids={len(quiz_question_ids)}")
        logger.info(f"セッション詳細: session keys={list(session.keys())}, quiz_current={session.get('quiz_current', 'MISSING')}")

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
        # 次の問題への遷移要求の場合はリセットしない
        logger.info(f"リセット判定: is_next={is_next_request}, quiz_ids={bool(quiz_question_ids)}, category_match={requested_category == session_category}, current_no={current_no}, len={len(quiz_question_ids)}")
        
        need_reset = (not is_next_request and (
                    not quiz_question_ids or
                    request.args.get('reset') == '1' or
                    requested_category != session_category or
                    current_no >= len(quiz_question_ids)))
        
        logger.info(f"need_reset = {need_reset}")

        if need_reset:
            # SRSを考慮した問題選択
            selected_questions = get_mixed_questions(session, all_questions, requested_category, session_size)
            question_ids = [int(q.get('id', 0)) for q in selected_questions]

            # デバッグ: 問題選択の詳細ログ
            logger.info(f"問題選択詳細: requested_size={session_size}, selected_count={len(selected_questions)}, question_ids_count={len(question_ids)}")
            logger.info(f"問題ID一覧: {question_ids}")

            session['quiz_question_ids'] = question_ids
            session['quiz_current'] = 0
            session['quiz_category'] = requested_category
            session.modified = True

            quiz_question_ids = question_ids
            current_no = 0

            logger.info(f"新しい問題セッション開始: {len(question_ids)}問, カテゴリ: {requested_category}")

        # 範囲チェック
        if current_no >= len(quiz_question_ids):
            logger.info(f"範囲チェック: current_no({current_no}) >= len({len(quiz_question_ids)}) - resultにリダイレクト")
            return redirect(url_for('result'))

        # 現在の問題を取得
        current_question_id = quiz_question_ids[current_no]
        logger.info(f"問題ID取得: current_no={current_no}, question_id={current_question_id}")
        question = next((q for q in all_questions if int(q.get('id', 0)) == current_question_id), None)

        if not question:
            logger.error(f"問題データ取得失敗: ID {current_question_id}, available_ids={[q.get('id') for q in all_questions[:5]]}")
            return render_template('error.html', error=f"問題データの取得に失敗しました。(ID: {current_question_id})")

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
        
        # デバッグ用：セッション内容を詳細出力
        logger.info(f"結果画面: 履歴件数={len(history)}")
        logger.info(f"セッションキー={list(session.keys())}")
        logger.info(f"セッション内容(最初の5件): {dict(list(session.items())[:5])}")
        
        
        quiz_question_ids = session.get('quiz_question_ids', [])
        session_size = len(quiz_question_ids) if quiz_question_ids else QuizConfig.QUESTIONS_PER_SESSION
        
        # 履歴が空の場合は適切にハンドリング（ダミーデータは削除）
        if not history:
            logger.info("履歴なしのため/quizにリダイレクト")
            return redirect(url_for('quiz'))
            
        recent_history = history[-session_size:] if len(history) >= session_size else history
        
        # 基本統計
        correct_count = sum(1 for h in recent_history if h.get('is_correct', False))
        total_questions = len(recent_history) if recent_history else 1
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
        # 強制的なキャッシュクリア
        clear_questions_cache()
        logger.info("セッションとキャッシュを完全リセット")
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

@app.route('/force_reset')
def force_reset():
    """強制リセット（トラブルシューティング用）"""
    try:
        # セッション完全削除
        session.clear()
        # キャッシュクリア
        clear_questions_cache()
        # セッションIDも新規生成
        session['session_id'] = os.urandom(16).hex()
        session.permanent = True
        logger.info("強制リセット実行完了")
        return jsonify({
            'success': True, 
            'message': '完全リセットが完了しました。ページを再読み込みしてください。',
            'new_session_id': session['session_id']
        })
    except Exception as e:
        logger.error(f"強制リセットエラー: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/help')
def help_page():
    """ヘルプページ"""
    return render_template('help.html', total_questions=QuizConfig.QUESTIONS_PER_SESSION)

@app.route('/debug')
def debug_page():
    """デバッグページ"""
    import json
    session_data = dict(session)
    session_data_json = json.dumps(session_data, indent=2, default=str)
    return render_template('debug.html', session_data=session_data_json)

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

@app.route('/api/bookmark', methods=['DELETE'])
def remove_bookmark():
    """復習リストから問題を除外"""
    try:
        data = request.get_json()
        question_id = data.get('question_id')
        
        if not question_id:
            return jsonify({'success': False, 'error': '問題IDが指定されていません'}), 400
        
        # セッションから復習リストを取得
        bookmarks = session.get('bookmarks', [])
        
        # リストから除外
        if question_id in bookmarks:
            bookmarks.remove(question_id)
            session['bookmarks'] = bookmarks
            session.modified = True
            logger.info(f"復習リストから除外: 問題ID {question_id}")
            return jsonify({'success': True, 'message': '復習リストから除外しました'})
        else:
            return jsonify({'success': False, 'error': '指定された問題は復習リストに登録されていません'}), 404
        
    except Exception as e:
        logger.error(f"復習除外エラー: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/review')
def review_page():
    """復習リスト専用ページ"""
    try:
        all_questions = load_questions()
        bookmarks = session.get('bookmarks', [])
        
        if not bookmarks:
            return render_template('review.html', questions=[], message="復習リストは空です。問題を解いて復習登録してください。")
        
        # ブックマークされた問題を取得
        review_questions = []
        for question in all_questions:
            if str(question.get('id')) in bookmarks:
                review_questions.append(question)
        
        return render_template('review.html', questions=review_questions, total_count=len(review_questions))
        
    except Exception as e:
        logger.error(f"復習ページエラー: {e}")
        return render_template('error.html', error="復習ページの表示中にエラーが発生しました。")

@app.route('/quiz/review')
def review_quiz():
    """復習リストの問題のみで問題練習を開始"""
    try:
        all_questions = load_questions()
        bookmarks = session.get('bookmarks', [])
        
        if not bookmarks:
            return render_template('error.html', error="復習リストが空です。まず問題を復習登録してください。")
        
        # ブックマークされた問題を取得
        review_questions = []
        for question in all_questions:
            if str(question.get('id')) in bookmarks:
                review_questions.append(question)
        
        if not review_questions:
            return render_template('error.html', error="復習対象の問題が見つかりません。")
        
        # 復習問題をランダムに並び替え
        random.shuffle(review_questions)
        
        # セッションに設定
        question_ids = [int(q.get('id', 0)) for q in review_questions]
        session['quiz_question_ids'] = question_ids
        session['quiz_current'] = 0
        session['quiz_category'] = '復習問題'
        session.modified = True
        
        logger.info(f"復習問題開始: {len(question_ids)}問")
        
        # 最初の問題にリダイレクト
        return redirect(url_for('quiz'))
        
    except Exception as e:
        logger.error(f"復習問題エラー: {e}")
        return render_template('error.html', error="復習問題の開始中にエラーが発生しました。")

@app.route('/achievements')
def achievements():
    """達成バッジ・ゲーミフィケーション画面"""
    try:
        earned_badges = session.get('earned_badges', [])
        badge_details = []
        
        for badge_id in earned_badges:
            badge_info = gamification_manager.get_badge_info(badge_id)
            badge_details.append({
                'id': badge_id,
                'name': badge_info['name'],
                'description': badge_info['description'],
                'icon': badge_info['icon'],
                'color': badge_info['color']
            })
        
        # 学習インサイト
        insights = gamification_manager.get_study_insights(session)
        logger.debug(f"Insights keys: {list(insights.keys()) if insights else 'None'}")
        
        # 学習カレンダー
        calendar_data = gamification_manager.generate_study_calendar(session)
        
        return render_template(
            'achievements.html',
            earned_badges=badge_details,
            all_badges=gamification_manager.achievements,
            insights=insights,
            calendar_data=calendar_data
        )
        
    except Exception as e:
        logger.error(f"達成画面エラー: {e}")
        return render_template('error.html', error="達成画面の表示中にエラーが発生しました。")

@app.route('/study_calendar')
def study_calendar():
    """学習カレンダー画面"""
    try:
        calendar_data = gamification_manager.generate_study_calendar(session, months=6)
        insights = gamification_manager.get_study_insights(session)
        
        return render_template(
            'study_calendar.html',
            calendar_data=calendar_data,
            insights=insights
        )
        
    except Exception as e:
        logger.error(f"学習カレンダーエラー: {e}")
        return render_template('error.html', error="学習カレンダーの表示中にエラーが発生しました。")

@app.route('/api/gamification/status')
def gamification_status():
    """ゲーミフィケーション状態のAPI"""
    try:
        insights = gamification_manager.get_study_insights(session)
        earned_badges = session.get('earned_badges', [])
        
        return jsonify({
            'streak': insights.get('study_streak', 0),
            'max_streak': insights.get('max_streak', 0),
            'badges_count': len(earned_badges),
            'total_questions': insights.get('total_questions', 0),
            'overall_accuracy': insights.get('overall_accuracy', 0),
            'recent_accuracy': insights.get('recent_accuracy', 0)
        })
        
    except Exception as e:
        logger.error(f"ゲーミフィケーション状態取得エラー: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/ai_analysis')
def ai_analysis():
    """AI弱点分析画面"""
    try:
        # AI分析実行
        analysis_result = ai_analyzer.analyze_weak_areas(session)
        
        # 推奨学習モード取得
        recommended_mode = adaptive_engine.get_learning_mode_recommendation(session, analysis_result)
        
        return render_template(
            'ai_analysis.html',
            analysis=analysis_result,
            recommended_mode=recommended_mode,
            learning_modes=adaptive_engine.learning_modes
        )
        
    except Exception as e:
        logger.error(f"AI分析エラー: {e}")
        return render_template('error.html', error="AI分析の表示中にエラーが発生しました。")

@app.route('/adaptive_quiz')
def adaptive_quiz():
    """アダプティブ問題練習モード"""
    try:
        learning_mode = request.args.get('mode', 'balanced')
        session_size = int(request.args.get('size', QuizConfig.QUESTIONS_PER_SESSION))
        
        all_questions = load_questions()
        if not all_questions:
            return render_template('error.html', error="問題データが存在しません。")
        
        # AI分析実行
        ai_analysis = ai_analyzer.analyze_weak_areas(session)
        
        # アダプティブ問題選択
        adaptive_questions = adaptive_engine.get_adaptive_questions(
            session, all_questions, ai_analysis, session_size, learning_mode
        )
        
        if not adaptive_questions:
            return render_template('error.html', error="選択可能な問題がありません。")
        
        # アダプティブセッション開始
        question_ids = [int(q.get('id', 0)) for q in adaptive_questions]
        session['quiz_question_ids'] = question_ids
        session['quiz_current'] = 0
        session['quiz_category'] = 'AI適応学習'
        session['adaptive_mode'] = learning_mode
        session.modified = True
        
        logger.info(f"アダプティブ問題開始: {len(question_ids)}問, モード: {learning_mode}")
        
        # 最初の問題を表示
        return redirect(url_for('quiz'))
        
    except Exception as e:
        logger.error(f"アダプティブ問題エラー: {e}")
        return render_template('error.html', error="アダプティブ問題の開始中にエラーが発生しました。")

@app.route('/api/ai_analysis', methods=['GET'])
def api_ai_analysis():
    """AI分析結果のAPI"""
    try:
        analysis_result = ai_analyzer.analyze_weak_areas(session)
        recommended_mode = adaptive_engine.get_learning_mode_recommendation(session, analysis_result)
        
        return jsonify({
            'analysis': analysis_result,
            'recommended_mode': recommended_mode,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"AI分析API エラー: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/learning_plan')
def learning_plan():
    """個人学習プラン画面"""
    try:
        # AI分析実行
        analysis_result = ai_analyzer.analyze_weak_areas(session)
        
        # 学習プラン詳細
        learning_plan = analysis_result.get('learning_plan', {})
        weak_areas = analysis_result.get('weak_areas', {})
        
        # 推奨スケジュール生成
        schedule = generate_weekly_schedule(learning_plan, weak_areas)
        
        return render_template(
            'learning_plan.html',
            analysis=analysis_result,
            plan=learning_plan,
            schedule=schedule
        )
        
    except Exception as e:
        logger.error(f"学習プランエラー: {e}")
        return render_template('error.html', error="学習プランの表示中にエラーが発生しました。")

def generate_weekly_schedule(learning_plan: Dict, weak_areas: Dict) -> List[Dict]:
    """週間学習スケジュールの生成"""
    schedule = []
    
    for day in range(7):
        day_names = ['月', '火', '水', '木', '金', '土', '日']
        
        if learning_plan.get('plan_type') == 'weakness_focused':
            primary_focus = learning_plan.get('primary_focus', {})
            if day % 3 == 0 and primary_focus:  # 3日に1回集中学習
                schedule.append({
                    'day': day_names[day],
                    'type': 'intensive',
                    'focus': primary_focus.get('category', ''),
                    'questions': primary_focus.get('recommended_questions', 10),
                    'description': f"{primary_focus.get('category', '')}の集中学習"
                })
            else:
                schedule.append({
                    'day': day_names[day],
                    'type': 'light',
                    'focus': 'mixed',
                    'questions': 5,
                    'description': '軽い復習とバランス学習'
                })
        else:
            schedule.append({
                'day': day_names[day],
                'type': 'balanced',
                'focus': 'mixed',
                'questions': 8,
                'description': 'バランス学習'
            })
    
    return schedule

@app.route('/exam_simulator')
def exam_simulator_page():
    """試験シミュレーター画面"""
    try:
        return render_template(
            'exam_simulator.html',
            exam_configs=exam_simulator.exam_configs
        )
        
    except Exception as e:
        logger.error(f"試験シミュレーター画面エラー: {e}")
        return render_template('error.html', error="試験シミュレーター画面の表示中にエラーが発生しました。")

@app.route('/start_exam/<exam_type>')
def start_exam(exam_type):
    """試験開始"""
    try:
        all_questions = load_questions()
        if not all_questions:
            return render_template('error.html', error="問題データが存在しません。")
        
        # 試験セッション生成
        exam_session = exam_simulator.generate_exam_session(all_questions, exam_type, session)
        
        # セッションに保存
        session['exam_session'] = exam_session
        session.modified = True
        
        logger.info(f"試験開始: {exam_type}, ID: {exam_session['exam_id']}")
        
        return redirect(url_for('exam_question'))
        
    except Exception as e:
        logger.error(f"試験開始エラー: {e}")
        return render_template('error.html', error="試験の開始中にエラーが発生しました。")

@app.route('/exam_question')
def exam_question():
    """試験問題表示"""
    try:
        exam_session = session.get('exam_session')
        if not exam_session or exam_session['status'] != 'in_progress':
            return redirect(url_for('exam_simulator_page'))
        
        current_q_index = exam_session['current_question']
        questions = exam_session['questions']
        
        if current_q_index >= len(questions):
            return redirect(url_for('exam_results'))
        
        current_question = questions[current_q_index]
        
        # 試験情報
        exam_info = {
            'current_question_number': current_q_index + 1,
            'total_questions': len(questions),
            'time_remaining': exam_simulator.get_time_remaining(exam_session),
            'exam_type': exam_session['exam_type'],
            'exam_name': exam_session['config']['name'],
            'flagged_questions': exam_session['flagged_questions'],
            'answered_questions': list(exam_session['answers'].keys())
        }
        
        # 時間警告チェック
        time_warning = exam_simulator.should_give_time_warning(exam_session)
        
        return render_template(
            'exam_question.html',
            question=current_question,
            exam_info=exam_info,
            time_warning=time_warning
        )
        
    except Exception as e:
        logger.error(f"試験問題表示エラー: {e}")
        return render_template('error.html', error="試験問題の表示中にエラーが発生しました。")

@app.route('/submit_exam_answer', methods=['POST'])
def submit_exam_answer():
    """試験回答提出"""
    try:
        exam_session = session.get('exam_session')
        if not exam_session or exam_session['status'] != 'in_progress':
            return jsonify({'success': False, 'error': '試験セッションが無効です'})
        
        answer = request.form.get('answer')
        elapsed = float(request.form.get('elapsed', 0))
        question_index = exam_session['current_question']
        
        # 自動提出チェック
        if exam_simulator.auto_submit_check(exam_session):
            result = exam_simulator.finish_exam(exam_session)
            session['exam_session'] = exam_session
            session.modified = True
            return jsonify({
                'success': True,
                'exam_finished': True,
                'redirect': url_for('exam_results')
            })
        
        # 回答提出
        result = exam_simulator.submit_exam_answer(exam_session, question_index, answer, elapsed)
        
        # セッション更新
        session['exam_session'] = exam_session
        session.modified = True
        
        if result.get('exam_completed'):
            return jsonify({
                'success': True,
                'exam_finished': True,
                'redirect': url_for('exam_results')
            })
        else:
            return jsonify({
                'success': True,
                'next_question': result.get('next_question', 0),
                'remaining_questions': result.get('remaining_questions', 0)
            })
        
    except Exception as e:
        logger.error(f"試験回答提出エラー: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/flag_exam_question', methods=['POST'])
def flag_exam_question():
    """試験問題フラグ設定"""
    try:
        exam_session = session.get('exam_session')
        if not exam_session:
            return jsonify({'success': False, 'error': '試験セッションが無効です'})
        
        question_index = int(request.form.get('question_index', 0))
        action = request.form.get('action', 'flag')  # flag or unflag
        
        if action == 'flag':
            success = exam_simulator.flag_question(exam_session, question_index)
        else:
            success = exam_simulator.unflag_question(exam_session, question_index)
        
        session['exam_session'] = exam_session
        session.modified = True
        
        return jsonify({'success': success})
        
    except Exception as e:
        logger.error(f"問題フラグエラー: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/exam_navigation')
def exam_navigation():
    """試験ナビゲーション画面"""
    try:
        exam_session = session.get('exam_session')
        if not exam_session:
            return redirect(url_for('exam_simulator_page'))
        
        summary = exam_simulator.get_exam_summary(exam_session)
        
        return render_template('exam_navigation.html', summary=summary, exam_session=exam_session)
        
    except Exception as e:
        logger.error(f"試験ナビゲーションエラー: {e}")
        return render_template('error.html', error="試験ナビゲーションの表示中にエラーが発生しました。")

@app.route('/finish_exam', methods=['POST'])
def finish_exam():
    """試験終了"""
    try:
        exam_session = session.get('exam_session')
        if not exam_session:
            return jsonify({'success': False, 'error': '試験セッションが無効です'})
        
        result = exam_simulator.finish_exam(exam_session)
        session['exam_session'] = exam_session
        session.modified = True
        
        return jsonify({
            'success': True,
            'redirect': url_for('exam_results')
        })
        
    except Exception as e:
        logger.error(f"試験終了エラー: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/exam_results')
def exam_results():
    """試験結果画面"""
    try:
        exam_session = session.get('exam_session')
        if not exam_session or 'results' not in exam_session:
            return redirect(url_for('exam_simulator_page'))
        
        results = exam_session['results']
        
        # 過去の試験結果を記録
        if 'exam_history' not in session:
            session['exam_history'] = []
        
        session['exam_history'].append({
            'exam_id': exam_session['exam_id'],
            'exam_type': exam_session['exam_type'],
            'score': results['score'],
            'date': exam_session['start_time'][:10],
            'passed': results['passed']
        })
        session.modified = True
        
        return render_template('exam_results.html', results=results, exam_session=exam_session)
        
    except Exception as e:
        logger.error(f"試験結果表示エラー: {e}")
        return render_template('error.html', error="試験結果の表示中にエラーが発生しました。")

@app.route('/advanced_statistics')
def advanced_statistics():
    """高度な統計分析画面"""
    try:
        # 試験履歴を取得
        exam_history = session.get('exam_history', [])
        
        # 包括的なレポートを生成
        comprehensive_report = advanced_analytics.generate_comprehensive_report(session, exam_history)
        
        return render_template(
            'advanced_statistics.html',
            report=comprehensive_report
        )
        
    except Exception as e:
        logger.error(f"高度な統計エラー: {e}")
        return render_template('error.html', error="高度な統計の表示中にエラーが発生しました。")

@app.route('/api/exam_status')
def api_exam_status():
    """試験状態API"""
    try:
        exam_session = session.get('exam_session')
        if not exam_session:
            return jsonify({'exam_active': False})
        
        return jsonify({
            'exam_active': exam_session['status'] == 'in_progress',
            'time_remaining': exam_simulator.get_time_remaining(exam_session),
            'current_question': exam_session['current_question'],
            'total_questions': len(exam_session['questions']),
            'auto_submit_warning': exam_simulator.get_time_remaining(exam_session) <= 5
        })
        
    except Exception as e:
        logger.error(f"試験状態API エラー: {e}")
        return jsonify({'error': str(e)}), 500

# モバイル機能のAPI エンドポイント

@app.route('/api/mobile/manifest')
def mobile_manifest():
    """PWAマニフェストの動的生成"""
    try:
        manifest = mobile_manager.get_pwa_manifest()
        return jsonify(manifest)
    except Exception as e:
        logger.error(f"マニフェスト生成エラー: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/mobile/offline/save', methods=['POST'])
def save_offline_data():
    """オフラインデータの保存"""
    try:
        data = request.get_json()
        session_id = session.get('session_id')
        
        if not session_id:
            return jsonify({'success': False, 'error': 'セッションIDが見つかりません'}), 400
        
        success = mobile_manager.save_offline_session(session_id, data)
        
        if success:
            return jsonify({'success': True, 'message': 'オフラインデータを保存しました'})
        else:
            return jsonify({'success': False, 'error': 'データ保存に失敗しました'}), 500
            
    except Exception as e:
        logger.error(f"オフラインデータ保存エラー: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/mobile/offline/sync', methods=['POST'])
def sync_offline_data():
    """オフラインデータの同期"""
    try:
        sync_result = mobile_manager.sync_offline_data(session)
        session.modified = True
        
        mobile_manager.update_last_sync_time()
        
        return jsonify({
            'success': sync_result['success'],
            'synced_sessions': sync_result['synced_sessions'],
            'failed_sessions': sync_result['failed_sessions'],
            'errors': sync_result['errors']
        })
        
    except Exception as e:
        logger.error(f"オフライン同期エラー: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/mobile/voice/settings', methods=['GET', 'POST'])
def voice_settings():
    """音声設定の取得・更新"""
    try:
        if request.method == 'GET':
            settings = mobile_manager.get_voice_settings()
            return jsonify(settings)
        else:
            data = request.get_json()
            success = mobile_manager.update_voice_settings(data)
            
            if success:
                return jsonify({'success': True, 'message': '音声設定を更新しました'})
            else:
                return jsonify({'success': False, 'error': '設定更新に失敗しました'}), 500
                
    except Exception as e:
        logger.error(f"音声設定エラー: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/mobile/touch/settings', methods=['GET', 'POST'])
def touch_settings():
    """タッチジェスチャー設定の取得・更新"""
    try:
        if request.method == 'GET':
            settings = mobile_manager.get_touch_settings()
            return jsonify(settings)
        else:
            data = request.get_json()
            success = mobile_manager.update_touch_settings(data)
            
            if success:
                return jsonify({'success': True, 'message': 'タッチ設定を更新しました'})
            else:
                return jsonify({'success': False, 'error': '設定更新に失敗しました'}), 500
                
    except Exception as e:
        logger.error(f"タッチ設定エラー: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/mobile/question/<int:question_id>')
def mobile_optimized_question(question_id):
    """モバイル最適化問題データ"""
    try:
        questions = load_questions()
        question = next((q for q in questions if int(q.get('id', 0)) == question_id), None)
        
        if not question:
            return jsonify({'error': '問題が見つかりません'}), 404
        
        mobile_question = mobile_manager.get_mobile_optimized_question(question)
        return jsonify(mobile_question)
        
    except Exception as e:
        logger.error(f"モバイル問題取得エラー: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/mobile/cache/questions')
def mobile_cache_questions():
    """モバイル用問題キャッシュデータ"""
    try:
        questions = load_questions()
        cache_data = mobile_manager.generate_mobile_cache_data(questions)
        return jsonify(cache_data)
        
    except Exception as e:
        logger.error(f"モバイルキャッシュ生成エラー: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/mobile/performance')
def mobile_performance_metrics():
    """モバイルパフォーマンス指標"""
    try:
        metrics = mobile_manager.get_performance_metrics()
        return jsonify(metrics)
        
    except Exception as e:
        logger.error(f"パフォーマンス指標エラー: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/mobile_settings')
def mobile_settings():
    """モバイル設定画面"""
    return render_template('mobile_settings.html')

@app.route('/manifest.json')
def pwa_manifest():
    """PWAマニフェストの配信"""
    try:
        manifest = mobile_manager.get_pwa_manifest()
        response = jsonify(manifest)
        response.headers['Content-Type'] = 'application/manifest+json'
        return response
    except Exception as e:
        logger.error(f"マニフェスト配信エラー: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/sw.js')
def service_worker():
    """Service Workerの配信"""
    try:
        return send_from_directory('static', 'sw.js', mimetype='application/javascript')
    except Exception as e:
        logger.debug(f"Service Worker配信エラー: {e}")
        return '', 404

@app.route('/favicon.ico')
def favicon():
    """Faviconの配信"""
    try:
        return send_from_directory('static/icons', 'favicon.ico')
    except Exception as e:
        logger.debug(f"Favicon配信エラー: {e}")
        return '', 404

@app.route('/icon-<size>.png')
def app_icon(size):
    """アプリアイコンの配信"""
    try:
        return send_from_directory('static/icons', f'icon-{size}.png')
    except Exception as e:
        logger.debug(f"アイコン配信エラー: {e}")
        return '', 404

@app.errorhandler(404)
def page_not_found(e):
    logger.warning(f"404エラー: {request.url}")
    # 静的ファイル（アイコン、sw.js等）の404エラーは警告レベルを下げる
    if any(path in request.url for path in ['/static/icons/', '/sw.js', '/favicon.ico', '/icon-']):
        logger.debug(f"静的ファイル404: {request.url}")
        return '', 404  # 空のレスポンスを返す
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