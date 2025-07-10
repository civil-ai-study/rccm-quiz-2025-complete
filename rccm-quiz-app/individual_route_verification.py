#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
個別ルート検証システム
static_bp、health_bp各ルートの動作・応答・エラーハンドリングを個別に検証
"""

import os
import sys
import tempfile
import subprocess
import requests
import json
import time
from threading import Thread
from flask import Flask

class IndividualRouteVerifier:
    """個別ルート検証システム"""
    
    def __init__(self):
        self.verification_results = {
            'static_bp_routes': [],
            'health_bp_routes': [],
            'server_info': {},
            'errors': [],
            'warnings': [],
            'summary': {}
        }
        self.test_server = None
        self.server_url = "http://localhost:5555"
    
    def start_test_server(self):
        """テスト用サーバーを分離プロセスで起動"""
        try:
            # テスト用サーバーコード作成
            server_code = '''
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from blueprints.static_bp import static_bp
from blueprints.health_bp import health_bp

app = Flask(__name__)
app.config['TESTING'] = True

# Blueprint登録
app.register_blueprint(static_bp)
app.register_blueprint(health_bp)

@app.route('/test/ping')
def ping():
    return "pong"

if __name__ == "__main__":
    print("Test server starting on port 5555...")
    app.run(host="127.0.0.1", port=5555, debug=False)
'''
            
            # 一時ファイル作成
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(server_code)
                server_file = f.name
            
            # blueprintsディレクトリへのシンボリックリンク作成
            temp_dir = os.path.dirname(server_file)
            blueprints_link = os.path.join(temp_dir, 'blueprints')
            blueprints_source = '/mnt/c/Users/ABC/Desktop/rccm-quiz-app/rccm-quiz-app/blueprints'
            
            if not os.path.exists(blueprints_link):
                os.symlink(blueprints_source, blueprints_link)
            
            # サーバー起動
            self.test_server = subprocess.Popen([
                sys.executable, server_file
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # サーバー起動待機
            for _ in range(30):  # 最大30秒待機
                try:
                    response = requests.get(f"{self.server_url}/test/ping", timeout=1)
                    if response.status_code == 200:
                        print("✅ テストサーバー起動完了")
                        return True
                except:
                    time.sleep(1)
            
            print("❌ テストサーバー起動失敗")
            return False
            
        except Exception as e:
            print(f"❌ サーバー起動エラー: {e}")
            return False
    
    def stop_test_server(self):
        """テストサーバー停止"""
        if self.test_server:
            try:
                self.test_server.terminate()
                self.test_server.wait(timeout=5)
                print("✅ テストサーバー停止完了")
            except:
                self.test_server.kill()
                print("⚠️  テストサーバー強制停止")
    
    def test_static_bp_routes(self):
        """static_bp個別ルートテスト"""
        print("\n🔍 static_bp個別ルートテスト開始")
        
        routes = [
            {
                'path': '/favicon.ico',
                'expected_status': [200, 404],
                'expected_content_type': ['image/x-icon', 'image/gif'],
                'description': 'ファビコン取得'
            },
            {
                'path': '/manifest.json',
                'expected_status': [200],
                'expected_content_type': ['application/json'],
                'description': 'PWAマニフェスト取得'
            },
            {
                'path': '/sw.js',
                'expected_status': [200],
                'expected_content_type': ['application/javascript'],
                'description': 'Service Worker取得'
            },
            {
                'path': '/robots.txt',
                'expected_status': [200],
                'expected_content_type': ['text/plain'],
                'description': 'robots.txt取得'
            },
            {
                'path': '/sitemap.xml',
                'expected_status': [200],
                'expected_content_type': ['application/xml'],
                'description': 'サイトマップ取得'
            },
            {
                'path': '/icon-192.png',
                'expected_status': [200, 404],
                'expected_content_type': ['image/png', 'image/x-icon'],
                'description': 'アプリアイコン取得'
            },
            {
                'path': '/icon-999.png',  # 無効サイズ
                'expected_status': [200, 404],
                'expected_content_type': ['image/png', 'image/x-icon'],
                'description': 'アプリアイコン取得（無効サイズ）'
            }
        ]
        
        for route in routes:
            result = self.test_individual_route(route)
            self.verification_results['static_bp_routes'].append(result)
            print(f"  ・{route['path']}: {result['status_code']} - {result['test_result']}")
    
    def test_health_bp_routes(self):
        """health_bp個別ルートテスト"""
        print("\n🔍 health_bp個別ルートテスト開始")
        
        routes = [
            {
                'path': '/health/simple',
                'expected_status': [200],
                'expected_content_type': ['application/json'],
                'description': 'シンプルヘルスチェック'
            },
            {
                'path': '/health/status',
                'expected_status': [200],
                'expected_content_type': ['application/json'],
                'description': '詳細ヘルスチェック'
            },
            {
                'path': '/health/',
                'expected_status': [200],
                'expected_content_type': ['application/json'],
                'description': 'ヘルスチェック（ルート）'
            },
            {
                'path': '/health/check',
                'expected_status': [200, 503],
                'expected_content_type': ['application/json'],
                'description': 'Kubernetes対応ヘルスチェック'
            },
            {
                'path': '/health/ready',
                'expected_status': [200, 503],
                'expected_content_type': ['application/json'],
                'description': 'Readiness Probe'
            },
            {
                'path': '/health/live',
                'expected_status': [200, 500],
                'expected_content_type': ['application/json'],
                'description': 'Liveness Probe'
            }
        ]
        
        for route in routes:
            result = self.test_individual_route(route)
            self.verification_results['health_bp_routes'].append(result)
            print(f"  ・{route['path']}: {result['status_code']} - {result['test_result']}")
    
    def test_individual_route(self, route_config):
        """個別ルートテスト実行"""
        result = {
            'path': route_config['path'],
            'description': route_config['description'],
            'test_result': 'UNKNOWN',
            'status_code': None,
            'content_type': None,
            'response_time_ms': None,
            'response_size': None,
            'error': None,
            'warnings': []
        }
        
        try:
            start_time = time.time()
            
            # HTTPリクエスト実行
            response = requests.get(
                f"{self.server_url}{route_config['path']}", 
                timeout=10
            )
            
            end_time = time.time()
            
            # レスポンス情報記録
            result['status_code'] = response.status_code
            result['content_type'] = response.headers.get('Content-Type', '')
            result['response_time_ms'] = round((end_time - start_time) * 1000, 2)
            result['response_size'] = len(response.content)
            
            # ステータスコード判定
            if response.status_code in route_config['expected_status']:
                result['test_result'] = 'PASS'
            else:
                result['test_result'] = 'FAIL'
                result['warnings'].append(f"予期しないステータスコード: {response.status_code}")
            
            # Content-Type判定
            content_type_match = False
            for expected_type in route_config['expected_content_type']:
                if expected_type in result['content_type']:
                    content_type_match = True
                    break
            
            if not content_type_match:
                result['warnings'].append(f"予期しないContent-Type: {result['content_type']}")
            
            # レスポンス時間チェック
            if result['response_time_ms'] > 5000:  # 5秒以上
                result['warnings'].append(f"レスポンス時間が遅い: {result['response_time_ms']}ms")
            
            # レスポンス内容の簡易チェック
            if response.status_code == 200:
                if 'json' in result['content_type']:
                    try:
                        response.json()
                    except json.JSONDecodeError:
                        result['warnings'].append("JSONパースエラー")
                
                if result['response_size'] == 0:
                    result['warnings'].append("レスポンスボディが空")
            
        except requests.exceptions.Timeout:
            result['test_result'] = 'TIMEOUT'
            result['error'] = 'Request timeout'
            
        except requests.exceptions.ConnectionError:
            result['test_result'] = 'CONNECTION_ERROR'
            result['error'] = 'Connection error'
            
        except Exception as e:
            result['test_result'] = 'ERROR'
            result['error'] = str(e)
        
        return result
    
    def generate_summary(self):
        """検証結果サマリー生成"""
        all_routes = self.verification_results['static_bp_routes'] + self.verification_results['health_bp_routes']
        
        total_routes = len(all_routes)
        passed_routes = sum(1 for r in all_routes if r['test_result'] == 'PASS')
        failed_routes = sum(1 for r in all_routes if r['test_result'] == 'FAIL')
        error_routes = sum(1 for r in all_routes if r['test_result'] in ['ERROR', 'TIMEOUT', 'CONNECTION_ERROR'])
        
        avg_response_time = 0
        if all_routes:
            valid_times = [r['response_time_ms'] for r in all_routes if r['response_time_ms'] is not None]
            if valid_times:
                avg_response_time = round(sum(valid_times) / len(valid_times), 2)
        
        self.verification_results['summary'] = {
            'total_routes': total_routes,
            'passed_routes': passed_routes,
            'failed_routes': failed_routes,
            'error_routes': error_routes,
            'success_rate': round((passed_routes / total_routes) * 100, 1) if total_routes > 0 else 0,
            'avg_response_time_ms': avg_response_time,
            'static_bp_routes': len(self.verification_results['static_bp_routes']),
            'health_bp_routes': len(self.verification_results['health_bp_routes'])
        }
    
    def print_results(self):
        """結果表示"""
        print("\n" + "="*80)
        print("🎯 個別ルート検証結果")
        print("="*80)
        
        summary = self.verification_results['summary']
        print(f"📊 サマリー:")
        print(f"  ・総ルート数: {summary['total_routes']}")
        print(f"  ・成功: {summary['passed_routes']} ({summary['success_rate']}%)")
        print(f"  ・失敗: {summary['failed_routes']}")
        print(f"  ・エラー: {summary['error_routes']}")
        print(f"  ・平均レスポンス時間: {summary['avg_response_time_ms']}ms")
        
        print(f"\n📋 詳細結果:")
        
        # static_bp結果
        print(f"\n  🔹 static_bp ({len(self.verification_results['static_bp_routes'])}ルート):")
        for route in self.verification_results['static_bp_routes']:
            status = "✅" if route['test_result'] == 'PASS' else "❌"
            print(f"    {status} {route['path']}")
            print(f"       - ステータス: {route['status_code']}")
            print(f"       - レスポンス時間: {route['response_time_ms']}ms")
            print(f"       - サイズ: {route['response_size']} bytes")
            if route['warnings']:
                print(f"       - 警告: {', '.join(route['warnings'])}")
        
        # health_bp結果
        print(f"\n  🔹 health_bp ({len(self.verification_results['health_bp_routes'])}ルート):")
        for route in self.verification_results['health_bp_routes']:
            status = "✅" if route['test_result'] == 'PASS' else "❌"
            print(f"    {status} {route['path']}")
            print(f"       - ステータス: {route['status_code']}")
            print(f"       - レスポンス時間: {route['response_time_ms']}ms")
            print(f"       - サイズ: {route['response_size']} bytes")
            if route['warnings']:
                print(f"       - 警告: {', '.join(route['warnings'])}")
    
    def run_verification(self):
        """メイン検証処理"""
        print("🚀 個別ルート検証開始")
        
        try:
            # テストサーバー起動
            if not self.start_test_server():
                print("❌ テストサーバー起動失敗")
                return False
            
            # ルート検証実行
            self.test_static_bp_routes()
            self.test_health_bp_routes()
            
            # 結果集計
            self.generate_summary()
            
            # 結果表示
            self.print_results()
            
            return True
            
        finally:
            # サーバー停止
            self.stop_test_server()

def main():
    """メイン処理"""
    verifier = IndividualRouteVerifier()
    
    success = verifier.run_verification()
    
    # 結果保存
    with open('individual_route_verification_results.json', 'w', encoding='utf-8') as f:
        json.dump(verifier.verification_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 詳細結果を保存: individual_route_verification_results.json")
    
    if success:
        print("✅ 個別ルート検証が正常に完了しました")
    else:
        print("❌ 個別ルート検証で問題が発生しました")

if __name__ == "__main__":
    main()