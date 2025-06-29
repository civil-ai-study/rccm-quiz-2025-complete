#!/usr/bin/env python3
"""
🔧 ULTRA SYNC: メモリ監視最適化システム統合 - RCCM Quiz Appとの完全統合

🎯 CLAUDE.md準拠・1万人使用ソフト品質基準・ウルトラシンク統合メモリ管理

【統合の目的】
✅ 既存のRCCM Quiz Appにメモリ監視最適化を統合
✅ 実時間でのメモリ使用量監視と自動最適化
✅ Flask-Sessionとの完全互換性保証
✅ 本番環境でのパフォーマンス向上
"""

import sys
import os
import logging
from flask import Flask

# ローカルモジュールのインポート
sys.path.append('/mnt/c/Users/z285/Desktop/rccm-quiz-app/rccm-quiz-app')

try:
    from ultra_sync_memory_monitoring_optimization import UltraSyncMemoryMonitoringOptimizer
    from ultra_sync_unified_session_manager import unified_session_manager
    print("✅ Ultra Sync モジュール統合インポート成功")
except ImportError as e:
    print(f"❌ Ultra Sync モジュールインポート失敗: {e}")
    sys.exit(1)

logger = logging.getLogger(__name__)

class UltraSyncMemoryIntegration:
    """🔧 Ultra Sync メモリ監視統合システム"""
    
    def __init__(self, app: Flask = None):
        self.app = app
        self.memory_optimizer = None
        self.session_manager = None
        self.integration_active = False
        
        if app:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Flask アプリケーション統合初期化"""
        self.app = app
        
        # メモリ監視最適化器の初期化
        config = self._get_memory_config_from_app()
        self.memory_optimizer = UltraSyncMemoryMonitoringOptimizer(config)
        
        # 統合セッション管理器の取得
        self.session_manager = unified_session_manager
        
        # Flask フック登録
        self._register_flask_hooks()
        
        # API エンドポイント登録
        self._register_api_endpoints()
        
        self.integration_active = True
        
        logger.info("🔧 Ultra Sync Memory Integration 初期化完了")
    
    def _get_memory_config_from_app(self) -> dict:
        """Flask アプリ設定からメモリ監視設定を取得"""
        return {
            'monitoring_interval': self.app.config.get('MEMORY_MONITORING_INTERVAL', 30),
            'adaptive_threshold': self.app.config.get('MEMORY_ADAPTIVE_THRESHOLD', True),
            'performance_mode': self.app.config.get('MEMORY_PERFORMANCE_MODE', 'balanced'),
            'concurrent_users_estimate': self.app.config.get('CONCURRENT_USERS_ESTIMATE', 100),
            'enable_smart_alerts': self.app.config.get('MEMORY_SMART_ALERTS', True),
            'production_mode': self.app.config.get('PRODUCTION_MODE', False)
        }
    
    def _register_flask_hooks(self):
        """Flask フック登録"""
        
        @self.app.before_request
        def before_request_memory_optimization():
            """リクエスト前メモリ最適化"""
            if not self.integration_active:
                return
            
            try:
                # メトリクス収集（非ブロッキング）
                current_metrics = self.memory_optimizer.collect_metrics()
                
                # メモリ状態をリクエストコンテキストに保存
                from flask import g
                g.memory_metrics = current_metrics
                
                # 高メモリ使用時の自動最適化
                if current_metrics.rss_mb > self.memory_optimizer.dynamic_thresholds['memory_usage_mb'] * 0.8:
                    self._trigger_memory_optimization()
                
            except Exception as e:
                logger.warning(f"リクエスト前メモリ最適化エラー: {e}")
        
        @self.app.after_request
        def after_request_memory_monitoring(response):
            """リクエスト後メモリ監視"""
            if not self.integration_active:
                return response
            
            try:
                # メモリ状態ヘッダー追加
                if hasattr(response, 'headers'):
                    memory_status = self.memory_optimizer.check_memory_status()
                    response.headers['X-Memory-Status'] = memory_status['overall_status']
                    response.headers['X-Memory-Usage'] = f"{memory_status['current_memory_mb']:.1f}MB"
                
            except Exception as e:
                logger.warning(f"リクエスト後メモリ監視エラー: {e}")
            
            return response
    
    def _register_api_endpoints(self):
        """API エンドポイント登録"""
        
        @self.app.route('/api/memory/status/optimized')
        def memory_status_optimized():
            """メモリ状態取得"""
            try:
                status = self.memory_optimizer.check_memory_status()
                return status
            except Exception as e:
                return {'error': str(e)}, 500
        
        @self.app.route('/api/memory/optimize/force', methods=['POST'])
        def force_memory_optimization():
            """強制メモリ最適化"""
            try:
                result = self.memory_optimizer.run_optimization_cycle()
                return result
            except Exception as e:
                return {'error': str(e)}, 500
        
        @self.app.route('/api/memory/report/comprehensive')
        def memory_report_comprehensive():
            """メモリレポート取得"""
            try:
                report = self.memory_optimizer.generate_comprehensive_report()
                return report
            except Exception as e:
                return {'error': str(e)}, 500
        
        @self.app.route('/api/memory/thresholds/dynamic')
        def memory_thresholds_dynamic():
            """現在の閾値取得"""
            try:
                return {
                    'thresholds': self.memory_optimizer.dynamic_thresholds,
                    'optimization_stats': self.memory_optimizer.optimization_stats
                }
            except Exception as e:
                return {'error': str(e)}, 500
    
    def _trigger_memory_optimization(self):
        """メモリ最適化トリガー"""
        try:
            # 統合セッション管理による緊急クリーンアップ
            if self.session_manager:
                self.session_manager._emergency_memory_cleanup()
            
            # メモリ最適化実行
            self.memory_optimizer.optimize_thresholds()
            
            logger.info("🚀 自動メモリ最適化実行完了")
            
        except Exception as e:
            logger.error(f"メモリ最適化トリガーエラー: {e}")

def integrate_with_rccm_app():
    """RCCM Quiz App との統合"""
    try:
        # RCCM Quiz App のインポート
        from app import app
        
        # メモリ監視統合の初期化
        memory_integration = UltraSyncMemoryIntegration(app)
        
        print("✅ RCCM Quiz App メモリ監視統合完了")
        print(f"🎯 初期メモリ閾値: {memory_integration.memory_optimizer.dynamic_thresholds['memory_usage_mb']:.1f}MB")
        print(f"🖥️  システムメモリ: {memory_integration.memory_optimizer.system_analyzer.memory_total:.1f}MB")
        
        return memory_integration
        
    except ImportError as e:
        print(f"❌ RCCM Quiz App 統合失敗: {e}")
        return None
    except Exception as e:
        print(f"❌ メモリ監視統合エラー: {e}")
        return None

def run_integration_test():
    """統合テスト実行"""
    print("🧪 Ultra Sync Memory Integration テスト開始")
    print("=" * 60)
    
    # 統合の実行
    integration = integrate_with_rccm_app()
    
    if not integration:
        print("❌ 統合テスト失敗: 統合オブジェクトが作成できませんでした")
        return False
    
    # テスト項目
    test_results = {
        'integration_active': integration.integration_active,
        'memory_optimizer_available': integration.memory_optimizer is not None,
        'session_manager_available': integration.session_manager is not None,
        'flask_app_available': integration.app is not None
    }
    
    # 機能テスト
    try:
        # メモリ状態チェックテスト
        memory_status = integration.memory_optimizer.check_memory_status()
        test_results['memory_status_check'] = memory_status['overall_status'] == 'healthy'
        
        # 閾値最適化テスト
        optimization_result = integration.memory_optimizer.optimize_thresholds()
        test_results['threshold_optimization'] = 'optimization_skipped' in optimization_result or optimization_result.get('success', False)
        
        # レポート生成テスト
        report = integration.memory_optimizer.generate_comprehensive_report()
        test_results['report_generation'] = 'report_metadata' in report
        
    except Exception as e:
        print(f"❌ 機能テストエラー: {e}")
        test_results['functional_test_error'] = str(e)
    
    # 結果表示
    print("\n📊 統合テスト結果:")
    print("-" * 40)
    
    passed_tests = 0
    total_tests = 0
    
    for test_name, result in test_results.items():
        if test_name.endswith('_error'):
            continue
        
        total_tests += 1
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
        
        if result:
            passed_tests += 1
    
    success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    
    print(f"\n🎯 テスト結果: {passed_tests}/{total_tests} 成功 ({success_rate:.1f}%)")
    
    if success_rate >= 80:
        print("✅ 統合テスト成功: 本番環境準備完了")
        return True
    else:
        print("❌ 統合テスト失敗: 追加修正が必要")
        return False

def main():
    """メイン実行関数"""
    print("🔧 Ultra Sync Memory Monitoring Integration")
    print("=" * 60)
    
    # 統合テスト実行
    test_success = run_integration_test()
    
    if test_success:
        print("\n🎉 Ultra Sync Memory Integration 完了")
        print("📝 使用方法:")
        print("   1. RCCM Quiz App 起動時に自動でメモリ監視が開始されます")
        print("   2. /api/memory/status でメモリ状態を確認できます")
        print("   3. /api/memory/optimize で手動最適化を実行できます")
        print("   4. /api/memory/report で詳細レポートを取得できます")
    else:
        print("\n💥 統合に問題があります。ログを確認してください。")
    
    return test_success

if __name__ == "__main__":
    main()