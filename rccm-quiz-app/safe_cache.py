# 🛡️ 副作用ゼロ保証のキャッシュシステム
"""
既存機能に一切影響を与えない安全なキャッシュ機能
キャッシュが失敗しても必ず元の関数を実行して結果を保証
"""

import time
import threading
from typing import Any, Callable, Optional, Dict
from functools import wraps

class SafeCache:
    """副作用ゼロを保証するキャッシュクラス"""
    
    def __init__(self):
        self.enabled = False  # デフォルト無効
        self.cache = {}
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'errors': 0
        }
        self.default_timeout = 300  # 5分
        self._lock = threading.Lock()
    
    def enable(self):
        """キャッシュを有効化"""
        try:
            self.enabled = True
        except Exception:
            self.enabled = False
    
    def disable(self):
        """キャッシュを無効化"""
        try:
            self.enabled = False
            self.cache.clear()
        except Exception:
            pass
    
    def _is_expired(self, cache_entry: Dict) -> bool:
        """キャッシュエントリの有効期限チェック"""
        try:
            if 'expires_at' not in cache_entry:
                return True
            return time.time() > cache_entry['expires_at']
        except Exception:
            return True  # エラー時は期限切れとして扱う
    
    def get_or_execute(self, key: str, func: Callable, timeout: Optional[int] = None) -> Any:
        """
        キャッシュから取得、なければ関数を実行
        キャッシュエラー時は必ず元の関数を実行（安全性保証）
        """
        # キャッシュ無効時は直接実行
        if not self.enabled:
            return func()
        
        # キャッシュから取得を試行
        try:
            with self._lock:
                if key in self.cache:
                    cache_entry = self.cache[key]
                    if not self._is_expired(cache_entry):
                        self.cache_stats['hits'] += 1
                        return cache_entry['value']
                    else:
                        # 期限切れエントリを削除
                        del self.cache[key]
        except Exception:
            # キャッシュアクセスエラーは無視
            self.cache_stats['errors'] += 1
        
        # キャッシュミス時は関数を実行
        try:
            result = func()  # 必ず元の関数を実行
            self.cache_stats['misses'] += 1
            
            # 結果をキャッシュに保存を試行（失敗しても結果は返す）
            try:
                timeout = timeout or self.default_timeout
                expires_at = time.time() + timeout
                
                with self._lock:
                    self.cache[key] = {
                        'value': result,
                        'expires_at': expires_at,
                        'created_at': time.time()
                    }
            except Exception:
                # キャッシュ保存エラーは無視
                self.cache_stats['errors'] += 1
            
            return result
            
        except Exception as e:
            # 元の関数のエラーはそのまま再発生
            raise e
    
    def clear(self):
        """キャッシュを安全にクリア"""
        try:
            with self._lock:
                self.cache.clear()
                self.cache_stats['hits'] = 0
                self.cache_stats['misses'] = 0
                self.cache_stats['errors'] = 0
        except Exception:
            pass
    
    def get_stats(self) -> Dict[str, Any]:
        """キャッシュ統計を取得"""
        try:
            total_requests = self.cache_stats['hits'] + self.cache_stats['misses']
            hit_rate = (self.cache_stats['hits'] / total_requests * 100) if total_requests > 0 else 0
            
            return {
                'enabled': self.enabled,
                'cache_size': len(self.cache),
                'hit_rate_percent': round(hit_rate, 2),
                'total_hits': self.cache_stats['hits'],
                'total_misses': self.cache_stats['misses'],
                'total_errors': self.cache_stats['errors']
            }
        except Exception:
            return {
                'enabled': False,
                'error': 'Unable to get stats'
            }

# グローバルキャッシュインスタンス
safe_cache = SafeCache()

def safe_cached(timeout: int = 300, key_prefix: str = ""):
    """
    既存関数に後付け可能な安全なキャッシュデコレーター
    キャッシュが失敗しても必ず元の関数を実行
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # キャッシュキーを生成
            try:
                # 引数からキャッシュキーを生成
                args_str = str(args) + str(sorted(kwargs.items()))
                cache_key = f"{key_prefix}:{func.__name__}:{hash(args_str)}"
            except Exception:
                # キー生成失敗時は直接実行
                return func(*args, **kwargs)
            
            # キャッシュから取得または実行
            def execute_original():
                return func(*args, **kwargs)
            
            return safe_cache.get_or_execute(cache_key, execute_original, timeout)
        
        return wrapper
    return decorator

class SafeFileCache:
    """ファイル読み込み専用の安全なキャッシュ"""
    
    def __init__(self):
        self.file_cache = {}
        self.enabled = False
        self._lock = threading.Lock()
    
    def enable(self):
        """ファイルキャッシュを有効化"""
        self.enabled = True
    
    def disable(self):
        """ファイルキャッシュを無効化"""
        self.enabled = False
        self.file_cache.clear()
    
    def get_file_content(self, file_path: str, reader_func: Callable) -> Any:
        """
        ファイル内容をキャッシュから取得、なければ読み込み
        ファイル変更時間もチェックして自動更新
        """
        if not self.enabled:
            return reader_func(file_path)
        
        try:
            import os
            
            # ファイルの最終更新時間を取得
            file_mtime = os.path.getmtime(file_path)
            
            with self._lock:
                cache_entry = self.file_cache.get(file_path)
                
                # キャッシュが有効かチェック
                if cache_entry and cache_entry['mtime'] >= file_mtime:
                    return cache_entry['content']
            
            # ファイルを読み込み
            content = reader_func(file_path)
            
            # キャッシュに保存
            try:
                with self._lock:
                    self.file_cache[file_path] = {
                        'content': content,
                        'mtime': file_mtime
                    }
            except Exception:
                pass  # キャッシュ保存エラーは無視
            
            return content
            
        except Exception:
            # エラー時は直接読み込み
            return reader_func(file_path)

# グローバルファイルキャッシュ
safe_file_cache = SafeFileCache()

# 使用例とテスト関数
def test_safe_cache():
    """安全なキャッシュのテスト"""
    print("🧪 Testing safe cache system...")
    
    # テスト関数
    call_count = 0
    def expensive_function(x):
        nonlocal call_count
        call_count += 1
        time.sleep(0.1)  # 重い処理をシミュレート
        return x * 2
    
    # キャッシュを有効化
    safe_cache.enable()
    
    # キャッシュデコレーターを適用
    @safe_cached(timeout=60)
    def cached_expensive_function(x):
        return expensive_function(x)
    
    # テスト実行
    print("First call (should miss cache):", cached_expensive_function(5))
    print("Second call (should hit cache):", cached_expensive_function(5))
    print("Call count:", call_count)
    print("Cache stats:", safe_cache.get_stats())
    
    # キャッシュを無効化
    safe_cache.disable()
    print("Cache disabled, stats:", safe_cache.get_stats())

if __name__ == "__main__":
    test_safe_cache()

# 既存コードでの使用例
"""
# 既存のapp.pyに以下を追加するだけ
from safe_cache import safe_cached, safe_cache, safe_file_cache

# キャッシュを有効化（必要に応じて）
# safe_cache.enable()
# safe_file_cache.enable()

# 既存の重い関数にキャッシュを後付け
@safe_cached(timeout=600, key_prefix="questions")
def load_questions_improved():
    # 既存コードはそのまま
    pass

# ファイル読み込みのキャッシュ
def load_csv_file_cached(file_path):
    def reader(path):
        # 既存のファイル読み込み処理
        pass
    
    return safe_file_cache.get_file_content(file_path, reader)
"""