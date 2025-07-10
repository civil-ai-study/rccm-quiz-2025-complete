#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
【ULTRATHIN区 Phase 1】ヘルスチェックBlueprint
システム状態監視・診断機能
既存システム完全非干渉・読み取り専用
"""

from flask import Blueprint, jsonify, request
import os
import sys
import psutil
import time
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# ヘルスチェック専用Blueprint定義
health_bp = Blueprint(
    'health_check',
    __name__,
    url_prefix='/health'
)

@health_bp.route('/simple')
def health_simple():
    """シンプルヘルスチェック（最軽量）"""
    try:
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'service': 'rccm-quiz-app'
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@health_bp.route('/')
@health_bp.route('/status')
def health_status():
    """詳細ヘルスチェック"""
    try:
        start_time = time.time()
        
        # システム情報収集
        memory_info = psutil.virtual_memory()
        disk_info = psutil.disk_usage('/')
        cpu_percent = psutil.cpu_percent(interval=0.1)
        
        # プロセス情報
        current_process = psutil.Process()
        process_memory = current_process.memory_info()
        
        # ファイルシステムチェック
        data_dir_exists = os.path.exists('data')
        templates_dir_exists = os.path.exists('templates')
        
        # 応答時間計算
        response_time_ms = (time.time() - start_time) * 1000
        
        health_data = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'service': 'rccm-quiz-app',
            'version': '2.0-ULTRATHIN',
            'python_version': sys.version,
            'uptime_seconds': time.time() - psutil.boot_time(),
            'response_time_ms': round(response_time_ms, 2),
            
            'system': {
                'cpu_percent': cpu_percent,
                'memory': {
                    'total_gb': round(memory_info.total / (1024**3), 2),
                    'available_gb': round(memory_info.available / (1024**3), 2),
                    'percent_used': memory_info.percent
                },
                'disk': {
                    'total_gb': round(disk_info.total / (1024**3), 2),
                    'free_gb': round(disk_info.free / (1024**3), 2),
                    'percent_used': round(((disk_info.total - disk_info.free) / disk_info.total) * 100, 1)
                }
            },
            
            'process': {
                'pid': current_process.pid,
                'memory_mb': round(process_memory.rss / (1024**2), 2),
                'cpu_percent': current_process.cpu_percent(),
                'num_threads': current_process.num_threads(),
                'open_files': len(current_process.open_files()) if hasattr(current_process, 'open_files') else 0
            },
            
            'filesystem': {
                'data_dir_exists': data_dir_exists,
                'templates_dir_exists': templates_dir_exists,
                'current_working_directory': os.getcwd(),
                'app_file_exists': os.path.exists('app.py')
            }
        }
        
        # ヘルス判定
        warnings = []
        if cpu_percent > 80:
            warnings.append('High CPU usage')
        if memory_info.percent > 85:
            warnings.append('High memory usage')
        if disk_info.free < (1024**3):  # 1GB未満
            warnings.append('Low disk space')
        if response_time_ms > 1000:
            warnings.append('Slow response time')
            
        if warnings:
            health_data['status'] = 'degraded'
            health_data['warnings'] = warnings
            
        return jsonify(health_data)
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat(),
            'service': 'rccm-quiz-app'
        }), 500

@health_bp.route('/check')
def health_check():
    """Kubernetes/Docker対応ヘルスチェック"""
    try:
        # 基本的な生存確認
        checks = {
            'app_file': os.path.exists('app.py'),
            'data_directory': os.path.exists('data'),
            'memory_ok': psutil.virtual_memory().percent < 90,
            'disk_ok': psutil.disk_usage('/').free > (500 * 1024 * 1024),  # 500MB以上
        }
        
        # すべてのチェックが成功した場合のみhealthy
        all_healthy = all(checks.values())
        
        result = {
            'status': 'healthy' if all_healthy else 'unhealthy',
            'timestamp': datetime.now().isoformat(),
            'checks': checks
        }
        
        if not all_healthy:
            failed_checks = [check for check, status in checks.items() if not status]
            result['failed_checks'] = failed_checks
            
        return jsonify(result), 200 if all_healthy else 503
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 503

@health_bp.route('/ready')
def readiness_check():
    """Readiness Probe（K8s対応）"""
    try:
        # アプリケーションが実際のリクエストを処理する準備ができているかチェック
        ready_checks = {
            'data_files_accessible': os.path.exists('data/4-1.csv'),
            'templates_accessible': os.path.exists('templates'),
            'memory_sufficient': psutil.virtual_memory().percent < 85,
            'disk_sufficient': psutil.disk_usage('/').free > (1024 * 1024 * 1024),  # 1GB以上
        }
        
        # オプション: 実際のデータ読み込みテスト
        try:
            with open('data/4-1.csv', 'r', encoding='utf-8', errors='ignore') as f:
                first_line = f.readline()
                ready_checks['data_readable'] = bool(first_line.strip())
        except:
            ready_checks['data_readable'] = False
        
        all_ready = all(ready_checks.values())
        
        result = {
            'ready': all_ready,
            'timestamp': datetime.now().isoformat(),
            'checks': ready_checks
        }
        
        if not all_ready:
            failed_checks = [check for check, status in ready_checks.items() if not status]
            result['failed_checks'] = failed_checks
            
        return jsonify(result), 200 if all_ready else 503
        
    except Exception as e:
        logger.error(f"Readiness check error: {e}")
        return jsonify({
            'ready': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 503

@health_bp.route('/live')
def liveness_check():
    """Liveness Probe（K8s対応）"""
    try:
        # プロセスが生きているかの最小限チェック
        current_time = time.time()
        
        # 基本的な計算テスト
        test_calculation = sum(range(100))
        expected_result = 4950
        
        if test_calculation != expected_result:
            raise Exception("Basic calculation test failed")
        
        return jsonify({
            'alive': True,
            'timestamp': datetime.now().isoformat(),
            'process_time': current_time,
            'test_passed': True
        })
        
    except Exception as e:
        logger.error(f"Liveness check error: {e}")
        return jsonify({
            'alive': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# Blueprint情報取得
def get_health_blueprint_info():
    """ヘルスチェックBlueprint情報"""
    return {
        'name': 'health_check',
        'url_prefix': '/health',
        'routes': [
            {'path': '/health/simple', 'endpoint': 'health_simple', 'methods': ['GET']},
            {'path': '/health/', 'endpoint': 'health_status', 'methods': ['GET']},
            {'path': '/health/status', 'endpoint': 'health_status', 'methods': ['GET']},
            {'path': '/health/check', 'endpoint': 'health_check', 'methods': ['GET']},
            {'path': '/health/ready', 'endpoint': 'readiness_check', 'methods': ['GET']},
            {'path': '/health/live', 'endpoint': 'liveness_check', 'methods': ['GET']}
        ],
        'description': 'システム監視・診断機能（K8s対応）',
        'risk_level': 'zero',
        'dependencies': 'psutil',
        'implementation_date': '2025-07-10',
        'phase': 'ULTRATHIN Phase 1'
    }

if __name__ == "__main__":
    print("【ULTRATHIN区 Phase 1】ヘルスチェックBlueprint実装完了")
    print(f"ルート数: 6個")
    print(f"機能: システム監視・K8s対応・診断")
    print(f"リスクレベル: ゼロ（読み取り専用）")