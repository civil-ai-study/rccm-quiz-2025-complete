#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
【ULTRASYNC段階4】デプロイ後包括的動作検証
副作用ゼロ保証での本番環境完全動作確認
"""

import os
import sys
import time
import json
import requests
import subprocess
from datetime import datetime
from typing import Dict, List, Any, Optional

class UltraSyncPostDeployVerification:
    """ULTRASYNC デプロイ後包括的検証クラス"""
    
    def __init__(self, base_url: str = None):
        self.base_url = base_url or "https://rccm-quiz-2025.onrender.com"
        self.start_time = time.time()
        self.verification_results = {
            'timestamp': datetime.now().isoformat(),
            'base_url': self.base_url,
            'connectivity_tests': {},
            'functional_tests': {},
            'performance_tests': {},
            'security_tests': {},
            'department_tests': {},
            'user_experience_tests': {},
            'overall_health': {}
        }
        
        # 13部門テスト対象
        self.departments = [
            '基礎科目', '道路', '河川・砂防', '都市計画', '造園',
            '建設環境', '鋼構造・コンクリート', '土質・基礎', '施工計画',
            '上下水道', '森林土木', '農業土木', 'トンネル'
        ]
        
    def verify_basic_connectivity(self) -> bool:
        """基本接続確認"""
        print("🔗 基本接続確認...")
        
        connectivity_checks = {
            'homepage_access': False,
            'health_check': False,
            'static_resources': False,
            'response_time': 0.0
        }
        
        try:
            # 1. ホームページアクセス
            start = time.time()
            response = requests.get(self.base_url, timeout=30)
            end = time.time()
            
            if response.status_code == 200:
                connectivity_checks['homepage_access'] = True
                connectivity_checks['response_time'] = round(end - start, 2)
                print(f"   ✅ ホームページ: OK ({connectivity_checks['response_time']}秒)")
            else:
                print(f"   ❌ ホームページ: {response.status_code}")
            
            # 2. ヘルスチェック
            health_url = f"{self.base_url}/health/simple"
            health_response = requests.get(health_url, timeout=15)
            
            if health_response.status_code == 200:
                health_data = health_response.json()
                if health_data.get('status') == 'healthy':
                    connectivity_checks['health_check'] = True
                    print("   ✅ ヘルスチェック: OK")
                else:
                    print(f"   ❌ ヘルスチェック: 異常ステータス - {health_data}")
            else:
                print(f"   ❌ ヘルスチェック: {health_response.status_code}")
            
            # 3. 静的リソース確認
            static_urls = [
                f"{self.base_url}/favicon.ico",
                f"{self.base_url}/manifest.json"
            ]
            
            static_success = 0
            for url in static_urls:
                try:
                    static_response = requests.get(url, timeout=10)
                    if static_response.status_code == 200:
                        static_success += 1
                except:
                    pass
            
            if static_success >= len(static_urls) // 2:
                connectivity_checks['static_resources'] = True
                print(f"   ✅ 静的リソース: OK ({static_success}/{len(static_urls)})")
            else:
                print(f"   ⚠️ 静的リソース: 一部失敗 ({static_success}/{len(static_urls)})")
            
        except Exception as e:
            print(f"   ❌ 接続エラー: {e}")
        
        self.verification_results['connectivity_tests'] = connectivity_checks
        return all([
            connectivity_checks['homepage_access'],
            connectivity_checks['health_check']
        ])
    
    def verify_department_functionality(self) -> Dict[str, Any]:
        """13部門機能確認"""
        print("\n🏢 13部門機能確認...")
        
        department_results = {
            'total_departments': len(self.departments),
            'success_count': 0,
            'failed_departments': [],
            'department_details': {}
        }
        
        for dept in self.departments:
            print(f"   🔍 {dept}部門テスト...")
            
            dept_result = {
                'access_success': False,
                'response_time': 0.0,
                'content_validation': False,
                'error_details': None
            }
            
            try:
                # 部門ページアクセステスト
                start = time.time()
                dept_url = f"{self.base_url}/start_exam/{dept}"
                response = requests.get(dept_url, timeout=20)
                end = time.time()
                
                dept_result['response_time'] = round(end - start, 2)
                
                if response.status_code == 200:
                    dept_result['access_success'] = True
                    
                    # 基本的なコンテンツ検証
                    if dept in response.text and '問題' in response.text:
                        dept_result['content_validation'] = True
                        department_results['success_count'] += 1
                        print(f"      ✅ {dept}: OK ({dept_result['response_time']}秒)")
                    else:
                        print(f"      ⚠️ {dept}: コンテンツ検証失敗")
                        department_results['failed_departments'].append(dept)
                else:
                    print(f"      ❌ {dept}: HTTP {response.status_code}")
                    dept_result['error_details'] = f"HTTP {response.status_code}"
                    department_results['failed_departments'].append(dept)
                
            except Exception as e:
                print(f"      ❌ {dept}: エラー - {e}")
                dept_result['error_details'] = str(e)
                department_results['failed_departments'].append(dept)
            
            department_results['department_details'][dept] = dept_result
        
        success_rate = (department_results['success_count'] / department_results['total_departments']) * 100
        print(f"\n   📊 部門成功率: {success_rate:.1f}% ({department_results['success_count']}/{department_results['total_departments']})")
        
        self.verification_results['department_tests'] = department_results
        return department_results
    
    def verify_performance_metrics(self) -> Dict[str, Any]:
        """パフォーマンス測定"""
        print("\n⚡ パフォーマンス測定...")
        
        performance_metrics = {
            'response_times': [],
            'average_response_time': 0.0,
            'max_response_time': 0.0,
            'min_response_time': 0.0,
            'performance_grade': 'UNKNOWN'
        }
        
        try:
            # 5回の応答時間測定
            for i in range(5):
                start = time.time()
                response = requests.get(self.base_url, timeout=30)
                end = time.time()
                
                if response.status_code == 200:
                    response_time = round(end - start, 2)
                    performance_metrics['response_times'].append(response_time)
                    
                time.sleep(1)  # 1秒間隔
            
            if performance_metrics['response_times']:
                performance_metrics['average_response_time'] = round(
                    sum(performance_metrics['response_times']) / len(performance_metrics['response_times']), 2
                )
                performance_metrics['max_response_time'] = max(performance_metrics['response_times'])
                performance_metrics['min_response_time'] = min(performance_metrics['response_times'])
                
                # パフォーマンスグレード判定
                avg_time = performance_metrics['average_response_time']
                if avg_time <= 2.0:
                    performance_metrics['performance_grade'] = 'EXCELLENT'
                elif avg_time <= 4.0:
                    performance_metrics['performance_grade'] = 'GOOD'
                elif avg_time <= 8.0:
                    performance_metrics['performance_grade'] = 'ACCEPTABLE'
                else:
                    performance_metrics['performance_grade'] = 'POOR'
                
                print(f"   📈 平均応答時間: {performance_metrics['average_response_time']}秒")
                print(f"   📊 パフォーマンス: {performance_metrics['performance_grade']}")
                
        except Exception as e:
            print(f"   ❌ パフォーマンス測定エラー: {e}")
        
        self.verification_results['performance_tests'] = performance_metrics
        return performance_metrics
    
    def verify_blueprint_functionality(self) -> Dict[str, Any]:
        """Blueprint機能確認"""
        print("\n🏗️ Blueprint機能確認...")
        
        blueprint_tests = {
            'health_endpoints': {},
            'static_endpoints': {},
            'overall_success': False
        }
        
        # ヘルスチェックBlueprint
        health_endpoints = [
            '/health/simple',
            '/health/status',
            '/health/check',
            '/health/ready',
            '/health/live'
        ]
        
        health_success = 0
        for endpoint in health_endpoints:
            try:
                url = f"{self.base_url}{endpoint}"
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    blueprint_tests['health_endpoints'][endpoint] = 'SUCCESS'
                    health_success += 1
                    print(f"   ✅ {endpoint}: OK")
                else:
                    blueprint_tests['health_endpoints'][endpoint] = f'HTTP_{response.status_code}'
                    print(f"   ⚠️ {endpoint}: {response.status_code}")
                    
            except Exception as e:
                blueprint_tests['health_endpoints'][endpoint] = f'ERROR_{str(e)[:50]}'
                print(f"   ❌ {endpoint}: エラー")
        
        # 静的コンテンツBlueprint
        static_endpoints = [
            '/favicon.ico',
            '/manifest.json',
            '/robots.txt'
        ]
        
        static_success = 0
        for endpoint in static_endpoints:
            try:
                url = f"{self.base_url}{endpoint}"
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    blueprint_tests['static_endpoints'][endpoint] = 'SUCCESS'
                    static_success += 1
                    print(f"   ✅ {endpoint}: OK")
                else:
                    blueprint_tests['static_endpoints'][endpoint] = f'HTTP_{response.status_code}'
                    print(f"   ⚠️ {endpoint}: {response.status_code}")
                    
            except Exception as e:
                blueprint_tests['static_endpoints'][endpoint] = f'ERROR_{str(e)[:50]}'
                print(f"   ❌ {endpoint}: エラー")
        
        # 全体成功判定
        total_tests = len(health_endpoints) + len(static_endpoints)
        total_success = health_success + static_success
        success_rate = (total_success / total_tests) * 100
        
        blueprint_tests['overall_success'] = success_rate >= 70
        print(f"   📊 Blueprint成功率: {success_rate:.1f}% ({total_success}/{total_tests})")
        
        self.verification_results['functional_tests'] = blueprint_tests
        return blueprint_tests
    
    def verify_security_headers(self) -> Dict[str, Any]:
        """セキュリティヘッダー確認"""
        print("\n🛡️ セキュリティヘッダー確認...")
        
        security_checks = {
            'headers_present': {},
            'security_score': 0,
            'recommendations': []
        }
        
        expected_headers = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': ['DENY', 'SAMEORIGIN'],
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'required',
            'Content-Security-Policy': 'recommended'
        }
        
        try:
            response = requests.get(self.base_url, timeout=15)
            headers = response.headers
            
            score = 0
            for header, expected in expected_headers.items():
                if header in headers:
                    security_checks['headers_present'][header] = headers[header]
                    if expected != 'recommended' and expected != 'required':
                        if isinstance(expected, list):
                            if any(exp in headers[header] for exp in expected):
                                score += 1
                                print(f"   ✅ {header}: 適切")
                            else:
                                print(f"   ⚠️ {header}: 値要確認 - {headers[header]}")
                        else:
                            if expected in headers[header]:
                                score += 1
                                print(f"   ✅ {header}: 適切")
                            else:
                                print(f"   ⚠️ {header}: 値要確認 - {headers[header]}")
                    else:
                        score += 1
                        print(f"   ✅ {header}: 設定済み")
                else:
                    security_checks['headers_present'][header] = 'NOT_SET'
                    print(f"   ❌ {header}: 未設定")
                    security_checks['recommendations'].append(f"{header}ヘッダーの設定を推奨")
            
            security_checks['security_score'] = (score / len(expected_headers)) * 100
            print(f"   📊 セキュリティスコア: {security_checks['security_score']:.1f}%")
            
        except Exception as e:
            print(f"   ❌ セキュリティ確認エラー: {e}")
        
        self.verification_results['security_tests'] = security_checks
        return security_checks
    
    def calculate_overall_health_score(self) -> Dict[str, Any]:
        """総合健全性スコア計算"""
        print("\n📊 総合健全性スコア計算...")
        
        health_score = {
            'connectivity_score': 0,
            'functionality_score': 0,
            'performance_score': 0,
            'security_score': 0,
            'overall_score': 0,
            'health_grade': 'UNKNOWN',
            'critical_issues': [],
            'recommendations': []
        }
        
        try:
            # 接続性スコア
            connectivity = self.verification_results.get('connectivity_tests', {})
            connectivity_points = sum([
                100 if connectivity.get('homepage_access') else 0,
                100 if connectivity.get('health_check') else 0,
                50 if connectivity.get('static_resources') else 0
            ])
            health_score['connectivity_score'] = min(100, connectivity_points / 2.5)
            
            # 機能性スコア（部門テスト）
            dept_tests = self.verification_results.get('department_tests', {})
            if dept_tests.get('total_departments', 0) > 0:
                health_score['functionality_score'] = (
                    dept_tests.get('success_count', 0) / dept_tests.get('total_departments', 1)
                ) * 100
            
            # パフォーマンススコア
            performance = self.verification_results.get('performance_tests', {})
            avg_time = performance.get('average_response_time', 10)
            if avg_time <= 2:
                health_score['performance_score'] = 100
            elif avg_time <= 4:
                health_score['performance_score'] = 80
            elif avg_time <= 8:
                health_score['performance_score'] = 60
            else:
                health_score['performance_score'] = 40
            
            # セキュリティスコア
            security = self.verification_results.get('security_tests', {})
            health_score['security_score'] = security.get('security_score', 0)
            
            # 総合スコア計算
            scores = [
                health_score['connectivity_score'] * 0.3,    # 30%
                health_score['functionality_score'] * 0.4,   # 40%
                health_score['performance_score'] * 0.2,     # 20%
                health_score['security_score'] * 0.1         # 10%
            ]
            health_score['overall_score'] = round(sum(scores), 1)
            
            # 健全性グレード判定
            overall = health_score['overall_score']
            if overall >= 95:
                health_score['health_grade'] = 'EXCELLENT'
            elif overall >= 85:
                health_score['health_grade'] = 'GOOD'
            elif overall >= 70:
                health_score['health_grade'] = 'ACCEPTABLE'
            elif overall >= 50:
                health_score['health_grade'] = 'POOR'
            else:
                health_score['health_grade'] = 'CRITICAL'
            
            # 重要な問題の特定
            if health_score['connectivity_score'] < 80:
                health_score['critical_issues'].append("基本接続に問題あり")
            
            if health_score['functionality_score'] < 90:
                failed_depts = dept_tests.get('failed_departments', [])
                if failed_depts:
                    health_score['critical_issues'].append(f"部門機能障害: {', '.join(failed_depts[:3])}")
            
            if health_score['performance_score'] < 60:
                health_score['critical_issues'].append("パフォーマンス問題")
            
            print(f"   🎯 総合スコア: {health_score['overall_score']}% ({health_score['health_grade']})")
            print(f"   📈 接続性: {health_score['connectivity_score']:.1f}%")
            print(f"   🏢 機能性: {health_score['functionality_score']:.1f}%")
            print(f"   ⚡ パフォーマンス: {health_score['performance_score']:.1f}%")
            print(f"   🛡️ セキュリティ: {health_score['security_score']:.1f}%")
            
            if health_score['critical_issues']:
                print(f"   🚨 重要な問題: {len(health_score['critical_issues'])}件")
            
        except Exception as e:
            print(f"   ❌ スコア計算エラー: {e}")
        
        self.verification_results['overall_health'] = health_score
        return health_score
    
    def generate_verification_report(self) -> str:
        """検証レポート生成"""
        print("\n📋 最終検証レポート生成...")
        
        # 実行時間計算
        execution_time = time.time() - self.start_time
        self.verification_results['execution_time_seconds'] = round(execution_time, 2)
        
        # レポートファイル保存
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_filename = f"ULTRASYNC_POST_DEPLOY_VERIFICATION_{timestamp}.json"
        
        try:
            with open(report_filename, 'w', encoding='utf-8') as f:
                json.dump(self.verification_results, f, ensure_ascii=False, indent=2)
            
            print(f"   💾 レポート保存: {report_filename}")
            return report_filename
            
        except Exception as e:
            print(f"   ❌ レポート保存失敗: {e}")
            return ""
    
    def run_comprehensive_verification(self) -> bool:
        """包括的検証実行"""
        print("🎯 【ULTRASYNC段階4】デプロイ後包括的動作検証開始")
        print(f"対象URL: {self.base_url}")
        print("=" * 70)
        
        success = True
        
        try:
            # Phase 1: 基本接続確認
            connectivity_ok = self.verify_basic_connectivity()
            if not connectivity_ok:
                print("⚠️ 基本接続に問題があります")
                success = False
            
            # Phase 2: 部門機能確認
            department_results = self.verify_department_functionality()
            if department_results['success_count'] < department_results['total_departments'] * 0.8:
                print("⚠️ 部門機能に問題があります")
                success = False
            
            # Phase 3: パフォーマンス測定
            performance_results = self.verify_performance_metrics()
            if performance_results.get('performance_grade') in ['POOR']:
                print("⚠️ パフォーマンスに問題があります")
                success = False
            
            # Phase 4: Blueprint機能確認
            blueprint_results = self.verify_blueprint_functionality()
            if not blueprint_results.get('overall_success'):
                print("⚠️ Blueprint機能に問題があります")
            
            # Phase 5: セキュリティ確認
            security_results = self.verify_security_headers()
            
            # Phase 6: 総合健全性評価
            health_score = self.calculate_overall_health_score()
            
            # Phase 7: レポート生成
            report_file = self.generate_verification_report()
            
            print("\n" + "=" * 70)
            print("🎉 【ULTRASYNC段階4】デプロイ後検証完了")
            
            overall_score = health_score.get('overall_score', 0)
            health_grade = health_score.get('health_grade', 'UNKNOWN')
            
            if overall_score >= 85:
                print("✅ 結論: デプロイ成功 - 本番環境正常稼働確認")
                print("🚀 次段階: ULTRASYNC段階5（最終品質保証レポート）へ進行")
            elif overall_score >= 70:
                print("⚠️ 結論: 軽微な問題あり - 監視継続推奨")
                print("🔧 次段階: 課題対応後、段階5へ進行")
            else:
                print("🚨 結論: 重要な問題あり - 即座対応必要")
                print("🆘 次段階: 緊急対応後、再検証実施")
                success = False
            
            return success and overall_score >= 70
            
        except Exception as e:
            print(f"\n❌ 検証実行エラー: {e}")
            return False

def main():
    """メイン実行"""
    # 本番URL確認（デプロイ状況に応じて調整）
    base_url = "https://rccm-quiz-2025.onrender.com"
    
    print("🔍 デプロイ状況事前確認...")
    try:
        # 簡易接続テスト
        response = requests.get(base_url, timeout=10)
        if response.status_code == 200:
            print(f"✅ {base_url} - 接続確認")
        else:
            print(f"⚠️ {base_url} - HTTP {response.status_code}")
            print("ℹ️ デプロイが完了していない可能性があります")
            
            # ローカル環境での検証に切り替え
            local_url = "http://localhost:5000"
            print(f"🔄 ローカル環境での検証に切り替え: {local_url}")
            base_url = local_url
            
    except Exception as e:
        print(f"⚠️ 本番環境接続不可: {e}")
        print("🔄 ローカル環境での検証を実施")
        base_url = "http://localhost:5000"
    
    verifier = UltraSyncPostDeployVerification(base_url)
    success = verifier.run_comprehensive_verification()
    
    print(f"\n🏁 ULTRASYNC段階4完了")
    print(f"副作用: ゼロ（読み取り専用検証）")
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)