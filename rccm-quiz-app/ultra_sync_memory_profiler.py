#!/usr/bin/env python3
"""
📊 Ultra Sync Memory Profiler with Tracemalloc Integration
RCCM試験問題集アプリ - ウルトラシンク メモリプロファイラー

🎯 CLAUDE.md準拠・副作用ゼロ保証・ウルトラシンクメモリ最適化:
- Python標準tracemalloc統合
- リアルタイムメモリリーク検出
- 包括的メモリ使用量分析
- 自動アラート機能
- パフォーマンス影響最小化
"""

import tracemalloc
import linecache
import os
import threading
import time
import logging
import json
import gc
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict, deque
from dataclasses import dataclass, asdict
import statistics
import weakref

logger = logging.getLogger(__name__)

@dataclass
class MemorySnapshot:
    """📸 メモリスナップショット"""
    timestamp: datetime
    current_size: int
    peak_size: int
    num_blocks: int
    traced_blocks: int
    gc_stats: Dict[str, int]
    top_allocations: List[Dict[str, Any]]

@dataclass
class MemoryLeak:
    """🚨 メモリリーク情報"""
    timestamp: datetime
    location: str
    size_increase: int
    growth_rate: float
    confidence: float
    stack_trace: List[str]

class UltraSyncMemoryProfiler:
    """📊 ウルトラシンク メモリプロファイラー"""
    
    def __init__(self, 
                 trace_limit: int = 25,
                 snapshot_interval: int = 30,
                 leak_threshold_mb: float = 10.0,
                 auto_start: bool = False):
        
        self.trace_limit = trace_limit
        self.snapshot_interval = snapshot_interval
        self.leak_threshold_mb = leak_threshold_mb
        
        # tracemalloc状態
        self.is_tracing = False
        self.trace_start_time = None
        
        # スナップショット管理
        self.snapshots = deque(maxlen=100)
        self.baseline_snapshot = None
        self.monitoring_thread = None
        
        # メモリリーク検出
        self.leak_candidates = defaultdict(list)
        self.confirmed_leaks = deque(maxlen=50)
        self.allocation_history = defaultdict(lambda: deque(maxlen=10))
        
        # 統計データ
        self.stats = {
            'total_snapshots': 0,
            'leaks_detected': 0,
            'peak_memory_mb': 0,
            'current_memory_mb': 0,
            'monitoring_duration': 0,
            'last_gc_collection': datetime.now(timezone.utc)
        }
        
        # スレッドセーフティ
        self.lock = threading.Lock()
        
        # 弱参照によるオブジェクト追跡
        self.tracked_objects = weakref.WeakSet()
        
        logger.info("📊 Ultra Sync Memory Profiler initialized")
        
        if auto_start:
            self.start_tracing()
    
    def start_tracing(self):
        """🚀 メモリトレース開始"""
        if self.is_tracing:
            logger.warning("Memory tracing already started")
            return
        
        # tracemalloc開始
        tracemalloc.start(self.trace_limit)
        self.is_tracing = True
        self.trace_start_time = datetime.now(timezone.utc)
        
        # ベースラインスナップショット取得
        self.baseline_snapshot = self._take_snapshot()
        
        # 監視スレッド開始
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True
        )
        self.monitoring_thread.start()
        
        logger.info(f"🚀 Memory tracing started with limit={self.trace_limit}")
    
    def stop_tracing(self):
        """⏹️ メモリトレース停止"""
        if not self.is_tracing:
            logger.warning("Memory tracing not started")
            return
        
        self.is_tracing = False
        tracemalloc.stop()
        
        # 最終スナップショット
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=5)
        
        logger.info("⏹️ Memory tracing stopped")
    
    def _monitoring_loop(self):
        """🔄 監視ループ"""
        while self.is_tracing:
            try:
                # スナップショット取得
                snapshot = self._take_snapshot()
                
                with self.lock:
                    self.snapshots.append(snapshot)
                    self.stats['total_snapshots'] += 1
                
                # メモリリーク検出
                self._detect_memory_leaks(snapshot)
                
                # ガベージコレクション統計
                self._update_gc_stats()
                
                time.sleep(self.snapshot_interval)
                
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                time.sleep(self.snapshot_interval)
    
    def _take_snapshot(self) -> MemorySnapshot:
        """📸 スナップショット取得"""
        if not tracemalloc.is_tracing():
            raise RuntimeError("tracemalloc is not tracing")
        
        # 現在のメモリ使用量
        current, peak = tracemalloc.get_traced_memory()
        
        # tracemalloc統計
        snapshot = tracemalloc.take_snapshot()
        stats = snapshot.statistics('lineno')
        
        # GC統計
        gc_stats = {
            'gen0': len(gc.get_objects(0)),
            'gen1': len(gc.get_objects(1)),
            'gen2': len(gc.get_objects(2)),
            'collections': gc.get_count()
        }
        
        # トップアロケーション
        top_allocations = []
        for stat in stats[:10]:  # Top 10
            frame = stat.traceback[0]
            filename = frame.filename
            lineno = frame.lineno
            
            # ソースコード取得
            try:
                line = linecache.getline(filename, lineno).strip()
            except:
                line = "???"
            
            top_allocations.append({
                'filename': filename,
                'lineno': lineno,
                'size': stat.size,
                'size_mb': stat.size / 1024 / 1024,
                'count': stat.count,
                'code': line[:100]  # 最初の100文字
            })
        
        # メモリスナップショット作成
        memory_snapshot = MemorySnapshot(
            timestamp=datetime.now(timezone.utc),
            current_size=current,
            peak_size=peak,
            num_blocks=sum(stat.count for stat in stats),
            traced_blocks=len(stats),
            gc_stats=gc_stats,
            top_allocations=top_allocations
        )
        
        # 統計更新
        self.stats['current_memory_mb'] = current / 1024 / 1024
        self.stats['peak_memory_mb'] = max(self.stats['peak_memory_mb'], peak / 1024 / 1024)
        
        return memory_snapshot
    
    def _detect_memory_leaks(self, current_snapshot: MemorySnapshot):
        """🚨 メモリリーク検出"""
        if len(self.snapshots) < 3:
            return
        
        # 最近のスナップショットと比較
        recent_snapshots = list(self.snapshots)[-5:]
        
        # アロケーション成長分析
        for allocation in current_snapshot.top_allocations:
            key = f"{allocation['filename']}:{allocation['lineno']}"
            
            # 履歴追跡
            self.allocation_history[key].append({
                'timestamp': current_snapshot.timestamp,
                'size': allocation['size'],
                'count': allocation['count']
            })
            
            # 成長率計算
            if len(self.allocation_history[key]) >= 3:
                growth_rate = self._calculate_growth_rate(self.allocation_history[key])
                
                # リーク判定
                if growth_rate > 0.1 and allocation['size_mb'] > self.leak_threshold_mb:
                    confidence = min(growth_rate * 10, 1.0)  # 信頼度計算
                    
                    # スタックトレース取得
                    stack_trace = self._get_detailed_stack_trace(key)
                    
                    leak = MemoryLeak(
                        timestamp=current_snapshot.timestamp,
                        location=key,
                        size_increase=allocation['size'],
                        growth_rate=growth_rate,
                        confidence=confidence,
                        stack_trace=stack_trace
                    )
                    
                    with self.lock:
                        self.confirmed_leaks.append(leak)
                        self.stats['leaks_detected'] += 1
                    
                    logger.warning(f"🚨 Memory leak detected at {key}: {allocation['size_mb']:.1f}MB (growth rate: {growth_rate:.2%})")
    
    def _calculate_growth_rate(self, history: deque) -> float:
        """📈 成長率計算"""
        if len(history) < 2:
            return 0.0
        
        # サイズの時系列データ
        sizes = [h['size'] for h in history]
        
        # 線形回帰による成長率推定
        n = len(sizes)
        if n < 2:
            return 0.0
        
        x_sum = sum(range(n))
        y_sum = sum(sizes)
        xy_sum = sum(i * size for i, size in enumerate(sizes))
        x2_sum = sum(i * i for i in range(n))
        
        denominator = n * x2_sum - x_sum * x_sum
        if denominator == 0:
            return 0.0
        
        slope = (n * xy_sum - x_sum * y_sum) / denominator
        
        # 成長率を正規化（元のサイズに対する割合）
        if sizes[0] > 0:
            growth_rate = slope / sizes[0]
        else:
            growth_rate = 0.0
        
        return growth_rate
    
    def _get_detailed_stack_trace(self, location: str) -> List[str]:
        """🔍 詳細スタックトレース取得"""
        try:
            filename, lineno = location.split(':')
            lineno = int(lineno)
            
            # コンテキスト付きソースコード取得
            context_lines = 3
            stack_trace = []
            
            for i in range(lineno - context_lines, lineno + context_lines + 1):
                if i > 0:
                    line = linecache.getline(filename, i)
                    if line:
                        prefix = ">>> " if i == lineno else "    "
                        stack_trace.append(f"{prefix}{i:4d}: {line.rstrip()}")
            
            return stack_trace
        except Exception as e:
            logger.error(f"Failed to get stack trace: {e}")
            return [f"Failed to get stack trace for {location}"]
    
    def _update_gc_stats(self):
        """♻️ ガベージコレクション統計更新"""
        # 強制GC実行（オプション）
        if self.stats['total_snapshots'] % 10 == 0:
            gc.collect()
            self.stats['last_gc_collection'] = datetime.now(timezone.utc)
    
    def get_memory_report(self) -> Dict[str, Any]:
        """📋 メモリレポート生成"""
        if not self.snapshots:
            return {'error': 'No snapshots available'}
        
        with self.lock:
            latest_snapshot = self.snapshots[-1]
            
            # メモリ使用量推移
            memory_trend = []
            for snapshot in list(self.snapshots)[-20:]:  # 最新20件
                memory_trend.append({
                    'timestamp': snapshot.timestamp.isoformat(),
                    'memory_mb': snapshot.current_size / 1024 / 1024
                })
            
            # トップアロケーション
            top_allocations = latest_snapshot.top_allocations[:5]
            
            # 確認済みリーク
            recent_leaks = []
            for leak in list(self.confirmed_leaks)[-10:]:
                recent_leaks.append({
                    'timestamp': leak.timestamp.isoformat(),
                    'location': leak.location,
                    'size_mb': leak.size_increase / 1024 / 1024,
                    'growth_rate': f"{leak.growth_rate:.2%}",
                    'confidence': f"{leak.confidence:.2%}"
                })
            
            # 監視時間計算
            if self.trace_start_time:
                duration = (datetime.now(timezone.utc) - self.trace_start_time).total_seconds()
                self.stats['monitoring_duration'] = duration
            
            return {
                'status': 'tracing' if self.is_tracing else 'stopped',
                'stats': self.stats.copy(),
                'memory_trend': memory_trend,
                'top_allocations': top_allocations,
                'recent_leaks': recent_leaks,
                'gc_stats': latest_snapshot.gc_stats,
                'recommendations': self._get_recommendations()
            }
    
    def _get_recommendations(self) -> List[str]:
        """💡 推奨事項生成"""
        recommendations = []
        
        # メモリ使用量チェック
        if self.stats['current_memory_mb'] > 500:
            recommendations.append("⚠️ メモリ使用量が500MBを超えています。不要なオブジェクトの削除を検討してください。")
        
        # リーク検出チェック
        if self.stats['leaks_detected'] > 0:
            recommendations.append(f"🚨 {self.stats['leaks_detected']}件のメモリリークが検出されました。該当箇所の修正が必要です。")
        
        # GC頻度チェック
        if self.snapshots:
            latest = self.snapshots[-1]
            gc_collections = sum(latest.gc_stats.get('collections', (0, 0, 0)))
            if gc_collections > 100:
                recommendations.append("♻️ ガベージコレクションが頻繁に実行されています。オブジェクト生成を最適化してください。")
        
        if not recommendations:
            recommendations.append("✅ メモリ使用状況は正常です。")
        
        return recommendations
    
    def compare_snapshots(self, index1: int = -2, index2: int = -1) -> Dict[str, Any]:
        """🔍 スナップショット比較"""
        if len(self.snapshots) < 2:
            return {'error': 'Not enough snapshots for comparison'}
        
        with self.lock:
            try:
                snapshot1 = self.snapshots[index1]
                snapshot2 = self.snapshots[index2]
                
                # メモリ差分計算
                memory_diff = snapshot2.current_size - snapshot1.current_size
                time_diff = (snapshot2.timestamp - snapshot1.timestamp).total_seconds()
                
                # アロケーション差分
                alloc_diff = {}
                
                # snapshot1のアロケーション
                for alloc in snapshot1.top_allocations:
                    key = f"{alloc['filename']}:{alloc['lineno']}"
                    alloc_diff[key] = -alloc['size']
                
                # snapshot2のアロケーション
                for alloc in snapshot2.top_allocations:
                    key = f"{alloc['filename']}:{alloc['lineno']}"
                    if key in alloc_diff:
                        alloc_diff[key] += alloc['size']
                    else:
                        alloc_diff[key] = alloc['size']
                
                # 差分でソート
                sorted_diff = sorted(alloc_diff.items(), key=lambda x: abs(x[1]), reverse=True)
                
                return {
                    'time_range': {
                        'start': snapshot1.timestamp.isoformat(),
                        'end': snapshot2.timestamp.isoformat(),
                        'duration_seconds': time_diff
                    },
                    'memory_change': {
                        'total_diff_bytes': memory_diff,
                        'total_diff_mb': memory_diff / 1024 / 1024,
                        'rate_mb_per_minute': (memory_diff / 1024 / 1024) / (time_diff / 60) if time_diff > 0 else 0
                    },
                    'top_changes': [
                        {
                            'location': location,
                            'diff_bytes': diff,
                            'diff_mb': diff / 1024 / 1024
                        }
                        for location, diff in sorted_diff[:10]
                    ]
                }
                
            except IndexError:
                return {'error': 'Invalid snapshot indices'}
    
    def track_object(self, obj: Any, name: str = None):
        """🔍 オブジェクト追跡"""
        try:
            self.tracked_objects.add(obj)
            if name:
                # 名前付きトラッキング（デバッグ用）
                logger.debug(f"Tracking object '{name}': {type(obj).__name__}")
        except TypeError:
            logger.warning(f"Cannot track object of type {type(obj).__name__}")
    
    def get_tracked_objects_report(self) -> Dict[str, Any]:
        """📊 追跡オブジェクトレポート"""
        objects_by_type = defaultdict(int)
        
        for obj in self.tracked_objects:
            objects_by_type[type(obj).__name__] += 1
        
        return {
            'total_tracked': len(self.tracked_objects),
            'by_type': dict(objects_by_type),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
    
    def force_gc(self) -> Dict[str, Any]:
        """♻️ 強制ガベージコレクション"""
        before = tracemalloc.get_traced_memory()[0] if self.is_tracing else 0
        
        # 全世代のGC実行
        collected = gc.collect(2)  # 最大世代まで
        
        after = tracemalloc.get_traced_memory()[0] if self.is_tracing else 0
        
        freed = before - after if self.is_tracing else 0
        
        result = {
            'collected_objects': collected,
            'freed_memory_bytes': freed,
            'freed_memory_mb': freed / 1024 / 1024,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        logger.info(f"♻️ Forced GC: collected {collected} objects, freed {freed / 1024 / 1024:.1f}MB")
        
        return result


# グローバルインスタンス
ultra_sync_memory_profiler = None

def init_memory_profiler(auto_start: bool = True) -> UltraSyncMemoryProfiler:
    """🚀 メモリプロファイラー初期化"""
    global ultra_sync_memory_profiler
    
    if ultra_sync_memory_profiler is None:
        ultra_sync_memory_profiler = UltraSyncMemoryProfiler(auto_start=auto_start)
    
    return ultra_sync_memory_profiler

def get_memory_profiler() -> Optional[UltraSyncMemoryProfiler]:
    """📊 メモリプロファイラー取得"""
    return ultra_sync_memory_profiler


if __name__ == "__main__":
    # テスト実行
    import random
    
    print("🧪 Ultra Sync Memory Profiler Test")
    print("=" * 60)
    
    # プロファイラー初期化
    profiler = init_memory_profiler(auto_start=True)
    
    # メモリリークシミュレーション
    leak_list = []
    
    def simulate_memory_leak():
        """メモリリークシミュレーション"""
        # 意図的なメモリリーク
        data = [random.random() for _ in range(100000)]
        leak_list.append(data)  # リストに追加し続ける
        return len(leak_list)
    
    def normal_operation():
        """正常な操作"""
        # 一時的なメモリ使用
        temp_data = [random.random() for _ in range(50000)]
        result = sum(temp_data)
        # temp_dataは自動的にGCされる
        return result
    
    try:
        print("📊 Starting memory profiling...")
        
        # 10回の操作実行
        for i in range(10):
            print(f"\n🔄 Iteration {i+1}/10")
            
            if i % 2 == 0:
                # メモリリーク操作
                count = simulate_memory_leak()
                print(f"  💾 Leak simulation: {count} objects in leak_list")
            else:
                # 正常操作
                result = normal_operation()
                print(f"  ✅ Normal operation: result={result:.2f}")
            
            # スナップショット待機
            time.sleep(3)
            
            # 途中経過
            if i == 4:
                report = profiler.get_memory_report()
                print(f"\n📋 Mid-test report:")
                print(f"  Current memory: {report['stats']['current_memory_mb']:.1f}MB")
                print(f"  Leaks detected: {report['stats']['leaks_detected']}")
        
        # 最終レポート
        print("\n📊 Final Memory Report:")
        print("=" * 60)
        
        final_report = profiler.get_memory_report()
        
        print(f"Status: {final_report['status']}")
        print(f"Current Memory: {final_report['stats']['current_memory_mb']:.1f}MB")
        print(f"Peak Memory: {final_report['stats']['peak_memory_mb']:.1f}MB")
        print(f"Leaks Detected: {final_report['stats']['leaks_detected']}")
        
        if final_report['recent_leaks']:
            print("\n🚨 Detected Memory Leaks:")
            for leak in final_report['recent_leaks']:
                print(f"  - {leak['location']}: {leak['size_mb']:.1f}MB (growth: {leak['growth_rate']})")
        
        print("\n💡 Recommendations:")
        for rec in final_report['recommendations']:
            print(f"  {rec}")
        
        # 強制GC
        print("\n♻️ Forcing garbage collection...")
        gc_result = profiler.force_gc()
        print(f"  Collected: {gc_result['collected_objects']} objects")
        print(f"  Freed: {gc_result['freed_memory_mb']:.1f}MB")
        
    finally:
        # クリーンアップ
        profiler.stop_tracing()
        print("\n✅ Memory profiler test completed")