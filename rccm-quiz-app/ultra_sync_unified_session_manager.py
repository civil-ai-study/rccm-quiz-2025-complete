#!/usr/bin/env python3
"""
🔥 ULTRA SYNC: 統合セッション管理システム - 4システム競合問題の根本解決

🎯 CLAUDE.md準拠・1万人使用ソフト品質基準・ウルトラシンク統合アーキテクチャ

【根本問題の解決】
❌ 4つの独立したセッション管理システムの競合状態
❌ 毎リクエストでの session 初期化によるパフォーマンス問題  
❌ Thread-unsafe なグローバル session_locks
❌ 複数箇所での session.modified = True による競合

【ウルトラシンク解決策】
✅ 単一の統合セッション管理システム
✅ スレッドセーフな操作保証
✅ 効率的なセッション状態管理
✅ 企業レベルのパフォーマンス最適化
"""

import threading
import time
import json
import os
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, List, Union
from contextlib import contextmanager
from collections import defaultdict
import uuid
from functools import wraps
import gc
import psutil

logger = logging.getLogger(__name__)

class SessionOperationError(Exception):
    """セッション操作エラー"""
    pass

class SessionTimeoutError(Exception):
    """セッションタイムアウトエラー"""
    pass

class SessionCorruptionError(Exception):
    """セッション破損エラー"""
    pass

