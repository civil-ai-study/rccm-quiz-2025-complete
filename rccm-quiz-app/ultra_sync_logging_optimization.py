#!/usr/bin/env python3
"""
🧹 ULTRA SYNC: ログ出力最適化システム - 本番環境パフォーマンス改善

🎯 CLAUDE.md準拠・1万人使用ソフト品質基準・ウルトラシンクログ最適化

【本番環境ログ問題の分析】
❌ 現在の問題点:
- 大量のDEBUGログによるパフォーマンス劣化
- ディスク容量の急激な消費
- ログローテーション不備による運用問題
- 本番環境に不適切な詳細ログ出力

【ウルトラシンク解決策】
✅ 環境別ログレベル自動調整
✅ 構造化ログによる効率的な出力
✅ 非同期ログ処理によるパフォーマンス向上
✅ 自動ログローテーション・圧縮
✅ 重要度別フィルタリング機能
"""

import os
import sys
import logging
import logging.handlers
import json
import time
import threading
import queue
import gzip
import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import psutil
import traceback
from contextlib import contextmanager
from dataclasses import dataclass, asdict
from enum import Enum

class LogLevel(Enum):
    """ログレベル定義"""
    CRITICAL = 50
    ERROR = 40
    WARNING = 30
    INFO = 20
    DEBUG = 10
    NOTSET = 0

