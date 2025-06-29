#!/usr/bin/env python3
"""
🛡️ RCCM App with Ultra Sync Circuit Breaker Integration
既存のapp.pyにウルトラシンク サーキットブレーカーを統合した実装例

この実装は既存のRCCMアプリケーションに対して最小限の変更で
世界標準のサーキットブレーカーパターンを適用します。
"""

from flask import Flask, session, request, jsonify, render_template, redirect, url_for
import os
import logging
import csv
import json
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

# ウルトラシンク サーキットブレーカー統合
from rccm_circuit_breaker_integration import (
    init_rccm_circuit_breakers,
    get_rccm_circuit_breakers,
    rccm_protected_csv_load,
    rccm_protected_session,
    rccm_protected_file_ops
)

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Flask アプリケーション作成
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'rccm-ultra-secure-secret-key-2025')
app.config['DEBUG'] = True

# 🛡️ STEP 1: ウルトラシンク サーキットブレーカー初期化
try:
    rccm_cb_integration = init_rccm_circuit_breakers()
    logger.info("✅ Ultra Sync Circuit Breaker Integration initialized")
except Exception as e:
    logger.error(f"❌ Circuit Breaker initialization failed: {e}")
    rccm_cb_integration = None

# 🛡️ STEP 2: 保護された関数群（ウルトラシンク適用）

@rccm_protected_csv_load
def load_questions_protected(file_path: str, encoding: str = 'shift_jis') -> List[Dict[str, Any]]:
    """📄 保護されたCSV問題データロード（ウルトラシンク適用）"""
    if not rccm_cb_integration:
        # フォールバック: 従来の方法
        return load_questions_traditional(file_path, encoding)
    
    return rccm_cb_integration.protected_csv_load(file_path, encoding)

def load_questions_traditional(file_path: str, encoding: str = 'shift_jis') -> List[Dict[str, Any]]:
    """📄 従来のCSVロード方法（フォールバック用）"""
    questions = []
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 11:
                    questions.append({
                        'id': row[0],
                        'category': row[1],
                        'year': row[2],
                        'question': row[3],
                        'choice_a': row[4],
                        'choice_b': row[5],
                        'choice_c': row[6],
                        'choice_d': row[7],
                        'correct': row[8],
                        'explanation': row[9],
                        'source': row[10],
                        'difficulty': row[11] if len(row) > 11 else 'standard'
                    })
    except Exception as e:
        logger.error(f"Traditional CSV load failed: {e}")
        # 緊急フォールバック
        questions = [{
            'id': '1',
            'category': 'システムエラー',
            'year': '2024',
            'question': 'データロードでエラーが発生しました。',
            'choice_a': 'ページを再読み込み',
            'choice_b': '管理者に連絡',
            'choice_c': '後ほど再試行',
            'choice_d': 'システム復旧を待つ',
            'correct': 'a',
            'explanation': 'サーキットブレーカーがエラーを検出しました',
            'source': 'システム',
            'difficulty': 'emergency'
        }]
    
    return questions

@rccm_protected_session
def save_user_session_protected(session_id: str, session_data: Dict[str, Any]) -> bool:
    """👤 保護されたセッション保存（ウルトラシンク適用）"""
    if not rccm_cb_integration:
        return save_user_session_traditional(session_id, session_data)
    
    return rccm_cb_integration.protected_session_save(session_id, session_data)

def save_user_session_traditional(session_id: str, session_data: Dict[str, Any]) -> bool:
    """👤 従来のセッション保存方法"""
    try:
        os.makedirs('user_data', exist_ok=True)
        session_file = f'user_data/{session_id}_session.json'
        
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2, default=str)
        
        return True
    except Exception as e:
        logger.error(f"Traditional session save failed: {e}")
        return False

@rccm_protected_session
def load_user_session_protected(session_id: str) -> Optional[Dict[str, Any]]:
    """👤 保護されたセッション読み込み（ウルトラシンク適用）"""
    if not rccm_cb_integration:
        return load_user_session_traditional(session_id)
    
    return rccm_cb_integration.protected_session_load(session_id)

