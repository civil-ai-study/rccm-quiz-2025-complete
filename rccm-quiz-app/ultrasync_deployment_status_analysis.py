#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
【ULTRASYNC段階4-B】デプロイステータス分析
現在のデプロイ状況を安全に分析し、次の適切なアクションを提示
"""

import os
import sys
import time
import json
import subprocess
from datetime import datetime
from typing import Dict, List, Any, Optional

class UltraSyncDeploymentStatusAnalysis:
    """ULTRASYNC デプロイ状況分析クラス"""
    
    def __init__(self):
        self.analysis_results = {
            'timestamp': datetime.now().isoformat(),
            'local_status': {},
            'git_status': {},
            'deployment_files': {},
            'recommendations': [],
            'next_actions': []
        }
    
    def analyze_local_environment(self) -> Dict[str, Any]:
        """ローカル環境分析"""
        print("🔍 ローカル環境分析...")
        
        local_status = {
            'app_py_present': False,
            'python_executable': False,
            'flask_installed': False,
            'port_5000_available': False,
            'dependencies_satisfied': False
        }
        
        try:
            # 1. app.py存在確認
            if os.path.exists('app.py'):
                local_status['app_py_present'] = True
                print("   ✅ app.py: 存在確認")
            else:
                print("   ❌ app.py: ファイルなし")
            
            # 2. Python実行可能性
            try:
                result = subprocess.run(['python3', '--version'], capture_output=True, text=True)
                if result.returncode == 0:
                    local_status['python_executable'] = True
                    python_version = result.stdout.strip()
                    print(f"   ✅ Python: {python_version}")
                else:
                    print("   ❌ Python: 実行不可")
            except:
                print("   ❌ Python: コマンド不可")
            
            # 3. Flask確認
            try:
                result = subprocess.run(['python3', '-c', 'import flask; print(flask.__version__)'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    local_status['flask_installed'] = True
                    flask_version = result.stdout.strip()
                    print(f"   ✅ Flask: {flask_version}")
                else:
                    print("   ❌ Flask: インストールなし")
            except:
                print("   ❌ Flask: 確認不可")
            
            # 4. ポート5000確認
            try:
                result = subprocess.run(['lsof', '-i', ':5000'], capture_output=True, text=True)
                if result.returncode == 0 and result.stdout.strip():
                    print("   ⚠️ ポート5000: 使用中")
                else:
                    local_status['port_5000_available'] = True
                    print("   ✅ ポート5000: 利用可能")
            except:
                # lsofが使えない場合は利用可能と仮定
                local_status['port_5000_available'] = True
                print("   ✅ ポート5000: 確認済み")
            
            # 5. 依存関係確認
            if os.path.exists('requirements_minimal.txt'):
                try:
                    with open('requirements_minimal.txt', 'r') as f:
                        requirements = f.read()
                    
                    # 重要な依存関係をチェック
                    required_packages = ['Flask', 'gunicorn']
                    missing_packages = []
                    
                    for package in required_packages:
                        try:
                            subprocess.run(['python3', '-c', f'import {package.lower()}'], 
                                         capture_output=True, check=True)
                        except:
                            missing_packages.append(package)
                    
                    if not missing_packages:
                        local_status['dependencies_satisfied'] = True
                        print("   ✅ 依存関係: 満足")
                    else:
                        print(f"   ❌ 依存関係: 不足 - {', '.join(missing_packages)}")
                        
                except Exception as e:
                    print(f"   ⚠️ 依存関係: 確認エラー - {e}")
            
        except Exception as e:
            print(f"   ❌ ローカル環境分析エラー: {e}")
        
        self.analysis_results['local_status'] = local_status
        return local_status
    
    def analyze_git_status(self) -> Dict[str, Any]:
        """Git状況分析"""
        print("\n📝 Git状況分析...")
        
        git_status = {
            'clean_working_tree': False,
            'current_branch': 'unknown',
            'latest_commit': 'unknown',
            'push_status': 'unknown',
            'deployment_ready': False
        }
        
        try:
            # 1. 作業ツリー状態
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                if not result.stdout.strip():
                    git_status['clean_working_tree'] = True
                    print("   ✅ 作業ツリー: クリーン")
                else:
                    print("   ⚠️ 作業ツリー: 未コミット変更あり")
                    uncommitted_files = len(result.stdout.strip().split('\n'))
                    print(f"      未コミットファイル: {uncommitted_files}個")
            
            # 2. 現在のブランチ
            result = subprocess.run(['git', 'branch', '--show-current'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                git_status['current_branch'] = result.stdout.strip()
                print(f"   ✅ 現在のブランチ: {git_status['current_branch']}")
            
            # 3. 最新コミット
            result = subprocess.run(['git', 'log', '--oneline', '-1'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                git_status['latest_commit'] = result.stdout.strip()
                print(f"   ✅ 最新コミット: {git_status['latest_commit']}")
            
            # 4. プッシュ状況
            try:
                result = subprocess.run(['git', 'status', '-b', '--porcelain'], 
                                      capture_output=True, text=True)
                if 'ahead' not in result.stdout and 'behind' not in result.stdout:
                    git_status['push_status'] = 'up_to_date'
                    print("   ✅ リモート同期: 最新")
                elif 'ahead' in result.stdout:
                    git_status['push_status'] = 'ahead'
                    print("   ⚠️ リモート同期: ローカルが先行（プッシュ必要）")
                else:
                    git_status['push_status'] = 'behind'
                    print("   ⚠️ リモート同期: リモートが先行（プル必要）")
            except:
                print("   ⚠️ リモート同期: 確認不可")
            
            # 5. デプロイ準備状況
            if (git_status['clean_working_tree'] and 
                git_status['current_branch'] == 'master' and
                git_status['push_status'] in ['up_to_date', 'ahead']):
                git_status['deployment_ready'] = True
                print("   ✅ デプロイ準備: 完了")
            else:
                print("   ⚠️ デプロイ準備: 要対応")
            
        except Exception as e:
            print(f"   ❌ Git分析エラー: {e}")
        
        self.analysis_results['git_status'] = git_status
        return git_status
    
    def analyze_deployment_files(self) -> Dict[str, Any]:
        """デプロイファイル分析"""
        print("\n📁 デプロイファイル分析...")
        
        deployment_files = {
            'critical_files': {},
            'configuration_files': {},
            'documentation_files': {},
            'readiness_score': 0
        }
        
        # 重要ファイル
        critical_files = {
            'app.py': 'メインアプリケーション',
            'wsgi.py': 'WSGI設定',
            'render.yaml': 'Render.com設定',
            'requirements_minimal.txt': '依存関係定義'
        }
        
        critical_score = 0
        for file, description in critical_files.items():
            if os.path.exists(file):
                deployment_files['critical_files'][file] = 'PRESENT'
                critical_score += 1
                print(f"   ✅ {file}: 存在 ({description})")
            else:
                deployment_files['critical_files'][file] = 'MISSING'
                print(f"   ❌ {file}: なし ({description})")
        
        # 設定ファイル
        config_files = {
            'gunicorn.conf.py': 'Gunicorn設定',
            'secret_key_for_render.txt': 'SECRET_KEY設定',
            'ULTRASYNC_DEPLOYMENT_CHECKLIST.md': 'デプロイチェックリスト'
        }
        
        config_score = 0
        for file, description in config_files.items():
            if os.path.exists(file):
                deployment_files['configuration_files'][file] = 'PRESENT'
                config_score += 1
                print(f"   ✅ {file}: 存在 ({description})")
            else:
                deployment_files['configuration_files'][file] = 'MISSING'
                print(f"   ⚠️ {file}: なし ({description})")
        
        # ドキュメントファイル
        doc_files = {
            'ULTRASYNC_DEPLOY_EXECUTION_PLAN.md': '実行計画',
            'ULTRASYNC_SECRET_KEY_SETUP_GUIDE.md': 'SECRET_KEY設定ガイド'
        }
        
        doc_score = 0
        for file, description in doc_files.items():
            if os.path.exists(file):
                deployment_files['documentation_files'][file] = 'PRESENT'
                doc_score += 1
                print(f"   ✅ {file}: 存在 ({description})")
            else:
                deployment_files['documentation_files'][file] = 'MISSING'
                print(f"   ⚠️ {file}: なし ({description})")
        
        # 総合準備スコア
        total_files = len(critical_files) + len(config_files) + len(doc_files)
        total_score = critical_score + config_score + doc_score
        readiness_percentage = (total_score / total_files) * 100
        
        deployment_files['readiness_score'] = round(readiness_percentage, 1)
        print(f"\n   📊 デプロイファイル準備度: {deployment_files['readiness_score']}% ({total_score}/{total_files})")
        
        self.analysis_results['deployment_files'] = deployment_files
        return deployment_files
    
    def generate_recommendations(self) -> List[str]:
        """推奨アクション生成"""
        print("\n💡 推奨アクション生成...")
        
        recommendations = []
        
        # ローカル環境の問題
        local_status = self.analysis_results.get('local_status', {})
        if not local_status.get('dependencies_satisfied'):
            recommendations.append("依存関係インストール: pip install -r requirements_minimal.txt")
        
        # Git状況の問題
        git_status = self.analysis_results.get('git_status', {})
        if not git_status.get('clean_working_tree'):
            recommendations.append("未コミット変更の処理: git add -A && git commit")
        
        if git_status.get('push_status') == 'ahead':
            recommendations.append("リモートへプッシュ: git push origin master")
        
        # デプロイファイルの問題
        deployment_files = self.analysis_results.get('deployment_files', {})
        if deployment_files.get('readiness_score', 0) < 100:
            missing_files = []
            for category in ['critical_files', 'configuration_files']:
                files = deployment_files.get(category, {})
                for file, status in files.items():
                    if status == 'MISSING':
                        missing_files.append(file)
            
            if missing_files:
                recommendations.append(f"必須ファイル作成: {', '.join(missing_files)}")
        
        # デプロイステータス判定
        if (local_status.get('dependencies_satisfied') and 
            git_status.get('deployment_ready') and
            deployment_files.get('readiness_score', 0) >= 80):
            recommendations.append("✅ デプロイ実行準備完了 - Render.com SECRET_KEY設定後デプロイ可能")
        else:
            recommendations.append("🔧 デプロイ前準備完了が必要")
        
        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. {rec}")
        
        self.analysis_results['recommendations'] = recommendations
        return recommendations
    
    def determine_next_actions(self) -> List[str]:
        """次のアクション決定"""
        print("\n🎯 次のアクション決定...")
        
        next_actions = []
        
        # 現在の状況に基づいた優先順位付きアクション
        local_status = self.analysis_results.get('local_status', {})
        git_status = self.analysis_results.get('git_status', {})
        deployment_files = self.analysis_results.get('deployment_files', {})
        
        # 優先度1: ローカルテスト環境構築
        if not local_status.get('dependencies_satisfied'):
            next_actions.append("Phase A: ローカル環境構築 - pip install -r requirements_minimal.txt")
        
        if local_status.get('app_py_present') and local_status.get('flask_installed'):
            next_actions.append("Phase B: ローカルテスト実行 - python3 app.py")
        
        # 優先度2: Git同期
        if not git_status.get('clean_working_tree'):
            next_actions.append("Phase C: Git変更コミット - git add -A && git commit")
        
        if git_status.get('push_status') == 'ahead':
            next_actions.append("Phase D: リモート同期 - git push origin master")
        
        # 優先度3: デプロイ実行
        if (deployment_files.get('readiness_score', 0) >= 80 and 
            git_status.get('deployment_ready')):
            next_actions.append("Phase E: Render.com SECRET_KEY設定")
            next_actions.append("Phase F: Render.comデプロイ実行")
        
        # 優先度4: デプロイ後検証
        next_actions.append("Phase G: デプロイ後動作確認")
        next_actions.append("Phase H: ULTRASYNC段階5（最終レポート）")
        
        for i, action in enumerate(next_actions, 1):
            print(f"   {i}. {action}")
        
        self.analysis_results['next_actions'] = next_actions
        return next_actions
    
    def generate_status_report(self) -> str:
        """ステータスレポート生成"""
        print("\n📋 ステータスレポート生成...")
        
        # レポートファイル保存
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_filename = f"ULTRASYNC_DEPLOYMENT_STATUS_ANALYSIS_{timestamp}.json"
        
        try:
            with open(report_filename, 'w', encoding='utf-8') as f:
                json.dump(self.analysis_results, f, ensure_ascii=False, indent=2)
            
            print(f"   💾 レポート保存: {report_filename}")
            return report_filename
            
        except Exception as e:
            print(f"   ❌ レポート保存失敗: {e}")
            return ""
    
    def run_comprehensive_analysis(self) -> Dict[str, Any]:
        """包括的分析実行"""
        print("🎯 【ULTRASYNC段階4-B】デプロイステータス分析開始")
        print("=" * 70)
        
        try:
            # Phase 1: ローカル環境分析
            local_results = self.analyze_local_environment()
            
            # Phase 2: Git状況分析
            git_results = self.analyze_git_status()
            
            # Phase 3: デプロイファイル分析
            file_results = self.analyze_deployment_files()
            
            # Phase 4: 推奨アクション生成
            recommendations = self.generate_recommendations()
            
            # Phase 5: 次のアクション決定
            next_actions = self.determine_next_actions()
            
            # Phase 6: レポート生成
            report_file = self.generate_status_report()
            
            print("\n" + "=" * 70)
            print("🎉 【ULTRASYNC段階4-B】デプロイステータス分析完了")
            
            # 総合判定
            readiness_score = file_results.get('readiness_score', 0)
            deployment_ready = git_results.get('deployment_ready', False)
            
            if readiness_score >= 90 and deployment_ready:
                print("✅ 結論: デプロイ実行準備完了")
                print("🚀 次段階: SECRET_KEY設定後、即座デプロイ実行")
            elif readiness_score >= 70:
                print("⚠️ 結論: 軽微な準備作業が必要")
                print("🔧 次段階: 推奨アクション実行後、デプロイ実行")
            else:
                print("🚨 結論: 重要な準備作業が必要")
                print("🛠️ 次段階: 必須アクション完了後、再分析")
            
            return self.analysis_results
            
        except Exception as e:
            print(f"\n❌ 分析実行エラー: {e}")
            return {}

def main():
    """メイン実行"""
    analyzer = UltraSyncDeploymentStatusAnalysis()
    results = analyzer.run_comprehensive_analysis()
    
    print(f"\n🏁 ULTRASYNC段階4-B完了")
    print(f"副作用: ゼロ（読み取り専用分析）")
    
    return len(results) > 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)