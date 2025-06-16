#!/usr/bin/env python3
"""
RCCM試験問題集2025 Enterprise Edition - EXE配布版
一般配布環境向け最適化版
"""

import os
import sys
import socket
import threading
import time
import webbrowser
from pathlib import Path

# EXE化時のパス修正
if getattr(sys, 'frozen', False):
    # PyInstallerでEXE化された場合
    application_path = sys._MEIPASS
    base_path = Path(sys.executable).parent
else:
    # 通常のPython実行時
    application_path = os.path.dirname(os.path.abspath(__file__))
    base_path = Path(__file__).parent

# パスを設定
sys.path.insert(0, application_path)
os.chdir(application_path)

# 元のFlaskアプリケーションをインポート
from flask import Flask, render_template, request, session, redirect, url_for, jsonify, send_file, make_response
from datetime import datetime, timedelta
import logging
import json
import hashlib
import random
from typing import Dict, List
import re
import html
from functools import wraps
import threading
import fcntl
import time
import uuid

# 新しいファイルからインポート
try:
    from config import Config, ExamConfig, SRSConfig, DataConfig, RCCMConfig
    from utils import (load_questions, load_rccm_data_files, get_sample_data_improved, 
                      resolve_id_conflicts, map_category_to_department,
                      cache_manager, enterprise_data_manager)
    from data_manager import DataManager, SessionDataManager, EnterpriseUserManager
except ImportError as e:
    print(f"設定ファイルの読み込みエラー: {e}")
    print("基本機能で起動します...")

# ログ設定（EXE版用に簡素化）
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

# 🔥 CRITICAL: セッション競合状態解決のためのロック管理
session_locks = {}
lock_cleanup_lock = threading.Lock()
logger = logging.getLogger(__name__)

def find_free_port(start_port=5003, max_attempts=10):
    """空いているポートを自動検出"""
    for port in range(start_port, start_port + max_attempts):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(('127.0.0.1', port))
            sock.close()
            return port
        except OSError:
            continue
    return start_port  # フォールバック

def open_browser_delayed(url, delay=3):
    """指定秒後にブラウザを開く"""
    def delayed_open():
        time.sleep(delay)
        try:
            webbrowser.open(url)
            print(f"✅ ブラウザが開きました: {url}")
        except Exception as e:
            print(f"❌ ブラウザを開けませんでした: {e}")
            print(f"手動でアクセスしてください: {url}")
    
    threading.Thread(target=delayed_open, daemon=True).start()

# Flask アプリケーション初期化
app = Flask(__name__)

# 設定適用
try:
    app.config.from_object(Config)
    app.config['SECRET_KEY'] = Config.SECRET_KEY
    app.config['SESSION_COOKIE_NAME'] = Config.SESSION_COOKIE_NAME
    app.config['SESSION_COOKIE_HTTPONLY'] = Config.SESSION_COOKIE_HTTPONLY
    app.config['SESSION_COOKIE_SAMESITE'] = Config.SESSION_COOKIE_SAMESITE
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(seconds=Config.PERMANENT_SESSION_LIFETIME)
except:
    # フォールバック設定
    app.config['SECRET_KEY'] = 'rccm-quiz-secret-key-2024-ultra-secure'
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)

# データマネージャー初期化
try:
    data_manager = DataManager()
    session_data_manager = SessionDataManager(data_manager)
    enterprise_user_manager = EnterpriseUserManager(data_manager)
    enterprise_data_manager = None
except:
    data_manager = None
    session_data_manager = None
    enterprise_user_manager = None
    enterprise_data_manager = None

# グローバル変数
_questions_cache = None
_cache_timestamp = None

# 🔥 CRITICAL: セッション安全性確保のための排他制御関数
def get_session_lock(user_id):
    """ユーザー固有のセッションロックを取得"""
    global session_locks, lock_cleanup_lock
    
    with lock_cleanup_lock:
        if user_id not in session_locks:
            session_locks[user_id] = threading.RLock()
        return session_locks[user_id]

def generate_unique_session_id():
    """一意なセッションIDを生成"""
    return f"{uuid.uuid4().hex[:8]}_{int(time.time())}"

# 強力なキャッシュ制御ヘッダーを設定（マルチユーザー・企業環境対応）
@app.after_request
def after_request(response):
    """レスポンス後処理（キャッシュ制御とセキュリティヘッダー）"""
    
    # 🔥 強力なキャッシュ制御（競合状態回避・企業環境対応）
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0, private'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    
    # セキュリティヘッダー追加（企業環境要求）
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    # CORS設定（API機能用）
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    
    return response

