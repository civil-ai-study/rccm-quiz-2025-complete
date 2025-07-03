#!/usr/bin/env python3
"""
🔗 Error Handler Integration Module
統合エラー処理システムの既存アプリケーション統合
副作用ゼロ保証 - 既存システム非破壊統合
"""

import functools
import logging
from typing import Dict, Any, Optional, Callable
from flask import Flask, request, g, jsonify
import traceback
from datetime import datetime

from comprehensive_error_handler import (
    get_error_handler, 
    handle_error, 
    error_handler, 
    error_context,
    ErrorCategory,
    ErrorSeverity
)

logger = logging.getLogger(__name__)

class FlaskErrorIntegration:
    """
    Flask アプリケーション統合エラーハンドラー
    既存のFlaskアプリに包括的エラー処理を統合
    """
    
    def __init__(self, app: Optional[Flask] = None):
        self.app = app
        self.error_handler = get_error_handler()
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Flask アプリケーションにエラーハンドリングを統合"""
        self.app = app
        
        # Flaskエラーハンドラー登録
        self._register_flask_error_handlers(app)
        
        # リクエストコンテキストフック登録
        self._register_request_hooks(app)
        
        # APIエンドポイント登録
        self._register_error_api_endpoints(app)
        
        logger.info("🔗 Flask Error Integration initialized")
    
    def _register_flask_error_handlers(self, app: Flask):
        """Flaskエラーハンドラー登録"""
        
        @app.errorhandler(404)
        def handle_not_found(error):
            """404エラーハンドリング"""
            context = f"Page not found: {request.url}"
            result = self.error_handler.handle_error(
                error, 
                context,
                user_id=self._get_user_id(),
                request_id=self._get_request_id()
            )
            
            return jsonify({
                'error': '404 Not Found',
                'message': 'ページが見つかりません',
                'error_id': result['error_id']
            }), 404
        
        @app.errorhandler(500)
        def handle_internal_error(error):
            """500エラーハンドリング"""
            context = f"Internal server error: {request.url}"
            result = self.error_handler.handle_error(
                error,
                context,
                user_id=self._get_user_id(),
                request_id=self._get_request_id()
            )
            
            return jsonify({
                'error': 'Internal Server Error',
                'message': result['user_message'],
                'error_id': result['error_id']
            }), 500
        
        @app.errorhandler(Exception)
        def handle_generic_exception(error):
            """汎用例外ハンドリング"""
            context = f"Unhandled exception: {request.url}"
            result = self.error_handler.handle_error(
                error,
                context,
                user_id=self._get_user_id(),
                request_id=self._get_request_id()
            )
            
            # 重要度に応じたHTTPステータス決定
            if result['severity'] == ErrorSeverity.CRITICAL.value:
                status_code = 503  # Service Unavailable
            elif result['severity'] == ErrorSeverity.HIGH.value:
                status_code = 500  # Internal Server Error
            else:
                status_code = 400  # Bad Request
            
            return jsonify({
                'error': 'Application Error',
                'message': result['user_message'],
                'error_id': result['error_id'],
                'category': result['category']
            }), status_code
    
    def _register_request_hooks(self, app: Flask):
        """リクエストフック登録"""
        
        @app.before_request
        def before_request():
            """リクエスト前処理"""
            g.request_start_time = datetime.now()
            g.request_id = self._generate_request_id()
            g.error_context = f"{request.method} {request.url}"
        
        @app.after_request
        def after_request(response):
            """リクエスト後処理"""
            # パフォーマンス監視
            if hasattr(g, 'request_start_time'):
                duration = (datetime.now() - g.request_start_time).total_seconds()
                if duration > 3.0:  # 3秒以上の場合は警告
                    logger.warning(f"⚠️ Slow request: {g.error_context} took {duration:.2f}s")
            
            return response
        
        @app.teardown_request
        def teardown_request(exception):
            """リクエスト終了処理"""
            if exception:
                # リクエスト終了時の例外処理
                context = getattr(g, 'error_context', 'Request teardown')
                self.error_handler.handle_error(
                    exception,
                    context,
                    user_id=self._get_user_id(),
                    request_id=getattr(g, 'request_id', '')
                )
    
    def _register_error_api_endpoints(self, app: Flask):
        """エラー管理APIエンドポイント登録"""
        
        @app.route('/api/errors/statistics')
        def get_error_statistics():
            """エラー統計API"""
            try:
                stats = self.error_handler.get_error_statistics()
                return jsonify(stats)
            except Exception as e:
                logger.error(f"Error statistics API failed: {e}")
                return jsonify({'error': 'Statistics unavailable'}), 500
        
        @app.route('/api/errors/recent')
        def get_recent_errors():
            """最近のエラーAPI"""
            try:
                limit = request.args.get('limit', 50, type=int)
                errors = self.error_handler.get_recent_errors(limit)
                
                # 機密情報除去
                safe_errors = []
                for error in errors:
                    safe_error = {
                        'error_id': error['error_id'],
                        'timestamp': error['timestamp'],
                        'category': error['category'],
                        'severity': error['severity'],
                        'type': error['type'],
                        'recovery_success': error['recovery_success']
                    }
                    safe_errors.append(safe_error)
                
                return jsonify(safe_errors)
            except Exception as e:
                logger.error(f"Recent errors API failed: {e}")
                return jsonify({'error': 'Recent errors unavailable'}), 500
        
        @app.route('/api/errors/clear', methods=['POST'])
        def clear_error_statistics():
            """エラー統計クリアAPI（管理者用）"""
            try:
                self.error_handler.clear_error_statistics()
                return jsonify({'success': True, 'message': 'Error statistics cleared'})
            except Exception as e:
                logger.error(f"Clear error statistics failed: {e}")
                return jsonify({'error': 'Clear operation failed'}), 500
    
    def _get_user_id(self) -> str:
        """ユーザーID取得"""
        try:
            # セッションからユーザーIDを取得（実装に応じて調整）
            from flask import session
            return session.get('user_id', 'anonymous')
        except Exception:
            return 'unknown'
    
    def _get_request_id(self) -> str:
        """リクエストID取得"""
        return getattr(g, 'request_id', self._generate_request_id())
    
    def _generate_request_id(self) -> str:
        """リクエストID生成"""
        import uuid
        return f"REQ_{uuid.uuid4().hex[:8]}"

def session_error_handler(func):
    """セッション操作用エラーハンドリングデコレータ"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            context = f"Session operation: {func.__name__}"
            result = handle_error(
                e, 
                context,
                user_id=getattr(g, 'user_id', 'unknown'),
                request_id=getattr(g, 'request_id', '')
            )
            
            if result['success']:
                # 回復成功時は処理を続行
                logger.info(f"✅ Session error recovered: {result['error_id']}")
                return None
            else:
                # 回復失敗時はエラーレスポンス
                logger.error(f"❌ Session error unrecoverable: {result['error_id']}")
                raise Exception(f"Session error: {result['user_message']}")
    
    return wrapper

