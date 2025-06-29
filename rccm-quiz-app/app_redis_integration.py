"""
RCCM学習アプリ - Redis統合版アプリケーション
Flask-Session + Redis 次世代セッション管理統合
"""

import os
import logging
from datetime import datetime, timedelta
from flask import Flask, session, request, jsonify, redirect, url_for
from flask_session import Session

# Redis設定とセッション管理
from redis_config import (
    redis_session_manager, 
    get_redis_config, 
    create_session_middleware,
    RedisConfig,
    RedisClusterConfig,
    SessionConfig
)
from session_manager import (
    advanced_session_manager,
    initialize_session_system,
    redis_session_required,
    session_analytics,
    get_session_migration_status
)
from config import RedisSessionConfig, ProductionRedisConfig

# 既存のアプリケーション設定
from config import Config, ExamConfig, SRSConfig, DataConfig, RCCMConfig

logger = logging.getLogger(__name__)


def create_redis_app(config_name='development'):
    """Redis統合版Flask アプリ作成"""
    app = Flask(__name__)
    
    # 環境別設定読み込み
    if config_name == 'production':
        app.config.from_object(ProductionRedisConfig)
    elif config_name == 'redis':
        app.config.from_object(RedisSessionConfig)
    else:
        # 開発環境用（Redis有効）
        app.config.from_object(Config)
        
        # Redis設定を開発環境に追加
        try:
            redis_config = get_redis_config()
            app.config.update(redis_config)
        except Exception as e:
            logger.warning(f"Redis設定読み込み失敗 - ファイルベースセッションを使用: {e}")
            # フォールバック設定
            app.config.update({
                'SESSION_TYPE': 'filesystem',
                'SESSION_FILE_DIR': os.path.join(os.path.dirname(__file__), 'flask_session'),
                'SESSION_PERMANENT': True,
                'SESSION_USE_SIGNER': True,
            })
    
    # セッション初期化
    Session(app)
    
    # Redis セッション管理システム初期化
    with app.app_context():
        try:
            success = initialize_session_system()
            if success:
                logger.info("✅ Redis セッション管理システム初期化完了")
            else:
                logger.warning("⚠️ Redis セッション管理システム初期化失敗 - フォールバックモード")
        except Exception as e:
            logger.error(f"セッション管理システム初期化エラー: {e}")
    
    # セッション管理関連ルート追加
    register_session_management_routes(app)
    
    # セッション監視ミドルウェア
    register_session_middleware(app)
    
    return app


