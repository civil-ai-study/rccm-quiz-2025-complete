from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_from_directory, make_response
import os
import random
from datetime import datetime, timedelta
from collections import defaultdict
import logging
from typing import Dict, List

# 新しいファイルからインポート
from config import Config, QuizConfig, SRSConfig, DataConfig, RCCMConfig
from utils import load_questions_improved, DataLoadError, DataValidationError, get_sample_data_improved, load_rccm_data_files
from data_manager import DataManager, SessionDataManager
from gamification import gamification_manager
from ai_analyzer import ai_analyzer
from adaptive_learning import adaptive_engine
from exam_simulator import exam_simulator
from advanced_analytics import advanced_analytics
from mobile_features import mobile_manager
from learning_optimizer import learning_optimizer
from admin_dashboard import admin_dashboard
from social_learning import social_learning_manager
from api_integration import api_manager
from advanced_personalization import advanced_personalization

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
    RCCM統合問題データの読み込み（4-1基礎・4-2専門対応）
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
    
    logger.info("RCCM統合問題データの読み込み開始")
    
    try:
        # RCCM統合データ読み込み（4-1・4-2ファイル対応）
        data_dir = os.path.dirname(DataConfig.QUESTIONS_CSV)
        questions = load_rccm_data_files(data_dir)
        
        if questions:
            _questions_cache = questions
            _cache_timestamp = current_time
            logger.info(f"RCCM統合データ読み込み完了: {len(questions)}問")
            return questions
        else:
            raise DataLoadError("統合データが空でした")
        
    except Exception as e:
        logger.warning(f"RCCM統合データ読み込みエラー: {e}")
        logger.info("レガシーデータ読み込みを試行")
        
        try:
            # フォールバック: レガシーデータ読み込み
            questions = load_questions_improved(DataConfig.QUESTIONS_CSV)
            # レガシーデータに部門・問題種別情報を追加
            for q in questions:
                if 'department' not in q:
                    q['department'] = 'road'  # デフォルト部門
                if 'question_type' not in q:
                    q['question_type'] = 'basic'  # デフォルト問題種別
            
            _questions_cache = questions
            _cache_timestamp = current_time
            logger.info(f"レガシーデータ読み込み完了: {len(questions)}問")
            return questions
            
        except Exception as e2:
            logger.error(f"レガシーデータ読み込みエラー: {e2}")
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

def get_mixed_questions(user_session, all_questions, requested_category='全体', session_size=None, department='', question_type='', year=None):
    """新問題と復習問題をミックスした出題（RCCM部門対応版）"""
    if session_size is None:
        session_size = QuizConfig.QUESTIONS_PER_SESSION
    
    due_questions = get_due_questions(user_session, all_questions)
    
    # 設定から復習問題の比率を取得
    max_review_count = min(len(due_questions), 
                          int(session_size * SRSConfig.MAX_REVIEW_RATIO))
    selected_questions = []
    
    # 復習問題を追加（部門・問題種別でもフィルタリング）
    for i, due_item in enumerate(due_questions):
        if i >= max_review_count:
            break
        
        question = due_item['question']
        # 部門・問題種別の条件チェック
        if department and question.get('department') != department:
            continue
        if question_type and question.get('question_type') != question_type:
            continue
        
        selected_questions.append(question)
    
    # 残りを新問題で埋める
    remaining_count = session_size - len(selected_questions)
    
    # 問題フィルタリング条件
    available_questions = all_questions
    
    # 問題種別でフィルタリング（最優先）
    if question_type:
        available_questions = [q for q in available_questions if q.get('question_type') == question_type]
        logger.info(f"問題種別フィルタ適用: {question_type}, 結果: {len(available_questions)}問")
    
    # 部門でフィルタリング（基礎科目の場合はスキップ）
    if department and question_type != 'basic':
        available_questions = [q for q in available_questions if q.get('department') == department]
        logger.info(f"部門フィルタ適用: {department}, 結果: {len(available_questions)}問")
    
    # カテゴリでフィルタリング
    if requested_category != '全体':
        available_questions = [q for q in available_questions if q.get('category') == requested_category]
    
    # 年度でフィルタリング
    if year:
        available_questions = [q for q in available_questions if str(q.get('year', '')) == str(year)]
    
    # 既に選択済みの問題を除外
    selected_ids = [int(q.get('id', 0)) for q in selected_questions]
    new_questions = [q for q in available_questions if int(q.get('id', 0)) not in selected_ids]
    
    random.shuffle(new_questions)
    selected_questions.extend(new_questions[:remaining_count])
    
    random.shuffle(selected_questions)
    
    filter_info = []
    if department:
        filter_info.append(f"部門:{RCCMConfig.DEPARTMENTS.get(department, {}).get('name', department)}")
    if question_type:
        filter_info.append(f"種別:{RCCMConfig.QUESTION_TYPES.get(question_type, {}).get('name', question_type)}")
    if requested_category != '全体':
        filter_info.append(f"カテゴリ:{requested_category}")
    if year:
        filter_info.append(f"年度:{year}")
    
    logger.info(f"問題選択完了: 復習{len([q for q in selected_questions if any(due['question'] == q for due in due_questions)])}問, "
                f"新規{len(selected_questions) - len([q for q in selected_questions if any(due['question'] == q for due in due_questions)])}問, "
                f"フィルタ:[{', '.join(filter_info) if filter_info else '全体'}]")
    
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
    response = make_response(render_template('index.html'))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/force_refresh')
