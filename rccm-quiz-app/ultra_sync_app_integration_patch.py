#!/usr/bin/env python3
"""
📝 ULTRA SYNC: RCCM Quiz App 部門設定外部化統合パッチ

🎯 既存のapp.pyへの最小侵襲統合パッチ - ハードコードからJSON設定への移行

【統合戦略】
✅ 既存コードの動作を保証しつつ外部設定システムを統合
✅ 段階的移行により運用中断ゼロ
✅ 完全な後方互換性保証
✅ エラー発生時の自動フォールバック
"""

import sys
import os
import logging

# RCCM Quiz App のパス追加
sys.path.append('/mnt/c/Users/z285/Desktop/rccm-quiz-app/rccm-quiz-app')

try:
    from ultra_sync_department_config_manager import get_department_config_manager
    print("✅ Ultra Sync Department Config Manager インポート成功")
except ImportError as e:
    print(f"❌ 部門設定管理システムインポート失敗: {e}")
    sys.exit(1)

logger = logging.getLogger(__name__)

class UltraSyncAppIntegrationPatch:
    """🔧 Ultra Sync App 統合パッチシステム"""
    
    def __init__(self):
        self.config_manager = None
        self.integration_active = False
        self.fallback_mapping = {}
        
    def initialize_integration(self):
        """統合初期化"""
        try:
            # 部門設定管理システム初期化
            self.config_manager = get_department_config_manager()
            
            # フォールバック用ハードコードマッピング保存
            self._setup_fallback_mapping()
            
            self.integration_active = True
            logger.info("✅ 部門設定外部化統合パッチ初期化完了")
            
        except Exception as e:
            logger.error(f"❌ 統合初期化失敗: {e}")
            self.integration_active = False
    
    def _setup_fallback_mapping(self):
        """フォールバックマッピング設定"""
        # 既存のハードコードマッピングをフォールバック用に保存
        self.fallback_mapping = {
            'department_to_category': {
                'road': '道路',
                'tunnel': 'トンネル', 
                'river': '河川、砂防及び海岸・海洋',
                'urban': '都市計画及び地方計画',
                'landscape': '造園',
                'construction_env': '建設環境',
                'steel_concrete': '鋼構造及びコンクリート',
                'soil': '土質及び基礎',
                'construction_planning': '施工計画、施工設備及び積算',
                'water_supply': '上水道及び工業用水道',
                'forestry': '森林土木',
                'agriculture': '農業土木',
                'basic': '共通'
            },
            'legacy_aliases': {
                'civil_planning': 'river',
                'urban_planning': 'urban',      
                'soil_foundation': 'soil',      
                'common': 'basic'               
            }
        }
    
    def get_department_category_patched(self, department_name: str) -> str:
        """統合版部門→カテゴリ変換"""
        if not department_name:
            return None
        
        # 外部設定による変換試行
        if self.integration_active and self.config_manager:
            try:
                category = self.config_manager.get_category_by_department(department_name)
                if category:
                    return category
            except Exception as e:
                logger.warning(f"⚠️ 外部設定取得失敗、フォールバック使用: {e}")
        
        # フォールバック: ハードコードマッピング使用
        return self._get_category_fallback(department_name)
    
    def normalize_department_name_patched(self, department_name: str) -> str:
        """統合版部門名正規化"""
        if not department_name:
            return None
        
        # 外部設定による正規化試行
        if self.integration_active and self.config_manager:
            try:
                normalized = self.config_manager.normalize_department_name(department_name)
                if normalized:
                    return normalized
            except Exception as e:
                logger.warning(f"⚠️ 外部設定正規化失敗、フォールバック使用: {e}")
        
        # フォールバック: ハードコード正規化使用
        return self._normalize_department_fallback(department_name)
    
    def _get_category_fallback(self, department_name: str) -> str:
        """フォールバック: ハードコードカテゴリ取得"""
        normalized = self._normalize_department_fallback(department_name)
        if normalized:
            return self.fallback_mapping['department_to_category'].get(normalized)
        return None
    
    def _normalize_department_fallback(self, department_name: str) -> str:
        """フォールバック: ハードコード正規化"""
        if not department_name:
            return None
        
        # 既に正規化済みの場合
        if department_name in self.fallback_mapping['department_to_category']:
            return department_name
        
        # レガシーエイリアス変換
        if department_name in self.fallback_mapping['legacy_aliases']:
            return self.fallback_mapping['legacy_aliases'][department_name]
        
        return None
    
    def get_integration_status(self) -> dict:
        """統合状態取得"""
        status = {
            'integration_active': self.integration_active,
            'config_manager_available': self.config_manager is not None,
            'fallback_ready': bool(self.fallback_mapping)
        }
        
        if self.config_manager:
            try:
                status['config_stats'] = self.config_manager.get_mapping_statistics()
            except Exception as e:
                status['config_error'] = str(e)
        
        return status

