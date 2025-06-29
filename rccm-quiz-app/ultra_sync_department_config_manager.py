#!/usr/bin/env python3
"""
📝 ULTRA SYNC: 部門マッピング外部コンフィグ管理システム

🎯 CLAUDE.md準拠・1万人使用ソフト品質基準・ウルトラシンク拡張性アーキテクチャ

【アーキテクチャ改善の目的】
❌ 従来の問題点:
- ハードコードされた部門マッピング（app.py内に直接記述）
- 変更時にソースコード修正が必要
- 複数ファイルでの重複管理
- 拡張性・メンテナンス性の欠如

【ウルトラシンク解決策】
✅ JSON設定ファイルによる外部化
✅ 設定の一元管理と整合性検証
✅ 動的リロード機能
✅ 後方互換性完全保証
✅ エンタープライズ級の拡張性
"""

import os
import sys
import json
import logging
import threading
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import hashlib
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class DepartmentConfigError(Exception):
    """部門設定エラー"""
    pass

class DepartmentConfigValidationError(DepartmentConfigError):
    """部門設定検証エラー"""
    pass

class UltraSyncDepartmentConfigManager:
    """
    📝 Ultra Sync 部門マッピング設定管理システム
    
    外部JSON設定ファイルによる部門マッピングの一元管理を提供し、
    ハードコードからの脱却と拡張性の向上を実現
    """
    
    def __init__(self, config_path: str = None, auto_reload: bool = True):
        # 🔥 ULTRA SYNC: 基本設定
        self.config_path = config_path or self._get_default_config_path()
        self.auto_reload = auto_reload
        
        # 📊 設定データ
        self.config_data = {}
        self.department_to_category = {}
        self.legacy_aliases = {}
        self.category_to_department = {}
        self.department_details = {}
        
        # 🔍 ファイル監視
        self._file_lock = threading.RLock()
        self._last_modified = 0
        self._file_hash = ""
        self._load_count = 0
        
        # 📈 統計情報
        self.stats = {
            'loads': 0,
            'reloads': 0,
            'validation_errors': 0,
            'mapping_requests': 0,
            'cache_hits': 0,
            'last_load_time': None,
            'config_version': None
        }
        
        # 初期設定ロード
        self.load_config()
        
        logger.info(f"📝 Ultra Sync Department Config Manager 初期化完了: {self.config_path}")
    
    def _get_default_config_path(self) -> str:
        """デフォルト設定ファイルパス取得"""
        # 環境変数による設定
        env_path = os.environ.get('RCCM_DEPARTMENT_CONFIG_PATH')
        if env_path and os.path.exists(env_path):
            return env_path
        
        # プロジェクトディレクトリ内の設定ファイル
        project_root = Path(__file__).parent
        config_file = project_root / 'config' / 'department_mapping.json'
        
        if config_file.exists():
            return str(config_file)
        
        # フォールバック: 同じディレクトリ
        fallback_file = project_root / 'department_mapping.json'
        return str(fallback_file)
    
    def load_config(self, force_reload: bool = False) -> bool:
        """設定ファイル読み込み"""
        with self._file_lock:
            try:
                # ファイル存在確認
                if not os.path.exists(self.config_path):
                    logger.error(f"❌ 設定ファイルが見つかりません: {self.config_path}")
                    return False
                
                # ファイル変更検証（自動リロード時）
                if not force_reload and self.auto_reload:
                    current_modified = os.path.getmtime(self.config_path)
                    if current_modified <= self._last_modified and self.config_data:
                        self.stats['cache_hits'] += 1
                        return True
                
                # ファイル読み込み
                start_time = time.time()
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    raw_content = f.read()
                    file_hash = hashlib.md5(raw_content.encode('utf-8')).hexdigest()
                    
                    # ハッシュ変更確認
                    if not force_reload and file_hash == self._file_hash and self.config_data:
                        self.stats['cache_hits'] += 1
                        return True
                    
                    # JSON解析
                    config_data = json.loads(raw_content)
                
                # 設定検証
                validation_result = self._validate_config(config_data)
                if not validation_result['valid']:
                    self.stats['validation_errors'] += 1
                    raise DepartmentConfigValidationError(f"設定検証失敗: {validation_result['errors']}")
                
                # 設定適用
                self._apply_config(config_data)
                
                # メタデータ更新
                self._last_modified = os.path.getmtime(self.config_path)
                self._file_hash = file_hash
                self._load_count += 1
                
                # 統計更新
                load_duration = time.time() - start_time
                if self.stats['loads'] == 0:
                    self.stats['loads'] = 1
                else:
                    self.stats['reloads'] += 1
                
                self.stats['last_load_time'] = datetime.now(timezone.utc).isoformat()
                self.stats['config_version'] = config_data.get('meta', {}).get('version', 'unknown')
                
                logger.info(f"✅ 部門設定ロード成功: {len(self.department_to_category)}部門, {load_duration:.3f}秒")
                return True
                
            except json.JSONDecodeError as e:
                logger.error(f"❌ JSON解析エラー: {e}")
                self.stats['validation_errors'] += 1
                return False
            except Exception as e:
                logger.error(f"❌ 設定ロードエラー: {e}")
                self.stats['validation_errors'] += 1
                return False
    
    def _validate_config(self, config_data: Dict) -> Dict[str, Any]:
        """設定データ検証"""
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        try:
            # 必須セクション確認
            required_sections = ['department_to_category_mapping', 'legacy_department_aliases']
            for section in required_sections:
                if section not in config_data:
                    validation_result['errors'].append(f"必須セクション '{section}' が見つかりません")
            
            # 部門マッピング検証
            dept_mapping = config_data.get('department_to_category_mapping', {})
            if not isinstance(dept_mapping, dict):
                validation_result['errors'].append("部門マッピングが辞書形式ではありません")
            elif len(dept_mapping) == 0:
                validation_result['errors'].append("部門マッピングが空です")
            else:
                # 重複カテゴリ検証
                categories = list(dept_mapping.values())
                duplicates = [cat for cat in set(categories) if categories.count(cat) > 1]
                if duplicates:
                    validation_result['errors'].append(f"重複カテゴリが検出されました: {duplicates}")
                
                # 必須部門確認
                validation_rules = config_data.get('validation_rules', {})
                required_departments = validation_rules.get('required_departments', [])
                missing_departments = [dept for dept in required_departments if dept not in dept_mapping]
                if missing_departments:
                    validation_result['warnings'].append(f"必須部門が不足: {missing_departments}")
            
            # レガシーエイリアス検証
            legacy_aliases = config_data.get('legacy_department_aliases', {})
            if not isinstance(legacy_aliases, dict):
                validation_result['warnings'].append("レガシーエイリアスが辞書形式ではありません")
            else:
                # エイリアス先部門の存在確認
                for alias, target in legacy_aliases.items():
                    if target not in dept_mapping:
                        validation_result['warnings'].append(f"エイリアス '{alias}' の参照先 '{target}' が存在しません")
            
            # バージョン情報確認
            meta = config_data.get('meta', {})
            if 'version' not in meta:
                validation_result['warnings'].append("バージョン情報が設定されていません")
            
        except Exception as e:
            validation_result['errors'].append(f"検証処理エラー: {e}")
        
        # 最終判定
        validation_result['valid'] = len(validation_result['errors']) == 0
        
        return validation_result
    
    def _apply_config(self, config_data: Dict):
        """設定データ適用"""
        # 基本設定
        self.config_data = config_data
        
        # 部門→カテゴリマッピング
        self.department_to_category = config_data.get('department_to_category_mapping', {})
        
        # レガシーエイリアス
        self.legacy_aliases = config_data.get('legacy_department_aliases', {})
        
        # カテゴリ→部門逆マッピング生成
        self.category_to_department = {v: k for k, v in self.department_to_category.items()}
        
        # 部門詳細情報
        self.department_details = config_data.get('department_details', {})
        
        logger.info(f"📝 設定適用完了: {len(self.department_to_category)}部門, {len(self.legacy_aliases)}エイリアス")
    
    def get_category_by_department(self, department: str) -> Optional[str]:
        """部門名からカテゴリ名を取得"""
        self.stats['mapping_requests'] += 1
        
        # 自動リロードチェック
        if self.auto_reload:
            self.load_config()
        
        if not department:
            return None
        
        # 直接マッピング
        if department in self.department_to_category:
            return self.department_to_category[department]
        
        # レガシーエイリアス確認
        if department in self.legacy_aliases:
            target_department = self.legacy_aliases[department]
            return self.department_to_category.get(target_department)
        
        # 大文字小文字を無視した検索
        department_lower = department.lower()
        for dept, category in self.department_to_category.items():
            if dept.lower() == department_lower:
                return category
        
        # レガシーエイリアスでも大文字小文字を無視
        for alias, target in self.legacy_aliases.items():
            if alias.lower() == department_lower:
                return self.department_to_category.get(target)
        
        logger.warning(f"⚠️ 未知の部門名: {department}")
        return None
    
    def get_department_by_category(self, category: str) -> Optional[str]:
        """カテゴリ名から部門名を取得"""
        self.stats['mapping_requests'] += 1
        
        # 自動リロードチェック
        if self.auto_reload:
            self.load_config()
        
        return self.category_to_department.get(category)
    
    def normalize_department_name(self, department: str) -> Optional[str]:
        """部門名正規化"""
        if not department:
            return None
        
        # 自動リロードチェック
        if self.auto_reload:
            self.load_config()
        
        # 既に正規化済み
        if department in self.department_to_category:
            return department
        
        # レガシーエイリアス変換
        if department in self.legacy_aliases:
            return self.legacy_aliases[department]
        
        # 大文字小文字を無視した検索
        department_lower = department.lower()
        for dept in self.department_to_category.keys():
            if dept.lower() == department_lower:
                return dept
        
        # レガシーエイリアス内での検索
        for alias, target in self.legacy_aliases.items():
            if alias.lower() == department_lower:
                return target
        
        return None
    
    def get_all_departments(self) -> List[str]:
        """全部門リスト取得"""
        if self.auto_reload:
            self.load_config()
        
        return list(self.department_to_category.keys())
    
    def get_all_categories(self) -> List[str]:
        """全カテゴリリスト取得"""
        if self.auto_reload:
            self.load_config()
        
        return list(self.department_to_category.values())
    
    def get_department_details(self, department: str) -> Optional[Dict[str, Any]]:
        """部門詳細情報取得"""
        if self.auto_reload:
            self.load_config()
        
        normalized_dept = self.normalize_department_name(department)
        if normalized_dept:
            return self.department_details.get(normalized_dept, {})
        
        return None
    
    def is_valid_department(self, department: str) -> bool:
        """部門名有効性確認"""
        return self.normalize_department_name(department) is not None
    
    def is_legacy_alias(self, department: str) -> bool:
        """レガシーエイリアス判定"""
        if self.auto_reload:
            self.load_config()
        
        return department in self.legacy_aliases
    
    def get_mapping_statistics(self) -> Dict[str, Any]:
        """マッピング統計情報取得"""
        return {
            'total_departments': len(self.department_to_category),
            'total_categories': len(set(self.department_to_category.values())),
            'legacy_aliases': len(self.legacy_aliases),
            'config_version': self.config_data.get('meta', {}).get('version', 'unknown'),
            'last_updated': self.config_data.get('meta', {}).get('last_updated', 'unknown'),
            'load_statistics': self.stats.copy()
        }
    
    def validate_current_config(self) -> Dict[str, Any]:
        """現在の設定検証"""
        if self.auto_reload:
            self.load_config()
        
        return self._validate_config(self.config_data)
    
    def reload_config(self) -> bool:
        """設定強制リロード"""
        logger.info("🔄 部門設定強制リロード開始")
        return self.load_config(force_reload=True)
    
    def export_config_to_python(self, output_file: str = None) -> str:
        """Python形式の設定ファイル生成（後方互換性用）"""
        if self.auto_reload:
            self.load_config()
        
        python_code = f'''#!/usr/bin/env python3
"""
自動生成された部門マッピング設定ファイル
生成日時: {datetime.now(timezone.utc).isoformat()}
元設定ファイル: {self.config_path}
バージョン: {self.config_data.get('meta', {}).get('version', 'unknown')}

⚠️ このファイルは自動生成されています。直接編集せずに、
   {self.config_path} を編集してください。
"""

# 部門→カテゴリマッピング
DEPARTMENT_TO_CATEGORY_MAPPING = {repr(self.department_to_category)}

# レガシーエイリアス
LEGACY_DEPARTMENT_ALIASES = {repr(self.legacy_aliases)}

# カテゴリ→部門逆マッピング
CATEGORY_TO_DEPARTMENT_MAPPING = {repr(self.category_to_department)}

def normalize_department_name(department_name):
    """部門名正規化"""
    if not department_name:
        return None
    
    if department_name in DEPARTMENT_TO_CATEGORY_MAPPING:
        return department_name
    
    if department_name in LEGACY_DEPARTMENT_ALIASES:
        return LEGACY_DEPARTMENT_ALIASES[department_name]
    
    return None

def get_department_category(department_name):
    """部門→カテゴリ変換"""
    normalized = normalize_department_name(department_name)
    if normalized:
        return DEPARTMENT_TO_CATEGORY_MAPPING.get(normalized)
    return None
'''
        
        if output_file:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(python_code)
                logger.info(f"✅ Python設定ファイル生成: {output_file}")
            except Exception as e:
                logger.error(f"❌ Python設定ファイル生成失敗: {e}")
        
        return python_code
    
    @contextmanager
    def config_update_context(self):
        """設定更新コンテキスト"""
        with self._file_lock:
            old_config = self.config_data.copy()
            try:
                yield
            except Exception:
                # エラー時は元の設定に戻す
                self._apply_config(old_config)
                raise

