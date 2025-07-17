#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
🔥 ULTRA SYNC タスク3: Python実行環境診断ツール
副作用ゼロで環境問題を診断し、最適な実行方法を提案
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

class UltraSyncEnvironmentDiagnostic:
    """Python実行環境の包括的診断と解決策提案"""
    
    def __init__(self):
        self.results = {
            'platform': platform.system(),
            'python_version': sys.version,
            'executable_path': sys.executable,
            'working_directory': os.getcwd(),
            'available_commands': {},
            'recommended_solution': None
        }
    
    def diagnose_python_commands(self):
        """利用可能なPythonコマンドを診断"""
        commands_to_test = [
            'python',
            'python3',
            'py',
            'python.exe',
            'python3.exe',
            sys.executable  # 現在のPython実行ファイル
        ]
        
        for cmd in commands_to_test:
            try:
                # 🛡️ 安全な実行テスト（副作用なし）
                result = subprocess.run(
                    [cmd, '--version'], 
                    capture_output=True, 
                    text=True, 
                    timeout=5
                )
                
                if result.returncode == 0:
                    self.results['available_commands'][cmd] = {
                        'version': result.stdout.strip(),
                        'working': True,
                        'path': cmd
                    }
                else:
                    self.results['available_commands'][cmd] = {
                        'version': 'Error',
                        'working': False,
                        'error': result.stderr.strip()
                    }
                    
            except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError) as e:
                self.results['available_commands'][cmd] = {
                    'version': 'Not Found',
                    'working': False,
                    'error': str(e)
                }
    
    def test_app_execution(self):
        """app.pyの実行テスト"""
        app_path = Path('app.py')
        
        if not app_path.exists():
            return {
                'app_exists': False,
                'error': 'app.py が見つかりません'
            }
        
        # 動作するコマンドでapp.pyの実行テスト
        working_commands = [
            cmd for cmd, info in self.results['available_commands'].items() 
            if info.get('working', False)
        ]
        
        execution_results = {}
        
        for cmd in working_commands:
            try:
                # 🛡️ 安全なテスト実行（即座に終了）
                result = subprocess.run(
                    [cmd, 'app.py', '--help'], 
                    capture_output=True, 
                    text=True, 
                    timeout=10
                )
                
                execution_results[cmd] = {
                    'success': result.returncode == 0,
                    'output': result.stdout[:200],  # 最初の200文字のみ
                    'error': result.stderr[:200] if result.stderr else None
                }
                
            except (subprocess.TimeoutExpired, subprocess.SubprocessError) as e:
                execution_results[cmd] = {
                    'success': False,
                    'error': str(e)
                }
        
        return {
            'app_exists': True,
            'execution_results': execution_results
        }
    
    def detect_environment_type(self):
        """実行環境の種類を特定"""
        env_type = 'unknown'
        
        # WSL検出
        if 'Microsoft' in platform.release() or 'WSL' in platform.release():
            env_type = 'wsl'
        # Windows検出
        elif platform.system() == 'Windows':
            env_type = 'windows'
        # Linux検出
        elif platform.system() == 'Linux':
            env_type = 'linux'
        # macOS検出
        elif platform.system() == 'Darwin':
            env_type = 'macos'
        
        self.results['environment_type'] = env_type
        return env_type
    
    def generate_solution(self):
        """環境に応じた最適な解決策を生成"""
        env_type = self.results.get('environment_type', 'unknown')
        working_commands = [
            cmd for cmd, info in self.results['available_commands'].items() 
            if info.get('working', False)
        ]
        
        if not working_commands:
            return {
                'type': 'no_python',
                'message': 'Pythonが見つかりません。Pythonをインストールしてください。',
                'commands': []
            }
        
        # 最適なコマンドを選択
        preferred_order = ['python', 'python3', 'py', 'python.exe']
        best_command = None
        
        for preferred in preferred_order:
            if preferred in working_commands:
                best_command = preferred
                break
        
        if not best_command:
            best_command = working_commands[0]
        
        # 環境別の実行方法を提案
        if env_type == 'windows':
            solution = {
                'type': 'windows',
                'message': f'Windows環境での推奨実行方法',
                'commands': [
                    f'# Windows PowerShell で実行:',
                    f'{best_command} app.py',
                    f'',
                    f'# または Windows コマンドプロンプトで実行:',
                    f'{best_command} app.py'
                ]
            }
        elif env_type == 'wsl':
            solution = {
                'type': 'wsl',
                'message': f'WSL環境での推奨実行方法',
                'commands': [
                    f'# WSL内で実行:',
                    f'{best_command} app.py',
                    f'',
                    f'# または Windows PowerShell で実行:',
                    f'powershell -Command "{best_command} app.py"'
                ]
            }
        else:
            solution = {
                'type': 'generic',
                'message': f'{env_type}環境での推奨実行方法',
                'commands': [
                    f'{best_command} app.py'
                ]
            }
        
        self.results['recommended_solution'] = solution
        return solution
    
    def run_full_diagnostic(self):
        """完全な診断を実行"""
        print("🔥 ULTRA SYNC環境診断開始...")
        print("=" * 60)
        
        # 基本情報
        print(f"プラットフォーム: {self.results['platform']}")
        print(f"Python バージョン: {self.results['python_version']}")
        print(f"実行ファイル: {self.results['executable_path']}")
        print(f"作業ディレクトリ: {self.results['working_directory']}")
        print()
        
        # 環境種別の特定
        env_type = self.detect_environment_type()
        print(f"環境種別: {env_type}")
        print()
        
        # Pythonコマンドの診断
        print("Pythonコマンド診断:")
        self.diagnose_python_commands()
        
        for cmd, info in self.results['available_commands'].items():
            status = "✅" if info['working'] else "❌"
            print(f"  {status} {cmd}: {info['version']}")
        print()
        
        # app.py実行テスト
        print("app.py実行テスト:")
        app_test = self.test_app_execution()
        
        if app_test['app_exists']:
            print("  ✅ app.py が見つかりました")
            for cmd, result in app_test.get('execution_results', {}).items():
                status = "✅" if result['success'] else "❌"
                print(f"  {status} {cmd} による実行: {'成功' if result['success'] else '失敗'}")
        else:
            print("  ❌ app.py が見つかりません")
        print()
        
        # 解決策の提案
        print("🎯 推奨解決策:")
        solution = self.generate_solution()
        print(f"  {solution['message']}")
        print()
        
        for command in solution['commands']:
            if command.startswith('#'):
                print(f"  {command}")
            else:
                print(f"    {command}")
        print()
        
        print("=" * 60)
        print("🔥 ULTRA SYNC環境診断完了")
        
        return self.results

def main():
    """メイン実行関数"""
    diagnostic = UltraSyncEnvironmentDiagnostic()
    results = diagnostic.run_full_diagnostic()
    
    # 結果をファイルに保存
    import json
    with open('ultrasync_environment_diagnostic_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print("\n診断結果を 'ultrasync_environment_diagnostic_results.json' に保存しました")

if __name__ == '__main__':
    main()