# 簡易版の問題データ読み込み関数
def load_questions():
    """問題データを読み込み（EXE版簡易版）"""
    global _questions_cache, _cache_timestamp
    
    try:
        # キャッシュチェック
        current_time = time.time()
        if _questions_cache and _cache_timestamp and (current_time - _cache_timestamp) < 3600:
            return _questions_cache
        
        # データファイルパス
        data_dir = os.path.join(application_path, 'data')
        
        all_questions = []
        
        # 4-1基礎データ読み込み
        basic_file = os.path.join(data_dir, '4-1.csv')
        if os.path.exists(basic_file):
            try:
                import pandas as pd
                df = pd.read_csv(basic_file, encoding='utf-8')
                for _, row in df.iterrows():
                    question = {
                        'id': int(row['id']),
                        'category': str(row.get('category', '共通')),
                        'question': str(row['question']),
                        'option_a': str(row['option_a']),
                        'option_b': str(row['option_b']),
                        'option_c': str(row['option_c']),
                        'option_d': str(row['option_d']),
                        'correct_answer': str(row['correct_answer']).upper(),
                        'explanation': str(row.get('explanation', '')),
                        'question_type': 'basic',
                        'department': 'common',
                        'year': None
                    }
                    all_questions.append(question)
                logger.info(f"4-1基礎データ読み込み完了: {len(all_questions)}問")
            except Exception as e:
                logger.warning(f"4-1基礎データ読み込みエラー: {e}")
        
        # 4-2専門データ読み込み
        for year in range(2008, 2019):
            specialist_file = os.path.join(data_dir, f'4-2_{year}.csv')
            if os.path.exists(specialist_file):
                try:
                    import pandas as pd
                    df = pd.read_csv(specialist_file, encoding='utf-8')
                    year_questions = []
                    for _, row in df.iterrows():
                        question = {
                            'id': len(all_questions) + len(year_questions) + 1001,  # ID自動調整
                            'category': str(row.get('category', '専門科目')),
                            'question': str(row['question']),
                            'option_a': str(row['option_a']),
                            'option_b': str(row['option_b']),
                            'option_c': str(row['option_c']),
                            'option_d': str(row['option_d']),
                            'correct_answer': str(row['correct_answer']).upper(),
                            'explanation': str(row.get('explanation', '')),
                            'question_type': 'specialist',
                            'department': 'road',  # デフォルト
                            'year': year
                        }
                        year_questions.append(question)
                    all_questions.extend(year_questions)
                    logger.info(f"4-2専門データ{year}年読み込み完了: {len(year_questions)}問")
                except Exception as e:
                    logger.warning(f"4-2専門データ{year}年読み込みエラー: {e}")
        
        # キャッシュ更新
        _questions_cache = all_questions
        _cache_timestamp = current_time
        
        logger.info(f"問題データ読み込み完了: 総計{len(all_questions)}問")
        return all_questions
        
    except Exception as e:
        logger.error(f"問題データ読み込みエラー: {e}")
        # フォールバック: 最小限のサンプルデータ
        return [{
            'id': 1,
            'category': 'サンプル',
            'question': 'これはサンプル問題です。',
            'option_a': '選択肢A',
            'option_b': '選択肢B', 
            'option_c': '選択肢C',
            'option_d': '選択肢D',
            'correct_answer': 'A',
            'explanation': 'サンプル問題の説明です。',
            'question_type': 'basic',
            'department': 'common',
            'year': None
        }]

# 基本ルート
@app.route('/')
def index():
    """ホームページ"""
    try:
        # 初期データ読み込み
        questions = load_questions()
        
        # 統計情報
        basic_count = len([q for q in questions if q.get('question_type') == 'basic'])
        specialist_count = len([q for q in questions if q.get('question_type') == 'specialist'])
        
        return render_template('index.html', 
                             basic_count=basic_count, 
                             specialist_count=specialist_count,
                             total_count=len(questions))
    except Exception as e:
        logger.error(f"ホームページエラー: {e}")
        return f"<h1>RCCM試験問題集2025</h1><p>起動完了！問題データ読み込み中...</p><p>エラー: {e}</p>"

@app.route('/health')
def health_check():
    """ヘルスチェック"""
    return jsonify({
        'status': 'healthy',
        'version': '2025.1.0-exe',
        'questions_loaded': len(_questions_cache) if _questions_cache else 0,
        'timestamp': datetime.now().isoformat()
    })

# エラーハンドラー
@app.errorhandler(404)
def not_found(error):
    return "<h1>404 - ページが見つかりません</h1><p><a href='/'>ホームに戻る</a></p>", 404

@app.errorhandler(500)
def internal_error(error):
    return f"<h1>500 - サーバーエラー</h1><p>エラー: {error}</p><p><a href='/'>ホームに戻る</a></p>", 500

if __name__ == '__main__':
    # EXE版専用起動処理
    print("="*50)
    print("  RCCM試験問題集2025 Enterprise Edition")
    print("  一般配布版")
    print("="*50)
    print()
    
    # ポート自動検出
    port = find_free_port()
    url = f"http://127.0.0.1:{port}"
    
    print(f"🚀 アプリケーションを起動しています...")
    print(f"📡 ポート: {port}")
    print(f"🌐 URL: {url}")
    print()
    print("⏳ ブラウザが自動で開きます（3秒後）...")
    print("📖 使い方はブラウザ内の「ヘルプ」をご確認ください")
    print()
    print("❌ 終了時はこのウィンドウを閉じてください")
    print("="*50)
    
    # データ事前読み込み
    try:
        questions = load_questions()
        print(f"✅ 問題データ読み込み完了: {len(questions)}問")
    except Exception as e:
        print(f"⚠️  問題データ読み込み警告: {e}")
    
    # ブラウザを遅延オープン
    open_browser_delayed(url, delay=3)
    
    try:
        # Flaskアプリ起動
        app.run(
            host='127.0.0.1',
            port=port,
            debug=False,  # EXE版ではDebugオフ
            use_reloader=False,  # リローダー無効
            threaded=True  # マルチスレッド有効
        )
    except KeyboardInterrupt:
        print("\n🛑 アプリケーションを終了します...")
    except Exception as e:
        print(f"\n❌ 起動エラー: {e}")
        print("手動でブラウザからアクセスしてください:")
        print(f"URL: {url}")
        input("\nEnterキーを押して終了...")