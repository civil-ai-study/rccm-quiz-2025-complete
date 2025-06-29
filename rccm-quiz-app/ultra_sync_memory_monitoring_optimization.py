#!/usr/bin/env python3
"""
🔧 ULTRA SYNC: メモリ監視閾値調整システム - 誤検知防止とパフォーマンス向上

🎯 CLAUDE.md準拠・1万人使用ソフト品質基準・ウルトラシンクメモリ最適化

【問題の分析】
❌ 現在のメモリ監視システムの課題:
- 固定閾値による誤検知（500MB一律設定）
- システム環境を考慮しない単純な警告
- パフォーマンス影響を無視したアグレッシブな監視
- フラッシュトラフィック時の不適切なアラート

【ウルトラシンク解決策】
✅ 動的閾値調整によるインテリジェント監視
✅ システムリソース考慮型の適応的アルゴリズム
✅ パフォーマンス影響最小化設計
✅ 企業レベルの監視精度と効率性
"""

import os
import sys
import psutil
import time
import threading
import logging
import json
from datetime import datetime, timezone
from typing import Dict, List, Tuple, Any, Optional
from collections import deque
import statistics
from dataclasses import dataclass
from contextlib import contextmanager
import gc
import tracemalloc

# ロガー設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MemoryMetrics:
    """メモリ使用量メトリクス"""
    timestamp: float
    rss_mb: float
    vms_mb: float
    percent: float
    available_mb: float
    system_total_mb: float
    
class SystemResourceAnalyzer:
    """システムリソース分析器"""
    
    def __init__(self):
        self.cpu_count = psutil.cpu_count()
        self.memory_total = psutil.virtual_memory().total / (1024 * 1024)  # MB
        self.process = psutil.Process()
        
    def get_system_profile(self) -> Dict[str, Any]:
        """システムプロファイル取得"""
        try:
            cpu_info = {
                'physical_cores': psutil.cpu_count(logical=False),
                'logical_cores': psutil.cpu_count(logical=True),
                'cpu_freq': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None,
                'cpu_usage_percent': psutil.cpu_percent(interval=1)
            }
            
            memory_info = psutil.virtual_memory()._asdict()
            memory_info['total_mb'] = memory_info['total'] / (1024 * 1024)
            memory_info['available_mb'] = memory_info['available'] / (1024 * 1024)
            
            disk_info = psutil.disk_usage('/')._asdict()
            disk_info['total_gb'] = disk_info['total'] / (1024 * 1024 * 1024)
            disk_info['free_gb'] = disk_info['free'] / (1024 * 1024 * 1024)
            
            return {
                'cpu': cpu_info,
                'memory': memory_info,
                'disk': disk_info,
                'platform': {
                    'system': os.name,
                    'architecture': os.uname() if hasattr(os, 'uname') else None
                }
            }
        except Exception as e:
            logger.warning(f"システムプロファイル取得エラー: {e}")
            return {}