def force_refresh():
    """強制的にキャッシュをクリアして最新版を表示"""
    response = make_response(redirect('/'))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

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
                'department': question.get('department', session.get('selected_department', '')),
                'question_type': question.get('question_type', session.get('selected_question_type', '')),
                'is_correct': is_correct,
                'user_answer': answer,
                'correct_answer': question.get('correct_answer', ''),
                'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'elapsed': float(elapsed),
                'srs_level': srs_info['level'],
                'is_review': srs_info['total_attempts'] > 1,
                'difficulty': question.get('difficulty', '標準')
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
            
            # リアルタイム難易度調整（5問ごとに実行）
            difficulty_adjustment = {'adjusted': False}
            if len(current_history) % 5 == 0 and len(current_history) >= 5:
                recent_results = current_history[-5:]  # 最近5問
                difficulty_adjustment = adaptive_engine.monitor_and_adjust_difficulty(session, recent_results)
                if difficulty_adjustment.get('adjusted', False):
                    logger.info(f"難易度自動調整: {difficulty_adjustment['old_level']} → {difficulty_adjustment['new_level']}")
                    session.modified = True
            
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
            is_last_question = (current_no >= len(quiz_question_ids) - 1)
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
                'badge_info': [gamification_manager.get_badge_info(badge) for badge in new_badges],
                'difficulty_adjustment': difficulty_adjustment
            }

            return render_template('quiz_feedback.html', **feedback_data)

        # GET処理（問題表示）
        # 次の問題への遷移の場合は現在のセッション情報を使用
        is_next_request = request.args.get('next') == '1'  # 次の問題へのリクエスト
        if is_next_request:
            requested_category = session.get('quiz_category', '全体')
            requested_department = session.get('selected_department', '')
            requested_question_type = session.get('selected_question_type', '')
            requested_year = session.get('selected_year')
        else:
            requested_category = request.args.get('category', '全体')
            requested_department = request.args.get('department', session.get('selected_department', ''))
            requested_question_type = request.args.get('question_type', session.get('selected_question_type', ''))
            
            # type=basicパラメータの処理（基礎科目専用）
            quiz_type = request.args.get('type')
            if quiz_type == 'basic':
                requested_question_type = 'basic'
                requested_department = ''  # 基礎科目は部門不問
                requested_category = '全体'  # カテゴリも全体に設定
                logger.info("基礎科目専用モード: question_type=basic, department=None")
        
        # 年度パラメータの取得
        requested_year = request.args.get('year')
        
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
            # SRSを考慮した問題選択（RCCM部門対応）
            selected_questions = get_mixed_questions(session, all_questions, requested_category, session_size, requested_department, requested_question_type, requested_year)
            question_ids = [int(q.get('id', 0)) for q in selected_questions]

            # デバッグ: 問題選択の詳細ログ
            logger.info(f"問題選択詳細: requested_size={session_size}, selected_count={len(selected_questions)}, question_ids_count={len(question_ids)}")
            logger.info(f"問題ID一覧: {question_ids}")

            # セッション情報を更新（部門・問題種別情報も保存）
            session['quiz_question_ids'] = question_ids
            session['quiz_current'] = 0
            session['quiz_category'] = requested_category
            if requested_department:
                session['selected_department'] = requested_department
            if requested_question_type:
                session['selected_question_type'] = requested_question_type
            if requested_year:
                session['selected_year'] = requested_year
            session.modified = True

            quiz_question_ids = question_ids
            current_no = 0

            filter_desc = []
            if requested_department:
                dept_name = RCCMConfig.DEPARTMENTS.get(requested_department, {}).get('name', requested_department)
                filter_desc.append(f"部門:{dept_name}")
            if requested_question_type:
                type_name = RCCMConfig.QUESTION_TYPES.get(requested_question_type, {}).get('name', requested_question_type)
                filter_desc.append(f"種別:{type_name}")
            if requested_category != '全体':
                filter_desc.append(f"カテゴリ:{requested_category}")
            
            logger.info(f"新しい問題セッション開始: {len(question_ids)}問, フィルタ: {', '.join(filter_desc) if filter_desc else '全体'}")

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

@app.route('/department_statistics')
def department_statistics():
    """部門別詳細統計画面"""
    try:
        from department_statistics import department_statistics as dept_stats_analyzer
        
        # 現在のユーザーセッション
        user_session = session
        
        # 包括的な部門別統計レポートを生成
        report = dept_stats_analyzer.generate_comprehensive_department_report(user_session)
        
        # 部門情報を追加
        departments = RCCMConfig.DEPARTMENTS
        
        logger.info(f"部門別統計レポート生成: {report.get('total_questions_analyzed', 0)}問分析")
        
        return render_template(
            'department_statistics.html',
            report=report,
            departments=departments,
            title='部門別詳細統計'
        )
        
    except Exception as e:
        logger.error(f"department_statistics関数でエラー: {e}")
        return render_template('error.html', error="部門別統計表示中にエラーが発生しました。")

@app.route('/departments')
def departments():
    """RCCM部門選択画面"""
    try:
        # 現在選択されている部門を取得
        current_department = session.get('selected_department', RCCMConfig.DEFAULT_DEPARTMENT)
        
        # 各部門の学習進捗を計算
        department_progress = {}
        history = session.get('history', [])
        
        for dept_id, dept_info in RCCMConfig.DEPARTMENTS.items():
            # この部門での問題数と正答数を集計
            dept_history = [h for h in history if h.get('department') == dept_id]
            total_answered = len(dept_history)
            correct_count = sum(1 for h in dept_history if h.get('is_correct', False))
            
            department_progress[dept_id] = {
                'total_answered': total_answered,
                'correct_count': correct_count,
                'accuracy': (correct_count / total_answered * 100) if total_answered > 0 else 0.0
            }
        
        return render_template(
            'departments.html',
            departments=RCCMConfig.DEPARTMENTS,
            current_department=current_department,
            department_progress=department_progress
        )
        
    except Exception as e:
        logger.error(f"departments関数でエラー: {e}")
        return render_template('error.html', error="部門選択画面の表示中にエラーが発生しました。")

@app.route('/departments/<department_id>')
def select_department(department_id):
    """部門選択処理"""
    try:
        if department_id not in RCCMConfig.DEPARTMENTS:
            logger.error(f"無効な部門ID: {department_id}")
            return render_template('error.html', error="指定された部門が見つかりません。")
        
        # セッションに部門を保存
        session['selected_department'] = department_id
        session.modified = True
        
        logger.info(f"部門選択: {department_id} ({RCCMConfig.DEPARTMENTS[department_id]['name']})")
        
        # 問題種別選択画面にリダイレクト
        return redirect(url_for('question_types', department_id=department_id))
        
    except Exception as e:
        logger.error(f"部門選択エラー: {e}")
        return render_template('error.html', error="部門選択中にエラーが発生しました。")

@app.route('/departments/<department_id>/types')
def question_types(department_id):
    """問題種別選択画面（4-1基礎 / 4-2専門）"""
    try:
        if department_id not in RCCMConfig.DEPARTMENTS:
            return render_template('error.html', error="指定された部門が見つかりません。")
        
        department_info = RCCMConfig.DEPARTMENTS[department_id]
        
        # 各問題種別の学習進捗を計算
        type_progress = {}
        history = session.get('history', [])
        
        for type_id, type_info in RCCMConfig.QUESTION_TYPES.items():
            # この部門・種別での問題数と正答数を集計
            type_history = [h for h in history 
                          if h.get('department') == department_id and h.get('question_type') == type_id]
            total_answered = len(type_history)
            correct_count = sum(1 for h in type_history if h.get('is_correct', False))
            
            type_progress[type_id] = {
                'total_answered': total_answered,
                'correct_count': correct_count,
                'accuracy': (correct_count / total_answered * 100) if total_answered > 0 else 0.0
            }
        
        return render_template(
            'question_types.html',
            department=department_info,
            question_types=RCCMConfig.QUESTION_TYPES,
            type_progress=type_progress
        )
        
    except Exception as e:
        logger.error(f"問題種別選択エラー: {e}")
        return render_template('error.html', error="問題種別選択画面の表示中にエラーが発生しました。")