# グローバルインスタンス
_global_config_manager = None

def get_department_config_manager() -> UltraSyncDepartmentConfigManager:
    """グローバル設定管理インスタンス取得"""
    global _global_config_manager
    
    if _global_config_manager is None:
        _global_config_manager = UltraSyncDepartmentConfigManager()
    
    return _global_config_manager

# 後方互換性関数
def get_department_category(department_name: str) -> Optional[str]:
    """後方互換性: 部門→カテゴリ変換"""
    manager = get_department_config_manager()
    return manager.get_category_by_department(department_name)

def normalize_department_name(department_name: str) -> Optional[str]:
    """後方互換性: 部門名正規化"""
    manager = get_department_config_manager()
    return manager.normalize_department_name(department_name)

def main():
    """設定管理テスト実行"""
    print("📝 Ultra Sync Department Config Manager テスト")
    print("=" * 60)
    
    # 設定管理インスタンス作成
    manager = UltraSyncDepartmentConfigManager()
    
    # 基本機能テスト
    print("🔍 基本機能テスト:")
    test_departments = ['road', 'tunnel', 'civil_planning', 'invalid_dept']
    
    for dept in test_departments:
        category = manager.get_category_by_department(dept)
        normalized = manager.normalize_department_name(dept)
        is_legacy = manager.is_legacy_alias(dept)
        
        print(f"  {dept} -> カテゴリ: {category}, 正規化: {normalized}, レガシー: {is_legacy}")
    
    # 統計情報表示
    print("\n📊 統計情報:")
    stats = manager.get_mapping_statistics()
    for key, value in stats.items():
        if key != 'load_statistics':
            print(f"  {key}: {value}")
    
    # 設定検証
    print("\n✅ 設定検証:")
    validation = manager.validate_current_config()
    print(f"  有効: {validation['valid']}")
    if validation['errors']:
        print(f"  エラー: {validation['errors']}")
    if validation['warnings']:
        print(f"  警告: {validation['warnings']}")
    
    print("\n🎉 テスト完了")

if __name__ == "__main__":
    main()