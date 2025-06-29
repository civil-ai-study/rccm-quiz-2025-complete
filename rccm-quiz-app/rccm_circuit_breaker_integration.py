#!/usr/bin/env python3
"""
🛡️ RCCM App Circuit Breaker Integration
RCCM試験問題集アプリ - ウルトラシンク サーキットブレーカー統合

🎯 主要統合ポイント:
- データベース接続保護
- Redis セッション保護
- ファイルIO 保護
- CSV データロード保護
- 包括的エラー回復
"""

import logging
import json
import csv
import os
import time
from typing import Dict, Any, List, Optional
from functools import wraps
from datetime import datetime, timezone

from ultra_sync_circuit_breaker import (
    circuit_breaker, 
    get_circuit_breaker_manager,
    UltraSyncCircuitBreaker
)

logger = logging.getLogger(__name__)

class RCCMCircuitBreakerIntegration:
    """🛡️ RCCM アプリケーション サーキットブレーカー統合"""
    
    def __init__(self):
        self.cb_manager = get_circuit_breaker_manager()
        
        # RCCM専用フォールバック関数
        self.fallback_functions = {
            'csv_data_load': self._fallback_csv_data,
            'session_management': self._fallback_session_data,
            'file_operations': self._fallback_file_operations,
            'redis_operations': self._fallback_redis_operations
        }
        
        # 統合統計
        self.integration_stats = {
            'total_protected_calls': 0,
            'total_fallback_executions': 0,
            'protected_operations': {},
            'last_updated': datetime.now(timezone.utc)
        }
        
        self._initialize_circuit_breakers()
        logger.info("🛡️ RCCM Circuit Breaker Integration initialized")
    
    def _initialize_circuit_breakers(self):
        """🔧 RCCM専用サーキットブレーカー初期化"""
        
        # CSV データロード保護
        self.csv_load_cb = self.cb_manager.create_circuit_breaker(
            name="csv_data_load",
            config_type="file_io",
            failure_threshold=3,
            recovery_timeout=30,
            fallback_function=self.fallback_functions['csv_data_load']
        )
        
        # セッション管理保護
        self.session_cb = self.cb_manager.create_circuit_breaker(
            name="session_management",
            config_type="redis",
            failure_threshold=3,
            recovery_timeout=15,
            fallback_function=self.fallback_functions['session_management']
        )
        
        # ファイル操作保護
        self.file_ops_cb = self.cb_manager.create_circuit_breaker(
            name="file_operations",
            config_type="file_io",
            failure_threshold=3,
            recovery_timeout=20,
            fallback_function=self.fallback_functions['file_operations']
        )
        
        # Redis操作保護
        self.redis_cb = self.cb_manager.create_circuit_breaker(
            name="redis_operations",
            config_type="redis",
            failure_threshold=2,
            recovery_timeout=10,
            fallback_function=self.fallback_functions['redis_operations']
        )
        
        logger.info("🔧 RCCM circuit breakers initialized")
    
    # 🔧 フォールバック関数群
    
    def _fallback_csv_data(self, *args, **kwargs) -> List[Dict[str, Any]]:
        """📄 CSV データロード フォールバック"""
        logger.warning("🔄 CSV data load fallback activated")
        
        # 最小限のダミーデータ返却
        return [
            {
                'id': '1',
                'category': 'エラー回復',
                'year': '2024',
                'question': 'システムでエラーが発生しました。サーキットブレーカーが作動中です。',
                'choice_a': 'しばらくお待ちください',
                'choice_b': 'ページを再読み込みしてください',
                'choice_c': 'システム管理者にお問い合わせください',
                'choice_d': '後ほど再度お試しください',
                'correct': 'a',
                'explanation': 'サーキットブレーカーが自動回復を試行中です',
                'source': 'システム管理',
                'difficulty': 'システム'
            }
        ]
    
    def _fallback_session_data(self, *args, **kwargs) -> Dict[str, Any]:
        """👤 セッション管理 フォールバック"""
        logger.warning("🔄 Session management fallback activated")
        
        return {
            'user_name': '一時ユーザー',
            'session_id': f'fallback_{int(time.time())}',
            'quiz_current': 0,
            'quiz_question_ids': [],
            'history': [],
            'fallback_mode': True,
            'message': 'セッション管理システムが一時的に利用できません'
        }
    
    def _fallback_file_operations(self, *args, **kwargs) -> Any:
        """📁 ファイル操作 フォールバック"""
        logger.warning("🔄 File operations fallback activated")
        
        # 操作の種類を推定
        if len(args) > 0 and isinstance(args[0], str):
            if args[0].endswith('.json'):
                return {'error': 'ファイルアクセスエラー', 'fallback': True}
            elif args[0].endswith('.csv'):
                return []
        
        return {'status': 'fallback', 'message': 'ファイル操作が一時的に利用できません'}
    
    def _fallback_redis_operations(self, *args, **kwargs) -> Any:
        """🔧 Redis操作 フォールバック"""
        logger.warning("🔄 Redis operations fallback activated")
        
        return {
            'redis_available': False,
            'fallback_mode': True,
            'message': 'Redis接続が一時的に利用できません。ファイルベースモードで動作中。'
        }
    
    # 🛡️ 保護されたRCCM操作メソッド群
    
    def protected_csv_load(self, file_path: str, encoding: str = 'shift_jis') -> List[Dict[str, Any]]:
        """📄 保護されたCSVデータロード"""
        
        def _load_csv_data():
            questions = []
            with open(file_path, 'r', encoding=encoding) as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row) >= 11:  # 最小限のフィールド数チェック
                        questions.append({
                            'id': row[0],
                            'category': row[1],
                            'year': row[2],
                            'question': row[3],
                            'choice_a': row[4],
                            'choice_b': row[5],
                            'choice_c': row[6],
                            'choice_d': row[7],
                            'correct': row[8],
                            'explanation': row[9],
                            'source': row[10] if len(row) > 10 else '',
                            'difficulty': row[11] if len(row) > 11 else 'standard'
                        })
            return questions
        
        self.integration_stats['total_protected_calls'] += 1
        self.integration_stats['protected_operations']['csv_load'] = \
            self.integration_stats['protected_operations'].get('csv_load', 0) + 1
        
        return self.csv_load_cb.call(_load_csv_data)
    
    def protected_session_save(self, session_id: str, session_data: Dict[str, Any]) -> bool:
        """👤 保護されたセッション保存"""
        
        def _save_session():
            # セッションファイル保存
            os.makedirs('user_data', exist_ok=True)
            session_file = f'user_data/{session_id}_session.json'
            
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2, default=str)
            
            return True
        
        self.integration_stats['total_protected_calls'] += 1
        self.integration_stats['protected_operations']['session_save'] = \
            self.integration_stats['protected_operations'].get('session_save', 0) + 1
        
        return self.session_cb.call(_save_session)
    
    def protected_session_load(self, session_id: str) -> Optional[Dict[str, Any]]:
        """👤 保護されたセッション読み込み"""
        
        def _load_session():
            session_file = f'user_data/{session_id}_session.json'
            
            if not os.path.exists(session_file):
                return None
            
            with open(session_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        self.integration_stats['total_protected_calls'] += 1
        self.integration_stats['protected_operations']['session_load'] = \
            self.integration_stats['protected_operations'].get('session_load', 0) + 1
        
        return self.session_cb.call(_load_session)
    
    def protected_file_write(self, file_path: str, data: Any, encoding: str = 'utf-8') -> bool:
        """📁 保護されたファイル書き込み"""
        
        def _write_file():
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            if isinstance(data, (dict, list)):
                with open(file_path, 'w', encoding=encoding) as f:
                    json.dump(data, f, ensure_ascii=False, indent=2, default=str)
            else:
                with open(file_path, 'w', encoding=encoding) as f:
                    f.write(str(data))
            
            return True
        
        self.integration_stats['total_protected_calls'] += 1
        self.integration_stats['protected_operations']['file_write'] = \
            self.integration_stats['protected_operations'].get('file_write', 0) + 1
        
        return self.file_ops_cb.call(_write_file)
    
    def protected_redis_operation(self, operation_func, *args, **kwargs) -> Any:
        """🔧 保護されたRedis操作"""
        
        self.integration_stats['total_protected_calls'] += 1
        self.integration_stats['protected_operations']['redis_ops'] = \
            self.integration_stats['protected_operations'].get('redis_ops', 0) + 1
        
        return self.redis_cb.call(operation_func, *args, **kwargs)
    
    # 📊 統計・監視メソッド
    
    def get_integration_stats(self) -> Dict[str, Any]:
        """📊 統合統計取得"""
        cb_stats = self.cb_manager.get_all_stats()
        
        # フォールバック実行回数計算
        total_fallbacks = 0
        for cb_name, cb_data in cb_stats['circuit_breakers'].items():
            if cb_name in ['csv_data_load', 'session_management', 'file_operations', 'redis_operations']:
                # 開放状態の呼び出し数がフォールバック実行数
                if cb_data['state'] == 'open':
                    total_fallbacks += cb_data['call_count'] - cb_data['success_count']
        
        self.integration_stats['total_fallback_executions'] = total_fallbacks
        self.integration_stats['last_updated'] = datetime.now(timezone.utc)
        
        return {
            'integration_stats': self.integration_stats,
            'circuit_breaker_stats': cb_stats,
            'rccm_specific_metrics': {
                'csv_load_protection': cb_stats['circuit_breakers'].get('csv_data_load', {}),
                'session_protection': cb_stats['circuit_breakers'].get('session_management', {}),
                'file_ops_protection': cb_stats['circuit_breakers'].get('file_operations', {}),
                'redis_protection': cb_stats['circuit_breakers'].get('redis_operations', {})
            }
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """🏥 システム健全性ステータス"""
        stats = self.get_integration_stats()
        cb_stats = stats['circuit_breaker_stats']
        
        # 健全性判定
        open_circuits = cb_stats['summary']['open_circuits']
        total_circuits = cb_stats['summary']['total_circuit_breakers']
        failure_rate = cb_stats['summary']['overall_failure_rate']
        
        if open_circuits == 0 and failure_rate < 0.1:
            health_status = "healthy"
            health_score = 100
        elif open_circuits <= 1 and failure_rate < 0.3:
            health_status = "degraded"
            health_score = 70
        elif open_circuits <= 2 and failure_rate < 0.5:
            health_status = "warning"
            health_score = 40
        else:
            health_status = "critical"
            health_score = 10
        
        return {
            'health_status': health_status,
            'health_score': health_score,
            'open_circuits': open_circuits,
            'total_circuits': total_circuits,
            'overall_failure_rate': failure_rate,
            'recommendations': self._get_health_recommendations(health_status, cb_stats),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
    
    def _get_health_recommendations(self, health_status: str, cb_stats: Dict[str, Any]) -> List[str]:
        """💡 健全性改善推奨事項"""
        recommendations = []
        
        if health_status == "critical":
            recommendations.extend([
                "🚨 複数のサーキットブレーカーが開放状態です",
                "🔧 システム管理者による緊急対応が必要です",
                "📞 技術サポートにお問い合わせください"
            ])
        elif health_status == "warning":
            recommendations.extend([
                "⚠️ 一部のサービスが不安定です",
                "🔄 システムの再起動を検討してください",
                "📊 ログを確認して根本原因を調査してください"
            ])
        elif health_status == "degraded":
            recommendations.extend([
                "🔍 システム監視を強化してください",
                "⏰ 定期的なヘルスチェックを実行してください"
            ])
        else:
            recommendations.append("✅ システムは正常に動作しています")
        
        return recommendations
    
    def reset_all_circuit_breakers(self):
        """🔄 全サーキットブレーカーリセット"""
        self.cb_manager.reset_all()
        self.integration_stats = {
            'total_protected_calls': 0,
            'total_fallback_executions': 0,
            'protected_operations': {},
            'last_updated': datetime.now(timezone.utc)
        }
        logger.info("🔄 All RCCM circuit breakers reset")


# グローバルインスタンス
rccm_circuit_breaker_integration = None

def init_rccm_circuit_breakers() -> RCCMCircuitBreakerIntegration:
    """🚀 RCCM サーキットブレーカー統合初期化"""
    global rccm_circuit_breaker_integration
    
    if rccm_circuit_breaker_integration is None:
        rccm_circuit_breaker_integration = RCCMCircuitBreakerIntegration()
    
    return rccm_circuit_breaker_integration

def get_rccm_circuit_breakers() -> Optional[RCCMCircuitBreakerIntegration]:
    """🔧 RCCM サーキットブレーカー統合取得"""
    return rccm_circuit_breaker_integration

# 🛡️ 便利なデコレータ関数群

def rccm_protected_csv_load(func):
    """📄 CSV ロード保護デコレータ"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        integration = get_rccm_circuit_breakers()
        if integration:
            return integration.csv_load_cb.call(func, *args, **kwargs)
        return func(*args, **kwargs)
    return wrapper

def rccm_protected_session(func):
    """👤 セッション操作保護デコレータ"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        integration = get_rccm_circuit_breakers()
        if integration:
            return integration.session_cb.call(func, *args, **kwargs)
        return func(*args, **kwargs)
    return wrapper

def rccm_protected_file_ops(func):
    """📁 ファイル操作保護デコレータ"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        integration = get_rccm_circuit_breakers()
        if integration:
            return integration.file_ops_cb.call(func, *args, **kwargs)
        return func(*args, **kwargs)
    return wrapper


if __name__ == "__main__":
    # テスト実行
    print("🧪 RCCM Circuit Breaker Integration Test")
    print("=" * 60)
    
    # 統合システム初期化
    integration = init_rccm_circuit_breakers()
    
    # テスト用ダミーファイル作成
    test_csv_content = """1,テスト,2024,テスト問題,選択肢A,選択肢B,選択肢C,選択肢D,a,テスト解説,テスト出典,標準"""
    
    with open('test_data.csv', 'w', encoding='utf-8') as f:
        f.write(test_csv_content)
    
    try:
        # 保護されたCSVロードテスト
        print("📄 Testing protected CSV load...")
        questions = integration.protected_csv_load('test_data.csv', encoding='utf-8')
        print(f"✅ Loaded {len(questions)} questions")
        
        # 保護されたセッション操作テスト
        print("👤 Testing protected session operations...")
        test_session = {'user': 'test', 'timestamp': time.time()}
        save_result = integration.protected_session_save('test_session', test_session)
        print(f"✅ Session save: {save_result}")
        
        load_result = integration.protected_session_load('test_session')
        print(f"✅ Session load: {load_result is not None}")
        
        # 統計確認
        print("\n📊 Integration Statistics:")
        stats = integration.get_integration_stats()
        print(json.dumps(stats['integration_stats'], indent=2, ensure_ascii=False, default=str))
        
        # 健全性ステータス
        print("\n🏥 Health Status:")
        health = integration.get_health_status()
        print(json.dumps(health, indent=2, ensure_ascii=False, default=str))
        
    finally:
        # クリーンアップ
        if os.path.exists('test_data.csv'):
            os.remove('test_data.csv')
        if os.path.exists('user_data/test_session_session.json'):
            os.remove('user_data/test_session_session.json')
    
    print("\n✅ RCCM Circuit Breaker Integration Test completed")