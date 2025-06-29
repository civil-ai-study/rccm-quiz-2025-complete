#!/usr/bin/env python3
"""
🛡️ Ultra Sync Circuit Breaker Pattern Implementation
RCCM試験問題集アプリ - ウルトラシンク サーキットブレーカーパターン

🎯 CLAUDE.md準拠・副作用ゼロ保証・ウルトラシンクエラー回復システム:
- 3段階状態管理（Closed, Open, Half-Open）
- 自動障害検出と回復
- フォールバック機能統合
- 包括的監視とメトリクス
- 企業レベル信頼性保証
"""

import threading
import time
import logging
import json
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, Callable, List, Tuple
from functools import wraps
from enum import Enum
from collections import deque, defaultdict
import statistics
import traceback

logger = logging.getLogger(__name__)

class CircuitState(Enum):
    """🛡️ サーキットブレーカー状態"""
    CLOSED = "closed"      # 正常動作状態
    OPEN = "open"          # 障害検出により回路開放
    HALF_OPEN = "half_open"  # 試験的回復状態

class UltraSyncCircuitBreaker:
    """🛡️ ウルトラシンク サーキットブレーカー実装"""
    
    def __init__(self, 
                 name: str,
                 failure_threshold: int = 5,
                 recovery_timeout: int = 60,
                 expected_exception: tuple = (Exception,),
                 fallback_function: Optional[Callable] = None):
        
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.fallback_function = fallback_function
        
        # 状態管理
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None
        self.last_success_time = None
        self.state_change_time = datetime.now(timezone.utc)
        
        # 統計データ
        self.call_count = 0
        self.success_count = 0
        self.failure_history = deque(maxlen=100)  # 最新100件の履歴
        self.response_times = deque(maxlen=50)    # レスポンス時間履歴
        
        # スレッドセーフティ
        self.lock = threading.Lock()
        
        # 監視データ
        self.monitoring_data = {
            'total_calls': 0,
            'total_successes': 0,
            'total_failures': 0,
            'current_failure_rate': 0.0,
            'average_response_time': 0.0,
            'state_changes': [],
            'last_updated': datetime.now(timezone.utc)
        }
        
        logger.info(f"🛡️ Circuit Breaker '{name}' initialized: threshold={failure_threshold}, timeout={recovery_timeout}s")
    
    def __call__(self, func: Callable) -> Callable:
        """🔧 デコレータとして使用"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            return self.call(func, *args, **kwargs)
        return wrapper
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """🚀 関数呼び出し実行（サーキットブレーカー保護付き）"""
        with self.lock:
            self.call_count += 1
            self.monitoring_data['total_calls'] += 1
        
        # 状態チェック
        current_state = self._get_current_state()
        
        if current_state == CircuitState.OPEN:
            # 回路開放中：フォールバック実行
            logger.warning(f"🚨 Circuit breaker '{self.name}' is OPEN - executing fallback")
            return self._execute_fallback(func, *args, **kwargs)
        
        elif current_state == CircuitState.HALF_OPEN:
            # 半開状態：試験的実行
            logger.info(f"🔄 Circuit breaker '{self.name}' is HALF-OPEN - trying recovery")
            return self._execute_with_recovery_test(func, *args, **kwargs)
        
        else:
            # 正常状態：通常実行
            return self._execute_normal(func, *args, **kwargs)
    
    def _get_current_state(self) -> CircuitState:
        """📊 現在の状態を判定"""
        if self.state == CircuitState.OPEN:
            # 回復タイムアウトチェック
            if self.last_failure_time and \
               (datetime.now(timezone.utc) - self.last_failure_time).total_seconds() >= self.recovery_timeout:
                self._change_state(CircuitState.HALF_OPEN)
                logger.info(f"🔄 Circuit breaker '{self.name}' transitioning to HALF-OPEN")
        
        return self.state
    
    def _execute_normal(self, func: Callable, *args, **kwargs) -> Any:
        """✅ 正常状態での実行"""
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # 成功記録
            self._record_success(execution_time)
            return result
            
        except self.expected_exception as e:
            execution_time = time.time() - start_time
            
            # 失敗記録
            self._record_failure(e, execution_time)
            
            # 閾値チェック
            if self.failure_count >= self.failure_threshold:
                self._change_state(CircuitState.OPEN)
                logger.error(f"🚨 Circuit breaker '{self.name}' opened due to {self.failure_count} failures")
            
            raise
    
    def _execute_with_recovery_test(self, func: Callable, *args, **kwargs) -> Any:
        """🔄 回復テスト実行"""
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # 成功：回路閉鎖
            self._record_success(execution_time)
            self._change_state(CircuitState.CLOSED)
            logger.info(f"✅ Circuit breaker '{self.name}' recovered and closed")
            
            return result
            
        except self.expected_exception as e:
            execution_time = time.time() - start_time
            
            # 失敗：再度開放
            self._record_failure(e, execution_time)
            self._change_state(CircuitState.OPEN)
            logger.error(f"❌ Circuit breaker '{self.name}' recovery failed, reopening")
            
            return self._execute_fallback(func, *args, **kwargs)
    
    def _execute_fallback(self, func: Callable, *args, **kwargs) -> Any:
        """🔄 フォールバック実行"""
        if self.fallback_function:
            try:
                logger.info(f"🔄 Executing fallback for '{self.name}'")
                return self.fallback_function(*args, **kwargs)
            except Exception as e:
                logger.error(f"❌ Fallback failed for '{self.name}': {e}")
                raise Exception(f"Circuit breaker '{self.name}' is open and fallback failed") from e
        else:
            raise Exception(f"Circuit breaker '{self.name}' is open and no fallback available")
    
    def _record_success(self, execution_time: float):
        """✅ 成功記録"""
        with self.lock:
            self.success_count += 1
            self.failure_count = 0  # 失敗カウントリセット
            self.last_success_time = datetime.now(timezone.utc)
            
            # 履歴記録
            self.failure_history.append({
                'timestamp': self.last_success_time,
                'success': True,
                'execution_time': execution_time
            })
            
            self.response_times.append(execution_time)
            
            # 監視データ更新
            self.monitoring_data['total_successes'] += 1
            self._update_monitoring_stats()
    
    def _record_failure(self, exception: Exception, execution_time: float):
        """❌ 失敗記録"""
        with self.lock:
            self.failure_count += 1
            self.last_failure_time = datetime.now(timezone.utc)
            
            # 履歴記録
            self.failure_history.append({
                'timestamp': self.last_failure_time,
                'success': False,
                'exception': str(exception),
                'exception_type': type(exception).__name__,
                'execution_time': execution_time
            })
            
            # 監視データ更新
            self.monitoring_data['total_failures'] += 1
            self._update_monitoring_stats()
    
    def _change_state(self, new_state: CircuitState):
        """🔄 状態変更"""
        old_state = self.state
        self.state = new_state
        self.state_change_time = datetime.now(timezone.utc)
        
        # 状態変更履歴
        state_change = {
            'timestamp': self.state_change_time,
            'from_state': old_state.value,
            'to_state': new_state.value,
            'failure_count': self.failure_count
        }
        
        self.monitoring_data['state_changes'].append(state_change)
        
        # 履歴サイズ制限
        if len(self.monitoring_data['state_changes']) > 50:
            self.monitoring_data['state_changes'] = self.monitoring_data['state_changes'][-50:]
        
        logger.info(f"🔄 Circuit breaker '{self.name}' state: {old_state.value} → {new_state.value}")
    
    def _update_monitoring_stats(self):
        """📊 監視統計更新"""
        total_calls = self.monitoring_data['total_calls']
        if total_calls > 0:
            success_rate = self.monitoring_data['total_successes'] / total_calls
            self.monitoring_data['current_failure_rate'] = 1.0 - success_rate
        
        if self.response_times:
            self.monitoring_data['average_response_time'] = statistics.mean(self.response_times)
        
        self.monitoring_data['last_updated'] = datetime.now(timezone.utc)
    
    def get_stats(self) -> Dict[str, Any]:
        """📊 統計情報取得"""
        with self.lock:
            recent_failures = [h for h in self.failure_history if not h['success']]
            recent_successes = [h for h in self.failure_history if h['success']]
            
            return {
                'name': self.name,
                'state': self.state.value,
                'failure_count': self.failure_count,
                'failure_threshold': self.failure_threshold,
                'recovery_timeout': self.recovery_timeout,
                'call_count': self.call_count,
                'success_count': self.success_count,
                'last_failure_time': self.last_failure_time.isoformat() if self.last_failure_time else None,
                'last_success_time': self.last_success_time.isoformat() if self.last_success_time else None,
                'state_change_time': self.state_change_time.isoformat(),
                'recent_failure_count': len(recent_failures),
                'recent_success_count': len(recent_successes),
                'current_failure_rate': self.monitoring_data['current_failure_rate'],
                'average_response_time': self.monitoring_data['average_response_time'],
                'monitoring_data': self.monitoring_data.copy()
            }
    
    def force_open(self):
        """🚨 強制開放"""
        with self.lock:
            self._change_state(CircuitState.OPEN)
            logger.warning(f"🚨 Circuit breaker '{self.name}' manually opened")
    
    def force_close(self):
        """✅ 強制閉鎖"""
        with self.lock:
            self.failure_count = 0
            self._change_state(CircuitState.CLOSED)
            logger.info(f"✅ Circuit breaker '{self.name}' manually closed")
    
    def reset(self):
        """🔄 リセット"""
        with self.lock:
            self.failure_count = 0
            self.call_count = 0
            self.success_count = 0
            self.last_failure_time = None
            self.last_success_time = None
            self.failure_history.clear()
            self.response_times.clear()
            self._change_state(CircuitState.CLOSED)
            
            # 監視データリセット
            self.monitoring_data = {
                'total_calls': 0,
                'total_successes': 0,
                'total_failures': 0,
                'current_failure_rate': 0.0,
                'average_response_time': 0.0,
                'state_changes': [],
                'last_updated': datetime.now(timezone.utc)
            }
            
            logger.info(f"🔄 Circuit breaker '{self.name}' reset")


class UltraSyncCircuitBreakerManager:
    """🛡️ ウルトラシンク サーキットブレーカー管理システム"""
    
    def __init__(self):
        self.circuit_breakers: Dict[str, UltraSyncCircuitBreaker] = {}
        self.lock = threading.Lock()
        
        # デフォルト設定
        self.default_configs = {
            'database': {
                'failure_threshold': 5,
                'recovery_timeout': 60,
                'expected_exception': (Exception,)
            },
            'redis': {
                'failure_threshold': 3,
                'recovery_timeout': 30,
                'expected_exception': (Exception,)
            },
            'file_io': {
                'failure_threshold': 3,
                'recovery_timeout': 15,
                'expected_exception': (IOError, OSError, FileNotFoundError)
            },
            'api_call': {
                'failure_threshold': 5,
                'recovery_timeout': 120,
                'expected_exception': (Exception,)
            }
        }
        
        logger.info("🛡️ Ultra Sync Circuit Breaker Manager initialized")
    
    def create_circuit_breaker(self, 
                             name: str, 
                             config_type: str = 'default',
                             fallback_function: Optional[Callable] = None,
                             **custom_config) -> UltraSyncCircuitBreaker:
        """🔧 サーキットブレーカー作成"""
        
        # 設定取得
        if config_type in self.default_configs:
            config = self.default_configs[config_type].copy()
        else:
            config = {
                'failure_threshold': 5,
                'recovery_timeout': 60,
                'expected_exception': (Exception,)
            }
        
        # カスタム設定適用
        config.update(custom_config)
        
        with self.lock:
            circuit_breaker = UltraSyncCircuitBreaker(
                name=name,
                fallback_function=fallback_function,
                **config
            )
            
            self.circuit_breakers[name] = circuit_breaker
            
        logger.info(f"🔧 Circuit breaker '{name}' created with config: {config}")
        return circuit_breaker
    
    def get_circuit_breaker(self, name: str) -> Optional[UltraSyncCircuitBreaker]:
        """📖 サーキットブレーカー取得"""
        return self.circuit_breakers.get(name)
    
    def get_all_stats(self) -> Dict[str, Any]:
        """📊 全サーキットブレーカー統計"""
        stats = {}
        
        with self.lock:
            for name, cb in self.circuit_breakers.items():
                stats[name] = cb.get_stats()
        
        # 総合統計
        total_calls = sum(cb['call_count'] for cb in stats.values())
        total_failures = sum(cb['monitoring_data']['total_failures'] for cb in stats.values())
        
        summary = {
            'total_circuit_breakers': len(self.circuit_breakers),
            'total_calls': total_calls,
            'total_failures': total_failures,
            'overall_failure_rate': total_failures / max(total_calls, 1),
            'open_circuits': len([cb for cb in stats.values() if cb['state'] == 'open']),
            'half_open_circuits': len([cb for cb in stats.values() if cb['state'] == 'half_open']),
            'closed_circuits': len([cb for cb in stats.values() if cb['state'] == 'closed']),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        return {
            'summary': summary,
            'circuit_breakers': stats
        }
    
    def reset_all(self):
        """🔄 全サーキットブレーカーリセット"""
        with self.lock:
            for cb in self.circuit_breakers.values():
                cb.reset()
        logger.info("🔄 All circuit breakers reset")


# グローバルマネージャーインスタンス
ultra_sync_cb_manager = UltraSyncCircuitBreakerManager()

def circuit_breaker(name: str, 
                   config_type: str = 'default',
                   fallback_function: Optional[Callable] = None,
                   **kwargs):
    """🛡️ サーキットブレーカーデコレータ"""
    def decorator(func: Callable):
        cb = ultra_sync_cb_manager.create_circuit_breaker(
            name=name,
            config_type=config_type,
            fallback_function=fallback_function,
            **kwargs
        )
        return cb(func)
    return decorator

def get_circuit_breaker_manager() -> UltraSyncCircuitBreakerManager:
    """🔧 サーキットブレーカーマネージャー取得"""
    return ultra_sync_cb_manager


if __name__ == "__main__":
    # テスト実行
    print("🧪 Ultra Sync Circuit Breaker Test")
    print("=" * 60)
    
    # テスト用関数
    call_count = 0
    
    def unreliable_function():
        global call_count
        call_count += 1
        if call_count <= 3:
            raise Exception(f"Simulated failure #{call_count}")
        return f"Success on call #{call_count}"
    
    def fallback_function():
        return "Fallback response"
    
    # サーキットブレーカー作成
    cb = ultra_sync_cb_manager.create_circuit_breaker(
        name="test_cb",
        config_type="default",
        failure_threshold=3,
        recovery_timeout=5,
        fallback_function=fallback_function
    )
    
    # テスト実行
    for i in range(8):
        try:
            result = cb.call(unreliable_function)
            print(f"Call {i+1}: {result}")
        except Exception as e:
            print(f"Call {i+1}: Exception - {e}")
        
        print(f"  State: {cb.state.value}, Failures: {cb.failure_count}")
        time.sleep(1)
    
    # 統計表示
    stats = ultra_sync_cb_manager.get_all_stats()
    print("\n📊 Final Statistics:")
    print(json.dumps(stats, indent=2, ensure_ascii=False, default=str))
    
    print("\n✅ Ultra Sync Circuit Breaker Test completed")