#!/usr/bin/env python3
"""
⚡ Redis Cache Implementation - CSV読み込みボトルネック解消
頻繁なCSV読み込み問題を高速Redisキャッシュで解決
"""

import os
import json
import hashlib
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from functools import wraps

# Redis imports with graceful fallback
try:
    import redis
    from flask_caching import Cache
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None
    Cache = None

logger = logging.getLogger(__name__)

class RedisCacheManager:
    """High-performance Redis cache manager for RCCM Quiz data"""
    
    def __init__(self, app=None, config=None):
        self.app = app
        self.cache = None
        self.redis_client = None
        self.config = config or {}
        
        # Default configuration
        self.default_config = {
            'CACHE_TYPE': 'redis',
            'CACHE_REDIS_URL': os.environ.get('REDIS_URL', 'redis://localhost:6379/0'),
            'CACHE_DEFAULT_TIMEOUT': 300,  # 5 minutes for question data
            'CACHE_KEY_PREFIX': 'rccm_quiz_',
            'CACHE_REDIS_DB': 0,
            'CACHE_REDIS_PASSWORD': os.environ.get('REDIS_PASSWORD'),
            'CACHE_REDIS_SOCKET_TIMEOUT': 30,
            'CACHE_REDIS_CONNECTION_TIMEOUT': 10,
            'CACHE_REDIS_MAX_CONNECTIONS': 50
        }
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize cache with Flask app"""
        if not REDIS_AVAILABLE:
            logger.warning("⚠️ Redis/Flask-Caching not available. Using in-memory fallback.")
            self._setup_memory_fallback()
            return
        
        try:
            # Merge configuration
            cache_config = {**self.default_config, **self.config}
            app.config.update(cache_config)
            
            # Initialize Flask-Caching
            self.cache = Cache(app, config=cache_config)
            
            # Initialize direct Redis client for advanced operations
            self.redis_client = redis.from_url(
                cache_config['CACHE_REDIS_URL'],
                socket_timeout=cache_config['CACHE_REDIS_SOCKET_TIMEOUT'],
                socket_connect_timeout=cache_config['CACHE_REDIS_CONNECTION_TIMEOUT'],
                max_connections=cache_config['CACHE_REDIS_MAX_CONNECTIONS'],
                decode_responses=True
            )
            
            # Test connection
            self.redis_client.ping()
            logger.info("✅ Redis cache initialized successfully")
            logger.info(f"🔗 Redis URL: {cache_config['CACHE_REDIS_URL'].split('@')[0]}@***")
            
        except Exception as e:
            logger.error(f"❌ Redis initialization failed: {e}")
            self._setup_memory_fallback()
    
    def _setup_memory_fallback(self):
        """Setup in-memory cache as fallback"""
        self._memory_cache = {}
        self._cache_timestamps = {}
        logger.info("🔄 Using in-memory cache fallback")
    
    def get_cache_key(self, key_type: str, identifier: str, **kwargs) -> str:
        """Generate consistent cache keys"""
        base_key = f"{self.default_config['CACHE_KEY_PREFIX']}{key_type}:{identifier}"
        
        if kwargs:
            # Add parameters to key for uniqueness
            params = "_".join(f"{k}:{v}" for k, v in sorted(kwargs.items()))
            base_key += f":{params}"
        
        return base_key
    
    def get_questions_by_department(self, department: str, question_count: Optional[int] = None) -> List[Dict]:
        """Get cached questions by department with high performance"""
        cache_key = self.get_cache_key('dept_questions', department, count=question_count)
        
        try:
            if self.cache:
                # Use Flask-Caching for primary cache
                cached_data = self.cache.get(cache_key)
                if cached_data is not None:
                    logger.debug(f"🎯 Cache HIT: {department} ({len(cached_data)} questions)")
                    return cached_data
            else:
                # Use memory fallback
                cached_data = self._get_from_memory_cache(cache_key)
                if cached_data is not None:
                    return cached_data
            
            logger.debug(f"💾 Cache MISS: {department}")
            return []
            
        except Exception as e:
            logger.error(f"❌ Cache get error for {department}: {e}")
            return []
    
    def set_questions_by_department(self, department: str, questions: List[Dict], 
                                  question_count: Optional[int] = None, timeout: int = 300) -> bool:
        """Cache questions by department with data integrity validation"""
        if not questions:
            logger.warning(f"⚠️ Attempting to cache empty questions for {department}")
            return False
        
        cache_key = self.get_cache_key('dept_questions', department, count=question_count)
        
        try:
            # Validate question data before caching
            if not self._validate_question_data(questions):
                logger.error(f"❌ Invalid question data for {department}")
                return False
            
            if self.cache:
                # Use Flask-Caching
                success = self.cache.set(cache_key, questions, timeout=timeout)
                if success:
                    logger.info(f"💾 Cached {len(questions)} questions for {department} (TTL: {timeout}s)")
                return success
            else:
                # Use memory fallback
                return self._set_to_memory_cache(cache_key, questions, timeout)
                
        except Exception as e:
            logger.error(f"❌ Cache set error for {department}: {e}")
            return False
    
    def get_user_session_data(self, user_id: str, session_key: str) -> Optional[Dict]:
        """Get cached user session data"""
        cache_key = self.get_cache_key('user_session', f"{user_id}:{session_key}")
        
        try:
            if self.cache:
                return self.cache.get(cache_key)
            else:
                return self._get_from_memory_cache(cache_key)
        except Exception as e:
            logger.error(f"❌ Session cache get error: {e}")
            return None
    
    def set_user_session_data(self, user_id: str, session_key: str, data: Dict, timeout: int = 3600) -> bool:
        """Cache user session data"""
        cache_key = self.get_cache_key('user_session', f"{user_id}:{session_key}")
        
        try:
            if self.cache:
                return self.cache.set(cache_key, data, timeout=timeout)
            else:
                return self._set_to_memory_cache(cache_key, data, timeout)
        except Exception as e:
            logger.error(f"❌ Session cache set error: {e}")
            return False
    
    def invalidate_department_cache(self, department: str) -> bool:
        """Invalidate all cached data for a specific department"""
        try:
            if self.redis_client:
                # Use Redis pattern matching to delete related keys
                pattern = f"{self.default_config['CACHE_KEY_PREFIX']}dept_questions:{department}*"
                keys = self.redis_client.keys(pattern)
                if keys:
                    deleted = self.redis_client.delete(*keys)
                    logger.info(f"🗑️ Invalidated {deleted} cache entries for {department}")
                    return True
            else:
                # Memory fallback - remove matching keys
                keys_to_remove = [k for k in self._memory_cache.keys() 
                                if f"dept_questions:{department}" in k]
                for key in keys_to_remove:
                    del self._memory_cache[key]
                    if key in self._cache_timestamps:
                        del self._cache_timestamps[key]
                logger.info(f"🗑️ Invalidated {len(keys_to_remove)} memory cache entries")
                return True
                
        except Exception as e:
            logger.error(f"❌ Cache invalidation error for {department}: {e}")
            return False
    
    def clear_all_cache(self) -> bool:
        """Clear all cached data"""
        try:
            if self.cache:
                self.cache.clear()
                logger.info("🗑️ All cache cleared via Flask-Caching")
                return True
            else:
                self._memory_cache.clear()
                self._cache_timestamps.clear()
                logger.info("🗑️ All memory cache cleared")
                return True
        except Exception as e:
            logger.error(f"❌ Cache clear error: {e}")
            return False
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        try:
            if self.redis_client:
                info = self.redis_client.info()
                return {
                    'cache_type': 'redis',
                    'status': 'connected',
                    'memory_usage': info.get('used_memory_human', 'unknown'),
                    'connected_clients': info.get('connected_clients', 0),
                    'total_commands': info.get('total_commands_processed', 0),
                    'keyspace_hits': info.get('keyspace_hits', 0),
                    'keyspace_misses': info.get('keyspace_misses', 0),
                    'hit_rate': self._calculate_hit_rate(
                        info.get('keyspace_hits', 0), 
                        info.get('keyspace_misses', 0)
                    )
                }
            else:
                return {
                    'cache_type': 'memory_fallback',
                    'status': 'active',
                    'cached_keys': len(self._memory_cache),
                    'memory_usage': f"{len(str(self._memory_cache))} bytes (estimated)"
                }
        except Exception as e:
            return {
                'cache_type': 'unknown',
                'status': 'error',
                'error': str(e)
            }
    
    def _validate_question_data(self, questions: List[Dict]) -> bool:
        """Validate question data structure"""
        if not isinstance(questions, list) or not questions:
            return False
        
        required_fields = ['id', 'question', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer']
        
        for question in questions:
            if not isinstance(question, dict):
                return False
            for field in required_fields:
                if field not in question or not str(question[field]).strip():
                    return False
        
        return True
    
    def _get_from_memory_cache(self, key: str) -> Optional[Any]:
        """Get data from memory cache with TTL check"""
        if key in self._memory_cache:
            timestamp = self._cache_timestamps.get(key)
            if timestamp and datetime.now() < timestamp:
                return self._memory_cache[key]
            else:
                # Expired
                del self._memory_cache[key]
                if key in self._cache_timestamps:
                    del self._cache_timestamps[key]
        return None
    
    def _set_to_memory_cache(self, key: str, data: Any, timeout: int) -> bool:
        """Set data to memory cache with TTL"""
        try:
            self._memory_cache[key] = data
            self._cache_timestamps[key] = datetime.now() + timedelta(seconds=timeout)
            return True
        except Exception as e:
            logger.error(f"❌ Memory cache set error: {e}")
            return False
    
    def _calculate_hit_rate(self, hits: int, misses: int) -> float:
        """Calculate cache hit rate percentage"""
        total = hits + misses
        return round((hits / total * 100) if total > 0 else 0.0, 2)

# Global cache manager instance
cache_manager = None

def init_cache(app, config=None):
    """Initialize global cache manager"""
    global cache_manager
    cache_manager = RedisCacheManager(app, config)
    return cache_manager

def cached_questions(timeout=300, key_suffix=""):
    """Decorator for caching question data with intelligent key generation"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not cache_manager:
                logger.warning("⚠️ Cache manager not initialized")
                return func(*args, **kwargs)
            
            # Generate cache key from function arguments
            func_name = func.__name__
            args_str = "_".join(str(arg) for arg in args)
            kwargs_str = "_".join(f"{k}:{v}" for k, v in sorted(kwargs.items()))
            
            cache_key_parts = [func_name, args_str, kwargs_str, key_suffix]
            cache_key_raw = "_".join(filter(None, cache_key_parts))
            
            # Use hash for long keys
            if len(cache_key_raw) > 100:
                cache_key = hashlib.md5(cache_key_raw.encode()).hexdigest()
            else:
                cache_key = cache_key_raw
            
            cache_key = f"{cache_manager.default_config['CACHE_KEY_PREFIX']}func:{cache_key}"
            
            try:
                if cache_manager.cache:
                    cached_result = cache_manager.cache.get(cache_key)
                    if cached_result is not None:
                        logger.debug(f"🎯 Function cache HIT: {func_name}")
                        return cached_result
                else:
                    cached_result = cache_manager._get_from_memory_cache(cache_key)
                    if cached_result is not None:
                        return cached_result
                
                # Cache miss - execute function
                logger.debug(f"💾 Function cache MISS: {func_name}")
                result = func(*args, **kwargs)
                
                # Cache the result
                if cache_manager.cache:
                    cache_manager.cache.set(cache_key, result, timeout=timeout)
                else:
                    cache_manager._set_to_memory_cache(cache_key, result, timeout)
                
                return result
                
            except Exception as e:
                logger.error(f"❌ Function cache error for {func_name}: {e}")
                return func(*args, **kwargs)
        
        return wrapper
    return decorator