@app.route('/departments/<department_id>/types/<question_type>/categories')
def department_categories(department_id, question_type):
    """部門・問題種別別のカテゴリ画面"""
    try:
        if department_id not in RCCMConfig.DEPARTMENTS:
            return render_template('error.html', error="指定された部門が見つかりません。")
        
        if question_type not in RCCMConfig.QUESTION_TYPES:
            return render_template('error.html', error="指定された問題種別が見つかりません。")
        
        # セッションに選択情報を保存
        session['selected_department'] = department_id
        session['selected_question_type'] = question_type
        session.modified = True
        
        department_info = RCCMConfig.DEPARTMENTS[department_id]
        type_info = RCCMConfig.QUESTION_TYPES[question_type]
        
        questions = load_questions()
        
        # 指定された部門・問題種別の問題のみをフィルタリング
        filtered_questions = [q for q in questions 
                             if q.get('department') == department_id and q.get('question_type') == question_type]
        
        # カテゴリ情報を集計
        category_details = {}
        for q in filtered_questions:
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
        
        # 統計情報を追加（部門・種別を考慮）
        cat_stats = session.get('category_stats', {})
        for cat, stat in cat_stats.items():
            if cat in category_details:
                # 部門・種別別の統計が必要な場合は履歴から計算
                history = session.get('history', [])
                dept_type_history = [h for h in history 
                                   if h.get('department') == department_id 
                                   and h.get('question_type') == question_type 
                                   and h.get('category') == cat]
                
                total = len(dept_type_history)
                correct = sum(1 for h in dept_type_history if h.get('is_correct', False))
                
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
            'department_categories.html',
            department=department_info,
            question_type=type_info,
            category_details=category_details,
            progresses=progresses,
            total_questions=len(filtered_questions)
        )
        
    except Exception as e:
        logger.error(f"部門別カテゴリ表示エラー: {e}")
        return render_template('error.html', error="カテゴリ表示中にエラーが発生しました。")

@app.route('/department_study/<department>')
def department_study(department):
    """部門特化学習画面 - ユーザーフレンドリーな部門学習インターフェース"""
    try:
        # 部門名を英語キーに変換
        department_key = None
        for key, info in RCCMConfig.DEPARTMENTS.items():
            if info['name'] == department or key == department:
                department_key = key
                break
        
        if not department_key:
            logger.error(f"無効な部門名: {department}")
            return render_template('error.html', error="指定された部門が見つかりません。")
        
        department_info = RCCMConfig.DEPARTMENTS[department_key]
        
        # セッションに部門を保存
        session['selected_department'] = department_key
        session.modified = True
        
        # 問題データを読み込み
        questions = load_questions()
        
        # 4-1基礎問題（全部門共通）の統計
        basic_questions = [q for q in questions if q.get('question_type') == 'basic']
        basic_history = [h for h in session.get('history', []) if h.get('question_type') == 'basic']
        basic_stats = {
            'total_questions': len(basic_questions),
            'answered': len(basic_history),
            'correct': sum(1 for h in basic_history if h.get('is_correct', False)),
            'accuracy': (sum(1 for h in basic_history if h.get('is_correct', False)) / len(basic_history) * 100) if basic_history else 0.0
        }
        
        # 4-2専門問題（選択部門のみ）の統計
        specialist_questions = [q for q in questions 
                              if q.get('question_type') == 'specialist' and q.get('department') == department_key]
        specialist_history = [h for h in session.get('history', []) 
                             if h.get('question_type') == 'specialist' and h.get('department') == department_key]
        specialist_stats = {
            'total_questions': len(specialist_questions),
            'answered': len(specialist_history),
            'correct': sum(1 for h in specialist_history if h.get('is_correct', False)),
            'accuracy': (sum(1 for h in specialist_history if h.get('is_correct', False)) / len(specialist_history) * 100) if specialist_history else 0.0
        }
        
        # 復習対象問題数
        review_questions = [h for h in session.get('history', []) 
                           if not h.get('is_correct', False) and h.get('department') == department_key]
        
        logger.info(f"部門特化学習画面表示: {department} ({department_info['name']})")
        logger.info(f"4-1基礎: {basic_stats['total_questions']}問, 4-2専門: {specialist_stats['total_questions']}問")
        
        return render_template(
            'department_study.html',
            department=department_info,
            department_key=department_key,
            basic_stats=basic_stats,
            specialist_stats=specialist_stats,
            review_count=len(review_questions),
            question_types=RCCMConfig.QUESTION_TYPES
        )
        
    except Exception as e:
        logger.error(f"部門特化学習画面エラー: {e}")
        return render_template('error.html', error="部門学習画面の表示中にエラーが発生しました。")

@app.route('/categories')
def categories():
    """カテゴリ画面（レガシー互換性のため維持）"""
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
    """復習リスト表示（強化版）"""
    try:
        # 復習リストから問題IDを取得
        bookmarks = session.get('bookmarks', [])
        history = session.get('history', [])
        
        if not bookmarks:
            return render_template('review_enhanced.html', 
                                 message="まだ復習問題が登録されていません。問題を解いて間違えた問題が復習リストに追加されます。",
                                 departments=RCCMConfig.DEPARTMENTS)
        
        # 問題データを読み込み
        all_questions = load_questions()
        questions = []
        
        # 間違い回数の統計を取得
        error_counts = {}
        for record in history:
            if not record.get('is_correct', True):  # 間違えた問題のみ
                qid = str(record.get('question_id', ''))
                error_counts[qid] = error_counts.get(qid, 0) + 1
        
        # 復習問題の詳細情報を作成
        departments = set()
        many_errors_count = 0
        
        for qid in bookmarks:
            question = next((q for q in all_questions if str(q.get('id', '')) == str(qid)), None)
            if question:
                error_count = error_counts.get(str(qid), 1)
                if error_count >= 3:
                    many_errors_count += 1
                
                # 部門名を取得
                dept_key = question.get('department', '')
                dept_name = ''
                if dept_key:
                    dept_info = RCCMConfig.DEPARTMENTS.get(dept_key, {})
                    dept_name = dept_info.get('name', dept_key)
                    departments.add(dept_key)
                
                # 最終挑戦日を取得
                last_attempted = ''
                for record in reversed(history):
                    if str(record.get('question_id', '')) == str(qid):
                        last_attempted = record.get('timestamp', '')[:10] if record.get('timestamp') else ''
                        break
                
                questions.append({
                    'id': question.get('id'),
                    'question': question.get('question', ''),
                    'category': question.get('category', ''),
                    'department_name': dept_name,
                    'year': question.get('year'),
                    'error_count': error_count,
                    'last_attempted': last_attempted
                })
        
        # 統計情報を計算
        total_count = len(questions)
        department_count = len(departments)
        
        # 直近の正答率を計算（最新20問）
        recent_history = history[-20:] if len(history) >= 20 else history
        correct_rate = 0
        if recent_history:
            correct_count = sum(1 for h in recent_history if h.get('is_correct', False))
            correct_rate = correct_count / len(recent_history)
        
        return render_template('review_enhanced.html',
                             questions=questions,
                             total_count=total_count,
                             many_errors_count=many_errors_count,
                             department_count=department_count,
                             correct_rate=correct_rate,
                             departments=RCCMConfig.DEPARTMENTS)
        
    except Exception as e:
        logger.error(f"復習リスト表示エラー: {e}")
        return render_template('error.html', error="復習リスト表示中にエラーが発生しました。")

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

