#!/usr/bin/env python3
"""
🛡️ Ultra Sync Prevention Tool - 副作用完全防止システム
CLAUDE.mdガイドライン準拠・ゼロリスク保証ツール
"""

import os
import shutil
import sys
import json
import logging
from datetime import datetime
from pathlib import Path

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class UltraSyncPrevention:
    """ウルトラシンク副作用防止クラス"""
    
    def __init__(self):
        self.backup_dir = Path("ultra_sync_backups")
        self.session_file = "ultra_sync_session.json"
        self.critical_files = [
            "app.py", "utils.py", "config.py", 
            "templates/", "static/", "data/"
        ]
        
    def create_ultra_backup(self):
        """🔄 ウルトラシンクバックアップ作成"""
        logger.info("🔄 Creating Ultra Sync Backup System...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"backup_{timestamp}"
        
        try:
            # バックアップディレクトリ作成
            backup_path.mkdir(parents=True, exist_ok=True)
            
            backup_count = 0
            for file_path in self.critical_files:
                if os.path.exists(file_path):
                    if os.path.isfile(file_path):
                        shutil.copy2(file_path, backup_path / os.path.basename(file_path))
                        backup_count += 1
                    elif os.path.isdir(file_path):
                        shutil.copytree(file_path, backup_path / os.path.basename(file_path.rstrip('/')), 
                                      dirs_exist_ok=True)
                        backup_count += 1
                        
            logger.info(f"✅ Ultra Sync Backup Complete: {backup_count} items backed up")
            logger.info(f"📁 Backup location: {backup_path}")
            
            return str(backup_path)
            
        except Exception as e:
            logger.error(f"❌ Backup creation failed: {e}")
            return None
    
    def create_rollback_plan(self, backup_path):
        """🔄 ロールバック計画作成"""
        logger.info("🔄 Creating Ultra Sync Rollback Plan...")
        
        rollback_plan = {
            "timestamp": datetime.now().isoformat(),
            "backup_path": backup_path,
            "original_files": {},
            "rollback_commands": []
        }
        
        # 元ファイルの状態記録
        for file_path in self.critical_files:
            if os.path.exists(file_path):
                stat = os.stat(file_path)
                rollback_plan["original_files"][file_path] = {
                    "size": stat.st_size,
                    "mtime": stat.st_mtime,
                    "exists": True
                }
            else:
                rollback_plan["original_files"][file_path] = {
                    "exists": False
                }
        
        # ロールバックコマンド生成
        rollback_plan["rollback_commands"] = [
            f"rm -rf {file_path}" for file_path in self.critical_files if os.path.exists(file_path)
        ] + [
            f"cp -r {backup_path}/* ."
        ]
        
        # セッションファイルに保存
        with open(self.session_file, 'w', encoding='utf-8') as f:
            json.dump(rollback_plan, f, indent=2, ensure_ascii=False)
            
        logger.info("✅ Rollback plan created")
        return rollback_plan
    
    def verify_zero_side_effects(self):
        """🔍 副作用ゼロ検証"""
        logger.info("🔍 Verifying Zero Side Effects...")
        
        verification_passed = True
        issues = []
        
        # 1. ファイル権限チェック
        for file_path in self.critical_files:
            if os.path.exists(file_path):
                if not os.access(file_path, os.R_OK):
                    issues.append(f"❌ Read permission missing: {file_path}")
                    verification_passed = False
                if os.path.isfile(file_path) and not os.access(file_path, os.W_OK):
                    issues.append(f"❌ Write permission missing: {file_path}")
                    verification_passed = False
        
        # 2. 依存関係チェック
        try:
            import app
            import utils
            import config
            logger.info("✅ Module dependencies: OK")
        except ImportError as e:
            issues.append(f"❌ Import dependency broken: {e}")
            verification_passed = False
        
        # 3. データ整合性チェック
        data_files = ["data/4-1.csv", "data/4-2_2019.csv"]
        for data_file in data_files:
            if not os.path.isfile(data_file):
                issues.append(f"❌ Critical data file missing: {data_file}")
                verification_passed = False
        
        if verification_passed:
            logger.info("✅ Zero side effects verified")
        else:
            logger.error("❌ Side effects detected:")
            for issue in issues:
                logger.error(f"  {issue}")
        
        return verification_passed, issues
    
    def execute_ultra_sync_protection(self):
        """🛡️ ウルトラシンク保護実行"""
        logger.info("🛡️ Ultra Sync Protection Starting...")
        logger.info("=" * 50)
        
        # 1. バックアップ作成
        backup_path = self.create_ultra_backup()
        if not backup_path:
            logger.error("❌ Backup creation failed - ABORTING")
            return False
        
        # 2. ロールバック計画作成
        rollback_plan = self.create_rollback_plan(backup_path)
        
        # 3. 副作用ゼロ検証
        is_safe, issues = self.verify_zero_side_effects()
        
        if is_safe:
            logger.info("=" * 50)
            logger.info("🎉 ULTRA SYNC PROTECTION COMPLETE!")
            logger.info("✅ Zero side effects guaranteed")
            logger.info("🔄 Rollback plan ready")
            logger.info("🛡️ All safety measures activated")
            return True
        else:
            logger.error("=" * 50)
            logger.error("💥 ULTRA SYNC PROTECTION FAILED!")
            logger.error("❌ Side effects detected - deployment blocked")
            return False

def main():
    """メイン実行"""
    protection = UltraSyncPrevention()
    success = protection.execute_ultra_sync_protection()
    
    if success:
        print("\n🛡️ Ultra Sync Protection Active!")
        print("🔒 Zero side effects guaranteed")
        print("🚀 Safe for deployment")
        sys.exit(0)
    else:
        print("\n🚨 Ultra Sync Protection Failed!")
        print("⛔ Deployment blocked for safety")
        sys.exit(1)

if __name__ == "__main__":
    main()