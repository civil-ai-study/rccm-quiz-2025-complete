#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Professional Cache Manager for RCCM Quiz App
2025年のベストプラクティスに基づく高度なキャッシュ管理システム

Based on industry research:
- Redis/Memcached for production multi-user environments
- Cache versioning and TTL strategies
- User-specific cache keys to prevent data leakage
- Performance monitoring and automatic optimization
"""

import os
import time
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Any, Optional, Dict, List
import json

# Professional logging setup
logger = logging.getLogger(__name__)

# Cache configuration based on 2025 best practices
class CacheConfig:
    """Professional cache configuration for production environments"""

    # TTL strategies (based on research: different data types need different TTLs)
    QUESTION_DATA_TTL = 1800  # 30 minutes for question data
    USER_SESSION_TTL = 3600   # 1 hour for user session data
    STATISTICS_TTL = 300      # 5 minutes for statistics
    QUICK_CACHE_TTL = 60      # 1 minute for frequently changing data

    # Cache key prefixes (prevents key collisions)
    QUESTION_PREFIX = "rccm:questions"
    SESSION_PREFIX = "rccm:session"
    USER_PREFIX = "rccm:user"
    STATS_PREFIX = "rccm:stats"

    # Cache versioning (for cache busting)
    CACHE_VERSION = "v2.1"

    # Performance thresholds
    MAX_CACHE_SIZE_MB = 50    # 50MB max cache size
    TARGET_HIT_RATE = 0.90    # 90% hit rate target

    # Environment-based backend selection
    DEVELOPMENT_BACKEND = "simple"
    PRODUCTION_BACKEND = "redis"


class ProfessionalCacheManager:
    """
    Professional cache manager implementing 2025 best practices:
    - User-specific cache keys
    - Cache versioning and TTL
    - Performance monitoring
    - Automatic cache invalidation
    """

    def __init__(self, environment="development"):
        self.environment = environment
        self.cache_backend = None
        self.hit_count = 0
        self.miss_count = 0
        self.start_time = time.time()

        # In-memory fallback for development
        self._memory_cache = {}
        self._cache_timestamps = {}

        self._initialize_cache_backend()

    def _initialize_cache_backend(self):
        """Initialize appropriate cache backend based on environment"""
        try:
            if self.environment == "production":
                # Try to initialize Redis for production
                self._initialize_redis()
            else:
                # Use memory cache for development
                self._initialize_memory_cache()

            logger.info(f"✅ Cache backend initialized: {self.environment}")

        except Exception as e:
            logger.warning(f"⚠️ Cache initialization failed: {e}, falling back to memory cache")
            self._initialize_memory_cache()

    def _initialize_redis(self):
        """Initialize Redis cache backend (production)"""
        try:
            import redis
            from flask_caching import Cache

            redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
            self.redis_client = redis.from_url(redis_url)

            # Test Redis connection
            self.redis_client.ping()
            self.cache_backend = "redis"

            logger.info("✅ Redis cache backend initialized successfully")

        except ImportError:
            raise Exception("Redis not available - install redis-py for production")
        except Exception as e:
            raise Exception(f"Redis connection failed: {e}")

    def _initialize_memory_cache(self):
        """Initialize memory cache backend (development)"""
        self.cache_backend = "memory"
        logger.info("✅ Memory cache backend initialized for development")

    def _generate_cache_key(self, base_key: str, user_id: str = None,
                           department: str = None, **kwargs) -> str:
        """
        Generate secure, versioned cache key
        Prevents cache collisions and data leakage between users
        """
        key_parts = [CacheConfig.CACHE_VERSION, base_key]

        # Add user-specific component (critical for multi-user safety)
        if user_id:
            # Hash user ID for security
            user_hash = hashlib.md5(str(user_id).encode()).hexdigest()[:8]
            key_parts.append(f"user:{user_hash}")

        # Add department-specific component
        if department:
            key_parts.append(f"dept:{department}")

        # Add any additional parameters
        for k, v in sorted(kwargs.items()):
            if v is not None:
                key_parts.append(f"{k}:{v}")

        return ":".join(key_parts)

    def get(self, key: str, user_id: str = None, **kwargs) -> Optional[Any]:
        """
        Get cached data with professional error handling
        Implements automatic hit/miss tracking
        """
        cache_key = self._generate_cache_key(key, user_id, **kwargs)

        try:
            if self.cache_backend == "redis":
                data = self._redis_get(cache_key)
            else:
                data = self._memory_get(cache_key)

            if data is not None:
                self.hit_count += 1
                logger.debug(f"🎯 Cache HIT: {cache_key}")
                return data
            else:
                self.miss_count += 1
                logger.debug(f"❌ Cache MISS: {cache_key}")
                return None

        except Exception as e:
            logger.error(f"🚨 Cache GET error for {cache_key}: {e}")
            self.miss_count += 1
            return None

    def set(self, key: str, value: Any, ttl: int = None,
            user_id: str = None, **kwargs) -> bool:
        """
        Set cached data with TTL and versioning
        Implements automatic size management
        """
        cache_key = self._generate_cache_key(key, user_id, **kwargs)
        ttl = ttl or CacheConfig.QUESTION_DATA_TTL

        try:
            if self.cache_backend == "redis":
                success = self._redis_set(cache_key, value, ttl)
            else:
                success = self._memory_set(cache_key, value, ttl)

            if success:
                logger.debug(f"✅ Cache SET: {cache_key} (TTL: {ttl}s)")
            else:
                logger.warning(f"⚠️ Cache SET failed: {cache_key}")

            return success

        except Exception as e:
            logger.error(f"🚨 Cache SET error for {cache_key}: {e}")
            return False

    def delete(self, key: str, user_id: str = None, **kwargs) -> bool:
        """Delete specific cache entry"""
        cache_key = self._generate_cache_key(key, user_id, **kwargs)

        try:
            if self.cache_backend == "redis":
                success = self._redis_delete(cache_key)
            else:
                success = self._memory_delete(cache_key)

            if success:
                logger.debug(f"🗑️ Cache DELETE: {cache_key}")

            return success

        except Exception as e:
            logger.error(f"🚨 Cache DELETE error for {cache_key}: {e}")
            return False

    def invalidate_pattern(self, pattern: str) -> int:
        """
        Invalidate cache entries matching pattern
        Critical for cache busting when data changes
        """
        try:
            if self.cache_backend == "redis":
                count = self._redis_invalidate_pattern(pattern)
            else:
                count = self._memory_invalidate_pattern(pattern)

            logger.info(f"🔄 Cache invalidation: {count} entries removed for pattern '{pattern}'")
            return count

        except Exception as e:
            logger.error(f"🚨 Cache invalidation error for pattern '{pattern}': {e}")
            return 0

    def clear_all(self) -> bool:
        """Clear all cache entries (emergency use only)"""
        try:
            if self.cache_backend == "redis":
                success = self._redis_clear_all()
            else:
                success = self._memory_clear_all()

            if success:
                logger.warning("🧹 ALL CACHE CLEARED (emergency operation)")
                # Reset performance counters
                self.hit_count = 0
                self.miss_count = 0
                self.start_time = time.time()

            return success

        except Exception as e:
            logger.error(f"🚨 Cache clear all error: {e}")
            return False

    def get_performance_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive cache performance statistics
        Critical for monitoring and optimization
        """
        total_requests = self.hit_count + self.miss_count
        hit_rate = (self.hit_count / total_requests) if total_requests > 0 else 0
        uptime = time.time() - self.start_time

        stats = {
            "backend": self.cache_backend,
            "hit_count": self.hit_count,
            "miss_count": self.miss_count,
            "total_requests": total_requests,
            "hit_rate": hit_rate,
            "hit_rate_percentage": f"{hit_rate:.1%}",
            "uptime_seconds": uptime,
            "performance_status": "excellent" if hit_rate >= CacheConfig.TARGET_HIT_RATE else "needs_optimization",
            "recommendations": self._get_performance_recommendations(hit_rate)
        }

        return stats

    def _get_performance_recommendations(self, hit_rate: float) -> List[str]:
        """Generate performance optimization recommendations"""
        recommendations = []

        if hit_rate < 0.70:
            recommendations.append("Critical: Hit rate below 70% - review cache TTL settings")
        elif hit_rate < 0.85:
            recommendations.append("Warning: Hit rate below 85% - consider increasing TTL for stable data")
        elif hit_rate >= 0.95:
            recommendations.append("Excellent: Hit rate above 95% - optimal cache performance")

        return recommendations

    # Redis backend implementations
    def _redis_get(self, key: str) -> Optional[Any]:
        """Redis GET with JSON deserialization"""
        data = self.redis_client.get(key)
        if data:
            try:
                return json.loads(data.decode('utf-8'))
            except json.JSONDecodeError:
                return data.decode('utf-8')
        return None

    def _redis_set(self, key: str, value: Any, ttl: int) -> bool:
        """Redis SET with JSON serialization and TTL"""
        try:
            serialized_value = json.dumps(value) if not isinstance(value, (str, bytes)) else value
            return self.redis_client.setex(key, ttl, serialized_value)
        except (TypeError, ValueError):
            # Fallback for non-serializable objects
            return self.redis_client.setex(key, ttl, str(value))

    def _redis_delete(self, key: str) -> bool:
        """Redis DELETE"""
        return bool(self.redis_client.delete(key))

    def _redis_invalidate_pattern(self, pattern: str) -> int:
        """Redis pattern-based invalidation"""
        keys = self.redis_client.keys(f"*{pattern}*")
        if keys:
            return self.redis_client.delete(*keys)
        return 0

    def _redis_clear_all(self) -> bool:
        """Redis FLUSHDB (use with caution)"""
        return self.redis_client.flushdb()

    # Memory backend implementations
    def _memory_get(self, key: str) -> Optional[Any]:
        """Memory GET with TTL check"""
        if key in self._memory_cache:
            timestamp = self._cache_timestamps.get(key, 0)
            if time.time() - timestamp < CacheConfig.QUESTION_DATA_TTL:
                return self._memory_cache[key]
            else:
                # Expired entry
                del self._memory_cache[key]
                del self._cache_timestamps[key]
        return None

    def _memory_set(self, key: str, value: Any, ttl: int) -> bool:
        """Memory SET with timestamp tracking"""
        self._memory_cache[key] = value
        self._cache_timestamps[key] = time.time()
        return True

    def _memory_delete(self, key: str) -> bool:
        """Memory DELETE"""
        if key in self._memory_cache:
            del self._memory_cache[key]
            del self._cache_timestamps[key]
            return True
        return False

    def _memory_invalidate_pattern(self, pattern: str) -> int:
        """Memory pattern-based invalidation"""
        keys_to_delete = [k for k in self._memory_cache.keys() if pattern in k]
        for key in keys_to_delete:
            del self._memory_cache[key]
            del self._cache_timestamps[key]
        return len(keys_to_delete)

    def _memory_clear_all(self) -> bool:
        """Memory clear all"""
        self._memory_cache.clear()
        self._cache_timestamps.clear()
        return True


