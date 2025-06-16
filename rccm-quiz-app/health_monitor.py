#!/usr/bin/env python3
"""
🚀 RCCM試験アプリ - エンタープライズ級ヘルスモニタリング
24/7 監視・自動復旧・アラートシステム
"""

import time
import requests
import smtplib
import subprocess
import json
import logging
from datetime import datetime
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/supervisor/health_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class RCCMHealthMonitor:
    def __init__(self):
        self.endpoints = [
            'http://localhost:8000/health',
            'http://localhost:8000/',
            'http://localhost:8001/health'  # バックアップ
        ]
        self.failure_count = {}
        self.max_failures = 3
        self.check_interval = 30  # 30秒間隔
        self.alert_sent = {}
        
    def check_endpoint(self, url):
        """エンドポイントヘルスチェック"""
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return True, None
            else:
                return False, f"HTTP {response.status_code}"
        except Exception as e:
            return False, str(e)
    
    def restart_service(self, service_name):
        """サービス自動再起動"""
        try:
            subprocess.run(['supervisorctl', 'restart', service_name], check=True)
            logger.info(f"✅ サービス {service_name} を自動再起動しました")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ サービス {service_name} の再起動に失敗: {e}")
            return False
    
    def send_alert(self, message):
        """アラート送信（メール・Slack等）"""
        logger.critical(f"🚨 CRITICAL ALERT: {message}")
        
        # 緊急時対応：バックアップサーバー自動起動
        if "rccm-app" in message.lower():
            logger.info("🔄 緊急バックアップサーバー起動中...")
            subprocess.run(['supervisorctl', 'start', 'rccm-app-backup'])
    
    def get_system_stats(self):
        """システム統計情報取得"""
        try:
            # CPU使用率
            cpu_result = subprocess.run(['top', '-bn1'], capture_output=True, text=True)
            
            # メモリ使用率
            mem_result = subprocess.run(['free', '-m'], capture_output=True, text=True)
            
            # ディスク使用率
            disk_result = subprocess.run(['df', '-h'], capture_output=True, text=True)
            
            return {
                'timestamp': datetime.now().isoformat(),
                'cpu': cpu_result.stdout.split('\n')[2] if cpu_result.returncode == 0 else 'N/A',
                'memory': mem_result.stdout.split('\n')[1] if mem_result.returncode == 0 else 'N/A',
                'disk': disk_result.stdout.split('\n')[1] if disk_result.returncode == 0 else 'N/A'
            }
        except Exception as e:
            logger.error(f"システム統計取得エラー: {e}")
            return {}
    
    def monitor_loop(self):
        """メイン監視ループ"""
        logger.info("🚀 RCCM ヘルスモニター開始 - 24/7監視体制")
        
        while True:
            try:
                all_healthy = True
                
                for endpoint in self.endpoints:
                    is_healthy, error = self.check_endpoint(endpoint)
                    
                    if not is_healthy:
                        all_healthy = False
                        self.failure_count[endpoint] = self.failure_count.get(endpoint, 0) + 1
                        
                        logger.warning(f"⚠️  エンドポイント異常: {endpoint} - {error} (失敗回数: {self.failure_count[endpoint]})")
                        
                        # 失敗回数が閾値を超えた場合
                        if self.failure_count[endpoint] >= self.max_failures:
                            alert_key = f"{endpoint}_{datetime.now().strftime('%Y%m%d%H')}"
                            
                            if alert_key not in self.alert_sent:
                                self.send_alert(f"エンドポイント {endpoint} が {self.max_failures} 回連続で失敗")
                                self.alert_sent[alert_key] = True
                                
                                # メインサービス再起動試行
                                if '8000' in endpoint:
                                    self.restart_service('rccm-app')
                    else:
                        # 成功時は失敗カウントリセット
                        if endpoint in self.failure_count:
                            del self.failure_count[endpoint]
                
                if all_healthy:
                    logger.info("✅ 全エンドポイント正常")
                
                # システム統計ログ出力（1時間に1回）
                if int(time.time()) % 3600 == 0:
                    stats = self.get_system_stats()
                    logger.info(f"📊 システム統計: {json.dumps(stats, indent=2)}")
                
                time.sleep(self.check_interval)
                
            except KeyboardInterrupt:
                logger.info("🛑 ヘルスモニター停止")
                break
            except Exception as e:
                logger.error(f"❌ 監視ループエラー: {e}")
                time.sleep(60)  # エラー時は1分待機

if __name__ == "__main__":
    monitor = RCCMHealthMonitor()
    monitor.monitor_loop()