# Utility functions for direct cache access
def get_cached_questions(department: str, question_count: Optional[int] = None) -> List[Dict]:
    """Utility function to get cached questions"""
    if cache_manager:
        return cache_manager.get_questions_by_department(department, question_count)
    return []

def cache_questions(department: str, questions: List[Dict], 
                   question_count: Optional[int] = None, timeout: int = 300) -> bool:
    """Utility function to cache questions"""
    if cache_manager:
        return cache_manager.set_questions_by_department(department, questions, question_count, timeout)
    return False

def invalidate_cache(department: str = None) -> bool:
    """Utility function to invalidate cache"""
    if cache_manager:
        if department:
            return cache_manager.invalidate_department_cache(department)
        else:
            return cache_manager.clear_all_cache()
    return False

def get_cache_statistics() -> Dict[str, Any]:
    """Utility function to get cache statistics"""
    if cache_manager:
        return cache_manager.get_cache_stats()
    return {'cache_type': 'none', 'status': 'not_initialized'}

if __name__ == "__main__":
    # Test cache functionality
    print("⚡ Redis Cache Implementation Test")
    print("=" * 50)
    
    if REDIS_AVAILABLE:
        print("✅ Redis libraries available")
        
        # Test cache configuration
        test_config = {
            'CACHE_TYPE': 'redis',
            'CACHE_REDIS_URL': 'redis://localhost:6379/0',
            'CACHE_DEFAULT_TIMEOUT': 300
        }
        
        # Create mock Flask app for testing
        class MockApp:
            def __init__(self):
                self.config = {}
        
        app = MockApp()
        cache_mgr = RedisCacheManager(app, test_config)
        
        print(f"📊 Cache Stats: {cache_mgr.get_cache_stats()}")
        print("Cache implementation ready for integration")
        
    else:
        print("❌ Redis libraries not available")
        print("💡 Install with: pip install redis flask-caching")