# 🛡️ 副作用ゼロ保証の監視システム
"""
既存機能に一切影響を与えない安全な監視機能
エラーが発生しても既存システムの動作を保護
"""

import logging
import time
import threading
from datetime import datetime
from typing import Optional, Dict, Any

class SafeMonitor:
    """副作用ゼロを保証する監視クラス"""
    
    def __init__(self):
        self.enabled = False  # デフォルト無効
        self.metrics = {}
        self.logger = None
        self._setup_safe_logger()
    
    def _setup_safe_logger(self):
        """安全なロガー設定（既存ログに影響なし）"""
        try:
            self.logger = logging.getLogger('safe_monitor')
            self.logger.setLevel(logging.INFO)
            # ファイルハンドラーは追加のみ（既存に影響なし）
            if not self.logger.handlers:
                handler = logging.FileHandler('safe_monitor.log')
                formatter = logging.Formatter('%(asctime)s - %(message)s')
                handler.setFormatter(formatter)
                self.logger.addHandler(handler)
        except Exception:
            # ログ設定エラーは無視（既存機能を保護）
            self.logger = None
    
    def safe_log(self, message: str):
        """安全なログ出力（エラーでも既存機能に影響なし）"""
        try:
            if self.logger and self.enabled:
                self.logger.info(message)
        except Exception:
            # ログエラーは完全に無視
            pass
    
    def track_memory_usage(self):
        """メモリ使用量監視（読み取り専用）"""
        if not self.enabled:
            return
        
        try:
            import psutil
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            
            self.metrics['memory_usage_mb'] = memory_mb
            self.safe_log(f"Memory usage: {memory_mb:.1f}MB")
            
            # 高メモリ使用を検出（警告のみ）
            if memory_mb > 500:
                self.safe_log(f"⚠️ High memory usage detected: {memory_mb:.1f}MB")
                
        except Exception:
            # メモリ監視エラーは無視
            pass
    
    def track_response_time(self, route: str, duration: float):
        """レスポンス時間追跡（非侵襲的）"""
        if not self.enabled:
            return
        
        try:
            if route not in self.metrics:
                self.metrics[route] = []
            
            self.metrics[route].append({
                'duration': duration,
                'timestamp': datetime.now().isoformat()
            })
            
            # 遅いレスポンスを検出（警告のみ）
            if duration > 2.0:
                self.safe_log(f"⚠️ Slow response: {route} took {duration:.2f}s")
                
        except Exception:
            # 追跡エラーは無視
            pass
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """メトリクス要約（読み取り専用）"""
        try:
            if not self.enabled:
                return {"status": "monitoring_disabled"}
            
            summary = {
                "memory_usage_mb": self.metrics.get('memory_usage_mb', 0),
                "monitored_routes": len([k for k in self.metrics.keys() if k != 'memory_usage_mb']),
                "monitoring_enabled": self.enabled,
                "timestamp": datetime.now().isoformat()
            }
            
            return summary
            
        except Exception:
            # エラー時は安全なデフォルト
            return {"status": "error_occurred", "monitoring_enabled": False}
    
    def enable_monitoring(self):
        """監視機能を有効化（安全に）"""
        try:
            self.enabled = True
            self.safe_log("🔍 Safe monitoring enabled")
        except Exception:
            self.enabled = False
    
    def disable_monitoring(self):
        """監視機能を無効化"""
        try:
            self.enabled = False
            self.safe_log("🔒 Safe monitoring disabled")
        except Exception:
            pass

class SafePerformanceTracker:
    """パフォーマンス追跡（既存機能への影響ゼロ）"""
    
    def __init__(self, monitor: SafeMonitor):
        self.monitor = monitor
        self.start_time = None
    
    def __enter__(self):
        """コンテキストマネージャー開始"""
        try:
            self.start_time = time.time()
        except Exception:
            self.start_time = None
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """コンテキストマネージャー終了"""
        try:
            if self.start_time is not None:
                duration = time.time() - self.start_time
                self.monitor.track_response_time("generic_operation", duration)
        except Exception:
            # エラーは無視（既存機能を保護）
            pass

# グローバルインスタンス（既存コードに影響なし）
safe_monitor = SafeMonitor()

def enable_safe_monitoring():
    """安全な監視機能を有効化"""
    safe_monitor.enable_monitoring()

def disable_safe_monitoring():
    """安全な監視機能を無効化"""
    safe_monitor.disable_monitoring()

def get_safe_metrics():
    """安全なメトリクス取得"""
    return safe_monitor.get_metrics_summary()

# 既存コードで使用可能な安全なデコレーター
def safe_performance_tracking(route_name: str):
    """既存関数に後付け可能な安全なパフォーマンス追跡"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                start_time = time.time()
                result = func(*args, **kwargs)  # 元の関数を必ず実行
                
                # パフォーマンス追跡（エラーでも元の結果を返す）
                try:
                    duration = time.time() - start_time
                    safe_monitor.track_response_time(route_name, duration)
                except Exception:
                    pass  # 追跡エラーは無視
                
                return result
            except Exception as e:
                # 元の関数のエラーはそのまま再発生
                raise e
        return wrapper
    return decorator

# 使用例（既存コードに後から追加可能）
"""
# 既存のapp.pyに以下を追加するだけ
from safe_monitoring import safe_performance_tracking, enable_safe_monitoring

# 監視を有効化（必要に応じて）
# enable_safe_monitoring()

# 既存ルートに後付けで追跡を追加（元の動作は保護）
@app.route('/quiz')
@safe_performance_tracking('quiz_route')
def quiz():
    # 既存コードはそのまま
    pass
"""