class UltraSyncMemoryMonitoringOptimizer:
    """
    🔧 Ultra Sync メモリ監視最適化システム
    
    動的閾値調整により誤検知を防止し、パフォーマンスを向上させる
    インテリジェントなメモリ監視システム
    """
    
    def __init__(self, config: Optional[Dict] = None):
        # 🔥 ULTRA SYNC: 基本設定
        self.config = self._init_config(config)
        
        # 📊 システム分析器
        self.system_analyzer = SystemResourceAnalyzer()
        self.system_profile = self.system_analyzer.get_system_profile()
        
        # 📈 メトリクス履歴（スレッドセーフ）
        self._metrics_lock = threading.RLock()
        self.metrics_history = deque(maxlen=self.config['history_window_size'])
        self.baseline_metrics = None
        
        # 🎯 動的閾値
        self.dynamic_thresholds = {
            'memory_usage_mb': self._calculate_initial_memory_threshold(),
            'memory_percent': self._calculate_initial_percent_threshold(),
            'growth_rate_mb_per_sec': self._calculate_initial_growth_threshold()
        }
        
        # ⚡ パフォーマンス最適化
        self.monitoring_enabled = True
        self.last_optimization = time.time()
        self.optimization_stats = {
            'false_positives_prevented': 0,
            'performance_improvements': 0,
            'threshold_adjustments': 0,
            'total_optimizations': 0
        }
        
        # 🔍 高度な分析
        self.memory_patterns = {
            'baseline_established': False,
            'peak_usage_times': [],
            'growth_patterns': [],
            'stability_periods': []
        }
        
        # 📝 診断ログ
        self.diagnostic_log = []
        
        logger.info(f"🔧 Ultra Sync Memory Monitoring Optimizer 初期化完了")
        logger.info(f"🖥️  システム: CPU={self.system_analyzer.cpu_count}コア, メモリ={self.system_analyzer.memory_total:.1f}MB")
        logger.info(f"🎯 初期閾値: メモリ={self.dynamic_thresholds['memory_usage_mb']:.1f}MB")
    
    def _init_config(self, config: Optional[Dict] = None) -> Dict[str, Any]:
        """設定初期化"""
        default_config = {
            # 基本監視設定
            'monitoring_interval': 30,  # 30秒間隔
            'history_window_size': 100,  # 100サンプル保持
            'baseline_samples': 20,  # ベースライン確立用サンプル数
            
            # 閾値調整設定
            'adaptive_threshold': True,
            'threshold_adjustment_factor': 0.1,  # 10%ずつ調整
            'min_threshold_mb': 100,  # 最小閾値100MB
            'max_threshold_mb': 2000,  # 最大閾値2GB
            
            # パフォーマンス設定
            'optimization_interval': 300,  # 5分ごとに最適化
            'false_positive_tolerance': 0.05,  # 5%の誤検知率許容
            'performance_mode': 'balanced',  # 'aggressive', 'balanced', 'conservative'
            
            # アラート設定
            'enable_smart_alerts': True,
            'alert_cooldown': 60,  # 1分間のクールダウン
            'suppress_transient_spikes': True,
            
            # 環境適応設定
            'auto_detect_environment': True,
            'production_mode': False,
            'concurrent_users_estimate': 100
        }
        
        if config:
            default_config.update(config)
        
        # 環境変数による設定上書き
        for key, value in default_config.items():
            env_key = f"MEMORY_MONITOR_{key.upper()}"
            if env_key in os.environ:
                if isinstance(value, bool):
                    default_config[key] = os.environ[env_key].lower() == 'true'
                elif isinstance(value, int):
                    default_config[key] = int(os.environ[env_key])
                elif isinstance(value, float):
                    default_config[key] = float(os.environ[env_key])
                else:
                    default_config[key] = os.environ[env_key]
        
        return default_config
    
    def _calculate_initial_memory_threshold(self) -> float:
        """初期メモリ閾値計算"""
        total_memory_mb = self.system_analyzer.memory_total
        
        # システムメモリ量に基づく動的計算
        if total_memory_mb >= 8192:  # 8GB以上
            base_threshold = total_memory_mb * 0.15  # 15%
        elif total_memory_mb >= 4096:  # 4GB以上
            base_threshold = total_memory_mb * 0.20  # 20%
        elif total_memory_mb >= 2048:  # 2GB以上
            base_threshold = total_memory_mb * 0.25  # 25%
        else:  # 2GB未満
            base_threshold = total_memory_mb * 0.30  # 30%
        
        # 同時使用者数による調整
        concurrent_users = self.config['concurrent_users_estimate']
        user_factor = 1 + (concurrent_users / 1000) * 0.1  # 1000ユーザーごとに10%増加
        
        # パフォーマンスモードによる調整
        mode_factors = {
            'aggressive': 0.8,  # 20%削減
            'balanced': 1.0,    # 標準
            'conservative': 1.3  # 30%増加
        }
        mode_factor = mode_factors.get(self.config['performance_mode'], 1.0)
        
        # 最終計算
        calculated_threshold = base_threshold * user_factor * mode_factor
        
        # 最小・最大値制限
        calculated_threshold = max(self.config['min_threshold_mb'], calculated_threshold)
        calculated_threshold = min(self.config['max_threshold_mb'], calculated_threshold)
        
        logger.info(f"🎯 初期メモリ閾値計算: {calculated_threshold:.1f}MB (基準:{base_threshold:.1f}MB × ユーザー倍率:{user_factor:.2f} × モード倍率:{mode_factor:.2f})")
        
        return calculated_threshold
    
    def _calculate_initial_percent_threshold(self) -> float:
        """初期パーセント閾値計算"""
        # システムメモリ使用率ベースの閾値
        performance_mode = self.config['performance_mode']
        
        base_thresholds = {
            'aggressive': 85.0,  # 85%
            'balanced': 75.0,    # 75%
            'conservative': 65.0  # 65%
        }
        
        return base_thresholds.get(performance_mode, 75.0)
    
    def _calculate_initial_growth_threshold(self) -> float:
        """初期成長率閾値計算"""
        # メモリ成長率の閾値（MB/秒）
        total_memory_mb = self.system_analyzer.memory_total
        
        # システムメモリ量に応じた成長率閾値
        if total_memory_mb >= 8192:
            base_growth = 50.0  # 50MB/秒
        elif total_memory_mb >= 4096:
            base_growth = 25.0  # 25MB/秒
        elif total_memory_mb >= 2048:
            base_growth = 10.0  # 10MB/秒
        else:
            base_growth = 5.0   # 5MB/秒
        
        return base_growth
    
    def collect_metrics(self) -> MemoryMetrics:
        """現在のメモリメトリクス収集"""
        try:
            # プロセスメモリ情報
            process_memory = self.system_analyzer.process.memory_info()
            
            # システムメモリ情報
            system_memory = psutil.virtual_memory()
            
            metrics = MemoryMetrics(
                timestamp=time.time(),
                rss_mb=process_memory.rss / (1024 * 1024),
                vms_mb=process_memory.vms / (1024 * 1024),
                percent=system_memory.percent,
                available_mb=system_memory.available / (1024 * 1024),
                system_total_mb=system_memory.total / (1024 * 1024)
            )
            
            # 履歴に追加（スレッドセーフ）
            with self._metrics_lock:
                self.metrics_history.append(metrics)
                
                # ベースライン確立
                if not self.baseline_metrics and len(self.metrics_history) >= self.config['baseline_samples']:
                    self.baseline_metrics = self._calculate_baseline()
                    self.memory_patterns['baseline_established'] = True
                    logger.info(f"📊 ベースライン確立: {self.baseline_metrics['avg_memory_mb']:.1f}MB")
            
            return metrics
            
        except Exception as e:
            logger.error(f"メトリクス収集エラー: {e}")
            # デフォルト値を返す
            return MemoryMetrics(
                timestamp=time.time(),
                rss_mb=0.0,
                vms_mb=0.0,
                percent=0.0,
                available_mb=0.0,
                system_total_mb=self.system_analyzer.memory_total
            )
    
    def _calculate_baseline(self) -> Dict[str, float]:
        """ベースラインメトリクス計算"""
        with self._metrics_lock:
            if len(self.metrics_history) < self.config['baseline_samples']:
                return {}
            
            # 直近のサンプルからベースライン計算
            recent_samples = list(self.metrics_history)[-self.config['baseline_samples']:]
            
            memory_values = [m.rss_mb for m in recent_samples]
            percent_values = [m.percent for m in recent_samples]
            
            baseline = {
                'avg_memory_mb': statistics.mean(memory_values),
                'median_memory_mb': statistics.median(memory_values),
                'stddev_memory_mb': statistics.stdev(memory_values) if len(memory_values) > 1 else 0,
                'avg_percent': statistics.mean(percent_values),
                'max_memory_mb': max(memory_values),
                'min_memory_mb': min(memory_values),
                'calculated_at': time.time()
            }
            
            return baseline
    
    def analyze_memory_patterns(self) -> Dict[str, Any]:
        """メモリパターン分析"""
        with self._metrics_lock:
            if len(self.metrics_history) < 10:
                return {'insufficient_data': True}
            
            recent_metrics = list(self.metrics_history)[-50:]  # 直近50サンプル
            
            # 成長率分析
            growth_rates = []
            for i in range(1, len(recent_metrics)):
                prev_metric = recent_metrics[i-1]
                curr_metric = recent_metrics[i]
                
                time_diff = curr_metric.timestamp - prev_metric.timestamp
                memory_diff = curr_metric.rss_mb - prev_metric.rss_mb
                
                if time_diff > 0:
                    growth_rate = memory_diff / time_diff  # MB/秒
                    growth_rates.append(growth_rate)
            
            # 変動性分析
            memory_values = [m.rss_mb for m in recent_metrics]
            variability = {
                'coefficient_of_variation': statistics.stdev(memory_values) / statistics.mean(memory_values) if statistics.mean(memory_values) > 0 else 0,
                'range_mb': max(memory_values) - min(memory_values),
                'trend': self._calculate_trend(memory_values)
            }
            
            # スパイク検出
            spikes = self._detect_memory_spikes(recent_metrics)
            
            analysis = {
                'sample_count': len(recent_metrics),
                'time_range_minutes': (recent_metrics[-1].timestamp - recent_metrics[0].timestamp) / 60,
                'avg_growth_rate_mb_per_sec': statistics.mean(growth_rates) if growth_rates else 0,
                'max_growth_rate_mb_per_sec': max(growth_rates) if growth_rates else 0,
                'variability': variability,
                'spikes_detected': len(spikes),
                'spike_details': spikes,
                'stability_score': self._calculate_stability_score(memory_values, growth_rates)
            }
            
            return analysis
    
    def _calculate_trend(self, values: List[float]) -> str:
        """トレンド計算"""
        if len(values) < 3:
            return 'insufficient_data'
        
        # 線形回帰によるトレンド計算
        n = len(values)
        x_values = list(range(n))
        
        sum_x = sum(x_values)
        sum_y = sum(values)
        sum_xy = sum(x * y for x, y in zip(x_values, values))
        sum_x2 = sum(x * x for x in x_values)
        
        if n * sum_x2 - sum_x * sum_x == 0:
            return 'no_trend'
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        
        if slope > 0.1:
            return 'increasing'
        elif slope < -0.1:
            return 'decreasing'
        else:
            return 'stable'
    
    def _detect_memory_spikes(self, metrics: List[MemoryMetrics]) -> List[Dict]:
        """メモリスパイク検出"""
        if len(metrics) < 5:
            return []
        
        spikes = []
        memory_values = [m.rss_mb for m in metrics]
        
        # 移動平均と標準偏差によるスパイク検出
        window_size = min(5, len(memory_values) // 2)
        
        for i in range(window_size, len(memory_values) - window_size):
            window_before = memory_values[i-window_size:i]
            window_after = memory_values[i+1:i+window_size+1]
            
            avg_before = statistics.mean(window_before)
            avg_after = statistics.mean(window_after)
            current_value = memory_values[i]
            
            # スパイク判定（前後の平均より大幅に高い）
            threshold_factor = 1.5
            if current_value > avg_before * threshold_factor and current_value > avg_after * threshold_factor:
                spike_info = {
                    'timestamp': metrics[i].timestamp,
                    'memory_mb': current_value,
                    'baseline_mb': (avg_before + avg_after) / 2,
                    'spike_factor': current_value / ((avg_before + avg_after) / 2),
                    'duration_estimated': self._estimate_spike_duration(metrics, i)
                }
                spikes.append(spike_info)
        
        return spikes
    
    def _estimate_spike_duration(self, metrics: List[MemoryMetrics], spike_index: int) -> float:
        """スパイク継続時間推定"""
        spike_value = metrics[spike_index].rss_mb
        baseline_factor = 0.8  # ベースラインの80%まで下がったら終了と判定
        
        # スパイク終了点を検索
        for i in range(spike_index + 1, len(metrics)):
            if metrics[i].rss_mb <= spike_value * baseline_factor:
                return metrics[i].timestamp - metrics[spike_index].timestamp
        
        # 終了点が見つからない場合
        return 0.0
    
    def _calculate_stability_score(self, memory_values: List[float], growth_rates: List[float]) -> float:
        """安定性スコア計算（0-100）"""
        if not memory_values or not growth_rates:
            return 0.0
        
        # 変動係数による安定性（低いほど安定）
        cv = statistics.stdev(memory_values) / statistics.mean(memory_values) if statistics.mean(memory_values) > 0 else 1
        cv_score = max(0, 100 - cv * 100)
        
        # 成長率の安定性
        growth_stability = 100 - (abs(statistics.mean(growth_rates)) * 10)
        growth_stability = max(0, min(100, growth_stability))
        
        # 総合スコア
        stability_score = (cv_score + growth_stability) / 2
        
        return round(stability_score, 2)
    
    def optimize_thresholds(self) -> Dict[str, Any]:
        """動的閾値最適化"""
        if not self.config['adaptive_threshold']:
            return {'optimization_skipped': 'adaptive_threshold_disabled'}
        
        current_time = time.time()
        if current_time - self.last_optimization < self.config['optimization_interval']:
            return {'optimization_skipped': 'too_soon'}
        
        self.last_optimization = current_time
        
        logger.info("🔧 動的閾値最適化開始")
        
        # 現在のパターン分析
        pattern_analysis = self.analyze_memory_patterns()
        
        if pattern_analysis.get('insufficient_data'):
            return {'optimization_skipped': 'insufficient_data'}
        
        # 最適化結果
        optimization_result = {
            'timestamp': current_time,
            'previous_thresholds': self.dynamic_thresholds.copy(),
            'pattern_analysis': pattern_analysis,
            'adjustments_made': []
        }
        
        # メモリ使用量閾値最適化
        memory_adjustment = self._optimize_memory_threshold(pattern_analysis)
        if memory_adjustment['adjusted']:
            optimization_result['adjustments_made'].append(memory_adjustment)
        
        # パーセント閾値最適化
        percent_adjustment = self._optimize_percent_threshold(pattern_analysis)
        if percent_adjustment['adjusted']:
            optimization_result['adjustments_made'].append(percent_adjustment)
        
        # 成長率閾値最適化
        growth_adjustment = self._optimize_growth_threshold(pattern_analysis)
        if growth_adjustment['adjusted']:
            optimization_result['adjustments_made'].append(growth_adjustment)
        
        # 統計更新
        if optimization_result['adjustments_made']:
            self.optimization_stats['threshold_adjustments'] += len(optimization_result['adjustments_made'])
            self.optimization_stats['total_optimizations'] += 1
        
        optimization_result['new_thresholds'] = self.dynamic_thresholds.copy()
        optimization_result['optimization_stats'] = self.optimization_stats.copy()
        
        logger.info(f"🎯 閾値最適化完了: {len(optimization_result['adjustments_made'])}項目調整")
        
        return optimization_result
    
    def _optimize_memory_threshold(self, analysis: Dict) -> Dict[str, Any]:
        """メモリ使用量閾値最適化"""
        current_threshold = self.dynamic_thresholds['memory_usage_mb']
        
        # 安定性に基づく調整
        stability_score = analysis.get('stability_score', 50)
        avg_growth_rate = analysis.get('avg_growth_rate_mb_per_sec', 0)
        
        adjustment_factor = 0
        reason = ""
        
        # 高安定性かつ低成長率 → 閾値を上げる（誤検知防止）
        if stability_score > 80 and abs(avg_growth_rate) < 1.0:
            adjustment_factor = self.config['threshold_adjustment_factor']
            reason = "high_stability_low_growth"
            self.optimization_stats['false_positives_prevented'] += 1
        
        # 低安定性かつ高成長率 → 閾値を下げる（早期警告）
        elif stability_score < 30 and avg_growth_rate > 5.0:
            adjustment_factor = -self.config['threshold_adjustment_factor']
            reason = "low_stability_high_growth"
        
        # スパイクが頻発 → 閾値を調整
        elif analysis.get('spikes_detected', 0) > 3:
            # スパイクが短時間なら誤検知の可能性
            spike_details = analysis.get('spike_details', [])
            avg_spike_duration = statistics.mean([s.get('duration_estimated', 0) for s in spike_details]) if spike_details else 0
            
            if avg_spike_duration < 30:  # 30秒未満の短時間スパイク
                adjustment_factor = self.config['threshold_adjustment_factor'] * 0.5
                reason = "transient_spikes_detected"
                self.optimization_stats['false_positives_prevented'] += 1
        
        # 調整実行
        if adjustment_factor != 0:
            new_threshold = current_threshold * (1 + adjustment_factor)
            
            # 制限値チェック
            new_threshold = max(self.config['min_threshold_mb'], new_threshold)
            new_threshold = min(self.config['max_threshold_mb'], new_threshold)
            
            if new_threshold != current_threshold:
                self.dynamic_thresholds['memory_usage_mb'] = new_threshold
                
                return {
                    'threshold_type': 'memory_usage_mb',
                    'adjusted': True,
                    'previous_value': current_threshold,
                    'new_value': new_threshold,
                    'adjustment_factor': adjustment_factor,
                    'reason': reason
                }
        
        return {
            'threshold_type': 'memory_usage_mb',
            'adjusted': False,
            'reason': 'no_adjustment_needed'
        }
    
    def _optimize_percent_threshold(self, analysis: Dict) -> Dict[str, Any]:
        """パーセント閾値最適化"""
        current_threshold = self.dynamic_thresholds['memory_percent']
        
        # システム全体のメモリ使用状況を考慮
        with self._metrics_lock:
            if self.metrics_history:
                recent_percent_values = [m.percent for m in list(self.metrics_history)[-20:]]
                avg_system_percent = statistics.mean(recent_percent_values)
            else:
                avg_system_percent = 50
        
        adjustment_factor = 0
        reason = ""
        
        # システム全体のメモリ使用率が低い場合、閾値を緩和
        if avg_system_percent < 40:
            adjustment_factor = 0.05  # 5%増加
            reason = "low_system_memory_usage"
        
        # システム全体のメモリ使用率が高い場合、閾値を厳しく
        elif avg_system_percent > 80:
            adjustment_factor = -0.05  # 5%減少
            reason = "high_system_memory_usage"
        
        # 調整実行
        if adjustment_factor != 0:
            new_threshold = current_threshold + (adjustment_factor * 100)
            new_threshold = max(50.0, min(90.0, new_threshold))  # 50-90%の範囲
            
            if abs(new_threshold - current_threshold) > 1.0:  # 1%以上の変更の場合のみ
                self.dynamic_thresholds['memory_percent'] = new_threshold
                
                return {
                    'threshold_type': 'memory_percent',
                    'adjusted': True,
                    'previous_value': current_threshold,
                    'new_value': new_threshold,
                    'adjustment_factor': adjustment_factor,
                    'reason': reason
                }
        
        return {
            'threshold_type': 'memory_percent',
            'adjusted': False,
            'reason': 'no_adjustment_needed'
        }
    
    def _optimize_growth_threshold(self, analysis: Dict) -> Dict[str, Any]:
        """成長率閾値最適化"""
        current_threshold = self.dynamic_thresholds['growth_rate_mb_per_sec']
        
        avg_growth_rate = analysis.get('avg_growth_rate_mb_per_sec', 0)
        max_growth_rate = analysis.get('max_growth_rate_mb_per_sec', 0)
        variability = analysis.get('variability', {})
        trend = variability.get('trend', 'stable')
        
        adjustment_factor = 0
        reason = ""
        
        # 成長率が一貫して低い場合、閾値を下げる（感度向上）
        if abs(avg_growth_rate) < current_threshold * 0.3 and trend == 'stable':
            adjustment_factor = -0.2  # 20%減少
            reason = "consistently_low_growth"
        
        # 成長率が高いが安定している場合、閾値を上げる（誤検知防止）
        elif avg_growth_rate > current_threshold * 0.5 and analysis.get('stability_score', 0) > 70:
            adjustment_factor = 0.3  # 30%増加
            reason = "high_but_stable_growth"
            self.optimization_stats['false_positives_prevented'] += 1
        
        # 調整実行
        if adjustment_factor != 0:
            new_threshold = current_threshold * (1 + adjustment_factor)
            new_threshold = max(1.0, min(100.0, new_threshold))  # 1-100 MB/秒の範囲
            
            if abs(new_threshold - current_threshold) > 0.5:  # 0.5MB/秒以上の変更の場合のみ
                self.dynamic_thresholds['growth_rate_mb_per_sec'] = new_threshold
                
                return {
                    'threshold_type': 'growth_rate_mb_per_sec',
                    'adjusted': True,
                    'previous_value': current_threshold,
                    'new_value': new_threshold,
                    'adjustment_factor': adjustment_factor,
                    'reason': reason
                }
        
        return {
            'threshold_type': 'growth_rate_mb_per_sec',
            'adjusted': False,
            'reason': 'no_adjustment_needed'
        }
    
    def check_memory_status(self) -> Dict[str, Any]:
        """インテリジェントメモリ状態チェック"""
        current_metrics = self.collect_metrics()
        
        # 基本ステータス
        status = {
            'timestamp': current_metrics.timestamp,
            'current_memory_mb': current_metrics.rss_mb,
            'current_percent': current_metrics.percent,
            'thresholds': self.dynamic_thresholds.copy(),
            'alerts': [],
            'recommendations': []
        }
        
        # メモリ使用量チェック
        memory_status = self._check_memory_threshold(current_metrics)
        if memory_status['alert_level'] != 'normal':
            status['alerts'].append(memory_status)
        
        # システムメモリパーセントチェック
        percent_status = self._check_percent_threshold(current_metrics)
        if percent_status['alert_level'] != 'normal':
            status['alerts'].append(percent_status)
        
        # 成長率チェック
        growth_status = self._check_growth_rate()
        if growth_status['alert_level'] != 'normal':
            status['alerts'].append(growth_status)
        
        # パターン分析ベースの推奨事項
        if len(self.metrics_history) >= 10:
            pattern_analysis = self.analyze_memory_patterns()
            recommendations = self._generate_recommendations(current_metrics, pattern_analysis)
            status['recommendations'] = recommendations
        
        # 全体的なステータス判定
        if not status['alerts']:
            status['overall_status'] = 'healthy'
        elif any(alert['alert_level'] == 'critical' for alert in status['alerts']):
            status['overall_status'] = 'critical'
        elif any(alert['alert_level'] == 'warning' for alert in status['alerts']):
            status['overall_status'] = 'warning'
        else:
            status['overall_status'] = 'attention'
        
        return status
    
    def _check_memory_threshold(self, metrics: MemoryMetrics) -> Dict[str, Any]:
        """メモリ閾値チェック"""
        threshold = self.dynamic_thresholds['memory_usage_mb']
        usage_ratio = metrics.rss_mb / threshold
        
        if usage_ratio >= 1.0:
            alert_level = 'critical'
            message = f"メモリ使用量が閾値を超過: {metrics.rss_mb:.1f}MB >= {threshold:.1f}MB"
        elif usage_ratio >= 0.9:
            alert_level = 'warning'
            message = f"メモリ使用量が閾値の90%に接近: {metrics.rss_mb:.1f}MB (閾値: {threshold:.1f}MB)"
        elif usage_ratio >= 0.8:
            alert_level = 'attention'
            message = f"メモリ使用量が閾値の80%に接近: {metrics.rss_mb:.1f}MB (閾値: {threshold:.1f}MB)"
        else:
            alert_level = 'normal'
            message = f"メモリ使用量は正常範囲: {metrics.rss_mb:.1f}MB (閾値: {threshold:.1f}MB)"
        
        return {
            'check_type': 'memory_threshold',
            'alert_level': alert_level,
            'message': message,
            'current_value': metrics.rss_mb,
            'threshold_value': threshold,
            'usage_ratio': usage_ratio
        }
    
    def _check_percent_threshold(self, metrics: MemoryMetrics) -> Dict[str, Any]:
        """システムメモリパーセント閾値チェック"""
        threshold = self.dynamic_thresholds['memory_percent']
        
        if metrics.percent >= threshold:
            alert_level = 'critical'
            message = f"システムメモリ使用率が閾値を超過: {metrics.percent:.1f}% >= {threshold:.1f}%"
        elif metrics.percent >= threshold * 0.9:
            alert_level = 'warning'
            message = f"システムメモリ使用率が閾値の90%に接近: {metrics.percent:.1f}% (閾値: {threshold:.1f}%)"
        elif metrics.percent >= threshold * 0.8:
            alert_level = 'attention'
            message = f"システムメモリ使用率が閾値の80%に接近: {metrics.percent:.1f}% (閾値: {threshold:.1f}%)"
        else:
            alert_level = 'normal'
            message = f"システムメモリ使用率は正常範囲: {metrics.percent:.1f}% (閾値: {threshold:.1f}%)"
        
        return {
            'check_type': 'memory_percent',
            'alert_level': alert_level,
            'message': message,
            'current_value': metrics.percent,
            'threshold_value': threshold,
            'available_mb': metrics.available_mb
        }
    
    def _check_growth_rate(self) -> Dict[str, Any]:
        """メモリ成長率チェック"""
        with self._metrics_lock:
            if len(self.metrics_history) < 3:
                return {
                    'check_type': 'growth_rate',
                    'alert_level': 'normal',
                    'message': 'データ不足のため成長率チェックをスキップ'
                }
            
            # 直近3サンプルの成長率計算
            recent_metrics = list(self.metrics_history)[-3:]
            growth_rates = []
            
            for i in range(1, len(recent_metrics)):
                prev_metric = recent_metrics[i-1]
                curr_metric = recent_metrics[i]
                
                time_diff = curr_metric.timestamp - prev_metric.timestamp
                memory_diff = curr_metric.rss_mb - prev_metric.rss_mb
                
                if time_diff > 0:
                    growth_rate = memory_diff / time_diff  # MB/秒
                    growth_rates.append(growth_rate)
            
            if not growth_rates:
                return {
                    'check_type': 'growth_rate',
                    'alert_level': 'normal',
                    'message': '成長率データが利用できません'
                }
            
            avg_growth_rate = statistics.mean(growth_rates)
            threshold = self.dynamic_thresholds['growth_rate_mb_per_sec']
            
            if avg_growth_rate >= threshold:
                alert_level = 'critical'
                message = f"メモリ成長率が閾値を超過: {avg_growth_rate:.2f}MB/秒 >= {threshold:.2f}MB/秒"
            elif avg_growth_rate >= threshold * 0.8:
                alert_level = 'warning'
                message = f"メモリ成長率が閾値の80%に接近: {avg_growth_rate:.2f}MB/秒 (閾値: {threshold:.2f}MB/秒)"
            elif avg_growth_rate >= threshold * 0.6:
                alert_level = 'attention'
                message = f"メモリ成長率が閾値の60%に接近: {avg_growth_rate:.2f}MB/秒 (閾値: {threshold:.2f}MB/秒)"
            else:
                alert_level = 'normal'
                message = f"メモリ成長率は正常範囲: {avg_growth_rate:.2f}MB/秒 (閾値: {threshold:.2f}MB/秒)"
            
            return {
                'check_type': 'growth_rate',
                'alert_level': alert_level,
                'message': message,
                'current_value': avg_growth_rate,
                'threshold_value': threshold,
                'sample_count': len(growth_rates)
            }
    
    def _generate_recommendations(self, current_metrics: MemoryMetrics, pattern_analysis: Dict) -> List[str]:
        """推奨事項生成"""
        recommendations = []
        
        # 安定性ベースの推奨事項
        stability_score = pattern_analysis.get('stability_score', 50)
        if stability_score < 30:
            recommendations.append("メモリ使用パターンが不安定です。アプリケーションのメモリリークを確認してください。")
        
        # 成長率ベースの推奨事項
        avg_growth_rate = pattern_analysis.get('avg_growth_rate_mb_per_sec', 0)
        if avg_growth_rate > 10:
            recommendations.append(f"高いメモリ成長率({avg_growth_rate:.2f}MB/秒)が検出されました。ガベージコレクションの頻度を見直してください。")
        
        # スパイクベースの推奨事項
        spikes_detected = pattern_analysis.get('spikes_detected', 0)
        if spikes_detected > 2:
            recommendations.append(f"{spikes_detected}個のメモリスパイクが検出されました。処理負荷の平準化を検討してください。")
        
        # システムリソースベースの推奨事項
        if current_metrics.available_mb < 500:
            recommendations.append("システムの利用可能メモリが少なくなっています。他のプロセスのメモリ使用量を確認してください。")
        
        # トレンドベースの推奨事項
        variability = pattern_analysis.get('variability', {})
        trend = variability.get('trend', 'stable')
        if trend == 'increasing':
            recommendations.append("メモリ使用量が継続的に増加しています。メモリリークの可能性があります。")
        
        # パフォーマンス改善推奨事項
        if pattern_analysis.get('coefficient_of_variation', 0) > 0.3:
            recommendations.append("メモリ使用量の変動が大きいです。キャッシュサイズやバッファサイズの最適化を検討してください。")
        
        return recommendations
    
    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """包括的レポート生成"""
        current_time = time.time()
        current_metrics = self.collect_metrics()
        memory_status = self.check_memory_status()
        pattern_analysis = self.analyze_memory_patterns()
        
        report = {
            'report_metadata': {
                'generated_at': datetime.fromtimestamp(current_time, timezone.utc).isoformat(),
                'system_profile': self.system_profile,
                'configuration': self.config,
                'monitoring_duration_minutes': (current_time - (self.metrics_history[0].timestamp if self.metrics_history else current_time)) / 60
            },
            'current_status': memory_status,
            'pattern_analysis': pattern_analysis,
            'threshold_optimization': {
                'current_thresholds': self.dynamic_thresholds,
                'baseline_metrics': self.baseline_metrics,
                'optimization_stats': self.optimization_stats
            },
            'system_information': {
                'total_memory_mb': self.system_analyzer.memory_total,
                'cpu_cores': self.system_analyzer.cpu_count,
                'current_metrics': {
                    'rss_mb': current_metrics.rss_mb,
                    'vms_mb': current_metrics.vms_mb,
                    'system_percent': current_metrics.percent,
                    'available_mb': current_metrics.available_mb
                }
            },
            'recommendations': {
                'immediate_actions': [],
                'optimization_suggestions': [],
                'monitoring_improvements': []
            }
        }
        
        # 推奨事項の分類
        all_recommendations = memory_status.get('recommendations', [])
        for rec in all_recommendations:
            if 'critical' in rec.lower() or 'urgent' in rec.lower():
                report['recommendations']['immediate_actions'].append(rec)
            elif 'optimize' in rec.lower() or 'improve' in rec.lower():
                report['recommendations']['optimization_suggestions'].append(rec)
            else:
                report['recommendations']['monitoring_improvements'].append(rec)
        
        # 追加的な分析情報
        if pattern_analysis.get('stability_score'):
            stability_score = pattern_analysis['stability_score']
            if stability_score < 50:
                report['recommendations']['immediate_actions'].append(
                    f"メモリ使用パターンの安定性が低い(スコア: {stability_score})ため、アプリケーション動作の見直しが必要です。"
                )
            elif stability_score > 80:
                report['recommendations']['optimization_suggestions'].append(
                    f"メモリ使用パターンが安定(スコア: {stability_score})しているため、閾値を緩和して誤検知を減らすことができます。"
                )
        
        return report
    
    def save_report(self, report: Dict[str, Any], filename: str = None) -> str:
        """レポート保存"""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"ultra_sync_memory_optimization_report_{timestamp}.json"
        
        try:
            report_path = os.path.join(os.path.dirname(__file__), filename)
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            logger.info(f"📊 メモリ最適化レポート保存: {report_path}")
            return report_path
            
        except Exception as e:
            logger.error(f"レポート保存エラー: {e}")
            return None
    
    def run_optimization_cycle(self) -> Dict[str, Any]:
        """最適化サイクル実行"""
        logger.info("🚀 メモリ監視最適化サイクル開始")
        
        cycle_start = time.time()
        results = {
            'cycle_start': cycle_start,
            'steps_completed': [],
            'errors': []
        }
        
        try:
            # ステップ1: メトリクス収集
            logger.info("📊 ステップ1: メトリクス収集")
            current_metrics = self.collect_metrics()
            results['steps_completed'].append('metrics_collection')
            results['current_metrics'] = {
                'rss_mb': current_metrics.rss_mb,
                'percent': current_metrics.percent,
                'timestamp': current_metrics.timestamp
            }
            
            # ステップ2: パターン分析
            logger.info("🔍 ステップ2: パターン分析")
            pattern_analysis = self.analyze_memory_patterns()
            results['steps_completed'].append('pattern_analysis')
            results['pattern_analysis_summary'] = {
                'stability_score': pattern_analysis.get('stability_score', 0),
                'spikes_detected': pattern_analysis.get('spikes_detected', 0),
                'trend': pattern_analysis.get('variability', {}).get('trend', 'unknown')
            }
            
            # ステップ3: 閾値最適化
            logger.info("🎯 ステップ3: 閾値最適化")
            optimization_result = self.optimize_thresholds()
            results['steps_completed'].append('threshold_optimization')
            results['optimization_result'] = optimization_result
            
            # ステップ4: ステータスチェック
            logger.info("✅ ステップ4: ステータスチェック")
            memory_status = self.check_memory_status()
            results['steps_completed'].append('status_check')
            results['memory_status'] = memory_status
            
            # ステップ5: レポート生成
            logger.info("📄 ステップ5: レポート生成")
            comprehensive_report = self.generate_comprehensive_report()
            results['steps_completed'].append('report_generation')
            
            # レポート保存
            report_path = self.save_report(comprehensive_report)
            if report_path:
                results['report_path'] = report_path
            
            cycle_end = time.time()
            results['cycle_duration'] = cycle_end - cycle_start
            results['success'] = True
            
            logger.info(f"✅ 最適化サイクル完了: {results['cycle_duration']:.2f}秒")
            
        except Exception as e:
            error_msg = f"最適化サイクルエラー: {e}"
            logger.error(error_msg)
            results['errors'].append(error_msg)
            results['success'] = False
        
        return results

def main():
    """メイン実行関数"""
    print("🔧 Ultra Sync Memory Monitoring Optimizer 開始")
    print("=" * 60)
    
    # 設定例（本番環境では環境変数や設定ファイルから読み込み）
    config = {
        'monitoring_interval': 30,
        'adaptive_threshold': True,
        'performance_mode': 'balanced',
        'concurrent_users_estimate': 1000,
        'enable_smart_alerts': True
    }
    
    # オプティマイザー初期化
    optimizer = UltraSyncMemoryMonitoringOptimizer(config)
    
    # 初期状態表示
    print(f"🖥️  システム情報:")
    print(f"   - CPU: {optimizer.system_analyzer.cpu_count}コア")
    print(f"   - メモリ: {optimizer.system_analyzer.memory_total:.1f}MB")
    print(f"   - 初期閾値: {optimizer.dynamic_thresholds['memory_usage_mb']:.1f}MB")
    
    # 最適化サイクル実行
    print("\n🚀 最適化サイクル実行中...")
    cycle_result = optimizer.run_optimization_cycle()
    
    # 結果表示
    print("\n📊 実行結果:")
    print(f"   - 成功: {'✅ YES' if cycle_result['success'] else '❌ NO'}")
    print(f"   - 実行時間: {cycle_result.get('cycle_duration', 0):.2f}秒")
    print(f"   - 完了ステップ: {len(cycle_result['steps_completed'])}")
    
    if cycle_result.get('current_metrics'):
        metrics = cycle_result['current_metrics']
        print(f"   - 現在のメモリ使用量: {metrics['rss_mb']:.1f}MB")
        print(f"   - システム使用率: {metrics['percent']:.1f}%")
    
    if cycle_result.get('optimization_result'):
        opt_result = cycle_result['optimization_result']
        adjustments = opt_result.get('adjustments_made', [])
        print(f"   - 閾値調整: {len(adjustments)}項目")
        
        for adj in adjustments:
            print(f"     - {adj['threshold_type']}: {adj['previous_value']:.1f} → {adj['new_value']:.1f}")
    
    if cycle_result.get('memory_status'):
        status = cycle_result['memory_status']
        print(f"   - 全体ステータス: {status['overall_status']}")
        print(f"   - アラート数: {len(status['alerts'])}")
        print(f"   - 推奨事項数: {len(status['recommendations'])}")
    
    if cycle_result.get('errors'):
        print("\n❌ エラー:")
        for error in cycle_result['errors']:
            print(f"   - {error}")
    
    if cycle_result.get('report_path'):
        print(f"\n📄 詳細レポート: {cycle_result['report_path']}")
    
    print("\n🎉 Ultra Sync Memory Monitoring Optimizer 完了")

if __name__ == "__main__":
    main()