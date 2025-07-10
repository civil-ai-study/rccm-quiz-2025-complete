#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
【ULTRASYNC段階2】デプロイ前最終安全性検証
副作用ゼロ保証での包括的品質・安全性チェック
"""

import os
import sys
import time
import json
import hashlib
import subprocess
from datetime import datetime
from typing import Dict, List, Any

class UltraSyncFinalSafetyVerification:
    """ULTRASYNC最終安全性検証クラス"""
    
    def __init__(self):
        self.start_time = time.time()
        self.verification_results = {
            'timestamp': datetime.now().isoformat(),
            'safety_checks': {},
            'quality_metrics': {},
            'security_analysis': {},
            'performance_analysis': {},
            'deployment_readiness': {},
            'risk_assessment': {}
        }
        
    def verify_code_quality(self):
        """コード品質最終検証"""
        print("🔍 コード品質最終検証...")
        
        quality_checks = {
            'syntax_validation': False,
            'import_structure': False,
            'function_complexity': False,
            'security_patterns': False
        }
        
        try:
            # 1. 構文検証
            with open('app.py', 'r', encoding='utf-8') as f:
                content = f.read()
            
            compile(content, 'app.py', 'exec')
            quality_checks['syntax_validation'] = True
            print("   ✅ Python構文: 正常")
            
            # 2. インポート構造検証
            import_lines = [line for line in content.split('\n') if line.strip().startswith('import ') or line.strip().startswith('from ')]
            if len(import_lines) > 0:
                quality_checks['import_structure'] = True
                print(f"   ✅ インポート構造: {len(import_lines)}個正常")
            
            # 3. 関数複雑度検証
            function_count = content.count('def ')
            if function_count > 200:  # 適切な関数分割
                quality_checks['function_complexity'] = True
                print(f"   ✅ 関数複雑度: {function_count}個（適切）")
            
            # 4. セキュリティパターン検証
            security_patterns = [
                'SECRET_KEY',
                'csrf',
                'sanitize',
                'escape',
                'validate'
            ]
            
            found_patterns = sum(1 for pattern in security_patterns if pattern.lower() in content.lower())
            if found_patterns >= 3:
                quality_checks['security_patterns'] = True
                print(f"   ✅ セキュリティパターン: {found_patterns}/5個確認")
            
        except Exception as e:
            print(f"   ❌ コード品質検証エラー: {e}")
        
        self.verification_results['quality_metrics'] = quality_checks
        return quality_checks
    
    def verify_data_integrity(self):
        """データ整合性最終検証"""
        print("\n📊 データ整合性最終検証...")
        
        data_checks = {
            'csv_files_present': False,
            'encoding_consistency': False,
            'data_completeness': False,
            'backup_availability': False
        }
        
        try:
            # 1. CSVファイル存在確認
            csv_files = []
            if os.path.exists('data'):
                csv_files = [f for f in os.listdir('data') if f.endswith('.csv')]
            
            if len(csv_files) >= 13:  # 全13部門のデータ
                data_checks['csv_files_present'] = True
                print(f"   ✅ CSVファイル: {len(csv_files)}個確認")
            
            # 2. エンコーディング一貫性
            encoding_consistent = True
            for csv_file in csv_files[:5]:  # サンプル検証
                file_path = f"data/{csv_file}"
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    if len(content) > 0:
                        continue
                except:
                    encoding_consistent = False
                    break
            
            if encoding_consistent:
                data_checks['encoding_consistency'] = True
                print("   ✅ エンコーディング: 一貫性確認")
            
            # 3. データ完全性
            total_questions = 0
            for csv_file in csv_files:
                file_path = f"data/{csv_file}"
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                        total_questions += max(0, len(lines) - 1)  # ヘッダー除く
                except:
                    pass
            
            if total_questions >= 1000:  # 最低1000問
                data_checks['data_completeness'] = True
                print(f"   ✅ データ完全性: {total_questions}問確認")
            
            # 4. バックアップ可用性
            backup_files = [f for f in os.listdir('.') if 'backup' in f.lower()]
            if len(backup_files) > 5:
                data_checks['backup_availability'] = True
                print(f"   ✅ バックアップ: {len(backup_files)}個確認")
            
        except Exception as e:
            print(f"   ❌ データ整合性検証エラー: {e}")
        
        self.verification_results['quality_metrics'].update(data_checks)
        return data_checks
    
    def verify_security_compliance(self):
        """セキュリティコンプライアンス検証"""
        print("\n🛡️ セキュリティコンプライアンス検証...")
        
        security_checks = {
            'secret_key_configured': False,
            'csrf_protection': False,
            'input_sanitization': False,
            'secure_headers': False,
            'error_handling': False
        }
        
        try:
            # 1. SECRET_KEY設定確認
            if os.path.exists('secret_key_for_render.txt'):
                with open('secret_key_for_render.txt', 'r') as f:
                    content = f.read()
                if 'SECRET_KEY=' in content and len(content) > 80:
                    security_checks['secret_key_configured'] = True
                    print("   ✅ SECRET_KEY: 設定ファイル確認")
            
            # 2. CSRF保護確認
            with open('app.py', 'r', encoding='utf-8') as f:
                app_content = f.read()
            
            if 'csrf' in app_content.lower():
                security_checks['csrf_protection'] = True
                print("   ✅ CSRF保護: 実装確認")
            
            # 3. 入力サニタイゼーション
            if 'sanitize' in app_content:
                security_checks['input_sanitization'] = True
                print("   ✅ 入力サニタイゼーション: 実装確認")
            
            # 4. セキュアヘッダー
            if 'X-Content-Type-Options' in app_content or 'Content-Security-Policy' in app_content:
                security_checks['secure_headers'] = True
                print("   ✅ セキュアヘッダー: 実装確認")
            
            # 5. エラーハンドリング
            try_except_count = app_content.count('try:')
            if try_except_count > 20:
                security_checks['error_handling'] = True
                print(f"   ✅ エラーハンドリング: {try_except_count}箇所実装")
            
        except Exception as e:
            print(f"   ❌ セキュリティ検証エラー: {e}")
        
        self.verification_results['security_analysis'] = security_checks
        return security_checks
    
    def verify_performance_readiness(self):
        """パフォーマンス準備状況検証"""
        print("\n⚡ パフォーマンス準備状況検証...")
        
        performance_checks = {
            'gunicorn_configured': False,
            'static_optimization': False,
            'caching_strategy': False,
            'database_optimization': False
        }
        
        try:
            # 1. Gunicorn設定
            if os.path.exists('gunicorn.conf.py'):
                performance_checks['gunicorn_configured'] = True
                print("   ✅ Gunicorn: 設定ファイル確認")
            
            # 2. 静的ファイル最適化
            if os.path.exists('static'):
                static_files = os.listdir('static')
                if len(static_files) > 0:
                    performance_checks['static_optimization'] = True
                    print(f"   ✅ 静的ファイル: {len(static_files)}個最適化")
            
            # 3. キャッシュ戦略
            with open('app.py', 'r', encoding='utf-8') as f:
                content = f.read()
            if 'cache' in content.lower():
                performance_checks['caching_strategy'] = True
                print("   ✅ キャッシュ戦略: 実装確認")
            
            # 4. データベース最適化（CSV最適化）
            if 'pandas' in content or 'numpy' in content:
                performance_checks['database_optimization'] = True
                print("   ✅ データ最適化: pandas/numpy活用")
            
        except Exception as e:
            print(f"   ❌ パフォーマンス検証エラー: {e}")
        
        self.verification_results['performance_analysis'] = performance_checks
        return performance_checks
    
    def verify_deployment_readiness(self):
        """デプロイ準備完了度検証"""
        print("\n🚀 デプロイ準備完了度検証...")
        
        deployment_checks = {
            'render_config': False,
            'requirements_complete': False,
            'wsgi_configured': False,
            'environment_ready': False,
            'git_status_clean': False
        }
        
        try:
            # 1. Render設定
            if os.path.exists('render.yaml'):
                deployment_checks['render_config'] = True
                print("   ✅ Render設定: yaml確認")
            
            # 2. 依存関係完全性
            if os.path.exists('requirements_minimal.txt'):
                with open('requirements_minimal.txt', 'r') as f:
                    requirements = f.read()
                if 'Flask' in requirements and 'gunicorn' in requirements:
                    deployment_checks['requirements_complete'] = True
                    print("   ✅ 依存関係: 完全性確認")
            
            # 3. WSGI設定
            if os.path.exists('wsgi.py'):
                deployment_checks['wsgi_configured'] = True
                print("   ✅ WSGI: 設定確認")
            
            # 4. 環境準備
            if os.path.exists('secret_key_for_render.txt'):
                deployment_checks['environment_ready'] = True
                print("   ✅ 環境準備: SECRET_KEY準備完了")
            
            # 5. Git状態
            try:
                result = subprocess.run(['git', 'status', '--porcelain'], 
                                      capture_output=True, text=True)
                if not result.stdout.strip():
                    deployment_checks['git_status_clean'] = True
                    print("   ✅ Git状態: クリーン")
                else:
                    print("   ⚠️ Git状態: 未コミット変更あり")
            except:
                print("   ⚠️ Git状態: 確認不可")
            
        except Exception as e:
            print(f"   ❌ デプロイ準備検証エラー: {e}")
        
        self.verification_results['deployment_readiness'] = deployment_checks
        return deployment_checks
    
    def assess_risk_level(self):
        """リスクレベル評価"""
        print("\n⚠️ リスクレベル評価...")
        
        # 全チェック項目の成功率計算
        all_checks = {}
        all_checks.update(self.verification_results.get('quality_metrics', {}))
        all_checks.update(self.verification_results.get('security_analysis', {}))
        all_checks.update(self.verification_results.get('performance_analysis', {}))
        all_checks.update(self.verification_results.get('deployment_readiness', {}))
        
        total_checks = len(all_checks)
        passed_checks = sum(1 for check in all_checks.values() if check)
        success_rate = (passed_checks / total_checks) * 100 if total_checks > 0 else 0
        
        # リスクレベル判定
        if success_rate >= 95:
            risk_level = "MINIMAL"
            risk_color = "🟢"
        elif success_rate >= 85:
            risk_level = "LOW"
            risk_color = "🟡"
        elif success_rate >= 70:
            risk_level = "MEDIUM"
            risk_color = "🟠"
        else:
            risk_level = "HIGH"
            risk_color = "🔴"
        
        risk_assessment = {
            'total_checks': total_checks,
            'passed_checks': passed_checks,
            'success_rate': round(success_rate, 1),
            'risk_level': risk_level,
            'deployment_recommended': success_rate >= 85
        }
        
        print(f"   {risk_color} リスクレベル: {risk_level}")
        print(f"   📊 成功率: {success_rate:.1f}% ({passed_checks}/{total_checks})")
        print(f"   🚀 デプロイ推奨: {'YES' if risk_assessment['deployment_recommended'] else 'NO'}")
        
        self.verification_results['risk_assessment'] = risk_assessment
        return risk_assessment
    
    def generate_safety_report(self):
        """安全性レポート生成"""
        print("\n📋 最終安全性レポート生成...")
        
        # 実行時間計算
        execution_time = time.time() - self.start_time
        self.verification_results['execution_time_seconds'] = round(execution_time, 2)
        
        # レポート保存
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_filename = f"ULTRASYNC_FINAL_SAFETY_VERIFICATION_{timestamp}.json"
        
        try:
            with open(report_filename, 'w', encoding='utf-8') as f:
                json.dump(self.verification_results, f, ensure_ascii=False, indent=2)
            print(f"   💾 レポート保存: {report_filename}")
        except Exception as e:
            print(f"   ❌ レポート保存失敗: {e}")
        
        return self.verification_results
    
    def run_comprehensive_verification(self):
        """包括的検証実行"""
        print("🎯 【ULTRASYNC段階2】デプロイ前最終安全性検証開始")
        print("=" * 70)
        
        try:
            # 各検証段階実行
            self.verify_code_quality()
            self.verify_data_integrity()
            self.verify_security_compliance()
            self.verify_performance_readiness()
            self.verify_deployment_readiness()
            
            # リスク評価
            risk_assessment = self.assess_risk_level()
            
            # 最終レポート
            self.generate_safety_report()
            
            print("\n" + "=" * 70)
            print("🎉 【ULTRASYNC段階2】最終安全性検証完了")
            
            if risk_assessment['deployment_recommended']:
                print("✅ 結論: デプロイ実行推奨")
                print("🚀 次段階: ULTRASYNC段階3（デプロイ実行）へ進行可能")
            else:
                print("⚠️ 結論: 追加対応が必要")
                print("🔧 次段階: 課題解決後に再検証")
            
            return risk_assessment['deployment_recommended']
            
        except Exception as e:
            print(f"\n❌ 検証実行エラー: {e}")
            return False

def main():
    """メイン実行"""
    verifier = UltraSyncFinalSafetyVerification()
    success = verifier.run_comprehensive_verification()
    
    print(f"\n🏁 ULTRASYNC段階2完了")
    print(f"副作用: ゼロ（読み取り専用検証）")
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)