#!/usr/bin/env python3
"""
🛡️ 副作用ゼロ保証デバッグ戦略
前チャットの11回エラー連鎖を防ぐ安全システム
"""

import os
import shutil
import json
import time
from datetime import datetime
from collections import defaultdict

class SafeDebugManager:
    def __init__(self, project_root):
        self.project_root = project_root
        self.backup_root = os.path.join(project_root, 'safe_debug_backups')
        self.test_environment = os.path.join(project_root, 'isolated_test_env')
        self.error_matrix = {}
        
    def create_checkpoint(self, description="Manual checkpoint"):
        """完全バックアップチェックポイント作成"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        checkpoint_dir = os.path.join(self.backup_root, f'checkpoint_{timestamp}')
        
        print(f"🔒 チェックポイント作成: {description}")
        
        # 重要ファイルのバックアップ
        critical_files = [
            'app.py',
            'utils.py',
            'config.py',
            'templates/',
            'static/',
            'data/',
            'requirements.txt',
            'CLAUDE.md'
        ]
        
        os.makedirs(checkpoint_dir, exist_ok=True)
        
        for file_path in critical_files:
            src = os.path.join(self.project_root, file_path)
            dst = os.path.join(checkpoint_dir, file_path)
            
            if os.path.exists(src):
                if os.path.isdir(src):
                    shutil.copytree(src, dst, dirs_exist_ok=True)
                else:
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                    shutil.copy2(src, dst)
        
        # チェックポイント情報保存
        checkpoint_info = {
            'timestamp': timestamp,
            'description': description,
            'git_commit': self.get_git_commit(),
            'files_backed_up': critical_files
        }
        
        with open(os.path.join(checkpoint_dir, 'checkpoint_info.json'), 'w') as f:
            json.dump(checkpoint_info, f, indent=2, ensure_ascii=False)
            
        print(f"✅ チェックポイント保存完了: {checkpoint_dir}")
        return checkpoint_dir
    
    def create_isolated_test_environment(self):
        """分離テスト環境作成"""
        print("🏗️ 分離テスト環境作成中...")
        
        if os.path.exists(self.test_environment):
            shutil.rmtree(self.test_environment)
        
        # プロジェクト全体をコピー
        shutil.copytree(self.project_root, self.test_environment, 
                       ignore=shutil.ignore_patterns('.git', '__pycache__', '*.pyc', 'safe_debug_*'))
        
        # テスト用設定ファイル作成
        test_config = {
            'TESTING': True,
            'DEBUG': True,
            'SECRET_KEY': 'test-key-not-for-production',
            'SESSION_PERMANENT': False,
            'PREFERRED_URL_SCHEME': 'http'
        }
        
        config_file = os.path.join(self.test_environment, 'test_config.py')
        with open(config_file, 'w') as f:
            f.write("# テスト専用設定\n")
            for key, value in test_config.items():
                f.write(f"{key} = {repr(value)}\n")
        
        print(f"✅ 分離テスト環境作成完了: {self.test_environment}")
        return self.test_environment
    
    def get_git_commit(self):
        """現在のGitコミット取得"""
        try:
            import subprocess
            result = subprocess.run(['git', 'rev-parse', 'HEAD'], 
                                  capture_output=True, text=True, cwd=self.project_root)
            return result.stdout.strip() if result.returncode == 0 else "unknown"
        except:
            return "git_not_available"
    
    def categorize_errors_by_risk(self):
        """エラーをリスク別に分類"""
        
        # 前回のエラーハンティング結果を基に分類
        risk_matrix = {
            'CRITICAL_SECURITY': {
                'description': 'セキュリティ脆弱性（即座に修正必要）',
                'errors': [
                    'XSS/SQLインジェクション脆弱性',
                    'パストラバーサル攻撃',
                    'セッション操作脆弱性'
                ],
                'side_effect_risk': 'LOW',  # セキュリティ修正は通常副作用が少ない
                'fix_approach': 'INPUT_VALIDATION'
            },
            'HIGH_ARCHITECTURE': {
                'description': 'アーキテクチャ問題（慎重な修正必要）',
                'errors': [
                    '論理エラー5,456個',
                    'ルート競合',
                    'セッション不整合'
                ],
                'side_effect_risk': 'VERY_HIGH',  # アーキテクチャ変更は危険
                'fix_approach': 'GRADUAL_REFACTORING'
            },
            'MEDIUM_DATA': {
                'description': 'データ整合性問題',
                'errors': [
                    'CSVカラム数不整合',
                    'エンコーディング問題',
                    'データ破損'
                ],
                'side_effect_risk': 'MEDIUM',
                'fix_approach': 'DATA_MIGRATION'
            },
            'LOW_COSMETIC': {
                'description': '表示・パフォーマンス問題',
                'errors': [
                    'テンプレート未定義変数',
                    'console.log残存',
                    'メモリリーク'
                ],
                'side_effect_risk': 'LOW',
                'fix_approach': 'SAFE_CLEANUP'
            }
        }
        
        return risk_matrix
    
    def create_fix_plan(self):
        """副作用を考慮した修正計画作成"""
        risk_matrix = self.categorize_errors_by_risk()
        
        fix_plan = {
            'phase_1_security': {
                'priority': 1,
                'description': 'セキュリティ脆弱性修正（副作用リスク最小）',
                'actions': [
                    'input validation追加',
                    'sanitization関数実装',
                    'セキュリティヘッダー追加'
                ],
                'testing': 'セキュリティテストのみ',
                'rollback_strategy': '即座にチェックポイント復元'
            },
            'phase_2_data': {
                'priority': 2,
                'description': 'データ整合性修正（分離環境で慎重に）',
                'actions': [
                    'CSVデータ修正',
                    'エンコーディング統一',
                    'データ検証強化'
                ],
                'testing': 'データロード全テスト',
                'rollback_strategy': 'データファイルのみ復元'
            },
            'phase_3_cosmetic': {
                'priority': 3,
                'description': '軽微な修正（安全）',
                'actions': [
                    'テンプレート変数修正',
                    'console.log削除',
                    'コードクリーンアップ'
                ],
                'testing': 'UI表示確認',
                'rollback_strategy': 'ファイル単位で復元'
            },
            'phase_4_architecture': {
                'priority': 4,
                'description': 'アーキテクチャ修正（最後に慎重に）',
                'actions': [
                    '段階的リファクタリング',
                    '一度に1つの変更のみ',
                    '各変更後の完全テスト'
                ],
                'testing': '全機能完走テスト',
                'rollback_strategy': '完全チェックポイント復元'
            }
        }
        
        return fix_plan
    
    def validate_fix_safety(self, fix_description, affected_files):
        """修正の安全性事前検証"""
        safety_score = 100
        warnings = []
        
        # 危険なパターンをチェック
        dangerous_patterns = [
            ('session', 'セッション変更は副作用リスク高'),
            ('global', 'グローバル変数変更は危険'),
            ('import', '新しいimportは依存関係変更'),
            ('def ', '新しい関数は呼び出し関係変更'),
            ('class ', '新しいクラスは設計変更'),
            ('@app.route', 'ルート変更は URL 設計変更')
        ]
        
        for pattern, warning in dangerous_patterns:
            if pattern in fix_description.lower():
                safety_score -= 20
                warnings.append(warning)
        
        # 影響ファイル数チェック
        if len(affected_files) > 3:
            safety_score -= 30
            warnings.append(f'影響ファイル数過多: {len(affected_files)}個')
        
        # アーキテクチャファイルチェック
        critical_files = ['app.py', 'config.py', 'utils.py']
        affected_critical = [f for f in affected_files if f in critical_files]
        if affected_critical:
            safety_score -= 40
            warnings.append(f'重要ファイル変更: {affected_critical}')
        
        return {
            'safety_score': max(0, safety_score),
            'warnings': warnings,
            'recommendation': 'SAFE' if safety_score > 70 else 'CAUTION' if safety_score > 40 else 'DANGEROUS'
        }

def generate_safe_debug_guide():
    """安全デバッグガイド生成"""
    guide = """
