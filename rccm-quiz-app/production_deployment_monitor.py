#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Production Deployment Monitor
本番環境デプロイメント監視・確認スクリプト

GitHubからのデプロイ後に自動でヘルスチェックを実行
"""

import os
import sys
import time
import json
import requests
from datetime import datetime
from typing import Dict, List, Optional

class ProductionDeploymentMonitor:
    """本番環境デプロイメント監視クラス"""
    
    def __init__(self):
        self.production_urls = [
            "https://rccm-quiz-app.onrender.com",  # Render
            "https://rccm-quiz-vercel.vercel.app",  # Vercel (example)
            "https://rccm-quiz.up.railway.app"     # Railway (example)
        ]
        
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "monitoring_type": "production_deployment",
            "environments": {},
            "overall_status": "unknown",
            "critical_issues": [],
            "recommendations": []
        }
    
    def check_environment_health(self, url: str) -> Dict:
        """環境ヘルスチェック"""
        env_name = url.split("//")[1].split(".")[0]
        
        print(f"🔍 Checking {env_name}: {url}")
        
        health_result = {
            "url": url,
            "environment": env_name,
            "status": "unknown",
            "response_time": None,
            "status_code": None,
            "content_check": False,
            "department_check": False,
            "timestamp": datetime.now().isoformat(),
            "errors": []
        }
        
        try:
            # 基本接続テスト
            start_time = time.time()
            response = requests.get(url, timeout=30)
            response_time = time.time() - start_time
            
            health_result["response_time"] = response_time
            health_result["status_code"] = response.status_code
            
            if response.status_code == 200:
                print(f"   ✅ HTTP 200 OK ({response_time:.2f}s)")
                
                # コンテンツ確認
                content = response.text
                if "RCCM" in content and "基礎科目" in content:
                    health_result["content_check"] = True
                    print(f"   ✅ Content validation passed")
                else:
                    health_result["errors"].append("Content validation failed")
                    print(f"   ❌ Content validation failed")
                
                # 基礎科目ページ確認
                try:
                    dept_url = f"{url}/quiz_department/基礎科目"
                    dept_response = requests.get(dept_url, timeout=15)
                    if dept_response.status_code == 200:
                        health_result["department_check"] = True
                        print(f"   ✅ Department page accessible")
                    else:
                        health_result["errors"].append(f"Department page error: {dept_response.status_code}")
                        print(f"   ❌ Department page error: {dept_response.status_code}")
                except Exception as e:
                    health_result["errors"].append(f"Department check failed: {str(e)}")
                    print(f"   ❌ Department check failed: {e}")
                
                # 総合ステータス判定
                if health_result["content_check"] and health_result["department_check"]:
                    health_result["status"] = "healthy"
                    print(f"   🎉 {env_name} is HEALTHY")
                else:
                    health_result["status"] = "degraded"
                    print(f"   ⚠️ {env_name} is DEGRADED")
                    
            else:
                health_result["status"] = "unhealthy"
                health_result["errors"].append(f"HTTP {response.status_code}")
                print(f"   ❌ HTTP {response.status_code}")
                
        except requests.exceptions.Timeout:
            health_result["status"] = "timeout"
            health_result["errors"].append("Request timeout")
            print(f"   ❌ Timeout after 30 seconds")
            
        except requests.exceptions.ConnectionError:
            health_result["status"] = "unreachable"
            health_result["errors"].append("Connection error")
            print(f"   ❌ Connection failed")
            
        except Exception as e:
            health_result["status"] = "error"
            health_result["errors"].append(str(e))
            print(f"   ❌ Error: {e}")
        
        return health_result
    
    def run_comprehensive_monitoring(self) -> Dict:
        """包括的監視実行"""
        print("🚀 Production Deployment Monitoring")
        print("=" * 50)
        print(f"Start time: {datetime.now()}")
        print()
        
        healthy_count = 0
        total_count = len(self.production_urls)
        
        for url in self.production_urls:
            health_result = self.check_environment_health(url)
            self.test_results["environments"][health_result["environment"]] = health_result
            
            if health_result["status"] == "healthy":
                healthy_count += 1
            elif health_result["status"] in ["unhealthy", "timeout", "unreachable"]:
                self.test_results["critical_issues"].append({
                    "environment": health_result["environment"],
                    "issue": health_result["status"],
                    "details": health_result["errors"]
                })
            
            print()  # 空行
        
        # 総合ステータス判定
        if healthy_count == total_count:
            self.test_results["overall_status"] = "all_healthy"
        elif healthy_count > 0:
            self.test_results["overall_status"] = "partially_healthy"
        else:
            self.test_results["overall_status"] = "all_unhealthy"
        
        # 推奨事項生成
        self.generate_recommendations()
        
        return self.test_results
    
    def generate_recommendations(self):
        """推奨事項生成"""
        if self.test_results["overall_status"] == "all_healthy":
            self.test_results["recommendations"].append("All environments are healthy. Continue monitoring.")
        
        elif self.test_results["overall_status"] == "partially_healthy":
            self.test_results["recommendations"].append("Some environments have issues. Check deployment logs.")
            self.test_results["recommendations"].append("Consider rollback if critical functionality is affected.")
        
        else:
            self.test_results["recommendations"].append("All environments are unhealthy. Immediate investigation required.")
            self.test_results["recommendations"].append("Check deployment pipeline and infrastructure status.")
            self.test_results["recommendations"].append("Consider emergency rollback.")
    
    def save_monitoring_report(self) -> str:
        """監視レポート保存"""
        report_filename = f"production_monitoring_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, ensure_ascii=False, indent=2)
        
        print(f"📋 Monitoring report saved: {report_filename}")
        return report_filename
    
    def print_summary(self):
        """監視結果サマリー表示"""
        print("=" * 50)
        print("🎯 PRODUCTION MONITORING SUMMARY")
        print("=" * 50)
        
        overall_status = self.test_results["overall_status"]
        
        print(f"📊 Overall Status: {overall_status.upper()}")
        print(f"🌐 Environments Monitored: {len(self.test_results['environments'])}")
        
        healthy_envs = [env for env, data in self.test_results['environments'].items() 
                       if data['status'] == 'healthy']
        print(f"✅ Healthy Environments: {len(healthy_envs)}")
        if healthy_envs:
            for env in healthy_envs:
                env_data = self.test_results['environments'][env]
                print(f"   - {env}: {env_data['response_time']:.2f}s response")
        
        if self.test_results['critical_issues']:
            print(f"❌ Critical Issues: {len(self.test_results['critical_issues'])}")
            for issue in self.test_results['critical_issues']:
                print(f"   - {issue['environment']}: {issue['issue']}")
        
        if self.test_results['recommendations']:
            print(f"\n💡 Recommendations:")
            for rec in self.test_results['recommendations']:
                print(f"   - {rec}")
        
        print("\n" + "=" * 50)
        
        # GitHub Actions 用の結果
        if overall_status == "all_healthy":
            print("🎉 DEPLOYMENT MONITORING: SUCCESS")
            return True
        else:
            print("⚠️ DEPLOYMENT MONITORING: ISSUES DETECTED")
            return False

def main():
    """メインエントリーポイント"""
    monitor = ProductionDeploymentMonitor()
    
    try:
        # 包括的監視実行
        results = monitor.run_comprehensive_monitoring()
        
        # レポート保存
        monitor.save_monitoring_report()
        
        # サマリー表示
        success = monitor.print_summary()
        
        # GitHub Actions用の終了コード
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n⚠️ Monitoring interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Monitoring failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()