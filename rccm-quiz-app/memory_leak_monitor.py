#!/usr/bin/env python3
"""
🔍 Memory Leak Monitoring System - Ultra Sync Implementation
RCCM試験問題集アプリ - 包括的メモリリーク監視とレポート機能

🎯 主要機能:
- リアルタイムメモリリーク検出
- 詳細なメモリ使用量分析
- 自動メモリ最適化
- 包括的レポート生成
- ダッシュボード形式の監視
"""

import gc
import psutil
import os
import threading
import time
import json
import logging
from datetime import datetime, timedelta
from collections import deque, defaultdict
from typing import Dict, List, Any, Optional, Tuple
from functools import wraps
import traceback

logger = logging.getLogger(__name__)

class MemoryLeakMonitor:
    """🔍 包括的メモリリーク監視システム"""
    
    def __init__(self, monitoring_interval=30, history_size=100):
        self.monitoring_interval = monitoring_interval  # 監視間隔（秒）
        self.history_size = history_size  # 履歴保持サイズ
        
        # メモリ使用量履歴
        self.memory_history = deque(maxlen=history_size)
        self.leak_detections = deque(maxlen=50)  # リーク検出履歴
        
        # 統計データ
        self.session_memory_usage = defaultdict(list)  # セッション別メモリ使用量
        self.route_memory_usage = defaultdict(list)    # ルート別メモリ使用量
        self.function_memory_usage = defaultdict(list) # 関数別メモリ使用量
        
        # 監視制御
        self.monitoring_active = False
        self.monitor_thread = None
        self.lock = threading.Lock()
        
        # リーク検出設定
        self.leak_threshold_mb = 50  # メモリリーク判定閾値（MB）
        self.leak_detection_window = 10  # 監視ウィンドウ（データポイント数）
        
        # アラート設定
        self.alert_callbacks = []
        
        logger.info("Memory Leak Monitor initialized")
    
    def start_monitoring(self):
        """🚀 メモリ監視開始"""
        if self.monitoring_active:
            logger.warning("Memory monitoring already active")
            return
        
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("Memory leak monitoring started")
    
    def stop_monitoring(self):
        """⏹️ メモリ監視停止"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("Memory leak monitoring stopped")
    
    def _monitoring_loop(self):
        """🔄 メモリ監視メインループ"""
        while self.monitoring_active:
            try:
                self._collect_memory_data()
                self._detect_memory_leaks()
                time.sleep(self.monitoring_interval)
            except Exception as e:
                logger.error(f"Memory monitoring loop error: {e}")
                time.sleep(self.monitoring_interval)
    
    def _collect_memory_data(self):
        """📊 メモリデータ収集"""
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            memory_percent = psutil.virtual_memory().percent
            
            # ガベージコレクション統計
            gc_stats = gc.get_stats()
            gc_counts = gc.get_count()
            
            # メモリデータポイント作成
            data_point = {
                'timestamp': datetime.now().isoformat(),
                'memory_mb': memory_info.rss / 1024 / 1024,
                'memory_percent': memory_percent,
                'gc_generation_0': gc_counts[0],
                'gc_generation_1': gc_counts[1],
                'gc_generation_2': gc_counts[2],
                'gc_collections': sum(stat['collections'] for stat in gc_stats),
                'gc_collected': sum(stat['collected'] for stat in gc_stats),
                'thread_count': threading.active_count(),
                'file_descriptors': len(process.open_files()) if hasattr(process, 'open_files') else 0
            }
            
            with self.lock:
                self.memory_history.append(data_point)
            
            logger.debug(f"Memory data collected: {data_point['memory_mb']:.1f}MB ({data_point['memory_percent']:.1f}%)")
            
        except Exception as e:
            logger.error(f"Failed to collect memory data: {e}")
    
    def _detect_memory_leaks(self):
        """🚨 メモリリーク検出"""
        if len(self.memory_history) < self.leak_detection_window:
            return
        
        try:
            # 最近のメモリ使用量を分析
            recent_data = list(self.memory_history)[-self.leak_detection_window:]
            memory_values = [point['memory_mb'] for point in recent_data]
            
            # トレンド分析
            if len(memory_values) >= 3:
                # 直線的増加を検出
                increasing_trend = self._calculate_trend(memory_values)
                
                # 急激な増加を検出
                memory_increase = memory_values[-1] - memory_values[0]
                time_span = (datetime.fromisoformat(recent_data[-1]['timestamp']) - 
                           datetime.fromisoformat(recent_data[0]['timestamp'])).total_seconds() / 60
                
                # リーク判定
                leak_detected = False
                leak_severity = 'none'
                leak_description = ''
                
                if increasing_trend > 0.5 and memory_increase > self.leak_threshold_mb:
                    leak_detected = True
                    leak_severity = 'high'
                    leak_description = f"High memory leak: {memory_increase:.1f}MB increase over {time_span:.1f} minutes"
                elif increasing_trend > 0.3 and memory_increase > self.leak_threshold_mb * 0.5:
                    leak_detected = True
                    leak_severity = 'medium'
                    leak_description = f"Medium memory leak: {memory_increase:.1f}MB increase over {time_span:.1f} minutes"
                elif memory_increase > self.leak_threshold_mb * 2:
                    leak_detected = True
                    leak_severity = 'critical'
                    leak_description = f"Critical memory spike: {memory_increase:.1f}MB sudden increase"
                
                if leak_detected:
                    leak_event = {
                        'timestamp': datetime.now().isoformat(),
                        'severity': leak_severity,
                        'description': leak_description,
                        'memory_increase_mb': memory_increase,
                        'time_span_minutes': time_span,
                        'trend_score': increasing_trend,
                        'current_memory_mb': memory_values[-1],
                        'gc_stats': recent_data[-1]
                    }
                    
                    with self.lock:
                        self.leak_detections.append(leak_event)
                    
                    logger.warning(f"Memory leak detected: {leak_description}")
                    self._trigger_alerts(leak_event)
        
        except Exception as e:
            logger.error(f"Memory leak detection error: {e}")
    
    def _calculate_trend(self, values: List[float]) -> float:
        """📈 メモリ使用量のトレンド計算"""
        if len(values) < 2:
            return 0.0
        
        # 単純な線形回帰でトレンドを計算
        n = len(values)
        x_sum = sum(range(n))
        y_sum = sum(values)
        xy_sum = sum(i * v for i, v in enumerate(values))
        x2_sum = sum(i * i for i in range(n))
        
        # 傾き計算
        denominator = n * x2_sum - x_sum * x_sum
        if denominator == 0:
            return 0.0
        
        slope = (n * xy_sum - x_sum * y_sum) / denominator
        return slope
    
    def _trigger_alerts(self, leak_event: Dict[str, Any]):
        """🚨 アラート発火"""
        for callback in self.alert_callbacks:
            try:
                callback(leak_event)
            except Exception as e:
                logger.error(f"Alert callback error: {e}")
    
    def add_alert_callback(self, callback):
        """📢 アラートコールバック追加"""
        self.alert_callbacks.append(callback)
    
    def record_function_memory_usage(self, function_name: str, memory_usage_mb: float):
        """📊 関数別メモリ使用量記録"""
        with self.lock:
            self.function_memory_usage[function_name].append({
                'timestamp': datetime.now().isoformat(),
                'memory_mb': memory_usage_mb
            })
            
            # 履歴サイズ制限
            if len(self.function_memory_usage[function_name]) > 50:
                self.function_memory_usage[function_name] = self.function_memory_usage[function_name][-50:]
    
    def record_route_memory_usage(self, route: str, memory_usage_mb: float):
        """🛣️ ルート別メモリ使用量記録"""
        with self.lock:
            self.route_memory_usage[route].append({
                'timestamp': datetime.now().isoformat(),
                'memory_mb': memory_usage_mb
            })
            
            # 履歴サイズ制限
            if len(self.route_memory_usage[route]) > 100:
                self.route_memory_usage[route] = self.route_memory_usage[route][-100:]
    
    def record_session_memory_usage(self, session_id: str, memory_usage_mb: float):
        """👤 セッション別メモリ使用量記録"""
        with self.lock:
            self.session_memory_usage[session_id].append({
                'timestamp': datetime.now().isoformat(),
                'memory_mb': memory_usage_mb
            })
            
            # 履歴サイズ制限
            if len(self.session_memory_usage[session_id]) > 30:
                self.session_memory_usage[session_id] = self.session_memory_usage[session_id][-30:]
    
    def get_memory_status(self) -> Dict[str, Any]:
        """📊 現在のメモリ状況取得"""
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            
            with self.lock:
                recent_leaks = list(self.leak_detections)[-10:]  # 最新10件のリーク
                memory_data = list(self.memory_history)[-10:]   # 最新10件のメモリデータ
            
            return {
                'current_memory_mb': memory_info.rss / 1024 / 1024,
                'memory_percent': psutil.virtual_memory().percent,
                'monitoring_active': self.monitoring_active,
                'recent_leaks': recent_leaks,
                'recent_memory_data': memory_data,
                'total_leaks_detected': len(self.leak_detections),
                'monitoring_duration_hours': len(self.memory_history) * self.monitoring_interval / 3600,
                'gc_counts': gc.get_count(),
                'thread_count': threading.active_count()
            }
        except Exception as e:
            logger.error(f"Failed to get memory status: {e}")
            return {'error': str(e)}
    
    def get_detailed_analysis(self) -> Dict[str, Any]:
        """🔬 詳細メモリ分析"""
        try:
            with self.lock:
                # 全履歴のコピー
                memory_data = list(self.memory_history)
                leaks = list(self.leak_detections)
                function_usage = dict(self.function_memory_usage)
                route_usage = dict(self.route_memory_usage)
                session_usage = dict(self.session_memory_usage)
            
            if not memory_data:
                return {'error': 'No memory data available'}
            
            # メモリ使用量統計
            memory_values = [point['memory_mb'] for point in memory_data]
            memory_stats = {
                'min_mb': min(memory_values),
                'max_mb': max(memory_values),
                'avg_mb': sum(memory_values) / len(memory_values),
                'current_mb': memory_values[-1] if memory_values else 0,
                'trend': self._calculate_trend(memory_values[-20:]) if len(memory_values) >= 20 else 0
            }
            
            # リーク統計
            leak_stats = {
                'total_leaks': len(leaks),
                'critical_leaks': len([l for l in leaks if l.get('severity') == 'critical']),
                'high_leaks': len([l for l in leaks if l.get('severity') == 'high']),
                'medium_leaks': len([l for l in leaks if l.get('severity') == 'medium'])
            }
            
            # 関数別メモリ使用量TOP 10
            function_avg_usage = {}
            for func_name, usage_list in function_usage.items():
                if usage_list:
                    avg_usage = sum(u['memory_mb'] for u in usage_list) / len(usage_list)
                    function_avg_usage[func_name] = avg_usage
            
            top_functions = sorted(function_avg_usage.items(), key=lambda x: x[1], reverse=True)[:10]
            
            # ルート別メモリ使用量TOP 10
            route_avg_usage = {}
            for route_name, usage_list in route_usage.items():
                if usage_list:
                    avg_usage = sum(u['memory_mb'] for u in usage_list) / len(usage_list)
                    route_avg_usage[route_name] = avg_usage
            
            top_routes = sorted(route_avg_usage.items(), key=lambda x: x[1], reverse=True)[:10]
            
            return {
                'memory_stats': memory_stats,
                'leak_stats': leak_stats,
                'top_memory_functions': top_functions,
                'top_memory_routes': top_routes,
                'monitoring_info': {
                    'monitoring_active': self.monitoring_active,
                    'data_points': len(memory_data),
                    'monitoring_duration_hours': len(memory_data) * self.monitoring_interval / 3600,
                    'leak_threshold_mb': self.leak_threshold_mb
                },
                'recent_leaks': leaks[-5:] if leaks else []
            }
            
        except Exception as e:
            logger.error(f"Failed to generate detailed analysis: {e}")
            return {'error': str(e)}
    
    def generate_report(self, format='text') -> str:
        """📋 メモリリーク監視レポート生成"""
        analysis = self.get_detailed_analysis()
        
        if 'error' in analysis:
            return f"Error generating report: {analysis['error']}"
        
        if format == 'json':
            return json.dumps(analysis, indent=2, ensure_ascii=False)
        
        # テキストレポート生成
        report_lines = [
            "🔍 MEMORY LEAK MONITORING REPORT",
            "=" * 50,
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "📊 MEMORY STATISTICS:",
            f"  Current: {analysis['memory_stats']['current_mb']:.1f} MB",
            f"  Average: {analysis['memory_stats']['avg_mb']:.1f} MB",
            f"  Peak: {analysis['memory_stats']['max_mb']:.1f} MB",
            f"  Minimum: {analysis['memory_stats']['min_mb']:.1f} MB",
            f"  Trend: {analysis['memory_stats']['trend']:.3f} MB/period",
            "",
            "🚨 LEAK DETECTION SUMMARY:",
            f"  Total Leaks: {analysis['leak_stats']['total_leaks']}",
            f"  Critical: {analysis['leak_stats']['critical_leaks']}",
            f"  High: {analysis['leak_stats']['high_leaks']}",
            f"  Medium: {analysis['leak_stats']['medium_leaks']}",
            "",
            "🔧 TOP MEMORY-CONSUMING FUNCTIONS:",
        ]
        
        for i, (func_name, avg_mb) in enumerate(analysis['top_memory_functions'], 1):
            report_lines.append(f"  {i}. {func_name}: {avg_mb:.1f} MB")
        
        report_lines.extend([
            "",
            "🛣️ TOP MEMORY-CONSUMING ROUTES:",
        ])
        
        for i, (route_name, avg_mb) in enumerate(analysis['top_memory_routes'], 1):
            report_lines.append(f"  {i}. {route_name}: {avg_mb:.1f} MB")
        
        if analysis['recent_leaks']:
            report_lines.extend([
                "",
                "⚠️ RECENT LEAK DETECTIONS:",
            ])
            for leak in analysis['recent_leaks']:
                report_lines.append(f"  - {leak['timestamp']}: {leak['description']} ({leak['severity']})")
        
        report_lines.extend([
            "",
            f"📈 MONITORING INFO:",
            f"  Status: {'Active' if analysis['monitoring_info']['monitoring_active'] else 'Inactive'}",
            f"  Duration: {analysis['monitoring_info']['monitoring_duration_hours']:.1f} hours",
            f"  Data Points: {analysis['monitoring_info']['data_points']}",
            f"  Leak Threshold: {analysis['monitoring_info']['leak_threshold_mb']} MB",
            "=" * 50
        ])
        
        return "\n".join(report_lines)


def memory_monitoring_decorator(monitor: MemoryLeakMonitor):
    """🔍 メモリ監視デコレータ"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 実行前メモリ
            start_memory = psutil.Process().memory_info().rss / 1024 / 1024
            
            try:
                result = func(*args, **kwargs)
                
                # 実行後メモリ
                end_memory = psutil.Process().memory_info().rss / 1024 / 1024
                memory_delta = end_memory - start_memory
                
                # 関数別メモリ使用量記録
                if monitor:
                    monitor.record_function_memory_usage(func.__name__, memory_delta)
                
                # 大量メモリ使用の警告
                if memory_delta > 10:  # 10MB以上の増加
                    logger.warning(f"High memory usage in {func.__name__}: {memory_delta:.1f} MB")
                
                return result
                
            except Exception as e:
                # エラー時もメモリ使用量を記録
                end_memory = psutil.Process().memory_info().rss / 1024 / 1024
                memory_delta = end_memory - start_memory
                
                if monitor:
                    monitor.record_function_memory_usage(f"{func.__name__}_error", memory_delta)
                
                raise
        
        return wrapper
    return decorator