🛡️ 絶対に副作用を起こさないデバッグガイド

【段階1: 準備フェーズ】
1. ✅ 完全バックアップ作成
2. ✅ 分離テスト環境構築
3. ✅ Git チェックポイント作成
4. ✅ エラー優先度マトリックス作成

【段階2: 安全修正フェーズ】
1. 🔐 セキュリティ修正（副作用リスク: 最小）
   - Input validation のみ
   - 既存ロジック変更なし
   - テスト: セキュリティスキャンのみ

2. 📊 データ修正（副作用リスク: 小）
   - CSVファイルのみ
   - アプリケーションロジック変更なし
   - テスト: データロード確認のみ

3. 🎨 表示修正（副作用リスク: 最小）
   - テンプレートのみ
   - バックエンドロジック変更なし
   - テスト: UI表示確認のみ

4. 🏗️ アーキテクチャ修正（副作用リスク: 最大）
   - 1つずつ段階的に
   - 各変更後に完全テスト
   - 問題時は即座にロールバック

【段階3: 検証フェーズ】
1. ✅ 分離環境での完全テスト
2. ✅ 元環境との比較確認
3. ✅ 副作用チェック
4. ✅ 完走テスト実行

【緊急時のロールバック】
1. 🚨 問題発生時は即座に停止
2. 🔄 最新チェックポイントに復元
3. 📝 問題原因の詳細分析
4. 🛡️ より安全な方法で再試行

【絶対禁止事項】
❌ 複数ファイルの同時変更
❌ テストなしでの本番適用
❌ アーキテクチャとデータの同時変更
❌ バックアップなしでの修正
❌ 副作用未確認での次修正
"""
    return guide

if __name__ == "__main__":
    project_root = '/mnt/c/Users/ABC/Desktop/rccm-quiz-app/rccm-quiz-app'
    manager = SafeDebugManager(project_root)
    
    print("🛡️ 安全デバッグ戦略初期化")
    print("=" * 60)
    
    # 1. チェックポイント作成
    checkpoint = manager.create_checkpoint("エラー修正開始前の安全バックアップ")
    
    # 2. 分離環境作成
    test_env = manager.create_isolated_test_environment()
    
    # 3. 修正計画作成
    fix_plan = manager.create_fix_plan()
    
    # 4. ガイド表示
    guide = generate_safe_debug_guide()
    print(guide)
    
    print("\n🎯 次のステップ:")
    print("1. セキュリティ修正から開始（最も安全）")
    print("2. 各修正後に必ず動作確認")
    print("3. 問題発生時は即座にロールバック")
    print("4. アーキテクチャ修正は最後に慎重に")