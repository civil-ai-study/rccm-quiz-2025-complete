#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask環境なしBlueprint動作検証システム
Blueprintの構造・ルート・動作ロジックを純粋Pythonで検証
"""

import sys
import os
import importlib.util
import inspect
from typing import Dict, List, Any

class FlaskFreeBlueprinterVerifier:
    """Flask環境なしでBlueprint動作検証"""
    
    def __init__(self):
        self.verification_results = {
            'blueprint_files': [],
            'route_analysis': [],
            'import_dependencies': [],
            'function_analysis': [],
            'errors': [],
            'warnings': []
        }
    
    def load_blueprint_module(self, file_path: str) -> Any:
        """Blueprintモジュールを直接読み込み"""
        try:
            spec = importlib.util.spec_from_file_location("blueprint_module", file_path)
            module = importlib.util.module_from_spec(spec)
            
            # Flask関連のモックを設定
            self.setup_flask_mocks(module)
            
            spec.loader.exec_module(module)
            return module
            
        except Exception as e:
            self.verification_results['errors'].append({
                'file': file_path,
                'error': str(e),
                'type': 'module_load_error'
            })
            return None
    
    def setup_flask_mocks(self, module):
        """Flask依存関係のモック設定"""
        # Flaskモック
        class MockBlueprint:
            def __init__(self, name, import_name, url_prefix=None):
                self.name = name
                self.import_name = import_name
                self.url_prefix = url_prefix
                self.routes = []
                self.deferred_functions = []
            
            def route(self, rule, **options):
                def decorator(func):
                    self.routes.append({
                        'rule': rule,
                        'function': func,
                        'options': options,
                        'endpoint': func.__name__
                    })
                    return func
                return decorator
        
        class MockFlaskModule:
            Blueprint = MockBlueprint
            
            def jsonify(self, data):
                return f"JSON: {data}"
            
            def send_from_directory(self, directory, filename, **kwargs):
                return f"FILE: {directory}/{filename}"
            
            def Response(self, content, **kwargs):
                return f"RESPONSE: {content}"
        
        # sys.modulesにモックを追加
        sys.modules['flask'] = MockFlaskModule()
        module.flask = MockFlaskModule()
    
    def analyze_blueprint_file(self, file_path: str) -> Dict:
        """Blueprintファイルの詳細分析"""
        try:
            # ファイル基本情報
            file_info = {
                'path': file_path,
                'filename': os.path.basename(file_path),
                'size': os.path.getsize(file_path),
                'exists': os.path.exists(file_path)
            }
            
            # モジュール読み込み
            module = self.load_blueprint_module(file_path)
            if not module:
                return file_info
            
            # Blueprint変数の検索
            blueprints = []
            for name, obj in inspect.getmembers(module):
                if hasattr(obj, 'name') and hasattr(obj, 'routes'):
                    blueprints.append({
                        'variable_name': name,
                        'blueprint_name': obj.name,
                        'url_prefix': getattr(obj, 'url_prefix', None),
                        'routes': obj.routes
                    })
            
            file_info['blueprints'] = blueprints
            
            # 関数分析
            functions = []
            for name, obj in inspect.getmembers(module, inspect.isfunction):
                if not name.startswith('_'):
                    functions.append({
                        'name': name,
                        'args': list(inspect.signature(obj).parameters.keys()),
                        'docstring': inspect.getdoc(obj),
                        'source_lines': len(inspect.getsource(obj).split('\n'))
                    })
            
            file_info['functions'] = functions
            
            # インポート依存関係の分析
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            imports = []
            for line in content.split('\n'):
                line = line.strip()
                if line.startswith(('import ', 'from ')):
                    imports.append(line)
            
            file_info['imports'] = imports
            
            return file_info
            
        except Exception as e:
            self.verification_results['errors'].append({
                'file': file_path,
                'error': str(e),
                'type': 'analysis_error'
            })
            return file_info
    
    def verify_route_logic(self, blueprint_info: Dict) -> List[Dict]:
        """ルートロジックの検証"""
        route_verifications = []
        
        for bp in blueprint_info.get('blueprints', []):
            for route in bp.get('routes', []):
                verification = {
                    'blueprint': bp['blueprint_name'],
                    'route': route['rule'],
                    'function': route['function'].__name__,
                    'endpoint': route['endpoint']
                }
                
                # 関数のソースコード分析
                try:
                    source = inspect.getsource(route['function'])
                    verification['source_lines'] = len(source.split('\n'))
                    verification['has_try_except'] = 'try:' in source
                    verification['has_return'] = 'return' in source
                    verification['has_jsonify'] = 'jsonify' in source
                    verification['complexity'] = source.count('if') + source.count('for') + source.count('while')
                    
                except Exception as e:
                    verification['source_analysis_error'] = str(e)
                
                route_verifications.append(verification)
        
        return route_verifications
    
    def test_function_execution(self, blueprint_info: Dict) -> List[Dict]:
        """関数の実行テスト（安全な範囲で）"""
        execution_tests = []
        
        for bp in blueprint_info.get('blueprints', []):
            for route in bp.get('routes', []):
                func = route['function']
                test_result = {
                    'function': func.__name__,
                    'route': route['rule'],
                    'executable': False,
                    'error': None
                }
                
                try:
                    # 引数なしの関数のみテスト
                    sig = inspect.signature(func)
                    if len(sig.parameters) == 0:
                        result = func()
                        test_result['executable'] = True
                        test_result['result_type'] = type(result).__name__
                        test_result['result_preview'] = str(result)[:100]
                    else:
                        test_result['skip_reason'] = 'requires_arguments'
                
                except Exception as e:
                    test_result['error'] = str(e)
                
                execution_tests.append(test_result)
        
        return execution_tests
    
    def verify_blueprints(self, blueprint_files: List[str]) -> Dict:
        """メインBlueprint検証処理"""
        print("🔍 Flask環境なしBlueprint検証開始")
        
        for file_path in blueprint_files:
            print(f"📁 分析中: {file_path}")
            
            # ファイル分析
            file_info = self.analyze_blueprint_file(file_path)
            self.verification_results['blueprint_files'].append(file_info)
            
            # ルート分析
            route_analysis = self.verify_route_logic(file_info)
            self.verification_results['route_analysis'].extend(route_analysis)
            
            # 実行テスト
            execution_tests = self.test_function_execution(file_info)
            self.verification_results['function_analysis'].extend(execution_tests)
        
        # 結果サマリー
        self.generate_summary()
        
        return self.verification_results
    
    def generate_summary(self):
        """検証結果サマリー生成"""
        total_blueprints = sum(len(f.get('blueprints', [])) for f in self.verification_results['blueprint_files'])
        total_routes = len(self.verification_results['route_analysis'])
        executable_functions = sum(1 for f in self.verification_results['function_analysis'] if f.get('executable', False))
        
        self.verification_results['summary'] = {
            'total_files': len(self.verification_results['blueprint_files']),
            'total_blueprints': total_blueprints,
            'total_routes': total_routes,
            'executable_functions': executable_functions,
            'error_count': len(self.verification_results['errors']),
            'warning_count': len(self.verification_results['warnings'])
        }
    
    def print_results(self):
        """結果出力"""
        print("\n" + "="*60)
        print("🎯 Flask環境なしBlueprint検証結果")
        print("="*60)
        
        summary = self.verification_results['summary']
        print(f"📊 サマリー:")
        print(f"  ・検証ファイル数: {summary['total_files']}")
        print(f"  ・Blueprint数: {summary['total_blueprints']}")
        print(f"  ・ルート数: {summary['total_routes']}")
        print(f"  ・実行可能関数数: {summary['executable_functions']}")
        print(f"  ・エラー数: {summary['error_count']}")
        print(f"  ・警告数: {summary['warning_count']}")
        
        print("\n📋 Blueprint詳細:")
        for file_info in self.verification_results['blueprint_files']:
            print(f"\n  📁 {file_info['filename']}:")
            for bp in file_info.get('blueprints', []):
                print(f"    ・Blueprint名: {bp['blueprint_name']}")
                print(f"    ・URLプレフィックス: {bp['url_prefix']}")
                print(f"    ・ルート数: {len(bp['routes'])}")
                
                for route in bp['routes']:
                    print(f"      - {route['rule']} → {route['endpoint']}")
        
        print("\n🔧 ルート分析:")
        for route in self.verification_results['route_analysis']:
            print(f"  ・{route['route']} ({route['function']})")
            print(f"    - ソース行数: {route.get('source_lines', 'N/A')}")
            print(f"    - 複雑度: {route.get('complexity', 'N/A')}")
            print(f"    - エラーハンドリング: {'あり' if route.get('has_try_except', False) else 'なし'}")
        
        if self.verification_results['errors']:
            print("\n❌ エラー:")
            for error in self.verification_results['errors']:
                print(f"  ・{error['file']}: {error['error']}")

def main():
    """メイン実行"""
    verifier = FlaskFreeBlueprinterVerifier()
    
    # Blueprintファイルの検索
    blueprint_files = [
        '/mnt/c/Users/ABC/Desktop/rccm-quiz-app/rccm-quiz-app/blueprints/static_bp.py',
        '/mnt/c/Users/ABC/Desktop/rccm-quiz-app/rccm-quiz-app/blueprints/health_bp.py'
    ]
    
    # 存在確認
    existing_files = [f for f in blueprint_files if os.path.exists(f)]
    if not existing_files:
        print("❌ Blueprintファイルが見つかりません")
        return
    
    print(f"🔍 検証対象: {len(existing_files)}個のBlueprint")
    
    # 検証実行
    results = verifier.verify_blueprints(existing_files)
    
    # 結果表示
    verifier.print_results()
    
    # 結果保存
    import json
    with open('flask_free_blueprint_verification_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n💾 詳細結果を保存: flask_free_blueprint_verification_results.json")

if __name__ == "__main__":
    main()