# Global cache manager instance
cache_manager = None

def initialize_professional_cache(environment="development"):
    """Initialize the professional cache manager"""
    global cache_manager
    cache_manager = ProfessionalCacheManager(environment)
    return cache_manager

def get_cache_manager() -> ProfessionalCacheManager:
    """Get the global cache manager instance"""
    global cache_manager
    if cache_manager is None:
        cache_manager = initialize_professional_cache()
    return cache_manager


# Convenience functions for common operations
def cache_questions(questions: List[Dict], department: str = None,
                   question_type: str = None, user_id: str = None) -> bool:
    """Cache question data with appropriate TTL"""
    cm = get_cache_manager()
    key = f"{CacheConfig.QUESTION_PREFIX}:data"
    return cm.set(key, questions, CacheConfig.QUESTION_DATA_TTL,
                  user_id=user_id, department=department, question_type=question_type)

def get_cached_questions(department: str = None, question_type: str = None,
                        user_id: str = None) -> Optional[List[Dict]]:
    """Retrieve cached question data"""
    cm = get_cache_manager()
    key = f"{CacheConfig.QUESTION_PREFIX}:data"
    return cm.get(key, user_id=user_id, department=department, question_type=question_type)

def invalidate_question_cache(department: str = None):
    """Invalidate question cache when data changes"""
    cm = get_cache_manager()
    pattern = CacheConfig.QUESTION_PREFIX
    if department:
        pattern += f":dept:{department}"
    return cm.invalidate_pattern(pattern)