# グローバルインスタンス
global_memory_monitor = MemoryLeakMonitor()


def init_memory_monitoring(app=None, auto_start=True):
    """🚀 メモリ監視初期化"""
    try:
        if auto_start:
            global_memory_monitor.start_monitoring()
        
        # アラートコールバック設定
        def log_alert(leak_event):
            logger.critical(f"MEMORY LEAK ALERT: {leak_event['description']}")
        
        global_memory_monitor.add_alert_callback(log_alert)
        
        if app:
            # Flask app にメモリ監視API を追加
            register_memory_monitoring_routes(app)
        
        logger.info("Memory leak monitoring initialized successfully")
        return global_memory_monitor
        
    except Exception as e:
        logger.error(f"Failed to initialize memory monitoring: {e}")
        return None


def register_memory_monitoring_routes(app):
    """📡 メモリ監視APIルート登録"""
    
    @app.route('/api/memory/status')
    def memory_status():
        """メモリ状況API"""
        try:
            status = global_memory_monitor.get_memory_status()
            return {'success': True, 'status': status}
        except Exception as e:
            return {'success': False, 'error': str(e)}, 500
    
    @app.route('/api/memory/analysis')
    def memory_analysis():
        """詳細メモリ分析API"""
        try:
            analysis = global_memory_monitor.get_detailed_analysis()
            return {'success': True, 'analysis': analysis}
        except Exception as e:
            return {'success': False, 'error': str(e)}, 500
    
    @app.route('/api/memory/report')
    def memory_report():
        """メモリレポートAPI"""
        try:
            format_type = request.args.get('format', 'text')
            report = global_memory_monitor.generate_report(format_type)
            
            if format_type == 'json':
                return {'success': True, 'report': json.loads(report)}
            else:
                return {'success': True, 'report': report}
        except Exception as e:
            return {'success': False, 'error': str(e)}, 500
    
    @app.route('/api/memory/control', methods=['POST'])
    def memory_control():
        """メモリ監視制御API"""
        try:
            action = request.json.get('action')
            
            if action == 'start':
                global_memory_monitor.start_monitoring()
                return {'success': True, 'message': 'Memory monitoring started'}
            elif action == 'stop':
                global_memory_monitor.stop_monitoring()
                return {'success': True, 'message': 'Memory monitoring stopped'}
            else:
                return {'success': False, 'error': 'Invalid action'}, 400
                
        except Exception as e:
            return {'success': False, 'error': str(e)}, 500


if __name__ == "__main__":
    # テスト実行
    monitor = MemoryLeakMonitor(monitoring_interval=5)  # 5秒間隔でテスト
    monitor.start_monitoring()
    
    print("Memory leak monitoring test started...")
    print("Press Ctrl+C to stop")
    
    try:
        # テスト関数
        @memory_monitoring_decorator(monitor)
        def test_memory_function():
            # 意図的にメモリを使用
            data = [i * "test" for i in range(10000)]
            return len(data)
        
        # テスト実行
        for i in range(10):
            result = test_memory_function()
            print(f"Test {i+1}: {result} items")
            time.sleep(2)
        
        # レポート生成
        print("\n" + monitor.generate_report())
        
    except KeyboardInterrupt:
        print("\nStopping memory monitoring...")
        monitor.stop_monitoring()