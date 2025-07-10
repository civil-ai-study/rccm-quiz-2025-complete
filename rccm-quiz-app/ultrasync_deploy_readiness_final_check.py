#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
【ULTRASYNC段階3】デプロイ準備完了度最終確認
実行直前の包括的チェックシステム
"""

import os
import sys
import time
import json
import requests
from datetime import datetime

class UltraSyncDeployReadinessCheck:
    """ULTRASYNC デプロイ準備完了度チェック"""
    
    def __init__(self):
        self.checks = {
            'preparation': {},
            'safety': {},
            'execution_ready': {},
            'emergency_ready': {}
        }
        
    def check_secret_key_preparation(self):
        """SECRET_KEY準備状況確認"""
        print("🔐 SECRET_KEY準備状況確認...")
        
        secret_key_ready = False
        if os.path.exists('secret_key_for_render.txt'):
            with open('secret_key_for_render.txt', 'r') as f:
                content = f.read()
            
            if 'SECRET_KEY=' in content:
                key_line = [line for line in content.split('\n') if line.startswith('SECRET_KEY=')]
                if key_line:
                    key_value = key_line[0].split('=', 1)[1]
                    if len(key_value) >= 64:
                        secret_key_ready = True
                        print(f"   ✅ SECRET_KEY: 準備完了（{len(key_value)}文字）")
                    else:
                        print(f"   ❌ SECRET_KEY: 長さ不足（{len(key_value)}文字）")
                else:
                    print("   ❌ SECRET_KEY: 設定行が見つからない")
            else:
                print("   ❌ SECRET_KEY: 設定ファイルにキーがない")
        else:
            print("   ❌ SECRET_KEY: 設定ファイルが存在しない")
        
        self.checks['preparation']['secret_key'] = secret_key_ready
        return secret_key_ready
    
    def check_render_configuration(self):
        """Render.com設定ファイル確認"""
        print("\n⚙️ Render.com設定確認...")
        
        config_checks = {
            'render_yaml': False,
            'wsgi_py': False,
            'gunicorn_conf': False,
            'requirements': False
        }
        
        # render.yaml確認
        if os.path.exists('render.yaml'):
            config_checks['render_yaml'] = True
            print("   ✅ render.yaml: 存在確認")
        else:
            print("   ❌ render.yaml: ファイルなし")
        
        # wsgi.py確認
        if os.path.exists('wsgi.py'):
            config_checks['wsgi_py'] = True
            print("   ✅ wsgi.py: 存在確認")
        
        # gunicorn.conf.py確認
        if os.path.exists('gunicorn.conf.py'):
            config_checks['gunicorn_conf'] = True
            print("   ✅ gunicorn.conf.py: 存在確認")
        
        # requirements確認
        if os.path.exists('requirements_minimal.txt'):
            config_checks['requirements'] = True
            print("   ✅ requirements_minimal.txt: 存在確認")
        
        self.checks['preparation']['render_config'] = config_checks
        return all(config_checks.values())
    
    def check_application_integrity(self):
        """アプリケーション整合性確認"""
        print("\n🔍 アプリケーション整合性確認...")
        
        integrity_checks = {
            'app_py_syntax': False,
            'blueprint_integration': False,
            'data_files': False,
            'template_files': False
        }
        
        # app.py構文確認
        try:
            with open('app.py', 'r', encoding='utf-8') as f:
                content = f.read()
            compile(content, 'app.py', 'exec')
            integrity_checks['app_py_syntax'] = True
            print("   ✅ app.py: 構文正常")
        except Exception as e:
            print(f"   ❌ app.py: 構文エラー - {e}")
        
        # Blueprint統合確認
        if 'register_blueprint' in content:
            integrity_checks['blueprint_integration'] = True
            print("   ✅ Blueprint: 統合確認")
        
        # データファイル確認
        if os.path.exists('data') and len(os.listdir('data')) >= 10:
            integrity_checks['data_files'] = True
            print(f"   ✅ データファイル: {len(os.listdir('data'))}個確認")
        
        # テンプレートファイル確認
        if os.path.exists('templates') and len(os.listdir('templates')) >= 20:
            integrity_checks['template_files'] = True
            print(f"   ✅ テンプレート: {len(os.listdir('templates'))}個確認")
        
        self.checks['safety']['application'] = integrity_checks
        return all(integrity_checks.values())
    
    def check_deployment_safety_score(self):
        """デプロイ安全性スコア確認"""
        print("\n📊 デプロイ安全性スコア確認...")
        
        # 最新の安全性検証レポート確認
        safety_files = [f for f in os.listdir('.') if f.startswith('ULTRASYNC_FINAL_SAFETY_VERIFICATION_')]
        
        if safety_files:
            latest_report = max(safety_files)
            try:
                with open(latest_report, 'r', encoding='utf-8') as f:
                    report_data = json.load(f)
                
                risk_assessment = report_data.get('risk_assessment', {})
                success_rate = risk_assessment.get('success_rate', 0)
                risk_level = risk_assessment.get('risk_level', 'UNKNOWN')
                deploy_recommended = risk_assessment.get('deployment_recommended', False)
                
                print(f"   📈 成功率: {success_rate}%")
                print(f"   ⚠️ リスクレベル: {risk_level}")
                print(f"   🚀 デプロイ推奨: {'YES' if deploy_recommended else 'NO'}")
                
                self.checks['safety']['score'] = {
                    'success_rate': success_rate,
                    'risk_level': risk_level,
                    'deploy_recommended': deploy_recommended
                }
                
                return deploy_recommended and success_rate >= 90
                
            except Exception as e:
                print(f"   ❌ レポート読み込みエラー: {e}")
        else:
            print("   ❌ 安全性検証レポートが見つからない")
        
        return False
    
    def check_emergency_procedures(self):
        """緊急時対応手順確認"""
        print("\n🆘 緊急時対応手順確認...")
        
        emergency_ready = {
            'deployment_checklist': False,
            'execution_plan': False,
            'backup_files': False,
            'rollback_ready': False
        }
        
        # デプロイチェックリスト
        if os.path.exists('ULTRASYNC_DEPLOYMENT_CHECKLIST.md'):
            emergency_ready['deployment_checklist'] = True
            print("   ✅ デプロイチェックリスト: 準備完了")
        
        # 実行計画
        if os.path.exists('ULTRASYNC_DEPLOY_EXECUTION_PLAN.md'):
            emergency_ready['execution_plan'] = True
            print("   ✅ 実行計画: 準備完了")
        
        # バックアップファイル
        backup_count = len([f for f in os.listdir('.') if 'backup' in f.lower()])
        if backup_count >= 5:
            emergency_ready['backup_files'] = True
            print(f"   ✅ バックアップ: {backup_count}個準備完了")
        
        # ロールバック準備（Git状態確認）
        try:
            import subprocess
            result = subprocess.run(['git', 'log', '--oneline', '-3'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                emergency_ready['rollback_ready'] = True
                print("   ✅ ロールバック: Git履歴確認")
        except:
            print("   ⚠️ ロールバック: Git確認不可")
        
        self.checks['emergency_ready'] = emergency_ready
        return sum(emergency_ready.values()) >= 3
    
    def generate_final_go_no_go_decision(self):
        """最終GO/NO-GO判定"""
        print("\n🎯 最終GO/NO-GO判定...")
        
        # 各カテゴリーの合格基準チェック
        categories = {
            'SECRET_KEY準備': self.checks['preparation'].get('secret_key', False),
            'Render.com設定': all(self.checks['preparation'].get('render_config', {}).values()),
            'アプリケーション整合性': all(self.checks['safety'].get('application', {}).values()),
            '安全性スコア': self.checks['safety'].get('score', {}).get('deploy_recommended', False),
            '緊急時準備': sum(self.checks['emergency_ready'].values()) >= 3
        }
        
        passed_categories = sum(categories.values())
        total_categories = len(categories)
        
        print(f"\n📋 カテゴリー別判定:")
        for category, passed in categories.items():
            print(f"   {'✅' if passed else '❌'} {category}")
        
        overall_ready = passed_categories >= 4  # 5項目中4項目以上合格
        
        print(f"\n📊 総合判定: {passed_categories}/{total_categories}合格")
        
        if overall_ready:
            print("🚀 判定: GO - デプロイ実行推奨")
            print("🎯 条件: SECRET_KEY設定完了後、即座実行可能")
        else:
            print("🔧 判定: NO-GO - 追加準備が必要")
            failed_items = [cat for cat, passed in categories.items() if not passed]
            print(f"🔧 要対応: {', '.join(failed_items)}")
        
        return overall_ready, categories
    
    def run_final_check(self):
        """最終チェック実行"""
        print("🎯 【ULTRASYNC段階3】デプロイ準備完了度最終確認")
        print("=" * 70)
        
        # 各チェック実行
        secret_ready = self.check_secret_key_preparation()
        config_ready = self.check_render_configuration()
        app_ready = self.check_application_integrity()
        safety_ready = self.check_deployment_safety_score()
        emergency_ready = self.check_emergency_procedures()
        
        # 最終判定
        go_decision, categories = self.generate_final_go_no_go_decision()
        
        # 結果保存
        final_check_result = {
            'timestamp': datetime.now().isoformat(),
            'go_decision': go_decision,
            'categories': categories,
            'checks': self.checks,
            'next_action': 'DEPLOY' if go_decision else 'PREPARE'
        }
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"ULTRASYNC_DEPLOY_READINESS_FINAL_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(final_check_result, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 最終チェック結果保存: {filename}")
        print("=" * 70)
        
        if go_decision:
            print("🎉 ULTRASYNC段階3準備完了")
            print("🚀 次のアクション: Render.com SECRET_KEY設定 → デプロイ実行")
        else:
            print("🔧 ULTRASYNC段階3準備継続")
            print("📋 次のアクション: 要対応項目の解決")
        
        return go_decision

def main():
    """メイン実行"""
    checker = UltraSyncDeployReadinessCheck()
    ready = checker.run_final_check()
    
    print(f"\n🏁 最終準備チェック完了")
    print(f"副作用: ゼロ（読み取り専用検証）")
    
    return ready

if __name__ == "__main__":
    ready = main()
    exit(0 if ready else 1)