@app.route('/api/review/remove', methods=['POST'])
def remove_from_review():
    """復習リストから問題を削除"""
    try:
        data = request.get_json()
        question_id = str(data.get('question_id', ''))
        
        if not question_id:
            return jsonify({'success': False, 'error': '問題IDが指定されていません'})
        
        bookmarks = session.get('bookmarks', [])
        if question_id in bookmarks:
            bookmarks.remove(question_id)
            session['bookmarks'] = bookmarks
            session.modified = True
            logger.info(f"復習リストから削除: 問題ID {question_id}")
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': '復習リストに存在しません'})
            
    except Exception as e:
        logger.error(f"復習問題削除エラー: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/review/bulk_remove', methods=['POST'])
def bulk_remove_from_review():
    """復習リストから複数問題を削除"""
    try:
        data = request.get_json()
        question_ids = data.get('question_ids', [])
        
        if not question_ids:
            return jsonify({'success': False, 'error': '問題IDが指定されていません'})
        
        bookmarks = session.get('bookmarks', [])
        removed_count = 0
        
        for qid in question_ids:
            qid_str = str(qid)
            if qid_str in bookmarks:
                bookmarks.remove(qid_str)
                removed_count += 1
        
        session['bookmarks'] = bookmarks
        session.modified = True
        
        logger.info(f"復習リストから一括削除: {removed_count}問")
        return jsonify({'success': True, 'removed_count': removed_count})
        
    except Exception as e:
        logger.error(f"復習問題一括削除エラー: {e}")
        return jsonify({'success': False, 'error': str(e)})

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
    """AI弱点分析画面（部門別対応版）"""
    try:
        # 部門フィルタを取得
        department_filter = request.args.get('department')
        
        # AI分析実行（部門別）
        analysis_result = ai_analyzer.analyze_weak_areas(session, department_filter)
        
        # 推奨学習モード取得
        recommended_mode = adaptive_engine.get_learning_mode_recommendation(session, analysis_result)
        
        # 利用可能な部門リスト
        available_departments = {}
        history = session.get('history', [])
        for entry in history:
            dept = entry.get('department')
            if dept and dept in RCCMConfig.DEPARTMENTS:
                if dept not in available_departments:
                    available_departments[dept] = {'count': 0, 'name': RCCMConfig.DEPARTMENTS[dept]['name']}
                available_departments[dept]['count'] += 1
        
        return render_template(
            'ai_analysis.html',
            analysis=analysis_result,
            recommended_mode=recommended_mode,
            learning_modes=adaptive_engine.learning_modes,
            available_departments=available_departments,
            current_department=department_filter,
            departments=RCCMConfig.DEPARTMENTS
        )
        
    except Exception as e:
        logger.error(f"AI分析エラー: {e}")
        return render_template('error.html', error="AI分析の表示中にエラーが発生しました。")

@app.route('/adaptive_quiz')
def adaptive_quiz():
    """アダプティブ問題練習モード（部門別対応版）"""
    try:
        learning_mode = request.args.get('mode', 'balanced')
        session_size = int(request.args.get('size', QuizConfig.QUESTIONS_PER_SESSION))
        department = request.args.get('department', session.get('selected_department', ''))
        
        all_questions = load_questions()
        if not all_questions:
            return render_template('error.html', error="問題データが存在しません。")
        
        # AI分析実行（部門フィルタ適用）
        ai_analysis = ai_analyzer.analyze_weak_areas(session, department)
        
        # アダプティブ問題選択（部門対応）
        adaptive_questions = adaptive_engine.get_adaptive_questions(
            session, all_questions, ai_analysis, session_size, learning_mode, department
        )
        
        if not adaptive_questions:
            return render_template('error.html', error="選択可能な問題がありません。")
        
        # アダプティブセッション開始（部門情報も保存）
        question_ids = [int(q.get('id', 0)) for q in adaptive_questions]
        session['quiz_question_ids'] = question_ids
        session['quiz_current'] = 0
        
        # カテゴリ名を部門別に調整
        category_name = 'AI適応学習'
        if department:
            dept_name = RCCMConfig.DEPARTMENTS.get(department, {}).get('name', department)
            category_name = f'AI適応学習 ({dept_name})'
        
        session['quiz_category'] = category_name
        session['adaptive_mode'] = learning_mode
        if department:
            session['selected_department'] = department
        session.modified = True
        
        logger.info(f"アダプティブ問題開始: {len(question_ids)}問, モード: {learning_mode}, 部門: {department or '全体'}")
        
        # 最初の問題を表示
        return redirect(url_for('quiz'))
        
    except Exception as e:
        logger.error(f"アダプティブ問題エラー: {e}")
        return render_template('error.html', error="アダプティブ問題の開始中にエラーが発生しました。")

@app.route('/integrated_learning')
def integrated_learning():
    """4-1基礎と4-2専門の連携学習モード"""
    try:
        # パラメータ取得
        learning_mode = request.args.get('mode', 'basic_to_specialist')
        session_size = int(request.args.get('size', QuizConfig.QUESTIONS_PER_SESSION))
        department = request.args.get('department', session.get('selected_department', ''))
        
        # 連携学習モードの検証
        if learning_mode not in ['basic_to_specialist', 'foundation_reinforced']:
            learning_mode = 'basic_to_specialist'
        
        all_questions = load_questions()
        if not all_questions:
            return render_template('error.html', error="問題データが存在しません。")
        
        # 基礎理解度を事前評価
        foundation_mastery = adaptive_engine._assess_foundation_mastery(session, department)
        
        # AI分析実行（部門フィルタ適用）
        ai_analysis = ai_analyzer.analyze_weak_areas(session, department)
        
        # 連携学習用問題選択
        integrated_questions = adaptive_engine.get_adaptive_questions(
            session, all_questions, ai_analysis, session_size, learning_mode, department
        )
        
        if not integrated_questions:
            return render_template('error.html', error="選択可能な問題がありません。")
        
        # 連携学習セッション開始
        question_ids = [int(q.get('id', 0)) for q in integrated_questions]
        session['quiz_question_ids'] = question_ids
        session['quiz_current'] = 0
        
        # カテゴリ名設定
        mode_names = {
            'basic_to_specialist': '基礎→専門連携学習',
            'foundation_reinforced': '基礎強化学習'
        }
        category_name = mode_names.get(learning_mode, '連携学習')
        
        if department:
            dept_name = RCCMConfig.DEPARTMENTS.get(department, {}).get('name', department)
            category_name = f'{category_name} ({dept_name})'
        
        session['quiz_category'] = category_name
        session['adaptive_mode'] = learning_mode
        session['foundation_mastery'] = foundation_mastery
        if department:
            session['selected_department'] = department
        session.modified = True
        
        logger.info(f"連携学習開始: {len(question_ids)}問, モード: {learning_mode}, 部門: {department or '全体'}, 基礎習熟度: {foundation_mastery:.2f}")
        
        # 最初の問題を表示
        return redirect(url_for('quiz'))
        
    except Exception as e:
        logger.error(f"連携学習エラー: {e}")
        return render_template('error.html', error="連携学習の開始中にエラーが発生しました。")

@app.route('/integrated_learning_selection')
def integrated_learning_selection():
    """連携学習モード選択画面"""
    try:
        department = request.args.get('department', session.get('selected_department', ''))
        
        # 現在の基礎理解度を評価
        foundation_mastery = adaptive_engine._assess_foundation_mastery(session, department)
        
        # 部門情報
        departments = RCCMConfig.DEPARTMENTS
        department_patterns = adaptive_engine.department_learning_patterns
        
        return render_template(
            'integrated_learning_selection.html',
            foundation_mastery=foundation_mastery,
            department=department,
            departments=departments,
            department_patterns=department_patterns,
            title='連携学習モード選択'
        )
        
    except Exception as e:
        logger.error(f"連携学習選択画面エラー: {e}")
        return render_template('error.html', error="連携学習選択画面の表示中にエラーが発生しました。")

@app.route('/learner_insights')
def learner_insights():
    """学習者インサイト画面（動的難易度制御情報を含む）"""
    try:
        department = request.args.get('department', session.get('selected_department', ''))
        
        # 学習者インサイト取得
        insights = adaptive_engine.get_learner_insights(session, department)
        
        # 部門情報
        departments = RCCMConfig.DEPARTMENTS
        
        return render_template(
            'learner_insights.html',
            insights=insights,
            department=department,
            departments=departments,
            title='学習者レベル・インサイト'
        )
        
    except Exception as e:
        logger.error(f"学習者インサイト画面エラー: {e}")
        return render_template('error.html', error="学習者インサイト画面の表示中にエラーが発生しました。")

@app.route('/api/difficulty/status')
def api_difficulty_status():
    """動的難易度制御状態のAPI"""
    try:
        department = request.args.get('department')
        
        # 学習者レベル評価
        from difficulty_controller import difficulty_controller
        learner_assessment = difficulty_controller.assess_learner_level(session, department)
        
        # 最近のパフォーマンス
        recent_history = session.get('history', [])[-10:]
        if recent_history:
            recent_performance = difficulty_controller._analyze_current_performance(recent_history)
        else:
            recent_performance = {'accuracy': 0, 'avg_time': 0, 'sample_size': 0, 'trend': 'unknown'}
        
        # 動的セッション設定
        dynamic_config = session.get('dynamic_session_config', {})
        
        return jsonify({
            'learner_level': learner_assessment['overall_level'],
            'level_name': learner_assessment['level_name'],
            'confidence': learner_assessment['confidence'],
            'recent_performance': recent_performance,
            'dynamic_config': dynamic_config,
            'recommended_difficulty': learner_assessment['recommended_difficulty'],
            'department_factor': learner_assessment.get('department_factor', 1.0),
            'next_adjustment_threshold': learner_assessment.get('next_adjustment_threshold', 20),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"難易度制御状態API エラー: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/learning_optimization')
def learning_optimization():
    """学習効率最適化画面"""
    try:
        # 個人学習パターン分析
        learning_pattern = learning_optimizer.analyze_personal_learning_pattern(session)
        
        # 最適学習時間推奨
        optimization_data = learning_optimizer.get_optimal_study_time_recommendation(session)
        
        return render_template(
            'learning_optimization.html',
            learning_pattern=learning_pattern,
            optimization_data=optimization_data,
            title='学習効率最適化'
        )
        
    except Exception as e:
        logger.error(f"学習効率最適化画面エラー: {e}")
        return render_template('error.html', error="学習効率最適化画面の表示中にエラーが発生しました。")

@app.route('/api/learning/realtime_tracking', methods=['POST'])
def api_realtime_learning_tracking():
    """リアルタイム学習効率追跡API"""
    try:
        data = request.get_json()
        session_start_time = data.get('session_start_time')
        
        if session_start_time:
            session_start = datetime.fromisoformat(session_start_time)
        else:
            session_start = datetime.now()
        
        current_session_data = {
            'start_time': session_start,
            'question_count': data.get('question_count', 0)
        }
        
        tracking_result = learning_optimizer.track_real_time_efficiency(session, current_session_data)
        
        return jsonify({
            'success': True,
            'tracking_data': tracking_result,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"リアルタイム学習追跡API エラー: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/learning/biorhythm', methods=['POST'])
def api_biorhythm_calculation():
    """バイオリズム計算API"""
    try:
        data = request.get_json()
        birth_date = data.get('birth_date')
        target_date_str = data.get('target_date')
        
        if not birth_date:
            return jsonify({'success': False, 'error': '生年月日が必要です'}), 400
        
        # セッションに生年月日を保存
        session['birth_date'] = birth_date
        session.modified = True
        
        target_date = datetime.now()
        if target_date_str:
            target_date = datetime.fromisoformat(target_date_str)
        
        biorhythm_scores = learning_optimizer.calculate_biorhythm_score(birth_date, target_date)
        
        # 今後7日間のバイオリズム予測
        future_biorhythms = {}
        for i in range(7):
            future_date = target_date + timedelta(days=i)
            future_scores = learning_optimizer.calculate_biorhythm_score(birth_date, future_date)
            future_biorhythms[future_date.strftime('%Y-%m-%d')] = future_scores
        
        return jsonify({
            'success': True,
            'current_biorhythm': biorhythm_scores,
            'future_biorhythms': future_biorhythms,
            'birth_date': birth_date,
            'target_date': target_date.strftime('%Y-%m-%d')
        })
        
    except Exception as e:
        logger.error(f"バイオリズム計算API エラー: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/learning/optimal_schedule')
def api_optimal_schedule():
    """最適学習スケジュールAPI"""
    try:
        target_date = request.args.get('date')
        if target_date:
            target_datetime = datetime.strptime(target_date, '%Y-%m-%d')
        else:
            target_datetime = datetime.now()
        
        recommendation = learning_optimizer.get_optimal_study_time_recommendation(session, target_datetime)
        
        return jsonify({
            'success': True,
            'recommendation': recommendation,
            'generated_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"最適スケジュールAPI エラー: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/ai_analysis', methods=['GET'])
def api_ai_analysis():
    """AI分析結果のAPI（部門別対応版）"""
    try:
        department_filter = request.args.get('department')
        
        analysis_result = ai_analyzer.analyze_weak_areas(session, department_filter)
        recommended_mode = adaptive_engine.get_learning_mode_recommendation(session, analysis_result)
        
        return jsonify({
            'analysis': analysis_result,
            'recommended_mode': recommended_mode,
            'department_filter': department_filter,
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

# === 管理者ダッシュボード ===

@app.route('/admin')
def admin_dashboard_page():
    """管理者ダッシュボードメイン"""
    try:
        # 全データを取得
        overview = admin_dashboard.get_system_overview()
        questions = admin_dashboard.get_question_management_data()
        users = admin_dashboard.get_user_progress_overview()
        content = admin_dashboard.get_content_analytics()
        performance = admin_dashboard.get_performance_metrics()
        
        return render_template('admin_dashboard.html',
                             overview=overview,
                             questions=questions,
                             users=users,
                             content=content,
                             performance=performance,
                             data={
                                 'overview': overview,
                                 'questions': questions,
                                 'users': users,
                                 'content': content,
                                 'performance': performance
                             })
    except Exception as e:
        logger.error(f"管理者ダッシュボードエラー: {e}")
        return render_template('error.html', error="ダッシュボードの読み込み中にエラーが発生しました")

@app.route('/admin/api/overview')
def admin_api_overview():
    """システム概要API"""
    try:
        overview = admin_dashboard.get_system_overview()
        return jsonify(overview)
    except Exception as e:
        logger.error(f"概要API エラー: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/admin/api/questions')
def admin_api_questions():
    """問題管理API"""
    try:
        questions = admin_dashboard.get_question_management_data()
        return jsonify(questions)
    except Exception as e:
        logger.error(f"問題管理API エラー: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/admin/api/users')
def admin_api_users():
    """ユーザー管理API"""
    try:
        users = admin_dashboard.get_user_progress_overview()
        return jsonify(users)
    except Exception as e:
        logger.error(f"ユーザー管理API エラー: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/admin/api/users/<user_id>')
def admin_api_user_detail(user_id):
    """ユーザー詳細API"""
    try:
        user_detail = admin_dashboard.get_detailed_user_analysis(user_id)
        return jsonify(user_detail)
    except Exception as e:
        logger.error(f"ユーザー詳細API エラー: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/admin/api/content')
def admin_api_content():
    """コンテンツ分析API"""
    try:
        content = admin_dashboard.get_content_analytics()
        return jsonify(content)
    except Exception as e:
        logger.error(f"コンテンツ分析API エラー: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/admin/api/performance')
def admin_api_performance():
    """パフォーマンス指標API"""
    try:
        performance = admin_dashboard.get_performance_metrics()
        return jsonify(performance)
    except Exception as e:
        logger.error(f"パフォーマンス指標API エラー: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/admin/api/reports/<report_type>')
def admin_api_reports(report_type):
    """レポート生成API"""
    try:
        if report_type not in ['comprehensive', 'users', 'content', 'performance']:
            return jsonify({'error': 'Invalid report type'}), 400
        
        report = admin_dashboard.generate_reports(report_type)
        return jsonify(report)
    except Exception as e:
        logger.error(f"レポート生成API エラー: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/admin/api/refresh')
def admin_api_refresh():
    """データ更新API"""
    try:
        # キャッシュをクリア
        global _questions_cache, _cache_timestamp
        _questions_cache = None
        _cache_timestamp = None
        
        # 新しい管理者ダッシュボードインスタンスを作成
        from admin_dashboard import AdminDashboard
        global admin_dashboard
        admin_dashboard = AdminDashboard()
        
        return jsonify({'success': True, 'message': 'データが更新されました'})
    except Exception as e:
        logger.error(f"データ更新API エラー: {e}")
        return jsonify({'error': str(e)}), 500

# === ソーシャル学習機能 ===

@app.route('/social')
def social_learning_page():
    """ソーシャル学習メインページ"""
    try:
        user_id = session.get('user_id', 'anonymous')
        
        # ユーザーの参加グループ取得
        user_groups = social_learning_manager.get_user_groups(user_id)
        
        # おすすめグループ取得
        recommended_groups = social_learning_manager.discover_groups(user_id, limit=6)
        
        # ディスカッション一覧取得
        discussions = social_learning_manager.get_discussions(limit=10)
        
        # ピア比較データ取得（エラーハンドリング強化）
        try:
            peer_comparison = social_learning_manager.get_peer_comparison(user_id, 'department')
            # エラーレスポンスの場合、Noneに設定
            if isinstance(peer_comparison, dict) and 'error' in peer_comparison:
                peer_comparison = None
        except Exception as e:
            logger.warning(f"ピア比較データ取得エラー: {e}")
            peer_comparison = None
        
        # リーダーボード取得
        leaderboard = social_learning_manager.get_leaderboard(time_period='month')
        
        return render_template('social_learning.html',
                             user_groups=user_groups,
                             recommended_groups=recommended_groups,
                             discussions=discussions,
                             peer_comparison=peer_comparison,
                             leaderboard=leaderboard)
    
    except Exception as e:
        logger.error(f"ソーシャル学習ページエラー: {e}")
        return render_template('error.html', error="ソーシャル学習ページの読み込み中にエラーが発生しました")

@app.route('/social/create_group', methods=['POST'])
def create_study_group():
    """学習グループ作成"""
    try:
        user_id = session.get('user_id', 'anonymous')
        
        group_name = request.form.get('group_name')
        description = request.form.get('description', '')
        department = request.form.get('department')
        target_exam_date = request.form.get('target_exam_date')
        
        if not group_name:
            return jsonify({'success': False, 'error': 'グループ名は必須です'})
        
        result = social_learning_manager.create_study_group(
            user_id, group_name, description, department, target_exam_date
        )
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"グループ作成エラー: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/social/join_group', methods=['POST'])
def join_study_group():
    """学習グループ参加"""
    try:
        user_id = session.get('user_id', 'anonymous')
        group_id = request.form.get('group_id')
        
        if not group_id:
            return jsonify({'success': False, 'error': 'グループIDが必要です'})
        
        result = social_learning_manager.join_group(user_id, group_id)
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"グループ参加エラー: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/social/leave_group', methods=['POST'])
def leave_study_group():
    """学習グループ退会"""
    try:
        user_id = session.get('user_id', 'anonymous')
        group_id = request.form.get('group_id')
        
        if not group_id:
            return jsonify({'success': False, 'error': 'グループIDが必要です'})
        
        result = social_learning_manager.leave_group(user_id, group_id)
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"グループ退会エラー: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/social/create_discussion', methods=['POST'])
def create_discussion():
    """ディスカッション作成"""
    try:
        user_id = session.get('user_id', 'anonymous')
        
        title = request.form.get('title')
        content = request.form.get('content')
        category = request.form.get('category', 'general')
        question_id = request.form.get('question_id')
        group_id = request.form.get('group_id')
        
        if not title or not content:
            return jsonify({'success': False, 'error': 'タイトルと内容は必須です'})
        
        # question_idを整数に変換（存在する場合）
        if question_id:
            try:
                question_id = int(question_id)
            except ValueError:
                question_id = None
        
        result = social_learning_manager.create_discussion(
            user_id, title, content, question_id, group_id, category
        )
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"ディスカッション作成エラー: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/social/discussion/<discussion_id>')
def discussion_detail(discussion_id):
    """ディスカッション詳細"""
    try:
        user_id = session.get('user_id', 'anonymous')
        discussion = social_learning_manager.get_discussion_detail(discussion_id, user_id)
        
        if 'error' in discussion:
            return render_template('error.html', error=discussion['error'])
        
        return render_template('discussion_detail.html', discussion=discussion)
    
    except Exception as e:
        logger.error(f"ディスカッション詳細エラー: {e}")
        return render_template('error.html', error="ディスカッション詳細の読み込み中にエラーが発生しました")

@app.route('/social/peer_comparison')
def peer_comparison():
    """ピア比較API"""
    try:
        user_id = session.get('user_id', 'anonymous')
        comparison_type = request.args.get('type', 'department')
        
        result = social_learning_manager.get_peer_comparison(user_id, comparison_type)
        
        # HTMLレスポンスとして返す（AJAX用）
        return render_template('peer_comparison_partial.html', peer_comparison=result)
    
    except Exception as e:
        logger.error(f"ピア比較エラー: {e}")
        return f'<div class="alert alert-danger">エラー: {str(e)}</div>'

@app.route('/social/leaderboard')
def leaderboard():
    """リーダーボードAPI"""
    try:
        period = request.args.get('period', 'month')
        department = request.args.get('department')
        
        result = social_learning_manager.get_leaderboard(department, period)
        
        # HTMLレスポンスとして返す（AJAX用）
        return render_template('leaderboard_partial.html', leaderboard=result, period=period)
    
    except Exception as e:
        logger.error(f"リーダーボードエラー: {e}")
        return f'<div class="alert alert-danger">エラー: {str(e)}</div>'

@app.route('/social/study_partners')
def study_partners():
    """学習パートナー推奨"""
    try:
        user_id = session.get('user_id', 'anonymous')
        partners = social_learning_manager.get_recommended_study_partners(user_id)
        
        return jsonify(partners)
    
    except Exception as e:
        logger.error(f"学習パートナー推奨エラー: {e}")
        return jsonify({'error': str(e)}), 500

# ========================
# API統合・プロフェッショナル機能
# ========================

@app.route('/api_integration')
def api_integration_dashboard():
    """API統合ダッシュボード"""
    try:
        # API統合データ取得
        api_keys = api_manager._load_api_keys()
        certifications = api_manager._load_certifications()
        organizations = api_manager._load_organizations()
        
        # APIキー一覧を整形
        formatted_api_keys = []
        for key, info in api_keys.items():
            formatted_api_keys.append({
                'api_key': key,
                'organization': info['organization'],
                'permissions': info['permissions'],
                'created_at': info['created_at'],
                'is_active': info['is_active'],
                'usage_stats': info['usage_stats']
            })
        
        # 認定プログラム一覧を整形
        formatted_certifications = []
        for cert_id, cert_info in certifications.items():
            formatted_certifications.append({
                'id': cert_id,
                'name': cert_info['name'],
                'description': cert_info['description'],
                'requirements': cert_info['requirements'],
                'statistics': cert_info['statistics']
            })
        
        # 組織一覧を整形
        formatted_organizations = []
        for org_id, org_info in organizations.items():
            formatted_organizations.append({
                'id': org_id,
                'name': org_info['name'],
                'description': org_info['description'],
                'statistics': org_info['statistics']
            })
        
        # 認定サマリー計算
        certifications_summary = {
            'total_programs': len(certifications),
            'total_participants': sum(cert['statistics']['total_participants'] for cert in certifications.values()),
            'completion_rate': sum(cert['statistics']['completion_rate'] for cert in certifications.values()) / len(certifications) if certifications else 0
        }
        
        return render_template('api_integration.html',
                             api_keys=formatted_api_keys,
                             certification_programs=formatted_certifications,
                             certifications_summary=certifications_summary,
                             organizations=formatted_organizations,
                             generated_reports=[])  # TODO: 実装
        
    except Exception as e:
        logger.error(f"API統合ダッシュボードエラー: {e}")
        return render_template('error.html', error=str(e))

# === API認証エンドポイント ===

@app.route('/api/auth/generate_key', methods=['POST'])
def generate_api_key():
    """APIキー生成"""
    try:
        data = request.get_json()
        organization = data.get('organization')
        permissions = data.get('permissions', [])
        expires_in_days = data.get('expires_in_days', 365)
        
        if not organization:
            return jsonify({'success': False, 'error': '組織名が必要です'}), 400
        
        result = api_manager.generate_api_key(organization, permissions, expires_in_days)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"APIキー生成エラー: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/auth/validate_key', methods=['POST'])
def validate_api_key():
    """APIキー検証"""
    try:
        data = request.get_json()
        api_key = data.get('api_key')
        required_permission = data.get('required_permission')
        
        if not api_key:
            return jsonify({'valid': False, 'error': 'APIキーが必要です'}), 400
        
        result = api_manager.validate_api_key(api_key, required_permission)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"APIキー検証エラー: {e}")
        return jsonify({'valid': False, 'error': str(e)}), 500

@app.route('/api/auth/revoke_key', methods=['DELETE'])
def revoke_api_key():
    """APIキー無効化"""
    try:
        data = request.get_json()
        api_key = data.get('api_key')
        
        if not api_key:
            return jsonify({'success': False, 'error': 'APIキーが必要です'}), 400
        
        result = api_manager.revoke_api_key(api_key)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"APIキー無効化エラー: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# === ユーザー管理API ===

@app.route('/api/users', methods=['GET'])
def api_users_list():
    """ユーザー一覧API"""
    try:
        # API認証チェック
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return jsonify({'error': 'API key required'}), 401
        
        validation = api_manager.validate_api_key(api_key, 'read_users')
        if not validation['valid']:
            return jsonify({'error': validation['error']}), 401
        
        # 全ユーザーデータ取得（簡略化）
        all_users = api_manager._load_all_user_data()
        
        users_list = []
        for user_id, user_data in all_users.items():
            history = user_data.get('history', [])
            users_list.append({
                'user_id': user_id,
                'total_questions': len(history),
                'accuracy': sum(1 for h in history if h.get('is_correct', False)) / len(history) if history else 0,
                'last_activity': max([h.get('date', '') for h in history], default=''),
                'primary_department': api_manager._get_user_primary_departments(user_data)[0] if history else 'unknown'
            })
        
        return jsonify({
            'users': users_list,
            'total_count': len(users_list),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"ユーザー一覧API エラー: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/users/<user_id>/progress', methods=['GET'])
def api_user_progress(user_id):
    """ユーザー進捗API"""
    try:
        # API認証チェック
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return jsonify({'error': 'API key required'}), 401
        
        validation = api_manager.validate_api_key(api_key, 'read_progress')
        if not validation['valid']:
            return jsonify({'error': validation['error']}), 401
        
        # 進捗レポート生成
        time_period = request.args.get('period', 'month')
        report_format = request.args.get('format', 'json')
        
        report = api_manager.generate_progress_report(user_id, None, time_period, report_format)
        
        return jsonify(report)
        
    except Exception as e:
        logger.error(f"ユーザー進捗API エラー: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/users/<user_id>/certifications', methods=['GET'])
def api_user_certifications(user_id):
    """ユーザー認定情報API"""
    try:
        # API認証チェック
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return jsonify({'error': 'API key required'}), 401
        
        validation = api_manager.validate_api_key(api_key, 'read_users')
        if not validation['valid']:
            return jsonify({'error': validation['error']}), 401
        
        user_data = api_manager._load_user_data(user_id)
        certifications = user_data.get('certifications', {})
        
        # 各認定の詳細情報を取得
        detailed_certifications = []
        for cert_id, enrollment in certifications.items():
            cert_progress = api_manager.check_certification_progress(user_id, cert_id)
            detailed_certifications.append(cert_progress)
        
        return jsonify({
            'user_id': user_id,
            'certifications': detailed_certifications,
            'total_certifications': len(detailed_certifications),
            'completed_certifications': len([c for c in detailed_certifications if c.get('enrollment_status') == 'completed'])
        })
        
    except Exception as e:
        logger.error(f"ユーザー認定情報API エラー: {e}")
        return jsonify({'error': str(e)}), 500

# === 進捗レポートAPI ===

@app.route('/api/reports/progress', methods=['GET'])
def api_progress_reports():
    """進捗レポートAPI"""
    try:
        # API認証チェック
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return jsonify({'error': 'API key required'}), 401
        
        validation = api_manager.validate_api_key(api_key, 'generate_reports')
        if not validation['valid']:
            return jsonify({'error': validation['error']}), 401
        
        user_id = request.args.get('user_id')
        organization = request.args.get('organization')
        time_period = request.args.get('period', 'month')
        report_format = request.args.get('format', 'json')
        
        report = api_manager.generate_progress_report(user_id, organization, time_period, report_format)
        
        return jsonify(report)
        
    except Exception as e:
        logger.error(f"進捗レポートAPI エラー: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/reports/organization/<org_id>', methods=['GET'])
def api_organization_report(org_id):
    """組織レポートAPI"""
    try:
        # API認証チェック
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return jsonify({'error': 'API key required'}), 401
        
        validation = api_manager.validate_api_key(api_key, 'generate_reports')
        if not validation['valid']:
            return jsonify({'error': validation['error']}), 401
        
        time_period = request.args.get('period', 'month')
        report_format = request.args.get('format', 'json')
        
        report = api_manager._generate_organization_report(org_id, time_period, report_format)
        
        return jsonify(report)
        
    except Exception as e:
        logger.error(f"組織レポートAPI エラー: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/reports/export/<format>', methods=['GET'])
def api_export_analytics(format):
    """学習分析エクスポートAPI"""
    try:
        # API認証チェック
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return jsonify({'error': 'API key required'}), 401
        
        validation = api_manager.validate_api_key(api_key, 'generate_reports')
        if not validation['valid']:
            return jsonify({'error': validation['error']}), 401
        
        include_personal = request.args.get('include_personal_data', 'false').lower() == 'true'
        
        result = api_manager.export_learning_analytics(format, include_personal)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"学習分析エクスポートAPI エラー: {e}")
        return jsonify({'error': str(e)}), 500

# === 認定管理API ===

@app.route('/api/certifications', methods=['GET', 'POST'])
def api_certifications():
    """認定プログラムAPI"""
    try:
        if request.method == 'GET':
            # 認定プログラム一覧取得
            certifications = api_manager._load_certifications()
            return jsonify({
                'certifications': list(certifications.values()),
                'total_count': len(certifications)
            })
        
        elif request.method == 'POST':
            # API認証チェック
            api_key = request.headers.get('X-API-Key')
            if not api_key:
                return jsonify({'error': 'API key required'}), 401
            
            validation = api_manager.validate_api_key(api_key, 'manage_certifications')
            if not validation['valid']:
                return jsonify({'error': validation['error']}), 401
            
            # 認定プログラム作成
            data = request.get_json()
            name = data.get('name')
            description = data.get('description')
            requirements = data.get('requirements', {})
            organization = data.get('organization')
            
            result = api_manager.create_certification_program(name, description, requirements, organization)
            
            return jsonify(result)
        
    except Exception as e:
        logger.error(f"認定プログラムAPI エラー: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/certifications/<cert_id>/progress', methods=['GET'])
def api_certification_progress(cert_id):
    """認定進捗API"""
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({'error': 'user_id required'}), 400
        
        progress = api_manager.check_certification_progress(user_id, cert_id)
        
        return jsonify(progress)
        
    except Exception as e:
        logger.error(f"認定進捗API エラー: {e}")
        return jsonify({'error': str(e)}), 500

# === 組織管理API ===

@app.route('/api/organizations', methods=['GET', 'POST'])
def api_organizations():
    """組織管理API"""
    try:
        if request.method == 'GET':
            # 組織一覧取得
            organizations = api_manager._load_organizations()
            return jsonify({
                'organizations': list(organizations.values()),
                'total_count': len(organizations)
            })
        
        elif request.method == 'POST':
            # API認証チェック
            api_key = request.headers.get('X-API-Key')
            if not api_key:
                return jsonify({'error': 'API key required'}), 401
            
            validation = api_manager.validate_api_key(api_key, 'manage_organizations')
            if not validation['valid']:
                return jsonify({'error': validation['error']}), 401
            
            # 組織作成
            data = request.get_json()
            name = data.get('name')
            description = data.get('description')
            settings = data.get('settings', {})
            
            result = api_manager.create_organization(name, description, settings)
            
            return jsonify(result)
        
    except Exception as e:
        logger.error(f"組織管理API エラー: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/organizations/<org_id>/users', methods=['GET'])
def api_organization_users(org_id):
    """組織ユーザー一覧API"""
    try:
        organizations = api_manager._load_organizations()
        
        if org_id not in organizations:
            return jsonify({'error': 'Organization not found'}), 404
        
        org_users = organizations[org_id]['users']
        
        # ユーザー詳細情報を取得
        users_details = []
        for user_id in org_users:
            user_data = api_manager._load_user_data(user_id)
            history = user_data.get('history', [])
            
            users_details.append({
                'user_id': user_id,
                'total_questions': len(history),
                'accuracy': sum(1 for h in history if h.get('is_correct', False)) / len(history) if history else 0,
                'last_activity': max([h.get('date', '') for h in history], default='')
            })
        
        return jsonify({
            'organization_id': org_id,
            'users': users_details,
            'total_users': len(users_details)
        })
        
    except Exception as e:
        logger.error(f"組織ユーザー一覧API エラー: {e}")
        return jsonify({'error': str(e)}), 500

# === 高度な個人化API ===

@app.route('/api/personalization/profile/<user_id>')
def api_personalization_profile(user_id):
    """個人化プロファイルAPI"""
    try:
        profile = advanced_personalization.analyze_user_profile(user_id)
        
        return jsonify({
            'user_id': user_id,
            'profile': profile,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"個人化プロファイルAPI エラー: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/personalization/recommendations/<user_id>')
def api_personalization_recommendations(user_id):
    """ML推薦API"""
    try:
        context = request.args.to_dict()
        recommendations = advanced_personalization.get_ml_recommendations(user_id, context)
        
        return jsonify({
            'user_id': user_id,
            'recommendations': recommendations,
            'context': context,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"ML推薦API エラー: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/personalization/ui/<user_id>')
def api_personalization_ui(user_id):
    """UI個人化API"""
    try:
        ui_customizations = advanced_personalization.customize_ui(user_id)
        
        return jsonify({
            'user_id': user_id,
            'ui_customizations': ui_customizations,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"UI個人化API エラー: {e}")
        return jsonify({'error': str(e)}), 500

# 初期化
try:
    initial_questions = load_questions()
    logger.info(f"アプリケーション初期化完了: {len(initial_questions)}問読み込み")
except Exception as e:
    logger.error(f"アプリケーション初期化エラー: {e}")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)