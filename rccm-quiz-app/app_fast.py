"""
RCCM試験問題集 - 高速起動版
起動時間を最小化するための最適化版
"""

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import os
import logging
from datetime import datetime, timedelta
import threading

# ログ設定（最小限）
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Flask アプリケーション初期化
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

# グローバル変数（遅延初期化）
_questions_cache = None
_cache_lock = threading.Lock()
_modules_loaded = False

def get_questions():
    """問題データを遅延読み込み"""
    global _questions_cache
    
    if _questions_cache is None:
        with _cache_lock:
            if _questions_cache is None:  # Double-check
                logger.info("問題データ初回読み込み開始")
                from utils import load_rccm_data_files
                _questions_cache = load_rccm_data_files('data')
                logger.info(f"問題データ読み込み完了: {len(_questions_cache)}問")
    
    return _questions_cache

def ensure_modules():
    """必要なモジュールを遅延読み込み"""
    global _modules_loaded
    if not _modules_loaded:
        with _cache_lock:
            if not _modules_loaded:
                logger.info("モジュール遅延読み込み開始")
                # 必要最小限のモジュールのみインポート
                global gamification_manager, ai_analyzer
                from gamification import gamification_manager
                from ai_analyzer import ai_analyzer
                _modules_loaded = True
                logger.info("モジュール読み込み完了")

@app.route('/')
def index():
    """ホームページ（高速版）"""
    # セッションクリア
    for key in ['exam_question_ids', 'exam_current']:
        session.pop(key, None)
    
    user_name = session.get('user_name', None)
    return render_template('index.html', user_name=user_name)

@app.route('/set_user', methods=['GET', 'POST'])
def set_user():
    """ユーザー名設定"""
    if request.method == 'POST':
        user_name = request.form.get('user_name', '').strip()
        if not user_name:
            user_name = f"ゲスト_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        session['user_name'] = user_name
        session['user_id'] = f"user_{hash(user_name) % 100000:05d}"
        session.permanent = True
        
        logger.info(f"ユーザー設定: {user_name}")
        return redirect(url_for('index'))
    
    return render_template('set_user.html')

@app.route('/settings', methods=['GET', 'POST'])
def settings_page():
    """設定画面"""
    if request.method == 'POST':
        questions_per_session = int(request.form.get('questions_per_session', 10))
        if questions_per_session not in [10, 20, 30]:
            questions_per_session = 10
        
        if 'quiz_settings' not in session:
            session['quiz_settings'] = {}
        
        session['quiz_settings']['questions_per_session'] = questions_per_session
        session.modified = True
        
        logger.info(f"問題数設定変更: {questions_per_session}問")
        return redirect(url_for('settings_page'))
    
    current_setting = session.get('quiz_settings', {}).get('questions_per_session', 10)
    return render_template('settings.html', current_setting=current_setting)

@app.route('/exam', methods=['GET', 'POST'])
def exam():
    """試験ページ（最小限実装）"""
    # 必要になったらモジュールを読み込む
    ensure_modules()
    
    # 必要になったら問題データを読み込む
    all_questions = get_questions()
    
    if not all_questions:
        return render_template('error.html', error="問題データが存在しません。")
    
    # 既存の処理をここに移植（省略）
    return render_template('exam.html')

@app.route('/health')
def health():
    """ヘルスチェック（高速）"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

# エラーハンドラー
@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', error="ページが見つかりません"), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"内部エラー: {str(error)}")
    return render_template('error.html', error="内部エラーが発生しました"), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5005))
    logger.info(f"🚀 RCCM高速起動モード - ポート{port}で起動")
    app.run(host='0.0.0.0', port=port, debug=True)