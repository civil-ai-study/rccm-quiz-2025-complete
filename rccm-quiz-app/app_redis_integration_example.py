#!/usr/bin/env python3
"""
🔧 RCCM App - Redis Integration Example
既存のapp.pyにRedis統合を適用する実装例

この例では、既存のFlaskアプリケーションにRedis Session Managerを統合する方法を示します。
"""

from flask import Flask, session, request, jsonify, render_template, redirect, url_for
import os
import logging
from datetime import datetime, timezone
from redis_session_manager import init_redis_session_manager, get_redis_session_manager
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Flask アプリケーション作成
app = Flask(__name__)

# 🔧 STEP 1: Basic Flask Configuration
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'rccm-ultra-secure-secret-key-2025')
app.config['DEBUG'] = os.environ.get('DEBUG', 'true').lower() == 'true'

# 🔧 STEP 2: Redis Session Manager 初期化
try:
    redis_session_manager = init_redis_session_manager(app)
    logger.info("✅ Redis Session Manager initialized successfully")
except Exception as e:
    logger.error(f"❌ Redis Session Manager initialization failed: {e}")
    redis_session_manager = None

# 🔧 STEP 3: セッション管理ヘルパー関数
def get_user_session_data():
    """現在のユーザーセッションデータを取得"""
    session_id = session.get('session_id')
    if not session_id:
        # 新しいセッションID生成
        import uuid
        session_id = str(uuid.uuid4())
        session['session_id'] = session_id
        session.permanent = True
    
    return {
        'session_id': session_id,
        'user_name': session.get('user_name', '匿名ユーザー'),
        'quiz_current': session.get('quiz_current', 0),
        'quiz_question_ids': session.get('quiz_question_ids', []),
        'history': session.get('history', []),
        'last_activity': datetime.now(timezone.utc).isoformat()
    }

def update_user_session_data(data):
    """ユーザーセッションデータを更新"""
    for key, value in data.items():
        session[key] = value
    
    # Redis Session Manager への明示的保存（オプション）
    if redis_session_manager and redis_session_manager.is_healthy:
        session_id = session.get('session_id')
        if session_id:
            redis_session_manager.set_session(session_id, dict(session))

# 🔧 STEP 4: ルート定義（Redis統合版）

