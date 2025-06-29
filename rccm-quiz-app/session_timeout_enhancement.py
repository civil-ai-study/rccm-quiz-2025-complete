#!/usr/bin/env python3
"""
RCCM試験問題集アプリ - セッションタイムアウト強化システム
ユーザー体験を向上させる包括的なセッション管理機能
"""

import json
import os
from datetime import datetime, timedelta, timezone
from flask import session, request, jsonify
import logging
import pytz

# 🔥 WORLD STANDARD: UTC統一処理のためのユーティリティ関数
def get_utc_now():
    """UTC timezone-aware な現在時刻を取得（世界標準）"""
    return datetime.now(timezone.utc)

def parse_iso_to_utc(iso_string):
    """ISO文字列をUTC timezone-awareなdatetimeに変換（世界標準）"""
    try:
        dt = datetime.fromisoformat(iso_string)
        if dt.tzinfo is None:
            # naive datetime の場合はUTCとして扱う
            dt = dt.replace(tzinfo=timezone.utc)
        else:
            # timezone-aware の場合はUTCに変換
            dt = dt.astimezone(timezone.utc)
        return dt
    except (ValueError, TypeError):
        return get_utc_now()

def datetime_to_utc_iso(dt):
    """datetime を UTC ISO文字列に変換（世界標準）"""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).isoformat()

logger = logging.getLogger(__name__)

