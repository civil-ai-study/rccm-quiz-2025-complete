#!/usr/bin/env python3
"""
RCCM学習アプリ - セッション移行ツール
ファイルベースセッション → Redis セッション移行システム
"""

import os
import sys
import argparse
import json
import logging
from datetime import datetime
from pathlib import Path

# アプリのパスを追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from redis_config import redis_session_manager, get_redis_config
from session_manager import advanced_session_manager, initialize_session_system
from config import RedisSessionConfig

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('session_migration.log')
    ]
)
logger = logging.getLogger(__name__)


class SessionMigrationTool:
    """セッション移行ツール"""
    
    def __init__(self):
        self.migration_report = {
            'start_time': None,
            'end_time': None,
            'source_type': None,
            'target_type': 'redis',
            'total_sessions': 0,
            'successful_migrations': 0,
            'failed_migrations': 0,
            'errors': [],
            'performance_stats': {}
        }
    
    def analyze_current_session_system(self):
        """現在のセッションシステム分析"""
        logger.info("🔍 現在のセッションシステム分析開始...")
        
        analysis = {
            'file_sessions': self._analyze_file_sessions(),
            'redis_availability': self._check_redis_availability(),
            'migration_requirements': {}
        }
        
        # 移行要件分析
        if analysis['file_sessions']['total_files'] > 0:
            analysis['migration_requirements'] = {
                'estimated_migration_time': analysis['file_sessions']['total_files'] * 0.1,  # 秒
                'estimated_redis_memory': analysis['file_sessions']['total_size'] * 1.2,  # バイト
                'recommended_backup': True
            }
        
        logger.info(f"分析完了: {analysis['file_sessions']['total_files']}個のファイルセッション検出")
        return analysis
    
    def _analyze_file_sessions(self):
        """ファイルセッション分析"""
        flask_session_dir = Path('flask_session')
        
        analysis = {
            'directory_exists': flask_session_dir.exists(),
            'total_files': 0,
            'total_size': 0,
            'oldest_session': None,
            'newest_session': None,
            'file_details': []
        }
        
        if not flask_session_dir.exists():
            logger.info("flask_sessionディレクトリが存在しません")
            return analysis
        
        session_files = list(flask_session_dir.glob('*'))
        analysis['total_files'] = len(session_files)
        
        timestamps = []
        for file_path in session_files:
            try:
                stat = file_path.stat()
                file_info = {
                    'path': str(file_path),
                    'size': stat.st_size,
                    'created': datetime.fromtimestamp(stat.st_ctime),
                    'modified': datetime.fromtimestamp(stat.st_mtime)
                }
                
                analysis['file_details'].append(file_info)
                analysis['total_size'] += stat.st_size
                timestamps.append(stat.st_mtime)
                
            except Exception as e:
                logger.warning(f"ファイル分析エラー {file_path}: {e}")
        
        if timestamps:
            analysis['oldest_session'] = datetime.fromtimestamp(min(timestamps))
            analysis['newest_session'] = datetime.fromtimestamp(max(timestamps))
        
        return analysis
    
    def _check_redis_availability(self):
        """Redis可用性チェック"""
        try:
            # Redis接続テスト
            redis_client = redis_session_manager.initialize_redis_connection()
            
            if not redis_client:
                return {'available': False, 'error': 'Redis接続を確立できません'}
            
            # 基本操作テスト
            test_key = 'rccm_migration_test'
            redis_client.set(test_key, 'test_value', ex=60)
            test_result = redis_client.get(test_key)
            redis_client.delete(test_key)
            
            if test_result != 'test_value':
                return {'available': False, 'error': 'Redis読み書きテスト失敗'}
            
            # Redis情報取得
            redis_info = redis_client.info()
            
            return {
                'available': True,
                'version': redis_info.get('redis_version'),
                'memory_usage': redis_info.get('used_memory_human'),
                'connected_clients': redis_info.get('connected_clients'),
                'max_memory': redis_info.get('maxmemory_human', '無制限')
            }
            
        except Exception as e:
            logger.error(f"Redis可用性チェックエラー: {e}")
            return {'available': False, 'error': str(e)}
    
    def create_migration_backup(self):
        """移行前バックアップ作成"""
        logger.info("📦 移行前バックアップ作成開始...")
        
        backup_dir = Path('session_migration_backup')
        backup_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_info = {
            'timestamp': timestamp,
            'backup_dir': str(backup_dir),
            'files_backed_up': 0,
            'backup_size': 0
        }
        
        try:
            # ファイルセッションバックアップ
            flask_session_dir = Path('flask_session')
            if flask_session_dir.exists():
                backup_session_dir = backup_dir / f'flask_session_{timestamp}'
                backup_session_dir.mkdir(exist_ok=True)
                
                import shutil
                for session_file in flask_session_dir.iterdir():
                    try:
                        backup_file = backup_session_dir / session_file.name
                        shutil.copy2(session_file, backup_file)
                        backup_info['files_backed_up'] += 1
                        backup_info['backup_size'] += session_file.stat().st_size
                        
                    except Exception as e:
                        logger.warning(f"ファイルバックアップエラー {session_file}: {e}")
            
            # バックアップ情報保存
            backup_info_file = backup_dir / f'backup_info_{timestamp}.json'
            with open(backup_info_file, 'w', encoding='utf-8') as f:
                json.dump(backup_info, f, ensure_ascii=False, indent=2, default=str)
            
            logger.info(f"✅ バックアップ完了: {backup_info['files_backed_up']}ファイル")
            return backup_info
            
        except Exception as e:
            logger.error(f"バックアップエラー: {e}")
            return None
    
    def execute_migration(self, dry_run=False):
        """セッション移行実行"""
        self.migration_report['start_time'] = datetime.now()
        
        logger.info(f"🚀 セッション移行開始 (dry_run={dry_run})...")
        
        try:
            # システム初期化
            if not initialize_session_system():
                raise Exception("セッションシステム初期化失敗")
            
            # ファイルセッション移行
            flask_session_dir = Path('flask_session')
            if flask_session_dir.exists():
                self.migration_report['source_type'] = 'file'
                migration_result = advanced_session_manager.migrate_file_session_to_redis(
                    str(flask_session_dir)
                )
                
                self.migration_report['total_sessions'] = migration_result['success'] + migration_result['failed']
                self.migration_report['successful_migrations'] = migration_result['success']
                self.migration_report['failed_migrations'] = migration_result['failed']
                self.migration_report['errors'] = migration_result['errors']
                
            else:
                logger.info("移行対象のファイルセッションが見つかりません")
            
            # 移行後検証
            if not dry_run:
                self._verify_migration()
            
            self.migration_report['end_time'] = datetime.now()
            duration = (self.migration_report['end_time'] - self.migration_report['start_time']).total_seconds()
            
            logger.info(f"✅ セッション移行完了 (所要時間: {duration:.2f}秒)")
            logger.info(f"成功: {self.migration_report['successful_migrations']}, 失敗: {self.migration_report['failed_migrations']}")
            
            return self.migration_report
            
        except Exception as e:
            logger.error(f"セッション移行エラー: {e}")
            self.migration_report['errors'].append(f"Migration process error: {str(e)}")
            return self.migration_report
    
    def _verify_migration(self):
        """移行後検証"""
        logger.info("🔍 移行後検証開始...")
        
        try:
            # Redisセッション確認
            redis_client = redis_session_manager.redis_client
            session_keys = redis_client.keys(f"{RedisSessionConfig.SESSION_KEY_PREFIX}*")
            
            verification_result = {
                'redis_sessions_count': len(session_keys),
                'sample_session_valid': False,
                'redis_connection_stable': False
            }
            
            # サンプルセッション検証
            if session_keys:
                sample_key = session_keys[0]
                sample_data = redis_client.get(sample_key)
                ttl = redis_client.ttl(sample_key)
                
                if sample_data and ttl > 0:
                    verification_result['sample_session_valid'] = True
            
            # Redis接続安定性確認
            verification_result['redis_connection_stable'] = redis_session_manager.health_check()
            
            logger.info(f"検証結果: {verification_result}")
            self.migration_report['verification'] = verification_result
            
        except Exception as e:
            logger.error(f"移行後検証エラー: {e}")
            self.migration_report['errors'].append(f"Verification error: {str(e)}")
    
    def generate_migration_report(self, output_file='session_migration_report.json'):
        """移行レポート生成"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.migration_report, f, ensure_ascii=False, indent=2, default=str)
            
            logger.info(f"📊 移行レポート生成: {output_file}")
            
            # コンソール用サマリー出力
            self._print_migration_summary()
            
        except Exception as e:
            logger.error(f"レポート生成エラー: {e}")
    
    def _print_migration_summary(self):
        """移行サマリー出力"""
        print("\n" + "="*60)
        print("          RCCM セッション移行サマリー")
        print("="*60)
        print(f"開始時刻: {self.migration_report['start_time']}")
        print(f"終了時刻: {self.migration_report['end_time']}")
        print(f"移行元: {self.migration_report['source_type']}")
        print(f"移行先: {self.migration_report['target_type']}")
        print(f"総セッション数: {self.migration_report['total_sessions']}")
        print(f"成功: {self.migration_report['successful_migrations']}")
        print(f"失敗: {self.migration_report['failed_migrations']}")
        
        if self.migration_report['errors']:
            print(f"エラー数: {len(self.migration_report['errors'])}")
            print("主なエラー:")
            for error in self.migration_report['errors'][:3]:
                print(f"  - {error}")
        
        print("="*60)
    
    def rollback_migration(self, backup_timestamp):
        """移行ロールバック"""
        logger.info(f"🔄 移行ロールバック開始: {backup_timestamp}")
        
        try:
            backup_dir = Path('session_migration_backup')
            backup_session_dir = backup_dir / f'flask_session_{backup_timestamp}'
            
            if not backup_session_dir.exists():
                raise FileNotFoundError(f"バックアップが見つかりません: {backup_session_dir}")
            
            # Redis セッション削除
            redis_client = redis_session_manager.redis_client
            session_keys = redis_client.keys(f"{RedisSessionConfig.SESSION_KEY_PREFIX}*")
            
            if session_keys:
                redis_client.delete(*session_keys)
                logger.info(f"Redisセッション削除: {len(session_keys)}キー")
            
            # ファイルセッション復元
            flask_session_dir = Path('flask_session')
            flask_session_dir.mkdir(exist_ok=True)
            
            import shutil
            restored_count = 0
            for backup_file in backup_session_dir.iterdir():
                try:
                    restore_file = flask_session_dir / backup_file.name
                    shutil.copy2(backup_file, restore_file)
                    restored_count += 1
                except Exception as e:
                    logger.warning(f"ファイル復元エラー {backup_file}: {e}")
            
            logger.info(f"✅ ロールバック完了: {restored_count}ファイル復元")
            return True
            
        except Exception as e:
            logger.error(f"ロールバックエラー: {e}")
            return False


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description='RCCM セッション移行ツール')
    parser.add_argument('--analyze', action='store_true', 
                       help='現在のセッションシステム分析のみ実行')
    parser.add_argument('--backup', action='store_true',
                       help='移行前バックアップのみ作成')
    parser.add_argument('--migrate', action='store_true',
                       help='セッション移行実行')
    parser.add_argument('--dry-run', action='store_true',
                       help='ドライラン（実際の変更は行わない）')
    parser.add_argument('--rollback', type=str, metavar='TIMESTAMP',
                       help='指定されたタイムスタンプのバックアップからロールバック')
    parser.add_argument('--report', type=str, metavar='FILE',
                       default='session_migration_report.json',
                       help='レポート出力ファイル名')
    
    args = parser.parse_args()
    
    tool = SessionMigrationTool()
    
    try:
        if args.rollback:
            # ロールバック
            success = tool.rollback_migration(args.rollback)
            sys.exit(0 if success else 1)
        
        if args.analyze:
            # 分析のみ
            analysis = tool.analyze_current_session_system()
            print(json.dumps(analysis, indent=2, ensure_ascii=False, default=str))
            return
        
        if args.backup:
            # バックアップ作成
            backup_info = tool.create_migration_backup()
            if backup_info:
                print(f"バックアップ作成完了: {backup_info['timestamp']}")
            else:
                print("バックアップ作成失敗")
                sys.exit(1)
            return
        
        if args.migrate:
            # 移行実行
            # 自動バックアップ作成
            backup_info = tool.create_migration_backup()
            if not backup_info:
                logger.warning("バックアップ作成失敗 - 移行を続行しますか？")
                input("続行するにはEnterキーを押してください...")
            
            # 移行実行
            migration_result = tool.execute_migration(dry_run=args.dry_run)
            
            # レポート生成
            tool.generate_migration_report(args.report)
            
            # 成功判定
            success_rate = migration_result['successful_migrations'] / max(migration_result['total_sessions'], 1)
            if success_rate < 0.9:  # 90%未満の成功率
                logger.warning(f"移行成功率が低いです: {success_rate:.1%}")
                sys.exit(1)
            
            return
        
        # デフォルト: 分析のみ
        analysis = tool.analyze_current_session_system()
        print("現在のセッションシステム分析結果:")
        print(json.dumps(analysis, indent=2, ensure_ascii=False, default=str))
        
    except KeyboardInterrupt:
        print("\n移行が中断されました")
        sys.exit(1)
    except Exception as e:
        logger.error(f"予期しないエラー: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()