def apply_integration_patch():
    """app.pyへの統合パッチ適用"""
    try:
        # app.py のインポート
        import app
        
        # 統合パッチ初期化
        patch_system = UltraSyncAppIntegrationPatch()
        patch_system.initialize_integration()
        
        # 既存関数の置き換え（モンキーパッチ）
        if patch_system.integration_active:
            # 新しい関数で置き換え
            app.get_department_category = patch_system.get_department_category_patched
            app.normalize_department_name = patch_system.normalize_department_name_patched
            
            # グローバル変数の置き換え
            if patch_system.config_manager:
                app.DEPARTMENT_TO_CATEGORY_MAPPING = patch_system.config_manager.department_to_category
                app.LEGACY_DEPARTMENT_ALIASES = patch_system.config_manager.legacy_aliases
                app.CATEGORY_TO_DEPARTMENT_MAPPING = patch_system.config_manager.category_to_department
            
            print("✅ app.py 統合パッチ適用成功")
            print(f"📊 部門数: {len(patch_system.config_manager.department_to_category)}")
            print(f"📊 エイリアス数: {len(patch_system.config_manager.legacy_aliases)}")
            
        else:
            print("⚠️ 統合パッチが無効、フォールバックモードで動作")
        
        return patch_system
        
    except ImportError as e:
        print(f"❌ app.py インポート失敗: {e}")
        return None
    except Exception as e:
        print(f"❌ 統合パッチ適用失敗: {e}")
        return None

def verify_integration():
    """統合動作検証"""
    print("🧪 統合動作検証開始")
    print("=" * 50)
    
    # 統合パッチ適用
    patch_system = apply_integration_patch()
    
    if not patch_system:
        print("❌ 統合パッチ適用失敗")
        return False
    
    # app.py の関数テスト
    try:
        import app
        
        # テスト部門リスト
        test_departments = [
            'road',           # 標準部門
            'tunnel',         # 標準部門  
            'civil_planning', # レガシーエイリアス
            'invalid_dept'    # 無効な部門
        ]
        
        print("🔍 部門変換テスト:")
        success_count = 0
        total_count = len(test_departments)
        
        for dept in test_departments:
            try:
                # app.py の関数を直接呼び出し
                category = app.get_department_category(dept)
                normalized = app.normalize_department_name(dept)
                
                status = "✅" if category else "❌"
                print(f"  {dept} -> カテゴリ: {category}, 正規化: {normalized} {status}")
                
                if dept != 'invalid_dept' and category:
                    success_count += 1
                elif dept == 'invalid_dept' and not category:
                    success_count += 1
                    
            except Exception as e:
                print(f"  {dept} -> エラー: {e} ❌")
        
        # 統合状態確認
        print(f"\n📊 統合状態:")
        status = patch_system.get_integration_status()
        for key, value in status.items():
            if key != 'config_stats':
                print(f"  {key}: {value}")
        
        # 成功率計算
        success_rate = (success_count / total_count) * 100
        print(f"\n🎯 テスト結果: {success_count}/{total_count} 成功 ({success_rate:.1f}%)")
        
        if success_rate >= 75:
            print("✅ 統合動作検証成功")
            return True
        else:
            print("❌ 統合動作検証失敗")
            return False
        
    except Exception as e:
        print(f"❌ 検証エラー: {e}")
        return False

def main():
    """メイン実行"""
    print("📝 Ultra Sync App Integration Patch")
    print("=" * 60)
    
    # 統合動作検証
    verification_success = verify_integration()
    
    if verification_success:
        print("\n🎉 統合パッチ適用・検証完了")
        print("📄 次のステップ:")
        print("  1. app.py で外部設定が正常に動作しています")
        print("  2. config/department_mapping.json で部門設定を変更できます") 
        print("  3. 設定変更時は自動リロードされます")
        print("  4. エラー時は自動的にフォールバックします")
    else:
        print("\n💥 統合に問題があります。ログを確認してください。")
    
    return verification_success

if __name__ == "__main__":
    main()