#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ULTRASYNC 4問目終了問題 根本原因調査ツール
Created: 2025-07-25
Purpose: get_user_session_size()が4を返す原因を特定し修正
"""

import sys
import os
import json
from datetime import datetime
import traceback

# アプリケーションのパスを追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class UltrasyncSessionSizeInvestigator:
    """ULTRASYNC セッションサイズ問題調査器"""
    
    def __init__(self):
        self.test_results = []
        self.issues_found = []
        self.session_samples = []
        
    def log_status(self, category: str, level: str, message: str):
        """調査ステータスログ出力"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {category}: {level} - {message}"
        print(log_message)
        
        if level == "CRITICAL":
            self.issues_found.append(message)
    
    def investigate_get_user_session_size_function(self):
        """get_user_session_size関数の詳細調査"""
        try:
            from app import get_user_session_size
            
            self.log_status("FUNCTION", "INFO", "get_user_session_size関数をインポート成功")
            
            # 様々なセッション状態でテスト
            test_sessions = [
                # 1. 空のセッション
                {},
                
                # 2. quiz_settingsなし
                {'other_data': 'test'},
                
                # 3. quiz_settingsが空
                {'quiz_settings': {}},
                
                # 4. questions_per_sessionなし
                {'quiz_settings': {'other_setting': 'value'}},
                
                # 5. questions_per_session = 10 (正常)
                {'quiz_settings': {'questions_per_session': 10}},
                
                # 6. questions_per_session = 20
                {'quiz_settings': {'questions_per_session': 20}},
                
                # 7. questions_per_session = 30
                {'quiz_settings': {'questions_per_session': 30}},
                
                # 8. questions_per_session = 4 (問題のケース)
                {'quiz_settings': {'questions_per_session': 4}},
                
                # 9. 異常値
                {'quiz_settings': {'questions_per_session': 'invalid'}},
                
                # 10. Noneパターン
                {'quiz_settings': {'questions_per_session': None}},
            ]
            
            results = []
            for i, test_session in enumerate(test_sessions):
                try:
                    result_size = get_user_session_size(test_session)
                    test_result = {
                        'test_number': i + 1,
                        'input_session': test_session,
                        'returned_size': result_size,
                        'expected_default': 10,
                        'is_problematic': result_size == 4
                    }
                    results.append(test_result)
                    
                    if result_size == 4:
                        self.log_status("FUNCTION", "CRITICAL", f"テスト{i+1}: セッションサイズ4を返しました - {test_session}")
                    elif result_size != 10 and test_session.get('quiz_settings', {}).get('questions_per_session') != result_size:
                        self.log_status("FUNCTION", "WARNING", f"テスト{i+1}: 予期しないサイズ{result_size} - {test_session}")
                    else:
                        self.log_status("FUNCTION", "SUCCESS", f"テスト{i+1}: 正常サイズ{result_size}")
                        
                except Exception as e:
                    results.append({
                        'test_number': i + 1,
                        'input_session': test_session,
                        'error': str(e),
                        'is_problematic': True
                    })
                    self.log_status("FUNCTION", "ERROR", f"テスト{i+1}例外: {e}")
            
            return results
            
        except Exception as e:
            self.log_status("FUNCTION", "CRITICAL", f"get_user_session_size関数調査失敗: {e}")
            return []
    
    def investigate_session_initialization_paths(self):
        """セッション初期化パスの調査"""
        try:
            # アプリケーションのテストクライアントで実際のHTTPリクエストをテスト
            from app import app
            
            with app.test_client() as client:
                test_scenarios = [
                    {
                        'name': 'ホームページアクセス',
                        'method': 'GET',
                        'url': '/'
                    },
                    {
                        'name': '基礎科目開始',
                        'method': 'POST',
                        'url': '/start_quiz',
                        'data': {'question_type': 'basic'}
                    },
                    {
                        'name': '道路部門開始',
                        'method': 'POST',
                        'url': '/start_quiz',
                        'data': {'department': '道路', 'question_type': 'specialist'}
                    },
                    {
                        'name': 'トンネル部門開始',
                        'method': 'POST', 
                        'url': '/start_quiz',
                        'data': {'department': 'トンネル', 'question_type': 'specialist'}
                    }
                ]
                
                session_investigation_results = []
                
                for scenario in test_scenarios:
                    try:
                        if scenario['method'] == 'GET':
                            response = client.get(scenario['url'])
                        else:
                            response = client.post(scenario['url'], data=scenario.get('data', {}))
                        
                        # セッション状態を確認（Flask test clientでは直接アクセスできないため、レスポンスから推測）
                        scenario_result = {
                            'scenario': scenario['name'],
                            'status_code': response.status_code,
                            'response_type': 'redirect' if response.status_code in [301, 302] else 'page',
                            'has_error': response.status_code >= 400
                        }
                        
                        session_investigation_results.append(scenario_result)
                        
                        if response.status_code >= 400:
                            self.log_status("SESSION", "WARNING", f"{scenario['name']}: エラーレスポンス {response.status_code}")
                        else:
                            self.log_status("SESSION", "SUCCESS", f"{scenario['name']}: 正常レスポンス {response.status_code}")
                            
                    except Exception as e:
                        session_investigation_results.append({
                            'scenario': scenario['name'],
                            'error': str(e)
                        })
                        self.log_status("SESSION", "ERROR", f"{scenario['name']} 失敗: {e}")
                
                return session_investigation_results
                
        except Exception as e:
            self.log_status("SESSION", "CRITICAL", f"セッション初期化調査失敗: {e}")
            return []
    
    def investigate_config_sources(self):
        """設定ファイルや環境変数での問題数設定調査"""
        try:
            config_investigation = {}
            
            # 1. 環境変数確認
            env_vars = {}
            for key in os.environ:
                if 'question' in key.lower() or 'session' in key.lower() or 'quiz' in key.lower():
                    env_vars[key] = os.environ[key]
            
            config_investigation['environment_variables'] = env_vars
            self.log_status("CONFIG", "INFO", f"環境変数: {len(env_vars)}個発見")
            
            # 2. 設定ファイル確認（存在する場合）
            config_files = ['config.py', 'settings.json', '.env']
            found_configs = {}
            
            for config_file in config_files:
                if os.path.exists(config_file):
                    try:
                        with open(config_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if '4' in content or 'question' in content.lower():
                                found_configs[config_file] = content[:500]  # 最初の500文字
                    except Exception as e:
                        found_configs[config_file] = f"読み込みエラー: {e}"
            
            config_investigation['config_files'] = found_configs
            self.log_status("CONFIG", "INFO", f"設定ファイル: {len(found_configs)}個確認")
            
            # 3. URLパラメータやフォームデータの初期値確認
            try:
                from app import app
                
                # アプリケーション設定確認
                app_config = {}
                for key in app.config:
                    if any(keyword in key.lower() for keyword in ['question', 'session', 'quiz', 'count']):
                        app_config[key] = app.config[key]
                
                config_investigation['app_config'] = app_config
                self.log_status("CONFIG", "INFO", f"アプリケーション設定: {len(app_config)}個発見")
                
            except Exception as e:
                config_investigation['app_config_error'] = str(e)
                self.log_status("CONFIG", "ERROR", f"アプリ設定取得失敗: {e}")
            
            return config_investigation
            
        except Exception as e:
            self.log_status("CONFIG", "CRITICAL", f"設定調査失敗: {e}")
            return {}
    
    def generate_investigation_report(self):
        """調査レポート生成"""
        try:
            self.log_status("MAIN", "INFO", "ULTRASYNC 4問目終了問題 調査開始")
            
            # 1. 関数レベル調査
            function_results = self.investigate_get_user_session_size_function()
            
            # 2. セッション初期化調査
            session_results = self.investigate_session_initialization_paths()
            
            # 3. 設定値調査
            config_results = self.investigate_config_sources()
            
            # レポート作成
            report = {
                'timestamp': datetime.now().isoformat(),
                'investigation_summary': {
                    'function_tests_count': len(function_results),
                    'problematic_cases_found': len([r for r in function_results if r.get('is_problematic', False)]),
                    'session_scenarios_tested': len(session_results),
                    'critical_issues': len(self.issues_found)
                },
                'function_level_investigation': function_results,
                'session_initialization_investigation': session_results,
                'configuration_investigation': config_results,
                'critical_issues': self.issues_found,
                'recommendations': []
            }
            
            # 推奨事項生成
            problematic_cases = [r for r in function_results if r.get('is_problematic', False)]
            if problematic_cases:
                report['recommendations'].append("セッションサイズ4を返すケースが発見されました - 緊急修正が必要")
            
            if self.issues_found:
                report['recommendations'].append("重要な問題が検出されました - 詳細な修正が必要")
            
            if not problematic_cases and not self.issues_found:
                report['recommendations'].append("関数レベルでは問題なし - 他の要因を調査")
            
            return report
            
        except Exception as e:
            self.log_status("MAIN", "CRITICAL", f"調査レポート生成失敗: {e}")
            return {'error': str(e)}
    
    def run_ultrasync_session_size_investigation(self):
        """ULTRASYNC セッションサイズ調査実行"""
        print("ULTRASYNC Session Size Investigation Starting")
        print("Investigating why sessions end at question 4 instead of 10\\n")
        
        try:
            report = self.generate_investigation_report()
            
            # レポート保存
            report_file = f"ultrasync_session_size_investigation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            print(f"\\n調査レポート保存: {report_file}")
            
            # 要約表示
            print("\\n" + "="*60)
            print("ULTRASYNC Session Size Investigation Summary")
            print("="*60)
            
            if 'investigation_summary' in report:
                summary = report['investigation_summary']
                print(f"関数テスト実行: {summary.get('function_tests_count', 0)}件")
                print(f"問題のケース: {summary.get('problematic_cases_found', 0)}件")
                print(f"重要な問題: {summary.get('critical_issues', 0)}件")
            
            if self.issues_found:
                print("\\n重要な問題:")
                for issue in self.issues_found:
                    print(f"  - {issue}")
            
            return len(self.issues_found) == 0
            
        except Exception as e:
            self.log_status("MAIN", "CRITICAL", f"調査実行失敗: {e}")
            return False

def main():
    """メイン実行関数"""
    investigator = UltrasyncSessionSizeInvestigator()
    
    try:
        success = investigator.run_ultrasync_session_size_investigation()
        
        if success:
            print("\\n調査完了: 重要な問題は検出されませんでした")
            return 0
        else:
            print("\\n調査完了: 重要な問題が検出されました - 修正が必要です")
            return 1
            
    except KeyboardInterrupt:
        print("\\n調査が中断されました")
        return 1
    except Exception as e:
        print(f"\\n予期しないエラー: {e}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())