def register_session_management_routes(app):
    """セッション管理用ルート登録"""
    
    @app.route('/admin/session/status')
    @redis_session_required
    @session_analytics
    def session_status():
        """セッション状態確認"""
        try:
            status = {
                'redis_status': redis_session_manager.health_check(),
                'session_stats': redis_session_manager.get_session_stats(),
                'migration_status': get_session_migration_status(),
                'current_session_info': {
                    'session_id': session.get('_id', 'unknown'),
                    'session_size': len(str(session)),
                    'session_keys': list(session.keys())
                }
            }
            
            return jsonify(status)
            
        except Exception as e:
            logger.error(f"セッション状態確認エラー: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/admin/session/analytics')
    @redis_session_required
    def session_analytics_view():
        """セッション分析データ表示"""
        try:
            analytics = advanced_session_manager.get_session_analytics()
            return jsonify(analytics)
            
        except Exception as e:
            logger.error(f"セッション分析エラー: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/admin/session/cleanup', methods=['POST'])
    @redis_session_required
    def session_cleanup():
        """期限切れセッションクリーンアップ"""
        try:
            cleaned_count = advanced_session_manager.cleanup_expired_sessions()
            return jsonify({
                'success': True,
                'cleaned_sessions': cleaned_count,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"セッションクリーンアップエラー: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/admin/session/backup', methods=['POST'])
    @redis_session_required  
    def create_session_backup():
        """セッションバックアップ作成"""
        try:
            backup_key = advanced_session_manager.create_session_backup()
            
            if backup_key:
                return jsonify({
                    'success': True,
                    'backup_key': backup_key,
                    'timestamp': datetime.now().isoformat()
                })
            else:
                return jsonify({'error': 'バックアップ作成に失敗しました'}), 500
                
        except Exception as e:
            logger.error(f"セッションバックアップエラー: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/admin/session/restore', methods=['POST'])
    @redis_session_required
    def restore_session_backup():
        """セッションバックアップからの復旧"""
        try:
            backup_key = request.json.get('backup_key')
            if not backup_key:
                return jsonify({'error': 'backup_keyが必要です'}), 400
            
            success = advanced_session_manager.restore_session_backup(backup_key)
            
            return jsonify({
                'success': success,
                'backup_key': backup_key,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"セッション復旧エラー: {e}")
            return jsonify({'error': str(e)}), 500


def register_session_middleware(app):
    """セッション監視ミドルウェア登録"""
    
    @app.before_request
    def before_request():
        """リクエスト前処理（セッション監視）"""
        try:
            # セッション有効性確認
            if 'user_id' in session:
                # 最終アクセス時刻更新
                session['last_access'] = datetime.now().isoformat()
                session.permanent = True
            
            # Redis接続ヘルスチェック（定期実行）
            if hasattr(request, 'environ') and request.environ.get('wsgi.url_scheme'):
                # 定期ヘルスチェック（5分に1回）
                last_health_check = session.get('last_health_check')
                if not last_health_check or \
                   datetime.now() - datetime.fromisoformat(last_health_check) > timedelta(minutes=5):
                    
                    if not redis_session_manager.health_check():
                        logger.warning("Redis ヘルスチェック失敗 - セッションが不安定な可能性があります")
                        # 必要に応じてフォールバック処理をここに実装
                    
                    session['last_health_check'] = datetime.now().isoformat()
            
        except Exception as e:
            logger.debug(f"セッション監視エラー: {e}")
    
    @app.after_request
    def after_request(response):
        """レスポンス後処理（セッション最適化）"""
        try:
            # セッションサイズ監視
            session_size = len(str(session))
            if session_size > 32000:  # 32KB制限
                logger.warning(f"セッションサイズが大きすぎます: {session_size}バイト")
                # セッション最適化実行
                if hasattr(advanced_session_manager, 'optimize_session'):
                    advanced_session_manager.optimize_session(session)
            
            # セッション統計更新（サンプリング）
            if hasattr(request, 'endpoint') and request.endpoint:
                import random
                if random.random() < 0.1:  # 10%サンプリング
                    try:
                        # 非同期でセッション統計更新
                        pass  # 実装は必要に応じて
                    except:
                        pass
            
        except Exception as e:
            logger.debug(f"セッション後処理エラー: {e}")
        
        return response
    
    @app.errorhandler(500)
    def handle_500_error(e):
        """500エラーハンドリング（セッション関連エラー対応）"""
        try:
            # セッション関連エラーの可能性をチェック
            error_msg = str(e)
            if 'redis' in error_msg.lower() or 'session' in error_msg.lower():
                logger.error(f"セッション関連500エラー: {error_msg}")
                
                # セッションリセット試行
                try:
                    session.clear()
                    logger.info("セッションリセット実行")
                except:
                    pass
                
                return redirect(url_for('index'))
            
        except Exception as handler_error:
            logger.error(f"500エラーハンドラーエラー: {handler_error}")
        
        return jsonify({'error': 'Internal server error'}), 500


def migrate_to_redis_sessions():
    """既存アプリのRedisセッション移行"""
    logger.info("🚀 Redisセッション移行開始...")
    
    try:
        from session_migration_tool import SessionMigrationTool
        
        migration_tool = SessionMigrationTool()
        
        # 現在のシステム分析
        analysis = migration_tool.analyze_current_session_system()
        logger.info(f"分析結果: {analysis['file_sessions']['total_files']}個のファイルセッション検出")
        
        if analysis['file_sessions']['total_files'] > 0:
            # バックアップ作成
            backup_info = migration_tool.create_migration_backup()
            
            if backup_info:
                logger.info(f"バックアップ作成完了: {backup_info['timestamp']}")
                
                # 移行実行
                migration_result = migration_tool.execute_migration()
                
                # レポート生成
                migration_tool.generate_migration_report()
                
                return migration_result
            else:
                logger.error("バックアップ作成失敗 - 移行を中断")
                return None
        else:
            logger.info("移行対象のセッションが見つかりません")
            return {'message': '移行対象なし'}
    
    except Exception as e:
        logger.error(f"セッション移行エラー: {e}")
        return None


# 設定情報表示関数
def print_redis_config_info():
    """Redis設定情報表示"""
    print("\n" + "="*60)
    print("     RCCM Redis セッション管理システム設定")
    print("="*60)
    print(f"Redis Host: {RedisConfig.REDIS_HOST}:{RedisConfig.REDIS_PORT}")
    print(f"Redis DB: {RedisConfig.REDIS_DB}")
    print(f"Session Prefix: {SessionConfig.SESSION_KEY_PREFIX}")
    print(f"Session Lifetime: {SessionConfig.PERMANENT_SESSION_LIFETIME}")
    print(f"Max Connections: {RedisConfig.REDIS_MAX_CONNECTIONS}")
    print(f"Health Check Interval: {RedisConfig.REDIS_HEALTH_CHECK_INTERVAL}秒")
    
    if RedisClusterConfig.REDIS_CLUSTER_ENABLED:
        print("クラスタモード: 有効")
        print(f"クラスタノード: {RedisClusterConfig.REDIS_CLUSTER_NODES}")
    
    if RedisClusterConfig.REDIS_SENTINEL_ENABLED:
        print("Sentinelモード: 有効")
        print(f"Sentinelホスト: {RedisClusterConfig.REDIS_SENTINEL_HOSTS}")
    
    print("="*60)


if __name__ == '__main__':
    # 設定情報表示
    print_redis_config_info()
    
    # Redis統合アプリ作成
    app = create_redis_app(config_name='redis')
    
    # 開発サーバー起動
    try:
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\nアプリケーション終了")
    except Exception as e:
        logger.error(f"アプリケーション起動エラー: {e}")
        print(f"エラー: {e}")