@app.route('/')
def index():
    """ホームページ（Redis統合版）"""
    try:
        # セッションデータ取得
        session_data = get_user_session_data()
        
        # Redis統計情報（デバッグ用）
        redis_stats = None
        if redis_session_manager:
            try:
                analytics = redis_session_manager.get_session_analytics()
                redis_stats = {
                    'redis_available': redis_session_manager.is_healthy,
                    'session_count': analytics.get('session_stats', {}).get('active_sessions', 0),
                    'redis_hits': analytics.get('session_stats', {}).get('redis_hits', 0),
                    'fallback_hits': analytics.get('session_stats', {}).get('fallback_hits', 0)
                }
            except:
                redis_stats = {'error': 'Redis stats unavailable'}
        
        # レンダリング用データ
        template_data = {
            'session_data': session_data,
            'redis_stats': redis_stats,
            'current_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return render_template_string(INDEX_TEMPLATE, **template_data)
        
    except Exception as e:
        logger.error(f"Index route error: {e}")
        return f"エラー: {e}", 500

@app.route('/quiz')
def quiz():
    """クイズページ（Redis統合版）"""
    try:
        # セッションデータ取得・更新
        session_data = get_user_session_data()
        
        # サンプルクイズデータ（実際の実装では質問データベースから取得）
        if not session_data['quiz_question_ids']:
            # 新しいクイズセッション開始
            sample_questions = [f"問題{i+1}" for i in range(10)]
            session_data['quiz_question_ids'] = sample_questions
            session_data['quiz_current'] = 0
            update_user_session_data(session_data)
        
        current_question = session_data['quiz_current']
        total_questions = len(session_data['quiz_question_ids'])
        
        quiz_data = {
            'current_question': current_question + 1,
            'total_questions': total_questions,
            'question_text': f"これは問題 {current_question + 1} です。",
            'progress': round((current_question / total_questions) * 100, 1)
        }
        
        template_data = {
            'quiz_data': quiz_data,
            'session_data': session_data
        }
        
        return render_template_string(QUIZ_TEMPLATE, **template_data)
        
    except Exception as e:
        logger.error(f"Quiz route error: {e}")
        return f"クイズエラー: {e}", 500

@app.route('/quiz/answer', methods=['POST'])
def quiz_answer():
    """クイズ回答処理（Redis統合版）"""
    try:
        session_data = get_user_session_data()
        
        # 回答処理
        answer = request.form.get('answer', '')
        current_question = session_data['quiz_current']
        
        # 履歴に追加
        if 'history' not in session_data:
            session_data['history'] = []
        
        session_data['history'].append({
            'question': current_question + 1,
            'answer': answer,
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
        
        # 次の問題へ
        session_data['quiz_current'] = current_question + 1
        update_user_session_data(session_data)
        
        # 最終問題チェック
        if session_data['quiz_current'] >= len(session_data['quiz_question_ids']):
            return redirect(url_for('results'))
        else:
            return redirect(url_for('quiz'))
            
    except Exception as e:
        logger.error(f"Quiz answer error: {e}")
        return f"回答処理エラー: {e}", 500

@app.route('/results')
def results():
    """結果ページ（Redis統合版）"""
    try:
        session_data = get_user_session_data()
        history = session_data.get('history', [])
        
        results_data = {
            'total_questions': len(session_data.get('quiz_question_ids', [])),
            'answered_questions': len(history),
            'completion_rate': round((len(history) / max(len(session_data.get('quiz_question_ids', [])), 1)) * 100, 1),
            'history': history
        }
        
        template_data = {
            'results_data': results_data,
            'session_data': session_data
        }
        
        return render_template_string(RESULTS_TEMPLATE, **template_data)
        
    except Exception as e:
        logger.error(f"Results route error: {e}")
        return f"結果エラー: {e}", 500

# 🔧 STEP 5: Redis管理API

@app.route('/admin/redis/status')
def admin_redis_status():
    """Redis統計情報管理ページ"""
    try:
        if not redis_session_manager:
            return jsonify({'error': 'Redis Session Manager not available'}), 503
        
        analytics = redis_session_manager.get_session_analytics()
        return jsonify({
            'success': True,
            'analytics': analytics,
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
        
    except Exception as e:
        logger.error(f"Redis status error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/admin/redis/sessions')
def admin_redis_sessions():
    """アクティブセッション一覧"""
    try:
        if not redis_session_manager:
            return jsonify({'error': 'Redis Session Manager not available'}), 503
        
        session_list = redis_session_manager.get_session_list()
        return jsonify({
            'success': True,
            'sessions': session_list,
            'count': len(session_list)
        })
        
    except Exception as e:
        logger.error(f"Redis sessions error: {e}")
        return jsonify({'error': str(e)}), 500

# 🔧 STEP 6: HTMLテンプレート（簡易版）

INDEX_TEMPLATE = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RCCM試験問題集 - Redis統合版</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { background: white; padding: 30px; border-radius: 8px; max-width: 800px; margin: 0 auto; }
        .stats { background: #e3f2fd; padding: 15px; border-radius: 4px; margin: 20px 0; }
        .btn { display: inline-block; padding: 10px 20px; background: #1976d2; color: white; text-decoration: none; border-radius: 4px; margin: 5px; }
        .redis-status { font-size: 12px; color: #666; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔧 RCCM試験問題集 - Redis統合版</h1>
        
        <div class="stats">
            <h3>📊 セッション情報</h3>
            <p><strong>セッションID:</strong> {{ session_data.session_id[:8] }}...</p>
            <p><strong>ユーザー名:</strong> {{ session_data.user_name }}</p>
            <p><strong>現在時刻:</strong> {{ current_time }}</p>
        </div>
        
        {% if redis_stats %}
        <div class="stats redis-status">
            <h3>🔧 Redis統合状況</h3>
            <p><strong>Redis利用可能:</strong> {{ redis_stats.redis_available }}</p>
            <p><strong>アクティブセッション:</strong> {{ redis_stats.session_count }}</p>
            <p><strong>Redis ヒット:</strong> {{ redis_stats.redis_hits }}</p>
            <p><strong>フォールバック ヒット:</strong> {{ redis_stats.fallback_hits }}</p>
        </div>
        {% endif %}
        
        <div>
            <a href="/quiz" class="btn">📝 クイズ開始</a>
            <a href="/results" class="btn">📊 結果確認</a>
            <a href="/admin/redis/status" class="btn" target="_blank">🔧 Redis統計</a>
        </div>
        
        <div style="margin-top: 30px; padding: 20px; background: #f9f9f9; border-radius: 4px;">
            <h3>🎯 Redis統合の特徴</h3>
            <ul>
                <li>✅ 高性能セッション管理</li>
                <li>✅ 自動フェイルオーバー機能</li>
                <li>✅ リアルタイム監視</li>
                <li>✅ ファイルベースフォールバック</li>
                <li>✅ 包括的分析機能</li>
            </ul>
        </div>
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
    <title>クイズ - Redis統合版</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { background: white; padding: 30px; border-radius: 8px; max-width: 600px; margin: 0 auto; }
        .progress-bar { width: 100%; height: 20px; background: #e0e0e0; border-radius: 10px; margin: 20px 0; }
        .progress-fill { height: 100%; background: #4caf50; border-radius: 10px; transition: width 0.3s; }
        .btn { padding: 10px 20px; background: #1976d2; color: white; border: none; border-radius: 4px; margin: 5px; cursor: pointer; }
        .question { background: #f9f9f9; padding: 20px; border-radius: 4px; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📝 クイズ ({{ quiz_data.current_question }}/{{ quiz_data.total_questions }})</h1>
        
        <div class="progress-bar">
            <div class="progress-fill" style="width: {{ quiz_data.progress }}%"></div>
        </div>
        <p>進捗: {{ quiz_data.progress }}%</p>
        
        <div class="question">
            <h3>{{ quiz_data.question_text }}</h3>
            <form method="POST" action="/quiz/answer">
                <p>
                    <input type="radio" name="answer" value="a" id="a"> 
                    <label for="a">選択肢 A</label>
                </p>
                <p>
                    <input type="radio" name="answer" value="b" id="b"> 
                    <label for="b">選択肢 B</label>
                </p>
                <p>
                    <input type="radio" name="answer" value="c" id="c"> 
                    <label for="c">選択肢 C</label>
                </p>
                <p>
                    <input type="radio" name="answer" value="d" id="d"> 
                    <label for="d">選択肢 D</label>
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
    <title>結果 - Redis統合版</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { background: white; padding: 30px; border-radius: 8px; max-width: 600px; margin: 0 auto; }
        .stats { background: #e8f5e8; padding: 20px; border-radius: 4px; margin: 20px 0; }
        .btn { display: inline-block; padding: 10px 20px; background: #1976d2; color: white; text-decoration: none; border-radius: 4px; margin: 5px; }
        .history { background: #f9f9f9; padding: 15px; border-radius: 4px; margin: 10px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 クイズ結果</h1>
        
        <div class="stats">
            <h3>🎯 完了統計</h3>
            <p><strong>回答問題数:</strong> {{ results_data.answered_questions }}/{{ results_data.total_questions }}</p>
            <p><strong>完了率:</strong> {{ results_data.completion_rate }}%</p>
        </div>
        
        {% if results_data.history %}
        <h3>📝 回答履歴</h3>
        {% for item in results_data.history %}
        <div class="history">
            <p><strong>問題 {{ item.question }}:</strong> {{ item.answer }}</p>
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

# render_template_string 関数（Flaskに含まれていない場合の代替）
def render_template_string(template_string, **context):
    """簡易テンプレートレンダリング"""
    try:
        from flask import render_template_string as flask_render
        return flask_render(template_string, **context)
    except:
        # Jinja2を直接使用
        from jinja2 import Template
        template = Template(template_string)
        return template.render(**context)

if __name__ == '__main__':
    print("🚀 RCCM Redis統合アプリケーション起動中...")
    print("=" * 60)
    print("📋 利用可能なエンドポイント:")
    print("  🏠 http://localhost:5000/ - ホームページ")
    print("  📝 http://localhost:5000/quiz - クイズページ")
    print("  📊 http://localhost:5000/results - 結果ページ")
    print("  🔧 http://localhost:5000/admin/redis/status - Redis統計")
    print("  📋 http://localhost:5000/admin/redis/sessions - セッション一覧")
    print("=" * 60)
    
    # Redis接続状況確認
    if redis_session_manager:
        print(f"✅ Redis Session Manager: 初期化済み")
        print(f"🔧 Redis接続状況: {'✅ 接続済み' if redis_session_manager.is_healthy else '❌ 未接続（フォールバックモード）'}")
    else:
        print("⚠️ Redis Session Manager: 未初期化（ファイルベースフォールバック）")
    
    print()
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=app.config['DEBUG']
    )