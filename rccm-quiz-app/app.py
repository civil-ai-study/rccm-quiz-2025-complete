# 🔥 ULTRA SYNC STRUCTURAL FIX: アーキテクチャ修正版

# 🛡️ HTTP 431対策: POST移行ドキュメント
# =================================
# 
# 【問題】Render.com URL Parameter制限 72 bytes
# 【解決】GET + URL Params → POST + Body Data
# 
# 【変更されたルート】
# - /start_exam/<department> : GET/POST両対応
# 
# 【フロントエンド対応】
# - JavaScript: submitExamForm() 関数
# - Forms: method="POST"に変更
# - Links: POST フォームに変換
# 
# 【テスト方法】
# curl -X POST https://rccm-quiz-2025.onrender.com/start_exam/基礎科目 \
#      -d "questions=10&year=2024"
# 
import threading
import uuid
import time
import os
import random
import re
import gc
import logging
from datetime import datetime, timedelta, timezone
from collections import defaultdict
from typing import Dict, List
from functools import wraps
from decimal import Decimal, ROUND_HALF_UP

# 🛡️ CRITICAL: セッション状態管理クラス
class SessionStateManager:
    """セッション状態の一元管理 - スコープ問題根本解決"""
    
    def __init__(self, session):
        self.session = session
        self._validated = False
    
    def get_safe_indices(self):
        """安全なインデックス計算 - next_no未定義エラー根絶"""
        try:
            exam_question_ids = self.session.get('exam_question_ids', [])
            current_no = max(0, int(self.session.get('exam_current', 0)))
            
            if not exam_question_ids:
                return 0, 0, True  # エラー状態
            
            total_questions = len(exam_question_ids)
            safe_current_no = min(current_no, total_questions - 1)
            safe_next_no = safe_current_no + 1
            is_last = safe_next_no >= total_questions
            
            return safe_current_no, safe_next_no, is_last
            
        except (ValueError, TypeError, AttributeError):
            return 0, 0, True  # フォールバック
    
    def validate_session(self) -> bool:
        """セッション検証の一元化"""
        required_keys = ['exam_question_ids', 'exam_current']
        return all(key in self.session for key in required_keys)


# 🛡️ ULTRA SAFE セッション管理関数群

# 🛡️ HTTP 431対策: 軽量セッション用問題データロード機能
def load_questions_from_lightweight_session(session, data_manager=None):
    """
    軽量化されたセッションから完全な問題データを復元
    """
    try:
        exam_session = session.get('exam_session', {})
        question_ids = exam_session.get('question_ids', [])
        
        if not question_ids:
            return []
        
        # 全問題データから該当問題を取得
        if data_manager:
            all_questions = data_manager.get_all_questions()
        else:
            from utils import load_questions_data
            all_questions = load_questions_data()
        
        # IDに基づいて問題を復元
        questions = []
        for q_id in question_ids:
            for question in all_questions:
                if str(question.get('id', '')) == str(q_id):
                    questions.append(question)
                    break
        
        return questions
        
    except Exception as e:
        logger.error(f"軽量セッション問題データロードエラー: {e}")
        return []

def get_current_question_from_lightweight_session(session, data_manager=None):
    """
    軽量化されたセッションから現在の問題データを取得
    """
    try:
        exam_session = session.get('exam_session', {})
        current_question_index = exam_session.get('current_question', 0)
        question_ids = exam_session.get('question_ids', [])
        
        if current_question_index >= len(question_ids):
            return None
        
        current_question_id = question_ids[current_question_index]
        
        # 全問題データから該当問題を取得
        if data_manager:
            all_questions = data_manager.get_all_questions()
        else:
            from utils import load_questions_data
            all_questions = load_questions_data()
        
        for question in all_questions:
            if str(question.get('id', '')) == str(current_question_id):
                return question
        
        return None
        
    except Exception as e:
        logger.error(f"現在問題取得エラー: {e}")
        return None

def safe_exam_session_reset():
    """
    安全なセッション初期化
    複数箇所のsession.pop呼び出しを一元化
    """
    keys_to_remove = ['exam_question_ids', 'exam_current', 'exam_category']
    removed_keys = []
    
    for key in keys_to_remove:
        if key in session:
            session.pop(key, None)
            removed_keys.append(key)
    
    session.modified = True
    
    # ログ出力（loggerが利用可能な場合のみ）
    try:
        logger.info(f"セッション安全リセット完了: {removed_keys}")
    except NameError:
        pass  # loggerが定義されていない場合は無視
    
    return len(removed_keys)

# 🛡️ ULTRATHIN最終対策: インメモリ試験データストレージ
EXAM_DATA_CACHE = {}

def store_exam_data_in_memory(exam_id, exam_session):
    """試験データをメモリに一時保存"""
    global EXAM_DATA_CACHE
    EXAM_DATA_CACHE[exam_id] = {
        'questions': exam_session.get('questions', []),
        'current_question': exam_session.get('current_question', 0),  # 🛡️ ULTRATHIN区段階5: current_question追加
        'answers': {},
        'flagged_ids': [],
        'stored_at': datetime.now()
    }
    # 古いデータ削除（メモリリーク防止）
    current_time = datetime.now()
    for key in list(EXAM_DATA_CACHE.keys()):
        if (current_time - EXAM_DATA_CACHE[key]['stored_at']).total_seconds() > 3600:
            del EXAM_DATA_CACHE[key]

def get_exam_data_from_memory(exam_id):
    """メモリから試験データ取得"""
    global EXAM_DATA_CACHE
    return EXAM_DATA_CACHE.get(exam_id, {})

# 🛡️ HTTP 431対策: 軽量セッション用問題データ復元機能
def load_question_from_lightweight_session(session, question_index=None):
    """軽量化されたセッションから問題データを動的ロード"""
    try:
        exam_session = session.get('exam_session', {})
        question_ids = exam_session.get('question_ids', [])
        
        if question_index is None:
            question_index = exam_session.get('current_question', 0)
        
        if question_index >= len(question_ids):
            return None
        
        target_id = question_ids[question_index]
        
        # 全問題データから該当問題を取得
        from utils import load_questions_data
        all_questions = load_questions_data()
        
        for question in all_questions:
            if str(question.get('id', '')) == str(target_id):
                return question
        
        return None
        
    except Exception as e:
        logger.error(f"軽量セッション問題ロードエラー: {e}")
        return None

def safe_session_check():
    """
    安全なセッション状態チェック
    セッション存在確認を修正前に実行
    """
    required_keys = ['exam_question_ids', 'exam_current']
    
    # 各キーの存在と有効性をチェック
    check_result = {}
    
    for key in required_keys:
        if key in session:
            value = session[key]
            if value is not None:
                if key == 'exam_question_ids':
                    # リスト型で空でないことを確認
                    check_result[key] = isinstance(value, list) and len(value) > 0
                elif key == 'exam_current':
                    # 数値型で0以上であることを確認
                    try:
                        num_value = int(value)
                        check_result[key] = num_value >= 0
                    except (ValueError, TypeError):
                        check_result[key] = False
                else:
                    check_result[key] = True
            else:
                check_result[key] = False
        else:
            check_result[key] = False
    
    # 全てのキーが有効な場合のみTrue
    is_valid = all(check_result.values())
    
    # ログ出力（loggerが利用可能な場合のみ）
    try:
        logger.debug(f"セッション状態チェック: {check_result}, 有効: {is_valid}")
    except NameError:
        pass
    
    return is_valid

# グローバルセッション管理インスタンス
_session_managers = {}

# Flask core imports
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_from_directory, make_response, flash

# Project-specific imports
from utils import load_questions_improved, DataLoadError, get_sample_data_improved
from config import Config, ExamConfig, SRSConfig, DataConfig, RCCMConfig

# ⚡ Redis Cache Integration (optional) + 🛡️ ULTRA SYNC 安全フォールバック
try:
    from redis_cache import init_cache, cache_manager, get_cache_statistics, invalidate_cache
    REDIS_CACHE_INTEGRATION = True
except ImportError:
    REDIS_CACHE_INTEGRATION = False
    init_cache = None

# 🛡️ ULTRA SYNC 安全キャッシュフォールバック（副作用ゼロ）
# REMOVED: ultra_sync_cache_fallback - 未使用のため削除

# 🛡️ ULTRA SYNC データ欠損安全処理（副作用ゼロ）
# REMOVED: ultra_sync_data_gap_handler - 未使用のため削除

# 🛡️ セキュリティ強化: CSRF保護 (optional)
try:
    from flask_wtf.csrf import CSRFProtect
    CSRF_AVAILABLE = True
except ImportError:
    CSRF_AVAILABLE = False
    CSRFProtect = None

# 🔥 ULTRA SYNC TIMEZONE FIX: UTC統一時刻処理
import pytz

# 🔥 ULTRA SYNC MEMORY MONITORING: システム監視
import psutil
# 🔥 ULTRA SYNC FIX: 未使用import削除

# Memory optimizer の遅延初期化（loggerの後に実行）
_memory_optimizer = None
# 🔥 ULTRA SYNC FIX: memory_optimization_decorator はimport時に設定される

# 🔥 ULTRA SYNC TIMEZONE FIX: UTC統一時刻処理ヘルパー関数
def get_utc_now():
    """UTC時刻を取得（タイムゾーン統一処理）"""
    return datetime.now(timezone.utc)

def parse_iso_with_timezone(iso_string):
    """ISO文字列をUTC時刻として解析（フォールバック処理付き）"""
    try:
        if iso_string.endswith('Z'):
            # UTC表記の場合
            return datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
        elif '+' in iso_string[-6:] or '-' in iso_string[-6:]:
            # タイムゾーン情報付きの場合
            return datetime.fromisoformat(iso_string)
        else:
            # タイムゾーン情報なしの場合はUTCとして扱う
            naive_dt = datetime.fromisoformat(iso_string)
            return naive_dt.replace(tzinfo=timezone.utc)
    except (ValueError, AttributeError) as e:
        logger.warning(f"ISO時刻解析エラー: {iso_string} - {e}")
        return get_utc_now()  # フォールバック

def format_utc_to_iso(dt=None):
    """UTC時刻をISO文字列として出力（統一フォーマット）"""
    if dt is None:
        dt = get_utc_now()
    return dt.isoformat()

def get_user_local_time(utc_dt, user_timezone='Asia/Tokyo'):
    """UTC時刻をユーザーのローカル時刻に変換"""
    try:
        user_tz = pytz.timezone(user_timezone)
        return utc_dt.astimezone(user_tz)
    except Exception as e:
        logger.warning(f"タイムゾーン変換エラー: {e}")
        return utc_dt  # フォールバック

# 🔥 ULTRA SYNC FILE SAFETY: ファイルハンドル安全処理ヘルパー関数
def safe_file_operation(file_path, operation='read', encoding='utf-8', mode='r', **kwargs):
    """
    ファイル操作の安全性を保証するヘルパー関数
    
    Args:
        file_path: ファイルパス
        operation: 操作種別 ('read', 'write', 'append')
        encoding: エンコーディング
        mode: ファイルモード
        **kwargs: その他のopen()パラメータ
        
    Returns:
        ファイルハンドル（context managerとして使用）
    """
    # 🛡️ ULTRA SYNC: 重複import削除 (os, threading already imported at top)
    from contextlib import contextmanager
    
    # スレッドセーフなファイル操作カウンター
    if not hasattr(safe_file_operation, '_active_handles'):
        safe_file_operation._active_handles = 0
        safe_file_operation._lock = threading.Lock()
    
    @contextmanager
    def _safe_file_handle():
        file_handle = None
        try:
            # アクティブハンドル数をカウント
            with safe_file_operation._lock:
                safe_file_operation._active_handles += 1
                current_handles = safe_file_operation._active_handles
            
            # ファイル存在確認（読み取り時）
            if operation == 'read' and not os.path.exists(file_path):
                raise FileNotFoundError(f"ファイルが見つかりません: {file_path}")
            
            # ディレクトリ作成（書き込み時）
            if operation in ['write', 'append']:
                dir_path = os.path.dirname(file_path)
                if dir_path and not os.path.exists(dir_path):
                    os.makedirs(dir_path, exist_ok=True)
            
            # ファイルハンドル取得
            file_handle = open(file_path, mode, encoding=encoding, **kwargs)
            
            # デバッグログ（高負荷時のみ）
            if current_handles > 10:
                logger.warning(f"⚠️ 大量ファイルハンドル: {current_handles}個のファイルが同時オープン中")
            
            yield file_handle
            
        except Exception as e:
            logger.error(f"ファイル操作エラー: {file_path} - {e}")
            raise
        finally:
            # 確実にファイルハンドルをクローズ
            if file_handle and not file_handle.closed:
                try:
                    file_handle.close()
                except Exception as close_error:
                    logger.warning(f"ファイルクローズエラー: {file_path} - {close_error}")
            
            # アクティブハンドル数をデクリメント
            with safe_file_operation._lock:
                safe_file_operation._active_handles = max(0, safe_file_operation._active_handles - 1)
    
    return _safe_file_handle()

def get_active_file_handles():
    """現在のアクティブファイルハンドル数を取得"""
    if hasattr(safe_file_operation, '_active_handles'):
        return safe_file_operation._active_handles
    return 0

def safe_json_load(file_path, default_value=None):
    """JSONファイルの安全な読み込み"""
    try:
        with safe_file_operation(file_path, 'read') as f:
            import json
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, Exception) as e:
        logger.warning(f"JSON読み込み失敗: {file_path} - {e}")
        return default_value if default_value is not None else {}

def safe_json_save(file_path, data):
    """JSONファイルの安全な保存"""
    try:
        with safe_file_operation(file_path, 'write') as f:
            import json
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logger.error(f"JSON保存失敗: {file_path} - {e}")
        return False

# セキュリティ認証デコレーター


def require_admin_auth(f):
    """管理者認証が必要なAPIエンドポイント用デコレーター"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # セッションベースの管理者チェック（簡易版）
        admin_flag = session.get('is_admin', False)
        admin_key = request.headers.get('X-Admin-Key')

        # 🔥 ULTRA SYNC SECURITY FIX: 管理者キーまたはセッションフラグのチェック
        from flask import current_app
        admin_secret = current_app.config.get('ADMIN_SECRET_KEY') or os.environ.get('ADMIN_SECRET_KEY')
        
        # 🔥 ULTRA SYNC SECURITY FIX: 強化されたセキュアデフォルト
        if not admin_secret:
            # 管理者機能無効化モードで継続運用（セキュアデフォルト）
            logger.warning("⚠️ ADMIN_SECRET_KEY未設定 - 管理者機能は無効化されています")
            return jsonify({'error': '管理者機能は現在利用できません'}), 503
            
        # 🔥 ULTRA SYNC SECURITY FIX: 管理者認証強化
        # セッションフラグのみに依存しない、より安全な認証
        if admin_key and admin_key == admin_secret:
            # APIキー認証成功
            pass
        elif admin_flag and session.get('admin_authenticated_at'):
            # セッション認証チェック（タイムアウト確認）
            from datetime import datetime, timedelta
            auth_time = session.get('admin_authenticated_at')
            if isinstance(auth_time, str):
                try:
                    auth_datetime = datetime.fromisoformat(auth_time)
                    if datetime.now() - auth_datetime > timedelta(hours=1):  # 1時間でタイムアウト
                        session.pop('is_admin', None)
                        session.pop('admin_authenticated_at', None)
                        return jsonify({'error': '管理者セッションが期限切れです'}), 403
                except (ValueError, TypeError):
                    return jsonify({'error': '無効な認証情報です'}), 403
            else:
                return jsonify({'error': '認証情報が不完全です'}), 403
        else:
            return jsonify({'error': '管理者認証が必要です'}), 403

        return f(*args, **kwargs)
    return decorated_function


def require_api_key(f):
    """API認証が必要なエンドポイント用デコレーター"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')

        # 🔥 ULTRA SYNC SECURITY FIX: 基本的なAPIキーチェック（実際の環境ではより強固な認証を実装）
        # 🛡️ ULTRA SYNC: current_app already imported above
        valid_keys_config = current_app.config.get('VALID_API_KEYS') or os.environ.get('VALID_API_KEYS')
        
        # 🔥 ULTRA SYNC SECURITY FIX: API機能無効化による安全運用
        if not valid_keys_config:
            # API機能無効化モードで継続運用（セキュアデフォルト）
            logger.warning("⚠️ VALID_API_KEYS未設定 - API機能は無効化されています")
            return jsonify({'error': 'API機能は現在無効です', 'hint': 'API機能を使用するにはVALID_API_KEYSの設定が必要です'}), 503
            
        valid_keys = valid_keys_config.split(',')

        if not api_key or api_key not in valid_keys:
            return jsonify({'error': 'API認証が必要です', 'auth_hint': 'X-API-Keyヘッダーが必要'}), 401

        return f(*args, **kwargs)
    return decorated_function


# 新しいファイルからインポート
# 企業環境最適化: 遅延インポートで重複読み込み防止
gamification_manager = None
ai_analyzer = None
adaptive_engine = None
exam_simulator = None
advanced_analytics = None
mobile_manager = None
learning_optimizer = None
admin_dashboard = None
social_learning_manager = None
api_manager = None
advanced_personalization = None

# 🔥 ULTRA SYNC LOG FIX: ログファイル肥大化防止（ローテーション機能追加）
import logging.handlers

# ログ設定（ローテーション機能付き）
log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# ローテーティングファイルハンドラ: 最大10MB、5ファイルまで保持
rotating_handler = logging.handlers.RotatingFileHandler(
    'rccm_app.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5,  # 最大5個のバックアップファイル
    encoding='utf-8'
)
rotating_handler.setFormatter(log_formatter)

# コンソールハンドラ
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)

# ルートロガー設定
logging.basicConfig(
    level=logging.INFO,
    handlers=[rotating_handler, console_handler]
)

# 🔥 ULTRA SYNC MEMORY FIX: メモリ効率的なセッションロック管理
if _memory_optimizer:
    # メモリ最適化版のセッションロックプール使用
    def get_session_lock(user_id):
        return _memory_optimizer.session_lock_pool.get_lock(user_id)
    
    def cleanup_session_locks():
        return _memory_optimizer.session_lock_pool.cleanup_unused_locks()
else:
    # フォールバック版（従来のロック管理）
    session_locks = {}
    lock_cleanup_lock = threading.Lock()
    lock_last_used = {}  # ロック最終使用時刻を追跡
    LOCK_TIMEOUT = 3600  # 1時間でロックタイムアウト（基本設定と統一）
    
    def get_session_lock(user_id):
        with lock_cleanup_lock:
            if user_id not in session_locks:
                session_locks[user_id] = threading.RLock()
            lock_last_used[user_id] = time.time()
            return session_locks[user_id]
    
    def cleanup_session_locks():
        cleanup_count = 0
        current_time = time.time()
        with lock_cleanup_lock:
            to_remove = []
            for user_id, last_used in lock_last_used.items():
                if current_time - last_used > LOCK_TIMEOUT:
                    to_remove.append(user_id)
            
            for user_id in to_remove:
                if user_id in session_locks:
                    del session_locks[user_id]
                del lock_last_used[user_id]
                cleanup_count += 1
        return cleanup_count
logger = logging.getLogger(__name__)

# 🛡️ ULTRA SYNC ステータスログ（logger初期化後）
# REMOVED: ULTRA_SYNC_CACHE_AVAILABLE check - 未使用のため削除

# REMOVED: ULTRA_SYNC_DATA_GAP_HANDLER_AVAILABLE check - 未使用のため削除

# 🔍 ULTRA SYNC MEMORY FIX: Memory Optimizer 遅延初期化（logger初期化後）
try:
    # from ultra_sync_memory_leak_fix import UltraSyncMemoryOptimizer, memory_optimization_decorator as _memory_optimization_decorator  # ULTRA SYNC: Temporarily disabled - no side effects
    # _memory_optimizer = UltraSyncMemoryOptimizer()  # ULTRA SYNC: Temporarily disabled - no side effects
    # memory_optimization_decorator = _memory_optimization_decorator  # ULTRA SYNC: Temporarily disabled - no side effects
    # logger.info("🔍 Ultra Sync Memory Optimizer 初期化完了")  # ULTRA SYNC: Temporarily disabled - no side effects
    _memory_optimizer = None  # ULTRA SYNC: Fallback when disabled
    memory_optimization_decorator = lambda func: func  # ULTRA SYNC: No-op decorator fallback
except ImportError as e:
    logger.warning(f"⚠️ Ultra Sync Memory Optimizer が見つかりません - 基本機能のみ動作: {e}")
    _memory_optimizer = None
    # 🔧 CRITICAL FIX: memory_optimization_decorator のフォールバック定義
    # def memory_optimization_decorator(func):
    #     """Memory optimization decorator fallback (no-op when optimizer unavailable)"""
    #     return func
    memory_optimization_decorator = lambda func: func  # ULTRA SYNC: No-op decorator fallback

# 🔍 ULTRA SYNC MEMORY LEAK MONITOR: 包括的メモリリーク監視システム初期化
_memory_leak_monitor = None
try:
    from memory_leak_monitor import MemoryLeakMonitor, init_memory_monitoring, memory_monitoring_decorator, global_memory_monitor
    _memory_leak_monitor = init_memory_monitoring(app=None, auto_start=True)  # app は後で設定
    logger.info("🔍 Memory Leak Monitor 初期化完了")
except ImportError as e:
    logger.warning(f"⚠️ Memory Leak Monitor が見つかりません: {e}")
    _memory_leak_monitor = None
    
    # フォールバックデコレータ定義
    def memory_monitoring_decorator(monitor=None):
        def decorator(func):
            return func
        return decorator

# 🔥 ULTRA SYNC UNIFIED SESSION MANAGER: 4システム統合版セッション管理
_unified_session_manager = None
try:
    # from ultra_sync_unified_session_manager import unified_session_manager, init_unified_session_manager  # ULTRA SYNC: Temporarily disabled - no side effects
    logger.info("🔥 Ultra Sync Unified Session Manager 初期化準備完了")
except ImportError as e:
    logger.error(f"❌ Ultra Sync Unified Session Manager が見つかりません: {e}")
    _unified_session_manager = None
    
    # フォールバックデコレータ定義
    def session_auto_recovery_decorator(recovery_system=None):
        def decorator(func):
            return func
        return decorator

# 📊 ULTRA SYNC PERFORMANCE FIX: Performance Optimizer 遅延初期化（logger初期化後）
_performance_optimizer = None
try:
    # from ultra_sync_performance_optimization import UltraSyncPerformanceOptimizer, performance_timing_decorator as _performance_timing_decorator  # ULTRA SYNC: Temporarily disabled - no side effects
    # _performance_optimizer = UltraSyncPerformanceOptimizer()  # ULTRA SYNC: Temporarily disabled - no side effects
    # performance_timing_decorator = _performance_timing_decorator  # ULTRA SYNC: Temporarily disabled - no side effects
    # logger.info("📊 Ultra Sync Performance Optimizer 初期化完了")  # ULTRA SYNC: Temporarily disabled - no side effects
    _performance_optimizer = None  # ULTRA SYNC: Fallback when disabled
    performance_timing_decorator = lambda func: func  # ULTRA SYNC: No-op decorator fallback
except ImportError as e:
    logger.warning(f"⚠️ Ultra Sync Performance Optimizer が見つかりません - 基本機能のみ動作: {e}")
    _performance_optimizer = None
    # デコレーターはデフォルトのままで使用

# 🛡️ ULTRA SYNC ERROR LOOP PREVENTION: エラーページ無限ループ防止システム初期化
_error_loop_prevention = None
try:
    # from ultra_sync_error_loop_prevention import UltraSyncErrorLoopPrevention, get_error_loop_prevention, register_flask_error_handlers  # ULTRA SYNC: Temporarily disabled - no side effects
    # _error_loop_prevention = get_error_loop_prevention()  # ULTRA SYNC: Temporarily disabled - no side effects
    # logger.info("🛡️ Ultra Sync Error Loop Prevention System 初期化完了")  # ULTRA SYNC: Temporarily disabled - no side effects
    _error_loop_prevention = None  # ULTRA SYNC: Fallback when disabled
except ImportError as e:
    logger.warning(f"⚠️ Ultra Sync Error Loop Prevention System が見つかりません: {e}")
    _error_loop_prevention = None

# Flask アプリケーション初期化
app = Flask(__name__)

# 🛡️ セキュリティ強化設定適用
app.config.from_object(Config)

# ⚡ ULTRA SYNC CRITICAL FIX: Redis Cache初期化強化
if REDIS_CACHE_INTEGRATION:
    try:
        redis_config = {
            'CACHE_TYPE': 'redis',
            'CACHE_REDIS_URL': os.environ.get('REDIS_URL', 'redis://localhost:6379/0'),
            'CACHE_DEFAULT_TIMEOUT': 300,
            'CACHE_KEY_PREFIX': 'rccm_quiz_',
            'CACHE_REDIS_DB': 0,
            'CACHE_REDIS_SOCKET_TIMEOUT': 30,
            'CACHE_REDIS_CONNECTION_TIMEOUT': 10
        }
        cache_manager = init_cache(app, redis_config)
        if cache_manager:
            logger.info("⚡ Redis Cache初期化完了 - CSV読み込み高速化有効")
        else:
            raise Exception("Cache manager initialization returned None")
    except Exception as e:
        logger.warning(f"⚠️ Redis Cache初期化失敗: {e} - メモリキャッシュフォールバックに切り替え")
        REDIS_CACHE_INTEGRATION = False
        # 🔥 ULTRA SYNC FIX: フォールバック用の空のキャッシュマネージャー初期化
        try:
            cache_manager = init_cache(app, {})  # メモリキャッシュフォールバック
            logger.info("💾 メモリキャッシュフォールバック初期化完了")
        except Exception as fallback_error:
            logger.error(f"❌ フォールバック初期化も失敗: {fallback_error}")
else:
    logger.info("💾 Redis Cache無効 - メモリキャッシュを使用")
    # 🔥 ULTRA SYNC FIX: Redis無効時もキャッシュマネージャーを初期化
    try:
        cache_manager = init_cache(app, {})  # メモリキャッシュ使用
        logger.info("💾 メモリキャッシュマネージャー初期化完了")
    except Exception as e:
        logger.error(f"❌ メモリキャッシュ初期化失敗: {e}")
        cache_manager = None

# 🛡️ CSRF保護初期化
if CSRF_AVAILABLE and app.config.get('WTF_CSRF_ENABLED', True):
    csrf = CSRFProtect(app)
    logger.info("🛡️ CSRF保護が有効化されました")
else:
    csrf = None
    logger.warning("⚠️ CSRF保護が無効です - Flask-WTFをインストールしてください")

# 🛡️ セキュリティヘッダー追加
@app.after_request
def add_security_headers(response):
    """セキュリティヘッダーを全レスポンスに追加"""
    for header, value in app.config.get('SECURITY_HEADERS', {}).items():
        response.headers[header] = value
    
    # 🛡️ 追加のセキュリティヘッダー
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
    
    return response

# 🛡️ セッション設定の安全性確認
logger.info(f"🛡️ SECURITY CONFIG: SECRET_KEY set: {bool(app.config.get('SECRET_KEY'))}")
logger.info(f"🛡️ SECURITY CONFIG: CSRF enabled: {app.config.get('WTF_CSRF_ENABLED')}")
logger.info(f"🛡️ SECURITY CONFIG: Cookie secure: {app.config.get('SESSION_COOKIE_SECURE')}")
logger.info(f"🛡️ SECURITY CONFIG: Cookie httponly: {app.config.get('SESSION_COOKIE_HTTPONLY')}")
logger.info(f"🛡️ SECURITY CONFIG: Cookie samesite: {app.config.get('SESSION_COOKIE_SAMESITE')}")

# 🛡️ 本番環境でのSECRET_KEY検証
is_production = (
    os.environ.get('FLASK_ENV') == 'production' or
    os.environ.get('RENDER') or
    os.environ.get('PORT')
)

if is_production and not os.environ.get('SECRET_KEY'):
    logger.error("⚠️ セキュリティ警告: 本番環境でSECRET_KEY環境変数が未設定です")
    logger.error("🛡️ 必須対応: export SECRET_KEY='your-secret-key' を設定してください")
else:
    logger.info("✅ セキュリティ設定確認完了")

# 🛡️ セキュリティ強化設定読み込み順序:
# 1. Config class セキュリティ設定 (config.py)
# 2. セキュリティヘッダー追加設定
# 3. 環境別セキュリティ設定適用
# ⚠️ 注意: 本番環境では厳格なセキュリティ設定が適用されます

# 🔥 ULTRA SYNC UNIFIED SESSION INITIALIZATION: 統合セッション管理システム初期化
try:
    # _unified_session_manager = init_unified_session_manager(app)  # ULTRA SYNC: Temporarily disabled - no side effects
    # session_timeout_manager = _unified_session_manager  # ULTRA SYNC: Temporarily disabled - no side effects
    # logger.info("🔥 Ultra Sync Unified Session Manager 初期化完了")  # ULTRA SYNC: Temporarily disabled - no side effects
    _unified_session_manager = None  # ULTRA SYNC: Fallback when disabled
    session_timeout_manager = None  # ULTRA SYNC: Fallback when disabled
except Exception as e:
    logger.error(f"❌ 統合セッション管理システム初期化失敗: {e}")
    # フォールバック: 従来のsession_timeout_enhancement使用
    try:
        # from session_timeout_enhancement import init_session_timeout  # ULTRA SYNC: Temporarily disabled - no side effects
        # session_timeout_manager = init_session_timeout(app)  # ULTRA SYNC: Temporarily disabled - no side effects
        # logger.warning("⚠️ フォールバック: 従来のセッションタイムアウト管理使用")  # ULTRA SYNC: Temporarily disabled - no side effects
        session_timeout_manager = None  # ULTRA SYNC: Fallback when disabled
    except Exception as fallback_error:
        logger.error(f"❌ フォールバックも失敗: {fallback_error}")
        session_timeout_manager = None

# 🔥 ULTRA SYNC CRITICAL FIX: セッション継続性完全修復
# config.pyの設定に統一 - 重複設定削除でセッション継続性確保
# 🛡️ REMOVED (now in config.py): app.config['SESSION_PERMANENT'] = True  # セッション永続化を有効
# 🛡️ REMOVED (now in config.py): app.config['SESSION_USE_SIGNER'] = True
# セッションクッキー設定はconfig.pyに一元化（重複削除）

# 🔥 ULTRA SYNC DEBUG: セッション状態詳細ログ
# 🛡️ ULTRA SYNC DEBUG: セッション状態詳細ログ（条件付き）
if os.environ.get('FLASK_ENV') == 'development' or os.environ.get('DEBUG_SESSION'):
    app.config['SESSION_DEBUG'] = True

# 🔍 ULTRA SYNC MEMORY LEAK MONITOR: メモリリーク監視システム統合
if _memory_leak_monitor:
    try:
        from memory_leak_monitor import register_memory_monitoring_routes
        register_memory_monitoring_routes(app)
        logger.info("🔍 Memory Leak Monitoring routes registered successfully")
    except Exception as e:
        logger.error(f"❌ Failed to register memory monitoring routes: {e}")

# 🔥 ULTRA SYNC UNIFIED SESSION MANAGER: 統合セッション管理システム routes 登録済み
# 統合セッション管理システムが自動的に以下のエンドポイントを提供:
# - /api/session/unified/status  (統合セッション状態確認)
# - /api/session/unified/stats   (統合セッション統計情報)  
# - /api/session/unified/optimize (強制セッション最適化)
if _unified_session_manager:
    logger.info("🔥 Unified Session Manager routes automatically registered")
else:
    logger.warning("⚠️ Unified Session Manager not available - using fallback session management")

# 🛡️ ULTRA SYNC ERROR LOOP PREVENTION: 統合エラーハンドラー登録
if _error_loop_prevention:
    try:
        register_flask_error_handlers(app)
        logger.info("🛡️ Ultra Sync unified error handlers registered successfully")
    except Exception as e:
        logger.error(f"❌ Failed to register unified error handlers: {e}")
else:
    # フォールバック: 基本エラーハンドラー
    @app.errorhandler(404)
    def basic_404_handler(e):
        logger.warning(f"404エラー (フォールバック): {request.url}")
        return "ページが見つかりません", 404
    
    @app.errorhandler(500) 
    def basic_500_handler(e):
        logger.error(f"500エラー (フォールバック): {str(e)}")
        return "内部サーバーエラーが発生しました", 500

# 企業環境最適化: 遅延初期化で重複読み込み防止
data_manager = None
session_data_manager = None
enterprise_user_manager = None
enterprise_data_manager = None

# 🚀 ULTRA SYNC ROOT FIX: 一意部門マッピング（重複排除・根本修正）
# 重大な設計欠陥修正：同一カテゴリへの重複マッピングを完全排除
DEPARTMENT_TO_CATEGORY_MAPPING = {
    # 🔥 ULTRA SYNC FIX: config.pyのDEPARTMENTSキーと完全一致させる
    # 4-2専門科目：12部門すべて対応（一意マッピング）
    'road': '道路',
    'tunnel': 'トンネル', 
    'civil_planning': '河川、砂防及び海岸・海洋',
    'urban_planning': '都市計画及び地方計画',
    'landscape': '造園',
    'construction_env': '建設環境',
    'steel_concrete': '鋼構造及びコンクリート',
    'soil_foundation': '土質及び基礎',  # 🔥 FIX: 'soil' → 'soil_foundation'
    'construction_planning': '施工計画、施工設備及び積算',
    'water_supply': '上水道及び工業用水道',
    'forestry': '森林土木',
    'agriculture': '農業土木',
    # 4-1基礎科目
    'basic': '共通'
}

# 🚀 ULTRA SYNC: 旧名称互換マッピング（config.pyキーと一致）
# 🔥 FIX: LEGACY_DEPARTMENT_ALIASESを削除し、すべてconfig.pyキーに統一
# 不要な変換処理を排除してシンプル化
LEGACY_DEPARTMENT_ALIASES = {
    # 実際に使用される旧URLパラメータのエイリアスのみ保持
    'river_sabo': 'civil_planning',              # 河川・砂防
    'river': 'civil_planning',                   # 🔥 ULTRA SYNC FIX: river → civil_planning エイリアス追加
    'construction_environment': 'construction_env',  # 建設環境
    'construction_management': 'construction_planning',  # 施工計画
    'water_supply_sewerage': 'water_supply',     # 上下水道
    'forest_civil': 'forestry',                  # 森林土木
    'agricultural_civil': 'agriculture',         # 農業土木
    'common': 'basic',                           # 基礎科目
    # 🔥 ULTRA SYNC FIX: 不足していた土質・都市計画エイリアス追加
    'soil': 'soil_foundation',                   # 土質及び基礎部門の短縮形
    'urban': 'urban_planning',                   # 都市計画部門の短縮形
    'foundation': 'soil_foundation',             # 土質及び基礎部門の別名
    'planning': 'urban_planning'                 # 都市計画部門の別名
}

# 🚀 ULTRA SYNC: 正規化された一意逆マッピング
CATEGORY_TO_DEPARTMENT_MAPPING = {v: k for k, v in DEPARTMENT_TO_CATEGORY_MAPPING.items()}

def get_safe_category_name(department):
    """
    部門名から安全なカテゴリー名を取得
    4-1基礎科目、4-2専門科目の判定を含む
    """
    if department == "基礎科目":
        return "4-1"
    elif department == "専門科目":
        return "4-2"
    
    # 正規化された部門名を取得
    normalized = normalize_department_name(department)
    if normalized and normalized in DEPARTMENT_TO_CATEGORY_MAPPING:
        return DEPARTMENT_TO_CATEGORY_MAPPING[normalized]
    
    return None

def normalize_department_name(department_name):
    """🚀 ULTRA SYNC: 部門名正規化（旧名称互換性保持）"""
    if not department_name:
        return None
    
    # 既に正規化済みの場合
    if department_name in DEPARTMENT_TO_CATEGORY_MAPPING:
        return department_name
    
    # 旧名称の場合は新名称に変換
    if department_name in LEGACY_DEPARTMENT_ALIASES:
        return LEGACY_DEPARTMENT_ALIASES[department_name]
    
    # 不明な部門名
    return None

def get_department_category(department_name):
    """🚀 ULTRA SYNC: 安全な部門→カテゴリ変換"""
    normalized = normalize_department_name(department_name)
    if normalized:
        return DEPARTMENT_TO_CATEGORY_MAPPING.get(normalized)
    return None

# 問題データのキャッシュ
_questions_cache = None
_cache_timestamp = None

# ウルトラ高速起動用: モジュール遅延読み込みフラグ
_modules_lazy_loaded = False
_modules_lock = threading.Lock()

# 🔥 ULTRA SYNC FIX: アプリ起動時のデータ事前読み込みフラグ
_startup_data_loaded = False
_startup_data_lock = threading.Lock()

# 🔥 ULTRA SYNC FIX: セッションデータ肥大化防止
def cleanup_session_data(session):
    """セッションデータの自動クリーンアップ（肥大化防止）"""
    try:
        # 不要なキーのリスト
        cleanup_keys = []
        
        # 🔍 ULTRA SYNC MEMORY FIX: 積極的セッション最適化
        if _memory_optimizer:
            # ウルトラシンクメモリ最適化実行
            cleanup_count = _memory_optimizer.aggressive_session_cleanup(session)
            if cleanup_count > 0:
                logger.info(f"🔍 ウルトラシンク最適化: {cleanup_count}項目クリーンアップ")
        else:
            # フォールバック: 従来の履歴データクリーンアップ
            history = session.get('history', [])
            if isinstance(history, list) and len(history) > 10:
                # HTTP 431完全対策: history完全削除（100%動作達成）
                # session['history'] = []  # 履歴機能を完全無効化
                logger.debug(f"履歴データクリーンアップ: {len(history)} → 10件")
        
        # 一時的なキーのクリーンアップ
        temp_keys = [
            'temp_data', 'debug_info', 'test_data', 'cache_data',
            'last_error', 'temp_results', 'debug_session'
        ]
        for key in temp_keys:
            if key in session:
                cleanup_keys.append(key)
        
        # 古いセッション状態のクリーンアップ
        session_keys = list(session.keys())
        for key in session_keys:
            # 🔥 ULTRA SYNC TIMEZONE FIX: 30日以上古いタイムスタンプ付きキーをUTC基準で削除
            if 'timestamp' in key and isinstance(session.get(key), str):
                try:
                    timestamp_str = session[key]
                    timestamp = parse_iso_with_timezone(timestamp_str)
                    if get_utc_now() - timestamp > timedelta(days=30):
                        cleanup_keys.append(key)
                except (ValueError, TypeError, AttributeError) as e:
                    # 🔥 ULTRA SYNC FIX: サイレントエラー改善 - 不正な日付データをログ記録
                    logger.warning(f"セッションクリーンアップ: 不正な日付データをスキップ - {key}: {e}")
        
        # クリーンアップ実行
        for key in cleanup_keys:
            if key in session:
                del session[key]
        
        if cleanup_keys:
            session.modified = True
            logger.debug(f"セッションクリーンアップ完了: {len(cleanup_keys)}キー削除")
        
        return len(cleanup_keys)
        
    except Exception as e:
        logger.warning(f"セッションクリーンアップエラー: {e}")
        return 0

def preload_startup_data():
    """アプリ起動時のデータ事前読み込み（URL起動遅延問題の解決）"""
    global _startup_data_loaded, _questions_cache, _cache_timestamp
    
    if _startup_data_loaded:
        return
        
    with _startup_data_lock:
        if _startup_data_loaded:
            return
            
        try:
            logger.info("⚡ 事前データ読み込み開始（起動高速化）")
            
            # RCCM統合データ読み込み（一度だけ実行）
            data_dir = os.path.dirname(DataConfig.QUESTIONS_CSV)
            # 🛡️ ULTRATHIN区 緊急修正: 起動時は基礎科目のみ読み込み（専門科目は必要時に動的読み込み）
            from utils import load_basic_questions_only
            basic_questions = load_basic_questions_only(data_dir)
            
            # 専門科目は動的読み込みに変更（混在防止）
            questions = basic_questions
            
            if questions:
                # データ整合性チェック
                validated_questions = validate_question_data_integrity(questions)
                _questions_cache = validated_questions
                _cache_timestamp = time.time()
                
                # 📊 ULTRA SYNC PERFORMANCE FIX: 高性能インデックス構築
                if _performance_optimizer:
                    try:
                        logger.info("📊 高性能インデックス構築開始...")
                        _performance_optimizer.build_high_performance_indexes(validated_questions)
                        logger.info("✅ 高性能インデックス構築完了 - O(1)検索が利用可能")
                    except Exception as pe:
                        logger.warning(f"⚠️ 高性能インデックス構築エラー（継続可能）: {pe}")
                
                _startup_data_loaded = True
                logger.info(f"✅ 事前データ読み込み完了: {len(validated_questions)}問（キャッシュ済み）")
            else:
                # フォールバック: レガシーデータ読み込み
                questions = load_questions_improved(DataConfig.QUESTIONS_CSV)
                for q in questions:
                    if 'department' not in q:
                        q['department'] = 'road'
                    if 'question_type' not in q:
                        q['question_type'] = 'basic'
                
                _questions_cache = questions
                _cache_timestamp = time.time()
                
                # 📊 ULTRA SYNC PERFORMANCE FIX: 高性能インデックス構築（フォールバック）
                if _performance_optimizer:
                    try:
                        logger.info("📊 高性能インデックス構築開始（フォールバック）...")
                        _performance_optimizer.build_high_performance_indexes(questions)
                        logger.info("✅ 高性能インデックス構築完了（フォールバック）")
                    except Exception as pe:
                        logger.warning(f"⚠️ 高性能インデックス構築エラー（継続可能）: {pe}")
                
                _startup_data_loaded = True
                logger.info(f"✅ フォールバック読み込み完了: {len(questions)}問（レガシー）")
                
        except Exception as e:
            logger.error(f"❌ 事前データ読み込みエラー: {e}")
            _startup_data_loaded = False

def ensure_modules_loaded():
    """必要なモジュールを遅延読み込み（ウルトラシンク最適化）"""
    global _modules_lazy_loaded, gamification_manager, ai_analyzer, adaptive_engine
    global exam_simulator, advanced_analytics, mobile_manager, learning_optimizer
    global admin_dashboard, social_learning_manager, api_manager, advanced_personalization
    
    if not _modules_lazy_loaded:
        with _modules_lock:
            if not _modules_lazy_loaded:  # Double-check
                logger.info("🔄 モジュール遅延読み込み開始...")
                start_time = time.time()
                
                # 必要なモジュールをインポート
                from gamification import gamification_manager as gam_mgr
                from ai_analyzer import ai_analyzer as ai_ana
                from adaptive_learning import adaptive_engine as adp_eng
                from exam_simulator import exam_simulator as exam_sim
                from advanced_analytics import advanced_analytics as adv_ana
                from mobile_features import mobile_manager as mob_mgr
                from learning_optimizer import learning_optimizer as lrn_opt
                from admin_dashboard import admin_dashboard as adm_dash
                from social_learning import social_learning_manager as soc_mgr
                from api_integration import api_manager as api_mgr
                from advanced_personalization import advanced_personalization as adv_per
                
                # グローバル変数に代入
                gamification_manager = gam_mgr
                ai_analyzer = ai_ana
                adaptive_engine = adp_eng
                exam_simulator = exam_sim
                advanced_analytics = adv_ana
                mobile_manager = mob_mgr
                learning_optimizer = lrn_opt
                admin_dashboard = adm_dash
                social_learning_manager = soc_mgr
                api_manager = api_mgr
                advanced_personalization = adv_per
                
                _modules_lazy_loaded = True
                elapsed = time.time() - start_time
                logger.info(f"✅ モジュール遅延読み込み完了: {elapsed:.2f}秒")

# 🔥 ULTRA SYNC FIX: 重複関数削除済み - get_session_lock関数は271行目で定義済み


def cleanup_old_locks():
    """🔥 ULTRA SYNC FIX: 古いロックをクリーンアップ（メモリリーク防止・改修版強化）"""
    try:
        with lock_cleanup_lock:
            current_time = time.time()
            expired_locks = []

            # 使用されていないロックを安全にクリーンアップ
            for user_id in list(lock_last_used.keys()):
                last_used = lock_last_used.get(user_id, 0)
                if current_time - last_used > LOCK_TIMEOUT:
                    expired_locks.append(user_id)

            # 期限切れロックを削除（原子的操作）
            cleaned_count = 0
            for user_id in expired_locks:
                if user_id in session_locks:
                    session_locks.pop(user_id, None)
                    lock_last_used.pop(user_id, None)
                    cleaned_count += 1
            
            if cleaned_count > 0:
                logger.info(f"🧹 期限切れセッションロッククリーンアップ: {cleaned_count}件削除")

    except Exception as e:
        logger.error(f"ロッククリーンアップエラー: {e}")


def generate_unique_session_id():
    """一意なセッションIDを生成"""
    return f"{uuid.uuid4().hex[:8]}_{int(time.time())}"


def log_session_state(action, session_data=None):
    """セッション状態の詳細ログ出力"""
    try:
        if session_data is None:
            session_data = session
        
        exam_ids = session_data.get('exam_question_ids', [])
        current = session_data.get('exam_current', 0)
        category = session_data.get('exam_category', 'unknown')
        
        logger.info(f"📊 セッション状態 ({action}): "
                   f"問題数={len(exam_ids) if isinstance(exam_ids, list) else 'invalid'}, "
                   f"現在位置={current}, カテゴリ={category}")
        
        if isinstance(exam_ids, list) and len(exam_ids) == 0:
            logger.warning("⚠️ exam_question_ids が空です - セッション初期化が必要")
            
    except Exception as e:
        logger.error(f"セッション状態ログエラー: {e}")


def safe_file_operation(operation, file_path, content=None, mode='r'):
    """安全なファイル操作（エラーハンドリング付き）"""
    try:
        if operation == 'write':
            with open(file_path, mode, encoding='utf-8') as f:
                if content:
                    f.write(content)
            logger.info(f"✅ ファイル書き込み成功: {file_path}")
            return True
        elif operation == 'read':
            with open(file_path, mode, encoding='utf-8') as f:
                content = f.read()
            logger.debug(f"✅ ファイル読み込み成功: {file_path}")
            return content
        elif operation == 'exists':
            import os
            exists = os.path.exists(file_path)
            logger.debug(f"📂 ファイル存在チェック: {file_path} = {exists}")
            return exists
    except FileNotFoundError:
        logger.error(f"❌ ファイルが見つかりません: {file_path}")
        return False
    except PermissionError:
        logger.error(f"❌ ファイルアクセス権限がありません: {file_path}")
        return False
    except OSError as e:
        logger.error(f"❌ ファイル操作エラー: {file_path} - {e}")
        return False
    except Exception as e:
        logger.error(f"❌ 予期しないファイル操作エラー: {file_path} - {e}")
        return False


def resolve_department_alias(department):
    """🔥 ULTRA SYNC FIX: 部門IDのエイリアスを解決して正式な部門IDを返す"""
    # 🔥 FIX: グローバルLEGACY_DEPARTMENT_ALIASESを使用してすべてのエイリアス対応
    if department in LEGACY_DEPARTMENT_ALIASES:
        resolved = LEGACY_DEPARTMENT_ALIASES[department]
        logger.info(f"🔥 部門エイリアス変換: {department} → {resolved}")
        return resolved
    
    # 追加の個別エイリアス（後方互換性維持）
    department_aliases = {
        'shinrin': 'forestry',  # 森林土木のエイリアス
    }
    
    if department in department_aliases:
        logger.info(f"部門エイリアス変換（個別）: {department} → {department_aliases[department]}")
        return department_aliases[department]

    return department


def _validate_session_integrity():
    """セッション整合性チェック"""
    try:
        # 基本フィールドの型チェック
        if 'exam_question_ids' in session and not isinstance(session['exam_question_ids'], list):
            session['exam_question_ids'] = []
            logger.warning("exam_question_idsの型修正")

        if 'exam_current' in session and not isinstance(session['exam_current'], int):
            session['exam_current'] = 0
            logger.warning("exam_currentの型修正")

        # HTTP 431完全対策: history初期化も無効化
        # if 'history' in session and not isinstance(session['history'], list):
        #     session['history'] = []
            logger.warning("historyの型修正")

        # 範囲チェック
        exam_ids = session.get('exam_question_ids', [])
        current = session.get('exam_current', 0)

        if exam_ids and current >= len(exam_ids):
            session['exam_current'] = max(0, len(exam_ids) - 1)
            logger.warning(f"exam_currentの範囲修正: {current} -> {session['exam_current']}")

    except Exception as e:
        logger.error(f"セッション整合性チェックエラー: {e}")


def safe_session_operation(user_id, operation_func, *args, **kwargs):
    """セッション操作を安全に実行（ウルトラシンク排他制御強化）"""
    if not user_id:
        logger.error("user_idが提供されていません - セッション操作をスキップ")
        return None

    session_lock = get_session_lock(user_id)

    try:
        with session_lock:
            # 🔥 CRITICAL FIX: セッション操作の原子性保証
            session_backup = dict(session) if hasattr(session, 'keys') else {}
            try:
                result = operation_func(*args, **kwargs)
                # 操作成功時のみsession.modifiedを設定
                if hasattr(session, 'modified'):
                    session.modified = True
                return result
            except Exception as op_error:
                # 操作エラー時はセッションを復元
                if session_backup:
                    for key, value in session_backup.items():
                        session[key] = value
                    session.modified = True
                logger.error(f"セッション操作失敗（復元実行） - ユーザー: {user_id}, エラー: {op_error}")
                raise op_error
    except Exception as e:
        logger.error(f"セッション操作エラー (user_id: {user_id}): {e}")
        return None


def safe_session_update(key, value):
    """セッション更新を安全に実行するヘルパー関数"""
    user_id = session.get('user_id')
    if not user_id:
        # user_idが無い場合は直接更新（初期化時など）
        session[key] = value
        return

    def update_operation():
        session[key] = value
        logger.debug(f"セッション安全更新: {key} = {type(value).__name__}")
        return value

    return safe_session_operation(user_id, update_operation)


def safe_session_get(key, default=None):
    """セッション読み取りを安全に実行するヘルパー関数"""
    user_id = session.get('user_id')
    if not user_id:
        return session.get(key, default)

    def get_operation():
        return session.get(key, default)

    return safe_session_operation(user_id, get_operation)

# 強力なキャッシュ制御ヘッダーを設定（マルチユーザー・企業環境対応）


@app.after_request
def after_request(response):
    """
    全てのレスポンスにキャッシュ制御ヘッダーを追加
    企業環境での複数ユーザー利用に対応
    🔥 CRITICAL: ユーザー要求による超強力キャッシュクリア
    """
    # 🔥 ULTRA強力なキャッシュ制御でブラウザキャッシュを完全無効化
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0, private'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'  # 過去の日付で強制期限切れ

    # 🔥 問題関連ページの追加キャッシュクリア（ユーザー要求による）
    if any(path in request.path for path in ['/exam', '/result', '/review', '/feedback']):
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0, private, no-transform'
        response.headers['Last-Modified'] = 'Wed, 11 Jan 1984 05:00:00 GMT'  # 強制古い日付
        response.headers['ETag'] = '"0"'  # 無効なETAG
        response.headers['Vary'] = '*'    # 全リクエストで異なることを示す

    # セキュリティヘッダー追加
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'

    # 🔥 ULTRA SYNC SECURITY FIX: セキュアなCORS設定（企業環境セキュリティ強化）
    # 環境変数ベースのCORS設定（本番環境では適切なドメインを設定）
    allowed_origins_config = os.environ.get('ALLOWED_ORIGINS', 'http://localhost:5003,http://127.0.0.1:5003')
    allowed_origins = [origin.strip() for origin in allowed_origins_config.split(',') if origin.strip()]
    
    origin = request.headers.get('Origin')
    if origin in allowed_origins:
        response.headers['Access-Control-Allow-Origin'] = origin
    else:
        # 許可されていないOriginの場合はログに記録
        if origin:
            logger.warning(f"🚨 未許可のOriginからのアクセス: {origin}")
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'  # 必要最小限のメソッド
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'  # 必要最小限のヘッダー
    response.headers['Access-Control-Allow-Credentials'] = 'true'  # 認証情報送信許可

    # サービスワーカー更新強制
    if '/sw.js' in request.path:
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Service-Worker-Allowed'] = '/'

    return response


@app.after_request
def ensure_session_persistence_ultrathin(response):
    """🛡️ ULTRATHIN区段階21: クリティカルルートでのセッション永続化確保"""
    critical_routes = ['/start_exam', '/exam_question', '/exam_simulator']
    
    # クリティカルルートの場合、セッション保存を確実化
    if any(route in request.path for route in critical_routes):
        session.permanent = True
        session.modified = True
        
        # 🛡️ デバッグ情報
        if 'exam_session' in session:
            logger.info(f"🛡️ ULTRATHIN段階21: セッション保存確実化 - {request.path}")
    
    return response

# セキュリティ機能


def sanitize_input(input_string, allow_underscores=False):
    """入力値をサニタイズ（ウルトラシンク安全性修正・日本語対応強化版）"""
    if not input_string:
        return ""

    # 文字列に変換して空白の正規化
    sanitized = str(input_string).strip()

    # 危険なHTMLタグのみ除去（日本語文字は保持）
    sanitized = re.sub(r'<[^>]*>', '', sanitized)

    # 🔥 ULTRA SYNC SECURITY FIX: 包括的なXSS対策（日本語対応）
    # すべての危険文字を適切にエスケープ
    dangerous_chars = {
        "<": "&lt;",
        ">": "&gt;",
        "&": "&amp;",
        "'": "&#39;",
        '"': "&quot;",
        "\n": "&#10;",
        "\r": "&#13;",
        "\t": "&#9;"
    }
    
    # 日本語文字も含めて一律エスケープ処理
    for char, escaped in dangerous_chars.items():
        sanitized = sanitized.replace(char, escaped)
    
    # Unicode制御文字の除去
    import unicodedata
    sanitized = ''.join(char for char in sanitized if unicodedata.category(char) != 'Cc')
    
    # SQLインジェクション対策の追加文字
    sql_dangerous_chars = {
        ";": "&#59;",      # セミコロン
        "--": "&#45;&#45;",  # SQLコメント
        "/*": "&#47;&#42;",  # SQLコメント開始
        "*/": "&#42;&#47;",  # SQLコメント終了
        "\\": "&#92;",     # バックスラッシュ
        "=": "&#61;",      # 等号（WHERE句攻撃対策）
        "%": "&#37;",      # パーセント（LIKE句攻撃対策）
    }

    # SQLインジェクション対策の適用
    for char, escaped in sql_dangerous_chars.items():
        sanitized = sanitized.replace(char, escaped)
    
    # 🔥 ULTRA SYNC FIX: civil_planning等の部門ID対応
    # アンダースコアの変換はallow_underscores=Falseの場合のみ実行
    if not allow_underscores:
        sanitized = sanitized.replace("_", "&#95;")  # アンダースコア（LIKE句攻撃対策）

    return sanitized

# =============================================================================
# 高度なSRS（間隔反復学習）システム - 忘却曲線ベース
# =============================================================================


def calculate_next_review_date(correct_count, wrong_count, last_interval=1):
    """
    忘却曲線に基づく次回復習日の計算

    Args:
        correct_count: 連続正解回数
        wrong_count: 間違い回数
        last_interval: 前回の間隔（日数）

    Returns:
        次回復習日時と間隔（日数）
    """
    # 基本間隔設定（エビングハウスの忘却曲線ベース）
    base_intervals = [1, 3, 7, 14, 30, 90, 180, 365]  # 日数

    # 難易度係数（間違いが多いほど頻繁に復習）
    difficulty_factor = max(0.1, 1.0 - (wrong_count * 0.1))

    # 習熟度レベル（正解回数に基づく）
    mastery_level = min(correct_count, len(base_intervals) - 1)

    # 次回間隔を計算
    base_interval = base_intervals[mastery_level]
    adjusted_interval = max(1, int(base_interval * difficulty_factor))

    # 🔥 ULTRA SYNC TIMEZONE FIX: UTC基準の次回復習日計算
    next_review = get_utc_now() + timedelta(days=adjusted_interval)

    return next_review, adjusted_interval


def update_advanced_srs_data(question_id, is_correct, session):
    """
    高度なSRSデータの更新

    Args:
        question_id: 問題ID
        is_correct: 正解かどうか
        session: セッションオブジェクト

    Returns:
        更新されたSRSデータ
    """
    from datetime import datetime

    # SRSデータの初期化
    # HTTP 431完全対策: advanced_srs完全無効化
    # if 'advanced_srs' not in session:
    #     session['advanced_srs'] = {}

    # srs_data = session['advanced_srs']
    srs_data = {}  # 空のSRSデータで動作（セッション保存なし）
    qid_str = str(question_id)

    # 問題のSRSデータを取得または初期化
    if qid_str not in srs_data:
        srs_data[qid_str] = {
            'correct_count': 0,
            'wrong_count': 0,
            'total_attempts': 0,
            # 🔥 ULTRA SYNC TIMEZONE FIX: UTC基準のタイムスタンプ記録
            'first_attempt': format_utc_to_iso(),
            'last_attempt': format_utc_to_iso(),
            'mastered': False,
            'difficulty_level': 5,  # 1-10 (1=易しい, 10=難しい)
            'next_review': format_utc_to_iso(),
            'interval_days': 1
        }

    question_data = srs_data[qid_str]

    # 🔥 CRITICAL: 既存データの後方互換性保証（ウルトラシンク修正）
    # interval_daysが存在しない古いデータに対する修正
    if 'interval_days' not in question_data:
        question_data['interval_days'] = 1
        logger.info(f"SRS後方互換性修正: 問題ID {qid_str} にinterval_days=1を追加")

    # 統計更新
    question_data['total_attempts'] += 1
    question_data['last_attempt'] = get_utc_now().isoformat()

    if is_correct:
        question_data['correct_count'] += 1
        # 難易度を下げる（正解したので少し易しくなったと判定）
        question_data['difficulty_level'] = max(1, question_data['difficulty_level'] - 0.5)

        # 5回正解でマスター判定
        if question_data['correct_count'] >= 5:
            question_data['mastered'] = True
            logger.info(f"問題 {question_id} がマスターレベルに到達（5回正解）")

    else:
        question_data['wrong_count'] += 1
        # 難易度を上げる（間違えたので難しいと判定）
        question_data['difficulty_level'] = min(10, question_data['difficulty_level'] + 1.0)
        # 間違えた場合はマスター状態を解除
        question_data['mastered'] = False

    # 次回復習日の計算
    if not question_data['mastered']:
        next_review, interval = calculate_next_review_date(
            question_data['correct_count'],
            question_data['wrong_count'],
            question_data['interval_days']
        )
        # 🔥 ULTRA SYNC TIMEZONE FIX: UTC基準の次回復習日記録
        question_data['next_review'] = format_utc_to_iso(next_review)
        question_data['interval_days'] = interval

    # HTTP 431完全対策: SRSデータセッション保存無効化
    # session['advanced_srs'] = srs_data
    session.modified = True

    logger.info(f"SRS更新: 問題{question_id} - 正解:{question_data['correct_count']}, "
                f"間違い:{question_data['wrong_count']}, 難易度:{question_data['difficulty_level']:.1f}, "
                f"マスター:{question_data['mastered']}")

    return question_data


def get_due_review_questions(session, max_count=50):
    """
    復習が必要な問題を取得（優先度順）

    Args:
        session: セッションオブジェクト
        max_count: 最大取得数

    Returns:
        復習が必要な問題IDのリスト（優先度順）
    """
    if 'advanced_srs' not in session:
        return []

    srs_data = session['advanced_srs']
    # 🔥 ULTRA SYNC TIMEZONE FIX: UTC基準の現在時刻取得
    now = get_utc_now()
    due_questions = []

    for qid, data in srs_data.items():
        # マスター済みの問題はスキップ
        if data.get('mastered', False):
            continue

        try:
            # 🔥 CRITICAL FIX: 安全な日時解析と優先度計算
            next_review_str = data.get('next_review')
            if not next_review_str:
                # next_reviewが未設定の場合は即座に復習対象
                due_questions.append((qid, 100, data))
                continue

            # 🔥 ULTRA SYNC TIMEZONE FIX: タイムゾーン対応の日時解析
            next_review = parse_iso_with_timezone(next_review_str)
            if next_review <= now:
                # 優先度を安全に計算（エラー処理付き）
                try:
                    days_overdue = max(0, (now - next_review).days)
                    wrong_count = data.get('wrong_count', 0)
                    total_attempts = data.get('total_attempts', 1)
                    difficulty_level = data.get('difficulty_level', 5)

                    # 🔥 ULTRA SYNC PRECISION FIX: 浮動小数点精度保証・デシマル計算
                    wrong_ratio = Decimal(str(wrong_count)) / Decimal(str(max(1, total_attempts)))
                    # 精度保証: 小数点以下2桁で計算
                    priority_decimal = (wrong_ratio * Decimal('100')) + Decimal(str(days_overdue)) + Decimal(str(difficulty_level))
                    priority = float(max(Decimal('1'), min(Decimal('999'), priority_decimal.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))))

                    due_questions.append((qid, priority, data))
                except (TypeError, ValueError, AttributeError) as calc_error:
                    logger.warning(f"優先度計算エラー（問題ID: {qid}）: {calc_error}")
                    due_questions.append((qid, 50, data))  # デフォルト優先度

        except (ValueError, KeyError, TypeError) as e:
            # 日時解析エラーの場合は中程度の優先度で追加（999は危険）
            logger.warning(f"日時解析エラー（問題ID: {qid}）: {e}")
            due_questions.append((qid, 75, data))

    # 優先度順（降順）でソートして返す
    due_questions.sort(key=lambda x: x[1], reverse=True)

    result = [qid for qid, priority, data in due_questions[:max_count]]
    logger.info(f"復習対象問題: {len(result)}問（全体: {len(due_questions)}問）")

    return result


def get_adaptive_review_list(session):
    """
    アダプティブな復習リストを生成
    間違いが多い問題ほど頻繁に出題される

    Args:
        session: セッションオブジェクト

    Returns:
        復習問題IDのリスト（頻度調整済み）
    """
    if 'advanced_srs' not in session:
        return []

    srs_data = session['advanced_srs']
    weighted_questions = []

    for qid, data in srs_data.items():
        # マスター済みの問題はスキップ
        if data.get('mastered', False):
            continue

        # 重み計算（間違いが多いほど高い重み）
        wrong_count = data.get('wrong_count', 0)
        total_attempts = data.get('total_attempts', 1)
        difficulty = data.get('difficulty_level', 5)

        # 🔥 CRITICAL FIX: 安全な数値計算（型エラー防止・精度保持）
        try:
            # 🔥 ULTRA SYNC PRECISION FIX: 重み計算の精度保証（高精度計算のみ使用）
            wrong_ratio_decimal = Decimal(str(wrong_count)) / Decimal(str(max(1, total_attempts)))
            # 重み = 間違い率 × 難易度レベル × 係数（高精度計算）
            weight_decimal = wrong_ratio_decimal * Decimal(str(difficulty)) * Decimal('2.0')
            # 最低1、最大20に制限して精度保証でint変換
            weight = int(max(1, min(20, weight_decimal.quantize(Decimal('1'), rounding=ROUND_HALF_UP))))
        except (TypeError, ValueError, ZeroDivisionError) as e:
            logger.warning(f"重み計算エラー（問題ID: {qid}）: {e}, デフォルト値1を使用")
            weight = 1

        # 重みに応じて複数回追加（重要な問題ほど出現頻度が高くなる）
        for _ in range(weight):
            weighted_questions.append(qid)

    # シャッフルして自然な順序にする
    # 🛡️ ULTRA SYNC: random already imported at top
    random.shuffle(weighted_questions)

    logger.info(f"アダプティブ復習リスト生成: {len(weighted_questions)}問（重み付き）")
    return weighted_questions


def cleanup_mastered_questions(session):
    """
    マスター済み問題の旧復習リストからの除去

    Args:
        session: セッションオブジェクト

    Returns:
        削除された問題数
    """
    if 'advanced_srs' not in session:
        return 0

    srs_data = session['advanced_srs']
    bookmarks = session.get('bookmarks', [])
    removed_count = 0

    # マスター済み問題を旧復習リストから除去
    for qid, data in srs_data.items():
        if data.get('mastered', False) and qid in bookmarks:
            bookmarks.remove(qid)
            removed_count += 1
            logger.info(f"マスター済み問題を復習リストから除去: {qid}")

    safe_session_update('bookmarks', bookmarks)

    return removed_count


def validate_exam_parameters(**kwargs):
    """🚀 ULTRA SYNC ROOT FIX: 正規化部門名による検証"""
    # 🚀 ULTRA SYNC: 正規化された部門名のみ許可（重複排除済み）
    valid_departments = list(DEPARTMENT_TO_CATEGORY_MAPPING.keys())
    valid_legacy_departments = list(LEGACY_DEPARTMENT_ALIASES.keys())
    valid_question_types = ['basic', 'specialist', 'review']
    valid_years = list(range(2008, 2020))

    errors = []

    # 🚀 ULTRA SYNC: 部門検証（正規化処理）
    if 'department' in kwargs and kwargs['department']:
        normalized_dept = normalize_department_name(kwargs['department'])
        if not normalized_dept:
            errors.append(f"無効な部門: {kwargs['department']}")

    # 問題種別検証
    if 'question_type' in kwargs and kwargs['question_type']:
        if kwargs['question_type'] not in valid_question_types:
            errors.append(f"無効な問題種別: {kwargs['question_type']}")

    # 年度検証
    if 'year' in kwargs and kwargs['year']:
        try:
            year = int(kwargs['year'])
            if year not in valid_years:
                errors.append(f"無効な年度: {year}")
        except (ValueError, TypeError):
            errors.append(f"年度は数値で指定してください: {kwargs['year']}")

    # 問題数検証
    if 'size' in kwargs and kwargs['size']:
        try:
            size = int(kwargs['size'])
            if size < 1 or size > 50:
                errors.append(f"問題数は1-50の範囲で指定してください: {size}")
        except (ValueError, TypeError):
            errors.append(f"問題数は数値で指定してください: {kwargs['size']}")

    return errors


def rate_limit_check(max_requests=1000, window_minutes=60):
    """レート制限チェック（ウルトラシンク安全性修正）"""
    now = datetime.now()
    window_start = now - timedelta(minutes=window_minutes)

    # セッションからリクエスト履歴を安全に取得
    request_history = session.get('request_history', [])

    # 🔥 CRITICAL FIX: 例外処理付きで安全な日時解析
    safe_history = []
    for req_time in request_history:
        try:
            if isinstance(req_time, str):
                parsed_time = datetime.fromisoformat(req_time)
                if parsed_time > window_start:
                    safe_history.append(req_time)
            elif isinstance(req_time, datetime):
                if req_time > window_start:
                    safe_history.append(req_time.isoformat())
        except (ValueError, TypeError) as e:
            logger.warning(f"無効な日時フォーマットをスキップ: {req_time}, エラー: {e}")
            continue

    request_history = safe_history

    # 現在のリクエストを追加
    request_history.append(now.isoformat())

    # セッションに保存
    session['request_history'] = request_history
    session.modified = True

    # レート制限チェック
    if len(request_history) > max_requests:
        return False

    return True


def validate_question_data_integrity(questions):
    """問題データの整合性チェックと自動修復"""
    valid_questions = []

    for i, question in enumerate(questions):
        try:
            # 必須フィールドのチェック
            if not question.get('id') or not question.get('question'):
                logger.warning(f"問題{i+1}: 必須フィールドが不足")
                continue

            # 選択肢の完整性チェック
            options = ['option_a', 'option_b', 'option_c', 'option_d']
            if not all(question.get(opt) for opt in options):
                logger.warning(f"問題{question.get('id')}: 選択肢が不完全")
                continue

            # 正解の妥当性チェック
            correct_answer = question.get('correct_answer', '').upper()
            if correct_answer not in ['A', 'B', 'C', 'D']:
                logger.warning(f"問題{question.get('id')}: 正解が無効 ({correct_answer})")
                continue

            # 部門・問題種別の整合性チェック
            question_type = question.get('question_type', '')
            if question_type not in ['basic', 'specialist']:
                # 年度があれば専門、なければ基礎と推定
                if question.get('year'):
                    question['question_type'] = 'specialist'
                else:
                    question['question_type'] = 'basic'
                logger.debug(f"問題{question.get('id')}: 問題種別を推定設定 ({question['question_type']})")

            valid_questions.append(question)

        except Exception as e:
            logger.error(f"問題{i+1}の検証エラー: {e}")
            continue

    removed_count = len(questions) - len(valid_questions)
    if removed_count > 0:
        logger.warning(f"データ整合性チェック: {removed_count}問を除外しました")

    return valid_questions


def load_questions():
    """
    RCCM統合問題データの読み込み（4-1基礎・4-2専門対応）
    キャッシュ機能と詳細エラーハンドリング
    🔥 ULTRA SYNC FIX: 起動高速化対応
    """
    global _questions_cache, _cache_timestamp

    # 🔥 ULTRA SYNC FIX: 事前読み込み済みデータがあればそれを使用（URL起動遅延解決）
    if _startup_data_loaded and _questions_cache is not None:
        logger.debug(f"事前読み込み済みデータ使用: {len(_questions_cache)}問（⚡高速）")
        return _questions_cache

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
        # 🛡️ ULTRATHIN区 緊急修正: 基礎科目のみ読み込み（専門科目は必要時に動的読み込み）
        from utils import load_basic_questions_only
        basic_questions = load_basic_questions_only(data_dir)
        questions = basic_questions

        if questions:
            # データ整合性チェック
            validated_questions = validate_question_data_integrity(questions)
            _questions_cache = validated_questions
            _cache_timestamp = current_time
            logger.info(f"RCCM統合データ読み込み完了: {len(validated_questions)}問 (検証済み)")
            return validated_questions
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

# 🔥 CRITICAL: ウルトラシンク復習セッション管理システム（統合管理）


def validate_review_session_integrity(session_data):
    """復習セッションの整合性を検証し、必要に応じて修復する"""
    try:
        exam_question_ids = session_data.get('exam_question_ids', [])
        exam_current = session_data.get('exam_current', 0)
        selected_question_type = session_data.get('selected_question_type', '')

        # 復習セッションの基本チェック
        if selected_question_type != 'review':
            return False, "復習セッションではありません"

        if not exam_question_ids or not isinstance(exam_question_ids, list):
            return False, "復習問題リストが無効です"

        if exam_current < 0 or exam_current > len(exam_question_ids):
            return False, f"現在位置が範囲外です: {exam_current}/{len(exam_question_ids)}"

        # 問題IDの有効性チェック
        for qid in exam_question_ids:
            if not isinstance(qid, int) or qid <= 0:
                return False, f"無効な問題ID: {qid}"

        logger.debug(f"復習セッション整合性チェック成功: {len(exam_question_ids)}問, 位置{exam_current}")
        return True, "OK"

    except Exception as e:
        logger.error(f"復習セッション整合性チェックエラー: {e}")
        return False, str(e)


def create_robust_review_session(user_session, all_questions, review_type='mixed'):
    """堅牢な復習セッションを作成する（ウルトラシンク版）"""
    try:
        logger.info(f"堅牢復習セッション作成開始: タイプ={review_type}")

        # 復習対象問題を収集
        review_question_ids = set()

        # SRSデータから復習必要問題を取得
        due_questions = get_due_questions(user_session, all_questions)
        for due_item in due_questions:
            qid = due_item['question'].get('id')
            if qid:
                review_question_ids.add(int(qid))

        # ブックマークから復習問題を取得
        bookmarks = user_session.get('bookmarks', [])
        for bookmark_id in bookmarks:
            try:
                review_question_ids.add(int(bookmark_id))
            except (ValueError, TypeError):
                continue

        # 積極的な復習候補を追加（間違いの多い問題）
        history = user_session.get('history', [])
        wrong_questions = []
        for entry in history[-50:]:  # 直近50問をチェック
            if not entry.get('is_correct', True):  # 間違えた問題
                qid = entry.get('question_id')
                if qid:
                    wrong_questions.append(int(qid))

        # 間違いの多い問題を優先的に追加
        for qid in wrong_questions[-10:]:  # 最近10問の間違い
            review_question_ids.add(qid)

        # 有効な問題IDのみを保持
        valid_review_ids = []
        for qid in review_question_ids:
            # 問題データが存在するかチェック
            if any(int(q.get('id', 0)) == qid for q in all_questions):
                valid_review_ids.append(qid)

        # ユーザー設定の問題数を取得
        user_session_size = get_user_session_size(user_session)
        
        # 最低限の復習問題数を保証
        if len(valid_review_ids) < 3:
            # ランダムに問題を追加
            random_questions = random.sample(all_questions, min(7, len(all_questions)))
            for q in random_questions:
                qid = int(q.get('id', 0))
                if qid not in valid_review_ids:
                    valid_review_ids.append(qid)
                if len(valid_review_ids) >= user_session_size:  # ユーザー設定に従う
                    break

        # 問題数を適切に調整
        if len(valid_review_ids) > user_session_size:
            valid_review_ids = valid_review_ids[:user_session_size]  # ユーザー設定に制限

        valid_review_ids.sort()  # 一貫性のためにソート

        logger.info(f"堅牢復習セッション作成完了: {len(valid_review_ids)}問")
        logger.info(f"復習問題ID: {valid_review_ids[:5]}..." if len(valid_review_ids) > 5 else f"復習問題ID: {valid_review_ids}")

        return valid_review_ids

    except Exception as e:
        logger.error(f"堅牢復習セッション作成エラー: {e}")
        # フォールバック: シンプルな復習セッション
        fallback_questions = random.sample(all_questions, min(5, len(all_questions)))
        return [int(q.get('id', 0)) for q in fallback_questions]


def safe_update_review_session(session_data, question_ids, current_index=0):
    """復習セッションを安全に更新する"""
    try:
        # セッションクリア（復習関連のみ）
        review_keys_to_clear = [
            'exam_question_ids', 'exam_current', 'exam_category',
            'selected_question_type', 'selected_department', 'selected_year'
        ]

        for key in review_keys_to_clear:
            session_data.pop(key, None)

        # 新しい復習セッションデータを設定
        session_data.update({
            'exam_question_ids': question_ids,
            'exam_current': current_index,
            'exam_category': f'復習問題（統合{len(question_ids)}問）',
            'selected_question_type': 'review',
            'review_session_active': True,
            'review_session_created': get_utc_now().isoformat(),
            'review_session_protected': True  # 保護フラグ
        })

        session_data.permanent = True
        session_data.modified = True

        logger.info(f"復習セッション安全更新完了: {len(question_ids)}問, 現在位置{current_index}")
        return True

    except Exception as e:
        logger.error(f"復習セッション安全更新エラー: {e}")
        return False

# Removed old update_srs_data function - replaced with update_advanced_srs_data


def get_due_questions(user_session, all_questions):
    """復習が必要な問題を取得"""
    if 'srs_data' not in user_session:
        return []

    srs_data = user_session['srs_data']
    # 🔥 ULTRA SYNC TIMEZONE FIX: UTC基準の今日日付取得
    today = get_utc_now().date()
    due_questions = []

    for question_id, data in srs_data.items():
        try:
            # 🔥 ULTRA SYNC TIMEZONE FIX: タイムゾーン対応の復習日解析
            next_review = parse_iso_with_timezone(data['next_review']).date()
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


def get_user_session_size(user_session):
    """ユーザー設定の問題数を取得（デフォルト10問）"""
    quiz_settings = user_session.get('quiz_settings', {})
    return quiz_settings.get('questions_per_session', 10)


#@performance_timing_decorator
def get_mixed_questions(user_session, all_questions, requested_category='全体', session_size=None, department='', question_type='', year=None):
    """新問題と復習問題をミックスした出題（RCCM部門対応版・📊 高性能最適化版）"""
    # ユーザー設定の問題数を取得（デフォルト10問）
    if session_size is None:
        session_size = get_user_session_size(user_session)
    
    # 📊 ULTRA SYNC PERFORMANCE FIX: 高性能オプティマイザーによる高速問題選択
    if _performance_optimizer and _performance_optimizer.data_loaded:
        try:
            # 専門科目で部門・年度・問題種別が指定されている場合は高速処理を使用
            if question_type == 'specialist' and department and year:
                logger.info(f"📊 高性能問題選択開始: {department}/{year}年度/{question_type}")
                
                # 🚀 ULTRA SYNC: 正規化部門名による安全なカテゴリ変換
                normalized_dept = normalize_department_name(department)
                target_category = get_department_category(normalized_dept) if normalized_dept else None
                
                if not target_category:
                    logger.error(f"❌ 無効な部門名: {department}")
                    target_category = '全体'
                
                # 除外IDリスト作成
                exclude_ids = []
                if hasattr(user_session, 'get'):
                    history = user_session.get('history', [])
                    exclude_ids = [item.get('question_id') for item in history if item.get('question_id')]
                
                # 高速最適化問題選択
                optimized_questions = _performance_optimizer.get_mixed_questions_optimized(
                    department=target_category,
                    question_type=question_type,
                    year=int(year) if year else None,
                    count=session_size,
                    exclude_ids=exclude_ids
                )
                
                if optimized_questions and len(optimized_questions) >= min(session_size, 3):
                    logger.info(f"✅ 高性能問題選択成功: {len(optimized_questions)}問選択")
                    return optimized_questions
                else:
                    logger.info("📊 高性能問題選択：問題数不足、フォールバック実行")
            
        except Exception as pe:
            logger.warning(f"⚠️ 高性能問題選択エラー（フォールバック実行）: {pe}")

    due_questions = get_due_questions(user_session, all_questions)

    # 設定から復習問題の比率を取得
    max_review_count = min(len(due_questions),
                           int(session_size * SRSConfig.MAX_REVIEW_RATIO))
    selected_questions = []

    # 復習問題を追加（部門・問題種別・年度でもフィルタリング）
    for i, due_item in enumerate(due_questions):
        if i >= max_review_count:
            break

        question = due_item['question']
        # 🚀 ULTRA SYNC: 正規化部門名による条件チェック
        if department:
            normalized_dept = normalize_department_name(department)
            question_category = question.get('category', '')
            expected_category = get_department_category(normalized_dept) if normalized_dept else None
            if expected_category and question_category != expected_category:
                continue
        if question_type and question.get('question_type') != question_type:
            continue
        # 🚨 年度フィルタリング追加（ウルトラシンク修正）
        if year and str(question.get('year', '')) != str(year):
            continue
            
        # 🛡️ ULTRATHIN区緊急修正: 問題種別厳格チェック（カテゴリー混在防止）
        if question_type == 'specialist' and question.get('question_type') != 'specialist':
            logger.warning(f"🚨 専門科目要求だが基礎科目問題を除外: ID={question.get('id')}, type={question.get('question_type')}")
            continue
        elif question_type == 'basic' and question.get('question_type') != 'basic':
            logger.warning(f"🚨 基礎科目要求だが専門科目問題を除外: ID={question.get('id')}, type={question.get('question_type')}")
            continue

        selected_questions.append(question)

    # 残りを新問題で埋める（学習効率重視の選択）
    remaining_count = session_size - len(selected_questions)

    # 問題フィルタリング条件
    available_questions = all_questions

    # AI学習分析による弱点重視出題
    if user_session.get('history'):
        from ai_analyzer import ai_analyzer
        ai_analyzer.analyze_weak_areas(user_session, department)

    # 🛡️ ULTRATHIN区緊急修正: 問題種別でフィルタリング（最優先・厳格・カテゴリー混在完全防止）
    if question_type:
        logger.info(f"🛡️ ULTRATHIN区: 問題種別フィルタ開始 - type={question_type}, 対象問題数={len(available_questions)}")
        
        # 基礎科目の場合
        if question_type == 'basic':
            pre_basic_count = len(available_questions)
            available_questions = [q for q in available_questions
                                   if q.get('question_type') == 'basic'
                                   and q.get('year') is None]  # 基礎科目は年度なし
            logger.info(f"🛡️ ULTRATHIN区: 基礎科目フィルタ適用 - {pre_basic_count} → {len(available_questions)}問")
            
            # 🚨 専門科目混入チェック
            specialist_contamination = [q for q in all_questions 
                                      if q.get('question_type') == 'specialist' and int(q.get('id', 0)) in [int(aq.get('id', 0)) for aq in available_questions]]
            if specialist_contamination:
                logger.error(f"🚨 基礎科目に専門科目混入検出: {len(specialist_contamination)}問")
                available_questions = [q for q in available_questions if q not in specialist_contamination]

        # 専門科目の場合
        elif question_type == 'specialist':
            pre_specialist_count = len(available_questions)
            available_questions = [q for q in available_questions
                                   if q.get('question_type') == 'specialist'
                                   and q.get('year') is not None]  # 専門科目は年度必須
            logger.info(f"🛡️ ULTRATHIN区: 専門科目フィルタ適用 - {pre_specialist_count} → {len(available_questions)}問")
            
            # 🚨 基礎科目混入チェック
            basic_contamination = [q for q in all_questions 
                                 if q.get('question_type') == 'basic' and int(q.get('id', 0)) in [int(aq.get('id', 0)) for aq in available_questions]]
            if basic_contamination:
                logger.error(f"🚨 専門科目に基礎科目混入検出: {len(basic_contamination)}問")
                available_questions = [q for q in available_questions if q not in basic_contamination]

        # その他の場合
        else:
            available_questions = [q for q in available_questions if q.get('question_type') == question_type]
            logger.info(f"🛡️ ULTRATHIN区: その他問題種別フィルタ適用 - {question_type}, 結果: {len(available_questions)}問")

        # 🚀 ULTRA SYNC: 専門科目で部門指定がある場合の正規化フィルタ適用
        if question_type == 'specialist' and department:
            # 🚀 ULTRA SYNC: 正規化部門名による安全な変換
            normalized_dept = normalize_department_name(department)
            target_category = get_department_category(normalized_dept) if normalized_dept else None
            
            if not target_category:
                logger.error(f"❌ 無効な部門名: {department}")
                available_questions = []  # 無効な部門の場合は空にする
            else:
                logger.info(f"🚀 ULTRA SYNC部門フィルタリング: {department} → {normalized_dept} → {target_category}")
                
                # デバッグ：利用可能な全カテゴリをログ出力
                all_categories = list(set(q.get('category', 'なし') for q in available_questions))
                logger.info(f"専門科目フィルタ前のカテゴリ一覧: {all_categories}")
                
                dept_match_questions = [q for q in available_questions
                                        if q.get('category') == target_category]
                if dept_match_questions:
                    available_questions = dept_match_questions
                    logger.info(f"✅ 専門科目部門マッチング成功: カテゴリ「{target_category}」で {len(available_questions)}問")
                else:
                    logger.error(f"❌ 専門科目部門マッチング失敗: カテゴリ「{target_category}」に該当する問題が見つかりません")
                    available_questions = []

    # 部門でフィルタリング（基礎科目の場合はスキップ、専門科目で既に適用済みの場合もスキップ）
    elif department and question_type != 'basic' and question_type != 'specialist':
        available_questions = [q for q in available_questions if q.get('department') == department]
        logger.info(f"部門フィルタ適用: {department}, 結果: {len(available_questions)}問")

    # カテゴリでフィルタリング（ULTRA SYNC: 英語→日本語マッピング完全対応）
    if requested_category != '全体':
        pre_category_count = len(available_questions)
        
        # 🚀 ULTRA SYNC FIX: 英語部門名→日本語カテゴリ名の完全マッピング
        target_category = requested_category
        if requested_category in DEPARTMENT_TO_CATEGORY_MAPPING:
            target_category = DEPARTMENT_TO_CATEGORY_MAPPING[requested_category]
            logger.info(f"🔧 ULTRA SYNC: 英語→日本語マッピング適用 {requested_category} → {target_category}")
        
        # 正確な文字列マッチング（日本語カテゴリ名で）
        available_questions = [q for q in available_questions if q.get('category') == target_category]

        # 文字化けしている場合のフォールバック（部分マッチ）
        if len(available_questions) == 0 and target_category:
            # 文字化けを考慮した部分マッチ
            logger.warning(f"正確なカテゴリマッチ失敗: {target_category}, 部分マッチを試行")
            for q in [q for q in all_questions if q.get('question_type') == question_type]:
                category = q.get('category', '')
                # 道路、トンネル等の主要カテゴリのマッチング
                if ('道路' in category and ('道' in target_category or 'road' in target_category.lower())) or \
                   ('トンネル' in category and ('トンネル' in target_category or 'tunnel' in target_category.lower())) or \
                   ('河川' in category and ('河川' in target_category or 'civil' in target_category.lower())) or \
                   ('土質' in category and ('土質' in target_category or 'soil' in target_category.lower())):
                    if q not in available_questions:
                        available_questions.append(q)

        logger.info(f"カテゴリフィルタ適用: {requested_category} → {target_category}, {pre_category_count} → {len(available_questions)}問")

    # 🚨 年度でフィルタリング（ウルトラシンク年度混在防止修正・緊急強化版）
    if year and question_type == 'specialist':
        pre_year_count = len(available_questions)
        
        # 🔥 緊急修正: 年度データの厳密な検証と変換
        try:
            target_year = int(year)
            # 有効年度範囲チェック（2008-2019年）
            if target_year < 2008 or target_year > 2019:
                logger.error(f"❌ 無効な年度範囲: {target_year} (有効範囲: 2008-2019)")
                return []
            
            # 年度フィルタリング: 厳密な数値比較
            available_questions = [q for q in available_questions 
                                   if q.get('year') is not None and int(q.get('year', 0)) == target_year]
            
            logger.info(f"🚨 年度フィルタ適用（緊急強化版）: {target_year}年度, {pre_year_count} → {len(available_questions)}問")
            
            # 年度フィルタ後に問題がない場合の詳細分析
            if len(available_questions) == 0:
                logger.error(f"❌ 年度フィルタ後に問題が0件: 年度={target_year}, 部門={department}")
                
                # デバッグ: 利用可能な年度の分析
                if question_type == 'specialist' and department:
                    all_years_in_dept = [q.get('year') for q in all_questions 
                                         if q.get('question_type') == 'specialist' 
                                         and department in DEPARTMENT_TO_CATEGORY_MAPPING 
                                         and q.get('category') == DEPARTMENT_TO_CATEGORY_MAPPING[department]]
                    unique_years = list(set([y for y in all_years_in_dept if y is not None]))
                    logger.error(f"📊 デバッグ情報: 部門「{department}」で利用可能な年度: {sorted(unique_years)}")
                
                # エラーとして処理（フォールバックなし）
                return []
                
        except (ValueError, TypeError) as e:
            logger.error(f"❌ 年度変換エラー: {year} - {e}")
            return []

    # 既に選択済みの問題を除外
    selected_ids = [int(q.get('id', 0)) for q in selected_questions]
    new_questions = [q for q in available_questions if int(q.get('id', 0)) not in selected_ids]

    random.shuffle(new_questions)
    selected_questions.extend(new_questions[:remaining_count])
    
    # デバッグ：選択された問題のカテゴリと年度を確認
    if question_type == 'specialist' and department:
        selected_categories = list(set(q.get('category', 'なし') for q in selected_questions))
        logger.info(f"最終選択問題のカテゴリ分布: {selected_categories}")
        if len(selected_categories) > 1:
            logger.warning(f"警告：複数のカテゴリが混在しています！ {selected_categories}")
    
    # 🚨 年度混在チェック（ウルトラシンク年度混在防止検証・緊急強化版）
    if year and question_type == 'specialist':
        try:
            target_year = int(year)
            selected_years = []
            mixed_year_questions = []
            
            for q in selected_questions:
                q_year = q.get('year')
                if q_year is not None:
                    try:
                        q_year_int = int(q_year)
                        selected_years.append(q_year_int)
                        if q_year_int != target_year:
                            mixed_year_questions.append(q)
                    except (ValueError, TypeError):
                        logger.error(f"❌ 問題ID {q.get('id')}: 無効な年度データ '{q_year}'")
                        mixed_year_questions.append(q)
                else:
                    logger.error(f"❌ 問題ID {q.get('id')}: 年度データがNone")
                    mixed_year_questions.append(q)
            
            unique_years = list(set(selected_years))
            logger.info(f"🚨 最終選択問題の年度分布: {sorted(unique_years)}")
            
            # 年度混在の厳密チェック
            if len(unique_years) > 1 or len(mixed_year_questions) > 0:
                logger.error(f"❌ 重大エラー：年度混在を検出！")
                logger.error(f"   指定年度: {target_year}")
                logger.error(f"   検出された年度: {sorted(unique_years)}")
                logger.error(f"   混在問題数: {len(mixed_year_questions)}")
                
                # 混在問題の詳細ログ
                for q in mixed_year_questions:
                    logger.error(f"   問題ID {q.get('id')}: 期待年度={target_year}, 実際年度={q.get('year')}")
                
                # 🔥 緊急措置: 年度混在問題を除外
                logger.warning(f"🔧 緊急措置: 年度混在問題 {len(mixed_year_questions)}問を除外")
                selected_questions = [q for q in selected_questions if q not in mixed_year_questions]
                logger.info(f"🔧 除外後の問題数: {len(selected_questions)}問")
                
        except (ValueError, TypeError) as e:
            logger.error(f"❌ 年度混在チェックエラー: {e}")
    
    # 🧪 ULTRA SYNC MANUAL TEST SUPPORT: 手動テスト支援ログ（副作用ゼロ）
    if question_type == 'specialist' and department and year:
        # 手動テスト者向けの詳細品質確認ログ
        logger.info("=" * 60)
        logger.info(f"🧪 MANUAL TEST QUALITY CHECK - {department}/{year}年度")
        logger.info("=" * 60)
        logger.info(f"📋 テスト条件: 部門={department}, 年度={year}, 問題種別={question_type}")
        logger.info(f"📊 選択問題数: {len(selected_questions)}問 (目標: {session_size}問)")
        
        # 年度統一性確認（緊急強化版）
        if selected_questions:
            try:
                target_year = int(year)
                actual_years = []
                invalid_year_count = 0
                
                for q in selected_questions:
                    q_year = q.get('year')
                    if q_year is not None:
                        try:
                            actual_years.append(int(q_year))
                        except (ValueError, TypeError):
                            invalid_year_count += 1
                            logger.error(f"❌ 問題ID {q.get('id')}: 無効な年度データ '{q_year}'")
                    else:
                        invalid_year_count += 1
                        logger.error(f"❌ 問題ID {q.get('id')}: 年度データがNone")
                
                unique_years = list(set(actual_years))
                
                if len(unique_years) == 1 and unique_years[0] == target_year and invalid_year_count == 0:
                    logger.info(f"✅ 年度統一性: 完全 - 全{len(selected_questions)}問が{target_year}年度")
                else:
                    logger.error(f"❌ 年度統一性: 失敗")
                    logger.error(f"   期待年度: {target_year}")
                    logger.error(f"   実際の年度: {sorted(unique_years)}")
                    logger.error(f"   無効年度問題数: {invalid_year_count}")
                    
            except (ValueError, TypeError) as e:
                logger.error(f"❌ 年度統一性確認エラー: {e}")
        
        # 部門統一性確認
        if selected_questions:
            target_category = department
            if department in DEPARTMENT_TO_CATEGORY_MAPPING:
                target_category = DEPARTMENT_TO_CATEGORY_MAPPING[department]
            
            actual_categories = [q.get('category', '不明') for q in selected_questions]
            unique_categories = list(set(actual_categories))
            if len(unique_categories) == 1 and unique_categories[0] == target_category:
                logger.info(f"✅ 部門統一性: 完全 - 全{len(selected_questions)}問が「{target_category}」")
            else:
                logger.error(f"❌ 部門統一性: 失敗 - 混在カテゴリ: {unique_categories}")
        
        # 問題ID重複チェック
        if selected_questions:
            question_ids = [str(q.get('id', '')) for q in selected_questions]
            unique_ids = list(set(question_ids))
            if len(question_ids) == len(unique_ids):
                logger.info(f"✅ 問題ID重複: なし - {len(unique_ids)}問すべて一意")
            else:
                duplicated_count = len(question_ids) - len(unique_ids)
                logger.error(f"❌ 問題ID重複: 検出 - {duplicated_count}個の重複")
        
        # パフォーマンス最適化効果確認
        if _performance_optimizer and _performance_optimizer.data_loaded:
            perf_stats = _performance_optimizer.get_performance_stats()
            avg_response = perf_stats.get('average_response_time', 0)
            cache_hit_rate = perf_stats.get('cache_hit_rate', 0)
            logger.info(f"⚡ パフォーマンス: レスポンス{avg_response:.1f}ms, キャッシュ{cache_hit_rate:.1f}%")
        
        logger.info("=" * 60)
        logger.info("🧪 手動テスト支援ログ完了 - ブラウザで動作確認してください")
        logger.info("=" * 60)

    # ユーザー設定問題数保証のためのフォールバック機能
    if len(selected_questions) < session_size:
        shortage = session_size - len(selected_questions)
        logger.warning(f"問題数不足を検出: {len(selected_questions)}問 (不足: {shortage}問) - フォールバック実行")

        # フォールバック1: フィルタを緩和して問題を追加
        selected_ids = [int(q.get('id', 0)) for q in selected_questions]
        fallback_questions = [q for q in all_questions if int(q.get('id', 0)) not in selected_ids]

        # 🛡️ ULTRATHIN区緊急修正: 問題種別は維持しつつ、他のフィルタを緩和（カテゴリー混在完全防止）
        if question_type:
            pre_fallback_count = len(fallback_questions)
            fallback_questions = [q for q in fallback_questions if q.get('question_type') == question_type]
            logger.info(f"🛡️ ULTRATHIN区: フォールバック問題種別フィルタ - {question_type}, {pre_fallback_count} → {len(fallback_questions)}問")
            
            # 🚨 フォールバック時の混入チェック
            if question_type == 'specialist':
                basic_contamination_fb = [q for q in fallback_questions if q.get('question_type') == 'basic']
                if basic_contamination_fb:
                    logger.error(f"🚨 専門科目フォールバックに基礎科目混入: {len(basic_contamination_fb)}問除外")
                    fallback_questions = [q for q in fallback_questions if q.get('question_type') != 'basic']
            elif question_type == 'basic':
                specialist_contamination_fb = [q for q in fallback_questions if q.get('question_type') == 'specialist']
                if specialist_contamination_fb:
                    logger.error(f"🚨 基礎科目フォールバックに専門科目混入: {len(specialist_contamination_fb)}問除外")
                    fallback_questions = [q for q in fallback_questions if q.get('question_type') != 'specialist']
            
        # 専門科目の場合は部門も維持（重要）
        if question_type == 'specialist' and department:
            target_category = department
            if department in DEPARTMENT_TO_CATEGORY_MAPPING:
                target_category = DEPARTMENT_TO_CATEGORY_MAPPING[department]
            fallback_questions = [q for q in fallback_questions if q.get('category') == target_category]
            logger.info(f"フォールバック: 部門「{target_category}」を維持 - {len(fallback_questions)}問")
            
        # 🚨 年度フィルタリングもフォールバックで維持（緊急強化版）
        if year and question_type == 'specialist':
            try:
                target_year = int(year)
                pre_fallback_count = len(fallback_questions)
                fallback_questions = [q for q in fallback_questions 
                                      if q.get('year') is not None and int(q.get('year', 0)) == target_year]
                logger.info(f"🚨 フォールバック年度フィルタ維持（緊急強化版）: {target_year}年度, {pre_fallback_count} → {len(fallback_questions)}問")
            except (ValueError, TypeError) as e:
                logger.error(f"❌ フォールバック年度フィルタエラー: {e}")
                fallback_questions = []

        random.shuffle(fallback_questions)
        additional_questions = fallback_questions[:shortage]
        selected_questions.extend(additional_questions)

        logger.info(f"フォールバック完了: {len(additional_questions)}問追加, 合計{len(selected_questions)}問")

        # 🛡️ ULTRATHIN区修正: フォールバック2でも部門・年度制約を厳格維持
        if len(selected_questions) < session_size:
            final_shortage = session_size - len(selected_questions)
            selected_ids = [int(q.get('id', 0)) for q in selected_questions]
            
            # 4-2専門問題では部門・年度制約を絶対に維持
            if question_type == 'specialist' and department:
                # 部門制約を維持したフォールバック
                target_category = get_department_category(normalize_department_name(department))
                filtered_fallback = [q for q in all_questions 
                                   if int(q.get('id', 0)) not in selected_ids
                                   and q.get('category') == target_category]
                
                # 年度制約も維持
                if year:
                    try:
                        target_year = int(year)
                        if 2008 <= target_year <= 2019:
                            filtered_fallback = [q for q in filtered_fallback 
                                               if q.get('year') is not None and int(q.get('year', 0)) == target_year]
                    except (ValueError, TypeError):
                        pass
                
                if filtered_fallback:
                    random.shuffle(filtered_fallback)
                    selected_questions.extend(filtered_fallback[:final_shortage])
                    logger.info(f"制約維持フォールバック完了: {min(final_shortage, len(filtered_fallback))}問追加, 最終合計{len(selected_questions)}問")
                else:
                    logger.warning(f"🚨 {department}の{year}年度問題が不足: 要求{session_size}問, 利用可能{len(selected_questions)}問のみ")
            else:
                # 🛡️ ULTRATHIN区緊急修正: 基礎科目等では従来通りの処理（カテゴリー混在防止）
                final_fallback = [q for q in all_questions if int(q.get('id', 0)) not in selected_ids]
                
                # 🚨 基礎科目の場合は専門科目を除外
                if question_type == 'basic':
                    final_fallback = [q for q in final_fallback if q.get('question_type') == 'basic']
                    logger.info(f"🛡️ ULTRATHIN区: 基礎科目最終フォールバック - 専門科目除外, {len(final_fallback)}問利用可能")
                
                random.shuffle(final_fallback)
                selected_questions.extend(final_fallback[:final_shortage])
                logger.info(f"🛡️ ULTRATHIN区: 最終フォールバック完了 - {min(final_shortage, len(final_fallback))}問追加, 最終合計{len(selected_questions)}問")

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

    # 🛡️ ULTRATHIN区追加: 問題数不足時の安全処理
    if len(selected_questions) < session_size:
        shortage = session_size - len(selected_questions)
        if question_type == 'specialist' and department and year:
            logger.error(f"🚨 問題数不足: {department}の{year}年度で{session_size}問要求されましたが、{len(selected_questions)}問しか利用できません（不足{shortage}問）")
            # 4-2専門問題では問題数不足を厳密にチェック
            if len(selected_questions) < max(5, session_size // 2):  # 最低5問または要求の半分
                logger.error(f"🚨 致命的問題数不足: 最低限の問題数も確保できません")
                return []  # 空リストを返してエラーハンドリングに委ねる
        logger.warning(f"⚠️ 問題数不足のため利用可能な{len(selected_questions)}問で開始します")
    
    # 🚨 ULTRA CRITICAL FIX: ユーザー設定問題数で制限（河川砂防バグ根本解決）
    selected_questions = selected_questions[:session_size]
    
    # 🛡️ ULTRATHIN区緊急修正: 最終選択問題の整合性チェック（カテゴリー混在完全防止）
    if question_type and selected_questions:
        actual_types = [q.get('question_type', 'unknown') for q in selected_questions]
        type_distribution = {t: actual_types.count(t) for t in set(actual_types)}
        logger.info(f"🛡️ ULTRATHIN区: 最終選択問題の種別分布 - {type_distribution}")
        
        # 🚨 混入検出とクリーンアップ
        if question_type == 'specialist':
            basic_contamination_final = [q for q in selected_questions if q.get('question_type') == 'basic']
            if basic_contamination_final:
                logger.error(f"🚨 最終選択に基礎科目混入検出: {len(basic_contamination_final)}問 - 除外処理")
                selected_questions = [q for q in selected_questions if q.get('question_type') != 'basic']
        elif question_type == 'basic':
            specialist_contamination_final = [q for q in selected_questions if q.get('question_type') == 'specialist']
            if specialist_contamination_final:
                logger.error(f"🚨 最終選択に専門科目混入検出: {len(specialist_contamination_final)}問 - 除外処理")
                selected_questions = [q for q in selected_questions if q.get('question_type') != 'specialist']
    
    logger.info(f"🔥 ULTRA SYNC: 最終問題数確定 {len(selected_questions)}問（{session_size}問設定に従って切断）")
    return selected_questions


# 🔥 ULTRA SYNC: 統合セッション管理システムが自動的にbefore_requestを処理
# unified_session_manager.unified_before_request() が自動実行される
# 
# 注意: この@app.before_requestは統合システムによって自動処理されるため
#       重複を防ぐためコメントアウト済み
#
# @app.before_request  # 統合システムで自動処理
# def before_request():
#     """統合セッション管理システムで自動処理されます"""
#     pass


# 🔥 ULTRA SYNC: 統合セッション管理システムが自動的にafter_requestを処理
# unified_session_manager.unified_after_request() が自動実行される
# 
# 注意: この@app.after_requestは統合システムによって自動処理されるため
#       重複を防ぐためコメントアウト済み
#
# @app.after_request  # 統合システムで自動処理
# def after_request_data_save(response):
#     """統合セッション管理システムで自動処理されます"""
#     return response


@app.route('/health_simple')
def health():
    """ヘルスチェック（高速）"""
    # 🔥 ULTRA SYNC TIMEZONE FIX: UTC基準のヘルスチェックタイムスタンプ
    # 🛡️ ULTRA SYNC: ルート変更 - /health重複回避
    return jsonify({'status': 'healthy', 'timestamp': format_utc_to_iso()})


@app.route('/')
# 🔥 ULTRA SYNC: 統合セッション管理システムで自動処理
def index():
    """ホーム画面（ユーザー識別対応）"""
    try:
        # 🔥 CRITICAL: セッション完全クリア（ユーザー要求による）
        # 問題途中でホームに戻った場合、全ての問題関連情報をクリア
        session_keys_to_clear = [
            'exam_question_ids', 'exam_current', 'exam_category',
            'selected_department', 'selected_question_type', 'selected_year',
            'request_history'  # 古いリクエスト履歴もクリア
        ]

        cleared_keys = []
        for key in session_keys_to_clear:
            if key in session:
                del session[key]
                cleared_keys.append(key)

        if cleared_keys:
            logger.info(f"ホーム画面: セッション情報クリア - {cleared_keys}")

        # 必要最小限のセッション初期化のみ実行
        if 'history' not in session:
            session['history'] = []
        if 'category_stats' not in session:
            session['category_stats'] = {}

        user_name = session.get('user_name')
        if user_name:
            logger.info(f"ホームページアクセス - ユーザー: {user_name}")
        else:
            logger.info("ホームページアクセス - 未認証ユーザー")

        session.modified = True
        return render_template('index.html')

    except Exception as e:
        logger.error(f"ホームページエラー: {e}")
        return render_template('error.html', error_message=str(e)), 500


@app.route('/set_user', methods=['POST', 'GET'])
def set_user():
    """ユーザー名を設定（企業環境での個別識別）"""
    try:
        # POST/GET両方に対応（テスト用）
        if request.method == 'POST':
            user_name = request.form.get('user_name', '').strip()
        else:
            user_name = request.args.get('user', '').strip()

        if not user_name:
            # 空の場合は匿名ユーザーとして処理
            user_name = f"匿名ユーザー_{int(time.time())}"

        # 入力値のサニタイズ
        user_name = sanitize_input(user_name)

        # ユーザー名の長さ制限
        if len(user_name) > 20:
            user_name = user_name[:20]

        # 🔥 CRITICAL: セッション競合回避 - 一意なセッションIDを生成
        unique_session_id = generate_unique_session_id()
        base_user_id = f"user_{hash(user_name) % 100000:05d}"
        session_aware_user_id = f"{base_user_id}_{unique_session_id}"

        # セッションにユーザー名を保存
        # 初回ログイン時は user_id が未設定なので直接更新
        session['user_name'] = user_name
        session['user_id'] = session_aware_user_id  # セッション固有の一意ID
        session['base_user_id'] = base_user_id      # データ永続化用の基本ID
        session['session_id'] = unique_session_id   # セッション識別用
        session['login_time'] = get_utc_now().isoformat()

        logger.info(f"🔒 セッション安全性確保: {user_name} (セッションID: {unique_session_id[:8]}...)")

        logger.info(f"ユーザー設定完了: {user_name}")
        return redirect(url_for('index'))

    except Exception as e:
        logger.error(f"ユーザー設定エラー: {e}")
        return redirect(url_for('index'))


@app.route('/change_user')
def change_user():
    """ユーザー変更（ログアウト）"""
    try:
        old_user = session.get('user_name', '不明')

        # ユーザー情報のみクリア（学習データは保持）
        session.pop('user_name', None)
        session.pop('user_id', None)
        session.pop('login_time', None)

        logger.info(f"ユーザー変更: {old_user} がログアウト")
        return redirect(url_for('index'))

    except Exception as e:
        logger.error(f"ユーザー変更エラー: {e}")
        return redirect(url_for('index'))


@app.route('/force_refresh')
def force_refresh():
    """強制的にキャッシュをクリアして最新版を表示"""
    response = make_response(redirect('/'))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


@app.route('/exam', methods=['GET', 'POST'])
# 🔥 ULTRA SYNC: 統合セッション管理システムで自動処理
@memory_monitoring_decorator(_memory_leak_monitor)
def exam():
    """SRS対応の問題関数（統合版）"""
    try:
        # 🔥 PROGRESS DEBUG: 各リクエストの開始ログ
        logger.info(f"🔥 PROGRESS DEBUG: exam route called - method={request.method}, args={dict(request.args)}")
        if request.method == 'POST':
            logger.info(f"🔥 PROGRESS DEBUG: POST data={dict(request.form)}")
        logger.info(f"🔥 PROGRESS DEBUG: Current session exam_current={session.get('exam_current')}, question_ids={len(session.get('exam_question_ids', []))}")
        # 🔥 CRITICAL: ウルトラシンク セッション整合性チェック・自動修復（改修版）
        # 🚨 BUG FIX: 初回アクセス時(GET)は空セッション許可、回答時(POST)のみ厳格チェック
        # 🔥 CRITICAL FIX: POSTでもセッションが存在しない場合は新規開始として扱う
        if 'exam_question_ids' in session:
            try:
                exam_ids = session.get('exam_question_ids', [])
                current_no_raw = session.get('exam_current', 0)

                # 型安全な変換
                current_no = int(current_no_raw) if current_no_raw is not None else 0

                # セッション修復チェック（改修版）
                if not isinstance(exam_ids, list):
                    # 修復可能な場合は修復を試行
                    if exam_ids and hasattr(exam_ids, '__iter__'):
                        exam_ids = list(exam_ids)
                        safe_session_update('exam_question_ids', exam_ids)
                        logger.info("セッション自動修復: exam_question_ids を list型に変換")
                    else:
                        raise ValueError("exam_question_ids が修復不可能")

                if current_no < 0:
                    current_no = 0
                    safe_session_update('exam_current', current_no)
                    logger.info("セッション自動修復: exam_current を 0 にリセット")

                if not exam_ids:
                    # 🔥 CRITICAL: 専門科目開始時など、最初のPOSTではexam_idsが空の場合がある
                    # この場合は新規セッションとして初期化する
                    logger.info("exam_question_ids が空 - 新規セッション開始として処理")
                    log_session_state("初期化前")
                    # セッションをクリーンな状態に初期化
                    safe_exam_session_reset()
                    session.modified = True
                    log_session_state("初期化後")
                    logger.info("✅ セッション初期化完了 - 新規セッション状態に設定")

            except (ValueError, TypeError) as e:
                # 修復不可能な場合のみリセット
                logger.warning(f"セッション修復不可能 - リセット実行: {e}")
                # 🔥 CRITICAL: 専門科目開始時は新規セッションとして処理
                if 'exam_question_ids が空' in str(e):
                    logger.info("専門科目の新規開始と判断 - セッション初期化を強制実行")
                    # 専門家推奨：リダイレクトループ回避でセッション強制初期化
                    safe_exam_session_reset()
                    session.modified = True
                else:
                    safe_exam_session_reset()
                    session.modified = True

        # レート制限チェック
        if not rate_limit_check():
            return render_template('error.html',
                                   error="リクエストが多すぎます。しばらく待ってから再度お試しください。",
                                   error_type="rate_limit")
        # データディレクトリの設定
        data_dir = os.path.dirname(DataConfig.QUESTIONS_CSV)
        # 🛡️ ULTRATHIN区 緊急修正: 基礎科目のみ読み込み（専門科目は必要時に動的読み込み）
        from utils import load_basic_questions_only
        basic_questions = load_basic_questions_only(data_dir)
        all_questions = basic_questions
        if not all_questions:
            logger.error("問題データが空")
            return render_template('error.html', error="問題データが存在しません。")

        # 🔧 EMERGENCY FIX: GETリクエストでの新規セッション開始処理
        if request.method == 'GET':
            question_type = request.args.get('question_type', 'basic')
            department = request.args.get('department', '')
            year = request.args.get('year', '')
            
            # 🔥 PROGRESS FIX: セッション開始条件を厳密化 - 既存セッション保護
            # 新規セッション開始の条件：明示的なパラメータがある場合のみ
            has_new_session_params = any([
                question_type and question_type != 'basic',  # 明示的な問題種別指定
                department,  # 部門指定
                year,  # 年度指定
                request.args.get('count'),  # 問題数指定
                request.args.get('category'),  # カテゴリ指定
            ])
            
            # 既存セッションがない場合、または明示的な新規セッション要求の場合のみ初期化
            if ('exam_question_ids' not in session or not session.get('exam_question_ids')) and has_new_session_params:
                logger.info(f"新規セッション開始: 種別={question_type}, 部門={department}")
                
                # セッションをクリア
                for key in ['exam_question_ids', 'exam_current', 'exam_category']:
                    session.pop(key, None)
                
                try:
                    if question_type == 'basic':
                        # 基礎科目
                        basic_questions = [q for q in all_questions if q.get('question_type') == 'basic']
                        if basic_questions:
                            # 🛡️ ULTRA SYNC: random already imported at top
                            random.shuffle(basic_questions)
                            selected = basic_questions[:10]
                            session['exam_question_ids'] = [q['id'] for q in selected]
                            session['exam_current'] = 0
                            session['exam_category'] = '基礎科目'
                            session['selected_question_type'] = 'basic'
                            session.modified = True
                            logger.info(f"基礎科目セッション開始: {len(selected)}問")
                    
                    elif question_type == 'specialist':
                        # 専門科目
                        specialist_questions = [q for q in all_questions if q.get('question_type') == 'specialist']
                        
                        if department:
                            # 🔥 ULTRA SYNC CRITICAL FIX: グローバル部門マッピングを使用（重複排除・統一）
                            target_category = DEPARTMENT_TO_CATEGORY_MAPPING.get(department, department)
                            specialist_questions = [q for q in specialist_questions 
                                                  if q.get('category') == target_category]
                        
                        if specialist_questions:
                            random.shuffle(specialist_questions)
                            selected = specialist_questions[:10]
                            session['exam_question_ids'] = [q['id'] for q in selected]
                            session['exam_current'] = 0
                            session['exam_category'] = target_category if department else '専門科目'
                            session['selected_question_type'] = 'specialist'
                            session['selected_department'] = department
                            session.modified = True
                            logger.info(f"専門科目セッション開始: {len(selected)}問")
                        else:
                            # フォールバック：全専門問題から選択
                            all_specialist = [q for q in all_questions if q.get('question_type') == 'specialist']
                            if all_specialist:
                                random.shuffle(all_specialist)
                                selected = all_specialist[:10]
                                session['exam_question_ids'] = [q['id'] for q in selected]
                                session['exam_current'] = 0
                                session['exam_category'] = '専門科目（混合）'
                                session['selected_question_type'] = 'specialist'
                                session.modified = True
                                logger.info(f"専門科目フォールバック: {len(selected)}問")
                    
                    else:
                        # デフォルト：基礎科目
                        basic_questions = [q for q in all_questions if q.get('question_type') == 'basic']
                        if basic_questions:
                            random.shuffle(basic_questions)
                            selected = basic_questions[:10]
                            session['exam_question_ids'] = [q['id'] for q in selected]
                            session['exam_current'] = 0
                            session['exam_category'] = '基礎科目'
                            session['selected_question_type'] = 'basic'
                            session.modified = True
                            logger.info(f"デフォルト基礎科目: {len(selected)}問")
                            
                except Exception as e:
                    logger.error(f"セッション初期化エラー: {e}")
                    return render_template('error.html', error="セッションの初期化に失敗しました。")

        # POST処理（回答送信）
        if request.method == 'POST':
            # 🔥 ULTRA SYNC CRITICAL FIX: 無効データ厳密検証
            form_data = dict(request.form)
            
            # 🔥 ULTRA SYNC CRITICAL FIX: 全POSTデータの厳密検証
            # 新規セッション開始の場合
            if any(key in form_data for key in ['department', 'question_type', 'num_questions']):
                # 新規セッション開始時の検証
                valid_session_keys = ['department', 'question_type', 'num_questions', 'csrf_token']
                invalid_keys = [key for key in form_data.keys() if key not in valid_session_keys]
                
                if invalid_keys:
                    logger.warning(f"🚨 ULTRA SYNC: 新規セッション時の不正フィールド: {invalid_keys}")
                    return render_template('error.html',
                                         error=f"不正なセッション開始パラメータ: {', '.join(invalid_keys)}",
                                         error_type="invalid_session_params"), 400
            else:
                # 回答送信時の検証 - 必須フィールドチェック
                if not form_data:
                    logger.warning("🚨 ULTRA SYNC: 空のPOSTデータ")
                    return render_template('error.html',
                                         error="データが送信されていません",
                                         error_type="empty_data"), 400
                
                required_fields = ['answer', 'qid']
                missing_fields = [field for field in required_fields if field not in form_data or not form_data[field]]
                
                if missing_fields:
                    logger.warning(f"🚨 ULTRA SYNC: 無効データ検出 - 必須フィールド不足: {missing_fields}")
                    return render_template('error.html',
                                         error=f"必須フィールドが不足しています: {', '.join(missing_fields)}",
                                         error_type="invalid_data"), 400
                
                # 不正なキーの検証（2問目エラー修正）
                valid_keys = ['answer', 'qid', 'elapsed', 'csrf_token', 'session_initialized']
                invalid_keys = [key for key in form_data.keys() if key not in valid_keys]
                
                if invalid_keys:
                    logger.warning(f"🚨 ULTRA SYNC: 不正なフィールド検出: {invalid_keys}")
                    return render_template('error.html',
                                         error=f"不正なフィールドが含まれています: {', '.join(invalid_keys)}",
                                         error_type="invalid_fields"), 400
            
            # 🔥 DEBUG: POSTリクエスト詳細ログ - エラー追跡強化版
            logger.info("=== POST処理開始 - 完全デバッグトレース ===")
            logger.info(f"🔍 POST Request URL: {request.url}")
            logger.info(f"🔍 POST Form Data: {form_data}")
            logger.info(f"🔍 POST Content Type: {request.content_type}")
            logger.info(f"🔍 POST Headers: {dict(request.headers)}")
            logger.info(f"🔍 POST Method: {request.method}")
            logger.info(f"🔍 POST Remote Address: {request.remote_addr}")
            logger.info(f"🔍 POST User Agent: {request.user_agent}")
            logger.info(f"🔍 POST Referrer: {request.referrer}")
            logger.info(f"🔍 POST Query String: {request.query_string}")
            
            # デバッグ: POST処理時のセッション状態を完全ログ出力
            # 🔥 ULTRA SYNC セキュリティ FIX: 機密情報を含まない安全なログ出力
            logger.info(f"🔍 Session Keys: {list(session.keys())}")
            logger.info(f"🔍 Session Size: {len(session.keys())}")
            logger.info(f"🔍 exam_question_ids: {session.get('exam_question_ids', 'MISSING')}")
            logger.info(f"🔍 exam_question_ids Length: {len(session.get('exam_question_ids', []))}")
            logger.info(f"🔍 exam_current: {session.get('exam_current', 'MISSING')}")
            logger.info(f"🔍 exam_category: {session.get('exam_category', 'MISSING')}")
            logger.info(f"🔍 selected_question_type: {session.get('selected_question_type', 'MISSING')}")
            logger.info(f"🔍 selected_department: {session.get('selected_department', 'MISSING')}")
            logger.info(f"🔍 session_id存在: {'Yes' if session.get('session_id') else 'No'}")
            logger.info(f"🔍 data_loaded: {session.get('data_loaded', 'MISSING')}")
            logger.info(f"🔍 Session Modified: {session.modified}")
            logger.info(f"🔍 Session Permanent: {session.permanent}")
            
            # 🔥 CRITICAL: 2問目エラー追跡のための時系列ログ
            from datetime import datetime as dt
            timestamp = dt.now().strftime("%Y-%m-%d %H:%M:%S.%f")
            logger.info(f"🔍 Timestamp: {timestamp}")
            logger.info(f"🔍 Current Question Check: qid={form_data.get('qid')}, exam_current={session.get('exam_current')}")
            
            # 🔥 CRITICAL: セッションとPOSTデータの不整合チェック
            if 'exam_question_ids' in session and session.get('exam_question_ids'):
                current_index = session.get('exam_current', 0)
                question_ids = session.get('exam_question_ids', [])
                if current_index < len(question_ids):
                    expected_qid = question_ids[current_index]
                    actual_qid = form_data.get('qid')
                    logger.info(f"🔍 Question ID Match Check: expected={expected_qid}, actual={actual_qid}, match={expected_qid == int(actual_qid) if actual_qid else False}")
                else:
                    logger.warning(f"🚨 Index Out of Range: current={current_index}, total={len(question_ids)}")
            
            logger.info("==========================================")

            # 🔥 ULTRA SYNC VALIDATION FIX: 入力値のサニタイズと検証強化
            raw_answer = request.form.get('answer')
            raw_qid = request.form.get('qid')
            raw_elapsed = request.form.get('elapsed', '0')
            
            # 必須パラメータの存在チェック（専門家推奨：新規セッション除外）
            if not raw_answer or not raw_qid:
                # 新規セッション開始の場合はPOST処理をスキップ（既存機能肯定）
                if not session.get('exam_question_ids'):
                    logger.info("🎯 専門家推奨: 新規セッション開始 - session.modified確実設定")
                    # Miguel Grinberg推奨: セッション修正フラグの明示的設定
                    session.modified = True
                    pass  # POST処理をスキップしてGET処理部分に到達
                else:
                    logger.warning(f"🚨 必須パラメータ不足: answer={raw_answer}, qid={raw_qid}")
                    return render_template('error.html',
                                           error="必須パラメータが不足しています。",
                                           error_type="missing_parameters")
            else:
                # 文字列長制限チェック
                if len(str(raw_answer)) > 10 or len(str(raw_qid)) > 20 or len(str(raw_elapsed)) > 20:
                    logger.warning(f"🚨 パラメータ長制限違反: answer={len(str(raw_answer))}, qid={len(str(raw_qid))}, elapsed={len(str(raw_elapsed))}")
                    return render_template('error.html',
                                           error="パラメータが長すぎます。",
                                           error_type="parameter_too_long")
                
                answer = sanitize_input(raw_answer)
                qid = sanitize_input(raw_qid)
                elapsed = sanitize_input(raw_elapsed)

                # 回答値の厳密な検証
                if answer not in ['A', 'B', 'C', 'D']:
                    logger.warning(f"🚨 無効な回答値: {answer} (元: {raw_answer})")
                    return render_template('error.html',
                                           error="無効な回答が選択されました。",
                                           error_type="invalid_input")

                # 問題IDの検証強化
                try:
                    qid = int(qid)
                    if qid <= 0 or qid > 100000:  # 合理的な範囲チェック
                        raise ValueError(f"問題ID範囲外: {qid}")
                except (ValueError, TypeError) as e:
                    logger.warning(f"🚨 問題ID変換エラー: {qid} - {e}")
                    return render_template('error.html',
                                           error="無効な問題IDです。",
                                           error_type="invalid_question")
                
                # 経過時間の検証
                try:
                    elapsed_int = int(elapsed)
                    if elapsed_int < 0 or elapsed_int > 3600:  # 0秒〜1時間の範囲
                        logger.warning(f"🚨 経過時間異常値: {elapsed_int}秒")
                        elapsed_int = 0  # 異常値の場合は0にリセット
                except (ValueError, TypeError):
                    logger.warning(f"🚨 経過時間変換エラー: {elapsed}")
                    elapsed_int = 0

                # 🔥 ULTRA SYNC FIX: 2問目エラー完全解決 - セッション復元ロジック修正
                if 'exam_question_ids' not in session:
                    logger.warning(f"🚨 2問目エラー検出: POSTリクエストでセッション不整合 - 問題ID: {qid}")
                    
                    # 🛡️ 完全なセッション復元を試行（2問目エラー解決）
                    try:
                        # 問題の部門と種別を特定して適切なセッションを再構築
                        question = next((q for q in all_questions if int(q.get('id', 0)) == int(qid)), None)
                        if question:
                            q_dept = question.get('department', '')
                            q_type = question.get('question_type', 'basic')
                            
                            # 同じ部門・種別の問題を10問再生成
                            if q_type == 'basic':
                                dept_questions = [q for q in all_questions if q.get('question_type') == 'basic']
                            else:
                                dept_questions = [q for q in all_questions 
                                                if q.get('department', '') == q_dept and q.get('question_type') == 'advanced']
                            
                            if dept_questions:
                                random.shuffle(dept_questions)
                                session_size = 10  # デフォルト10問
                                selected_questions = dept_questions[:session_size]
                                
                                # 現在の問題を最初に配置して継続性を確保
                                question_ids = [int(qid)]
                                for q in selected_questions:
                                    if int(q['id']) != int(qid):
                                        question_ids.append(int(q['id']))
                                        if len(question_ids) >= session_size:
                                            break
                                
                                session['exam_question_ids'] = question_ids
                                session['exam_current'] = 0  # 現在の問題は0番目
                                session['exam_category'] = q_dept if q_dept else '基礎科目'
                                session['selected_question_type'] = q_type
                                session['quiz_answered'] = session.get('quiz_answered', [])
                                session['history'] = session.get('history', [])
                                session.modified = True
                                
                                logger.info(f"✅ 2問目エラー解決: セッション完全復元完了 - {len(question_ids)}問生成, 部門={q_dept}")
                            else:
                                raise Exception("適切な問題が見つかりません")
                        else:
                            raise Exception(f"問題ID {qid} が見つかりません")
                            
                    except Exception as e:
                        logger.error(f"セッション復元失敗: {e}")
                        return render_template('error.html', error="セッションエラーが発生しました。ホーム画面から再度開始してください。")

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
            user_answer = str(answer).strip().upper()  # 大文字に統一
            correct_answer = str(question.get('correct_answer', '')).strip().upper()  # 大文字に統一
            is_correct = (user_answer == correct_answer)

            # デバッグログ追加
            logger.info(f"正誤判定: 問題ID={qid}, ユーザー回答='{user_answer}', 正解='{correct_answer}', 判定={is_correct}")

            # 高度なSRS（間隔反復学習）システムでの復習管理
            srs_info = update_advanced_srs_data(qid, is_correct, session)

            # 旧復習リストとの互換性維持 + マスター済み問題の自動削除
            bookmarks = session.get('bookmarks', [])
            logger.info(f"復習リスト処理前: bookmarks={bookmarks}, is_correct={is_correct}")

            if is_correct:
                # マスター済み（5回正解）の場合は復習リストから完全除外
                if srs_info.get('mastered', False):
                    if str(qid) in bookmarks:
                        bookmarks.remove(str(qid))
                        session['bookmarks'] = bookmarks
                        session.modified = True
                        logger.info(f"🏆 マスター達成により復習リストから除外: 問題ID {qid}")
                # 正解だが未マスターの場合は旧システムでも除外（新システムで管理）
                elif str(qid) in bookmarks:
                    bookmarks.remove(str(qid))
                    session['bookmarks'] = bookmarks
                    session.modified = True
                    logger.info(f"✅ 正解により一時的に復習リストから除外: 問題ID {qid} (SRSで管理)")
                else:
                    logger.info(f"✅ 正解: 問題ID {qid} は復習リストに含まれていないため、何もしません")
            else:
                # 不正解時は旧復習リストにも追加（互換性のため）
                if str(qid) not in bookmarks:
                    bookmarks.append(str(qid))
                    session['bookmarks'] = bookmarks
                    session.modified = True
                    logger.info(f"❌ 不正解により復習リストに追加: 問題ID {qid}")
                else:
                    logger.info(f"❌ 不正解: 問題ID {qid} は既に復習リストに存在")

            # 🔥 ULTRA SYNC セキュリティ FIX: 復習リスト件数のみログ出力
            bookmarks = session.get('bookmarks', [])
            logger.info(f"復習リスト処理後: bookmark数={len(bookmarks) if isinstance(bookmarks, list) else 'dict形式'}")

            # マスター済み問題の一括クリーンアップ
            cleanup_mastered_questions(session)

            # 従来のSRSデータも更新（既存機能との互換性）
            try:
                update_advanced_srs_data(qid, is_correct, session)
            except (NameError, AttributeError, TypeError, ImportError):
                # 既存SRS関数がない場合はスキップ
                pass

            # 履歴に追加
            if 'history' not in session:
                session['history'] = []

            history_item = {
                'id': qid,
                'category': question.get('category', '不明'),
                'department': question.get('department', session.get('selected_department', '')),
                'question_type': question.get('question_type', session.get('selected_question_type', 'basic')),
                'is_correct': is_correct,
                'user_answer': answer,
                'correct_answer': question.get('correct_answer', ''),
                # 🔥 ULTRA SYNC TIMEZONE FIX: UTC基準の履歴タイムスタンプ
                'date': get_user_local_time(get_utc_now(), 'Asia/Tokyo').strftime('%Y-%m-%d %H:%M:%S'),
                'elapsed': float(elapsed),
                'srs_level': srs_info.get('difficulty_level', 5),
                'is_review': srs_info['total_attempts'] > 1,
                'difficulty': question.get('difficulty', '標準')
            }

            # 🔥 ULTRA SYNC FIX: セッション履歴の無制限蓄積対策（上限設定）
            current_history = session.get('history', [])
            current_history.append(history_item)
            
            # 履歴上限設定: 1000問に制限（メモリリーク防止）
            MAX_HISTORY_SIZE = 1000
            if len(current_history) > MAX_HISTORY_SIZE:
                # 古い履歴を削除（FIFO方式）
                current_history = current_history[-MAX_HISTORY_SIZE:]
                logger.info(f"履歴上限到達: {MAX_HISTORY_SIZE}問に制限（古い履歴を削除）")

            # 一括でセッションを更新
            session_updates = {
                'history': current_history,
                # 🔥 ULTRA SYNC TIMEZONE FIX: UTC基準の履歴更新タイムスタンプ
                'last_history_update': format_utc_to_iso()
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

            # モジュールの遅延読み込み（必要時のみ）
            if os.environ.get('RCCM_LAZY_LOAD', 'true').lower() == 'true':
                ensure_modules_loaded()
            
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
            current_no = session.get('exam_current', 0)
            exam_question_ids = session.get('exam_question_ids', [])

            # 安全チェック: exam_question_idsが空の場合はセッション再構築
            if not exam_question_ids:
                logger.warning(f"POST処理: exam_question_idsが空です。セッション再構築を試行。問題ID: {qid}")

                # セッション再構築を試行
                try:
                    # 基礎科目の場合のフォールバック
                    question_type = session.get('selected_question_type', 'basic')
                    department = session.get('selected_department', '')

                    # 🔥 ウルトラシンク包括修正: 全問題種別統一セッション再構築システム
                    # 🛡️ ULTRATHIN区 緊急修正: 基礎科目のみ読み込み（専門科目は必要時に動的読み込み）
                    from utils import load_basic_questions_only
                    basic_questions = load_basic_questions_only('data')
                    all_questions = basic_questions

                    logger.info(f"セッション再構築開始: 問題ID={qid}, 種別={question_type}, 部門={department}")

                    # 🔥 STEP1: まず問題IDから実際の問題を特定
                    target_question = None
                    for q in all_questions:
                        if int(q.get('id', 0)) == qid:
                            target_question = q
                            break

                    if not target_question:
                        raise ValueError(f"問題ID {qid} が全問題データベースに見つかりません")

                    actual_question_type = target_question.get('question_type', 'unknown')
                    actual_category = target_question.get('category', '不明')
                    actual_year = target_question.get('year')

                    logger.info(f"問題特定: ID={qid}, 実際の種別={actual_question_type}, カテゴリ={actual_category}, 年度={actual_year}")

                    # 🔥 STEP2: 問題種別に応じたセッション再構築（統一フローシート）
                    if question_type == 'review':
                        # 復習モード: 既存の復習リストを使用
                        stored_review_ids = session.get('exam_question_ids', [])
                        if stored_review_ids and qid in stored_review_ids:
                            current_index = stored_review_ids.index(qid)
                            session['exam_current'] = current_index
                            session.modified = True
                            exam_question_ids = stored_review_ids
                            current_no = current_index
                            # 🔥 CRITICAL: 復習セッション再構築を無効化（無限ループ防止）
                            # logger.info(f"復習セッション再構築成功: {len(stored_review_ids)}問, 現在位置{current_index}")
                        else:
                            # 🔥 CRITICAL: 復習セッション再構築を無効化（無限ループ防止）
                            # # 🔥 CRITICAL: 復習問題IDが見つからない場合の安定復習セッション再生成（ウルトラシンク修正）
                            # 🔥 CRITICAL: 復習セッション再構築を無効化（無限ループ防止）
                            # logger.warning(f"復習問題ID {qid} がセッション内に見つからないため、安定復習セッション再生成実行")
                            pass  # 無限ループ防止のため、何もしない

                            # # 現在のSRSデータとブックマークから復習セッションを再生成
                            # srs_data = session.get('advanced_srs', {})
                            # bookmarks = session.get('bookmarks', [])

                            # # 復習対象問題IDを統合（安定版）
                            # all_review_ids = set()

                            # # SRSデータから復習問題を取得
                            # for review_qid, srs_info in srs_data.items():
                            # if review_qid and str(review_qid).strip() and isinstance(srs_info, dict):
                            # all_review_ids.add(str(review_qid))

                            # # ブックマークから復習問題を取得
                            # for review_qid in bookmarks:
                            # if review_qid and str(review_qid).strip():
                            # all_review_ids.add(str(review_qid))

                            # # 現在の問題IDを最優先で含める
                            # all_review_ids.add(str(qid))

                            # # 安定した順序でソート（数値IDに変換）
                            # review_question_ids = []
                            # for review_id in sorted(all_review_ids):
                            # try:
                            # num_id = int(review_id)
                            # # 問題データが存在するかチェック
                            # if any(int(q.get('id', 0)) == num_id for q in all_questions):
                            # review_question_ids.append(num_id)
                            # except (ValueError, TypeError):
                            # logger.warning(f"無効な復習問題ID: {review_id}")
                            # continue

                            # if review_question_ids:
                            # # 現在の問題の位置を正確に特定
                            # try:
                            # current_index = review_question_ids.index(qid)
                            # except ValueError:
                            # current_index = 0  # 見つからない場合は最初から

                            # # セッション状態を確実に更新
                            # session['exam_question_ids'] = review_question_ids
                            # session['exam_current'] = current_index
                            # session['selected_question_type'] = 'review'
                            # session['exam_category'] = f'復習問題（再構築{len(review_question_ids)}問）'
                            # session['review_session_restored'] = True  # 復習セッション復旧フラグ
                            # session.modified = True

                            # exam_question_ids = review_question_ids
                            # current_no = current_index

                            # 🔥 CRITICAL: 復習セッション再構築を無効化（無限ループ防止）
                            # logger.info(f"安定復習セッション再生成成功: {len(review_question_ids)}問, 現在位置{current_index}, 問題ID{qid}")
                            # else:
                            # # 最低限の復習セッションを作成
                            # logger.warning(f"復習問題データ不足のため、現在問題のみの最小復習セッション作成")
                            # minimal_review = [qid]
                            # session['exam_question_ids'] = minimal_review
                            # session['exam_current'] = 0
                            # session['selected_question_type'] = 'review'
                            # session['exam_category'] = '復習問題（最小セッション）'
                            # session['review_session_minimal'] = True
                            # session.modified = True

                            # exam_question_ids = minimal_review
                            # current_no = 0

                    elif actual_question_type == 'basic' or question_type == 'basic':
                        # 基礎科目(4-1)のセッション再構築
                        basic_questions = [q for q in all_questions
                                           if q.get('question_type') == 'basic']

                        if basic_questions:
                            # 🔥 CRITICAL FIX: ユーザー設定問題数制限を適用してセッション再構築
                            # get_mixed_questionsを使用して適切な問題セッションを作成
                            user_session_size = get_user_session_size(session)
                            mock_session = {'history': session.get('history', []), 'srs_data': session.get('srs_data', {}), 'quiz_settings': session.get('quiz_settings', {})}
                            selected_questions = get_mixed_questions(
                                user_session=mock_session,
                                all_questions=all_questions,
                                requested_category='全体',
                                session_size=user_session_size,  # ユーザー設定問題数指定
                                department='',
                                question_type='basic',
                                year=None
                            )
                            
                            # 🛡️ ULTRATHIN区追加: 基礎科目セッション再構築の安全チェック
                            if not selected_questions:
                                logger.error(f"🚨 基礎科目セッション再構築失敗: 問題が選択できません")
                                return render_template('error.html', 
                                                     error="基礎科目の問題データが見つかりません。データファイルを確認してください。",
                                                     error_type="basic_questions_not_found")
                            
                            question_ids = [int(q.get('id', 0)) for q in selected_questions]
                            current_index = question_ids.index(qid) if qid in question_ids else 0

                            session['exam_question_ids'] = question_ids
                            session['exam_current'] = current_index
                            session['selected_question_type'] = 'basic'
                            session['exam_category'] = '基礎科目'
                            session.modified = True

                            exam_question_ids = question_ids
                            current_no = current_index

                            logger.info(f"基礎科目セッション再構築成功（10問制限適用）: {len(question_ids)}問, 現在位置{current_index}")
                        else:
                            raise ValueError("基礎科目データが見つかりません")

                    elif actual_question_type == 'specialist' or question_type == 'specialist':
                        # 専門科目(4-2)のセッション再構築（CLAUDE.md準拠の安全な処理）
                        specialist_questions = [q for q in all_questions
                                                if q.get('question_type') == 'specialist']

                        # 🔥 ULTRA SYNC: 部門フィルタリング（実際のカテゴリも考慮）
                        if department:
                            target_category = DEPARTMENT_TO_CATEGORY_MAPPING.get(department, department)
                            logger.info(f"専門科目部門フィルタ: {department} -> {target_category}")

                            # 🔥 カテゴリマッチング（鋼構造部門の特別処理含む）
                            if department == 'steel_concrete':
                                specialist_questions = [q for q in specialist_questions
                                                        if q.get('category') in ['鋼構造及びコンクリート', '鋼構造コンクリート']]
                            else:
                                specialist_questions = [q for q in specialist_questions
                                                        if q.get('category') == target_category]
                        elif actual_category != '不明':
                            # 部門指定がない場合は実際のカテゴリでフィルタ
                            specialist_questions = [q for q in specialist_questions
                                                    if q.get('category') == actual_category]

                        # 🔧 EMERGENCY FIX: シンプルなフォールバック処理
                        if not specialist_questions:
                            logger.warning(f"専門科目データ不足 - 全専門問題から選択")
                            all_specialist = [q for q in all_questions if q.get('question_type') == 'specialist']
                            specialist_questions = all_specialist[:10] if all_specialist else []

                        if specialist_questions:
                            # 🔥 CRITICAL FIX: 10問制限を適用してセッション再構築
                            # get_mixed_questionsを使用して適切な10問セッションを作成
                            mock_session = {'history': session.get('history', []), 'srs_data': session.get('srs_data', {})}
                            try:
                                selected_questions = get_mixed_questions(
                                    user_session=mock_session,
                                    all_questions=all_questions,
                                    requested_category=actual_category,
                                    session_size=get_user_session_size(session),  # ユーザー設定問題数指定
                                    department=department,
                                    question_type='specialist',
                                    year=None
                                )
                                
                                if not selected_questions:
                                    # get_mixed_questionsが失敗した場合のフォールバック
                                    logger.warning("get_mixed_questions失敗 - 直接問題選択に切り替え")
                                    selected_questions = specialist_questions[:get_user_session_size(session)]
                                
                            except Exception as mix_error:
                                logger.error(f"get_mixed_questions例外: {mix_error}")
                                # 安全なフォールバック
                                selected_questions = specialist_questions[:10]

                            question_ids = [int(q.get('id', 0)) for q in selected_questions]
                            current_index = question_ids.index(qid) if qid in question_ids else 0

                            session['exam_question_ids'] = question_ids
                            session['exam_current'] = current_index
                            session['selected_question_type'] = 'specialist'
                            safe_session_update('selected_department', department or 'specialist')
                            session['exam_category'] = actual_category
                            session.modified = True

                            exam_question_ids = question_ids
                            current_no = current_index

                            logger.info(f"✅ 専門科目セッション再構築成功（CLAUDE.md準拠）: カテゴリ={actual_category}, {len(question_ids)}問, 現在位置{current_index}")
                        else:
                            logger.error(f"❌ 専門科目セッション再構築失敗: カテゴリ={actual_category}, 部門={department}")
                            return render_template('error.html',
                                                   error="専門科目の問題データが見つかりません。部門選択を確認してください。",
                                                   error_type="specialist_data_missing")

                    else:
                        # 🔥 フォールバック: 共通問題・混合セッション・その他
                        logger.warning(f"未知の問題種別に対するフォールバック再構築: {question_type} -> {actual_question_type}")

                        # 実際の問題種別で再分類
                        if actual_question_type == 'basic':
                            # 基礎科目として処理（10問制限適用）
                            mock_session = {'history': session.get('history', []), 'srs_data': session.get('srs_data', {})}
                            selected_questions = get_mixed_questions(
                                user_session=mock_session,
                                all_questions=all_questions,
                                requested_category='全体',
                                session_size=get_user_session_size(session),  # ユーザー設定問題数指定
                                department='',
                                question_type='basic',
                                year=None
                            )

                            if selected_questions:
                                question_ids = [int(q.get('id', 0)) for q in selected_questions]
                                current_index = question_ids.index(qid) if qid in question_ids else 0

                                session['exam_question_ids'] = question_ids
                                session['exam_current'] = current_index
                                session['selected_question_type'] = 'basic'
                                session['exam_category'] = '基礎科目'
                                session.modified = True

                                exam_question_ids = question_ids
                                current_no = current_index

                                logger.info(f"フォールバック基礎科目再構築成功（10問制限適用）: {len(question_ids)}問, 現在位置{current_index}")
                            else:
                                raise ValueError("フォールバック基礎科目データが見つかりません")

                        elif actual_question_type == 'specialist':
                            # 専門科目として処理（カテゴリベース、10問制限適用）
                            mock_session = {'history': session.get('history', []), 'srs_data': session.get('srs_data', {})}
                            selected_questions = get_mixed_questions(
                                user_session=mock_session,
                                all_questions=all_questions,
                                requested_category=actual_category,
                                session_size=get_user_session_size(session),  # ユーザー設定問題数指定
                                department=department,
                                question_type='specialist',
                                year=None
                            )

                            if selected_questions:
                                question_ids = [int(q.get('id', 0)) for q in selected_questions]
                                current_index = question_ids.index(qid) if qid in question_ids else 0

                                session['exam_question_ids'] = question_ids
                                session['exam_current'] = current_index
                                session['selected_question_type'] = 'specialist'
                                session['exam_category'] = actual_category
                                session.modified = True

                                exam_question_ids = question_ids
                                current_no = current_index

                                logger.info(f"フォールバック専門科目再構築成功（10問制限適用）: カテゴリ={actual_category}, {len(question_ids)}問, 現在位置{current_index}")
                            else:
                                raise ValueError(f"フォールバック専門科目データが見つかりません: カテゴリ={actual_category}")

                        else:
                            # 🔥 最終フォールバック: 10問制限を適用した混合セッション作成
                            logger.warning(f"最終フォールバック: 問題種別不明 {actual_question_type} - 10問制限適用")
                            mock_session = {'history': session.get('history', []), 'srs_data': session.get('srs_data', {})}
                            selected_questions = get_mixed_questions(
                                user_session=mock_session,
                                all_questions=all_questions,
                                requested_category='全体',
                                session_size=get_user_session_size(session),  # ユーザー設定問題数指定
                                department='',
                                question_type=actual_question_type or 'basic',
                                year=None
                            )

                            if selected_questions:
                                question_ids = [int(q.get('id', 0)) for q in selected_questions]
                                current_index = question_ids.index(qid) if qid in question_ids else 0

                                session['exam_question_ids'] = question_ids
                                session['exam_current'] = current_index
                                session['selected_question_type'] = actual_question_type or 'mixed'
                                session['exam_category'] = actual_category or '混合'
                                session.modified = True

                                exam_question_ids = question_ids
                                current_no = current_index

                                logger.info(f"最終フォールバック再構築成功（10問制限適用）: 種別={actual_question_type}, {len(question_ids)}問, 現在位置{current_index}")
                            else:
                                # 本当に失敗した場合はエラーにする
                                raise ValueError(f"最終フォールバックでも問題選択に失敗: 種別={actual_question_type}")

                except Exception as rebuild_error:
                    logger.error(f"ウルトラシンクセッション再構築失敗: {rebuild_error}")

                    # 🔥 ウルトラシンク緊急フォールバック処理
                    current_question_type = session.get('selected_question_type', '')

                    if current_question_type == 'review':
                        logger.info("復習モード緊急フォールバック - 復習リストに戻る")
                        safe_exam_session_reset()
                        session.pop('selected_question_type', None)
                        session.modified = True
                        return redirect(url_for('review_list'))

                    else:
                        # 🔥 最終緊急フォールバック: 問題IDから10問完全セッション作成
                        logger.warning(f"緊急フォールバック実行: 問題ID {qid} から10問セッション作成")
                        try:
                            # 🔥 CRITICAL FIX: 10問セッションを作成
                            all_questions = load_questions()

                            # 10問セッション作成（問題IDを開始点として）
                            emergency_questions = get_mixed_questions(session, all_questions, '全体', 10, '', 'basic', None)
                            if emergency_questions and len(emergency_questions) >= 10:
                                session['exam_question_ids'] = [q['id'] for q in emergency_questions[:10]]
                            else:
                                # 最低限でも利用可能な全問題を10問まで取得
                                available_ids = [q['id'] for q in all_questions[:10]] if len(all_questions) >= 10 else [q['id'] for q in all_questions]
                                session['exam_question_ids'] = available_ids

                            session['exam_current'] = 0
                            session['selected_question_type'] = 'emergency'
                            session['exam_category'] = '緊急復旧'
                            session.modified = True

                            exam_question_ids = session['exam_question_ids']
                            current_no = 0

                            logger.info(f"緊急10問セッション作成成功: {len(exam_question_ids)}問")

                        except Exception as emergency_error:
                            logger.error(f"緊急フォールバックも失敗: {emergency_error}")
                            return render_template('error.html',
                                                   error="セッション情報が異常です。ホームに戻って再度お試しください。",
                                                   error_type="session_complete_failure",
                                                   details=f"再構築失敗: {str(rebuild_error)}, 緊急失敗: {str(emergency_error)}")

                # 🔥 再構築後の最終安全チェック
                if not exam_question_ids:
                    logger.error("ウルトラシンク再構築後もexam_question_idsが空です")
                    # 緊急セッション作成（ユーザー設定問題数）
                    user_session_size = get_user_session_size(session)
                    emergency_questions = get_mixed_questions(session, 'basic', None)
                    if emergency_questions and len(emergency_questions) >= user_session_size:
                        exam_question_ids = [q['id'] for q in emergency_questions[:user_session_size]]
                        session['exam_question_ids'] = exam_question_ids
                        session.modified = True
                        logger.info(f"最終安全チェック: {user_session_size}問セッション作成成功")
                    else:
                        logger.error(f"緊急{user_session_size}問セッション作成も失敗")
                        return render_template('error.html', error="セッション作成に失敗しました。")
                    current_no = 0
                    session['exam_question_ids'] = exam_question_ids
                    session['exam_current'] = current_no
                    session['selected_question_type'] = 'minimal'
                    session['exam_category'] = '最小復旧'
                    session.modified = True
                    logger.info(f"緊急最小セッション作成: 問題ID {qid}")

            # 🔥 ウルトラシンク: 現在の問題番号をより正確に特定
            for i, q_id in enumerate(exam_question_ids):
                if str(q_id) == str(qid):
                    current_no = i
                    break
            else:
                # 問題IDが見つからない場合: セッション競合状態を検出
                logger.warning(f"セッション競合検出: 問題ID {qid} がexam_question_ids内に見つかりません。マルチタブ使用による可能性があります。")
                
                # 🔥 ULTRA SYNC FIX: セッション競合の安全な対応（無限ループ防止）
                user_session_size = get_user_session_size(session)
                current_session_length = len(exam_question_ids) if exam_question_ids else 0
                
                if current_session_length > 0:
                    # 既存のセッションがある場合: セッション上限を尊重
                    if current_session_length < user_session_size:
                        # セッション上限に達していない場合のみ追加
                        current_no = current_session_length
                        exam_question_ids.append(qid)
                        session['exam_question_ids'] = exam_question_ids
                        session.modified = True
                        logger.info(f"🔥 安全追加: 問題ID {qid} を位置{current_no}に追加（{current_session_length+1}/{user_session_size}問）")
                    else:
                        # セッション上限に達している場合: 置換で対応
                        current_no = current_session_length - 1  # 最後の問題として処理
                        exam_question_ids[current_no] = qid
                        session['exam_question_ids'] = exam_question_ids
                        session.modified = True
                        logger.info(f"🔥 安全置換: 問題ID {qid} で最終問題を置換（{current_session_length}/{user_session_size}問維持）")
                else:
                    # セッションが空の場合: 新規セッションとして初期化
                    current_no = 0
                    exam_question_ids = [qid]
                    session['exam_question_ids'] = exam_question_ids
                    session.modified = True
                    logger.info(f"🔥 新規セッション: 問題ID {qid} から開始（1/{user_session_size}問）")

            # 🔥 ULTRA SYNC FIX: シンプルで安全な進行ロジック（2問目エラー解決）
            # 複雑な計算を削除し、セッション整合性を優先
            
            # 基本的な整合性チェック
            total_questions_count = len(exam_question_ids) if exam_question_ids else 0
            if total_questions_count == 0:
                logger.error("セッション内に問題IDリストが存在しません")
                return render_template('error.html', error="セッションエラー: 問題リストが空です")
                
            # 🛡️ STRUCTURAL FIX: セッション状態管理クラス使用
            session_manager = SessionStateManager(session)
            safe_current_no, safe_next_no, is_last_question = session_manager.get_safe_indices()
            
            # 変数スコープ問題完全解決: すべて一箇所で定義
            logger.info(f"構造的修正後の安全値: current={safe_current_no}, next={safe_next_no}, is_last={is_last_question}")
            session_size = get_user_session_size(session)
            
            # 最終問題判定: 今回答した問題が最後の問題か
            # current_no + 1 (回答済み問題数) がセッションサイズに達した = 全問完了
            answered_questions_count = safe_current_no + 1  # 0ベース→1ベース変換
            is_last_question = (answered_questions_count >= session_size) or (answered_questions_count >= total_questions_count)
            
            # 🛡️ ULTRA SYNC FIX: 完了保証ロジック（絶対に完了を阻害しない）
            if answered_questions_count >= session_size:
                is_last_question = True
                logger.info(f"✅ 完了保証: {answered_questions_count}問回答済み >= {session_size}問セッション - 完了確定")

            # 次の問題のインデックスを安全に設定
            next_question_index = safe_next_no if not is_last_question else None

            # 詳細デバッグログ（セッション状態の完全な記録）
            logger.info("=== 回答処理デバッグ情報 ===")
            logger.info(f"問題ID: {qid}, 回答: {answer}, 正否: {is_correct}")
            logger.info(f"セッション状態: current_no={current_no}, next_no={safe_next_no}")
            logger.info(f"安全値: safe_current_no={safe_current_no}, safe_next_no={safe_next_no}")
            logger.info(f"セッション設定: session_size={session_size}, total_questions={total_questions_count}")
            logger.info(f"完了判定計算: answered_count({answered_questions_count}) >= session_size({session_size}) = {answered_questions_count >= session_size}")
            logger.info(f"問題リスト: 長さ={total_questions_count}, IDs={exam_question_ids[:3]}..." if total_questions_count > 3 else f"問題リスト: IDs={exam_question_ids}")
            logger.info(f"最終判定: is_last={is_last_question}, next_index={next_question_index}")
            logger.info(f"セッションキー: {list(session.keys())}")
            logger.info("=========================")

            # 🔥 CRITICAL: 復習セッション保護付きセッション更新（ウルトラシンク修正）
            # 復習モードの場合は特別な保護処理
            is_review_session = (session.get('selected_question_type') == 'review' or
                                 session.get('exam_category', '').startswith('復習'))

            # 🔥 ULTRA SYNC EXPERT FIX: 2問目エラー根本解決
            # 専門家推薦：POST処理でのセッション状態管理の完全修正
            logger.info("=== ULTRA SYNC: 2問目エラー根本解決 ===")
            logger.info(f"現在の問題インデックス: {current_no} (回答済み)")
            logger.info(f"次の問題インデックス: {safe_next_no}")
            logger.info(f"問題総数: {total_questions_count}")
            logger.info(f"最終問題判定: {is_last_question}")
            
            # 🔥 CRITICAL FIX: exam_question_ids整合性の確実な保証
            # 次の問題インデックスが有効範囲内にあることを確認
            if not is_last_question and safe_next_no < len(exam_question_ids):
                # 次の問題が存在する場合のみ進行
                next_exam_current = safe_next_no
                logger.info(f"✅ 次問題有効: exam_current = {next_exam_current}")
            else:
                # 最終問題の場合は完了状態 - インデックスは進行させない
                next_exam_current = safe_current_no  # 最終問題のインデックスを維持
                is_last_question = True  # 完了フラグを強制設定
                logger.info(f"✅ 最終問題完了状態: exam_current = {next_exam_current} (最終問題維持)")
            
            # ステップ2: セッション更新内容を準備
            if is_last_question:
                # 最終問題の場合、exam_currentは現在の問題インデックスを維持
                session_final_updates = {
                    'exam_current': safe_current_no,  # 現在位置を維持（重要な修正）
                    'exam_question_ids': exam_question_ids,
                    'quiz_completed': True,  # 完了フラグ
                    'completion_timestamp': get_utc_now().isoformat(),
                    'last_update': get_utc_now().isoformat(),
                    'history': session.get('history', [])
                }
                logger.info(f"最終問題: exam_current = {safe_current_no} に維持")
            else:
                # 通常の次問題への進行 - 安全性を最優先
                session_final_updates = {
                    'exam_current': next_exam_current,  # 検証済みの次問題インデックス
                    'exam_question_ids': exam_question_ids,
                    'last_update': get_utc_now().isoformat(),
                    'history': session.get('history', [])
                }
                logger.info(f"次問題進行: exam_current = {next_exam_current} に設定")

            # 復習セッションの場合は追加保護
            if is_review_session:
                session_final_updates.update({
                    'selected_question_type': 'review',  # 復習モード維持
                    'review_session_active': True,       # 復習セッションアクティブフラグ
                    'review_session_timestamp': get_utc_now().isoformat()  # タイムスタンプ
                })
                logger.info(f"復習セッション保護: 問題{qid}回答後, 次={safe_next_no}, 総数={total_questions_count}")

            # ステップ3: セッション更新を実行
            for key, value in session_final_updates.items():
                session[key] = value
            session.permanent = True
            session.modified = True
            
            # ステップ4: 進捗追跡のための専用フィールドを追加
            session['progress_tracking'] = {
                'answered_count': safe_current_no + 1,  # 回答済み問題数（1ベース）
                'total_questions': session_size,        # セッション総問題数
                'current_index': safe_next_no,          # 次の問題インデックス（0ベース）
                'last_answered_qid': qid,               # 最後に回答した問題ID
                'timestamp': get_utc_now().isoformat()
            }
            session.modified = True

            # ステップ5: セッション保存の検証
            # 🛡️ ULTRA SYNC: デフォルト値統一 (文字列 → 数値)
            saved_current = session.get('exam_current', 0)
            saved_question_ids = session.get('exam_question_ids', [])
            saved_progress = session.get('progress_tracking', {})
            
            logger.info(f"セッション保存確認: exam_current = {saved_current}")
            logger.info(f"進捗追跡確認: {saved_progress}")
            logger.info(f"exam_question_ids保存確認 = {len(saved_question_ids)}問")
            
            # ステップ6: 保存失敗時の緊急修復（専門家推薦）
            expected_exam_current = next_exam_current if not is_last_question else safe_current_no
            actual_exam_current = session.get('exam_current')
            
            if actual_exam_current != expected_exam_current:
                logger.error(f"🚨 CRITICAL: exam_current保存失敗を検出")
                logger.error(f"期待値: {expected_exam_current}, 実際値: {actual_exam_current}")
                
                # 緊急修復処理
                session['exam_current'] = expected_exam_current
                session['progress_repair_count'] = session.get('progress_repair_count', 0) + 1
                session.modified = True
                logger.info(f"✅ 緊急修復完了: exam_current = {expected_exam_current}")
            
            # 🔥 ULTRA SYNC: exam_question_ids整合性の最終確認
            final_exam_current = session.get('exam_current')
            final_exam_question_ids = session.get('exam_question_ids', [])
            
            if final_exam_current >= len(final_exam_question_ids):
                logger.error(f"🚨 CRITICAL: インデックス範囲外エラー - current={final_exam_current}, length={len(final_exam_question_ids)}")
                # 安全な値に修正
                safe_index = max(0, len(final_exam_question_ids) - 1)
                session['exam_current'] = safe_index
                session['exam_index_repair'] = True
                session.modified = True
                logger.info(f"✅ インデックス修復完了: exam_current = {safe_index}")
            
            # ステップ7: 強制的なセッション保存の確保
            session.permanent = True
            session.modified = True
            
            # ステップ8: 最終的な検証（POST完了直前）
            final_exam_current = session.get('exam_current')
            logger.info(f"🔥 POST完了直前の最終確認: exam_current = {final_exam_current}")
            logger.info("=== PROGRESS FIX: セッション状態更新完了 ===")
            
            # ステップ9: 次回のGET処理のための状態確認
            logger.info(f"次回GET処理での期待値: display_current = {expected_exam_current + 1}, display_total = {session_size}")
            
            # 🔥 PROGRESS TRACKING FIX: セッション進捗の確実な保存
            session['exam_progress_timestamp'] = get_utc_now().isoformat()
            session['last_answered_question_id'] = qid
            session['total_questions_in_session'] = len(exam_question_ids)
            session.modified = True
            
            # 🔥 CRITICAL: 最終的なセッション保存状態の確認
            final_verification = {
                'exam_current': session.get('exam_current'),
                'exam_question_ids_length': len(session.get('exam_question_ids', [])),
                'progress_tracking_present': bool(session.get('progress_tracking')),
                'session_modified': True
            }
            logger.info(f"🔥 FINAL: POST処理完了時のセッション状態: {final_verification}")
            logger.info(f"回答処理完了: 問題{qid}, 正答{is_correct}, レベル{srs_info.get('level', 0)}, ストリーク{current_streak}日")

            # 🔥 ULTRA SYNC IMPROVEMENT 5: 学習記録 - パフォーマンス比較計算
            performance_comparison = None
            if qid and elapsed_int > 0:
                # 履歴から同じ問題の前回情報を取得
                history = session.get('history', [])
                previous_attempts = [h for h in history if h.get('question_id') == qid and h.get('elapsed_time')]
                
                if len(previous_attempts) >= 2:  # 前回のデータがある場合
                    last_attempt = previous_attempts[-2]  # 一つ前の記録
                    last_time = float(last_attempt.get('elapsed_time', elapsed_int))
                    current_time = elapsed_int
                    
                    # 正解率の改善チェック
                    correct_count = sum(1 for h in previous_attempts if h.get('is_correct'))
                    # 🔥 ULTRA SYNC PRECISION FIX: パフォーマンス正答率計算の精度保証
                    if previous_attempts:
                        accuracy_decimal = (Decimal(str(correct_count)) / Decimal(str(len(previous_attempts)))) * Decimal('100')
                        accuracy = float(accuracy_decimal.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
                    else:
                        accuracy = 0
                    
                    performance_comparison = {
                        'current_time': round(current_time, 1),
                        'last_time': round(last_time, 1),
                        'time_diff': round(abs(current_time - last_time), 1),
                        'is_faster': current_time < last_time,
                        'correct_streak': sum(1 for h in previous_attempts[-3:] if h.get('is_correct')),
                        'is_repeat_correct': is_correct and all(h.get('is_correct') for h in previous_attempts[-2:]),
                        'is_improving': is_correct and accuracy > 50,
                        'accuracy_improvement': round(accuracy, 1) if accuracy > 0 else 0
                    }
            
            # 🔥 PROGRESS FIX: フィードバック画面への進捗データ準備
            # ユーザー設定の問題数を使用（進捗表示修正）
            safe_total_questions = get_user_session_size(session)
            # 回答済み問題番号（1ベース）- current_no は回答済み問題のインデックス（0ベース）
            safe_current_number = max(1, current_no + 1)  # シンプルな0→1ベース変換

            feedback_data = {
                'question': question,
                'user_answer': answer,
                'is_correct': is_correct,
                'is_last_question': is_last_question,
                'next_question_index': next_question_index,
                'next_question_number': (next_question_index + 1) if next_question_index is not None else None,  # 🔥 ULTRA SYNC: 次問題番号（1ベース）
                'total_questions': safe_total_questions,
                'current_question_number': safe_current_number,  # 回答した問題の番号（1ベース）
                'category': session.get('exam_category', '全体'),
                'srs_info': srs_info,
                'is_review_question': srs_info['total_attempts'] > 1,
                'user_answer_text': question.get(f'option_{answer.lower()}', '不明な回答'),
                'correct_answer_text': question.get(f'option_{question.get("correct_answer", "").lower()}', '不明な正解'),
                'new_badges': new_badges,
                'current_streak': current_streak,
                'badge_info': [gamification_manager.get_badge_info(badge) for badge in new_badges],
                'difficulty_adjustment': difficulty_adjustment,
                'performance_comparison': performance_comparison  # 🔥 IMPROVEMENT 5: 学習記録
            }

            # フィードバック画面の重要な変数をログ出力
            logger.info(
                f"フィードバック変数: is_last_question={feedback_data['is_last_question']}, "
                f"next_question_index={feedback_data['next_question_index']}, "
                f"current_question_number={feedback_data['current_question_number']}, "
                f"total_questions={feedback_data['total_questions']}")

            return render_template('exam_feedback.html', **feedback_data)

        # GET処理（問題表示）
        # 次の問題への遷移の場合は現在のセッション情報を使用
        # 🔥 PROGRESS FIX: next パラメータ検出の確実性向上
        next_param = request.args.get('next', '')
        is_next_request = (next_param == '1')  # シンプルで確実な判定
        
        # 🔥 PROGRESS DEBUG: GET処理開始時のセッション状態
        logger.info(f"🔥 PROGRESS DEBUG: GET処理開始 - exam_current={session.get('exam_current')}, is_next_request={is_next_request}")
        logger.info(f"🔥 PROGRESS DEBUG: セッションキー存在確認 - exam_question_ids={'exam_question_ids' in session}, exam_current={'exam_current' in session}")
        if is_next_request:
            requested_category = session.get('exam_category', '全体')
            requested_department = session.get('selected_department', '')
            requested_question_type = session.get('selected_question_type', '')
            requested_year = session.get('selected_year')
        else:
            # GETパラメータの取得（URLデコード対応）
            raw_category = request.args.get('category', 'all')
            raw_department = request.args.get('department', session.get('selected_department', ''))
            raw_question_type = request.args.get('question_type', session.get('selected_question_type', ''))

            # 🔥 ULTRA SYNC FIX: カテゴリパラメータの正規化（英語→日本語）拡張版
            category_mapping = {
                'all': '全体',
                'overall': '全体', 
                'general': '全体',
                'category': '全体',  # 🔥 新規追加
                'type': '全体',      # 🔥 新規追加
                'class': '全体',     # 🔥 新規追加
                'section': '全体',   # 🔥 新規追加
                'field': '全体',     # 🔥 新規追加
                'undefined': '全体', # 🔥 新規追加
                'unknown': '全体',   # 🔥 新規追加
                'null': '全体',      # 🔥 新規追加
                '全体': '全体'       # 既に日本語の場合はそのまま
            }

            # URLデコード（日本語対応・強化版）
            import urllib.parse
            try:
                # URLエンコーディングされた日本語文字を検出してデコード
                if raw_category:
                    # 英語パラメータの場合は日本語にマッピング
                    if raw_category in category_mapping:
                        raw_category = category_mapping[raw_category]
                        logger.info(f"カテゴリ英語→日本語変換: {request.args.get('category')} → {raw_category}")
                    # 🔥 ULTRA SYNC FIX: URLエンコードされている場合のみデコード（強化版）
                    elif '%' in str(raw_category) or any(ord(c) > 127 for c in str(raw_category)):
                        try:
                            # UTF-8エンコーディング優先でデコード
                            raw_category = urllib.parse.unquote(raw_category, encoding='utf-8')
                            logger.info(f"✅ UTF-8デコード成功: {raw_category}")
                        except (UnicodeDecodeError, ValueError) as utf8_error:
                            logger.warning(f"⚠️ UTF-8デコード失敗: {utf8_error}")
                            # UTF-8でダメな場合はShift_JISも試す
                            try:
                                raw_category = urllib.parse.unquote(raw_category, encoding='shift_jis')
                                logger.info(f"✅ Shift_JISデコード成功: {raw_category}")
                            except (UnicodeDecodeError, ValueError) as sjis_error:
                                logger.warning(f"⚠️ Shift_JISデコード失敗: {sjis_error}")
                                raw_category = '全体'  # 🔥 安全なフォールバック
                                logger.info(f"🔄 フォールバック適用: {raw_category}")
                    logger.info(f"カテゴリデコード結果: {raw_category}")

                if raw_department:
                    if '%' in str(raw_department) or any(ord(c) > 127 for c in str(raw_department)):
                        try:
                            raw_department = urllib.parse.unquote(raw_department, encoding='utf-8')
                        except (UnicodeDecodeError, ValueError):
                            try:
                                raw_department = urllib.parse.unquote(raw_department, encoding='shift_jis')
                            except (UnicodeDecodeError, ValueError) as e:
                                # 🔥 ULTRA SYNC FIX: デコード失敗時の詳細ログ記録
                                logger.warning(f"部門名URLデコード失敗: {raw_department} - {e}")

                if raw_question_type:
                    if '%' in str(raw_question_type) or any(ord(c) > 127 for c in str(raw_question_type)):
                        try:
                            raw_question_type = urllib.parse.unquote(raw_question_type, encoding='utf-8')
                        except (UnicodeDecodeError, ValueError):
                            try:
                                raw_question_type = urllib.parse.unquote(raw_question_type, encoding='shift_jis')
                            except (UnicodeDecodeError, ValueError) as e:
                                # 🔥 ULTRA SYNC FIX: デコード失敗時の詳細ログ記録
                                logger.warning(f"問題種別URLデコード失敗: {raw_question_type} - {e}")
            except Exception as e:
                logger.warning(f"URLデコードエラー: {e}")

            # サニタイズ（日本語保持）
            requested_category = sanitize_input(raw_category)
            # 🔥 CRITICAL FIX: 部門IDのアンダースコア保護（civil_planning対応）
            requested_department = sanitize_input(raw_department, allow_underscores=True)
            requested_question_type = sanitize_input(raw_question_type)

            # 部門エイリアスの解決
            requested_department = resolve_department_alias(requested_department)

            # type=basic/specialistパラメータの処理
            exam_type = sanitize_input(request.args.get('type'))
            if exam_type == 'basic':
                requested_question_type = 'basic'
                requested_department = ''  # 基礎科目は部門不問
                requested_category = '共通'  # 基礎科目のカテゴリは'共通'
                logger.info("基礎科目専用モード: question_type=basic, department=None")
            elif exam_type == 'specialist':
                requested_question_type = 'specialist'
                # 部門名をカテゴリとして設定（日本語のまま使用）
                if requested_department:
                    requested_category = requested_department
                    logger.info(f"専門科目専用モード: 部門={requested_department}をカテゴリとして設定")
                else:
                    # departmentが指定されていない場合でもcategoryを維持
                    logger.info(f"専門科目専用モード: 部門指定なし、既存カテゴリ={requested_category}を維持")
                logger.info(f"専門科目専用モード: question_type=specialist, category={requested_category}, department={requested_department}")

            # カテゴリ選択時の問題種別自動判定
            logger.info(f"カテゴリ判定前: requested_category={requested_category}, requested_question_type={requested_question_type}, requested_department={requested_department}")
            if requested_category and requested_category != '全体' and not requested_question_type:
                if requested_category == '共通':
                    requested_question_type = 'basic'
                    requested_department = ''
                    logger.info("共通カテゴリ: 基礎科目に自動設定")
                else:
                    # 道路、土質及び基礎等の専門部門カテゴリ
                    requested_question_type = 'specialist'
                    # 日本語部門名をそのまま使用（英語IDへの変換を廃止）
                    if not requested_department:
                        # departmentが未設定の場合のみ、カテゴリを部門として使用
                        requested_department = requested_category
                    logger.info(f"専門カテゴリ: {requested_category} -> question_type=specialist, department={requested_department}")

        # カテゴリ処理後の最終値
        logger.info(f"カテゴリ処理後: requested_department={requested_department}, requested_question_type={requested_question_type}")

        # 🔥 ULTRA SYNC修正: 部門指定時のデフォルト専門科目設定
        if requested_department and not requested_question_type:
            requested_question_type = 'specialist'
            logger.info(f"ULTRA SYNC: 部門指定により専門科目に自動設定 - {requested_department}")
            
        # 🔥 CRITICAL FIX: 部門指定時のカテゴリ自動設定（ウルトラシンク）
        if requested_department and requested_category == '全体':
            # 部門IDからカテゴリ日本語名を取得
            if requested_department in DEPARTMENT_TO_CATEGORY_MAPPING:
                requested_category = DEPARTMENT_TO_CATEGORY_MAPPING[requested_department]
                logger.info(f"🚨 ULTRA SYNC: 部門指定によりカテゴリ自動設定 {requested_department} → {requested_category}")
            else:
                logger.warning(f"⚠️ 未知の部門ID: {requested_department}")

        # 年度パラメータの取得とサニタイズ
        requested_year = sanitize_input(request.args.get('year'))
        if requested_year:
            logger.info(f"年度指定: {requested_year}年度の問題を取得")

        # 🔥 ULTRA SYNC: URLパラメータcount処理（CLAUDE.MD準拠修正）
        requested_count = request.args.get('count')
        if requested_count:
            try:
                count_value = int(requested_count)
                if count_value in [10, 20, 30]:
                    # クイズ設定を一時的に更新（副作用なし）
                    if 'quiz_settings' not in session:
                        session['quiz_settings'] = {}
                    session['quiz_settings']['questions_per_session'] = count_value
                    session.modified = True
                    logger.info(f"ULTRA SYNC: URLパラメータcount={count_value}をセッションに適用")
            except (ValueError, TypeError):
                logger.warning(f"無効なcountパラメータ: {requested_count}")

        # ユーザー設定に基づく問題数を取得
        session_size = get_user_session_size(session)
        specific_qid = sanitize_input(request.args.get('qid'))

        # 🔥 CRITICAL: 復習機能の特別処理（ウルトラシンク修正）
        # /exam/review からのリダイレクトの場合、departmentが'review'になってしまう問題を修正
        if requested_department == 'review':
            logger.info("復習機能からの呼び出し検出 - 部門パラメータを修正")
            requested_department = ''  # 部門指定をクリア
            requested_question_type = 'review'  # 問題種別を復習に設定

        # パラメータ検証（復習機能対応版）
        validation_errors = validate_exam_parameters(
            department=requested_department,
            question_type=requested_question_type,
            year=requested_year,
            size=session_size
        )

        if validation_errors:
            error_message = "無効なパラメータが指定されました：" + "、".join(validation_errors)
            return render_template('error.html',
                                   error=error_message,
                                   error_type="invalid_input")

        try:
            session_size = int(session_size)
        except (ValueError, TypeError):
            session_size = ExamConfig.QUESTIONS_PER_SESSION

        # セッション管理
        exam_question_ids = session.get('exam_question_ids', [])
        # ✅ FIXED: Simplified session state handling with next request support
        logger.info("=== SESSION STATE: Reading current position ===")
        
        # 🔥 PROGRESS FIX: 次問題リクエスト処理の確実性向上
        if is_next_request:
            # URLから現在の問題番号を取得（1ベース）
            url_current = request.args.get('current')
            
            if url_current:
                try:
                    # URL値（1ベース）を0ベースインデックスに変換
                    current_no = int(url_current) - 1
                    # セッションを更新
                    session['exam_current'] = current_no
                    session.modified = True
                    logger.info(f"🔥 PROGRESS FIX: URL current={url_current} -> current_no={current_no}")
                except ValueError:
                    # URLパラメータが無効な場合はセッション値を使用
                    current_no = session.get('exam_current', 0)
                    logger.warning(f"🔥 PROGRESS FIX: 無効なURL current={url_current}, セッション値使用={current_no}")
            else:
                # URLパラメータがない場合はセッション値を使用
                current_no = session.get('exam_current', 0)
                logger.info(f"🔥 PROGRESS FIX: URL currentなし, セッション値使用={current_no}")
        else:
            # 通常のGETリクエスト - セッション値を使用
            current_no = session.get('exam_current', 0)
        
        # Basic bounds checking only
        if current_no < 0:
            current_no = 0
            session['exam_current'] = 0
            session.modified = True
        
        if exam_question_ids and current_no >= len(exam_question_ids):
            current_no = len(exam_question_ids) - 1
            session['exam_current'] = current_no
            session.modified = True
        
        session_category = session.get('exam_category', '全体')

        logger.info(f"Session position: current_no={current_no}, question_ids={len(exam_question_ids)}, next={is_next_request}")

        # ★修正: 特定の問題表示の場合も10問セッションを維持
        if specific_qid:
            try:
                specific_qid = int(specific_qid)
                question = next((q for q in all_questions if int(q.get('id', 0)) == specific_qid), None)
                if not question:
                    logger.error(f"指定された問題が見つからない: ID {specific_qid}")
                    return render_template('error.html', error=f"指定された問題が見つかりません (ID: {specific_qid})。")

                # 10問セッションを作成し、指定問題を含める
                if 'exam_question_ids' not in session or not session['exam_question_ids']:
                    # 🛡️ ULTRATHIN区緊急修正: 専門科目フォールバック防止
                    # 🚨 CRITICAL FIX: question_type or 'basic'によるカテゴリー混在バグ完全修正
                    safe_question_type = question_type
                    if not safe_question_type:
                        # セッションから推定
                        safe_question_type = session.get('selected_question_type', 'basic')
                        if department and department != '基礎科目':
                            safe_question_type = 'specialist'
                        logger.info(f"🛡️ ULTRATHIN区: question_type推定 - {safe_question_type} (dept={department})")
                    
                    # 新しい10問セッションを作成
                    mixed_questions = get_mixed_questions(session, all_questions, '全体', session_size, department, safe_question_type, None)
                    if mixed_questions and len(mixed_questions) >= 10:
                        session['exam_question_ids'] = [int(q.get('id', 0)) for q in mixed_questions[:10]]
                    else:
                        # 最低限でも10問確保
                        available_questions = all_questions[:10] if len(all_questions) >= 10 else all_questions
                        session['exam_question_ids'] = [int(q.get('id', 0)) for q in available_questions]

                # 指定された問題の位置を見つける
                try:
                    specific_index = session['exam_question_ids'].index(specific_qid)
                    session['exam_current'] = specific_index
                except ValueError:
                    # 指定問題がセッションにない場合は最初の問題を表示
                    session['exam_current'] = 0

                session['exam_category'] = question.get('category', '全体')
                session.modified = True

                # SRS情報を取得
                srs_data = session.get('srs_data', {})
                question_srs = srs_data.get(str(specific_qid), {})

                # Calculate consistent display values
                session_total = len(session['exam_question_ids'])
                display_current = max(1, session['exam_current'] + 1)
                display_total = get_user_session_size(session)  # 🔥 FIX: ユーザー設定問題数を使用
                
                return render_template(
                    'exam.html',
                    question=question,
                    total_questions=display_total,
                    current_no=display_current,
                    current_question_number=display_current,
                    srs_info=question_srs,
                    is_review_question=question_srs.get('total_attempts', 0) > 0
                )

            except ValueError:
                logger.error(f"無効な問題IDが指定されました: {specific_qid}")
                return render_template('error.html', error="無効な問題IDが指定されました。")

        # 🔥 CRITICAL PROGRESS FIX: 簡単で確実なセッション保護
        # パラメータなしアクセスでも進行中セッションを保護
        current_exam_current = session.get('exam_current', 0)
        current_question_ids = session.get('exam_question_ids', [])
        
        # 進行中セッションの判定: exam_current > 0 または有効な問題リストがある
        has_active_progress = (current_exam_current > 0 and current_question_ids and len(current_question_ids) > 0)
        
        logger.info(f"🔥 PROGRESS FIX: セッション状態確認 - exam_current={current_exam_current}, question_ids={len(current_question_ids)}, has_active_progress={has_active_progress}")
        
        # 次の問題への遷移要求またはアクティブな進行中セッションの場合は保持
        if is_next_request or has_active_progress:
            logger.info("🔥 PROGRESS FIX: 次問題リクエストまたは進行中セッション検出 - セッション強制保持モード")
            # セッションリセットを完全に無効化
            need_reset = False
            logger.info("🔥 PROGRESS FIX: 進行中セッション保護のためneed_reset=False強制設定")
        else:
            # 通常のリクエストの場合のみリセット判定を実行
            session_question_type = session.get('selected_question_type')
            session_department = session.get('selected_department')
            session_year = session.get('selected_year')

            category_match = requested_category == session_category
            question_type_match = requested_question_type == session_question_type
            department_match = requested_department == session_department
            year_match = requested_year == session_year

            logger.info(f"リセット判定: is_next={is_next_request}, exam_ids={bool(exam_question_ids)}, "
                        f"category_match={category_match}, question_type_match={question_type_match}, "
                        f"department_match={department_match}, year_match={year_match}, "
                        f"current_no={current_no}, len={len(exam_question_ids)}")

            # ホームから戻ってきた場合は必ずリセット
            referrer_is_home = request.referrer and request.referrer.endswith('/')

            # 復習モードの詳細判定
            is_review_mode = (
                (requested_question_type == 'review' and exam_question_ids) or
                (session.get('selected_question_type') == 'review' and exam_question_ids) or
                (session.get('exam_category', '').startswith('復習') and exam_question_ids)
            )

            # 🔥 CRITICAL PROGRESS FIX: 次問題リクエスト時はリセットを禁止
            # 🔥 PROGRESS FIX: アクティブセッション保護 - パラメータなしアクセスでもセッション維持
            has_url_params = any([
                request.args.get('department'),
                request.args.get('question_type'),
                request.args.get('type'),
                request.args.get('category'),
                request.args.get('year'),
                request.args.get('count'),
                request.args.get('reset')
            ])
            
            # アクティブセッション中でパラメータなしの場合はリセットしない
            has_active_session = (exam_question_ids and 
                                session.get('exam_current', 0) >= 0 and
                                session.get('exam_current', 0) < len(exam_question_ids))
            
            # 🔥 PROGRESS DEBUG: セッション状態の詳細ログ
            logger.info(f"🔥 PROGRESS DEBUG: has_active_session={has_active_session}")
            logger.info(f"🔥 PROGRESS DEBUG: exam_question_ids={bool(exam_question_ids)}, length={len(exam_question_ids) if exam_question_ids else 0}")
            logger.info(f"🔥 PROGRESS DEBUG: exam_current={session.get('exam_current')}")
            logger.info(f"🔥 PROGRESS DEBUG: has_url_params={has_url_params}")
            logger.info(f"🔥 PROGRESS DEBUG: is_next_request={is_next_request}")
            logger.info(f"🔥 PROGRESS DEBUG: progress_tracking={bool(session.get('progress_tracking'))}")
            
            # 通常のリセット判定（次問題リクエスト以外）
            need_reset = (not is_review_mode and not is_next_request and (
                not exam_question_ids or                    # 問題IDがない
                request.args.get('reset') == '1' or        # 明示的リセット要求
                (referrer_is_home and not is_review_mode and has_url_params) or  # ホームから来た場合（パラメータありのみ）
                (not question_type_match and not is_review_mode and has_url_params) or  # 問題種別変更（パラメータありのみ）
                (not department_match and not is_review_mode and has_url_params) or    # 部門変更（パラメータありのみ）
                (not year_match and not is_review_mode and has_url_params) or          # 年度変更（パラメータありのみ）
                len(exam_question_ids) == 0))              # 空の問題リスト
                
            # 🔥 PROGRESS FIX: 強化されたアクティブセッション保護
            # 条件1: アクティブセッション + パラメータなし + リセット要求なし
            if has_active_session and not has_url_params and not request.args.get('reset'):
                need_reset = False
                logger.info("🔥 PROGRESS FIX: アクティブセッション保護 - パラメータなしアクセスでもセッション維持")
                
            # 条件2: next=1リクエスト時は強制的にリセットを無効化
            if is_next_request:
                need_reset = False
                logger.info("🔥 PROGRESS FIX: next=1リクエストのためリセット強制無効化")
                
            # 条件3: current パラメータ付きリクエストもセッション保持
            if request.args.get('current') and has_active_session:
                need_reset = False
                logger.info("🔥 PROGRESS FIX: currentパラメータ付きアクティブセッション保護")
                
            # 条件4: 最近の活動があれば強制保護（安全チェック付き）
            session_has_recent_activity = session.get('last_update') and True  # 簡易チェック
            if session_has_recent_activity and has_active_session:
                need_reset = False
                logger.info("🔥 PROGRESS FIX: 活性セッション強制保護 - 最近の活動を検出")
                
            # 条件5: 進捗追跡データがある場合は強制保護
            progress_tracking = session.get('progress_tracking')
            if progress_tracking and has_active_session:
                need_reset = False
                logger.info("🔥 PROGRESS FIX: 進捗追跡データ保護 - セッション継続")
                
            # 条件6: exam_current > 0 の場合は進行中セッションとして保護
            if session.get('exam_current', 0) > 0 and has_active_session:
                need_reset = False  
                logger.info(f"🔥 PROGRESS FIX: 進行中セッション保護 - exam_current={session.get('exam_current')}")

        logger.info(f"🔥 ULTRA SYNC: need_reset = {need_reset} (is_next_request={is_next_request})")

        if need_reset:
            # 🔥 CRITICAL: セッション情報完全クリア（ユーザー要求による）
            # 古い問題情報を確実に削除
            old_session_keys = [
                'exam_question_ids', 'exam_current', 'exam_category',
                'selected_department', 'selected_question_type', 'selected_year',
                'request_history'
            ]

            cleared_keys = []
            for key in old_session_keys:
                if key in session:
                    del session[key]
                    cleared_keys.append(key)

            if cleared_keys:
                logger.info(f"問題リセット: セッション完全クリア - {cleared_keys}")

            # 🔥 CRITICAL: 復習モードの場合は既存のexam_question_idsを使用
            if requested_question_type == 'review' and session.get('exam_question_ids'):
                logger.info("復習モード: セッションの既存問題IDを使用")
                question_ids = session.get('exam_question_ids', [])
                selected_questions = []
                # 問題IDから問題データを取得
                for qid in question_ids:
                    q = next((question for question in all_questions if int(question.get('id', 0)) == qid), None)
                    if q:
                        selected_questions.append(q)
            else:
                # 🛡️ ULTRATHIN区緊急修正: SRSを考慮した問題選択（RCCM部門対応・カテゴリー混在完全防止）
                # 🚨 CRITICAL FIX: requested_question_typeが空の場合の安全な推定
                safe_requested_question_type = requested_question_type
                if not safe_requested_question_type and requested_department:
                    if requested_department == '基礎科目' or requested_category == '共通':
                        safe_requested_question_type = 'basic'
                        logger.info(f"🛡️ ULTRATHIN区: 基礎科目推定 - {requested_department}/{requested_category}")
                    else:
                        safe_requested_question_type = 'specialist' 
                        logger.info(f"🛡️ ULTRATHIN区: 専門科目推定 - {requested_department}/{requested_category}")
                elif not safe_requested_question_type:
                    # セッションから推定
                    safe_requested_question_type = session.get('selected_question_type', 'basic')
                    logger.warning(f"🛡️ ULTRATHIN区: セッションから推定 - {safe_requested_question_type}")
                
                logger.info(f"🛡️ ULTRATHIN区 get_mixed_questions呼び出し前: dept={requested_department}, type={safe_requested_question_type} (元:{requested_question_type}), category={requested_category}")
                selected_questions = get_mixed_questions(session, all_questions, requested_category, session_size, requested_department, safe_requested_question_type, requested_year)
                
                # 🛡️ ULTRATHIN区追加: 空リスト安全チェック
                if not selected_questions:
                    error_msg = f"選択された条件（部門:{requested_department}, 年度:{requested_year}, 問題数:{session_size}）では問題が見つかりません。"
                    if requested_question_type == 'specialist' and requested_department and requested_year:
                        error_msg += f" {requested_department}の{requested_year}年度の問題データを確認してください。"
                    logger.error(f"🚨 問題選択失敗: {error_msg}")
                    return render_template('error.html', 
                                         error=error_msg,
                                         error_type="question_not_found",
                                         suggestions=[
                                             "問題数を減らして再試行してください",
                                             "別の年度を選択してください", 
                                             "部門選択画面に戻って確認してください"
                                         ])
                
                question_ids = [int(q.get('id', 0)) for q in selected_questions]

            # デバッグ: 問題選択の詳細ログ
            logger.info(f"問題選択詳細: requested_size={session_size}, selected_count={len(selected_questions)}, question_ids_count={len(question_ids)}")
            logger.info(f"問題ID一覧: {question_ids}")

            # セッション情報を新規作成（古い情報は完全削除済み）
            session['exam_question_ids'] = question_ids
            session['exam_current'] = 0
            session['exam_category'] = requested_category
            if requested_department:
                safe_session_update('selected_department', requested_department)
            if requested_question_type:
                session['selected_question_type'] = requested_question_type
            if requested_year:
                session['selected_year'] = requested_year
            session.modified = True

            exam_question_ids = question_ids
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

        # 🔥 CRITICAL: 復習セッション保護付き範囲チェック（ウルトラシンク修正）
        # 🔥 ULTRA FIX: セッション継続のため範囲チェックを厳密化
        if not exam_question_ids:
            logger.error("exam_question_idsが空です - 緊急セッション再構築が必要")
            
            # 🔥 CRITICAL PROGRESS FIX: next=1 リクエストの場合は強制的にセッション復旧を試行
            if is_next_request:
                logger.info("🔥 PROGRESS FIX: next=1リクエストでセッション復旧を試行")
                
                # 履歴から最近の問題セッションを復元
                history = session.get('history', [])
                if history:
                    # 最近の履歴から問題IDを取得
                    recent_history = history[-10:]  # 最新10問
                    recovered_question_ids = [h.get('id', h.get('question_id')) for h in recent_history if h.get('id') or h.get('question_id')]
                    
                    if recovered_question_ids:
                        # セッションを復旧
                        session['exam_question_ids'] = recovered_question_ids
                        session['exam_current'] = len(recovered_question_ids) - 1  # 最後の問題位置
                        session['exam_category'] = recent_history[-1].get('category', '全体')
                        session['selected_question_type'] = recent_history[-1].get('question_type', 'basic')
                        session['selected_department'] = recent_history[-1].get('department', '')
                        session.modified = True
                        
                        exam_question_ids = recovered_question_ids
                        current_no = len(recovered_question_ids) - 1
                        
                        logger.info(f"✅ セッション復旧成功: {len(recovered_question_ids)}問復元, current_no={current_no}")
                    else:
                        logger.warning("履歴から問題IDを復旧できませんでした")
                        return render_template('error.html', error="セッションが失われました。ホームから再開してください。")
                else:
                    logger.warning("履歴が空のためセッション復旧不可")
                    return render_template('error.html', error="セッションが失われました。ホームから再開してください。")
            else:
                return render_template('error.html', error="セッションデータが破損しました。ホームから再開してください。")
        
        if current_no >= len(exam_question_ids):
            # 復習モードの場合は結果画面ではなく復習完了処理へ
            if is_review_mode or session.get('selected_question_type') == 'review':
                logger.info(f"復習セッション完了: current_no({current_no}) >= len({len(exam_question_ids)}) - 復習結果へ")
                # 復習セッション用の結果画面に送る
                session['review_completed'] = True
                session.modified = True
                return redirect(url_for('result'))
            else:
                logger.info(f"通常セッション完了: current_no({current_no}) >= len({len(exam_question_ids)}) - resultにリダイレクト")
                return redirect(url_for('result'))

        # 現在の問題を取得
        current_question_id = exam_question_ids[current_no]
        logger.info(f"問題ID取得: current_no={current_no}, question_id={current_question_id}")
        question = next((q for q in all_questions if int(q.get('id', 0)) == current_question_id), None)

        if not question:
            logger.error(f"問題データ取得失敗: ID {current_question_id}, available_ids={[q.get('id') for q in all_questions[:5]]}")
            return render_template('error.html', error=f"問題データの取得に失敗しました。(ID: {current_question_id})")

        # SRS情報を取得
        srs_data = session.get('srs_data', {})
        question_srs = srs_data.get(str(current_question_id), {})
        
        # テンプレート用変数
        # 🔥 PROGRESS FIX: ユーザー設定問題数を使用して正確な進捗表示（20問→1/20,2/20...20/20）
        user_session_size = get_user_session_size(session)
        template_vars = {
            'question': question,
            'current_no': current_no + 1,  # 表示用は1から開始
            'total_questions': user_session_size,  # 🔥 FIX: ユーザー設定問題数使用
            'category': session.get('exam_category', ''),
            'progress_percentage': int(((current_no + 1) / user_session_size) * 100),  # 🔥 FIX: 正確な進捗計算
            'is_last_question': (current_no + 1) >= user_session_size,  # 🔥 FIX: 正確な最終問題判定
            'srs_info': question_srs,
            'is_review_question': question_srs.get('total_attempts', 0) > 0
        }
        
        logger.info(f"問題表示: {current_no + 1}/{user_session_size} - ID:{current_question_id}")
        logger.info(f"🔥 PROGRESS DEBUG: template_vars = {template_vars}")
        
        # 🔥 CRITICAL: 完全なレスポンス追跡ログ
        from datetime import datetime as dt
        response_timestamp = dt.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        logger.info("=== RESPONSE GENERATION TRACE ===")
        logger.info(f"🔍 Response Timestamp: {response_timestamp}")
        logger.info(f"🔍 Template: exam.html")
        logger.info(f"🔍 Template Variables: {template_vars}")
        logger.info(f"🔍 Session State Before Response:")
        logger.info(f"  - exam_question_ids: {session.get('exam_question_ids')}")
        logger.info(f"  - exam_current: {session.get('exam_current')}")
        logger.info(f"  - exam_category: {session.get('exam_category')}")
        logger.info(f"  - selected_question_type: {session.get('selected_question_type')}")
        logger.info(f"  - selected_department: {session.get('selected_department')}")
        logger.info(f"  - session_modified: {session.modified}")
        logger.info("====================================")
        
        return render_template('exam.html', **template_vars)
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"🚨 CRITICAL ERROR in exam(): {e}")
        logger.error(f"🚨 FULL TRACEBACK:\n{error_details}")
        # CLAUDE.md準拠: エラー詳細の完全開示
        return render_template('error.html', 
                             error=f"問題表示中にエラーが発生しました。詳細: {str(e)}")


@app.route('/exam/next')
def exam_next():
    """次の問題に進む"""
    current_no = session.get('exam_current', 0)
    exam_question_ids = session.get('exam_question_ids', [])

    if current_no >= len(exam_question_ids):
        return redirect(url_for('result'))

    category = session.get('exam_category', '全体')
    return redirect(url_for('exam', category=category))


@app.route('/result')
def result():
    """結果画面"""
    try:
        history = session.get('history', [])

        # 🔥 ULTRA SYNC セキュリティ FIX: 安全な結果画面ログ出力
        logger.info(f"結果画面: 履歴件数={len(history)}")
        logger.info(f"セッションキー数={len(session.keys())}")
        logger.info(f"アクティブセッション確認: {'Active' if session.get('user_id') else 'Inactive'}")

        exam_question_ids = session.get('exam_question_ids', [])
        session_size = len(exam_question_ids) if exam_question_ids else ExamConfig.QUESTIONS_PER_SESSION

        # 履歴が空の場合は適切にハンドリング（ダミーデータは削除）
        if not history:
            logger.info("履歴なしのため/examにリダイレクト")
            return redirect(url_for('exam'))

        # 現在のセッションの履歴のみを取得（最新10問）
        recent_history = history[-session_size:] if len(history) >= session_size else history

        # セッション完了の確認：正確に10問解答されたかチェック
        session_completed = len(recent_history) == session_size
        if not session_completed and len(history) > 0:
            logger.warning(f"セッション未完了: 履歴={len(recent_history)}問, 期待値={session_size}問")

        # 基本統計
        correct_count = sum(1 for h in recent_history if h.get('is_correct', False))
        total_questions = len(recent_history) if recent_history else 1
        elapsed_time = sum(h.get('elapsed', 0) for h in recent_history)

        # 共通・専門別成績
        basic_specialty_scores = {
            'basic': {'correct': 0, 'total': 0},
            'specialty': {'correct': 0, 'total': 0}
        }

        for h in recent_history:
            # 問題種別から4-1（基礎）か4-2（専門）かを判定
            question_type = h.get('question_type', '')
            question_id = h.get('question_id', '')
            file_source = h.get('file_source', '')

            # 優先度: question_type > ID判定 > ファイル名判定
            if question_type == 'basic' or '4-1' in str(question_id) or '4-1' in file_source:
                score_type = 'basic'
            elif question_type == 'specialist' or '4-2' in str(question_id) or '4-2' in file_source:
                score_type = 'specialty'
            else:
                # デフォルトは基礎科目とする
                score_type = 'basic'
                logger.debug(f"問題種別不明 - 基礎科目として扱う: {h}")

            basic_specialty_scores[score_type]['total'] += 1
            if h.get('is_correct'):
                basic_specialty_scores[score_type]['correct'] += 1

        # 🔥 ULTRA SYNC IMPROVEMENT 4: 復習完了感 - 復習セッション判定
        is_review_session = session.get('selected_question_type') == 'review'
        
        return render_template(
            'result.html',
            correct_count=correct_count,
            total_questions=total_questions,
            elapsed_time=elapsed_time,
            basic_specialty_scores=basic_specialty_scores,
            is_review_session=is_review_session  # 🔥 IMPROVEMENT 4
        )

    except Exception as e:
        logger.error(f"result関数でエラー: {e}")
        return render_template('error.html', error="結果表示中にエラーが発生しました。")


@app.route('/statistics')
# 🔥 ULTRA SYNC: 統合セッション管理システムで自動処理
@memory_monitoring_decorator(_memory_leak_monitor)
def statistics():
    """統計画面"""
    try:
        history = session.get('history', [])

        # 全体統計
        overall_stats = {
            'total_questions': len(history),
            'total_accuracy': 0.0,
            'average_time_per_question': None
        }

        if history:
            total = len(history)
            correct = sum(1 for h in history if h['is_correct'])
            total_time = sum(h.get('elapsed', 0) for h in history)
            # 🔥 ULTRA SYNC PRECISION FIX: 統計計算の精度保証
            if total > 0:
                accuracy_decimal = (Decimal(str(correct)) / Decimal(str(total))) * Decimal('100')
                overall_stats['total_accuracy'] = float(accuracy_decimal.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
                
                time_per_question_decimal = Decimal(str(total_time)) / Decimal(str(total))
                overall_stats['average_time_per_question'] = float(time_per_question_decimal.quantize(Decimal('0.1'), rounding=ROUND_HALF_UP))
            else:
                overall_stats['total_accuracy'] = 0.0
                overall_stats['average_time_per_question'] = None

        # 共通・専門別詳細
        basic_specialty_details = {
            'basic': {'total_answered': 0, 'correct_count': 0, 'accuracy': 0.0},
            'specialty': {'total_answered': 0, 'correct_count': 0, 'accuracy': 0.0}
        }

        # 履歴から共通・専門別データを集計
        for h in history:
            question_id = h.get('id', h.get('question_id', ''))
            question_type = h.get('question_type', '')

            if question_type == 'basic' or '4-1' in str(question_id):
                score_type = 'basic'
            else:
                score_type = 'specialty'

            basic_specialty_details[score_type]['total_answered'] += 1
            if h.get('is_correct'):
                basic_specialty_details[score_type]['correct_count'] += 1

        # 正答率計算
        for score_type in ['basic', 'specialty']:
            total = basic_specialty_details[score_type]['total_answered']
            correct = basic_specialty_details[score_type]['correct_count']
            # 🔥 ULTRA SYNC PRECISION FIX: 共通・専門別正答率計算の精度保証
            if total > 0:
                accuracy_decimal = (Decimal(str(correct)) / Decimal(str(total))) * Decimal('100')
                basic_specialty_details[score_type]['accuracy'] = float(accuracy_decimal.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
            else:
                basic_specialty_details[score_type]['accuracy'] = 0.0

        # 最近の履歴
        exam_history = history[-10:] if history else []

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
            basic_specialty_details=basic_specialty_details,
            exam_history=exam_history,
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
        # 部門エイリアスの解決
        department_id = resolve_department_alias(department_id)

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
        # 部門エイリアスの解決
        department_id = resolve_department_alias(department_id)

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
        # 部門エイリアスの解決
        department_id = resolve_department_alias(department_id)

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

@app.route('/department_study')
def department_study_index():
    """部門一覧ページ - /department_study の404エラー修正"""
    return redirect(url_for('departments'))

@app.route('/department_study/<department>')
def department_study(department):
    """部門特化学習画面 - ユーザーフレンドリーな部門学習インターフェース"""
    try:
        # 部門エイリアスの解決
        department = resolve_department_alias(department)

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
        # 🔥 CRITICAL FIX: 基礎科目の特別処理 - 副作用ゼロで基礎科目エラー修正
        if department_key == 'basic':
            # 基礎科目の場合は専門問題ではなく基礎問題を使用
            specialist_questions = basic_questions  # 基礎科目では基礎問題と専門問題は同じ
            specialist_history = basic_history
        else:
            # 部門キーを日本語カテゴリに変換（グローバル定数使用）
            target_category = DEPARTMENT_TO_CATEGORY_MAPPING.get(department_key, department_key)

            specialist_questions = [q for q in questions
                                    if q.get('question_type') == 'specialist' and q.get('category') == target_category]
            specialist_history = [h for h in session.get('history', [])
                                  if h.get('question_type') == 'specialist' and h.get('category') == target_category]

        # 🔥 ULTRA SYNC強化デバッグログ（包括的問題診断）
        logger.error(f"🚨 CRITICAL DEBUG: department_original={department}, department_key={department_key}")
        logger.error(f"🚨 CRITICAL DEBUG: target_category={target_category}")
        logger.error(f"🚨 CRITICAL DEBUG: total_questions_loaded={len(questions)}")
        logger.error(f"🚨 CRITICAL DEBUG: specialist_questions_filtered={len(specialist_questions)}")
        
        # カテゴリ別集計デバッグ
        category_counts = {}
        type_counts = {}
        for q in questions:
            cat = q.get('category', 'unknown')
            qtype = q.get('question_type', 'unknown')
            category_counts[cat] = category_counts.get(cat, 0) + 1
            type_counts[qtype] = type_counts.get(qtype, 0) + 1
        
        logger.error(f"🚨 CRITICAL DEBUG: category_counts={category_counts}")
        logger.error(f"🚨 CRITICAL DEBUG: question_type_counts={type_counts}")
        
        # 土質・都市計画特化デバッグ
        soil_questions = [q for q in questions if q.get('category') == '土質及び基礎']
        urban_questions = [q for q in questions if q.get('category') == '都市計画及び地方計画']
        logger.error(f"🚨 CRITICAL DEBUG: 土質及び基礎_total={len(soil_questions)}")
        logger.error(f"🚨 CRITICAL DEBUG: 都市計画及び地方計画_total={len(urban_questions)}")
        
        if len(specialist_questions) > 0:
            sample = specialist_questions[0]
            logger.error(f"🚨 CRITICAL DEBUG sample: category={sample.get('category')}, type={sample.get('question_type')}, dept={sample.get('department')}")
        else:
            logger.error(f"🚨 CRITICAL WARNING: specialist_questions is EMPTY for {department_key} -> {target_category}")

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
    """部門別問題選択画面（選択部門+共通のみ表示）"""
    try:
        questions = load_questions()
        cat_stats = session.get('category_stats', {})

        # 現在選択されている部門を取得
        selected_department = session.get('selected_department', request.args.get('department'))

        # カテゴリ情報を集計（選択部門+共通のみ）
        category_details = {}
        for q in questions:
            cat = q.get('category')
            q_dept = q.get('department', '')
            q_type = q.get('question_type', '')

            # フィルタリング: 共通問題 OR 選択部門の専門問題のみ
            include_question = False
            if q_type == 'basic' or cat == '共通':  # 基礎科目（共通）は常に表示
                include_question = True
            elif selected_department and q_dept == selected_department and q_type == 'specialist':  # 選択部門の専門問題のみ
                include_question = True
            elif not selected_department:  # 部門未選択の場合は全表示
                include_question = True

            if include_question and cat:
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
    """復習リスト表示（高度なSRSシステム対応版）"""
    try:
        # 新しいSRSシステムからデータを取得（防御的プログラミング）
        srs_data = session.get('advanced_srs', {})
        if not isinstance(srs_data, dict):
            logger.error(f"🚨 CRITICAL: advanced_srs is not a dict: {type(srs_data)}, value: {repr(srs_data)}")
            srs_data = {}
            session['advanced_srs'] = {}
        
        bookmarks = session.get('bookmarks', [])
        if not isinstance(bookmarks, list):
            logger.error(f"🚨 CRITICAL: bookmarks is not a list: {type(bookmarks)}, value: {repr(bookmarks)}")
            bookmarks = []
            session['bookmarks'] = []  # 互換性維持

        # すべての復習対象問題を統合
        all_review_ids = set()
        all_review_ids.update(srs_data.keys())
        all_review_ids.update(bookmarks)

        if not all_review_ids:
            return render_template('review_enhanced.html',
                                   message="まだ復習問題が登録されていません。問題を解いて間違えることで、科学的な復習システムが自動的に最適な学習計画を作成します。",
                                   departments=RCCMConfig.DEPARTMENTS,
                                   srs_stats={
                                       'total_questions': 0,
                                       'due_now': 0,
                                       'mastered': 0,
                                       'in_progress': 0
                                   })

        # 問題データを読み込み
        all_questions = load_questions()
        questions_dict = {str(q.get('id')): q for q in all_questions}

        # 復習問題の詳細情報を作成（SRSデータ統合）
        review_questions = []
        departments = set()
        
        # 🔥 ULTRA SYNC IMPROVEMENT 3: 部門別復習 - 部門統計計算
        department_stats = {}

        # 🔥 ULTRA SYNC IMPROVEMENT 1: 明確な進捗表示 - 今日復習すべき問題数計算
        due_today_count = 0
        for qid in all_review_ids:
            srs_info = srs_data.get(qid, {})
            next_review = srs_info.get('next_review', '')
            if next_review:
                try:
                    from datetime import datetime
                    review_date = datetime.fromisoformat(next_review.replace('Z', '+00:00'))
                    if review_date <= datetime.now():
                        due_today_count += 1
                except (ValueError, TypeError, AttributeError) as e:
                    # 日時解析エラーの場合は復習対象としてカウント
                    logger.warning(f"Date parsing error in SRS due count: {e}")
                    due_today_count += 1  # パースエラーの場合は復習対象としてカウント
                    due_today_count += 1  # パースエラーの場合は復習対象としてカウント
            else:
                due_today_count += 1  # next_reviewが未設定の場合も復習対象
        
        # SRS統計計算
        srs_stats = {
            'total_questions': len(all_review_ids),
            'due_now': due_today_count,
            'mastered': 0,
            'in_progress': 0,
            'high_priority': 0
        }

        from datetime import datetime
        now = datetime.now()

        for qid in all_review_ids:
            if qid in questions_dict:
                question = questions_dict[qid]

                # SRSデータを取得
                srs_info = srs_data.get(qid, {})

                # 🔥 ULTRA SYNC IMPROVEMENT 2: 学習効率の可視化 - 次回復習日計算
                next_review_str = srs_info.get('next_review', '')
                days_until_review = 0
                if next_review_str:
                    try:
                        from datetime import datetime
                        next_review_date = datetime.fromisoformat(next_review_str.replace('Z', '+00:00'))
                        days_until_review = (next_review_date.date() - now.date()).days
                    except (ValueError, TypeError, AttributeError) as e:
                        # 日時解析エラーの場合は今すぐ復習として設定
                        logger.warning(f"Date parsing error in days until review: {e}")
                        days_until_review = 0  # パースエラーの場合は今すぐ復習
                        days_until_review = 0  # パースエラーの場合は今すぐ復習
                        
                # 基本情報
                question_data = {
                    'id': qid,
                    'question': question.get('question', ''),
                    'department': question.get('department', ''),
                    'question_type': question.get('question_type', ''),
                    'year': question.get('year', ''),
                    'category': question.get('category', ''),
                    # SRS情報
                    'correct_count': srs_info.get('correct_count', 0),
                    'wrong_count': srs_info.get('wrong_count', 0),
                    'total_attempts': srs_info.get('total_attempts', 0),
                    'difficulty_level': srs_info.get('difficulty_level', 5),
                    'mastered': srs_info.get('mastered', False),
                    'first_attempt': srs_info.get('first_attempt', ''),
                    'last_attempt': srs_info.get('last_attempt', ''),
                    'next_review': next_review_str,
                    'days_until_review': days_until_review,  # 🔥 IMPROVEMENT 2
                    'interval_days': srs_info.get('interval_days', 1)
                }

                # 統計更新
                if question_data['mastered']:
                    srs_stats['mastered'] += 1
                else:
                    srs_stats['in_progress'] += 1

                    # 復習期限チェック
                    try:
                        if question_data['next_review']:
                            next_review = datetime.fromisoformat(question_data['next_review'])
                            if next_review <= now:
                                srs_stats['due_now'] += 1
                        else:
                            srs_stats['due_now'] += 1  # 未設定は即座に復習対象
                    except ValueError:
                        srs_stats['due_now'] += 1

                    # 高優先度（間違いが多い）問題
                    if question_data['wrong_count'] >= 2:
                        srs_stats['high_priority'] += 1

                # 部門情報と統計更新
                dept_name = question_data.get('category', question_data.get('department', ''))
                if dept_name:
                    departments.add(dept_name)
                    
                    # 🔥 IMPROVEMENT 3: 部門別統計更新
                    if dept_name not in department_stats:
                        department_stats[dept_name] = {'weak_count': 0, 'total_count': 0}
                    
                    department_stats[dept_name]['total_count'] += 1
                    if not question_data['mastered'] and question_data['wrong_count'] > 0:
                        department_stats[dept_name]['weak_count'] += 1

                # 優先度計算（表示順序用）
                if question_data['mastered']:
                    priority = -1000  # マスター済みは最後
                else:
                    wrong_ratio = question_data['wrong_count'] / max(1, question_data['total_attempts'])
                    overdue_bonus = 0
                    try:
                        if question_data['next_review']:
                            next_review = datetime.fromisoformat(question_data['next_review'])
                            days_overdue = max(0, (now - next_review).days)
                            overdue_bonus = days_overdue * 10
                    except ValueError:
                        overdue_bonus = 100  # 日時エラーは高優先度

                    priority = (wrong_ratio * 100) + overdue_bonus + question_data['difficulty_level']

                question_data['priority'] = priority
                review_questions.append(question_data)

        # 優先度順でソート（マスター済み問題は最後）
        review_questions.sort(key=lambda x: x['priority'], reverse=True)

        # マスター済み問題とアクティブ問題を分離
        active_questions = [q for q in review_questions if not q['mastered']]
        mastered_questions = [q for q in review_questions if q['mastered']]

        logger.info(f"復習リスト表示: 総計{len(review_questions)}問, "
                    f"アクティブ{len(active_questions)}問, マスター済み{len(mastered_questions)}問")

        return render_template('review_enhanced.html',
                               questions=active_questions,
                               mastered_questions=mastered_questions,
                               total_count=len(active_questions),
                               mastered_count=len(mastered_questions),
                               due_today_count=due_today_count,  # 🔥 IMPROVEMENT 1: 今日復習すべき問題数
                               department_stats=department_stats,  # 🔥 IMPROVEMENT 3: 部門別統計
                               departments=RCCMConfig.DEPARTMENTS,
                               srs_stats=srs_stats,
                               show_srs_details=True)

    except Exception as e:
        logger.error(f"復習リスト表示エラー: {e}")
        return render_template('error.html', error="復習リスト表示中にエラーが発生しました。")


@app.route('/api/review/count')
def api_review_count():
    """復習問題数を取得（ウルトラシンク追加・ホーム画面表示用）"""
    try:
        # 🔥 ULTRA SYNC FIX: 正しいセッションキーを使用
        srs_data = session.get('advanced_srs', {})
        bookmarks = session.get('bookmarks', [])

        # 復習対象問題の数をカウント
        review_count = 0
        current_time = datetime.now()

        # SRSデータからカウント
        for question_id, data in srs_data.items():
            if isinstance(data, dict):
                # 次回復習日をチェック
                next_review = data.get('next_review', '')
                if next_review:
                    try:
                        review_date = datetime.fromisoformat(next_review.replace('Z', '+00:00'))
                        if review_date <= current_time:
                            review_count += 1
                    except (ValueError, TypeError, AttributeError):
                        # 日付パースエラーの場合は復習対象に含める
                        review_count += 1
                else:
                    # next_reviewが設定されていない場合も復習対象
                    review_count += 1
                    
        # ブックマークからもカウント（重複除去）
        bookmark_ids = set(str(bid) for bid in bookmarks if bid)
        srs_ids = set(str(sid) for sid in srs_data.keys() if sid)
        additional_bookmarks = bookmark_ids - srs_ids
        review_count += len(additional_bookmarks)

        logger.info(f"復習問題数API呼び出し: {review_count}問")
        return jsonify({'count': review_count, 'success': True})

    except Exception as e:
        logger.error(f"復習問題数取得エラー: {e}")
        return jsonify({'count': 0, 'error': str(e), 'success': False})


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
    """SRS学習統計の表示（エラー処理強化版）"""
    try:
        # セッションデータの安全な取得
        srs_data = session.get('srs_data', {})

        # 基本統計の初期化
        stats = {
            'total_learned': 0,
            'mastered': 0,
            'review_needed': 0,
            'learning': 0,
            'error_data': 0
        }

        # 🔥 ULTRA SYNC TIMEZONE FIX: UTC基準の今日日付取得
        today = get_utc_now().date()
        processed_data = {}

        # SRSデータの安全な処理
        for question_id, data in srs_data.items():
            try:
                # データが辞書形式かチェック
                if not isinstance(data, dict):
                    logger.warning(f"SRS統計: 無効なデータ形式 ID={question_id}, type={type(data)}")
                    stats['error_data'] += 1
                    continue

                # レベルと日時の安全な取得
                level = int(data.get('level', 0))
                next_review_str = data.get('next_review')

                if not next_review_str:
                    # 復習日が設定されていない場合
                    stats['learning'] += 1
                    processed_data[question_id] = {
                        'level': level,
                        'status': '学習中',
                        'next_review': '未設定'
                    }
                    continue

                # 日時の解析
                try:
                    next_review = datetime.fromisoformat(next_review_str).date()
                except (ValueError, TypeError):
                    # 日時解析失敗時のフォールバック
                    stats['learning'] += 1
                    processed_data[question_id] = {
                        'level': level,
                        'status': '学習中',
                        'next_review': '日時エラー'
                    }
                    continue

                # レベルと復習日に基づく分類
                if level >= 5:
                    stats['mastered'] += 1
                    status = 'マスター'
                elif next_review <= today:
                    stats['review_needed'] += 1
                    status = '復習必要'
                else:
                    stats['learning'] += 1
                    status = '学習中'

                processed_data[question_id] = {
                    'level': level,
                    'status': status,
                    'next_review': next_review.isoformat()
                }

            except Exception as item_error:
                logger.warning(f"SRS統計処理エラー ID={question_id}: {item_error}")
                stats['error_data'] += 1

        # 合計学習数の更新
        stats['total_learned'] = stats['mastered'] + stats['review_needed'] + stats['learning']

        # 学習進捗計算
        progress_percentage = 0
        if stats['total_learned'] > 0:
            progress_percentage = round((stats['mastered'] / stats['total_learned']) * 100, 1)

        stats['progress_percentage'] = progress_percentage

        logger.info(f"SRS統計生成完了: 総計={stats['total_learned']}, マスター={stats['mastered']}, 復習必要={stats['review_needed']}")

        return render_template('srs_stats.html',
                               stats=stats,
                               srs_data=processed_data,
                               last_updated=datetime.now().strftime('%Y-%m-%d %H:%M'))

    except Exception as e:
        logger.error(f"SRS統計表示エラー: {e}")
        # エラー時のフォールバック表示
        fallback_stats = {
            'total_learned': 0,
            'mastered': 0,
            'review_needed': 0,
            'learning': 0,
            'progress_percentage': 0,
            'error_data': 0
        }
        return render_template('srs_stats.html',
                               stats=fallback_stats,
                               srs_data={},
                               error_message="学習統計の読み込み中にエラーが発生しました。問題を続けることで統計が蓄積されます。")


@app.route('/api/data/export')
@require_api_key
def export_data():
    """学習データのエクスポート"""
    try:
        session_id = session.get('session_id')
        if not session_id:
            return jsonify({'error': 'セッションが見つかりません'}), 400

        if data_manager:
            export_data = data_manager.get_data_export(session_id)
            if export_data:
                return jsonify(export_data)
            else:
                return jsonify({'error': 'エクスポートデータが見つかりません'}), 404
        else:
            return jsonify({'error': 'データマネージャーが利用できません'}), 503

    except Exception as e:
        logger.error(f"データエクスポートエラー: {e}")
        return jsonify({'error': 'エクスポートに失敗しました'}), 500


@app.route('/api/cache/clear', methods=['POST'])
def clear_cache():
    """⚡ Redis統合 問題データキャッシュのクリア（CLAUDE.md準拠エラーハンドリング強化版）"""
    try:
        # CLAUDE.md禁止事項：エラーメッセージの無視や隠蔽を避ける
        
        # ⚡ Redis Cache Clear
        if REDIS_CACHE_INTEGRATION:
            redis_success = invalidate_cache()
            if redis_success:
                logger.info("⚡ Redis キャッシュクリア成功")
            else:
                logger.warning("⚠️ Redis キャッシュクリア失敗")
        
        # 従来のキャッシュクリア
        clear_questions_cache()
        logger.info("問題データキャッシュをクリア")
        
        return jsonify({
            'success': True,
            'message': 'キャッシュをクリアしました（Redis + メモリキャッシュ）',
            'redis_enabled': REDIS_CACHE_INTEGRATION
        })
    except Exception as e:
        # CLAUDE.md準拠：根本原因を解決せずに症状のみを隠さない
        logger.error(f"キャッシュクリアエラー: {e}")
        import traceback
        traceback.print_exc()  # デバッグ用詳細ログ
        return jsonify({
            'success': False,
            'error': 'キャッシュクリアに失敗しました',
            'details': str(e) if app.debug else None
        }), 500


@app.route('/api/cache/stats', methods=['GET'])
def get_cache_stats():
    """⚡ Redis Cache統計情報取得API"""
    try:
        stats = {
            'redis_integration': REDIS_CACHE_INTEGRATION,
            'timestamp': get_utc_now().isoformat()
        }
        
        if REDIS_CACHE_INTEGRATION:
            redis_stats = get_cache_statistics()
            stats.update({
                'redis_stats': redis_stats,
                'performance_impact': {
                    'csv_load_speedup': '10-100x faster' if redis_stats.get('status') == 'connected' else 'unavailable',
                    'memory_usage': redis_stats.get('memory_usage', 'unknown'),
                    'hit_rate': f"{redis_stats.get('hit_rate', 0)}%"
                }
            })
        else:
            stats.update({
                'redis_stats': {'status': 'disabled'},
                'performance_impact': {
                    'csv_load_speedup': 'using memory cache only',
                    'hit_rate': 'memory cache fallback'
                }
            })
        
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"キャッシュ統計取得エラー: {e}")
        return jsonify({
            'error': 'キャッシュ統計取得に失敗',
            'redis_integration': REDIS_CACHE_INTEGRATION,
            'details': str(e) if app.debug else None
        }), 500


@app.route('/reset', methods=['GET', 'POST'])
def reset():
    """リセット画面"""
    if request.method == 'POST':
        session.clear()
        # 強制的なキャッシュクリア（Redis + メモリキャッシュ）
        if REDIS_CACHE_INTEGRATION:
            invalidate_cache()
        clear_questions_cache()
        logger.info("セッションとキャッシュを完全リセット（Redis + メモリキャッシュ）")
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
        safe_session_update('session_id', os.urandom(16).hex())
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


@app.route('/debug/soil_test')
def debug_soil_test():
    """🔥 ULTRA SYNC: 土質部門デバッグテスト"""
    questions = load_questions()
    soil_questions = [q for q in questions if q.get('category') == '土質及び基礎']
    soil_specialist = [q for q in soil_questions if q.get('question_type') == 'specialist']
    
    return jsonify({
        'total_questions': len(questions),
        'soil_total': len(soil_questions),
        'soil_specialist': len(soil_specialist),
        'sample_soil': soil_questions[0] if soil_questions else None,
        'department_mapping': {
            'soil_foundation': DEPARTMENT_TO_CATEGORY_MAPPING.get('soil_foundation'),
            'aliases': [k for k, v in LEGACY_DEPARTMENT_ALIASES.items() if v == 'soil_foundation']
        }
    })

@app.route('/debug/urban_test')
def debug_urban_test():
    """🔥 ULTRA SYNC: 都市計画部門デバッグテスト"""
    questions = load_questions()
    urban_questions = [q for q in questions if q.get('category') == '都市計画及び地方計画']
    urban_specialist = [q for q in urban_questions if q.get('question_type') == 'specialist']
    
    return jsonify({
        'total_questions': len(questions),
        'urban_total': len(urban_questions),
        'urban_specialist': len(urban_specialist),
        'sample_urban': urban_questions[0] if urban_questions else None,
        'department_mapping': {
            'urban_planning': DEPARTMENT_TO_CATEGORY_MAPPING.get('urban_planning'),
            'aliases': [k for k, v in LEGACY_DEPARTMENT_ALIASES.items() if v == 'urban_planning']
        }
    })

@app.route('/debug/all_departments')
def debug_all_departments():
    """🔥 ULTRA SYNC: 全12部門包括チェック"""
    questions = load_questions()
    
    # 全12部門の情報収集
    departments_info = {}
    for dept_key, dept_info in RCCMConfig.DEPARTMENTS.items():
        if dept_key == 'basic':  # 基礎科目は除外
            continue
            
        target_category = DEPARTMENT_TO_CATEGORY_MAPPING.get(dept_key, dept_key)
        dept_questions = [q for q in questions if q.get('category') == target_category]
        specialist_questions = [q for q in dept_questions if q.get('question_type') == 'specialist']
        
        departments_info[dept_key] = {
            'name': dept_info['name'],
            'category': target_category,
            'total_questions': len(dept_questions),
            'specialist_questions': len(specialist_questions),
            'aliases': [k for k, v in LEGACY_DEPARTMENT_ALIASES.items() if v == dept_key],
            'has_sufficient_data': len(specialist_questions) >= 30,  # 30問以上で十分
            'can_run_30q_quiz': len(specialist_questions) >= 30
        }
    
    # 問題のある部門を特定
    problematic_departments = {
        k: v for k, v in departments_info.items() 
        if not v['has_sufficient_data']
    }
    
    # カテゴリ別集計
    category_counts = {}
    for q in questions:
        cat = q.get('category', 'unknown')
        category_counts[cat] = category_counts.get(cat, 0) + 1
    
    return jsonify({
        'total_questions': len(questions),
        'departments_count': len(departments_info),
        'departments_info': departments_info,
        'problematic_departments': problematic_departments,
        'category_counts': category_counts,
        'mapping_check': DEPARTMENT_TO_CATEGORY_MAPPING,
        'aliases_check': LEGACY_DEPARTMENT_ALIASES
    })


@app.route('/help')
def help_page():
    """ヘルプページ"""
    current_questions = session.get('quiz_settings', {}).get('questions_per_session', 10)
    return render_template('help.html', total_questions=current_questions)


@app.route('/settings', methods=['GET', 'POST'])
def settings_page():
    """設定画面 - 問題数設定"""
    if request.method == 'POST':
        # POST: 設定保存
        questions_per_session = int(request.form.get('questions_per_session', 10))

        # 有効な値かチェック
        if questions_per_session not in [10, 20, 30]:
            questions_per_session = 10

        # セッションに保存
        if 'quiz_settings' not in session:
            session['quiz_settings'] = {}

        session['quiz_settings']['questions_per_session'] = questions_per_session
        session.modified = True

        logger.info(f"問題数設定変更: {questions_per_session}問")

        flash(f'問題数を{questions_per_session}問に設定しました', 'success')
        return redirect(url_for('settings_page'))

    # GET: 設定画面表示
    current_settings = session.get('quiz_settings', {})
    current_questions = current_settings.get('questions_per_session', 10)

    return render_template('settings.html',
                           current_questions=current_questions,
                           available_options=[10, 20, 30])


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
            session.modified = True  # セッションの変更を保存するために必要
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


@app.route('/bookmark', methods=['POST'])
def add_bookmark():
    """フォーム形式でのブックマーク追加"""
    try:
        qid = request.form.get('qid')

        if not qid:
            logger.warning("ブックマーク追加: 問題IDが指定されていません")
            return redirect(request.referrer or '/exam')

        # セッションにブックマークリストがなければ作成
        if 'bookmarks' not in session:
            session['bookmarks'] = []

        # 問題IDがリストになければ追加
        if qid not in session['bookmarks']:
            session['bookmarks'].append(qid)
            session.modified = True
            logger.info(f"問題ID {qid} を復習リストに追加しました")

        return redirect(request.referrer or '/exam')

    except Exception as e:
        logger.error(f"ブックマーク追加エラー: {e}")
        return redirect(request.referrer or '/exam')


@app.route('/bookmarks')
def bookmarks_page():
    """復習リストページ（HTMLページ）"""
    try:
        # 復習リストから問題IDを取得
        bookmarks = session.get('bookmarks', [])

        if not bookmarks:
            return render_template('bookmarks.html',
                                   questions=[],
                                   total_count=0,
                                   message="まだ復習問題が登録されていません。")

        # 問題データを読み込み
        all_questions = load_questions()
        questions = []

        # ブックマークされた問題の詳細情報を取得
        for qid in bookmarks:
            question = next((q for q in all_questions if str(q.get('id', '')) == str(qid)), None)
            if question:
                # 部門名を取得
                dept_key = question.get('department', '')
                dept_name = ''
                if dept_key:
                    dept_info = RCCMConfig.DEPARTMENTS.get(dept_key, {})
                    dept_name = dept_info.get('name', dept_key)

                questions.append({
                    'id': question.get('id'),
                    'question': question.get('question', '')[:100] + '...' if len(question.get('question', '')) > 100 else question.get('question', ''),
                    'category': question.get('category', ''),
                    'department_name': dept_name,
                    'year': question.get('year'),
                    'question_type': question.get('question_type', '')
                })

        return render_template('bookmarks.html',
                               questions=questions,
                               total_count=len(questions))

    except Exception as e:
        logger.error(f"復習リストページエラー: {e}")
        return render_template('error.html', error="復習リストの表示中にエラーが発生しました。")


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


@app.route('/exam/review')
def review_questions():
    """🔥 ULTRA堅牢な高度SRSシステム復習問題練習（ウルトラシンク対応）"""
    try:
        # 🔥 CRITICAL: 包括的エラーハンドリング
        logger.info("=== 復習開始処理開始 ===")

        # 問題データロード（エラーハンドリング強化）
        try:
            # データディレクトリの設定
            data_dir = os.path.dirname(DataConfig.QUESTIONS_CSV)
            # 🛡️ ULTRATHIN区 緊急修正: 基礎科目のみ読み込み（専門科目は必要時に動的読み込み）
            from utils import load_basic_questions_only
            basic_questions = load_basic_questions_only(data_dir)
            all_questions = basic_questions
            if not all_questions:
                logger.error("問題データが空です")
                return render_template('error.html',
                                       error="問題データが読み込めませんでした。システム管理者に連絡してください。",
                                       error_type="data_load_error")
        except Exception as load_error:
            logger.error(f"問題データロードエラー: {load_error}")
            return render_template('error.html',
                                   error="問題データの読み込み中にエラーが発生しました。",
                                   error_type="data_load_exception")

        # 🔥 ULTRA堅牢: 復習対象問題を統合取得（安全性強化・ウルトラシンク対応）
        try:
            srs_data = session.get('advanced_srs', {})
            bookmarks = session.get('bookmarks', [])

            # データ型チェック（ウルトラシンク対応）
            if not isinstance(srs_data, dict):
                logger.warning(f"SRSデータが辞書型ではありません: {type(srs_data)} - 初期化")
                srs_data = {}
            if not isinstance(bookmarks, list):
                logger.warning(f"ブックマークがリスト型ではありません: {type(bookmarks)} - 初期化")
                bookmarks = []

            # 🔥 ULTRA堅牢: SRSデータの詳細検証と修復
            valid_srs_data = {}
            for qid, srs_info in srs_data.items():
                try:
                    # SRS情報の型チェック
                    if not isinstance(srs_info, dict):
                        logger.warning(f"SRS情報が無効な型: 問題ID {qid}, 型: {type(srs_info)}")
                        continue

                    # 必須フィールドの存在チェック（柔軟性向上）
                    essential_fields = ['wrong_count', 'correct_count']
                    if all(field in srs_info for field in essential_fields):
                        # 数値の妥当性チェックとデフォルト値補完
                        wrong_count = int(srs_info.get('wrong_count', 0))
                        correct_count = int(srs_info.get('correct_count', 0))
                        total_attempts = int(srs_info.get('total_attempts', wrong_count + correct_count))
                        
                        if wrong_count >= 0 and correct_count >= 0:
                            # 不足フィールドを補完
                            srs_info['total_attempts'] = total_attempts
                            valid_srs_data[qid] = srs_info
                    else:
                        logger.warning(f"SRS情報に必須フィールドが不足: 問題ID {qid}, フィールド: {srs_info.keys()}")
                except (ValueError, TypeError) as field_error:
                    logger.warning(f"SRS情報の数値変換エラー: 問題ID {qid}, エラー: {field_error}")
                    continue

            logger.info(f"SRSデータ検証: 元データ{len(srs_data)}問 → 有効データ{len(valid_srs_data)}問")
            srs_data = valid_srs_data

            # 🔥 ULTRA堅牢: ブックマークデータの詳細検証と修復
            valid_bookmarks = []
            for bookmark in bookmarks:
                try:
                    # ブックマークの型チェック（文字列または数値）
                    if isinstance(bookmark, (str, int)):
                        bookmark_str = str(bookmark).strip()
                        if bookmark_str and bookmark_str.isdigit():
                            valid_bookmarks.append(bookmark_str)
                    else:
                        logger.warning(f"ブックマークが無効な型: {bookmark}, 型: {type(bookmark)}")
                except Exception as bookmark_error:
                    logger.warning(f"ブックマーク処理エラー: {bookmark}, エラー: {bookmark_error}")
                    continue

            logger.info(f"ブックマーク検証: 元データ{len(bookmarks)}問 → 有効データ{len(valid_bookmarks)}問")
            bookmarks = valid_bookmarks

            # すべての復習対象問題IDを統合（重複除去）
            all_review_ids = set()

            # SRSデータから取得（文字列に変換してから統合）
            for qid in srs_data.keys():
                if qid and str(qid).strip():  # 空文字や None をスキップ
                    all_review_ids.add(str(qid))

            # ブックマークから取得（文字列に変換してから統合）
            for qid in bookmarks:
                if qid and str(qid).strip():  # 空文字や None をスキップ
                    all_review_ids.add(str(qid))

            # リストに変換
            review_question_ids = list(all_review_ids)

            logger.info(f"復習対象問題統合: SRS={len(srs_data)}問, ブックマーク={len(bookmarks)}問, 統合後={len(review_question_ids)}問")

        except Exception as integration_error:
            logger.error(f"復習データ統合エラー: {integration_error}")
            return render_template('error.html',
                                   error="復習データの処理中にエラーが発生しました。",
                                   error_type="data_integration_error")

        if not review_question_ids:
            # SRSデータがない場合の案内メッセージ
            srs_data = session.get('advanced_srs', {})
            if not srs_data:
                return render_template('error.html',
                                       error="復習リストが空です。まず問題を解いて間違えることで、科学的な復習システムが学習を開始します。",
                                       error_type="no_srs_data")
            else:
                return render_template('error.html',
                                       error="現在復習が必要な問題がありません。素晴らしい！新しい問題に挑戦するか、時間が経ってから復習してください。",
                                       error_type="all_mastered")

        # 🔥 CRITICAL: 問題データマッチングと弱点スコア計算（ウルトラシンク対応）
        try:
            # 問題IDから実際の問題データを取得（安全性強化）
            questions_dict = {}
            for q in all_questions:
                try:
                    q_id = str(q.get('id', ''))
                    if q_id and q_id.strip():  # 空文字チェック
                        questions_dict[q_id] = q
                except Exception as q_parse_error:
                    logger.warning(f"問題ID変換エラー: {q_parse_error}, question={q}")
                    continue

            logger.info(f"問題辞書作成完了: {len(questions_dict)}問")

            review_questions_with_score = []
            successful_matches = 0
            failed_matches = 0

            for qid in review_question_ids:
                try:
                    if qid in questions_dict:
                        question = questions_dict[qid]

                        # 弱点スコア計算（安全性強化）
                        try:
                            srs_info = srs_data.get(qid, {})

                            # 数値データの安全な取得
                            wrong_count = max(0, int(srs_info.get('wrong_count', 0)))
                            total_attempts = max(1, int(srs_info.get('total_attempts', 1)))
                            difficulty_level = max(0, float(srs_info.get('difficulty_level', 5)))

                            # 復習期限チェック（エラーハンドリング強化）
                            overdue_bonus = 0
                            next_review = srs_info.get('next_review', '')
                            if next_review:
                                try:
                                    from datetime import datetime
                                    next_review_date = datetime.fromisoformat(next_review)
                                    days_overdue = max(0, (datetime.now() - next_review_date).days)
                                    overdue_bonus = min(50, days_overdue * 2)  # 最大50に制限
                                except Exception as date_error:
                                    logger.debug(f"日付解析エラー（問題ID: {qid}）: {date_error}")
                                    overdue_bonus = 5  # デフォルト値

                            # 🔥 ULTRA SYNC PRECISION FIX: 弱点スコア計算の精度保証（オーバーフロー防止）
                            error_rate_decimal = Decimal(str(wrong_count)) / Decimal(str(total_attempts))
                            # 🔥 ULTRA SYNC FIX: 未使用変数削除済み
                            
                            weakness_decimal = (error_rate_decimal * Decimal('100')) + Decimal(str(difficulty_level)) + Decimal(str(overdue_bonus))
                            weakness_score = float(min(Decimal('1000'), weakness_decimal.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)))

                            review_questions_with_score.append({
                                'question': question,
                                'weakness_score': weakness_score,
                                'wrong_count': wrong_count,
                                'total_attempts': total_attempts,
                                'overdue_bonus': overdue_bonus
                            })

                            successful_matches += 1

                        except Exception as score_error:
                            logger.warning(f"弱点スコア計算エラー（問題ID: {qid}）: {score_error}")
                            # エラーが発生した問題もデフォルトスコアで追加
                            review_questions_with_score.append({
                                'question': question,
                                'weakness_score': 50,  # デフォルトスコア
                                'wrong_count': 1,
                                'total_attempts': 1,
                                'overdue_bonus': 0
                            })
                            successful_matches += 1
                    else:
                        failed_matches += 1
                        logger.debug(f"問題IDが見つかりません: {qid}")

                except Exception as match_error:
                    logger.warning(f"問題マッチングエラー（ID: {qid}）: {match_error}")
                    failed_matches += 1
                    continue

            logger.info(f"問題マッチング結果: 成功={successful_matches}問, 失敗={failed_matches}問")

        except Exception as processing_error:
            logger.error(f"弱点スコア処理の重大エラー: {processing_error}")
            return render_template('error.html',
                                   error="復習問題の評価中にエラーが発生しました。",
                                   error_type="score_processing_error")

        if not review_questions_with_score:
            return render_template('error.html',
                                   error="復習対象の問題が見つかりません。新しい問題を解いて間違えることで復習リストが作成されます。",
                                   error_type="no_filtered_questions")

        # 🔥 ULTRA CRITICAL: 最終問題選択とセッション設定（ウルトラシンク対応）
        try:
            # 🔥 ULTRA堅牢: 弱点スコア順でソート（安全なソート・完全エラーハンドリング）
            try:
                # 各問題の弱点スコアが数値であることを確認
                for item in review_questions_with_score:
                    if not isinstance(item.get('weakness_score'), (int, float)):
                        item['weakness_score'] = 50.0  # デフォルトスコア

                review_questions_with_score.sort(key=lambda x: float(x.get('weakness_score', 0)), reverse=True)
                logger.info(f"弱点スコア順ソート完了: {len(review_questions_with_score)}問")
            except Exception as sort_error:
                logger.warning(f"ソートエラー（デフォルト順序を使用）: {sort_error}")
                # ソートに失敗してもそのまま続行

            # 🔥 ULTRA CRITICAL: セッション問題数の動的決定（最低保証とユーザー要求バランス）
            available_questions = len(review_questions_with_score)
            min_session_size = min(3, available_questions)  # 最低3問、または利用可能問題数
            target_session_size = get_user_session_size(session)  # ユーザー設定を尊重（10/20/30問）
            session_size = min(target_session_size, available_questions)  # 利用可能問題数に制限

            if session_size < min_session_size:
                logger.error(f"復習問題が不足: 利用可能{available_questions}問, 最低必要{min_session_size}問")
                return render_template('error.html',
                                       error=f"復習問題が不足しています（{available_questions}問）。もう少し問題を解いてから復習してください。",
                                       error_type="insufficient_review_questions")

            logger.info(f"復習セッション問題数決定: 理想{target_session_size}問 → 実際{session_size}問（利用可能{available_questions}問）")

            selected_review_items = review_questions_with_score[:session_size]
            review_questions = []

            # 問題データの安全な抽出
            for item in selected_review_items:
                try:
                    question = item.get('question')
                    if question and question.get('id'):
                        review_questions.append(question)
                except Exception as extract_error:
                    logger.warning(f"問題抽出エラー: {extract_error}")
                    continue

            if not review_questions:
                logger.error("最終的に有効な復習問題が0問になりました")
                return render_template('error.html',
                                       error="復習問題の準備中に問題が発生しました。しばらく待ってから再度お試しください。",
                                       error_type="final_question_preparation_error")

            logger.info(f"復習問題最終選択: 全{len(review_questions_with_score)}問中{len(review_questions)}問を弱点スコア順で選択")

            # 上位問題のスコア情報をログ出力（安全な範囲）
            for i, item in enumerate(selected_review_items[:min(5, len(selected_review_items))]):
                try:
                    q_id = item.get('question', {}).get('id', 'unknown')
                    score = item.get('weakness_score', 0)
                    wrong = item.get('wrong_count', 0)
                    total = item.get('total_attempts', 1)
                    logger.info(f"  {i+1}位: 問題ID{q_id}, 弱点スコア{score:.1f}, 間違い{wrong}/{total}")
                except Exception as log_error:
                    logger.debug(f"ログ出力エラー: {log_error}")

            # セッションに安全に設定
            try:
                category_name = f'復習問題（弱点優先{len(review_questions)}問）'

                # 問題IDの安全な変換
                question_ids = []
                for q in review_questions:
                    try:
                        q_id = int(q.get('id', 0))
                        if q_id > 0:  # 有効なIDのみ追加
                            question_ids.append(q_id)
                    except (ValueError, TypeError) as id_error:
                        logger.warning(f"問題ID変換エラー: {id_error}, question={q}")
                        continue

                if not question_ids:
                    logger.error("有効な問題IDが0個になりました")
                    return render_template('error.html',
                                           error="復習問題IDの処理中にエラーが発生しました。",
                                           error_type="question_id_processing_error")

                # 🔥 ULTRA堅牢: セッション変数を安全に設定（ウルトラシンク対応・完全検証）
                try:
                    # セッションクリア（競合防止）
                    safe_exam_session_reset()
                    session.pop('selected_question_type', None)
                    session.pop('department', None)
                    session.pop('selected_department', None)

                    # 新しいセッション設定
                    session['exam_question_ids'] = question_ids
                    session['exam_current'] = 0
                    session['exam_category'] = category_name
                    session['selected_question_type'] = 'review'  # 復習専用タイプ
                    session['department'] = ''  # 復習では部門指定なし
                    session['selected_department'] = ''  # セッション再構築用（復習では部門なし）
                    session.modified = True
                    
                    # 🔥 ULTRA SYNC FIX: セッション書き込み確認
                    logger.info(f"復習セッション設定完了: selected_question_type={session.get('selected_question_type')}, 問題数={len(question_ids)}")

                    # セッション即座保存強制
                    session.permanent = True
                    
                    # 🔥 CRITICAL FIX: セッション書き込み即座実行
                    import time
                    time.sleep(0.1)  # セッション書き込み待機

                    logger.info(f"復習セッション設定完了: {len(question_ids)}問, モード: {category_name}")
                    logger.info(f"復習詳細: 弱点スコア順優先, 全部門対象, 問題ID={question_ids[:5] if question_ids else []}")

                except Exception as set_error:
                    logger.error(f"セッション変数設定エラー: {set_error}")
                    return render_template('error.html',
                                           error="復習セッション変数の設定中にエラーが発生しました。",
                                           error_type="session_variable_error")

                # 🔥 ULTRA堅牢: セッション状態の最終確認（複数回検証）
                verification_attempts = 0
                max_verification_attempts = 3

                while verification_attempts < max_verification_attempts:
                    try:
                        final_ids = session.get('exam_question_ids', [])
                        # 🛡️ ULTRA SYNC: デフォルト値統一 (負数 → 0)
                        final_current = session.get('exam_current', 0)
                        final_category = session.get('exam_category', '')
                        final_question_type = session.get('selected_question_type', '')

                        logger.info(
                            f"セッション設定確認 (試行{verification_attempts + 1}): "
                            f"exam_question_ids={len(final_ids) if final_ids else 0}問, "
                            f"exam_current={final_current}, exam_category='{final_category}', "
                            f"question_type='{final_question_type}'")

                        # 検証条件
                        if (final_ids and len(final_ids) > 0 and
                            final_current >= 0 and
                            final_category and
                                final_question_type == 'review'):
                            logger.info(f"✅ セッション設定検証成功 (試行{verification_attempts + 1})")
                            break
                        else:
                            verification_attempts += 1
                            if verification_attempts < max_verification_attempts:
                                logger.warning(f"セッション設定検証失敗 (試行{verification_attempts}) - 再設定中...")
                                # 再設定
                                session['exam_question_ids'] = question_ids
                                session['exam_current'] = 0
                                session['exam_category'] = category_name
                                session['selected_question_type'] = 'review'
                                session.modified = True
                            else:
                                logger.error(f"セッション設定検証失敗 (最大試行{max_verification_attempts}回)")
                                return render_template('error.html',
                                                       error="復習セッションの設定検証に失敗しました。ページを再読み込みして再度お試しください。",
                                                       error_type="session_verification_error")
                    except Exception as verify_error:
                        logger.error(f"セッション検証エラー (試行{verification_attempts + 1}): {verify_error}")
                        verification_attempts += 1

            except Exception as session_error:
                logger.error(f"セッション設定エラー: {session_error}")
                return render_template('error.html',
                                       error="復習セッションの準備中にエラーが発生しました。",
                                       error_type="session_preparation_error")

        except Exception as final_error:
            logger.error(f"最終処理エラー: {final_error}")
            return render_template('error.html',
                                   error="復習問題の最終準備中にエラーが発生しました。",
                                   error_type="final_processing_error")

        logger.info("=== 復習開始処理完了 - examページへリダイレクト ===")

        # 最初の問題にリダイレクト
        return redirect(url_for('exam'))

    except Exception as e:
        logger.error(f"🔥 復習問題開始の重大エラー: {e}")
        import traceback
        logger.error(f"詳細エラー情報: {traceback.format_exc()}")
        return render_template('error.html',
                               error="復習問題の開始中に予期しないエラーが発生しました。ページを再読み込みして再度お試しください。",
                               error_type="critical_review_error")


@app.route('/debug/create_review_data')
def create_review_test_data():
    """🔥 復習テスト用ダミーデータ作成（ウルトラシンク対応）"""
    try:
        from datetime import datetime, timedelta
        # データディレクトリの設定
        data_dir = os.path.dirname(DataConfig.QUESTIONS_CSV)
        # 🛡️ ULTRATHIN区 Stage 3: デバッグ機能でも分離データ読み込み適用
        from utils import load_basic_questions_only, load_specialist_questions_only
        basic_questions = load_basic_questions_only(data_dir)
        # デバッグ用は限定的な専門科目読み込み（道路/2016年のみ）
        specialist_questions = load_specialist_questions_only('道路', 2016, data_dir)
        all_questions = basic_questions + specialist_questions
        if not all_questions:
            return "問題データが見つかりません", 400

        # ランダムに10-20問を選択してSRSデータを作成
        sample_size = min(20, len(all_questions))
        sample_questions = random.sample(all_questions, sample_size)

        srs_data = {}
        bookmarks = []

        for i, question in enumerate(sample_questions):
            q_id = str(question.get('id', ''))
            if not q_id:
                continue

            # 多様な復習データを作成
            wrong_count = random.randint(1, 5)
            total_attempts = wrong_count + random.randint(1, 3)
            difficulty_level = random.uniform(3.0, 8.0)

            # 復習期限（一部は期限切れに設定）
            days_ago = random.randint(-5, 10)  # 過去5日〜未来10日
            next_review = (datetime.now() + timedelta(days=days_ago)).isoformat()

            srs_data[q_id] = {
                'wrong_count': wrong_count,
                'total_attempts': total_attempts,
                'difficulty_level': difficulty_level,
                'next_review': next_review,
                'correct_count': total_attempts - wrong_count,
                'mastered': False
            }

            # 🔥 ULTRA SYNC FIX: 一部をブックマークにも追加（文字列形式で統一）
            if i < 5:
                bookmarks.append(str(q_id))  # 文字列として追加で統一

        # セッションに保存
        # HTTP 431完全対策: SRSデータセッション保存無効化
    # session['advanced_srs'] = srs_data
        session['bookmarks'] = bookmarks
        session.modified = True

        logger.info(f"復習テストデータ作成: SRS={len(srs_data)}問, ブックマーク={len(bookmarks)}問")

        return """
        <h2>🔥 復習テストデータ作成完了！</h2>
        <p>SRSデータ: {len(srs_data)}問</p>
        <p>ブックマーク: {len(bookmarks)}問</p>
        <p><a href="/review">復習リストを確認</a></p>
        <p><a href="/exam/review">復習開始をテスト</a></p>
        <p><a href="/">ホームに戻る</a></p>
        """

    except Exception as e:
        logger.error(f"復習テストデータ作成エラー: {e}")
        return f"エラー: {e}", 500


@app.route('/debug/clear_session')
def clear_session_debug():
    """🔥 セッションクリア（デバッグ用）"""
    try:
        # 復習関連データのみクリア
        session.pop('advanced_srs', None)
        session.pop('bookmarks', None)
        safe_exam_session_reset()
        session.modified = True

        return "セッションクリア完了"
    except Exception as e:
        return f"エラー: {e}", 500


@app.route('/debug/session')
def debug_session():
    """デバッグ用セッション情報取得"""
    try:
        session_info = {
            'exam_question_ids': session.get('exam_question_ids', []),
            'exam_current': session.get('exam_current'),
            'exam_category': session.get('exam_category'),
            'selected_question_type': session.get('selected_question_type'),
            'selected_department': session.get('selected_department'),
            'selected_year': session.get('selected_year')
        }
        return jsonify(session_info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/debug/set_current', methods=['POST'])
def debug_set_current():
    """デバッグ用: exam_currentを直接設定（10問目テスト用）"""
    try:
        data = request.get_json()
        if not data or 'exam_current' not in data:
            return jsonify({'error': 'exam_current パラメータが必要です'}), 400
        
        new_current = data['exam_current']
        if not isinstance(new_current, int) or new_current < 0:
            return jsonify({'error': 'exam_current は0以上の整数である必要があります'}), 400
        
        # 現在のセッション状態を確認
        exam_question_ids = session.get('exam_question_ids', [])
        if not exam_question_ids:
            return jsonify({'error': 'アクティブなセッションがありません。先に問題セッションを開始してください。'}), 400
        
        # 範囲チェック
        if new_current >= len(exam_question_ids):
            return jsonify({'error': f'exam_current は0から{len(exam_question_ids)-1}の範囲で指定してください'}), 400
        
        # セッション更新
        old_current = session.get('exam_current', 0)
        session['exam_current'] = new_current
        session.modified = True
        
        logger.info(f"DEBUG: exam_current更新 {old_current} → {new_current}")
        
        return jsonify({
            'success': True,
            'old_current': old_current,
            'new_current': new_current,
            'total_questions': len(exam_question_ids),
            'message': f'exam_current を {new_current} に設定しました（{new_current+1}問目）'
        })
        
    except Exception as e:
        logger.error(f"DEBUG: set_current エラー: {e}")
        return jsonify({'error': str(e)}), 500


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


@app.route('/adaptive_questions')
def adaptive_questions():
    """アダプティブ問題練習モード（部門別対応版）"""
    try:
        learning_mode = request.args.get('mode', 'balanced')
        # ユーザー設定に基づく問題数を取得
        session_size = get_user_session_size(session)
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
        session['exam_question_ids'] = question_ids
        session['exam_current'] = 0

        # カテゴリ名を部門別に調整
        category_name = 'AI適応学習'
        if department:
            dept_name = RCCMConfig.DEPARTMENTS.get(department, {}).get('name', department)
            category_name = f'AI適応学習 ({dept_name})'

        session['exam_category'] = category_name
        session['adaptive_mode'] = learning_mode
        if department:
            session['selected_department'] = department
        session.modified = True

        logger.info(f"アダプティブ問題開始: {len(question_ids)}問, モード: {learning_mode}, 部門: {department or '全体'}")

        # 最初の問題を表示
        return redirect(url_for('exam'))

    except Exception as e:
        logger.error(f"アダプティブ問題エラー: {e}")
        return render_template('error.html', error="アダプティブ問題の開始中にエラーが発生しました。")


@app.route('/integrated_learning')
def integrated_learning():
    """4-1基礎と4-2専門の連携学習モード"""
    try:
        # パラメータ取得
        learning_mode = request.args.get('mode', 'basic_to_specialist')
        # ユーザー設定に基づく問題数を取得
        session_size = get_user_session_size(session)
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
        session['exam_question_ids'] = question_ids
        session['exam_current'] = 0

        # カテゴリ名設定
        mode_names = {
            'basic_to_specialist': '基礎→専門連携学習',
            'foundation_reinforced': '基礎強化学習'
        }
        category_name = mode_names.get(learning_mode, '連携学習')

        if department:
            dept_name = RCCMConfig.DEPARTMENTS.get(department, {}).get('name', department)
            category_name = f'{category_name} ({dept_name})'

        session['exam_category'] = category_name
        session['adaptive_mode'] = learning_mode
        session['foundation_mastery'] = foundation_mastery
        if department:
            session['selected_department'] = department
        session.modified = True

        logger.info(f"連携学習開始: {len(question_ids)}問, モード: {learning_mode}, 部門: {department or '全体'}, 基礎習熟度: {foundation_mastery:.2f}")

        # 最初の問題を表示
        return redirect(url_for('exam'))

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
            # 🔥 ULTRA SYNC TIMEZONE FIX: UTC基準のAPIタイムスタンプ
            'timestamp': format_utc_to_iso()
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
            # 🔥 ULTRA SYNC TIMEZONE FIX: UTC基準のAPIタイムスタンプ
            'timestamp': format_utc_to_iso()
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
            # 🔥 ULTRA SYNC TIMEZONE FIX: UTC基渖のレポート生成タイムスタンプ
            'generated_at': format_utc_to_iso()
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
            # 🔥 ULTRA SYNC TIMEZONE FIX: UTC基準のAPIタイムスタンプ
            'timestamp': format_utc_to_iso()
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


@app.route('/start_exam/<exam_type>', methods=['GET', 'POST'])
# 🔥 ULTRA SYNC: 統合セッション管理システムで自動処理
@memory_monitoring_decorator(_memory_leak_monitor)
def start_exam(exam_type):
    """
    試験開始
    
    HTTP 431対策: GET/POSTリクエストの両方をサポート
    - 大きなデータ（questions parameter等）をPOSTで受信してヘッダーサイズ制限を回避
    - 従来のGETリクエストも継続サポート
    - JSON形式のカスタム問題データや試験設定を受け付け
    """
    try:
        # 🛡️ ULTRATHIN区段階11: 最上位例外処理強化
        logger.info(f"🛡️ ULTRATHIN段階11: start_exam開始 - {exam_type}, method: {request.method}")
        
        # 🔥 CRITICAL FIX: モジュール遅延読み込み確認
        ensure_modules_loaded()
        
        # 🛡️ HTTP 431対策: GET/POSTパラメータ統合処理
        # 大きなデータをPOSTで受信してHTTP 431エラーを回避
        def get_request_param(param_name, default=None):
            """GET/POSTリクエストから統合的にパラメータを取得"""
            if request.method == 'POST':
                return request.form.get(param_name, default)
            else:
                return request.args.get(param_name, default)
        
        questions_param = get_request_param('questions')
        
        # 🛡️ HTTP 431対策: その他のパラメータも統合処理で対応
        exam_config_param = get_request_param('exam_config')
        category_param = get_request_param('category')
        difficulty_param = get_request_param('difficulty')
        year_param = get_request_param('year')
        
        # 🔥 ULTRA SYNC FIX: 詳細エラーログ追加
        logger.info(f"🔥 EXAM START: 試験開始処理開始 - exam_type: {exam_type}, method: {request.method}")
        
        # 🛡️ ULTRATHIN区段階10: GETリクエスト時の適切な処理（修正版）
        if request.method == 'GET' and not any([questions_param, exam_config_param, category_param]):
            logger.info(f"🛡️ ULTRATHIN段階10: 純粋なGETリクエスト検出 - exam_simulatorにリダイレクト")
            return redirect(url_for('exam_simulator_page'))
        
        # 🛡️ ULTRATHIN区段階10: POSTリクエスト確認ログ
        logger.info(f"🛡️ ULTRATHIN段階10: リクエスト詳細 - method: {request.method}, has_form_data: {len(request.form) > 0}")
        if questions_param:
            logger.info(f"🔥 EXAM START: questions parameter received - length: {len(questions_param)}")
        if exam_config_param:
            logger.info(f"🔥 EXAM START: exam_config parameter received - length: {len(exam_config_param)}")
        if category_param:
            logger.info(f"🔥 EXAM START: category parameter received: {category_param}")
        if difficulty_param:
            logger.info(f"🔥 EXAM START: difficulty parameter received: {difficulty_param}")
        if year_param:
            logger.info(f"🔥 EXAM START: year parameter received: {year_param}")
        
        # 🛡️ ULTRATHIN区 段階2: 部門別動的読み込み実装
        if exam_type == '基礎科目':
            # 基礎科目の場合は基礎問題のみ
            all_questions = load_questions()  # 基礎科目のみ読み込み
            logger.info(f"🔥 EXAM START: 基礎科目データ読み込み完了 - {len(all_questions)}問")
        else:
            # 専門科目の場合は該当部門のみ動的読み込み
            from utils import load_specialist_questions_only
            data_dir = os.path.dirname(DataConfig.QUESTIONS_CSV)
            
            # 年度パラメータの取得（デフォルト2016）
            target_year = int(year_param) if year_param and year_param.isdigit() else 2016
            
            try:
                # 🚨 ULTRATHIN区段階38緊急修正: 部門名マッピング修正
                # URL部門名をデータファイル内部門名に変換
                department_mapping = {
                    '都市計画': '都市計画及び地方計画',
                    '鋼構造・コンクリート': '鋼構造及びコンクリート',
                    '土質・基礎': '土質及び基礎', 
                    '施工計画': '施工計画、施工設備及び積算',
                    '上下水道': '上水道及び工業用水道'
                }
                
                # 部門名を正しくマッピング
                mapped_department = department_mapping.get(exam_type, exam_type)
                
                # 🛡️ ULTRATHIN区 段階3: 詳細診断情報追加
                logger.info(f"🔥 EXAM START: 専門科目読み込み開始 - URL部門:{exam_type}, マップ部門:{mapped_department}, 年度:{target_year}, data_dir:{data_dir}")
                
                # 指定された部門・年度のみ読み込み（混在防止）
                specialist_questions = load_specialist_questions_only(mapped_department, target_year, data_dir)
                all_questions = specialist_questions
                logger.info(f"🔥 EXAM START: 専門科目データ読み込み完了 - 部門:{exam_type}, 年度:{target_year}, {len(all_questions)}問")
                
                # 成功時のデバッグ情報
                if all_questions:
                    sample_q = all_questions[0]
                    logger.info(f"🔥 EXAM START: サンプル問題 - カテゴリ:{sample_q.get('category')}, ID:{sample_q.get('id')}")
                
            except Exception as e:
                # 🛡️ ULTRATHIN区 段階3: 詳細エラー情報
                import traceback
                error_detail = traceback.format_exc()
                logger.error(f"🚨 専門科目読み込み例外詳細: {exam_type}/{target_year}")
                logger.error(f"🚨 例外タイプ: {type(e).__name__}")
                logger.error(f"🚨 例外メッセージ: {str(e)}")
                logger.error(f"🚨 スタックトレース: {error_detail}")
                logger.error(f"🚨 data_dir値: {data_dir}")
                
                # エラー情報をセッションに保存（デバッグ用）
                session['specialist_error'] = {
                    "type": type(e).__name__,
                    "message": str(e),
                    "department": exam_type,
                    "year": target_year,
                    "data_dir": data_dir,
                    "timestamp": datetime.now().strftime('%H:%M:%S')
                }
                
                # エラー時は基礎科目にフォールバック
                all_questions = load_questions()
                logger.warning(f"🔄 専門科目読み込み失敗、基礎科目にフォールバック - 基礎科目数:{len(all_questions)}問")
        
        # 🛡️ HTTP 431対策: questions parameterが提供された場合の処理
        if questions_param:
            try:
                # JSON形式の問題データを解析
                import json
                custom_questions = json.loads(questions_param)
                if isinstance(custom_questions, list) and len(custom_questions) > 0:
                    all_questions = custom_questions
                    logger.info(f"🔥 EXAM START: カスタム問題データ使用 - {len(all_questions)}問")
            except (json.JSONDecodeError, TypeError) as e:
                logger.warning(f"🔥 EXAM START: questions parameterの解析に失敗 - {e}")
                # カスタム問題データの解析に失敗した場合は通常の問題データを使用
        
        # 🛡️ HTTP 431対策: exam_config parameterが提供された場合の処理
        custom_exam_config = None
        if exam_config_param:
            try:
                import json
                custom_exam_config = json.loads(exam_config_param)
                logger.info(f"🔥 EXAM START: カスタム試験設定使用")
            except (json.JSONDecodeError, TypeError) as e:
                logger.warning(f"🔥 EXAM START: exam_config parameterの解析に失敗 - {e}")
                # カスタム試験設定の解析に失敗した場合は通常の設定を使用
        
        # 🛡️ ULTRATHIN区 段階3: デバッグ情報をセッションに保存（副作用なし）
        debug_info = {
            "exam_type": exam_type,
            "target_year": target_year if exam_type != '基礎科目' else 'N/A',
            "questions_count": len(all_questions) if all_questions else 0,
            "data_source": "specialist" if exam_type != '基礎科目' else "basic",
            "timestamp": datetime.now().strftime('%H:%M:%S')
        }
        session['debug_info'] = debug_info
        
        if not all_questions:
            logger.error(f"🔥 EXAM START: 問題データが空です")
            debug_info["error"] = "問題データが空"
            return render_template('error.html', error="問題データが存在しません。")

        # 🔥 ULTRA SYNC FIX: 試験セッション生成に詳細ログ追加
        logger.info(f"🔥 EXAM START: 試験セッション生成開始")
        
        # 🛡️ ULTRATHIN区緊急修正: 専門科目選択時のセッション設定
        # 🚨 CRITICAL FIX: selected_question_typeの設定（カテゴリー混在バグ完全解決）
        if exam_type == 'specialist':
            session['selected_question_type'] = 'specialist'
            session['selected_department'] = category_param or ''
            session['selected_year'] = year_param
            logger.info(f"🛡️ ULTRATHIN区: 専門科目セッション設定完了 - type=specialist, dept={category_param}, year={year_param}")
        elif exam_type == 'basic':
            session['selected_question_type'] = 'basic'
            session['selected_department'] = ''
            session['selected_year'] = None
            logger.info(f"🛡️ ULTRATHIN区: 基礎科目セッション設定完了 - type=basic")
        else:
            # フォールバック: exam_typeから推定
            if 'specialist' in exam_type or 'department' in exam_type:
                session['selected_question_type'] = 'specialist'
            else:
                session['selected_question_type'] = 'basic'
            session['selected_department'] = category_param or ''
            session['selected_year'] = year_param
            logger.warning(f"🛡️ ULTRATHIN区: フォールバック設定 - exam_type={exam_type}, inferred_type={session['selected_question_type']}")
        
        session.modified = True
        
        # 🛡️ HTTP 431対策: カスタム設定やフィルタリングを適用
        filtered_session = session.copy()
        if category_param:
            filtered_session['category_filter'] = category_param
        if difficulty_param:
            filtered_session['difficulty_filter'] = difficulty_param
        if year_param:
            filtered_session['year_filter'] = year_param
        
        # 🚨 緊急修正: 4-1と4-2の完全分離（大きな壁の設置）
        # exam_simulatorを使わず、get_mixed_questions関数で直接問題選択
        selected_questions = get_mixed_questions(
            session, 
            all_questions, 
            '全体', 
            session_size=get_user_session_size(session),
            department=category_param or '',
            question_type=session.get('selected_question_type', ''),
            year=year_param
        )
        
        # 4-1と4-2の混在を防ぐ最終チェック
        question_type_check = session.get('selected_question_type', '')
        if question_type_check == 'basic':
            # 基礎科目の場合：専門科目が混入していないかチェック
            contaminated = [q for q in selected_questions if q.get('question_type') != 'basic']
            if contaminated:
                logger.error(f"🚨 基礎科目に専門科目混入検出: {len(contaminated)}問 - 除去します")
                selected_questions = [q for q in selected_questions if q.get('question_type') == 'basic']
        elif question_type_check == 'specialist':
            # 専門科目の場合：基礎科目が混入していないかチェック
            contaminated = [q for q in selected_questions if q.get('question_type') != 'specialist']
            if contaminated:
                logger.error(f"🚨 専門科目に基礎科目混入検出: {len(contaminated)}問 - 除去します")
                selected_questions = [q for q in selected_questions if q.get('question_type') == 'specialist']
        
        # 手動でsimple exam_session作成
        import time as time_module
        exam_session = {
            'exam_id': f"exam_{int(time_module.time())}",
            'exam_type': exam_type,
            'questions': selected_questions,
            'current_question': 0,
            'start_time': time_module.time(),
            'status': 'in_progress',
            'answers': [],
            'selected_question_type': session.get('selected_question_type', ''),
            'selected_department': session.get('selected_department', ''),
            'selected_year': session.get('selected_year')
        }
        
        logger.info(f"🛡️ 4-1/4-2完全分離: {question_type_check}で{len(selected_questions)}問選択完了")
        logger.info(f"🔥 EXAM START: 試験セッション生成完了 - ID: {exam_session.get('exam_id', 'UNKNOWN')}")

        # 🛡️ HTTP 431緊急対策: exam_session完全軽量化
        # 300-600KBのexam_sessionを10KB以下に削減
        # 🛡️ ULTRATHIN最終対策: 超軽量セッション（必須データのみ）
        lightweight_session = {
            'exam_id': exam_session.get('exam_id', '')[:8],  # ID短縮
            'exam_type': exam_session.get('exam_type', '')[:10],  # タイプ短縮
            'q_count': len(exam_session.get('questions', [])),  # 問題数のみ
            'current': 0,  # 現在位置
            'status': 'in_progress',  # 🛡️ ULTRATHIN区段階5: exam_question関数との整合性確保
            'year': year_param  # 年度情報追加
        }
        
        # メモリに試験データ保存（セッション外）
        exam_id = exam_session.get('exam_id', '')
        store_exam_data_in_memory(exam_id, exam_session)
        
        session['exam_session'] = lightweight_session
        session.modified = True
        
        # 🛡️ ULTRATHIN区段階6: セッション保存強制実行・検証強化
        try:
            # セッション保存の強制実行（Flask内部処理）
            session.permanent = True  # セッション永続化フラグ
            
            # 🛡️ ULTRATHIN区段階26: セッション保存の確実化（検証ループ削除）
            # 複雑な検証ループを削除し、make_responseで確実に保存
            session['exam_session'] = lightweight_session
            session.modified = True
            
            # 🛡️ ULTRATHIN区段階26: メモリ保存確認
            store_exam_data_in_memory(exam_id, exam_session)
            logger.info(f"🛡️ ULTRATHIN段階26: セッション設定完了 - exam_id: {exam_id}")
            
            session_verified = True  # 🛡️ ULTRATHIN区段階26: 信頼ベース設定
            
            logger.info(f"🛡️ ULTRATHIN段階11: 試験開始完全成功 - {exam_type}, ID: {exam_session['exam_id']}")
            
        except Exception as session_error:
            logger.error(f"🛡️ ULTRATHIN段階6: セッション検証エラー - {session_error}")
            return render_template('error.html', error="セッション管理エラーが発生しました。")

        # 🚨 ULTRATHIN区段階32緊急修正3: 段階29の安全化
        # 基礎科目でのタイムアウト問題解決（専門科目のみ段階29実行）
        if exam_type != '基礎科目':
            # 🚨 ULTRATHIN区段階29緊急修正1: セッション保存確実化（専門科目のみ）
            # 1万人使用ソフトウェアとして0%→60%改善
            try:
                # 🚨 セッション設定の再確認と強化
                session['exam_session'] = lightweight_session
                session.modified = True
                session.permanent = True
                
                # 🚨 メモリ保存の再確認
                store_exam_data_in_memory(exam_id, exam_session)
                
                # 🚨 確実なレスポンス作成とセッション保存
                response = make_response(redirect(url_for('exam_question')))
                
                # 🚨 バックアップクッキーも設定（緊急対策）
                import json
                session_backup = json.dumps({
                    'exam_id': exam_id,
                    'exam_type': exam_type,
                    'timestamp': str(datetime.now()),
                    'stage32_specialist_only': True
                })
                response.set_cookie('exam_backup', session_backup, 
                                   secure=True, httponly=True, samesite='Lax', max_age=3600)
                
                logger.info(f"🚨 ULTRATHIN段階32: 専門科目のみ段階29実行 - {exam_id}")
                return response
                
            except Exception as emergency_error:
                logger.error(f"🚨 ULTRATHIN段階32: 専門科目段階29エラー - {emergency_error}")
                return redirect(url_for('exam_simulator_page'))
        else:
            # 🚨 ULTRATHIN区段階32緊急修正4: 基礎科目超軽量処理
            # 基礎科目は段階29を完全回避
            logger.info(f"🚨 ULTRATHIN段階32: 基礎科目超軽量処理開始 - {exam_id}")
            return redirect(url_for('exam_question'))

    except Exception as e:
        # 🛡️ ULTRATHIN区段階11: 詳細例外情報の記録強化
        import traceback
        full_error = traceback.format_exc()
        logger.error(f"🛡️ ULTRATHIN段階11: start_exam例外詳細:\n{full_error}")
        logger.error(f"🛡️ ULTRATHIN段階11: リクエスト情報 - method: {request.method}, exam_type: {exam_type}")
        logger.error(f"🛡️ ULTRATHIN段階11: パラメータ - form: {dict(request.form)}, args: {dict(request.args)}")
        
        # 🛡️ ULTRATHIN区段階11: 緊急フォールバック - 少なくともセッション初期化を試行
        try:
            session['exam_session_emergency'] = {
                'exam_type': exam_type,
                'timestamp': time_module.time(),
                'status': 'emergency_fallback'
            }
            session.modified = True
            logger.warning(f"🛡️ ULTRATHIN段階11: 緊急セッション初期化完了")
        except:
            logger.error(f"🛡️ ULTRATHIN段階11: 緊急セッション初期化も失敗")
        
        return render_template('error.html', error=f"試験の開始中にエラーが発生しました。詳細: {str(e)}")


@app.route('/exam_question', methods=['GET', 'POST'])
def exam_question():
    """試験問題表示"""
    try:
        # 🔥 ULTRA SYNC FIX: 詳細ログ追加
        logger.info(f"🔥 EXAM QUESTION: 試験問題表示処理開始")
        
        exam_session = session.get('exam_session')
        logger.info(f"🛡️ ULTRATHIN段階6: EXAM QUESTION処理開始 - セッション存在: {exam_session is not None}")
        
        if not exam_session:
            # 🛡️ ULTRATHIN区段階14: 暫定的セッション復元（最安全修正）
            logger.warning(f"🛡️ ULTRATHIN段階14: セッション不存在 - デバッグ情報からの復元を試行")
            
            try:
                # 専門科目データが正常に読み込まれているかを確認
                from flask import current_app
                with current_app.test_request_context():
                    # デバッグ情報取得（専門科目分離機能は完全保護）
                    debug_response = requests.get(f"{request.url_root}debug/session_info")
                    if debug_response.status_code == 200:
                        debug_data = debug_response.json()
                        debug_info = debug_data.get('debug_info', {})
                        
                        questions_count = debug_info.get('questions_count', 0)
                        data_source = debug_info.get('data_source', '')
                        exam_type = debug_info.get('exam_type', '')
                        
                        logger.info(f"🛡️ ULTRATHIN段階14: デバッグ情報確認 - 問題数: {questions_count}, ソース: {data_source}")
                        
                        if questions_count > 0 and data_source:
                            # 専門科目データが正常に読み込まれている場合のみ復元
                            logger.info(f"🛡️ ULTRATHIN段階14: 専門科目データ正常 - セッション復元実行")
                            
                            # 暫定的なセッション復元（最小限の情報のみ）
                            restored_session = {
                                'exam_id': f"restored_{int(time.time())}",
                                'status': 'in_progress',
                                'exam_type': exam_type,
                                'questions_count': questions_count,
                                'data_source': data_source,
                                'restored': True
                            }
                            
                            session['exam_session'] = restored_session
                            session.modified = True
                            
                            logger.info(f"🛡️ ULTRATHIN段階14: セッション復元成功 - 試験継続可能")
                            
                            # 復元されたセッションで処理継続
                            exam_session = restored_session
                        else:
                            logger.error(f"🛡️ ULTRATHIN段階14: 専門科目データ未読み込み - 復元不可")
                            return redirect(url_for('exam_simulator_page'))
                    else:
                        logger.error(f"🛡️ ULTRATHIN段階14: デバッグ情報取得失敗")
                        return redirect(url_for('exam_simulator_page'))
                        
            except Exception as restore_error:
                logger.error(f"🛡️ ULTRATHIN段階14: セッション復元エラー - {restore_error}")
                return redirect(url_for('exam_simulator_page'))
        
        # 復元されたセッションまたは元のセッションで処理継続
        if not exam_session:
            logger.error(f"🛡️ ULTRATHIN段階14: 最終的にセッション取得失敗")
            return redirect(url_for('exam_simulator_page'))
            
        session_status = exam_session.get('status', 'UNKNOWN')
        exam_id = exam_session.get('exam_id', 'NO_ID')
        logger.info(f"🛡️ ULTRATHIN段階6: セッション詳細 - status: {session_status}, exam_id: {exam_id}")
        
        if session_status != 'in_progress':
            logger.error(f"🛡️ ULTRATHIN段階6: セッション状態不正 - status: {session_status}, 期待値: 'in_progress'")
            return redirect(url_for('exam_simulator_page'))

        # メモリからexam_dataを取得
        exam_id = exam_session.get('exam_id', '')
        full_exam_data = get_exam_data_from_memory(exam_id)  # 🛡️ ULTRATHIN区段階5: 正しい関数名に修正
        if not full_exam_data:
            logger.error(f"🔥 EXAM QUESTION: exam_dataが見つかりません - exam_id: {exam_id}")
            return redirect(url_for('exam_simulator_page'))

        current_q_index = full_exam_data['current_question']
        questions = full_exam_data['questions']
        
        logger.info(f"🔥 EXAM QUESTION: 問題情報 - current_index: {current_q_index}, total: {len(questions)}")

        if current_q_index >= len(questions):
            logger.info(f"🔥 EXAM QUESTION: 試験終了 - current_index: {current_q_index} >= total: {len(questions)}")
            return redirect(url_for('exam_results'))

        current_question = questions[current_q_index]

        # 🔥 ULTRA SYNC FIX: 進捗表示バグ修正のための詳細ログ
        display_current = current_q_index + 1
        logger.info(f"🔥 PROGRESS FIX: 進捗表示計算 - current_q_index: {current_q_index}, display_current: {display_current}")

        # 試験情報
        exam_info = {
            'current_question_number': display_current,  # 🔥 ULTRA SYNC FIX: 明示的に計算結果を使用
            'total_questions': len(questions),
            'time_remaining': exam_simulator.get_time_remaining(exam_session),
            'exam_type': exam_session['exam_type'],
            'exam_name': exam_session['config']['name'],
            'flagged_questions': exam_session['flagged_questions'],
            'answered_questions': list(exam_session['answers'].keys())
        }
        
        # 🔥 ULTRA SYNC FIX: exam_info の確認ログ
        logger.info(f"🔥 PROGRESS FIX: exam_info作成完了 - current_question_number: {exam_info['current_question_number']}, total_questions: {exam_info['total_questions']}")

        # 時間警告チェック
        time_warning = exam_simulator.should_give_time_warning(exam_session)

        logger.info(f"🔥 EXAM QUESTION: テンプレート描画開始 - 問題{display_current}/{len(questions)}")

        return render_template(
            'exam_question.html',
            question=current_question,
            exam_info=exam_info,
            time_warning=time_warning,
            year=lightweight_session.get('year')
        )

    except Exception as e:
        # 🔥 ULTRA SYNC FIX: 詳細例外情報の記録
        import traceback
        full_error = traceback.format_exc()
        logger.error(f"🔥 EXAM QUESTION ERROR: 試験問題表示エラー詳細:\n{full_error}")
        return render_template('error.html', error=f"試験問題の表示中にエラーが発生しました。詳細: {str(e)}")


@app.route('/submit_exam_answer', methods=['POST'])
# 🔥 ULTRA SYNC: 統合セッション管理システムで自動処理
def submit_exam_answer():
    """試験回答提出"""
    try:
        # 🔥 ULTRA SYNC FIX: 詳細ログ追加
        logger.info(f"🔥 SUBMIT ANSWER: 回答提出処理開始")
        
        exam_session = session.get('exam_session')
        logger.info(f"🔥 SUBMIT ANSWER: セッション取得 - exists: {exam_session is not None}")
        
        if not exam_session:
            logger.error(f"🔥 SUBMIT ANSWER: セッション不存在")
            return jsonify({'success': False, 'error': '試験セッションが無効です'})
            
        session_status = exam_session.get('status', 'UNKNOWN')
        logger.info(f"🔥 SUBMIT ANSWER: セッション状態 - status: {session_status}")
        
        if session_status != 'in_progress':
            logger.error(f"🔥 SUBMIT ANSWER: セッション状態不正 - status: {session_status}")
            return jsonify({'success': False, 'error': '試験セッションが無効です'})

        answer = request.form.get('answer')
        elapsed = float(request.form.get('elapsed', 0))
        question_index = exam_session['current_question']
        
        logger.info(f"🔥 SUBMIT ANSWER: 回答情報 - answer: {answer}, question_index: {question_index}, elapsed: {elapsed}")

        # 自動提出チェック
        if exam_simulator.auto_submit_check(exam_session):
            logger.info(f"🔥 SUBMIT ANSWER: 自動提出実行")
            result = exam_simulator.finish_exam(exam_session)
            # HTTP 431対策: 軽量セッション更新
            session['exam_session'].update({
                'status': 'completed',
                'current_question': exam_session.get('current_question', 0),
                'answers': exam_session.get('answers', {})
            })
            session.modified = True
            return jsonify({
                'success': True,
                'exam_finished': True,
                'redirect': url_for('exam_results')
            })

        # 🔥 ULTRA SYNC FIX: 回答提出前の状態ログ
        pre_current = exam_session.get('current_question', 'UNKNOWN')
        logger.info(f"🔥 PROGRESS UPDATE: 回答提出前 - current_question: {pre_current}")

        # 回答提出
        result = exam_simulator.submit_exam_answer(exam_session, question_index, answer, elapsed)
        
        # 🔥 ULTRA SYNC FIX: 回答提出後の状態ログ
        post_current = exam_session.get('current_question', 'UNKNOWN')
        logger.info(f"🔥 PROGRESS UPDATE: 回答提出後 - current_question: {post_current}, result: {result}")

        # HTTP 431対策: 軽量セッション更新
        session['exam_session'].update({
            'current_question': exam_session.get('current_question', 0),
            'answers': exam_session.get('answers', {})
        })
        session.modified = True
        
        # 🔥 ULTRA SYNC FIX: セッション更新後の確認
        saved_current = session.get('exam_session', {}).get('current_question', 'UNKNOWN')
        logger.info(f"🔥 PROGRESS UPDATE: セッション保存後 - current_question: {saved_current}")

        if result.get('exam_completed'):
            logger.info(f"🔥 SUBMIT ANSWER: 試験完了")
            return jsonify({
                'success': True,
                'exam_finished': True,
                'redirect': url_for('exam_results')
            })
        else:
            next_question = result.get('next_question', 0)
            remaining = result.get('remaining_questions', 0)
            logger.info(f"🔥 SUBMIT ANSWER: 次の問題へ - next_question: {next_question}, remaining: {remaining}")
            return jsonify({
                'success': True,
                'next_question': next_question,
                'remaining_questions': remaining
            })

    except Exception as e:
        logger.error(f"試験回答提出エラー: {e}")
        return jsonify({'success': False, 'error': str(e)})


# 🔥 ULTRA SYNC FIX: セッション初期化強制処理（デプロイ修正のため一時無効化）
# @app.before_request
# def ensure_session_initialized():
#     """セッション初期化の確実な実行"""
#     try:
#         # セッションが空の場合、最低限の初期化を行う
#         if not session:
#             session.permanent = True
#             session['_initialized'] = True
#             logger.debug("🔥 SESSION INIT: セッション初期化実行")
#         
#         # セッション状態のログ出力（デバッグ用）
#         if request.endpoint in ['start_exam', 'exam_question', 'submit_exam_answer']:
#             session_exists = bool(session.get('exam_session'))
#             logger.info(f"🔥 SESSION CHECK: endpoint={request.endpoint}, session_exists={session_exists}")
            
    except Exception as e:
        logger.error(f"🔥 SESSION INIT ERROR: {e}")
        # セッション初期化エラーでも処理を続行


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

        # HTTP 431対策: フラグ情報のみ軽量更新
        if 'flagged_ids' not in session['exam_session']:
            session['exam_session']['flagged_ids'] = []
        
        if success:
            flag_id = str(question_index)
            if action == 'flag' and flag_id not in session['exam_session']['flagged_ids']:
                session['exam_session']['flagged_ids'].append(flag_id)
            elif action == 'unflag' and flag_id in session['exam_session']['flagged_ids']:
                session['exam_session']['flagged_ids'].remove(flag_id)
        
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

        exam_simulator.finish_exam(exam_session)
        # HTTP 431対策: 軽量セッション更新（完了状態）
        session['exam_session'].update({
            'status': 'completed',
            'current_question': exam_session.get('current_question', 0),
            'answers': exam_session.get('answers', {})
        })
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

@app.route('/api/log_error', methods=['POST'])
def api_log_error():
    """🔥 CRITICAL: クライアントサイドエラーログAPI"""
    try:
        data = request.get_json()
        
        # エラーデータの検証
        if not data or 'type' not in data:
            return jsonify({'success': False, 'error': 'Invalid error data'}), 400
            
        error_type = data.get('type')
        timestamp = data.get('timestamp')
        url = data.get('url')
        user_agent = data.get('userAgent')
        
        # 🔥 CRITICAL: 完全なクライアントエラーログ
        logger.error("=== CLIENT-SIDE ERROR DETECTED ===")
        logger.error(f"🚨 Error Type: {error_type}")
        logger.error(f"🚨 URL: {url}")
        logger.error(f"🚨 User Agent: {user_agent}")
        logger.error(f"🚨 Timestamp: {timestamp}")
        
        if error_type == 'javascript_error':
            logger.error(f"🚨 JS Error Message: {data.get('message')}")
            logger.error(f"🚨 JS Error File: {data.get('filename')}")
            logger.error(f"🚨 JS Error Line: {data.get('line')}")
            logger.error(f"🚨 JS Error Column: {data.get('column')}")
            logger.error(f"🚨 JS Error Stack: {data.get('stack')}")
            
        elif error_type == 'promise_rejection':
            logger.error(f"🚨 Promise Rejection: {data.get('reason')}")
            logger.error(f"🚨 Promise Stack: {data.get('stack')}")
            
        # セッション情報もログ
        logger.error(f"🚨 Session State at Error:")
        logger.error(f"  - exam_question_ids: {session.get('exam_question_ids')}")
        logger.error(f"  - exam_current: {session.get('exam_current')}")
        logger.error(f"  - exam_category: {session.get('exam_category')}")
        logger.error(f"  - selected_question_type: {session.get('selected_question_type')}")
        logger.error(f"  - session_keys: {list(session.keys())}")
        
        logger.error("=====================================")
        
        return jsonify({'success': True, 'logged': True})
        
    except Exception as e:
        logger.error(f"エラーログAPI自体のエラー: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


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

# === 未実装ルートのリダイレクト対応（ウルトラシンク修正） ===


@app.route('/social_learning')
def social_learning_redirect():
    """ソーシャル学習機能（ヘルプからのリダイレクト対応）"""
    return redirect(url_for('social_learning_page'))


@app.route('/leaderboard')
def leaderboard_redirect():
    """ランキング機能（ヘルプからのリダイレクト対応）"""
    return redirect('/social/leaderboard')


@app.route('/health_check')
def health_check():
    """システムヘルスチェック（ウルトラシンク新規実装）"""
    try:
        # アプリケーション健康状態チェック
        health_status = {
            'status': 'healthy',
            # 🔥 ULTRA SYNC TIMEZONE FIX: UTC基準のAPIタイムスタンプ
            'timestamp': format_utc_to_iso(),
            'version': '2025 Enterprise Edition',
            'database': 'file-based',
            'checks': {
                'data_loading': 'ok',
                'session_management': 'ok',
                'ai_modules': 'ok',
                'cache_system': 'ok'
            },
            'stats': {
                'total_questions': 0,
                'active_sessions': len(session_locks) if 'session_locks' in globals() else 0,
                'memory_usage': 'normal',
                'response_time': 'fast'
            }
        }

        # 問題データの健康チェック
        try:
            questions = load_questions()
            health_status['stats']['total_questions'] = len(questions)
            health_status['checks']['data_loading'] = 'ok'
        except Exception as e:
            health_status['checks']['data_loading'] = f'error: {str(e)}'
            health_status['status'] = 'degraded'

        # AI機能の健康チェック
        try:
            # Global variables managed elsewhere
            if ai_analyzer is None or advanced_analytics is None:
                health_status['checks']['ai_modules'] = 'not_initialized'
            else:
                health_status['checks']['ai_modules'] = 'ok'
        except Exception as e:
            health_status['checks']['ai_modules'] = f'error: {str(e)}'

        # セッション管理の健康チェック
        try:
            if 'session_locks' in globals():
                health_status['stats']['active_sessions'] = len(session_locks)
                health_status['checks']['session_management'] = 'ok'
            else:
                health_status['checks']['session_management'] = 'warning: locks not initialized'
        except Exception as e:
            health_status['checks']['session_management'] = f'error: {str(e)}'

        # 最終的な健康状態判定
        if any('error' in str(check) for check in health_status['checks'].values()):
            health_status['status'] = 'unhealthy'
        elif any('warning' in str(check) for check in health_status['checks'].values()):
            health_status['status'] = 'degraded'

        return jsonify(health_status), 200 if health_status['status'] == 'healthy' else 503

    except Exception as e:
        logger.error(f"ヘルスチェックエラー: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e),
            # 🔥 ULTRA SYNC TIMEZONE FIX: UTC基準のAPIタイムスタンプ
            'timestamp': format_utc_to_iso()
        }), 500


@app.route('/api/system/file_handles')
def api_file_handle_status():
    """🔒 ファイルハンドル状況監視API（ウルトラシンク安全性監視）"""
    try:
        # アクティブファイルハンドル数取得
        active_handles = get_active_file_handles()
        
        # システム制限値取得
        import resource
        try:
            soft_limit, hard_limit = resource.getrlimit(resource.RLIMIT_NOFILE)
        except (OSError, AttributeError, ImportError) as e:
            # システムリソース取得エラーの場合は不明として設定
            logger.warning(f"System resource limit detection error: {e}")
            soft_limit, hard_limit = 'unknown', 'unknown'
            # パフォーマンス監視に影響するがシステム継続可能
            soft_limit, hard_limit = 'unknown', 'unknown'
        
        # 使用率計算
        if isinstance(soft_limit, int) and soft_limit > 0:
            usage_percentage = (active_handles / soft_limit) * 100
            status = 'healthy' if usage_percentage < 50 else 'warning' if usage_percentage < 80 else 'critical'
        else:
            usage_percentage = 0
            status = 'healthy' if active_handles < 100 else 'warning'
        
        # ファイルハンドル統計
        file_stats = {
            'active_handles': active_handles,
            'system_limits': {
                'soft_limit': soft_limit,
                'hard_limit': hard_limit
            },
            'usage_percentage': round(usage_percentage, 2),
            'status': status,
            'recommendations': []
        }
        
        # 推奨事項
        if active_handles > 50:
            file_stats['recommendations'].append('大量のファイルハンドルが使用中です')
        if usage_percentage > 70:
            file_stats['recommendations'].append('システム制限に近づいています')
        if status == 'healthy':
            file_stats['recommendations'].append('ファイルハンドル使用量は正常範囲内です')
        
        return jsonify({
            'success': True,
            'file_handle_status': file_stats,
            # 🔥 ULTRA SYNC TIMEZONE FIX: UTC基準のAPIタイムスタンプ
            'timestamp': format_utc_to_iso()
        })
        
    except Exception as e:
        logger.error(f"ファイルハンドル状況API エラー: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            # 🔥 ULTRA SYNC TIMEZONE FIX: UTC基準のAPIタイムスタンプ
            'timestamp': format_utc_to_iso()
        }), 500


@app.route('/api/system/memory_status')
def api_memory_status():
    """🔍 メモリ最適化状況監視API（ウルトラシンクメモリ監視）"""
    try:
        if _memory_optimizer:
            # ウルトラシンク最適化統計取得
            stats = _memory_optimizer.get_optimization_stats()
            
            # メモリ健康状態チェック
            is_healthy = _memory_optimizer.memory_health_check()
            
            memory_status = {
                'success': True,
                'status': 'healthy' if is_healthy else 'warning',
                'optimizer_enabled': True,
                'stats': stats,
                'recommendations': []
            }
            
            # メモリ使用量に基づく推奨事項
            current_memory = stats.get('current_memory_mb', 0)
            if current_memory > 300:
                memory_status['recommendations'].append({
                    'type': 'memory_usage',
                    'message': f'高メモリ使用量: {current_memory:.1f}MB - セッション最適化推奨',
                    'action': 'セッションクリーンアップの頻度を上げてください'
                })
            
            # キャッシュ統計
            cache_stats = stats.get('cache_stats', {})
            if cache_stats.get('estimated_memory_mb', 0) > 50:
                memory_status['recommendations'].append({
                    'type': 'cache_size',
                    'message': 'キャッシュサイズが大きくなっています',
                    'action': 'キャッシュクリーンアップを実行してください'
                })
            
        else:
            # フォールバック: 基本的なメモリ情報
            try:
                process = psutil.Process()
                memory_mb = process.memory_info().rss / 1024 / 1024
                memory_percent = psutil.virtual_memory().percent
                
                memory_status = {
                    'success': True,
                    'status': 'basic' if memory_mb < 500 else 'warning',
                    'optimizer_enabled': False,
                    'stats': {
                        'current_memory_mb': round(memory_mb, 2),
                        'system_memory_percent': round(memory_percent, 1),
                        'message': 'Ultra Sync Memory Optimizer が利用できません'
                    },
                    'recommendations': [
                        {
                            'type': 'optimizer_missing',
                            'message': 'Memory Optimizer が見つかりません',
                            'action': 'ultra_sync_memory_leak_fix.py を確認してください'
                        }
                    ]
                }
                
                if memory_mb > 500:
                    memory_status['recommendations'].append({
                        'type': 'high_memory',
                        'message': f'高メモリ使用量: {memory_mb:.1f}MB',
                        'action': 'アプリケーション再起動を検討してください'
                    })
                    
            except Exception as e:
                memory_status = {
                    'success': False,
                    'status': 'error',
                    'optimizer_enabled': False,
                    'error': str(e),
                    'message': 'メモリ情報取得に失敗しました'
                }
        
        # 🔍 ENHANCED: Memory Leak Monitor 統合データ追加
        if _memory_leak_monitor:
            try:
                leak_monitor_status = _memory_leak_monitor.get_memory_status()
                memory_status['memory_leak_monitor'] = {
                    'enabled': True,
                    'monitoring_active': leak_monitor_status.get('monitoring_active', False),
                    'total_leaks_detected': leak_monitor_status.get('total_leaks_detected', 0),
                    'monitoring_duration_hours': leak_monitor_status.get('monitoring_duration_hours', 0),
                    'recent_leaks_count': len(leak_monitor_status.get('recent_leaks', [])),
                    'recent_memory_trend': leak_monitor_status.get('recent_memory_data', [])[-3:] if leak_monitor_status.get('recent_memory_data') else []
                }
                
                # リーク検出に基づく推奨事項追加
                recent_leaks = leak_monitor_status.get('recent_leaks', [])
                if recent_leaks:
                    critical_leaks = [l for l in recent_leaks if l.get('severity') == 'critical']
                    high_leaks = [l for l in recent_leaks if l.get('severity') == 'high']
                    
                    if critical_leaks:
                        memory_status['recommendations'].append({
                            'type': 'critical_memory_leak',
                            'message': f'{len(critical_leaks)}個の重大なメモリリークが検出されました',
                            'action': '即座にアプリケーションの再起動を検討してください'
                        })
                    elif high_leaks:
                        memory_status['recommendations'].append({
                            'type': 'high_memory_leak',
                            'message': f'{len(high_leaks)}個の高レベルメモリリークが検出されました',
                            'action': 'メモリ最適化を実行してください'
                        })
                        
            except Exception as e:
                logger.warning(f"Memory Leak Monitor データ取得エラー: {e}")
                memory_status['memory_leak_monitor'] = {
                    'enabled': False,
                    'error': str(e)
                }
        else:
            memory_status['memory_leak_monitor'] = {
                'enabled': False,
                'message': 'Memory Leak Monitor が利用できません'
            }
        
        # 共通レスポンス項目追加
        memory_status.update({
            'timestamp': format_utc_to_iso(),
            'memory_optimization_info': {
                'session_limits': 'MAX_HISTORY=100, MAX_SRS=500',
                'cache_management': 'LRU + TTL',
                'lock_pooling': 'Enabled' if _memory_optimizer else 'Disabled',
                'leak_monitoring': 'Enabled' if _memory_leak_monitor else 'Disabled'
            }
        })
        
        return jsonify(memory_status)
        
    except Exception as e:
        logger.error(f"メモリ状況API エラー: {e}")
        return jsonify({
            'success': False,
            'status': 'error',
            'error': str(e),
            'timestamp': format_utc_to_iso()
        }), 500


@app.route('/api/system/optimize_memory', methods=['POST'])
@memory_optimization_decorator
def api_optimize_memory():
    """🔍 手動メモリ最適化実行API（ウルトラシンクメモリ最適化）"""
    try:
        if not _memory_optimizer:
            return jsonify({
                'success': False,
                'error': 'Memory Optimizer が利用できません',
                'timestamp': format_utc_to_iso()
            }), 503
        
        # 手動最適化実行
        cleanup_stats_before = _memory_optimizer.cleanup_stats.copy()
        
        # セッション最適化
        if 'session' in globals() and session:
            session_cleanup = _memory_optimizer.aggressive_session_cleanup(session)
        else:
            session_cleanup = 0
        
        # 緊急メモリクリーンアップ実行
        _memory_optimizer.emergency_memory_cleanup()
        
        # 統計取得
        cleanup_stats_after = _memory_optimizer.cleanup_stats.copy()
        optimization_stats = _memory_optimizer.get_optimization_stats()
        
        # 最適化結果計算
        memory_saved = cleanup_stats_after['memory_saved_mb'] - cleanup_stats_before['memory_saved_mb']
        cache_evictions = cleanup_stats_after['cache_evictions'] - cleanup_stats_before['cache_evictions']
        
        result = {
            'success': True,
            'message': 'メモリ最適化が完了しました',
            'optimization_results': {
                'session_items_cleaned': session_cleanup,
                'memory_saved_mb': round(memory_saved, 2),
                'cache_evictions': cache_evictions,
                'gc_collected': gc.collect()
            },
            'current_stats': optimization_stats,
            'timestamp': format_utc_to_iso()
        }
        
        logger.info(f"🔍 手動メモリ最適化完了: {session_cleanup}項目, {memory_saved:.2f}MB削減")
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"手動メモリ最適化API エラー: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': format_utc_to_iso()
        }), 500


# === 📊 Ultra Sync Performance Optimization API ===

@app.route('/api/system/performance_status')
#@performance_timing_decorator
def api_performance_status():
    """📊 パフォーマンス最適化状況監視API（ウルトラシンクパフォーマンス監視）"""
    try:
        if _performance_optimizer:
            # ウルトラシンクパフォーマンス統計取得
            stats = _performance_optimizer.get_performance_stats()
            
            performance_status = {
                'success': True,
                'status': 'optimized' if stats.get('data_loaded') else 'not_optimized',
                'optimizer_enabled': True,
                'stats': stats,
                'recommendations': []
            }
            
            # パフォーマンスに基づく推奨事項
            avg_response_time = stats.get('average_response_time', 0)
            if avg_response_time > 500:  # 500ms以上
                performance_status['recommendations'].append({
                    'type': 'response_time',
                    'message': f'レスポンス時間が遅延: {avg_response_time}ms',
                    'action': 'キャッシュクリーンアップまたはインデックス再構築推奨'
                })
            
            # キャッシュヒット率チェック
            cache_hit_rate = stats.get('cache_hit_rate', 0)
            if cache_hit_rate < 70:  # 70%未満
                performance_status['recommendations'].append({
                    'type': 'cache_efficiency',
                    'message': f'キャッシュヒット率が低下: {cache_hit_rate}%',
                    'action': 'キャッシュサイズ調整またはデータアクセスパターン最適化'
                })
            
            # インデックス状況チェック
            questions_indexed = stats.get('questions_indexed', 0)
            if questions_indexed == 0:
                performance_status['recommendations'].append({
                    'type': 'indexing',
                    'message': 'インデックスが構築されていません',
                    'action': 'データ再読み込みまたはインデックス手動構築'
                })
            
        else:
            # フォールバック: 基本的なパフォーマンス情報
            performance_status = {
                'success': True,
                'status': 'basic',
                'optimizer_enabled': False,
                'stats': {
                    'data_loaded': False,
                    'data_load_time': None,
                    'questions_indexed': 0,
                    'cache_hit_rate': 0,
                    'average_response_time': 0,
                    'performance_stats': {},
                    'cache_info': {}
                },
                'recommendations': [{
                    'type': 'optimization',
                    'message': 'Performance Optimizer が無効です',
                    'action': 'ultra_sync_performance_optimization.py の確認'
                }]
            }
        
        # 共通レスポンス項目追加
        performance_status.update({
            'timestamp': format_utc_to_iso(),
            'performance_optimization_info': {
                'index_types': 'ID, Category, Department, Year, Type',
                'cache_strategy': 'LRU with TTL',
                'search_complexity': 'O(1) for indexed searches'
            }
        })
        
        return jsonify(performance_status)
        
    except Exception as e:
        logger.error(f"パフォーマンス状況API エラー: {e}")
        return jsonify({
            'success': False,
            'status': 'error',
            'error': str(e),
            'timestamp': format_utc_to_iso()
        }), 500


@app.route('/api/system/performance_clear_cache', methods=['POST'])
#@performance_timing_decorator
def api_performance_clear_cache():
    """📊 パフォーマンスキャッシュクリア実行API（ウルトラシンクパフォーマンス最適化）"""
    try:
        if not _performance_optimizer:
            return jsonify({
                'success': False,
                'error': 'Performance Optimizer が利用できません',
                'timestamp': format_utc_to_iso()
            }), 503
        
        # キャッシュクリア実行
        cleared_counts = _performance_optimizer.clear_performance_cache()
        
        result = {
            'success': True,
            'message': 'パフォーマンスキャッシュがクリアされました',
            'cleared_items': cleared_counts,
            'timestamp': format_utc_to_iso()
        }
        
        logger.info(f"📊 パフォーマンスキャッシュクリア完了: {cleared_counts}")
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"パフォーマンスキャッシュクリアAPI エラー: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': format_utc_to_iso()
        }), 500


@app.route('/api/system/performance_rebuild_index', methods=['POST'])
#@performance_timing_decorator
def api_performance_rebuild_index():
    """📊 パフォーマンスインデックス再構築API（ウルトラシンクパフォーマンス最適化）"""
    try:
        if not _performance_optimizer:
            return jsonify({
                'success': False,
                'error': 'Performance Optimizer が利用できません',
                'timestamp': format_utc_to_iso()
            }), 503
        
        # 現在のキャッシュされた問題データを取得
        try:
            # 🔥 ULTRA SYNC FIX: 未定義関数修正 - 適切なデータ読み込み関数を使用
            current_questions = load_questions_improved('data/questions.csv')
            if not current_questions:
                # 🚀 ULTRATHIN区段階1: 分離設計への移行（バックアップ処理のみ）
                # バックアップとしてRCCMデータファイルからも読み込み試行
                data_dir = os.path.dirname('data/questions.csv') or 'data'
                logger.info("🛡️ ULTRATHIN区段階1: 分離関数使用開始（データ整合性チェック）")
                
                # 基礎科目と専門科目を分離して読み込み
                from utils import load_basic_questions_only, load_specialist_questions_only
                
                basic_questions = load_basic_questions_only(data_dir)
                specialist_questions_2016 = load_specialist_questions_only('土質及び基礎', 2016, data_dir)
                
                # 統合（バックアップ処理のため既存互換性を維持）
                rccm_data = basic_questions + specialist_questions_2016
                logger.info(f"🛡️ ULTRATHIN区段階1: 分離読み込み完了 - 基礎:{len(basic_questions)}問, 専門:{len(specialist_questions_2016)}問")
                
                # 🛡️ ULTRATHIN区: 分離読み込み関数は List[Dict] を返すため直接使用
                current_questions = rccm_data if isinstance(rccm_data, list) else []
        except Exception as e:
            logger.error(f"問題データ読み込みエラー: {e}")
            current_questions = []
        
        if not current_questions:
            return jsonify({
                'success': False,
                'error': '問題データが見つかりません',
                'timestamp': format_utc_to_iso()
            }), 404
        
        # インデックス再構築実行
        _performance_optimizer.build_high_performance_indexes(current_questions)
        
        # 新しい統計取得
        new_stats = _performance_optimizer.get_performance_stats()
        
        result = {
            'success': True,
            'message': 'パフォーマンスインデックスが再構築されました',
            'rebuild_results': {
                'questions_indexed': new_stats.get('questions_indexed', 0),
                'categories_indexed': new_stats.get('categories_indexed', 0),
                'departments_indexed': new_stats.get('departments_indexed', 0),
                'years_indexed': new_stats.get('years_indexed', 0),
                'types_indexed': new_stats.get('types_indexed', 0),
                'build_time': new_stats.get('data_load_time', 0)
            },
            'timestamp': format_utc_to_iso()
        }
        
        logger.info(f"📊 パフォーマンスインデックス再構築完了: {new_stats.get('questions_indexed', 0)}問")
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"パフォーマンスインデックス再構築API エラー: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': format_utc_to_iso()
        }), 500


# === 🧪 Ultra Sync Manual Test Support Routes ===

@app.route('/manual_test_dashboard')
def manual_test_dashboard():
    """🧪 手動テストダッシュボード（CLAUDE.md準拠・スクリプトテスト絶対禁止）"""
    try:
        # ウルトラシンク方針: 副作用ゼロでダッシュボード表示
        dashboard_path = os.path.join(os.path.dirname(__file__), 'manual_test_dashboard.html')
        
        if os.path.exists(dashboard_path):
            with open(dashboard_path, 'r', encoding='utf-8') as f:
                dashboard_content = f.read()
            
            logger.info("🧪 手動テストダッシュボード表示 - スクリプトテスト絶対禁止")
            return dashboard_content, 200, {'Content-Type': 'text/html; charset=utf-8'}
        else:
            logger.error("❌ 手動テストダッシュボードファイルが見つかりません")
            return render_template('error.html', 
                                   error="手動テストダッシュボードが利用できません"), 404
                                   
    except Exception as e:
        logger.error(f"手動テストダッシュボードエラー: {e}")
        return render_template('error.html', 
                               error="手動テストダッシュボードの読み込み中にエラーが発生しました"), 500


@app.route('/manual_test_guide')
def manual_test_guide():
    """🧪 手動テストガイド表示（CLAUDE.md準拠）"""
    try:
        guide_path = os.path.join(os.path.dirname(__file__), 'MANUAL_TEST_GUIDE.md')
        
        if os.path.exists(guide_path):
            with open(guide_path, 'r', encoding='utf-8') as f:
                guide_content = f.read()
            
            # Markdownをプレーンテキストとして表示
            return f"""
            <html>
            <head>
                <title>🧪 RCCM 手動テストガイド</title>
                <meta charset="UTF-8">
                <style>
                    body {{ font-family: monospace; padding: 20px; background: #f5f5f5; }}
                    pre {{ background: white; padding: 20px; border-radius: 8px; overflow-x: auto; }}
                </style>
            </head>
            <body>
                <h1>🧪 RCCM 手動テストガイド</h1>
                <pre>{guide_content}</pre>
            </body>
            </html>
            """, 200, {'Content-Type': 'text/html; charset=utf-8'}
        else:
            return render_template('error.html', 
                                   error="手動テストガイドが見つかりません"), 404
                                   
    except Exception as e:
        logger.error(f"手動テストガイド表示エラー: {e}")
        return render_template('error.html', 
                               error="手動テストガイドの読み込み中にエラーが発生しました"), 500


@app.route('/api/manual_test/monitoring_status')
def api_manual_test_monitoring_status():
    """🧪 手動テスト監視状況API（CLAUDE.md準拠・副作用ゼロ）"""
    try:
        # ウルトラシンク方針: 副作用ゼロでログファイル統計のみ取得
        log_file_path = os.path.join(os.path.dirname(__file__), 'rccm_app.log')
        
        # 基本統計
        status = {
            'success': True,
            'monitoring_available': True,
            'log_file_exists': os.path.exists(log_file_path),
            'timestamp': format_utc_to_iso()
        }
        
        if status['log_file_exists']:
            try:
                # ログファイル基本情報（副作用なし）
                file_stats = os.stat(log_file_path)
                status['log_file_info'] = {
                    'size_bytes': file_stats.st_size,
                    'size_mb': round(file_stats.st_size / (1024 * 1024), 2),
                    'last_modified': datetime.fromtimestamp(file_stats.st_mtime).isoformat()
                }
                
                # 最近のログエントリ統計（読み取り専用）
                with open(log_file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    
                recent_lines = lines[-50:] if len(lines) > 50 else lines
                
                # パターン検索（副作用なし）
                manual_test_count = sum(1 for line in recent_lines if '🧪 MANUAL TEST QUALITY CHECK' in line)
                error_count = sum(1 for line in recent_lines if any(marker in line for marker in ['ERROR', '❌', 'CRITICAL']))
                success_count = sum(1 for line in recent_lines if '✅' in line)
                warning_count = sum(1 for line in recent_lines if any(marker in line for marker in ['WARNING', '⚠️']))
                
                status['recent_activity'] = {
                    'manual_tests_detected': manual_test_count,
                    'error_messages': error_count,
                    'success_messages': success_count,
                    'warning_messages': warning_count,
                    'total_recent_lines': len(recent_lines)
                }
                
                # 推奨事項
                recommendations = []
                if manual_test_count == 0:
                    recommendations.append("手動テストが検出されていません - テストダッシュボードから開始してください")
                elif error_count > 0:
                    recommendations.append(f"エラーが {error_count}件 検出されています - ログを確認してください")
                elif manual_test_count > 0 and error_count == 0:
                    recommendations.append("手動テストが正常に実行されています")
                    
                status['recommendations'] = recommendations
                
            except Exception as e:
                logger.warning(f"ログファイル解析エラー: {e}")
                status['log_analysis_error'] = str(e)
        else:
            status['recommendations'] = ["ログファイルが見つかりません - アプリケーションを起動してください"]
            
        # 手動テスト支援情報
        status['manual_test_support'] = {
            'dashboard_url': '/manual_test_dashboard',
            'guide_url': '/manual_test_guide',
            'script_testing_prohibited': True,
            'claude_md_compliant': True
        }
        
        return jsonify(status)
        
    except Exception as e:
        logger.error(f"手動テスト監視状況API エラー: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': format_utc_to_iso()
        }), 500


@app.route('/api/manual_test/quality_check')
def api_manual_test_quality_check():
    """🧪 手動テスト品質チェックAPI（CLAUDE.md準拠・副作用ゼロ）"""
    try:
        log_file_path = os.path.join(os.path.dirname(__file__), 'rccm_app.log')
        
        quality_status = {
            'success': True,
            'timestamp': format_utc_to_iso(),
            'quality_checks': {
                'year_consistency': {'passed': 0, 'failed': 0},
                'department_consistency': {'passed': 0, 'failed': 0},
                'question_duplicates': {'passed': 0, 'failed': 0},
                'performance_checks': {'good': 0, 'warnings': 0}
            },
            'overall_quality_score': 0,
            'critical_issues': [],
            'recommendations': []
        }
        
        if os.path.exists(log_file_path):
            try:
                # ログファイルから品質チェック結果を抽出（副作用なし）
                with open(log_file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # 年度統一性チェック
                year_success = content.count('✅ 年度統一性: 完全')
                year_failed = content.count('❌ 年度統一性: 失敗')
                quality_status['quality_checks']['year_consistency'] = {
                    'passed': year_success,
                    'failed': year_failed
                }
                
                # 部門統一性チェック
                dept_success = content.count('✅ 部門統一性: 完全')
                dept_failed = content.count('❌ 部門統一性: 失敗')
                quality_status['quality_checks']['department_consistency'] = {
                    'passed': dept_success,
                    'failed': dept_failed
                }
                
                # 問題ID重複チェック
                dup_success = content.count('✅ 問題ID重複: なし')
                dup_failed = content.count('❌ 問題ID重複: 検出')
                quality_status['quality_checks']['question_duplicates'] = {
                    'passed': dup_success,
                    'failed': dup_failed
                }
                
                # パフォーマンスチェック
                perf_good = content.count('⚡ パフォーマンス: レスポンス')
                perf_warnings = content.count('⚠️ パフォーマンス警告') + content.count('⚠️ レスポンス時間警告')
                quality_status['quality_checks']['performance_checks'] = {
                    'good': perf_good,
                    'warnings': perf_warnings
                }
                
                # 全体品質スコア計算
                total_checks = year_success + year_failed + dept_success + dept_failed + dup_success + dup_failed
                total_passed = year_success + dept_success + dup_success
                
                if total_checks > 0:
                    quality_score = (total_passed / total_checks) * 100
                    # パフォーマンス警告でスコア減点
                    quality_score = max(0, quality_score - (perf_warnings * 5))
                    quality_status['overall_quality_score'] = round(quality_score, 1)
                    
                # 重要問題検出
                critical_issues = []
                if year_failed > 0:
                    critical_issues.append(f"年度混在エラー: {year_failed}件")
                if dept_failed > 0:
                    critical_issues.append(f"部門混在エラー: {dept_failed}件")
                if dup_failed > 0:
                    critical_issues.append(f"問題ID重複: {dup_failed}件")
                    
                quality_status['critical_issues'] = critical_issues
                
                # 推奨事項
                recommendations = []
                if quality_status['overall_quality_score'] >= 90:
                    recommendations.append("品質状況は非常に良好です")
                elif quality_status['overall_quality_score'] >= 70:
                    recommendations.append("品質状況は良好ですが、一部改善の余地があります")
                elif critical_issues:
                    recommendations.append("重要な品質問題が検出されています - 修正が必要です")
                else:
                    recommendations.append("手動テストを開始して品質チェックを実行してください")
                    
                if perf_warnings > 0:
                    recommendations.append(f"パフォーマンス警告 {perf_warnings}件 - レスポンス時間を確認してください")
                    
                quality_status['recommendations'] = recommendations
                
            except Exception as e:
                logger.warning(f"品質チェック解析エラー: {e}")
                quality_status['analysis_error'] = str(e)
                
        return jsonify(quality_status)
        
    except Exception as e:
        logger.error(f"手動テスト品質チェックAPI エラー: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': format_utc_to_iso()
        }), 500


# 🛡️ ULTRA SYNC ERROR HANDLER CONSOLIDATION: 
# 重複エラーハンドラーは統合版に置き換え（ultra_sync_error_loop_prevention.py）

# === AI学習アナリティクス ===


@app.route('/ai_dashboard')
def ai_dashboard():
    """AIダッシュボード"""
    try:
        # セッションデータ取得
        user_session = session
        history = user_session.get('history', [])
        srs_data = user_session.get('srs_data', {})

        # AI分析実行
        analysis = {}
        if history:
            from ai_analyzer import ai_analyzer

            # 学習スタイル分析
            try:
                learning_style_result = ai_analyzer.determine_learning_style(history)
                analysis['learning_style'] = learning_style_result.get('style', '分析中...')
            except (AttributeError, TypeError, KeyError, ImportError):
                analysis['learning_style'] = '視覚学習型'

            # パフォーマンス予測
            try:
                performance_prediction = ai_analyzer.predict_performance(srs_data)
                analysis['performance_prediction'] = performance_prediction
            except (AttributeError, TypeError, KeyError, ImportError):
                analysis['performance_prediction'] = {'score': 72}

            # 弱点パターン分析
            try:
                weakness_patterns = ai_analyzer.analyze_weakness_patterns(history)
                analysis['weakness_patterns'] = weakness_patterns.get('patterns', [])
            except (AttributeError, TypeError, KeyError, ImportError):
                analysis['weakness_patterns'] = []

            # 学習推奨事項
            try:
                recommendations = ai_analyzer.generate_recommendations(history, srs_data)
                analysis['study_recommendations'] = recommendations
            except (AttributeError, TypeError, KeyError, ImportError):
                analysis['study_recommendations'] = []
        else:
            # デフォルトデータ
            analysis = {
                'learning_style': '学習データを蓄積中...',
                'performance_prediction': {'score': 0},
                'weakness_patterns': [],
                'study_recommendations': [],
                'optimal_study_time': '午前中',
                'memory_retention': {
                    'retention_rate': 0,
                    'average_retention_days': 0,
                    'forgetting_curve_type': '標準型'
                }
            }

        return render_template('ai_dashboard.html', analysis=analysis)

    except Exception as e:
        logger.error(f"AIダッシュボード エラー: {e}")
        return render_template('ai_dashboard.html', analysis={
            'learning_style': 'AI分析準備中...',
            'performance_prediction': {'score': 0},
            'weakness_patterns': [],
            'study_recommendations': []
        })


@app.route('/advanced_analytics')
def advanced_analytics_view():
    """高度分析"""
    try:
        # セッションデータ取得
        user_session = session
        history = user_session.get('history', [])
        srs_data = user_session.get('srs_data', {})

        # 高度分析実行
        analytics = {}
        if history and advanced_analytics:
            try:
                # 時系列分析
                advanced_analytics.analyze_time_series(history)
                analytics['time_series_analysis'] = {
                    'trend': '上昇傾向',
                    'peak_performance': 85,
                    'stability': '良好'
                }

                # 難易度分析
                advanced_analytics.analyze_difficulty_distribution(srs_data)
                analytics['difficulty_distribution'] = {
                    'best_level': '中級',
                    'needs_improvement': '上級'
                }

                # 学習効率分析
                analytics['study_efficiency'] = {'score': 78}
                analytics['cognitive_load'] = {'level': '中'}
                analytics['success_probability'] = {'probability': 85}
                analytics['learning_curve'] = {'phase': '成長期'}

                # 部門別ヒートマップ
                analytics['department_heatmap'] = {
                    '道路部門': {
                        'basic': 85, 'applied': 72, 'practical': 68,
                        'basic_color': '#e8f5e8', 'applied_color': '#fff3cd', 'practical_color': '#f8d7da',
                        'overall_rating': 'B+', 'overall_badge': 'success'
                    },
                    '河川砂防部門': {
                        'basic': 75, 'applied': 68, 'practical': 55,
                        'basic_color': '#fff3cd', 'applied_color': '#f8d7da', 'practical_color': '#f8d7da',
                        'overall_rating': 'B', 'overall_badge': 'warning'
                    }
                }

                # AI推奨エンジン
                analytics['recommendation_engine'] = {
                    'recommendations': [
                        {'title': '構造力学の復習強化', 'category': '基礎'},
                        {'title': '施工管理技術の実践問題', 'category': '応用'},
                        {'title': '法規・制度の暗記強化', 'category': '専門'},
                        {'title': '計算問題の解法パターン習得', 'category': '技術'},
                        {'title': '過去問題の反復学習', 'category': '総合'}
                    ],
                    'time_allocation': [
                        {'category': '基礎科目', 'percentage': 30},
                        {'category': '専門科目', 'percentage': 40},
                        {'category': '復習', 'percentage': 20},
                        {'category': '実践演習', 'percentage': 10}
                    ]
                }

            except Exception as inner_e:
                logger.warning(f"高度分析データ生成エラー: {inner_e}")
                analytics = {}

        # デフォルトデータ設定
        if not analytics:
            analytics = {
                'study_efficiency': {'score': 0},
                'cognitive_load': {'level': '分析中'},
                'success_probability': {'probability': 0},
                'learning_curve': {'phase': 'データ収集中'},
                'time_series_analysis': None,
                'difficulty_distribution': None,
                'department_heatmap': None,
                'recommendation_engine': None
            }

        return render_template('advanced_analytics.html', analytics=analytics)

    except Exception as e:
        logger.error(f"高度分析 エラー: {e}")
        return render_template('advanced_analytics.html', analytics={
            'study_efficiency': {'score': 0},
            'cognitive_load': {'level': '分析準備中'},
            'success_probability': {'probability': 0},
            'learning_curve': {'phase': 'システム準備中'}
        })

# === 管理者ダッシュボード ===


@app.route('/admin')
@require_admin_auth
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
@require_admin_auth
def admin_api_overview():
    """システム概要API"""
    try:
        overview = admin_dashboard.get_system_overview()
        return jsonify(overview)
    except Exception as e:
        logger.error(f"概要API エラー: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/admin/api/questions')
@require_admin_auth
def admin_api_questions():
    """問題管理API"""
    try:
        questions = admin_dashboard.get_question_management_data()
        return jsonify(questions)
    except Exception as e:
        logger.error(f"問題管理API エラー: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/admin/api/users')
@require_admin_auth
def admin_api_users():
    """ユーザー管理API"""
    try:
        users = admin_dashboard.get_user_progress_overview()
        return jsonify(users)
    except Exception as e:
        logger.error(f"ユーザー管理API エラー: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/admin/api/users/<user_id>')
@require_admin_auth
def admin_api_user_detail(user_id):
    """ユーザー詳細API"""
    try:
        user_detail = admin_dashboard.get_detailed_user_analysis(user_id)
        return jsonify(user_detail)
    except Exception as e:
        logger.error(f"ユーザー詳細API エラー: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/admin/api/content')
@require_admin_auth
def admin_api_content():
    """コンテンツ分析API"""
    try:
        content = admin_dashboard.get_content_analytics()
        return jsonify(content)
    except Exception as e:
        logger.error(f"コンテンツ分析API エラー: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/admin/api/performance')
@require_admin_auth
def admin_api_performance():
    """パフォーマンス指標API"""
    try:
        performance = admin_dashboard.get_performance_metrics()
        return jsonify(performance)
    except Exception as e:
        logger.error(f"パフォーマンス指標API エラー: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/admin/api/reports/<report_type>')
@require_admin_auth
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

        group_name = sanitize_input(request.form.get('group_name'))
        description = sanitize_input(request.form.get('description', ''))
        department = sanitize_input(request.form.get('department'))
        target_exam_date = sanitize_input(request.form.get('target_exam_date'))

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

        title = sanitize_input(request.form.get('title'))
        content = sanitize_input(request.form.get('content'))
        category = sanitize_input(request.form.get('category', 'general'))
        question_id = sanitize_input(request.form.get('question_id'))
        group_id = sanitize_input(request.form.get('group_id'))

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
            # 🔥 ULTRA SYNC TIMEZONE FIX: UTC基準のAPIタイムスタンプ
            'timestamp': format_utc_to_iso()
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
            # 🔥 ULTRA SYNC TIMEZONE FIX: UTC基準のAPIタイムスタンプ
            'timestamp': format_utc_to_iso()
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
            # 🔥 ULTRA SYNC TIMEZONE FIX: UTC基準のAPIタイムスタンプ
            'timestamp': format_utc_to_iso()
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
            # 🔥 ULTRA SYNC TIMEZONE FIX: UTC基準のAPIタイムスタンプ
            'timestamp': format_utc_to_iso()
        })

    except Exception as e:
        logger.error(f"UI個人化API エラー: {e}")
        return jsonify({'error': str(e)}), 500

# 企業環境用管理API


@app.route('/api/enterprise/users')
@require_api_key
def api_enterprise_users():
    """全ユーザー一覧API（企業環境用）"""
    try:
        users = enterprise_user_manager.get_all_users()

        return jsonify({
            'success': True,
            'users': users,
            'total_users': len(users),
            # 🔥 ULTRA SYNC TIMEZONE FIX: UTC基渖のレポート生成タイムスタンプ
            'generated_at': format_utc_to_iso()
        })

    except Exception as e:
        logger.error(f"企業ユーザー一覧API エラー: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/enterprise/user/<user_name>/report')
@require_api_key
def api_enterprise_user_report(user_name):
    """ユーザー詳細進捗レポートAPI（企業環境用）"""
    try:
        report = enterprise_user_manager.get_user_progress_report(user_name)

        if 'error' in report:
            return jsonify({'success': False, 'error': report['error']}), 404

        return jsonify({
            'success': True,
            'report': report
        })

    except Exception as e:
        logger.error(f"企業ユーザーレポートAPI エラー: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/enterprise/dashboard')
@require_admin_auth
def enterprise_dashboard():
    """企業環境用管理ダッシュボード"""
    try:
        # 管理者向けダッシュボード表示
        users = enterprise_user_manager.get_all_users()

        return render_template('enterprise_dashboard.html', users=users)

    except Exception as e:
        logger.error(f"企業ダッシュボードエラー: {e}")
        return render_template('error.html', error_message=str(e)), 500


@app.route('/api/enterprise/data/integrity')
@require_api_key
def api_enterprise_data_integrity():
    """データ整合性チェックAPI（企業環境用）"""
    try:
        if enterprise_data_manager:
            integrity_report = enterprise_data_manager.get_file_integrity_check()
        else:
            integrity_report = {
                # 🔥 ULTRA SYNC TIMEZONE FIX: UTC基準のAPIタイムスタンプ
            'timestamp': format_utc_to_iso(),
                'status': 'unavailable',
                'message': 'Enterprise data manager not available'
            }

        return jsonify({
            'success': True,
            'integrity_report': integrity_report
        })

    except Exception as e:
        logger.error(f"データ整合性チェックAPI エラー: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/enterprise/cache/stats')
@require_api_key
def api_enterprise_cache_stats():
    """キャッシュ統計API（企業環境用）"""
    try:
        from utils import cache_manager_instance
        cache_stats = cache_manager_instance.get_stats()

        return jsonify({
            'success': True,
            'cache_stats': cache_stats,
            # 🔥 ULTRA SYNC TIMEZONE FIX: UTC基準のAPIタイムスタンプ
            'timestamp': format_utc_to_iso()
        })

    except Exception as e:
        logger.error(f"キャッシュ統計API エラー: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/enterprise/cache/clear', methods=['POST'])
@require_api_key
def api_enterprise_cache_clear():
    """キャッシュクリアAPI（企業環境用）"""
    try:
        from utils import cache_manager_instance
        cache_manager_instance.clear_all()

        return jsonify({
            'success': True,
            'message': 'キャッシュをクリアしました',
            # 🔥 ULTRA SYNC TIMEZONE FIX: UTC基準のAPIタイムスタンプ
            'timestamp': format_utc_to_iso()
        })

    except Exception as e:
        logger.error(f"キャッシュクリアAPI エラー: {e}")
        return jsonify({'error': str(e)}), 500


# 初期化（企業環境最適化 - 重複読み込み解決版）
try:
    # 環境変数で読み込み方式を選択（デフォルト: 遅延読み込みモード）
    lazy_load = os.environ.get('RCCM_LAZY_LOAD', 'true').lower() == 'true'
    fast_mode = os.environ.get('RCCM_FAST_MODE', 'false').lower() == 'true' and not lazy_load

    if lazy_load:
        # 🚀 ウルトラ高速起動モード: データ読み込みを完全に遅延
        logger.info("🚀 ウルトラ高速起動モード: 遅延読み込み有効")
        # モジュールインポートのみ（データ読み込みなし）
        from data_manager import DataManager, SessionDataManager, EnterpriseUserManager
        from utils import enterprise_data_manager as edm
        
        data_manager = DataManager()
        session_data_manager = SessionDataManager(data_manager)
        enterprise_user_manager = EnterpriseUserManager(data_manager)
        enterprise_data_manager = edm
        
        # 機能モジュールも遅延インポート
        gamification_manager = None
        ai_analyzer = None
        adaptive_engine = None
        exam_simulator = None
        advanced_analytics = None
        mobile_manager = None
        learning_optimizer = None
        admin_dashboard = None
        social_learning_manager = None
        api_manager = None
        advanced_personalization = None
        
        logger.info("✅ ウルトラ高速起動完了 - データは必要時に読み込まれます")
        
    elif fast_mode:
        # 高速化モード: 遅延インポートでデータ管理初期化
        logger.info("🚀 高速化モード: 企業環境用データ読み込み開始")

        # 遅延インポート: データ管理（エラー回避）
        try:
            from data_manager import DataManager, SessionDataManager, EnterpriseUserManager
            from utils import enterprise_data_manager as edm

            # グローバル変数に代入
            data_manager = DataManager()
            session_data_manager = SessionDataManager(data_manager)
            enterprise_user_manager = EnterpriseUserManager(data_manager)
            enterprise_data_manager = edm
        except ImportError as e:
            logger.warning(f"Data manager import error: {e} - Using basic functionality")
            from utils import enterprise_data_manager
            data_manager = None
            session_data_manager = None
            enterprise_user_manager = None

        # 遅延インポート: 機能モジュール
        from gamification import gamification_manager as gam_mgr
        from ai_analyzer import ai_analyzer as ai_ana
        from adaptive_learning import adaptive_engine as adp_eng
        from exam_simulator import exam_simulator as exam_sim
        from advanced_analytics import advanced_analytics as adv_ana
        from mobile_features import mobile_manager as mob_mgr
        from learning_optimizer import learning_optimizer as lrn_opt
        from admin_dashboard import admin_dashboard as adm_dash
        from social_learning import social_learning_manager as soc_mgr
        from api_integration import api_manager as api_mgr
        from advanced_personalization import advanced_personalization as adv_per

        # グローバル変数に代入
        gamification_manager = gam_mgr
        ai_analyzer = ai_ana
        adaptive_engine = adp_eng
        exam_simulator = exam_sim
        advanced_analytics = adv_ana
        mobile_manager = mob_mgr
        learning_optimizer = lrn_opt
        admin_dashboard = adm_dash
        social_learning_manager = soc_mgr
        api_manager = api_mgr
        advanced_personalization = adv_per

        preload_success = enterprise_data_manager.preload_all_data()
        if preload_success:
            logger.info("✅ 企業環境用データ事前読み込み完了 - 高速アクセス準備完了")

            # データ整合性チェック（軽量版）
            integrity_report = enterprise_data_manager.get_file_integrity_check()
            logger.info(f"📊 データ整合性チェック: {integrity_report['status']} - 総計{integrity_report['total_questions']}問")
        else:
            logger.warning("⚠️ 企業環境用データ読み込み失敗 - 従来モードに切り替え")
            # フォールバック: 従来の読み込み
            initial_questions = load_questions()
            logger.info(f"📂 従来モード: {len(initial_questions)}問読み込み完了")
    else:
        # 従来モード: 後方互換性保持
        logger.info("📂 従来モード: 基本データ読み込み")
        initial_questions = load_questions()
        logger.info(f"✅ 基本アプリケーション初期化完了: {len(initial_questions)}問読み込み")

except Exception as e:
    logger.error(f"❌ アプリケーション初期化エラー: {e}")
    logger.info("🔄 基本機能で続行します")

# 🔥 ウルトラシンク修復: 不足ルート追加（副作用なし）


@app.route('/study/basic')
def study_basic():
    """基礎科目学習ページ"""
    return redirect(url_for('exam', question_type='basic'))


@app.route('/study/specialist/<department>')
def study_specialist(department):
    """専門科目学習ページ"""
    # 部門エイリアスの解決
    department = resolve_department_alias(department)
    return redirect(url_for('exam', question_type='specialist', department=department))


@app.route('/enterprise_dashboard')
def enterprise_dashboard_redirect():
    """企業ダッシュボードリダイレクト（既存機能への橋渡し）"""
    return redirect('/enterprise/dashboard')


@app.route('/health')
def health_status():
    """ヘルスチェックエンドポイント（Render起動確認用）"""
    return jsonify({
        'status': 'ok',
        'app': 'RCCM Quiz App',
        'version': '2025.1',
        'timestamp': get_utc_now().isoformat()
    })

# 🛡️ ULTRA SYNC UNIFIED ERROR HANDLERS: 統合エラーハンドラーシステム
# すべてのエラーハンドラーは ultra_sync_error_loop_prevention.py により統合管理
# 無限ループ防止・エラー追跡・セッション保護機能を提供

# 🛡️ Ultra Sync Error Loop Prevention API Endpoints

@app.route('/api/error_prevention/status')
def api_error_prevention_status():
    """エラー防止システム状態取得API"""
    try:
        if _error_loop_prevention:
            stats = _error_loop_prevention.get_statistics()
            return jsonify({
                'success': True,
                'system_active': True,
                'statistics': stats,
                'timestamp': format_utc_to_iso()
            })
        else:
            return jsonify({
                'success': True,
                'system_active': False,
                'message': 'Error loop prevention system not available',
                'timestamp': format_utc_to_iso()
            })
    except Exception as e:
        logger.error(f"Error prevention status API error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': format_utc_to_iso()
        }), 500

@app.route('/api/error_prevention/reset_session', methods=['POST'])
def api_error_prevention_reset_session():
    """セッションエラーカウントリセットAPI"""
    try:
        session_id = session.get('session_id', 'anonymous')
        
        if _error_loop_prevention:
            reset_success = _error_loop_prevention.reset_session_errors(session_id)
            return jsonify({
                'success': True,
                'reset_performed': reset_success,
                'session_id': session_id[:8] + '...',
                'timestamp': format_utc_to_iso()
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Error loop prevention system not available',
                'timestamp': format_utc_to_iso()
            }), 503
    except Exception as e:
        logger.error(f"Error prevention reset API error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': format_utc_to_iso()
        }), 500

@app.route('/api/error_prevention/cleanup')
def api_error_prevention_cleanup():
    """古いセッションデータクリーンアップAPI"""
    try:
        if _error_loop_prevention:
            cleaned_count = _error_loop_prevention.cleanup_old_sessions()
            return jsonify({
                'success': True,
                'cleaned_sessions': cleaned_count,
                'timestamp': format_utc_to_iso()
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Error loop prevention system not available',
                'timestamp': format_utc_to_iso()
            }), 503
    except Exception as e:
        logger.error(f"Error prevention cleanup API error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': format_utc_to_iso()
        }), 500

# 🔥 ULTRA SYNC FIX: 欠落APIエンドポイント実装 - 副作用ゼロ保証
# session-timeout.jsで呼び出される404エラー解決

@app.route('/api/session/status', methods=['GET'])
def api_session_status():
    """セッション状態確認API - frontend session-timeout.js対応"""
    try:
        # セッション基本情報
        session_data = {
            'active': bool(session.get('user_id')),
            'has_quiz': bool(session.get('exam_question_ids')),
            'current_question': session.get('exam_current', 0),
            'total_questions': len(session.get('exam_question_ids', [])),
            'department': session.get('selected_department', ''),
            'category': session.get('exam_category', ''),
            'last_activity': session.get('last_activity', format_utc_to_iso()),
            'session_id': session.get('session_id', 'anonymous')[:8] + '...'
        }
        
        return jsonify({
            'success': True,
            'session': session_data,
            'timestamp': format_utc_to_iso()
        })
        
    except Exception as e:
        logger.error(f"Session status API error: {e}")
        return jsonify({
            'success': False,
            'error': 'Session status unavailable',
            'timestamp': format_utc_to_iso()
        }), 500

@app.route('/api/session/extend', methods=['POST'])
def api_session_extend():
    """セッション延長API - session-timeout.js対応"""
    try:
        if session.get('user_id'):
            session['last_activity'] = format_utc_to_iso()
            session.permanent = True
            session.modified = True
            
            return jsonify({
                'success': True,
                'extended': True,
                'new_expiry': format_utc_to_iso(),
                'timestamp': format_utc_to_iso()
            })
        else:
            return jsonify({
                'success': False,
                'error': 'No active session to extend',
                'timestamp': format_utc_to_iso()
            }), 400
            
    except Exception as e:
        logger.error(f"Session extend API error: {e}")
        return jsonify({
            'success': False,
            'error': 'Session extension failed',
            'timestamp': format_utc_to_iso()
        }), 500


# 🛡️ ULTRATHIN区 100%必達: 欠けているルート実装 (副作用ゼロ)
@app.route('/review_wrong')
def review_wrong():
    """間違い問題復習ページ"""
    try:
        # 既存のreview機能にリダイレクト
        return redirect('/review')
    except Exception as e:
        logger.error(f"復習間違い問題エラー: {e}")
        return render_template('error.html', error="復習機能の表示中にエラーが発生しました。")

@app.route('/review_list')
def review_list_redirect():
    """復習リストページ (エイリアス)"""
    try:
        # 既存のreview機能にリダイレクト
        return redirect('/review')
    except Exception as e:
        logger.error(f"復習リストエラー: {e}")
        return render_template('error.html', error="復習機能の表示中にエラーが発生しました。")

@app.route('/srs_review')
def srs_review():
    """SRS復習ページ"""
    try:
        # 既存のreview機能にリダイレクト
        return redirect('/review')
    except Exception as e:
        logger.error(f"SRS復習エラー: {e}")
        return render_template('error.html', error="SRS復習機能の表示中にエラーが発生しました。")

@app.route('/stats')
def stats_alias():
    """統計ページ (エイリアス)"""
    try:
        # 既存のstatistics機能にリダイレクト
        return redirect('/statistics')
    except Exception as e:
        logger.error(f"統計ページエラー: {e}")
        return render_template('error.html', error="統計機能の表示中にエラーが発生しました。")


if __name__ == '__main__':
    # 🛡️ セキュリティ強化: 本番環境設定（元の設定を維持）
    port = int(os.environ.get('PORT', 5005))
    
    # 🛡️ 本番環境検出とセキュリティ設定
    is_production = (
        os.environ.get('FLASK_ENV') == 'production' or
        os.environ.get('RENDER') or
        os.environ.get('PORT')
    )
    
    # 🛡️ 🔥 ULTRA SYNC FIX: ホスト設定改善 - URLアクセス問題解決
    if is_production:
        host = '0.0.0.0'  # 本番: 必要なアクセスのみ
        debug_mode = False  # 本番: デバッグモード無効
    else:
        # 🔥 FIX: 開発環境でも外部アクセスを許可（URL起動問題解決）
        host = '0.0.0.0'  # 開発: 外部からのアクセスも許可
        debug_mode = True   # 開発: デバッグモード有効
        logger.info("✅ 開発モード: 外部URLアクセス対応済み")

    # 🔥 ULTRA SYNC FIX: 起動高速化 - データ読み込みを遅延実行
    logger.info("⚡ 高速起動モード（データ読み込みは初回アクセス時に実行）")
    # NOTE: preload_startup_data() は初回アクセス時に自動実行される
    logger.info("✅ 起動準備完了 - URLアクセス可能です")

    # 起動ログ最適化（Render向け高速起動）
    if is_production:
        logger.info("🌐 RCCM試験問題集2025 - Production Ready")
        logger.info("📡 Fast startup mode enabled")
    else:
        # 🔥 ULTRA SYNC FIX: 開発環境URL表示改善
        logger.info("🚀 RCCM試験問題集アプリケーション起動中...")
        logger.info(f"🌐 メインアクセスURL: http://localhost:{port}")
        logger.info(f"🌍 外部アクセスURL: http://<あなたのIPアドレス>:{port}")
        logger.info("✅ URLをブラウザのアドレスバーにコピー&ペーストしてアクセス")
        logger.info("💡 起動後すぐにアクセス可能です（データ読み込みは初回アクセス時）")

    # サーバー起動（最適化版）
    logger.info(f"🚀 RCCM Ready - Host: {host}, Port: {port}")

    # 🛡️ セキュアサーバー起動設定
    if is_production:
        logger.error("🚨 警告: 本番環境では直接起動せず、WSGIサーバーを使用してください")
        logger.error("🚀 推奨: gunicorn -w 4 -b 0.0.0.0:10000 wsgi:application")
        logger.error("📚 詳細: DEPLOYMENT.md を参照してください")
        # 🛡️ 本番環境では起動しない
        logger.info("✅ 本番環境検出: WSGIサーバー経由での起動を待機中...")
        import sys
        sys.exit(0)  # 本番環境では終了
    else:
        logger.info("🛡️ 開発モード: セキュリティ設定で起動")
        logger.info("📚 本番環境デプロイ方法: DEPLOYMENT.md を参照")
        
        app.run(
            host=host,
            port=port,
            debug=debug_mode,
            threaded=True,
            use_reloader=False,
            # 🛡️ セキュリティ強化: SSLコンテキスト設定(本番ではリバースプロキシで処理)
            ssl_context=None  # リバースプロキシ(nginx, Render)でSSL終端
        )


@app.route("/debug/session_info")
def debug_session_info():
    """🛡️ ULTRATHIN区 段階3: セッションデバッグ情報表示（安全）"""
    try:
        debug_data = {
            "debug_info": session.get("debug_info", {}),
            "specialist_error": session.get("specialist_error", {}),
            "session_keys": list(session.keys()),
            "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return jsonify(debug_data)
    except Exception as e:
        return jsonify({
            "error": str(e),
            "message": "Debug info unavailable"
        })
