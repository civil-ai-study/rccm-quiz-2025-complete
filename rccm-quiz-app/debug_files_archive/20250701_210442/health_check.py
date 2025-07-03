#!/usr/bin/env python3
"""
RCCM試験問題集 - ヘルスチェック・自動復旧システム
"""

import requests
import subprocess
import time
import logging
from datetime import datetime

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/health_check.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def check_server_health():
    """サーバーの健康状態をチェック"""
    try:
        response = requests.get('http://172.18.44.152:5003/', timeout=5)
        if response.status_code == 200:
            logger.info("✅ サーバー正常動作中")
            return True
        else:
            logger.warning(f"⚠️ サーバー応答異常: HTTP {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ サーバー接続エラー: {e}")
        return False

def restart_server():
    """サーバーを再起動"""
    logger.info("🔄 サーバー再起動を実行中...")
    try:
        # 既存プロセス停止
        subprocess.run(['pkill', '-f', 'python3.*app.py'], check=False)
        time.sleep(2)
        
        # 新しいプロセス起動
        subprocess.Popen(
            ['python3', 'app.py'],
            stdout=open('logs/app_auto_restart.log', 'w'),
            stderr=subprocess.STDOUT,
            cwd='/mnt/c/Users/z285/Desktop/rccm-quiz-app/rccm-quiz-app'
        )
        
        # 起動確認
        for i in range(30):
            time.sleep(1)
            if check_server_health():
                logger.info(f"✅ サーバー再起動成功 ({i+1}秒)")
                return True
        
        logger.error("❌ サーバー再起動失敗")
        return False
        
    except Exception as e:
        logger.error(f"❌ 再起動処理エラー: {e}")
        return False

def main():
    """メイン監視ループ"""
    logger.info("🚀 RCCM健康監視システム開始")
    
    consecutive_failures = 0
    max_failures = 3
    
    while True:
        try:
            if check_server_health():
                consecutive_failures = 0
                time.sleep(30)  # 30秒間隔でチェック
            else:
                consecutive_failures += 1
                logger.warning(f"⚠️ 連続失敗回数: {consecutive_failures}/{max_failures}")
                
                if consecutive_failures >= max_failures:
                    logger.error("❌ 最大失敗回数に到達。サーバー再起動を実行...")
                    if restart_server():
                        consecutive_failures = 0
                        logger.info("✅ 自動復旧成功")
                    else:
                        logger.error("❌ 自動復旧失敗。手動対応が必要です。")
                        time.sleep(60)  # 1分待機してから再試行
                else:
                    time.sleep(10)  # 10秒待機してから再チェック
                    
        except KeyboardInterrupt:
            logger.info("🛑 監視システム停止")
            break
        except Exception as e:
            logger.error(f"❌ 監視システムエラー: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()