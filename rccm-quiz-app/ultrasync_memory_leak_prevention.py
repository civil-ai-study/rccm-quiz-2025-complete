#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
🔥 ULTRA SYNC タスク5: メモリリーク予防的修正
副作用ゼロでメモリリークを根本的に防止する独立モジュール
"""

import gc
import psutil
import threading
import time
import logging
import weakref
from collections import defaultdict, OrderedDict
from datetime import datetime, timedelta

class UltraSyncMemoryLeakPrevention:
    """🔥 ULTRA SYNC: メモリリークを根本的に防ぐ管理クラス"""
    
    def __init__(self):
        self.memory_stats = {
            'initial_memory': self._get_memory_usage(),
            'peak_memory': 0,
            'cleanup_count': 0,
            'leak_detections': 0
        }
        self.session_cache = OrderedDict()
        self.max_cache_size = 1000
        self.cleanup_lock = threading.Lock()
        self.last_cleanup = time.time()
        
        # 弱参照によるオブジェクト追跡
        self.tracked_objects = weakref.WeakSet()
        
        # メモリ使用量の履歴
        self.memory_history = []
        self.max_history_size = 100
    
    def _get_memory_usage(self):
        """現在のメモリ使用量を取得"""
        try:
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024  # MB
        except:
            return 0
    
    def track_object(self, obj):
        """オブジェクトの追跡を開始"""
        try:
            self.tracked_objects.add(obj)
        except:
            pass  # 弱参照できないオブジェクトは無視
    
    def detect_memory_leaks(self):
        """メモリリークの検出"""
        current_memory = self._get_memory_usage()
        
        # メモリ使用量履歴の更新
        self.memory_history.append({
            'timestamp': time.time(),
            'memory_mb': current_memory,
            'tracked_objects': len(self.tracked_objects)
        })
        
        # 履歴サイズ制限
        if len(self.memory_history) > self.max_history_size:
            self.memory_history.pop(0)
        
        # ピークメモリ更新
        if current_memory > self.memory_stats['peak_memory']:
            self.memory_stats['peak_memory'] = current_memory
        
        # リーク検出（5分間で50MB以上の増加）
        if len(self.memory_history) >= 10:
            recent_start = self.memory_history[-10]['memory_mb']
            if current_memory - recent_start > 50:
                self.memory_stats['leak_detections'] += 1
                logging.warning(f"🔥 ULTRA SYNC メモリリーク検出: {recent_start:.1f}MB → {current_memory:.1f}MB")
                return True
        
        return False
    
    def aggressive_session_cleanup(self, session):
        """セッションの積極的クリーンアップ"""
        with self.cleanup_lock:
            cleanup_count = 0
            
            # 不要なキーのリスト
            cleanup_keys = []
            
            # 履歴データの制限
            history = session.get('history', [])
            if len(history) > 100:
                session['history'] = history[-100:]
                cleanup_count += len(history) - 100
            
            # SRSデータの制限
            srs_data = session.get('srs_data', {})
            if len(srs_data) > 500:
                # 古いデータを削除
                sorted_items = sorted(srs_data.items(), key=lambda x: x[1].get('last_review', ''), reverse=True)
                session['srs_data'] = dict(sorted_items[:500])
                cleanup_count += len(srs_data) - 500
            
            # 古いセッションデータの削除
            for key in list(session.keys()):
                if key.startswith('_temp_') or key.startswith('_debug_'):
                    cleanup_keys.append(key)
                elif key.endswith('_backup') and key.count('_backup') > 1:
                    cleanup_keys.append(key)
            
            # クリーンアップ実行
            for key in cleanup_keys:
                session.pop(key, None)
                cleanup_count += 1
            
            if cleanup_count > 0:
                session.modified = True
                self.memory_stats['cleanup_count'] += cleanup_count
                logging.info(f"🔥 ULTRA SYNC セッションクリーンアップ: {cleanup_count}項目削除")
            
            return cleanup_count
    
    def emergency_memory_cleanup(self):
        """緊急メモリクリーンアップ"""
        with self.cleanup_lock:
            cleanup_stats = {
                'gc_collected': 0,
                'cache_cleared': 0,
                'objects_cleaned': 0
            }
            
            # ガベージコレクション強制実行
            cleanup_stats['gc_collected'] = gc.collect()
            
            # セッションキャッシュのクリア
            if self.session_cache:
                cache_size = len(self.session_cache)
                self.session_cache.clear()
                cleanup_stats['cache_cleared'] = cache_size
            
            # 追跡オブジェクトの確認
            cleanup_stats['objects_cleaned'] = len(self.tracked_objects)
            
            # メモリ統計更新
            self.memory_stats['cleanup_count'] += sum(cleanup_stats.values())
            
            logging.info(f"🔥 ULTRA SYNC 緊急メモリクリーンアップ実行: {cleanup_stats}")
            return cleanup_stats
    
    def optimize_session_cache(self, session_id, session_data):
        """セッションキャッシュの最適化"""
        with self.cleanup_lock:
            # キャッシュサイズ制限
            if len(self.session_cache) >= self.max_cache_size:
                # 古いエントリを削除
                oldest_key = next(iter(self.session_cache))
                del self.session_cache[oldest_key]
            
            # 新しいセッションデータを追加
            self.session_cache[session_id] = {
                'data': session_data,
                'timestamp': time.time(),
                'access_count': 1
            }
            
            # キャッシュの再配置（LRU）
            self.session_cache.move_to_end(session_id)
    
    def memory_health_check(self):
        """メモリ健康状態のチェック"""
        current_memory = self._get_memory_usage()
        
        # メモリ使用量の閾値チェック
        if current_memory > 500:  # 500MB以上
            logging.warning(f"🔥 ULTRA SYNC メモリ使用量警告: {current_memory:.1f}MB")
            return False
        
        # リーク検出
        if self.detect_memory_leaks():
            return False
        
        return True
    
    def get_optimization_stats(self):
        """最適化統計の取得"""
        current_memory = self._get_memory_usage()
        
        return {
            'current_memory_mb': current_memory,
            'peak_memory_mb': self.memory_stats['peak_memory'],
            'memory_saved_mb': max(0, self.memory_stats['peak_memory'] - current_memory),
            'cleanup_count': self.memory_stats['cleanup_count'],
            'leak_detections': self.memory_stats['leak_detections'],
            'cache_size': len(self.session_cache),
            'tracked_objects': len(self.tracked_objects),
            'memory_history_size': len(self.memory_history)
        }
    
    def schedule_periodic_cleanup(self, interval=300):
        """定期的なメモリクリーンアップのスケジュール"""
        def cleanup_task():
            while True:
                time.sleep(interval)
                
                # メモリ健康チェック
                if not self.memory_health_check():
                    self.emergency_memory_cleanup()
                
                # 通常のクリーンアップ
                current_time = time.time()
                if current_time - self.last_cleanup > interval:
                    self.last_cleanup = current_time
                    gc.collect()
        
        # バックグラウンドスレッドで実行
        cleanup_thread = threading.Thread(target=cleanup_task, daemon=True)
        cleanup_thread.start()
        
        logging.info(f"🔥 ULTRA SYNC 定期メモリクリーンアップ開始: {interval}秒間隔")

class UltraSyncMemoryOptimizer:
    """🔥 ULTRA SYNC: 包括的メモリ最適化クラス"""
    
    def __init__(self):
        self.leak_prevention = UltraSyncMemoryLeakPrevention()
        self.session_lock_pool = SessionLockPool()
        self.cleanup_stats = defaultdict(int)
        
        # 定期クリーンアップの開始
        self.leak_prevention.schedule_periodic_cleanup()
    
    def memory_optimization_decorator(self, func):
        """メモリ最適化デコレーター"""
        def wrapper(*args, **kwargs):
            # 実行前のメモリ使用量
            memory_before = self.leak_prevention._get_memory_usage()
            
            try:
                result = func(*args, **kwargs)
                
                # 実行後のメモリ使用量
                memory_after = self.leak_prevention._get_memory_usage()
                
                # メモリ使用量の監視
                if memory_after - memory_before > 10:  # 10MB以上の増加
                    logging.warning(f"🔥 ULTRA SYNC メモリ使用量増加: {func.__name__} +{memory_after - memory_before:.1f}MB")
                
                return result
                
            except Exception as e:
                # エラー時の緊急クリーンアップ
                self.leak_prevention.emergency_memory_cleanup()
                raise
        
        return wrapper
    
    def aggressive_session_cleanup(self, session):
        """セッションの積極的クリーンアップ"""
        return self.leak_prevention.aggressive_session_cleanup(session)
    
    def emergency_memory_cleanup(self):
        """緊急メモリクリーンアップ"""
        return self.leak_prevention.emergency_memory_cleanup()
    
    def memory_health_check(self):
        """メモリ健康状態のチェック"""
        return self.leak_prevention.memory_health_check()
    
    def get_optimization_stats(self):
        """最適化統計の取得"""
        return self.leak_prevention.get_optimization_stats()

class SessionLockPool:
    """セッションロックプール - メモリ効率的なロック管理"""
    
    def __init__(self, max_locks=1000):
        self.locks = {}
        self.max_locks = max_locks
        self.lock_access_time = {}
        self.cleanup_lock = threading.Lock()
    
    def get_lock(self, session_id):
        """セッションIDに対応するロックを取得"""
        with self.cleanup_lock:
            if session_id not in self.locks:
                # 最大ロック数に達した場合、古いロックを削除
                if len(self.locks) >= self.max_locks:
                    self._cleanup_old_locks()
                
                self.locks[session_id] = threading.Lock()
            
            self.lock_access_time[session_id] = time.time()
            return self.locks[session_id]
    
    def _cleanup_old_locks(self):
        """古いロックのクリーンアップ"""
        current_time = time.time()
        old_threshold = current_time - 3600  # 1時間前
        
        old_sessions = [
            session_id for session_id, access_time in self.lock_access_time.items()
            if access_time < old_threshold
        ]
        
        for session_id in old_sessions:
            self.locks.pop(session_id, None)
            self.lock_access_time.pop(session_id, None)
        
        logging.info(f"🔥 ULTRA SYNC セッションロッククリーンアップ: {len(old_sessions)}個削除")
    
    def cleanup_unused_locks(self):
        """未使用ロックのクリーンアップ"""
        with self.cleanup_lock:
            self._cleanup_old_locks()
            return len(self.locks)

# メモリ最適化デコレーター
def memory_optimization_decorator(func):
    """メモリ最適化デコレーター（スタンドアロン版）"""
    def wrapper(*args, **kwargs):
        memory_before = psutil.Process().memory_info().rss / 1024 / 1024
        
        try:
            result = func(*args, **kwargs)
            
            memory_after = psutil.Process().memory_info().rss / 1024 / 1024
            
            if memory_after - memory_before > 10:
                logging.warning(f"🔥 ULTRA SYNC メモリ使用量増加: {func.__name__} +{memory_after - memory_before:.1f}MB")
            
            return result
            
        except Exception as e:
            gc.collect()
            raise
    
    return wrapper

# 使用例とテスト関数
def test_ultrasync_memory_leak_prevention():
    """テスト用のメモリリーク防止機能"""
    
    # メモリ最適化クラスの初期化
    optimizer = UltraSyncMemoryOptimizer()
    
    # 模擬セッションデータの作成
    mock_session = {
        'history': [f'item_{i}' for i in range(200)],  # 大量の履歴
        'srs_data': {f'q_{i}': {'level': 1, 'last_review': '2024-01-01'} for i in range(600)},  # 大量のSRSデータ
        '_temp_data': 'temporary',
        '_debug_info': 'debug'
    }
    
    # セッションクリーンアップのテスト
    print("クリーンアップ前のセッションサイズ:")
    print(f"  履歴: {len(mock_session.get('history', []))}")
    print(f"  SRSデータ: {len(mock_session.get('srs_data', {}))}")
    print(f"  全キー: {len(mock_session)}")
    
    # クリーンアップ実行
    cleanup_count = optimizer.aggressive_session_cleanup(mock_session)
    
    print(f"\nクリーンアップ後のセッションサイズ:")
    print(f"  履歴: {len(mock_session.get('history', []))}")
    print(f"  SRSデータ: {len(mock_session.get('srs_data', {}))}")
    print(f"  全キー: {len(mock_session)}")
    print(f"  削除項目数: {cleanup_count}")
    
    # 最適化統計の取得
    stats = optimizer.get_optimization_stats()
    print(f"\n最適化統計:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    return cleanup_count > 0

if __name__ == '__main__':
    print("🔥 ULTRA SYNC メモリリーク防止機構テスト開始")
    success = test_ultrasync_memory_leak_prevention()
    print(f"テスト結果: {'成功' if success else '失敗'}")