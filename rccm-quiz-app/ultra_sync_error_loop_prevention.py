#!/usr/bin/env python3
"""
🛡️ Ultra Sync Error Page Infinite Loop Prevention System
RCCM試験問題集アプリ - エラーページ無限ループ防止システム

🎯 CLAUDE.md準拠・副作用ゼロ保証・ウルトラシンクエラー防止:
- エラーハンドラー内でのエラー発生時の無限ループ防止
- エラーページアクセス頻度の監視と制限
- 重複エラーハンドラーの統合
- エラー処理時の安全な代替ページ表示
- セッション毎のエラー累積カウント
- エラー連鎖の早期切断
"""

import threading
import time
import json
import logging
from datetime import datetime, timedelta
from collections import defaultdict, deque
from typing import Dict, List, Any, Optional
from functools import wraps
import os

logger = logging.getLogger(__name__)

class UltraSyncErrorLoopPrevention:
    """🛡️ ウルトラシンクエラーループ防止システム"""
    
    def __init__(self):
        # エラー追跡データ
        self.error_tracking = defaultdict(lambda: {
            'count': 0,
            'first_seen': None,
            'last_seen': None,
            'error_chain': deque(maxlen=10),
            'blocked': False,
            'blocked_until': None
        })
        
        # セッション毎エラーカウント
        self.session_errors = defaultdict(lambda: {
            'count': 0,
            'last_reset': datetime.now(),
            'error_types': defaultdict(int),
            'in_error_loop': False
        })
        
        # グローバル統計
        self.global_stats = {
            'total_errors_handled': 0,
            'loops_prevented': 0,
            'blocked_sessions': 0,
            'fallback_activations': 0,
            'last_reset': datetime.now()
        }
        
        # 設定
        self.config = {
            'max_errors_per_session': 10,  # セッション毎最大エラー数
            'max_errors_per_minute': 5,    # 1分間あたり最大エラー数
            'reset_interval_minutes': 30,  # エラーカウントリセット間隔
            'block_duration_minutes': 15,  # ブロック継続時間
            'error_chain_threshold': 3,    # エラー連鎖検出閾値
            'fallback_content_max_size': 1024  # フォールバック内容最大サイズ
        }
        
        # スレッドセーフティ
        self.lock = threading.Lock()
        
        # エラーテンプレート重複統合
        self.unified_error_handlers = {}
        
        # セーフフォールバック内容
        self.safe_fallback_content = self._create_safe_fallback_content()
        
        logger.info("🛡️ Ultra Sync Error Loop Prevention System initialized")
    
    def _create_safe_fallback_content(self) -> str:
        """🔒 安全なフォールバック内容作成（エラー処理でエラーが起きない保証）"""
        timestamp = datetime.now().isoformat()
        return f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>システムエラー | RCCM試験問題集</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
        .error-container {{ background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); max-width: 600px; margin: 0 auto; }}
        .error-title {{ color: #d32f2f; margin-bottom: 20px; font-size: 24px; }}
        .error-message {{ color: #666; line-height: 1.6; margin-bottom: 20px; }}
        .action-buttons {{ margin-top: 20px; }}
        .btn {{ display: inline-block; padding: 10px 20px; background: #1976d2; color: white; text-decoration: none; border-radius: 4px; margin-right: 10px; }}
        .btn:hover {{ background: #1565c0; }}
    </style>
</head>
<body>
    <div class="error-container">
        <h1 class="error-title">🛡️ 安全モード - システムエラー</h1>
        <div class="error-message">
            <p>申し訳ございません。システムでエラーが発生しましたが、安全な処理により無限ループを防止しました。</p>
            <p>このページは最小限の安全な内容で構成されており、追加のエラーを発生させません。</p>
        </div>
        <div class="action-buttons">
            <a href="/" class="btn">ホームページに戻る</a>
            <a href="javascript:history.back()" class="btn" style="background:#666;">前のページ</a>
        </div>
        <div style="margin-top: 20px; padding: 10px; background: #f9f9f9; border-radius: 4px; font-size: 12px; color: #888;">
            エラー防止システム作動 - タイムスタンプ: {timestamp}
        </div>
    </div>
</body>
</html>"""
    
    def track_error(self, session_id: str, error_type: str, error_message: str, url: str) -> dict:
        """🔍 エラー追跡とループ検出"""
        with self.lock:
            current_time = datetime.now()
            
            # セッション毎エラー追跡
            session_data = self.session_errors[session_id]
            session_data['count'] += 1
            session_data['error_types'][error_type] += 1
            
            # エラー連鎖追跡
            error_chain = session_data.get('error_chain', deque(maxlen=10))
            error_chain.append({
                'timestamp': current_time,
                'error_type': error_type,
                'url': url,
                'message': error_message[:200]  # メッセージは200文字まで
            })
            session_data['error_chain'] = error_chain
            
            # ループ検出ロジック
            loop_detected = self._detect_error_loop(session_id, error_chain)
            
            # グローバル統計更新
            self.global_stats['total_errors_handled'] += 1
            
            # 結果作成
            result = {
                'session_id': session_id,
                'error_type': error_type,
                'timestamp': current_time.isoformat(),
                'session_error_count': session_data['count'],
                'loop_detected': loop_detected,
                'should_block': False,
                'fallback_required': False,
                'safe_to_continue': True
            }
            
            # ブロック判定
            if self._should_block_session(session_id):
                result['should_block'] = True
                result['safe_to_continue'] = False
                session_data['blocked'] = True
                session_data['blocked_until'] = current_time + timedelta(
                    minutes=self.config['block_duration_minutes']
                )
                self.global_stats['blocked_sessions'] += 1
                
            # フォールバック必要性判定
            if loop_detected or session_data['count'] >= self.config['max_errors_per_session']:
                result['fallback_required'] = True
                result['safe_to_continue'] = False
                self.global_stats['fallback_activations'] += 1
                
            # ループ防止統計
            if loop_detected:
                self.global_stats['loops_prevented'] += 1
                session_data['in_error_loop'] = True
            
            logger.info(f"🔍 Error tracked: {error_type} for session {session_id[:8]}... (count: {session_data['count']})")
            
            return result
    
    def _detect_error_loop(self, session_id: str, error_chain: deque) -> bool:
        """🔄 エラーループ検出ロジック"""
        if len(error_chain) < self.config['error_chain_threshold']:
            return False
            
        # 最近のエラーパターン分析
        recent_errors = list(error_chain)[-self.config['error_chain_threshold']:]
        
        # 同一エラータイプの連続発生チェック
        error_types = [e['error_type'] for e in recent_errors]
        if len(set(error_types)) == 1:  # 全て同じエラータイプ
            return True
            
        # 同一URLでの連続エラーチェック
        urls = [e['url'] for e in recent_errors]
        if len(set(urls)) == 1:  # 全て同じURL
            return True
            
        # 時間的なループパターン検出
        time_intervals = []
        for i in range(1, len(recent_errors)):
            prev_timestamp = recent_errors[i-1]['timestamp']
            curr_timestamp = recent_errors[i]['timestamp']
            
            # datetime object を isoformat string に変換
            if isinstance(prev_timestamp, datetime):
                prev_time = prev_timestamp
            else:
                prev_time = datetime.fromisoformat(prev_timestamp.replace('Z', '+00:00') if 'Z' in prev_timestamp else prev_timestamp)
                
            if isinstance(curr_timestamp, datetime):
                curr_time = curr_timestamp
            else:
                curr_time = datetime.fromisoformat(curr_timestamp.replace('Z', '+00:00') if 'Z' in curr_timestamp else curr_timestamp)
                
            interval = (curr_time - prev_time).total_seconds()
            time_intervals.append(interval)
        
        # 短時間での連続エラー（3秒以内）
        if all(interval < 3 for interval in time_intervals):
            return True
            
        return False
    
    def _should_block_session(self, session_id: str) -> bool:
        """🚫 セッションブロック判定"""
        session_data = self.session_errors[session_id]
        
        # 既にブロック中の場合
        if session_data.get('blocked') and session_data.get('blocked_until'):
            if datetime.now() < session_data['blocked_until']:
                return True
            else:
                # ブロック期間終了
                session_data['blocked'] = False
                session_data['blocked_until'] = None
                return False
        
        # エラー数による判定
        if session_data['count'] >= self.config['max_errors_per_session']:
            return True
            
        # エラーループ発生時
        if session_data.get('in_error_loop'):
            return True
            
        return False
    
    def get_safe_error_response(self, session_id: str, error_type: str = "unknown") -> tuple:
        """🔒 安全なエラーレスポンス生成"""
        try:
            # エラー追跡情報取得
            session_data = self.session_errors.get(session_id, {})
            
            # 安全な内容作成
            safe_content = self.safe_fallback_content
            
            # ヘッダー設定（キャッシュ無効化）
            headers = {
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache',
                'Expires': '0',
                'X-Error-Handler': 'ultra-sync-safe-mode',
                'X-Session-Errors': str(session_data.get('count', 0)),
                'X-Loop-Prevention': 'active'
            }
            
            return safe_content, 500, headers
            
        except Exception as e:
            # 最後の安全網：完全に静的な内容
            logger.error(f"Safe error response generation failed: {e}")
            return """<!DOCTYPE html><html><head><title>Error</title></head><body><h1>System Error</h1><p>An error occurred. <a href="/">Return to home</a></p></body></html>""", 500, {}
    
    def create_unified_error_handler(self, error_codes: List[int]) -> callable:
        """🔧 統合エラーハンドラー作成"""
        def unified_handler(error):
            """統合エラーハンドラー"""
            try:
                from flask import request, session as flask_session
                
                # セッションID取得
                session_id = flask_session.get('session_id', 'anonymous')
                error_code = getattr(error, 'code', 500)
                error_type = f"http_{error_code}"
                error_message = str(error)
                url = request.url if request else 'unknown'
                
                # エラー追跡
                tracking_result = self.track_error(session_id, error_type, error_message, url)
                
                # 安全性チェック
                if not tracking_result['safe_to_continue'] or tracking_result['fallback_required']:
                    logger.warning(f"🛡️ Fallback activated for session {session_id[:8]}... (error: {error_type})")
                    return self.get_safe_error_response(session_id, error_type)
                
                # 通常のエラー処理（安全な場合のみ）
                return self._safe_normal_error_response(error_code, error_message)
                
            except Exception as e:
                # エラーハンドラー内でエラー発生時の安全処理
                logger.error(f"Error in unified error handler: {e}")
                return self.get_safe_error_response('emergency', 'handler_error')
        
        return unified_handler
    
    def _safe_normal_error_response(self, error_code: int, error_message: str) -> tuple:
        """🔒 安全な通常エラーレスポンス"""
        try:
            # エラーコード別メッセージ
            error_messages = {
                400: "不正なリクエストです",
                403: "アクセスが拒否されました", 
                404: "ページが見つかりません",
                405: "許可されていないメソッドです",
                500: "内部サーバーエラーが発生しました",
                502: "外部サービスとの通信に失敗しました",
                503: "サービスが一時的に利用できません",
                504: "リクエストがタイムアウトしました"
            }
            
            message = error_messages.get(error_code, "予期しないエラーが発生しました")
            
            # 簡易HTML生成（テンプレートエンジンを使わない安全な方法）
            html_content = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>エラー {error_code} | RCCM試験問題集</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
        .container {{ background: white; padding: 30px; border-radius: 8px; max-width: 600px; margin: 0 auto; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .error-title {{ color: #d32f2f; margin-bottom: 20px; }}
        .error-message {{ color: #666; line-height: 1.6; }}
        .btn {{ display: inline-block; padding: 10px 20px; background: #1976d2; color: white; text-decoration: none; border-radius: 4px; margin: 5px; }}
        .btn:hover {{ background: #1565c0; }}
    </style>
</head>
<body>
    <div class="container">
        <h1 class="error-title">エラー {error_code}</h1>
        <div class="error-message">
            <p>{message}</p>
            <p>ご不便をおかけして申し訳ございません。以下の方法をお試しください：</p>
            <ul>
                <li>ページを再読み込みしてください</li>
                <li>ブラウザの戻るボタンで前のページに戻ってください</li>
                <li>ホームページから改めてアクセスしてください</li>
            </ul>
        </div>
        <div>
            <a href="/" class="btn">ホームページ</a>
            <a href="javascript:history.back()" class="btn" style="background:#666;">前のページ</a>
            <a href="javascript:location.reload()" class="btn" style="background:#666;">再読み込み</a>
        </div>
    </div>
</body>
</html>"""
            
            headers = {
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache',
                'X-Error-Handler': 'ultra-sync-unified'
            }
            
            return html_content, error_code, headers
            
        except Exception as e:
            logger.error(f"Safe normal error response failed: {e}")
            return self.get_safe_error_response('emergency', 'response_generation_error')
    
    def get_statistics(self) -> dict:
        """📊 エラー防止システム統計取得"""
        with self.lock:
            current_time = datetime.now()
            
            # アクティブセッション数
            active_sessions = sum(1 for session_data in self.session_errors.values() 
                                if (current_time - session_data.get('last_reset', current_time)).total_seconds() < 3600)
            
            # ブロック中セッション数
            blocked_sessions = sum(1 for session_data in self.session_errors.values()
                                 if session_data.get('blocked') and 
                                    session_data.get('blocked_until') and
                                    current_time < session_data['blocked_until'])
            
            return {
                'system_status': 'active',
                'global_stats': self.global_stats.copy(),
                'current_metrics': {
                    'active_sessions': active_sessions,
                    'blocked_sessions': blocked_sessions,
                    'total_tracked_sessions': len(self.session_errors),
                    'average_errors_per_session': sum(s['count'] for s in self.session_errors.values()) / max(len(self.session_errors), 1)
                },
                'config': self.config.copy(),
                'timestamp': current_time.isoformat()
            }
    
    def reset_session_errors(self, session_id: str) -> bool:
        """🔄 セッションエラーカウントリセット"""
        with self.lock:
            if session_id in self.session_errors:
                session_data = self.session_errors[session_id]
                session_data['count'] = 0
                session_data['last_reset'] = datetime.now()
                session_data['error_types'].clear()
                session_data['in_error_loop'] = False
                session_data['blocked'] = False
                session_data['blocked_until'] = None
                if 'error_chain' in session_data:
                    session_data['error_chain'].clear()
                
                logger.info(f"🔄 Session errors reset for {session_id[:8]}...")
                return True
        return False
    
    def cleanup_old_sessions(self) -> int:
        """🧹 古いセッションデータのクリーンアップ"""
        with self.lock:
            current_time = datetime.now()
            cleanup_threshold = current_time - timedelta(hours=24)
            
            sessions_to_remove = []
            for session_id, session_data in self.session_errors.items():
                last_activity = session_data.get('last_reset', current_time)
                if last_activity < cleanup_threshold:
                    sessions_to_remove.append(session_id)
            
            for session_id in sessions_to_remove:
                del self.session_errors[session_id]
            
            logger.info(f"🧹 Cleaned up {len(sessions_to_remove)} old sessions")
            return len(sessions_to_remove)


# グローバルインスタンス
error_loop_prevention = None

def get_error_loop_prevention():
    """エラーループ防止システムインスタンス取得"""
    global error_loop_prevention
    if error_loop_prevention is None:
        error_loop_prevention = UltraSyncErrorLoopPrevention()
    return error_loop_prevention

def ultra_sync_error_handler_decorator(error_codes: List[int]):
    """🛡️ ウルトラシンクエラーハンドラーデコレータ"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                prevention_system = get_error_loop_prevention()
                return prevention_system.create_unified_error_handler(error_codes)(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error handler decorator failed: {e}")
                return get_error_loop_prevention().get_safe_error_response('decorator_error', 'decorator_failure')
        return wrapper
    return decorator

def register_flask_error_handlers(app):
    """🔧 Flaskアプリにエラーハンドラー登録"""
    prevention_system = get_error_loop_prevention()
    
    # 統合エラーハンドラー作成
    unified_handler = prevention_system.create_unified_error_handler([400, 403, 404, 405, 500, 502, 503, 504])
    
    # 各エラーコードに対してハンドラー登録
    error_codes = [400, 403, 404, 405, 500, 502, 503, 504]
    for code in error_codes:
        app.errorhandler(code)(unified_handler)
    
    # 例外ハンドラー登録
    app.errorhandler(Exception)(unified_handler)
    
    logger.info("🛡️ Ultra Sync unified error handlers registered")
    
    return prevention_system


if __name__ == "__main__":
    # テスト実行
    prevention = UltraSyncErrorLoopPrevention()
    
    # テストシナリオ
    print("🧪 Testing error loop prevention...")
    
    # 通常エラー
    result1 = prevention.track_error("test_session", "404", "Page not found", "/test")
    print(f"Normal error: {result1}")
    
    # ループ発生シミュレーション
    for i in range(5):
        result = prevention.track_error("test_session", "500", "Internal error", "/same_page")
        print(f"Loop test {i+1}: loop_detected={result['loop_detected']}, should_block={result['should_block']}")
    
    # 統計確認
    stats = prevention.get_statistics()
    print(f"📊 Statistics: {stats}")
    
    print("✅ Error loop prevention test completed")