#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
【ULTRATHIN区 PHASE 2-2-2】基礎科目専用Blueprint実装
Flask Blueprint基礎科目専用ルートハンドラー
URL: /v2/basic_exam/* プレフィックス
既存システム完全非干渉・新ファイル作成のみ
"""

from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify
import uuid
from datetime import datetime
import random

# 基礎科目専用Blueprint定義
basic_exam_bp = Blueprint(
    'basic_exam',
    __name__,
    url_prefix='/v2/basic_exam',
    template_folder='templates/v2/basic_exam',
    static_folder='static/v2/basic_exam'
)

# 基礎科目専用セッションキープレフィックス
BASIC_EXAM_SESSION_PREFIX = 'basic_exam_'

def get_basic_exam_session_key(key):
    """基礎科目専用セッションキー生成"""
    return f"{BASIC_EXAM_SESSION_PREFIX}{key}"

def init_basic_exam_session():
    """基礎科目専用セッション初期化"""
    session_id = str(uuid.uuid4())
    session[get_basic_exam_session_key('session_id')] = session_id
    session[get_basic_exam_session_key('start_time')] = datetime.now().isoformat()
    session[get_basic_exam_session_key('current_question')] = 0
    session[get_basic_exam_session_key('answers')] = {}
    session[get_basic_exam_session_key('questions')] = []
    return session_id

def get_basic_exam_session_data():
    """基礎科目専用セッションデータ取得"""
    return {
        'session_id': session.get(get_basic_exam_session_key('session_id')),
        'start_time': session.get(get_basic_exam_session_key('start_time')),
        'current_question': session.get(get_basic_exam_session_key('current_question'), 0),
        'answers': session.get(get_basic_exam_session_key('answers'), {}),
        'questions': session.get(get_basic_exam_session_key('questions'), [])
    }

def clear_basic_exam_session():
    """基礎科目専用セッションクリア"""
    keys_to_remove = [key for key in session.keys() if key.startswith(BASIC_EXAM_SESSION_PREFIX)]
    for key in keys_to_remove:
        session.pop(key, None)

@basic_exam_bp.route('/')
def basic_exam_index():
    """基礎科目専用トップページ"""
    try:
        # 既存セッションクリア
        clear_basic_exam_session()
        
        return render_template('basic_exam_index.html', {
            'title': '基礎科目専用試験システム (v2)',
            'description': '新システムによる基礎科目専用試験',
            'system_version': 'v2.0 (Strangler Fig Pattern)',
            'isolation_status': '完全分離動作'
        })
        
    except Exception as e:
        return jsonify({
            'error': 'basic_exam_index_error',
            'message': f'基礎科目トップページエラー: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@basic_exam_bp.route('/start', methods=['GET', 'POST'])
def basic_exam_start():
    """基礎科目試験開始"""
    try:
        if request.method == 'GET':
            # 試験開始ページ表示
            return render_template('basic_exam_start.html', {
                'title': '基礎科目試験開始',
                'question_count': 10,
                'time_limit': '制限なし',
                'data_source': 'data/4-1.csv (基礎科目専用)',
                'session_isolation': 'basic_exam_* プレフィックス'
            })
        
        elif request.method == 'POST':
            # 試験セッション初期化
            session_id = init_basic_exam_session()
            
            # 基礎科目データ読み込み（basic_data_service.py使用）
            try:
                from basic_data_service import load_basic_questions, select_random_questions
                
                # 基礎科目データ読み込み
                all_basic_questions = load_basic_questions()
                if len(all_basic_questions) < 10:
                    raise Exception(f"基礎科目問題数不足: {len(all_basic_questions)}問 < 10問")
                
                # 10問選択
                selected_questions = select_random_questions(all_basic_questions, 10)
                session[get_basic_exam_session_key('questions')] = selected_questions
                
                # 第1問へリダイレクト
                return redirect(url_for('basic_exam.basic_exam_question', question_no=1))
                
            except ImportError:
                # basic_data_service.py未実装時の仮実装
                # 実際の実装では削除される
                mock_questions = []
                for i in range(10):
                    mock_questions.append({
                        'id': f'basic_mock_{i+1}',
                        'question': f'基礎科目問題{i+1}（仮実装）',
                        'option_a': '選択肢A',
                        'option_b': '選択肢B', 
                        'option_c': '選択肢C',
                        'option_d': '選択肢D',
                        'correct_answer': random.choice(['A', 'B', 'C', 'D'])
                    })
                
                session[get_basic_exam_session_key('questions')] = mock_questions
                return redirect(url_for('basic_exam.basic_exam_question', question_no=1))
                
    except Exception as e:
        clear_basic_exam_session()
        return jsonify({
            'error': 'basic_exam_start_error',
            'message': f'基礎科目試験開始エラー: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@basic_exam_bp.route('/question/<int:question_no>')
def basic_exam_question(question_no):
    """基礎科目問題表示"""
    try:
        # セッション確認
        session_data = get_basic_exam_session_data()
        if not session_data['session_id']:
            return redirect(url_for('basic_exam.basic_exam_start'))
        
        questions = session_data['questions']
        if not questions:
            return redirect(url_for('basic_exam.basic_exam_start'))
        
        # 問題番号確認
        if question_no < 1 or question_no > len(questions):
            return redirect(url_for('basic_exam.basic_exam_result'))
        
        # 現在問題更新
        session[get_basic_exam_session_key('current_question')] = question_no - 1
        
        # 問題データ取得
        current_question = questions[question_no - 1]
        
        # 進捗情報
        progress = {
            'current': question_no,
            'total': len(questions),
            'percentage': (question_no / len(questions)) * 100
        }
        
        # ナビゲーション情報
        navigation = {
            'has_previous': question_no > 1,
            'has_next': question_no < len(questions),
            'previous_url': url_for('basic_exam.basic_exam_question', question_no=question_no-1) if question_no > 1 else None,
            'next_url': url_for('basic_exam.basic_exam_question', question_no=question_no+1) if question_no < len(questions) else None,
            'result_url': url_for('basic_exam.basic_exam_result') if question_no == len(questions) else None
        }
        
        return render_template('basic_exam_question.html', {
            'question': current_question,
            'progress': progress,
            'navigation': navigation,
            'session_info': {
                'session_id': session_data['session_id'][:8],  # 短縮表示
                'start_time': session_data['start_time'],
                'system_version': 'v2.0 基礎科目専用'
            }
        })
        
    except Exception as e:
        return jsonify({
            'error': 'basic_exam_question_error',
            'message': f'基礎科目問題表示エラー: {str(e)}',
            'question_no': question_no,
            'timestamp': datetime.now().isoformat()
        }), 500

@basic_exam_bp.route('/submit', methods=['POST'])
def basic_exam_submit():
    """基礎科目回答送信"""
    try:
        # セッション確認
        session_data = get_basic_exam_session_data()
        if not session_data['session_id']:
            return jsonify({'error': 'session_not_found'}), 400
        
        # 回答データ取得
        answer_data = request.get_json() or {}
        question_no = answer_data.get('question_no')
        selected_answer = answer_data.get('answer')
        
        if not question_no or not selected_answer:
            return jsonify({'error': 'invalid_answer_data'}), 400
        
        # 回答保存
        answers = session_data['answers']
        answers[str(question_no)] = {
            'answer': selected_answer,
            'timestamp': datetime.now().isoformat()
        }
        session[get_basic_exam_session_key('answers')] = answers
        
        # 次の質問URL決定
        questions = session_data['questions']
        if question_no < len(questions):
            next_url = url_for('basic_exam.basic_exam_question', question_no=question_no + 1)
        else:
            next_url = url_for('basic_exam.basic_exam_result')
        
        return jsonify({
            'success': True,
            'next_url': next_url,
            'progress': {
                'answered': len(answers),
                'total': len(questions)
            }
        })
        
    except Exception as e:
        return jsonify({
            'error': 'basic_exam_submit_error',
            'message': f'基礎科目回答送信エラー: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@basic_exam_bp.route('/result')
def basic_exam_result():
    """基礎科目結果表示"""
    try:
        # セッション確認
        session_data = get_basic_exam_session_data()
        if not session_data['session_id']:
            return redirect(url_for('basic_exam.basic_exam_start'))
        
        questions = session_data['questions']
        answers = session_data['answers']
        
        if not questions or not answers:
            return redirect(url_for('basic_exam.basic_exam_start'))
        
        # 結果計算
        correct_count = 0
        total_questions = len(questions)
        result_details = []
        
        for i, question in enumerate(questions):
            question_no = str(i + 1)
            user_answer = answers.get(question_no, {}).get('answer', '')
            correct_answer = question.get('correct_answer', '')
            is_correct = user_answer.upper() == correct_answer.upper()
            
            if is_correct:
                correct_count += 1
            
            result_details.append({
                'question_no': i + 1,
                'question_text': question.get('question', '')[:100] + '...',
                'user_answer': user_answer,
                'correct_answer': correct_answer,
                'is_correct': is_correct
            })
        
        # 成績計算
        score_percentage = (correct_count / total_questions) * 100
        
        # 判定
        if score_percentage >= 60:
            result_status = 'pass'
            result_message = '合格'
        else:
            result_status = 'fail'
            result_message = '不合格'
        
        # セッション終了時刻
        end_time = datetime.now().isoformat()
        
        result_summary = {
            'total_questions': total_questions,
            'correct_count': correct_count,
            'incorrect_count': total_questions - correct_count,
            'score_percentage': score_percentage,
            'result_status': result_status,
            'result_message': result_message,
            'start_time': session_data['start_time'],
            'end_time': end_time,
            'session_id': session_data['session_id']
        }
        
        return render_template('basic_exam_result.html', {
            'result_summary': result_summary,
            'result_details': result_details,
            'system_info': {
                'version': 'v2.0 基礎科目専用',
                'data_source': 'data/4-1.csv',
                'session_type': 'basic_exam_* 分離セッション'
            }
        })
        
    except Exception as e:
        return jsonify({
            'error': 'basic_exam_result_error',
            'message': f'基礎科目結果表示エラー: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

# Blueprint エラーハンドラー
@basic_exam_bp.errorhandler(404)
def basic_exam_not_found(error):
    """基礎科目システム404エラー"""
    return render_template('basic_exam_error.html', {
        'error_type': '404 Not Found',
        'error_message': '基礎科目システム内で指定されたページが見つかりません',
        'system_version': 'v2.0 基礎科目専用',
        'back_url': url_for('basic_exam.basic_exam_index')
    }), 404

@basic_exam_bp.errorhandler(500)
def basic_exam_server_error(error):
    """基礎科目システム500エラー"""
    return render_template('basic_exam_error.html', {
        'error_type': '500 Server Error',
        'error_message': '基礎科目システム内でサーバーエラーが発生しました',
        'system_version': 'v2.0 基礎科目専用',
        'back_url': url_for('basic_exam.basic_exam_index')
    }), 500

# Blueprint情報取得関数
def get_basic_exam_blueprint_info():
    """基礎科目Blueprint情報取得"""
    return {
        'name': 'basic_exam',
        'url_prefix': '/v2/basic_exam',
        'routes': [
            {'path': '/', 'endpoint': 'basic_exam_index', 'methods': ['GET']},
            {'path': '/start', 'endpoint': 'basic_exam_start', 'methods': ['GET', 'POST']},
            {'path': '/question/<int:question_no>', 'endpoint': 'basic_exam_question', 'methods': ['GET']},
            {'path': '/submit', 'endpoint': 'basic_exam_submit', 'methods': ['POST']},
            {'path': '/result', 'endpoint': 'basic_exam_result', 'methods': ['GET']}
        ],
        'session_prefix': BASIC_EXAM_SESSION_PREFIX,
        'isolation_status': 'complete',
        'data_source': 'data/4-1.csv (基礎科目専用)',
        'version': '2.0',
        'implementation_date': '2025-07-10'
    }

# デバッグ用関数
def debug_basic_exam_session():
    """デバッグ用セッション情報取得"""
    debug_info = {}
    for key in session.keys():
        if key.startswith(BASIC_EXAM_SESSION_PREFIX):
            debug_info[key] = session[key]
    return debug_info

if __name__ == "__main__":
    # Blueprint単独テスト用
    print("基礎科目専用Blueprint実装完了")
    print(f"URL Prefix: {basic_exam_bp.url_prefix}")
    print(f"Session Prefix: {BASIC_EXAM_SESSION_PREFIX}")
    print("注意: app.pyへの登録は手動で行う必要があります")