def load_user_session_traditional(session_id: str) -> Optional[Dict[str, Any]]:
    """👤 従来のセッション読み込み方法"""
    try:
        session_file = f'user_data/{session_id}_session.json'
        
        if not os.path.exists(session_file):
            return None
        
        with open(session_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Traditional session load failed: {e}")
        return None

# 🛡️ STEP 3: ルート定義（サーキットブレーカー統合版）

@app.route('/')
def index():
    """ホームページ（サーキットブレーカー統合版）"""
    try:
        # セッション管理
        if 'session_id' not in session:
            import uuid
            session['session_id'] = str(uuid.uuid4())
            session['user_name'] = '匿名ユーザー'
            session.permanent = True
        
        # サーキットブレーカー統計
        cb_stats = None
        health_status = None
        
        if rccm_cb_integration:
            try:
                stats = rccm_cb_integration.get_integration_stats()
                health_status = rccm_cb_integration.get_health_status()
                
                cb_stats = {
                    'total_calls': stats['integration_stats']['total_protected_calls'],
                    'fallback_executions': stats['integration_stats']['total_fallback_executions'],
                    'health_score': health_status['health_score'],
                    'health_status': health_status['health_status']
                }
            except Exception as e:
                logger.error(f"Failed to get circuit breaker stats: {e}")
                cb_stats = {'error': 'Stats unavailable'}
        
        # レンダリング用データ
        template_data = {
            'session_id': session['session_id'][:8],
            'user_name': session['user_name'],
            'cb_stats': cb_stats,
            'health_status': health_status,
            'current_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'circuit_breaker_enabled': rccm_cb_integration is not None
        }
        
        return render_template_string(INDEX_TEMPLATE, **template_data)
        
    except Exception as e:
        logger.error(f"Index route error: {e}")
        return f"エラー: {e}", 500

@app.route('/quiz')
def quiz():
    """クイズページ（サーキットブレーカー統合版）"""
    try:
        # セッションデータ取得
        session_id = session.get('session_id', 'anonymous')
        user_session = load_user_session_protected(session_id) or {}
        
        # 問題データロード（保護されたロード）
        try:
            questions = load_questions_protected('data/4-1.csv')
            logger.info(f"✅ Loaded {len(questions)} questions via circuit breaker")
        except Exception as e:
            logger.error(f"❌ Protected question load failed: {e}")
            questions = []
        
        # クイズセッション初期化
        if 'quiz_question_ids' not in user_session:
            if questions:
                # 最初の10問を選択
                selected_questions = questions[:10]
                user_session['quiz_question_ids'] = [q['id'] for q in selected_questions]
                user_session['quiz_current'] = 0
                user_session['quiz_questions_data'] = selected_questions
            else:
                # フォールバックデータ
                user_session['quiz_question_ids'] = ['fallback_1']
                user_session['quiz_current'] = 0
                user_session['quiz_questions_data'] = questions  # フォールバック問題
        
        current_index = user_session.get('quiz_current', 0)
        quiz_questions = user_session.get('quiz_questions_data', [])
        
        if current_index < len(quiz_questions):
            current_question = quiz_questions[current_index]
            quiz_data = {
                'current_question': current_index + 1,
                'total_questions': len(quiz_questions),
                'question_data': current_question,
                'progress': round(((current_index + 1) / len(quiz_questions)) * 100, 1)
            }
        else:
            # 完了
            return redirect(url_for('results'))
        
        # セッション保存
        save_user_session_protected(session_id, user_session)
        
        template_data = {
            'quiz_data': quiz_data,
            'session_id': session_id[:8]
        }
        
        return render_template_string(QUIZ_TEMPLATE, **template_data)
        
    except Exception as e:
        logger.error(f"Quiz route error: {e}")
        return f"クイズエラー: {e}", 500

@app.route('/quiz/answer', methods=['POST'])
def quiz_answer():
    """クイズ回答処理（サーキットブレーカー統合版）"""
    try:
        session_id = session.get('session_id', 'anonymous')
        user_session = load_user_session_protected(session_id) or {}
        
        # 回答処理
        answer = request.form.get('answer', '')
        current_index = user_session.get('quiz_current', 0)
        
        # 履歴に追加
        if 'history' not in user_session:
            user_session['history'] = []
        
        user_session['history'].append({
            'question_index': current_index,
            'answer': answer,
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
        
        # 次の問題へ
        user_session['quiz_current'] = current_index + 1
        
        # セッション保存
        save_user_session_protected(session_id, user_session)
        
        return redirect(url_for('quiz'))
        
    except Exception as e:
        logger.error(f"Quiz answer error: {e}")
        return f"回答処理エラー: {e}", 500

@app.route('/results')
def results():
    """結果ページ（サーキットブレーカー統合版）"""
    try:
        session_id = session.get('session_id', 'anonymous')
        user_session = load_user_session_protected(session_id) or {}
        
        history = user_session.get('history', [])
        quiz_questions = user_session.get('quiz_questions_data', [])
        
        results_data = {
            'total_questions': len(quiz_questions),
            'answered_questions': len(history),
            'completion_rate': round((len(history) / max(len(quiz_questions), 1)) * 100, 1),
            'history': history
        }
        
        template_data = {
            'results_data': results_data,
            'session_id': session_id[:8]
        }
        
        return render_template_string(RESULTS_TEMPLATE, **template_data)
        
    except Exception as e:
        logger.error(f"Results route error: {e}")
        return f"結果エラー: {e}", 500

# 🛡️ STEP 4: サーキットブレーカー管理API

@app.route('/api/circuit-breaker/status')
def circuit_breaker_status():
    """サーキットブレーカー統計API"""
    try:
        if not rccm_cb_integration:
            return jsonify({'error': 'Circuit Breaker not available'}), 503
        
        stats = rccm_cb_integration.get_integration_stats()
        return jsonify({
            'success': True,
            'stats': stats,
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
        
    except Exception as e:
        logger.error(f"Circuit breaker status error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/circuit-breaker/health')
def circuit_breaker_health():
    """システム健全性API"""
    try:
        if not rccm_cb_integration:
            return jsonify({'error': 'Circuit Breaker not available'}), 503
        
        health = rccm_cb_integration.get_health_status()
        status_code = 200 if health['health_status'] == 'healthy' else 503
        
        return jsonify({
            'success': True,
            'health': health
        }), status_code
        
    except Exception as e:
        logger.error(f"Circuit breaker health error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/circuit-breaker/reset', methods=['POST'])
def circuit_breaker_reset():
    """サーキットブレーカーリセットAPI"""
    try:
        if not rccm_cb_integration:
            return jsonify({'error': 'Circuit Breaker not available'}), 503
        
        rccm_cb_integration.reset_all_circuit_breakers()
        
        return jsonify({
            'success': True,
            'message': 'All circuit breakers reset successfully'
        })
        
    except Exception as e:
        logger.error(f"Circuit breaker reset error: {e}")
        return jsonify({'error': str(e)}), 500

# 🛡️ STEP 5: HTMLテンプレート（サーキットブレーカー対応版）

INDEX_TEMPLATE = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RCCM試験問題集 - ウルトラシンク サーキットブレーカー対応版</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { background: white; padding: 30px; border-radius: 8px; max-width: 800px; margin: 0 auto; }
        .stats { background: #e3f2fd; padding: 15px; border-radius: 4px; margin: 20px 0; }
        .health-good { background: #e8f5e8; }
        .health-warning { background: #fff3e0; }
        .health-critical { background: #ffebee; }
        .btn { display: inline-block; padding: 10px 20px; background: #1976d2; color: white; text-decoration: none; border-radius: 4px; margin: 5px; }
        .cb-status { font-size: 12px; color: #666; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🛡️ RCCM試験問題集 - ウルトラシンク サーキットブレーカー対応版</h1>
        
        <div class="stats">
            <h3>📊 セッション情報</h3>
            <p><strong>セッションID:</strong> {{ session_id }}...</p>
            <p><strong>ユーザー名:</strong> {{ user_name }}</p>
            <p><strong>現在時刻:</strong> {{ current_time }}</p>
        </div>
        
        {% if circuit_breaker_enabled %}
        <div class="stats {% if health_status %}{% if health_status.health_status == 'healthy' %}health-good{% elif health_status.health_status == 'warning' %}health-warning{% else %}health-critical{% endif %}{% endif %}">
            <h3>🛡️ ウルトラシンク サーキットブレーカー状態</h3>
            {% if cb_stats %}
            <p><strong>保護された呼び出し:</strong> {{ cb_stats.total_calls }}</p>
            <p><strong>フォールバック実行:</strong> {{ cb_stats.fallback_executions }}</p>
            <p><strong>健全性スコア:</strong> {{ cb_stats.health_score }}/100</p>
            <p><strong>システム状態:</strong> {{ cb_stats.health_status }}</p>
            {% else %}
            <p><strong>ステータス:</strong> 統計取得中...</p>
            {% endif %}
        </div>
        {% else %}
        <div class="stats health-warning">
            <h3>⚠️ サーキットブレーカー無効</h3>
            <p>フォールバックモードで動作中</p>
        </div>
        {% endif %}
        
        <div>
            <a href="/quiz" class="btn">📝 クイズ開始</a>
            <a href="/results" class="btn">📊 結果確認</a>
            <a href="/api/circuit-breaker/status" class="btn" target="_blank">🛡️ CB統計</a>
            <a href="/api/circuit-breaker/health" class="btn" target="_blank">🏥 健全性</a>
        </div>
        
        <div style="margin-top: 30px; padding: 20px; background: #f9f9f9; border-radius: 4px;">
            <h3>🎯 ウルトラシンク サーキットブレーカーの特徴</h3>
            <ul>
                <li>✅ 3段階状態管理 (Closed/Open/Half-Open)</li>
                <li>✅ 自動障害検出と回復</li>
                <li>✅ 保護されたデータロード</li>
                <li>✅ フォールバック機能</li>
                <li>✅ リアルタイム監視</li>
                <li>✅ 包括的健全性管理</li>
            </ul>
        </div>
        
        {% if health_status and health_status.recommendations %}
        <div style="margin-top: 20px; padding: 15px; background: #fff3e0; border-radius: 4px;">
            <h4>💡 推奨事項</h4>
            <ul>
            {% for rec in health_status.recommendations %}
                <li>{{ rec }}</li>
            {% endfor %}
            </ul>
        </div>
        {% endif %}
    </div>
</body>
</html>
"""

QUIZ_TEMPLATE = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>クイズ - サーキットブレーカー対応版</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { background: white; padding: 30px; border-radius: 8px; max-width: 600px; margin: 0 auto; }
        .progress-bar { width: 100%; height: 20px; background: #e0e0e0; border-radius: 10px; margin: 20px 0; }
        .progress-fill { height: 100%; background: #4caf50; border-radius: 10px; transition: width 0.3s; }
        .btn { padding: 10px 20px; background: #1976d2; color: white; border: none; border-radius: 4px; margin: 5px; cursor: pointer; }
        .question { background: #f9f9f9; padding: 20px; border-radius: 4px; margin: 20px 0; }
        .protected { background: #e8f5e8; padding: 10px; border-radius: 4px; margin: 10px 0; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📝 クイズ ({{ quiz_data.current_question }}/{{ quiz_data.total_questions }})</h1>
        
        <div class="protected">
            🛡️ サーキットブレーカー保護済み - セッション: {{ session_id }}...
        </div>
        
        <div class="progress-bar">
            <div class="progress-fill" style="width: {{ quiz_data.progress }}%"></div>
        </div>
        <p>進捗: {{ quiz_data.progress }}%</p>
        
        <div class="question">
            <h3>{{ quiz_data.question_data.question }}</h3>
            <form method="POST" action="/quiz/answer">
                <p>
                    <input type="radio" name="answer" value="a" id="a"> 
                    <label for="a">A. {{ quiz_data.question_data.choice_a }}</label>
                </p>
                <p>
                    <input type="radio" name="answer" value="b" id="b"> 
                    <label for="b">B. {{ quiz_data.question_data.choice_b }}</label>
                </p>
                <p>
                    <input type="radio" name="answer" value="c" id="c"> 
                    <label for="c">C. {{ quiz_data.question_data.choice_c }}</label>
                </p>
                <p>
                    <input type="radio" name="answer" value="d" id="d"> 
                    <label for="d">D. {{ quiz_data.question_data.choice_d }}</label>
                </p>
                <button type="submit" class="btn">回答して次へ</button>
            </form>
        </div>
        
        <p><a href="/">← ホームに戻る</a></p>
    </div>
</body>
</html>
"""

RESULTS_TEMPLATE = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>結果 - サーキットブレーカー対応版</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { background: white; padding: 30px; border-radius: 8px; max-width: 600px; margin: 0 auto; }
        .stats { background: #e8f5e8; padding: 20px; border-radius: 4px; margin: 20px 0; }
        .btn { display: inline-block; padding: 10px 20px; background: #1976d2; color: white; text-decoration: none; border-radius: 4px; margin: 5px; }
        .history { background: #f9f9f9; padding: 15px; border-radius: 4px; margin: 10px 0; }
        .protected { background: #e8f5e8; padding: 10px; border-radius: 4px; margin: 10px 0; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 クイズ結果</h1>
        
        <div class="protected">
            🛡️ サーキットブレーカー保護済み - セッション: {{ session_id }}...
        </div>
        
        <div class="stats">
            <h3>🎯 完了統計</h3>
            <p><strong>回答問題数:</strong> {{ results_data.answered_questions }}/{{ results_data.total_questions }}</p>
            <p><strong>完了率:</strong> {{ results_data.completion_rate }}%</p>
        </div>
        
        {% if results_data.history %}
        <h3>📝 回答履歴</h3>
        {% for item in results_data.history %}
        <div class="history">
            <p><strong>問題 {{ item.question_index + 1 }}:</strong> {{ item.answer }}</p>
            <small>{{ item.timestamp }}</small>
        </div>
        {% endfor %}
        {% endif %}
        
        <div>
            <a href="/" class="btn">🏠 ホーム</a>
            <a href="/quiz" class="btn">🔄 再挑戦</a>
        </div>
    </div>
</body>
</html>
"""

# render_template_string 関数
def render_template_string(template_string, **context):
    """簡易テンプレートレンダリング"""
    try:
        from flask import render_template_string as flask_render
        return flask_render(template_string, **context)
    except:
        from jinja2 import Template
        template = Template(template_string)
        return template.render(**context)

if __name__ == '__main__':
    print("🚀 RCCM ウルトラシンク サーキットブレーカー統合アプリ起動中...")
    print("=" * 80)
    print("📋 利用可能なエンドポイント:")
    print("  🏠 http://localhost:5000/ - ホームページ")
    print("  📝 http://localhost:5000/quiz - クイズページ")
    print("  📊 http://localhost:5000/results - 結果ページ")
    print("  🛡️ http://localhost:5000/api/circuit-breaker/status - CB統計")
    print("  🏥 http://localhost:5000/api/circuit-breaker/health - 健全性")
    print("  🔄 http://localhost:5000/api/circuit-breaker/reset - CB リセット")
    print("=" * 80)
    
    # サーキットブレーカー状況確認
    if rccm_cb_integration:
        print(f"✅ Ultra Sync Circuit Breaker: 統合済み")
        try:
            health = rccm_cb_integration.get_health_status()
            print(f"🏥 システム健全性: {health['health_status']} (Score: {health['health_score']}/100)")
        except:
            print("🔍 健全性確認中...")
    else:
        print("⚠️ Circuit Breaker: 未統合（フォールバックモード）")
    
    print()
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=app.config['DEBUG']
    )