class SessionTimeoutManager:
    """セッションタイムアウト管理システム"""
    
    def __init__(self, app=None):
        self.app = app
        self.session_lifetime = 3600  # 1時間 (デフォルト)
        self.warning_threshold = 300   # 5分前に警告
        self.auto_save_interval = 60   # 1分ごとに自動保存
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Flaskアプリケーション初期化"""
        self.app = app
        
        # 設定値の取得
        self.session_lifetime = app.config.get('PERMANENT_SESSION_LIFETIME', 3600)
        self.warning_threshold = app.config.get('SESSION_WARNING_THRESHOLD', 300)
        self.auto_save_interval = app.config.get('SESSION_AUTO_SAVE_INTERVAL', 60)
        
        # セッション前後処理の登録
        app.before_request(self.before_request)
        app.after_request(self.after_request)
        
        # セッション管理エンドポイントの追加
        self._register_endpoints()
        
        logger.info(f"セッションタイムアウトマネージャー初期化完了: 有効期限={self.session_lifetime}秒")
    
    def _register_endpoints(self):
        """セッション管理エンドポイントの登録"""
        
        @self.app.route('/api/session/status')
        def session_status():
            """セッション状態確認API"""
            try:
                status = self.get_session_status()
                return jsonify(status)
            except Exception as e:
                logger.error(f"セッション状態確認エラー: {e}")
                return jsonify({'error': 'セッション状態の確認に失敗しました'}), 500
        
        @self.app.route('/api/session/extend', methods=['POST'])
        def extend_session():
            """セッション延長API"""
            try:
                self.extend_session_lifetime()
                return jsonify({
                    'success': True,
                    'message': 'セッションを延長しました',
                    'new_status': self.get_session_status()
                })
            except Exception as e:
                logger.error(f"セッション延長エラー: {e}")
                return jsonify({'error': 'セッション延長に失敗しました'}), 500
        
        @self.app.route('/api/session/save', methods=['POST'])
        def save_session():
            """セッション手動保存API"""
            try:
                backup_id = self.create_session_backup()
                return jsonify({
                    'success': True,
                    'backup_id': backup_id,
                    'message': 'セッションを保存しました'
                })
            except Exception as e:
                logger.error(f"セッション保存エラー: {e}")
                return jsonify({'error': 'セッション保存に失敗しました'}), 500
        
        @self.app.route('/api/session/restore', methods=['POST'])
        def restore_session():
            """セッション復元API"""
            try:
                data = request.get_json()
                backup_id = data.get('backup_id')
                
                if not backup_id:
                    return jsonify({'error': 'バックアップIDが指定されていません'}), 400
                
                success = self.restore_session_backup(backup_id)
                if success:
                    return jsonify({
                        'success': True,
                        'message': 'セッションを復元しました'
                    })
                else:
                    return jsonify({'error': 'セッション復元に失敗しました'}), 400
                    
            except Exception as e:
                logger.error(f"セッション復元エラー: {e}")
                return jsonify({'error': 'セッション復元に失敗しました'}), 500
    
    def before_request(self):
        """リクエスト前処理 - セッション状態チェック"""
        # 静的ファイルやAPIエンドポイントはスキップ
        if request.endpoint and (
            request.endpoint.startswith('static') or 
            request.endpoint.startswith('api.session')
        ):
            return
        
        # セッション活動時間を更新
        self.update_session_activity()
        
        # タイムアウトチェック
        if self.is_session_expired():
            self.handle_session_expiration()
    
    def after_request(self, response):
        """リクエスト後処理 - セッション状態更新"""
        # セッション状態をレスポンスヘッダーに追加
        try:
            status = self.get_session_status()
            response.headers['X-Session-Status'] = json.dumps(status)
        except Exception as e:
            logger.warning(f"セッション状態ヘッダー追加失敗: {e}")
        
        return response
    
    def update_session_activity(self):
        """セッション活動時間の更新（世界標準UTC統一）"""
        current_time = get_utc_now()  # 🔥 WORLD STANDARD: UTC timezone-aware
        session['last_activity'] = datetime_to_utc_iso(current_time)  # 🔥 WORLD STANDARD: UTC ISO
        session['total_requests'] = session.get('total_requests', 0) + 1
        
        # 定期的な自動保存
        last_auto_save = session.get('last_auto_save')
        if not last_auto_save or self._time_diff_seconds(last_auto_save, current_time) >= self.auto_save_interval:
            self.create_session_backup(auto_save=True)
            session['last_auto_save'] = datetime_to_utc_iso(current_time)  # 🔥 WORLD STANDARD: UTC ISO
    
    def get_session_status(self):
        """セッション状態の取得（世界標準UTC統一）"""
        current_time = get_utc_now()  # 🔥 WORLD STANDARD: UTC timezone-aware
        last_activity = session.get('last_activity')
        
        if not last_activity:
            return {
                'status': 'new',
                'remaining_time': self.session_lifetime,
                'warning': False,
                'expires_at': None
            }
        
        last_activity_time = parse_iso_to_utc(last_activity)  # 🔥 WORLD STANDARD: UTC統一解析
        elapsed_time = (current_time - last_activity_time).total_seconds()
        remaining_time = max(0, self.session_lifetime - elapsed_time)
        
        expires_at = last_activity_time + timedelta(seconds=self.session_lifetime)
        
        return {
            'status': 'active' if remaining_time > 0 else 'expired',
            'remaining_time': int(remaining_time),
            'warning': remaining_time <= self.warning_threshold and remaining_time > 0,
            'expires_at': datetime_to_utc_iso(expires_at),  # 🔥 WORLD STANDARD: UTC ISO
            'last_activity': last_activity,
            'total_requests': session.get('total_requests', 0)
        }
    
    def is_session_expired(self):
        """セッション期限切れチェック"""
        status = self.get_session_status()
        return status['status'] == 'expired'
    
    def extend_session_lifetime(self):
        """セッション有効期限の延長（世界標準UTC統一）"""
        current_time = get_utc_now()  # 🔥 WORLD STANDARD: UTC timezone-aware
        session['last_activity'] = datetime_to_utc_iso(current_time)  # 🔥 WORLD STANDARD: UTC ISO
        session['session_extended_count'] = session.get('session_extended_count', 0) + 1
        session.permanent = True
        
        logger.info(f"セッション延長: ユーザー要求による延長 ({session.get('session_extended_count', 1)}回目)")
    
    def handle_session_expiration(self):
        """セッション期限切れ時の処理"""
        # 期限切れ直前のセッションバックアップを作成
        backup_id = self.create_session_backup(expired=True)
        
        # 重要なセッション情報を保持
        user_progress = {
            'exam_current': session.get('exam_current'),
            'exam_question_ids': session.get('exam_question_ids'),
            'selected_department': session.get('selected_department'),
            'selected_question_type': session.get('selected_question_type'),
            'backup_id': backup_id
        }
        
        # セッションクリア前に復元用データを退避
        session.clear()
        session['expired_session_backup'] = backup_id
        session['user_progress_backup'] = user_progress
        session.permanent = True
        
        logger.warning(f"セッション期限切れ処理完了: バックアップID={backup_id}")
    
    def create_session_backup(self, auto_save=False, expired=False):
        """セッションバックアップの作成（世界標準UTC統一）"""
        try:
            current_time = get_utc_now()  # 🔥 WORLD STANDARD: UTC timezone-aware
            backup_id = f"session_backup_{current_time.strftime('%Y%m%d_%H%M%S')}_{os.urandom(4).hex()}"
            
            # バックアップデータの準備
            backup_data = {
                'backup_id': backup_id,
                'timestamp': datetime_to_utc_iso(current_time),  # 🔥 WORLD STANDARD: UTC ISO
                'auto_save': auto_save,
                'expired': expired,
                'session_data': {}
            }
            
            # 重要なセッションデータのみバックアップ
            important_keys = [
                'exam_question_ids', 'exam_current', 'exam_category',
                'selected_department', 'selected_question_type', 'selected_year',
                'history', 'category_stats', 'quiz_settings',
                'srs_data', 'user_settings', 'learning_progress'
            ]
            
            for key in important_keys:
                if key in session:
                    backup_data['session_data'][key] = session[key]
            
            # バックアップファイルの保存
            backup_dir = os.path.join(os.path.dirname(__file__), 'session_backups')
            os.makedirs(backup_dir, exist_ok=True)
            
            backup_file = os.path.join(backup_dir, f"{backup_id}.json")
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, ensure_ascii=False, indent=2)
            
            # セッションにバックアップ履歴を記録
            backup_history = session.get('backup_history', [])
            backup_history.append({
                'backup_id': backup_id,
                'timestamp': datetime_to_utc_iso(current_time),  # 🔥 WORLD STANDARD: UTC ISO
                'auto_save': auto_save,
                'expired': expired
            })
            
            # 履歴は最新10件まで保持
            session['backup_history'] = backup_history[-10:]
            
            if not auto_save:  # 自動保存以外はログ出力
                logger.info(f"セッションバックアップ作成完了: {backup_id} (期限切れ: {expired})")
            
            return backup_id
            
        except Exception as e:
            logger.error(f"セッションバックアップ作成エラー: {e}")
            return None
    
    def restore_session_backup(self, backup_id):
        """セッションバックアップの復元"""
        try:
            backup_dir = os.path.join(os.path.dirname(__file__), 'session_backups')
            backup_file = os.path.join(backup_dir, f"{backup_id}.json")
            
            if not os.path.exists(backup_file):
                logger.error(f"バックアップファイルが見つかりません: {backup_id}")
                return False
            
            with open(backup_file, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            # セッションデータの復元
            session_data = backup_data.get('session_data', {})
            for key, value in session_data.items():
                session[key] = value
            
            # セッション状態をリフレッシュ（世界標準UTC統一）
            current_time = get_utc_now()  # 🔥 WORLD STANDARD: UTC timezone-aware
            session['last_activity'] = datetime_to_utc_iso(current_time)  # 🔥 WORLD STANDARD: UTC ISO
            session['session_restored'] = True
            session['restored_from'] = backup_id
            session['restored_at'] = datetime_to_utc_iso(current_time)  # 🔥 WORLD STANDARD: UTC ISO
            session.permanent = True
            
            logger.info(f"セッション復元完了: {backup_id}")
            return True
            
        except Exception as e:
            logger.error(f"セッション復元エラー: {e}")
            return False
    
    def get_backup_list(self):
        """利用可能なバックアップ一覧を取得"""
        try:
            backup_dir = os.path.join(os.path.dirname(__file__), 'session_backups')
            if not os.path.exists(backup_dir):
                return []
            
            backups = []
            for filename in os.listdir(backup_dir):
                if filename.endswith('.json'):
                    backup_file = os.path.join(backup_dir, filename)
                    try:
                        with open(backup_file, 'r', encoding='utf-8') as f:
                            backup_data = json.load(f)
                        
                        backups.append({
                            'backup_id': backup_data.get('backup_id'),
                            'timestamp': backup_data.get('timestamp'),
                            'auto_save': backup_data.get('auto_save', False),
                            'expired': backup_data.get('expired', False)
                        })
                    except Exception:
                        continue
            
            # タイムスタンプでソート（新しい順）
            backups.sort(key=lambda x: x['timestamp'], reverse=True)
            return backups
            
        except Exception as e:
            logger.error(f"バックアップ一覧取得エラー: {e}")
            return []
    
    def cleanup_old_backups(self, days=7):
        """古いバックアップの削除"""
        try:
            backup_dir = os.path.join(os.path.dirname(__file__), 'session_backups')
            if not os.path.exists(backup_dir):
                return
            
            cutoff_date = get_utc_now() - timedelta(days=days)  # 🔥 WORLD STANDARD: UTC timezone-aware
            deleted_count = 0
            
            for filename in os.listdir(backup_dir):
                if filename.endswith('.json'):
                    backup_file = os.path.join(backup_dir, filename)
                    try:
                        with open(backup_file, 'r', encoding='utf-8') as f:
                            backup_data = json.load(f)
                        
                        timestamp = parse_iso_to_utc(backup_data.get('timestamp'))  # 🔥 WORLD STANDARD: UTC統一解析
                        if timestamp < cutoff_date:
                            os.remove(backup_file)
                            deleted_count += 1
                    except Exception:
                        continue
            
            logger.info(f"古いバックアップクリーンアップ完了: {deleted_count}件削除")
            
        except Exception as e:
            logger.error(f"バックアップクリーンアップエラー: {e}")
    
    def _time_diff_seconds(self, time_str, current_time):
        """時間差を秒で計算（世界標準UTC統一）"""
        try:
            past_time = parse_iso_to_utc(time_str)  # 🔥 WORLD STANDARD: UTC統一解析
            # current_time は既に UTC timezone-aware であることを前提
            if current_time.tzinfo is None:
                current_time = current_time.replace(tzinfo=timezone.utc)
            return (current_time - past_time).total_seconds()
        except:
            return float('inf')


# グローバルインスタンス
session_timeout_manager = SessionTimeoutManager()

def init_session_timeout(app):
    """セッションタイムアウト機能の初期化"""
    session_timeout_manager.init_app(app)
    return session_timeout_manager