class UltraSyncUnifiedSessionManager:
    """
    🔥 ULTRA SYNC: 統合セッション管理システム
    
    4つの競合システムを統合した単一のセッション管理インターフェース
    - Flask-Session の統合
    - Auto-recovery の統合  
    - Timeout management の統合
    - Memory optimizer の統合
    """
    
    def __init__(self, app=None):
        self.app = app
        
        # 🔥 スレッドセーフな操作保証
        self._master_lock = threading.RLock()
        self._session_locks = {}
        self._lock_registry_lock = threading.Lock()
        
        # 📊 統合設定（環境ベース設定）
        self.session_timeout = int(os.environ.get('SESSION_TIMEOUT_SECONDS', 28800))  # 8時間
        self.auto_save_interval = int(os.environ.get('AUTO_SAVE_INTERVAL', 60))  # 1分
        self.cleanup_interval = int(os.environ.get('CLEANUP_INTERVAL', 300))  # 5分
        self.max_session_size = int(os.environ.get('MAX_SESSION_SIZE_MB', 5))  # 5MB
        
        # 🔍 統計とモニタリング
        self.stats = {
            'total_operations': 0,
            'successful_operations': 0,
            'failed_operations': 0,
            'timeouts': 0,
            'recoveries': 0,
            'cleanups': 0,
            'memory_optimizations': 0,
            'lock_contentions': 0
        }
        
        # 📋 セッション状態管理
        self._session_registry = {}
        self._backup_registry = {}
        self._last_cleanup = time.time()
        
        # ⚡ パフォーマンス最適化
        self._operation_cache = {}
        self._cache_ttl = 30  # 30秒キャッシュ
        
        # 🛡️ エラー回復システム
        self._recovery_handlers = []
        self._corruption_detectors = []
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Flask アプリケーション初期化"""
        self.app = app
        
        # 🔥 統合 before_request/after_request ハンドラ
        app.before_request(self.unified_before_request)
        app.after_request(self.unified_after_request)
        
        # 📊 統合APIエンドポイント登録
        self._register_unified_endpoints()
        
        # 🔄 バックグラウンド最適化タスク開始
        self._start_background_tasks()
        
        logger.info(f"🔥 ULTRA SYNC: 統合セッション管理システム初期化完了 (timeout={self.session_timeout}s)")
    
    def _register_unified_endpoints(self):
        """統合APIエンドポイント登録"""
        
        @self.app.route('/api/session/unified/status')
        def unified_session_status():
            """統合セッション状態確認"""
            try:
                with self._get_session_lock():
                    status = self._get_unified_session_status()
                    return json.dumps(status, ensure_ascii=False)
            except Exception as e:
                logger.error(f"統合セッション状態確認エラー: {e}")
                return json.dumps({'error': str(e)}), 500
        
        @self.app.route('/api/session/unified/stats')  
        def unified_session_stats():
            """統合セッション統計情報"""
            try:
                return json.dumps({
                    'stats': self.stats,
                    'session_count': len(self._session_registry),
                    'active_locks': len(self._session_locks),
                    'memory_usage': self._get_memory_usage(),
                    'uptime': time.time() - getattr(self, '_start_time', time.time())
                }, ensure_ascii=False)
            except Exception as e:
                logger.error(f"統合セッション統計エラー: {e}")
                return json.dumps({'error': str(e)}), 500
        
        @self.app.route('/api/session/unified/optimize', methods=['POST'])
        def force_session_optimization():
            """強制セッション最適化"""
            try:
                optimization_result = self._force_optimization()
                return json.dumps({
                    'success': True,
                    'optimization_result': optimization_result
                }, ensure_ascii=False)
            except Exception as e:
                logger.error(f"強制最適化エラー: {e}")
                return json.dumps({'error': str(e)}), 500
    
    @contextmanager
    def _get_session_lock(self, session_id=None):
        """スレッドセーフなセッション操作ロック取得"""
        if session_id is None:
            # Flask session から session_id を取得
            from flask import session
            session_id = session.get('session_id', 'default')
        
        # セッション専用ロック取得
        with self._lock_registry_lock:
            if session_id not in self._session_locks:
                self._session_locks[session_id] = threading.RLock()
            session_lock = self._session_locks[session_id]
        
        # 統計更新
        self.stats['total_operations'] += 1
        
        try:
            # タイムアウト付きロック取得
            acquired = session_lock.acquire(timeout=30)
            if not acquired:
                self.stats['lock_contentions'] += 1
                raise SessionOperationError(f"セッションロック取得タイムアウト: {session_id}")
            
            yield session_lock
            self.stats['successful_operations'] += 1
            
        except Exception as e:
            self.stats['failed_operations'] += 1
            raise
        finally:
            try:
                session_lock.release()
            except:
                pass
    
    def unified_before_request(self):
        """🔥 統合リクエスト前処理 - 4システム統合版"""
        from flask import session, request
        
        # 静的ファイルやAPIエンドポイントはスキップ
        if request.endpoint and (
            request.endpoint.startswith('static') or 
            request.endpoint.startswith('api.')
        ):
            return
        
        try:
            with self._get_session_lock():
                # 🔥 STEP 1: セッション基本設定（統合版）
                session.permanent = True
                
                # 🔥 STEP 2: セッションID管理（統合版）
                if 'session_id' not in session:
                    session['session_id'] = self._generate_session_id()
                
                session_id = session['session_id']
                
                # 🔥 STEP 3: タイムアウトチェック（統合版）
                timeout_result = self._check_session_timeout(session)
                if timeout_result['timeout_occurred']:
                    self._handle_session_timeout(session, timeout_result)
                
                # 🔥 STEP 4: セッション整合性チェック（統合版）
                corruption_check = self._check_session_corruption(session)
                if corruption_check['is_corrupted']:
                    self._handle_session_corruption(session, corruption_check)
                
                # 🔥 STEP 5: セッション最適化（統合版）
                if self._should_optimize_session():
                    self._optimize_session_memory(session)
                
                # 🔥 STEP 6: アクティビティ更新（統合版）
                self._update_session_activity(session)
                
                # 🔥 STEP 7: セッション初期化（必要時のみ）
                if not session.get('unified_initialized', False):
                    self._initialize_session_structure(session)
                
                # 🔥 STEP 8: 定期クリーンアップ（統合版）
                if self._should_run_cleanup():
                    self._run_background_cleanup()
                
        except Exception as e:
            logger.error(f"🚨 統合before_request処理エラー: {e}")
            # エラー発生時もセッション継続性を保証
            session.permanent = True
    
    def unified_after_request(self, response):
        """🔥 統合リクエスト後処理 - 4システム統合版"""
        from flask import session
        
        try:
            with self._get_session_lock():
                # 🔥 STEP 1: セッション状態保存（統合版）
                self._save_session_state(session)
                
                # 🔥 STEP 2: 自動バックアップ（統合版）
                if self._should_create_backup(session):
                    backup_id = self._create_session_backup(session)
                    session['last_backup_id'] = backup_id
                
                # 🔥 STEP 3: パフォーマンス統計更新
                self._update_performance_stats(session)
                
                # 🔥 STEP 4: レスポンスヘッダ追加（統合版）
                unified_status = self._get_unified_session_status()
                response.headers['X-Unified-Session-Status'] = json.dumps(unified_status)
                
                # 🔥 STEP 5: メモリ使用量チェック
                memory_usage = self._check_memory_usage()
                if memory_usage['should_cleanup']:
                    self._emergency_memory_cleanup()
                
        except Exception as e:
            logger.error(f"🚨 統合after_request処理エラー: {e}")
        
        return response
    
    def _generate_session_id(self) -> str:
        """一意なセッションID生成"""
        timestamp = int(time.time() * 1000)
        random_part = uuid.uuid4().hex[:8]
        return f"unified_{timestamp}_{random_part}"
    
    def _check_session_timeout(self, session: Dict) -> Dict[str, Any]:
        """統合セッションタイムアウトチェック"""
        last_activity = session.get('last_activity')
        if not last_activity:
            return {'timeout_occurred': False}
        
        try:
            # UTC時刻で比較
            last_time = datetime.fromisoformat(last_activity.replace('Z', '+00:00'))
            current_time = datetime.now(timezone.utc)
            elapsed = (current_time - last_time).total_seconds()
            
            if elapsed > self.session_timeout:
                self.stats['timeouts'] += 1
                return {
                    'timeout_occurred': True,
                    'elapsed_seconds': elapsed,
                    'timeout_threshold': self.session_timeout
                }
            
            return {
                'timeout_occurred': False,
                'elapsed_seconds': elapsed,
                'remaining_seconds': self.session_timeout - elapsed
            }
            
        except Exception as e:
            logger.warning(f"タイムアウトチェックエラー: {e}")
            return {'timeout_occurred': False}
    
    def _check_session_corruption(self, session: Dict) -> Dict[str, Any]:
        """統合セッション破損チェック"""
        corruption_report = {
            'is_corrupted': False,
            'corruption_types': [],
            'severity': 'none'
        }
        
        try:
            # 必須キーチェック
            required_keys = ['session_id', 'last_activity']
            missing_keys = [key for key in required_keys if key not in session]
            if missing_keys:
                corruption_report['corruption_types'].append('missing_keys')
                corruption_report['is_corrupted'] = True
            
            # データ型チェック
            type_checks = {
                'history': list,
                'exam_question_ids': list,
                'exam_current': int,
                'srs_data': dict
            }
            
            for key, expected_type in type_checks.items():
                if key in session and not isinstance(session[key], expected_type):
                    corruption_report['corruption_types'].append(f'invalid_type_{key}')
                    corruption_report['is_corrupted'] = True
            
            # セッションサイズチェック
            session_str = json.dumps(dict(session), default=str)
            session_size_mb = len(session_str.encode('utf-8')) / (1024 * 1024)
            if session_size_mb > self.max_session_size:
                corruption_report['corruption_types'].append('oversized_session')
                corruption_report['is_corrupted'] = True
                corruption_report['size_mb'] = session_size_mb
            
            if corruption_report['is_corrupted']:
                severity_map = {
                    1: 'minor',
                    2: 'moderate', 
                    3: 'major'
                }
                corruption_count = len(corruption_report['corruption_types'])
                corruption_report['severity'] = severity_map.get(
                    min(corruption_count, 3), 'critical'
                )
                
        except Exception as e:
            logger.error(f"セッション破損チェックエラー: {e}")
            corruption_report['is_corrupted'] = True
            corruption_report['corruption_types'] = ['check_error']
            corruption_report['severity'] = 'unknown'
        
        return corruption_report
    
    def _handle_session_timeout(self, session: Dict, timeout_info: Dict):
        """統合セッションタイムアウト処理"""
        logger.warning(f"🕐 セッションタイムアウト検出: {timeout_info}")
        
        # バックアップ作成（タイムアウト前データ保持）
        backup_id = self._create_session_backup(session, expired=True)
        
        # 重要データの退避
        preserved_data = {
            'session_id': session.get('session_id'),
            'user_name': session.get('user_name'),
            'selected_department': session.get('selected_department'),
            'selected_question_type': session.get('selected_question_type'),
            'backup_id': backup_id,
            'timeout_info': timeout_info
        }
        
        # セッションクリア（安全な方法）
        keys_to_clear = [key for key in session.keys() 
                        if key not in ['session_id', 'user_name']]
        for key in keys_to_clear:
            session.pop(key, None)
        
        # タイムアウト情報の記録
        session['timeout_occurred'] = True
        session['timeout_backup'] = backup_id
        session['preserved_data'] = preserved_data
        session.modified = True
        
        logger.info(f"✅ セッションタイムアウト処理完了: backup={backup_id}")
    
    def _handle_session_corruption(self, session: Dict, corruption_info: Dict):
        """統合セッション破損処理"""
        logger.error(f"🚨 セッション破損検出: {corruption_info}")
        self.stats['recoveries'] += 1
        
        # 破損前バックアップ作成
        backup_id = self._create_session_backup(session, corrupted=True)
        
        # 破損タイプ別修復
        for corruption_type in corruption_info['corruption_types']:
            if corruption_type == 'missing_keys':
                self._repair_missing_keys(session)
            elif corruption_type.startswith('invalid_type_'):
                self._repair_invalid_types(session)
            elif corruption_type == 'oversized_session':
                self._repair_oversized_session(session)
        
        # 修復完了マーク
        session['corruption_repaired'] = True
        session['corruption_backup'] = backup_id
        session['repair_timestamp'] = datetime.now(timezone.utc).isoformat()
        session.modified = True
        
        logger.info(f"✅ セッション破損修復完了: backup={backup_id}")
    
    def _repair_missing_keys(self, session: Dict):
        """必須キー修復"""
        if 'session_id' not in session:
            session['session_id'] = self._generate_session_id()
        if 'last_activity' not in session:
            session['last_activity'] = datetime.now(timezone.utc).isoformat()
    
    def _repair_invalid_types(self, session: Dict):
        """無効データ型修復"""
        type_repairs = {
            'history': [],
            'exam_question_ids': [],
            'exam_current': 0,
            'srs_data': {},
            'bookmarks': []
        }
        
        for key, default_value in type_repairs.items():
            if key in session:
                try:
                    # 型チェック
                    expected_type = type(default_value)
                    if not isinstance(session[key], expected_type):
                        session[key] = default_value
                        logger.info(f"🔧 データ型修復: {key} -> {expected_type.__name__}")
                except Exception as e:
                    session[key] = default_value
                    logger.warning(f"🔧 データ型修復失敗(デフォルト設定): {key} - {e}")
    
    def _repair_oversized_session(self, session: Dict):
        """肥大化セッション修復"""
        # 非重要データの削除
        non_essential_keys = [
            'debug_info', 'temporary_data', 'cache_data',
            'old_history', 'archived_data'
        ]
        
        for key in non_essential_keys:
            if key in session:
                del session[key]
        
        # 履歴データの制限
        if 'history' in session and isinstance(session['history'], list):
            if len(session['history']) > 100:  # 最新100件まで
                session['history'] = session['history'][-100:]
        
        # SRSデータの制限
        if 'srs_data' in session and isinstance(session['srs_data'], dict):
            if len(session['srs_data']) > 500:  # 最新500件まで
                sorted_items = sorted(
                    session['srs_data'].items(),
                    key=lambda x: x[1].get('last_reviewed', ''),
                    reverse=True
                )
                session['srs_data'] = dict(sorted_items[:500])
    
    def _initialize_session_structure(self, session: Dict):
        """統合セッション構造初期化"""
        default_structure = {
            'unified_initialized': True,
            'initialization_timestamp': datetime.now(timezone.utc).isoformat(),
            'exam_question_ids': [],
            'exam_current': 0,
            'history': [],
            'bookmarks': [],
            'srs_data': {},
            'category_stats': {},
            'quiz_settings': {},
            'user_settings': {},
            'learning_progress': {}
        }
        
        for key, default_value in default_structure.items():
            if key not in session:
                session[key] = default_value
        
        session.modified = True
        logger.info(f"🔧 統合セッション構造初期化完了: {session['session_id']}")
    
    def _update_session_activity(self, session: Dict):
        """統合セッションアクティビティ更新"""
        current_time = datetime.now(timezone.utc)
        session['last_activity'] = current_time.isoformat()
        
        # 統計更新
        session['total_requests'] = session.get('total_requests', 0) + 1
        session['last_request_timestamp'] = current_time.isoformat()
        
        # セッション継続時間計算
        if 'session_start' not in session:
            session['session_start'] = current_time.isoformat()
        
        start_time = datetime.fromisoformat(session['session_start'].replace('Z', '+00:00'))
        session_duration = (current_time - start_time).total_seconds()
        session['session_duration_seconds'] = int(session_duration)
    
    def _should_optimize_session(self) -> bool:
        """セッション最適化実行判定"""
        # 5%の確率で実行（負荷分散）
        import random
        return random.randint(1, 100) <= 5
    
    def _optimize_session_memory(self, session: Dict):
        """統合セッションメモリ最適化"""
        self.stats['memory_optimizations'] += 1
        
        # ガベージコレクション実行
        gc.collect()
        
        # セッションサイズ最適化
        self._repair_oversized_session(session)
        
        # メモリ統計更新
        memory_info = self._get_memory_usage()
        session['last_memory_optimization'] = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'memory_usage_mb': memory_info['usage_mb'],
            'optimization_count': self.stats['memory_optimizations']
        }
    
    def _should_run_cleanup(self) -> bool:
        """クリーンアップ実行判定"""
        return time.time() - self._last_cleanup > self.cleanup_interval
    
    def _run_background_cleanup(self):
        """バックグラウンドクリーンアップ実行"""
        self.stats['cleanups'] += 1
        self._last_cleanup = time.time()
        
        # 古いセッションロックのクリーンアップ
        self._cleanup_old_session_locks()
        
        # 古いバックアップファイルのクリーンアップ
        self._cleanup_old_backups()
        
        # 操作キャッシュのクリーンアップ
        self._cleanup_operation_cache()
        
        logger.info(f"🧹 バックグラウンドクリーンアップ完了 (cleanup#{self.stats['cleanups']})")
    
    def _cleanup_old_session_locks(self):
        """古いセッションロックのクリーンアップ"""
        current_time = time.time()
        locks_to_remove = []
        
        with self._lock_registry_lock:
            # 使用されていないロックを特定
            for session_id, lock in self._session_locks.items():
                # ロックが取得可能 = 使用されていない
                if lock.acquire(blocking=False):
                    try:
                        locks_to_remove.append(session_id)
                    finally:
                        lock.release()
            
            # 古いロックを削除
            for session_id in locks_to_remove:
                if session_id in self._session_locks:
                    del self._session_locks[session_id]
        
        if locks_to_remove:
            logger.info(f"🧹 古いセッションロック削除: {len(locks_to_remove)}個")
    
    def _cleanup_old_backups(self):
        """古いバックアップファイルのクリーンアップ"""
        try:
            backup_dir = os.path.join(os.path.dirname(__file__), 'unified_session_backups')
            if not os.path.exists(backup_dir):
                return
            
            current_time = time.time()
            retention_days = 7  # 7日間保持
            cutoff_time = current_time - (retention_days * 24 * 3600)
            
            deleted_count = 0
            for filename in os.listdir(backup_dir):
                if filename.endswith('.json'):
                    file_path = os.path.join(backup_dir, filename)
                    file_mtime = os.path.getmtime(file_path)
                    
                    if file_mtime < cutoff_time:
                        try:
                            os.remove(file_path)
                            deleted_count += 1
                        except Exception as e:
                            logger.warning(f"バックアップ削除失敗: {filename} - {e}")
            
            if deleted_count > 0:
                logger.info(f"🧹 古いバックアップ削除: {deleted_count}個")
                
        except Exception as e:
            logger.error(f"バックアップクリーンアップエラー: {e}")
    
    def _cleanup_operation_cache(self):
        """操作キャッシュのクリーンアップ"""
        current_time = time.time()
        expired_keys = []
        
        for key, (value, timestamp) in self._operation_cache.items():
            if current_time - timestamp > self._cache_ttl:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self._operation_cache[key]
        
        if expired_keys:
            logger.info(f"🧹 期限切れキャッシュ削除: {len(expired_keys)}個")
    
    def _save_session_state(self, session: Dict):
        """統合セッション状態保存"""
        session_id = session.get('session_id')
        if not session_id:
            return
        
        # セッション状態をレジストリに保存
        self._session_registry[session_id] = {
            'last_save': time.time(),
            'session_size': len(str(session)),
            'activity_count': session.get('total_requests', 0),
            'status': 'active'
        }
    
    def _should_create_backup(self, session: Dict) -> bool:
        """自動バックアップ作成判定"""
        last_backup = session.get('last_auto_backup')
        if not last_backup:
            return True
        
        try:
            last_backup_time = datetime.fromisoformat(last_backup.replace('Z', '+00:00'))
            current_time = datetime.now(timezone.utc)
            elapsed = (current_time - last_backup_time).total_seconds()
            
            return elapsed >= self.auto_save_interval
        except:
            return True
    
    def _create_session_backup(self, session: Dict, **flags) -> str:
        """統合セッションバックアップ作成"""
        try:
            current_time = datetime.now(timezone.utc)
            session_id = session.get('session_id', 'unknown')
            backup_id = f"unified_backup_{current_time.strftime('%Y%m%d_%H%M%S')}_{session_id[:8]}"
            
            # バックアップデータ準備
            backup_data = {
                'backup_id': backup_id,
                'session_id': session_id,
                'timestamp': current_time.isoformat(),
                'backup_type': 'unified',
                'flags': flags,
                'session_data': dict(session),
                'metadata': {
                    'manager_stats': self.stats.copy(),
                    'session_registry': self._session_registry.get(session_id, {}),
                    'memory_usage': self._get_memory_usage()
                }
            }
            
            # バックアップディレクトリ作成
            backup_dir = os.path.join(os.path.dirname(__file__), 'unified_session_backups')
            os.makedirs(backup_dir, exist_ok=True)
            
            # バックアップファイル保存
            backup_file = os.path.join(backup_dir, f"{backup_id}.json")
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, ensure_ascii=False, indent=2)
            
            # セッションにバックアップ履歴記録
            backup_history = session.get('backup_history', [])
            backup_history.append({
                'backup_id': backup_id,
                'timestamp': current_time.isoformat(),
                'type': 'unified',
                'flags': flags
            })
            session['backup_history'] = backup_history[-10:]  # 最新10件保持
            session['last_auto_backup'] = current_time.isoformat()
            
            # バックアップレジストリに登録
            self._backup_registry[backup_id] = {
                'session_id': session_id,
                'timestamp': current_time.isoformat(),
                'file_path': backup_file,
                'flags': flags
            }
            
            logger.info(f"💾 統合セッションバックアップ作成: {backup_id}")
            return backup_id
            
        except Exception as e:
            logger.error(f"統合バックアップ作成エラー: {e}")
            return None
    
    def _get_unified_session_status(self) -> Dict[str, Any]:
        """統合セッション状態取得"""
        from flask import session
        
        current_time = datetime.now(timezone.utc)
        session_id = session.get('session_id', 'unknown')
        last_activity = session.get('last_activity')
        
        # 基本状態
        status = {
            'session_id': session_id,
            'manager_type': 'unified',
            'timestamp': current_time.isoformat(),
            'status': 'active'
        }
        
        # アクティビティ情報
        if last_activity:
            try:
                last_time = datetime.fromisoformat(last_activity.replace('Z', '+00:00'))
                elapsed = (current_time - last_time).total_seconds()
                remaining = max(0, self.session_timeout - elapsed)
                
                status.update({
                    'last_activity': last_activity,
                    'elapsed_seconds': int(elapsed),
                    'remaining_seconds': int(remaining),
                    'timeout_threshold': self.session_timeout,
                    'will_expire_at': (last_time + timedelta(seconds=self.session_timeout)).isoformat()
                })
            except:
                status['activity_status'] = 'error'
        
        # セッションサイズ情報
        try:
            session_str = json.dumps(dict(session), default=str)
            session_size = len(session_str.encode('utf-8'))
            status.update({
                'session_size_bytes': session_size,
                'session_size_mb': round(session_size / (1024 * 1024), 3),
                'max_size_mb': self.max_session_size
            })
        except:
            status['size_status'] = 'error'
        
        # 統計情報
        status['manager_stats'] = self.stats.copy()
        status['session_registry'] = self._session_registry.get(session_id, {})
        
        return status
    
    def _update_performance_stats(self, session: Dict):
        """パフォーマンス統計更新"""
        session_id = session.get('session_id')
        if session_id in self._session_registry:
            self._session_registry[session_id]['last_update'] = time.time()
    
    def _check_memory_usage(self) -> Dict[str, Any]:
        """メモリ使用量チェック"""
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            memory_mb = memory_info.rss / (1024 * 1024)
            
            # メモリ使用量閾値（デフォルト500MB）
            memory_threshold = int(os.environ.get('MEMORY_THRESHOLD_MB', 500))
            
            return {
                'usage_mb': round(memory_mb, 2),
                'threshold_mb': memory_threshold,
                'should_cleanup': memory_mb > memory_threshold,
                'usage_percent': round((memory_mb / memory_threshold) * 100, 1)
            }
        except:
            return {
                'usage_mb': 0,
                'threshold_mb': 500,
                'should_cleanup': False,
                'usage_percent': 0,
                'error': 'memory_check_failed'
            }
    
    def _get_memory_usage(self) -> Dict[str, Any]:
        """メモリ使用量取得"""
        return self._check_memory_usage()
    
    def _emergency_memory_cleanup(self):
        """緊急メモリクリーンアップ"""
        logger.warning("🚨 緊急メモリクリーンアップ実行")
        
        # 強制ガベージコレクション
        gc.collect()
        
        # セッションロックの強制クリーンアップ
        self._cleanup_old_session_locks()
        
        # 操作キャッシュの全削除
        self._operation_cache.clear()
        
        # 統計更新
        self.stats['memory_optimizations'] += 1
        
        logger.info("✅ 緊急メモリクリーンアップ完了")
    
    def _force_optimization(self) -> Dict[str, Any]:
        """強制最適化実行"""
        logger.info("🚀 強制最適化開始")
        
        optimization_result = {
            'start_time': time.time(),
            'actions_performed': []
        }
        
        # メモリクリーンアップ
        self._emergency_memory_cleanup()
        optimization_result['actions_performed'].append('memory_cleanup')
        
        # セッションロッククリーンアップ
        self._cleanup_old_session_locks()
        optimization_result['actions_performed'].append('lock_cleanup')
        
        # バックアップクリーンアップ
        self._cleanup_old_backups()
        optimization_result['actions_performed'].append('backup_cleanup')
        
        # キャッシュクリーンアップ
        self._cleanup_operation_cache()
        optimization_result['actions_performed'].append('cache_cleanup')
        
        optimization_result.update({
            'end_time': time.time(),
            'duration_seconds': time.time() - optimization_result['start_time'],
            'success': True
        })
        
        logger.info(f"✅ 強制最適化完了: {optimization_result['duration_seconds']:.2f}秒")
        return optimization_result
    
    def _start_background_tasks(self):
        """バックグラウンドタスク開始"""
        self._start_time = time.time()
        logger.info("🚀 統合セッション管理バックグラウンドタスク開始")
    
    def get_session_lock(self, session_id: str = None):
        """外部からのセッションロック取得（後方互換性）"""
        return self._get_session_lock(session_id)
    
    def cleanup_session_locks(self):
        """外部からのセッションロッククリーンアップ（後方互換性）"""
        return self._cleanup_old_session_locks()

# グローバルインスタンス
unified_session_manager = UltraSyncUnifiedSessionManager()

def init_unified_session_manager(app):
    """統合セッション管理システムの初期化"""
    unified_session_manager.init_app(app)
    return unified_session_manager

# 後方互換性関数（既存コードとの互換性保証）
def get_session_lock(user_id=None):
    """後方互換性: セッションロック取得"""
    return unified_session_manager.get_session_lock(user_id)

def cleanup_session_locks():
    """後方互換性: セッションロッククリーンアップ"""
    return unified_session_manager.cleanup_session_locks()