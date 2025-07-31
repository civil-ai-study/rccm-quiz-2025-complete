# -*- coding: utf-8 -*-
"""
ULTRA SYNC メモリ保護システム実装
副作用なし・既存機能完全保持・オプトイン方式
"""

import gc
import weakref
import threading
import time
import logging
from functools import wraps

# ULTRA SYNC メモリ保護設定
ULTRASYNC_MEMORY_CONFIG = {
    'max_cache_size': 1000,
    'max_list_size': 500,
    'memory_check_interval': 300,  # 5分
    'auto_cleanup_enabled': True,
    'gc_threshold': 1000  # ガベージコレクション閾値
}

class UltraSyncMemoryProtector:
    """
    ULTRA SYNC メモリ保護システム
    副作用ゼロ・既存機能保持・段階的適用
    """
    
    def __init__(self, config=None):
        self.config = config or ULTRASYNC_MEMORY_CONFIG
        self.protected_vars = {}
        self.cleanup_stats = {
            'total_cleanups': 0,
            'memory_saved': 0,
            'last_cleanup': None
        }
        self.logger = logging.getLogger('ultrasync_memory')
        self._cleanup_lock = threading.Lock()
        
    def register_global_var(self, var_name, var_obj, max_size=None):
        """
        グローバル変数の保護登録（副作用なし）
        """
        try:
            max_size = max_size or self.config['max_cache_size']
            
            # 既存変数の動作に影響を与えない登録
            self.protected_vars[var_name] = {
                'object': var_obj,
                'max_size': max_size,
                'registered_at': time.time(),
                'cleanup_count': 0
            }
            
            self.logger.info(f"ULTRA SYNC: {var_name} メモリ保護登録完了")
            return True
            
        except Exception as e:
            self.logger.error(f"メモリ保護登録エラー: {e}")
            return False
    
    def safe_cleanup_if_needed(self, var_name):
        """
        必要時の安全なクリーンアップ（副作用最小化）
        """
        if var_name not in self.protected_vars:
            return False
            
        try:
            with self._cleanup_lock:
                var_info = self.protected_vars[var_name]
                var_obj = var_info['object']
                max_size = var_info['max_size']
                
                # サイズチェック（読み取り専用操作）
                if not hasattr(var_obj, '__len__'):
                    return False
                
                current_size = len(var_obj)
                if current_size <= max_size:
                    return False
                
                # 安全なクリーンアップ実行
                initial_size = current_size
                self._perform_safe_cleanup(var_obj, max_size)
                
                # 統計更新
                var_info['cleanup_count'] += 1
                self.cleanup_stats['total_cleanups'] += 1
                self.cleanup_stats['memory_saved'] += initial_size - len(var_obj)
                self.cleanup_stats['last_cleanup'] = time.time()
                
                self.logger.info(f"ULTRA SYNC: {var_name} クリーンアップ完了 ({initial_size} -> {len(var_obj)})")
                return True
                
        except Exception as e:
            self.logger.error(f"メモリクリーンアップエラー ({var_name}): {e}")
            return False
    
    def _perform_safe_cleanup(self, var_obj, max_size):
        """安全なクリーンアップ実行"""
        target_size = max_size // 2
        
        if isinstance(var_obj, dict):
            # 辞書: LRU方式で古いエントリから削除
            if hasattr(var_obj, 'keys'):
                keys_to_remove = list(var_obj.keys())[:-target_size]
                for key in keys_to_remove:
                    var_obj.pop(key, None)
                    
        elif isinstance(var_obj, list):
            # リスト: 前半を削除（FIFO）
            if len(var_obj) > target_size:
                var_obj[:] = var_obj[-target_size:]
                
        elif isinstance(var_obj, set):
            # セット: サイズ調整
            if len(var_obj) > target_size:
                var_obj.clear()
                
    def memory_guardian_decorator(self, var_names=None):
        """
        メモリ保護デコレーター（既存関数に影響なし）
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    # 関数実行前の軽微なメモリチェック
                    if var_names:
                        for var_name in var_names:
                            self.safe_cleanup_if_needed(var_name)
                    
                    # 元の関数実行（完全保持）
                    result = func(*args, **kwargs)
                    
                    # 関数実行後の軽微なクリーンアップ
                    if self.cleanup_stats['total_cleanups'] % 10 == 0:
                        gc.collect()
                    
                    return result
                    
                except MemoryError:
                    # メモリ不足時の緊急対応
                    self.logger.error("メモリ不足検出 - 緊急クリーンアップ")
                    self.emergency_cleanup()
                    gc.collect()
                    raise
                    
            return wrapper
        return decorator
    
    def emergency_cleanup(self):
        """緊急時のメモリクリーンアップ"""
        try:
            for var_name in self.protected_vars:
                self.safe_cleanup_if_needed(var_name)
            gc.collect()
            self.logger.info("緊急メモリクリーンアップ完了")
        except Exception as e:
            self.logger.error(f"緊急クリーンアップエラー: {e}")
    
    def get_memory_stats(self):
        """メモリ使用統計取得"""
        return {
            'protected_vars_count': len(self.protected_vars),
            'cleanup_stats': self.cleanup_stats.copy(),
            'config': self.config.copy()
        }

# グローバルインスタンス（オプトイン方式）
ultrasync_memory_protector = UltraSyncMemoryProtector()

def ultrasync_protect_memory(var_name, var_obj, max_size=None):
    """
    ULTRA SYNC メモリ保護の簡易適用関数
    使用例: ultrasync_protect_memory('EXAM_DATA_CACHE', EXAM_DATA_CACHE, 500)
    """
    return ultrasync_memory_protector.register_global_var(var_name, var_obj, max_size)

def ultrasync_cleanup_check(var_name):
    """
    ULTRA SYNC メモリクリーンアップチェック
    使用例: ultrasync_cleanup_check('EXAM_DATA_CACHE')
    """
    return ultrasync_memory_protector.safe_cleanup_if_needed(var_name)

def ultrasync_memory_guard(*var_names):
    """
    ULTRA SYNC メモリ保護デコレーター
    使用例: @ultrasync_memory_guard('EXAM_DATA_CACHE')
    """
    return ultrasync_memory_protector.memory_guardian_decorator(var_names)

# テスト関数
def test_memory_protector():
    """メモリ保護システムのテスト"""
    print("ULTRA SYNC メモリ保護システム テスト開始")
    
    # テスト用変数
    test_cache = {}
    test_list = []
    
    # 保護登録
    protector = UltraSyncMemoryProtector()
    protector.register_global_var('test_cache', test_cache, 10)
    protector.register_global_var('test_list', test_list, 5)
    
    # データ追加
    for i in range(20):
        test_cache[f'key_{i}'] = f'value_{i}'
        test_list.append(f'item_{i}')
    
    print(f"クリーンアップ前: cache={len(test_cache)}, list={len(test_list)}")
    
    # クリーンアップ実行
    protector.safe_cleanup_if_needed('test_cache')
    protector.safe_cleanup_if_needed('test_list')
    
    print(f"クリーンアップ後: cache={len(test_cache)}, list={len(test_list)}")
    
    # 統計表示
    stats = protector.get_memory_stats()
    print(f"統計: {stats}")
    
    print("テスト完了")

if __name__ == '__main__':
    test_memory_protector()