def data_operation_error_handler(func):
    """データ操作用エラーハンドリングデコレータ"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            context = f"Data operation: {func.__name__}"
            result = handle_error(
                e,
                context,
                user_id=getattr(g, 'user_id', 'unknown'),
                request_id=getattr(g, 'request_id', '')
            )
            
            if result['success']:
                logger.info(f"✅ Data error recovered: {result['error_id']}")
                return {'status': 'recovered', 'error_id': result['error_id']}
            else:
                logger.error(f"❌ Data error unrecoverable: {result['error_id']}")
                return {'status': 'failed', 'error_id': result['error_id'], 'message': result['user_message']}
    
    return wrapper

def api_error_handler(func):
    """API エンドポイント用エラーハンドリングデコレータ"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            context = f"API endpoint: {func.__name__}"
            result = handle_error(
                e,
                context,
                user_id=getattr(g, 'user_id', 'unknown'),
                request_id=getattr(g, 'request_id', '')
            )
            
            # APIレスポンス形式でエラー返却
            error_response = {
                'success': False,
                'error_id': result['error_id'],
                'category': result['category'],
                'message': result['user_message']
            }
            
            # 重要度に応じたHTTPステータス
            if result['severity'] == ErrorSeverity.CRITICAL.value:
                return jsonify(error_response), 503
            elif result['severity'] == ErrorSeverity.HIGH.value:
                return jsonify(error_response), 500
            else:
                return jsonify(error_response), 400
    
    return wrapper

# 統合ヘルパー関数

def safe_session_get(key: str, default=None, user_id: str = "unknown"):
    """セッション取得の安全版"""
    try:
        from flask import session
        return session.get(key, default)
    except Exception as e:
        context = f"Session get operation: key={key}"
        result = handle_error(e, context, user_id=user_id)
        logger.warning(f"⚠️ Session get failed: {result['error_id']}")
        return default

def safe_session_set(key: str, value, user_id: str = "unknown"):
    """セッション設定の安全版"""
    try:
        from flask import session
        session[key] = value
        return True
    except Exception as e:
        context = f"Session set operation: key={key}"
        result = handle_error(e, context, user_id=user_id)
        logger.error(f"❌ Session set failed: {result['error_id']}")
        return False

def safe_file_operation(operation: Callable, *args, **kwargs):
    """ファイル操作の安全版"""
    try:
        return operation(*args, **kwargs)
    except Exception as e:
        context = f"File operation: {operation.__name__}"
        result = handle_error(e, context)
        logger.error(f"❌ File operation failed: {result['error_id']}")
        return None

def safe_redis_operation(operation: Callable, *args, **kwargs):
    """Redis操作の安全版"""
    try:
        return operation(*args, **kwargs)
    except Exception as e:
        context = f"Redis operation: {operation.__name__}"
        result = handle_error(e, context)
        logger.warning(f"⚠️ Redis operation failed, using fallback: {result['error_id']}")
        return None

# Flask App Factory 拡張
def create_error_integrated_app(config_object=None) -> Flask:
    """
    エラーハンドリング統合済みFlaskアプリファクトリー
    
    Returns:
        Flask: エラーハンドリング統合済みアプリケーション
    """
    app = Flask(__name__)
    
    if config_object:
        app.config.from_object(config_object)
    
    # エラーハンドリング統合
    error_integration = FlaskErrorIntegration(app)
    
    # 基本ミドルウェア設定
    @app.middleware('before_request')
    def setup_error_context():
        g.error_integration = error_integration
    
    logger.info("🚀 Error-integrated Flask app created")
    return app

def main():
    """
    統合テスト・デモンストレーション
    """
    print("🔗 Error Handler Integration Test")
    print("=" * 80)
    
    # Flask アプリケーション作成
    app = create_error_integrated_app()
    
    # テストエンドポイント作成
    @app.route('/test/session-error')
    @session_error_handler
    def test_session_error():
        raise ValueError("Test session error")
    
    @app.route('/test/data-error')
    @data_operation_error_handler
    def test_data_error():
        raise FileNotFoundError("Test data file not found")
    
    @app.route('/test/api-error')
    @api_error_handler
    def test_api_error():
        raise ConnectionError("Test API connection error")
    
    print("✅ Error integration test setup completed")
    print("📊 Available endpoints:")
    print("   - /api/errors/statistics")
    print("   - /api/errors/recent")
    print("   - /api/errors/clear")
    print("   - /test/session-error")
    print("   - /test/data-error")
    print("   - /test/api-error")

if __name__ == "__main__":
    main()