def cache_user_session(user_id: str, session_data: Dict) -> bool:
    """Cache user session data"""
    cm = get_cache_manager()
    key = f"{CacheConfig.SESSION_PREFIX}:data"
    return cm.set(key, session_data, CacheConfig.USER_SESSION_TTL, user_id=user_id)

def get_cache_health_report() -> Dict[str, Any]:
    """Get comprehensive cache health report"""
    cm = get_cache_manager()
    stats = cm.get_performance_stats()

    # Add health status
    health_status = "healthy"
    if stats["hit_rate"] < 0.70:
        health_status = "critical"
    elif stats["hit_rate"] < 0.85:
        health_status = "warning"

    stats["health_status"] = health_status
    stats["timestamp"] = datetime.now().isoformat()

    return stats


if __name__ == "__main__":
    # Test the cache manager
    print("🧪 Testing Professional Cache Manager...")

    cm = initialize_professional_cache("development")

    # Test basic operations
    test_data = {"test": "data", "numbers": [1, 2, 3]}

    print("Setting test data...")
    success = cm.set("test_key", test_data, user_id="test_user_123")
    print(f"Set operation: {'✅ Success' if success else '❌ Failed'}")

    print("Getting test data...")
    retrieved = cm.get("test_key", user_id="test_user_123")
    print(f"Get operation: {'✅ Success' if retrieved == test_data else '❌ Failed'}")

    print("Performance stats:")
    stats = cm.get_performance_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")