class EnvironmentType(Enum):
    """環境タイプ定義"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"

@dataclass
class LogMetrics:
    """ログメトリクス"""
    timestamp: float
    level: str
    message_length: int
    module: str
    function: str
    line_number: int
    thread_id: int
    process_id: int
    memory_usage_mb: float
    execution_time_ms: Optional[float] = None

class UltraSyncLogOptimizer:
    """
    🧹 Ultra Sync ログ最適化システム
    
    本番環境でのパフォーマンス向上を目的とした
    高度なログ管理・最適化システム
    """
    
    def __init__(self, environment: str = None, config: Dict = None):
        # 🔥 ULTRA SYNC: 環境検出・設定
        self.environment = self._detect_environment(environment)
        self.config = self._init_config(config)
        
        # 📊 パフォーマンス監視
        self.metrics = {
            'logs_processed': 0,
            'logs_filtered': 0,
            'logs_compressed': 0,
            'total_log_size_mb': 0,
            'performance_gains_ms': 0,
            'last_optimization': None
        }
        
        # 🚀 非同期ログ処理
        self.async_queue = queue.Queue(maxsize=self.config['async_queue_size'])
        self.async_worker = None
        self.async_worker_running = False
        
        # 🔄 ログローテーション
        self.rotation_handler = None
        
        # 📝 構造化ログフォーマッター
        self.structured_formatter = None
        
        # 🎯 フィルタリングシステム
        self.performance_filter = None
        self.environment_filter = None
        
        # 初期化実行
        self._initialize_optimization()
        
        print(f"🧹 Ultra Sync Log Optimizer 初期化完了 ({self.environment.value}環境)")
    
    def _detect_environment(self, environment: str = None) -> EnvironmentType:
        """環境自動検出"""
        if environment:
            try:
                return EnvironmentType(environment.lower())
            except ValueError:
                pass
        
        # 環境変数による検出
        env_mappings = {
            'FLASK_ENV': {
                'production': EnvironmentType.PRODUCTION,
                'staging': EnvironmentType.STAGING,
                'testing': EnvironmentType.TESTING,
                'development': EnvironmentType.DEVELOPMENT
            },
            'RCCM_ENV': {
                'prod': EnvironmentType.PRODUCTION,
                'stage': EnvironmentType.STAGING,
                'test': EnvironmentType.TESTING,
                'dev': EnvironmentType.DEVELOPMENT
            }
        }
        
        for env_var, mappings in env_mappings.items():
            env_value = os.environ.get(env_var, '').lower()
            if env_value in mappings:
                return mappings[env_value]
        
        # デフォルト: 本番環境の存在ファイルで判定
        production_indicators = [
            '/etc/rccm-production',
            '/var/log/rccm',
            'gunicorn.pid'
        ]
        
        if any(os.path.exists(indicator) for indicator in production_indicators):
            return EnvironmentType.PRODUCTION
        
        # フォールバック: 開発環境
        return EnvironmentType.DEVELOPMENT
    
    def _init_config(self, config: Dict = None) -> Dict[str, Any]:
        """設定初期化"""
        default_config = {
            # 環境別ログレベル
            'log_levels': {
                EnvironmentType.DEVELOPMENT: LogLevel.DEBUG,
                EnvironmentType.TESTING: LogLevel.INFO,
                EnvironmentType.STAGING: LogLevel.WARNING,
                EnvironmentType.PRODUCTION: LogLevel.ERROR
            },
            
            # パフォーマンス設定
            'async_logging': True,
            'async_queue_size': 1000,
            'batch_size': 100,
            'flush_interval': 5.0,
            
            # ローテーション設定
            'max_file_size_mb': 50,
            'backup_count': 10,
            'compression_enabled': True,
            
            # フィルタリング設定
            'performance_filtering': True,
            'debug_sampling_rate': 0.1,  # DEBUG: 10%のみ出力
            'info_sampling_rate': 0.5,   # INFO: 50%のみ出力
            
            # 構造化ログ設定
            'structured_logging': True,
            'include_metrics': True,
            'include_context': True,
            
            # ディスク使用量制限
            'max_total_log_size_gb': 5,
            'cleanup_older_than_days': 30
        }
        
        if config:
            default_config.update(config)
        
        return default_config
    
    def _initialize_optimization(self):
        """最適化システム初期化"""
        try:
            # 構造化フォーマッター作成
            self._create_structured_formatter()
            
            # フィルタ作成
            self._create_filters()
            
            # ローテーションハンドラー作成
            self._create_rotation_handler()
            
            # 非同期ワーカー開始
            if self.config['async_logging']:
                self._start_async_worker()
            
            print("✅ ログ最適化システム初期化完了")
            
        except Exception as e:
            print(f"❌ ログ最適化システム初期化失敗: {e}")
            raise
    
    def _create_structured_formatter(self):
        """構造化ログフォーマッター作成"""
        class UltraSyncStructuredFormatter(logging.Formatter):
            def __init__(self, include_metrics=True, include_context=True):
                super().__init__()
                self.include_metrics = include_metrics
                self.include_context = include_context
            
            def format(self, record):
                # 基本ログデータ
                log_data = {
                    'timestamp': datetime.datetime.fromtimestamp(record.created).isoformat(),
                    'level': record.levelname,
                    'message': record.getMessage(),
                    'module': record.module,
                    'function': record.funcName,
                    'line': record.lineno
                }
                
                # メトリクス追加
                if self.include_metrics:
                    try:
                        process = psutil.Process()
                        log_data['metrics'] = {
                            'memory_mb': round(process.memory_info().rss / (1024 * 1024), 2),
                            'cpu_percent': process.cpu_percent(),
                            'thread_count': threading.active_count()
                        }
                    except:
                        pass
                
                # コンテキスト追加
                if self.include_context and hasattr(record, 'extra_context'):
                    log_data['context'] = record.extra_context
                
                # 例外情報追加
                if record.exc_info:
                    log_data['exception'] = self.formatException(record.exc_info)
                
                return json.dumps(log_data, ensure_ascii=False)
        
        self.structured_formatter = UltraSyncStructuredFormatter(
            include_metrics=self.config['include_metrics'],
            include_context=self.config['include_context']
        )
    
    def _create_filters(self):
        """フィルタ作成"""
        class PerformanceFilter(logging.Filter):
            def __init__(self, config):
                super().__init__()
                self.config = config
                self.debug_counter = 0
                self.info_counter = 0
            
            def filter(self, record):
                # 本番環境でのサンプリング
                if record.levelno == LogLevel.DEBUG.value:
                    self.debug_counter += 1
                    if self.debug_counter % int(1/self.config['debug_sampling_rate']) != 0:
                        return False
                
                elif record.levelno == LogLevel.INFO.value:
                    self.info_counter += 1
                    if self.info_counter % int(1/self.config['info_sampling_rate']) != 0:
                        return False
                
                return True
        
        class EnvironmentFilter(logging.Filter):
            def __init__(self, environment, min_level):
                super().__init__()
                self.environment = environment
                self.min_level = min_level.value
            
            def filter(self, record):
                # 環境別ログレベルフィルタ
                return record.levelno >= self.min_level
        
        # フィルタ作成
        if self.config['performance_filtering']:
            self.performance_filter = PerformanceFilter(self.config)
        
        min_level = self.config['log_levels'][self.environment]
        self.environment_filter = EnvironmentFilter(self.environment, min_level)
    
    def _create_rotation_handler(self):
        """ローテーションハンドラー作成"""
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / f'rccm_app_{self.environment.value}.log'
        
        # サイズベースローテーション
        max_bytes = self.config['max_file_size_mb'] * 1024 * 1024
        backup_count = self.config['backup_count']
        
        self.rotation_handler = logging.handlers.RotatingFileHandler(
            filename=str(log_file),
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        
        # フォーマッター設定
        if self.config['structured_logging']:
            self.rotation_handler.setFormatter(self.structured_formatter)
        else:
            # 従来フォーマット
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            self.rotation_handler.setFormatter(formatter)
        
        # フィルタ適用
        if self.environment_filter:
            self.rotation_handler.addFilter(self.environment_filter)
        
        if self.performance_filter:
            self.rotation_handler.addFilter(self.performance_filter)
    
    def _start_async_worker(self):
        """非同期ログワーカー開始"""
        self.async_worker_running = True
        
        def async_log_worker():
            batch = []
            last_flush = time.time()
            
            while self.async_worker_running:
                try:
                    # バッチ処理
                    try:
                        record = self.async_queue.get(timeout=1.0)
                        batch.append(record)
                        
                        # バッチサイズまたは時間経過でフラッシュ
                        if (len(batch) >= self.config['batch_size'] or 
                            time.time() - last_flush >= self.config['flush_interval']):
                            
                            self._flush_batch(batch)
                            batch.clear()
                            last_flush = time.time()
                            
                    except queue.Empty:
                        # タイムアウト時も定期フラッシュ
                        if batch and time.time() - last_flush >= self.config['flush_interval']:
                            self._flush_batch(batch)
                            batch.clear()
                            last_flush = time.time()
                
                except Exception as e:
                    print(f"❌ 非同期ログワーカーエラー: {e}")
            
            # 終了時に残りをフラッシュ
            if batch:
                self._flush_batch(batch)
        
        self.async_worker = threading.Thread(target=async_log_worker, daemon=True)
        self.async_worker.start()
    
    def _flush_batch(self, batch: List[logging.LogRecord]):
        """バッチログフラッシュ"""
        try:
            for record in batch:
                if self.rotation_handler:
                    self.rotation_handler.emit(record)
                self.metrics['logs_processed'] += 1
        except Exception as e:
            print(f"❌ バッチフラッシュエラー: {e}")
    
    def optimize_existing_loggers(self) -> Dict[str, Any]:
        """既存ロガーの最適化"""
        optimization_results = {
            'optimized_loggers': [],
            'performance_improvements': {},
            'errors': []
        }
        
        try:
            # 全ロガーを取得
            loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict]
            loggers.append(logging.getLogger())  # rootロガー
            
            for logger in loggers:
                try:
                    logger_name = logger.name or 'root'
                    
                    # 既存ハンドラーのバックアップ
                    original_handlers = logger.handlers.copy()
                    
                    # 最適化されたハンドラーに置き換え
                    if self.rotation_handler:
                        # 古いハンドラーを削除
                        for handler in original_handlers:
                            logger.removeHandler(handler)
                        
                        # 最適化されたハンドラーを追加
                        logger.addHandler(self.rotation_handler)
                        
                        # ログレベル設定
                        min_level = self.config['log_levels'][self.environment]
                        logger.setLevel(min_level.value)
                        
                        optimization_results['optimized_loggers'].append(logger_name)
                
                except Exception as e:
                    optimization_results['errors'].append(f"ロガー {logger_name} 最適化失敗: {e}")
            
            print(f"✅ ロガー最適化完了: {len(optimization_results['optimized_loggers'])}個")
            return optimization_results
            
        except Exception as e:
            optimization_results['errors'].append(f"ロガー最適化エラー: {e}")
            return optimization_results
    
    def create_optimized_logger(self, name: str, **kwargs) -> logging.Logger:
        """最適化されたロガー作成"""
        logger = logging.getLogger(name)
        
        # 既存ハンドラーをクリア
        logger.handlers.clear()
        
        # 最適化されたハンドラーを追加
        if self.rotation_handler:
            logger.addHandler(self.rotation_handler)
        
        # ログレベル設定
        min_level = self.config['log_levels'][self.environment]
        logger.setLevel(min_level.value)
        
        # 非同期ログ対応
        if self.config['async_logging']:
            original_handle = logger.handle
            
            def async_handle(record):
                try:
                    self.async_queue.put_nowait(record)
                except queue.Full:
                    # キューが満杯の場合は同期処理
                    original_handle(record)
            
            logger.handle = async_handle
        
        return logger
    
    @contextmanager
    def performance_logging_context(self, operation_name: str):
        """パフォーマンス測定付きログコンテキスト"""
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / (1024 * 1024)
        
        try:
            yield
        finally:
            end_time = time.time()
            end_memory = psutil.Process().memory_info().rss / (1024 * 1024)
            
            execution_time = (end_time - start_time) * 1000  # ms
            memory_delta = end_memory - start_memory
            
            # パフォーマンスログ
            perf_logger = self.create_optimized_logger('performance')
            perf_logger.info(f"Operation: {operation_name}, Duration: {execution_time:.2f}ms, Memory: {memory_delta:+.2f}MB")
    
    def cleanup_old_logs(self) -> Dict[str, Any]:
        """古いログファイルクリーンアップ"""
        cleanup_results = {
            'deleted_files': [],
            'freed_space_mb': 0,
            'errors': []
        }
        
        try:
            log_dir = Path('logs')
            if not log_dir.exists():
                return cleanup_results
            
            cutoff_date = datetime.datetime.now() - datetime.timedelta(
                days=self.config['cleanup_older_than_days']
            )
            
            for log_file in log_dir.glob('*.log*'):
                try:
                    file_mtime = datetime.datetime.fromtimestamp(log_file.stat().st_mtime)
                    
                    if file_mtime < cutoff_date:
                        file_size = log_file.stat().st_size
                        log_file.unlink()
                        
                        cleanup_results['deleted_files'].append(str(log_file))
                        cleanup_results['freed_space_mb'] += file_size / (1024 * 1024)
                
                except Exception as e:
                    cleanup_results['errors'].append(f"ファイル削除失敗 {log_file}: {e}")
            
            print(f"🧹 ログクリーンアップ完了: {len(cleanup_results['deleted_files'])}ファイル, {cleanup_results['freed_space_mb']:.1f}MB削除")
            return cleanup_results
            
        except Exception as e:
            cleanup_results['errors'].append(f"クリーンアップエラー: {e}")
            return cleanup_results
    
    def compress_old_logs(self) -> Dict[str, Any]:
        """古いログファイル圧縮"""
        compression_results = {
            'compressed_files': [],
            'compression_ratio': 0,
            'space_saved_mb': 0,
            'errors': []
        }
        
        if not self.config['compression_enabled']:
            return compression_results
        
        try:
            log_dir = Path('logs')
            if not log_dir.exists():
                return compression_results
            
            # 1日以上古いログファイルを圧縮
            cutoff_date = datetime.datetime.now() - datetime.timedelta(days=1)
            
            for log_file in log_dir.glob('*.log.*'):
                if log_file.suffix == '.gz':
                    continue  # 既に圧縮済み
                
                try:
                    file_mtime = datetime.datetime.fromtimestamp(log_file.stat().st_mtime)
                    
                    if file_mtime < cutoff_date:
                        original_size = log_file.stat().st_size
                        compressed_file = log_file.with_suffix(log_file.suffix + '.gz')
                        
                        # gzip圧縮
                        with open(log_file, 'rb') as f_in:
                            with gzip.open(compressed_file, 'wb') as f_out:
                                f_out.write(f_in.read())
                        
                        compressed_size = compressed_file.stat().st_size
                        space_saved = (original_size - compressed_size) / (1024 * 1024)
                        
                        # 元ファイル削除
                        log_file.unlink()
                        
                        compression_results['compressed_files'].append(str(log_file))
                        compression_results['space_saved_mb'] += space_saved
                        
                        self.metrics['logs_compressed'] += 1
                
                except Exception as e:
                    compression_results['errors'].append(f"圧縮失敗 {log_file}: {e}")
            
            # 圧縮率計算
            if compression_results['compressed_files']:
                compression_results['compression_ratio'] = compression_results['space_saved_mb'] / len(compression_results['compressed_files'])
            
            print(f"🗜️ ログ圧縮完了: {len(compression_results['compressed_files'])}ファイル, {compression_results['space_saved_mb']:.1f}MB節約")
            return compression_results
            
        except Exception as e:
            compression_results['errors'].append(f"圧縮エラー: {e}")
            return compression_results
    
    def get_optimization_report(self) -> Dict[str, Any]:
        """最適化レポート生成"""
        return {
            'environment': self.environment.value,
            'configuration': self.config,
            'metrics': self.metrics,
            'performance_improvements': {
                'async_logging_enabled': self.config['async_logging'],
                'structured_logging_enabled': self.config['structured_logging'],
                'performance_filtering_enabled': self.config['performance_filtering'],
                'compression_enabled': self.config['compression_enabled']
            },
            'recommendations': self._generate_recommendations()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """改善推奨事項生成"""
        recommendations = []
        
        # 環境別推奨事項
        if self.environment == EnvironmentType.PRODUCTION:
            if self.config['log_levels'][self.environment] == LogLevel.DEBUG:
                recommendations.append("本番環境でDEBUGログが有効です。ERRORレベルに変更することを推奨します。")
            
            if not self.config['async_logging']:
                recommendations.append("本番環境では非同期ログ処理の有効化を推奨します。")
        
        # パフォーマンス推奨事項
        if self.metrics['logs_processed'] > 10000 and not self.config['compression_enabled']:
            recommendations.append("大量のログが生成されています。圧縮機能の有効化を推奨します。")
        
        return recommendations
    
    def shutdown(self):
        """最適化システム終了"""
        print("🧹 ログ最適化システム終了中...")
        
        # 非同期ワーカー停止
        if self.async_worker_running:
            self.async_worker_running = False
            if self.async_worker:
                self.async_worker.join(timeout=5.0)
        
        # 最終クリーンアップ
        self.cleanup_old_logs()
        self.compress_old_logs()
        
        print("✅ ログ最適化システム終了完了")

def integrate_with_rccm_app():
    """RCCM Quiz App との統合"""
    try:
        # 環境検出
        environment = os.environ.get('FLASK_ENV', 'production')
        
        # ログ最適化システム初期化
        log_optimizer = UltraSyncLogOptimizer(environment=environment)
        
        # 既存ロガーの最適化
        optimization_results = log_optimizer.optimize_existing_loggers()
        
        print("✅ RCCM Quiz App ログ最適化統合完了")
        print(f"📊 最適化されたロガー: {len(optimization_results['optimized_loggers'])}個")
        
        return log_optimizer
        
    except Exception as e:
        print(f"❌ ログ最適化統合失敗: {e}")
        return None

def main():
    """メイン実行関数"""
    print("🧹 Ultra Sync Logging Optimization System")
    print("=" * 60)
    
    # ログ最適化システム作成
    log_optimizer = UltraSyncLogOptimizer()
    
    # RCCM Quiz App 統合
    integration_result = integrate_with_rccm_app()
    
    if integration_result:
        # 最適化レポート表示
        report = integration_result.get_optimization_report()
        
        print(f"\n📊 最適化レポート:")
        print(f"   環境: {report['environment']}")
        print(f"   非同期ログ: {'✅' if report['configuration']['async_logging'] else '❌'}")
        print(f"   構造化ログ: {'✅' if report['configuration']['structured_logging'] else '❌'}")
        print(f"   パフォーマンスフィルタ: {'✅' if report['configuration']['performance_filtering'] else '❌'}")
        print(f"   圧縮機能: {'✅' if report['configuration']['compression_enabled'] else '❌'}")
        
        print(f"\n📈 処理統計:")
        print(f"   処理済みログ: {report['metrics']['logs_processed']}")
        print(f"   フィルタ済みログ: {report['metrics']['logs_filtered']}")
        print(f"   圧縮済みログ: {report['metrics']['logs_compressed']}")
        
        # 推奨事項表示
        if report['recommendations']:
            print(f"\n💡 推奨事項:")
            for rec in report['recommendations']:
                print(f"   - {rec}")
        
        # クリーンアップ・圧縮実行
        print(f"\n🧹 メンテナンス実行:")
        cleanup_result = integration_result.cleanup_old_logs()
        compression_result = integration_result.compress_old_logs()
        
        print(f"   削除ファイル: {len(cleanup_result['deleted_files'])}")
        print(f"   解放容量: {cleanup_result['freed_space_mb']:.1f}MB")
        print(f"   圧縮ファイル: {len(compression_result['compressed_files'])}")
        print(f"   節約容量: {compression_result['space_saved_mb']:.1f}MB")
    
    print("\n🎉 Ultra Sync Logging Optimization 完了")

if __name__ == "__main__":
    main()