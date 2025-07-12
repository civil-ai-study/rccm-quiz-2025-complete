#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
【ULTRASYNC総合デバッグ】全体俯瞰・詳細分析・副作用防止
プログラム改良のための包括的デバッグシステム
"""

import os
import ast
import re
import json
import subprocess
from datetime import datetime
from collections import defaultdict

class UltraSyncComprehensiveDebugger:
    """ULTRASYNC総合デバッグシステム"""
    
    def __init__(self):
        self.debug_report = {
            "timestamp": datetime.now().isoformat(),
            "overview": {},
            "detailed_analysis": {},
            "side_effects_check": {},
            "improvement_recommendations": []
        }
        
    def analyze_overall_architecture(self):
        """全体アーキテクチャ俯瞰分析"""
        print("🔍 【全体俯瞰】アーキテクチャ分析開始")
        print("=" * 60)
        
        architecture_analysis = {
            "app_py_structure": self._analyze_app_py_structure(),
            "utils_py_structure": self._analyze_utils_py_structure(),
            "data_layer_structure": self._analyze_data_layer(),
            "session_management": self._analyze_session_management(),
            "route_mapping": self._analyze_route_mapping(),
            "existing_functions": self._analyze_existing_functions()
        }
        
        self.debug_report["overview"] = architecture_analysis
        return architecture_analysis
    
    def _analyze_app_py_structure(self):
        """app.py の構造詳細分析"""
        try:
            with open('app.py', 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 関数とルートの抽出
            functions = re.findall(r'def\s+(\w+)\s*\(', content)
            routes = re.findall(r'@app\.route\([\'"]([^\'"]+)[\'"]', content)
            imports = re.findall(r'^from\s+(\w+)\s+import', content, re.MULTILINE)
            
            # 新実装部分の確認
            new_implementation = {
                "csv_japanese_categories": "CSV_JAPANESE_CATEGORIES" in content,
                "get_department_questions_ultrasync": "get_department_questions_ultrasync" in content,
                "exam_department_ultrasync": "exam_department_ultrasync" in content,
                "departments_list_ultrasync": "departments_list_ultrasync" in content
            }
            
            return {
                "total_functions": len(functions),
                "total_routes": len(routes),
                "key_routes": routes,
                "imports": imports,
                "new_implementation": new_implementation,
                "file_size": len(content),
                "line_count": content.count('\n')
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def _analyze_utils_py_structure(self):
        """utils.py の構造分析"""
        try:
            with open('utils.py', 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 既存の重要関数確認
            key_functions = {
                "load_basic_questions_only": "load_basic_questions_only" in content,
                "load_specialist_questions_only": "load_specialist_questions_only" in content,
                "load_questions_improved": "load_questions_improved" in content,
                "validate_file_path": "validate_file_path" in content
            }
            
            return {
                "key_functions_available": key_functions,
                "redis_integration": "REDIS_CACHE_AVAILABLE" in content,
                "file_size": len(content)
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def _analyze_data_layer(self):
        """データ層の構造分析"""
        try:
            data_files = []
            if os.path.exists('data'):
                data_files = os.listdir('data')
            
            csv_analysis = {
                "basic_csv": "4-1.csv" in data_files,
                "specialist_csv_count": len([f for f in data_files if f.startswith('4-2_') and f.endswith('.csv')]),
                "specialist_years": [f.replace('4-2_', '').replace('.csv', '') for f in data_files if f.startswith('4-2_') and f.endswith('.csv')],
                "all_data_files": data_files
            }
            
            # CSVカテゴリーの実際の確認
            categories_found = set()
            try:
                if os.path.exists('data/4-1.csv'):
                    result = subprocess.run(['grep', '-h', '^[0-9]', 'data/4-1.csv'], 
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        for line in result.stdout.split('\n')[:5]:  # 最初の5行
                            if line:
                                parts = line.split(',')
                                if len(parts) > 1:
                                    categories_found.add(parts[1])
                
                # 専門科目のカテゴリー確認
                specialist_files = [f"data/{f}" for f in data_files if f.startswith('4-2_')][:3]  # 最初の3ファイル
                for csv_file in specialist_files:
                    result = subprocess.run(['grep', '-h', '^[0-9]', csv_file], 
                                          capture_output=True, text=True)
                    if result.returncode == 0:
                        for line in result.stdout.split('\n')[:10]:  # 最初の10行
                            if line:
                                parts = line.split(',')
                                if len(parts) > 1:
                                    categories_found.add(parts[1])
                                    
            except Exception as e:
                print(f"   ⚠️ CSV分析エラー: {e}")
            
            csv_analysis["actual_categories"] = list(categories_found)
            return csv_analysis
            
        except Exception as e:
            return {"error": str(e)}
    
    def _analyze_session_management(self):
        """セッション管理システム分析"""
        try:
            with open('app.py', 'r', encoding='utf-8') as f:
                content = f.read()
            
            session_features = {
                "lightweight_session_manager": "LightweightSessionManager" in content,
                "session_state_manager": "SessionStateManager" in content,
                "memory_storage": "store_exam_data_in_memory" in content,
                "session_clear_usage": content.count("session.clear()"),
                "session_modified_usage": content.count("session.modified = True")
            }
            
            return session_features
            
        except Exception as e:
            return {"error": str(e)}
    
    def _analyze_route_mapping(self):
        """ルートマッピング分析"""
        try:
            with open('app.py', 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 既存の重要ルート確認
            important_routes = {
                "/exam": "@app.route('/exam'" in content,
                "/start_exam": "@app.route('/start_exam" in content,
                "/exam_department": "@app.route('/exam_department" in content,
                "/departments_list": "@app.route('/departments_list'" in content,
                "/result": "@app.route('/result'" in content
            }
            
            # ルートの競合チェック
            exam_routes = re.findall(r'@app\.route\([\'"]([^\'"]*exam[^\'"]*)[\'"]', content)
            
            return {
                "important_routes": important_routes,
                "all_exam_routes": exam_routes,
                "route_conflicts": self._check_route_conflicts(exam_routes)
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def _check_route_conflicts(self, routes):
        """ルート競合チェック"""
        conflicts = []
        for i, route1 in enumerate(routes):
            for j, route2 in enumerate(routes[i+1:], i+1):
                if route1 == route2:
                    conflicts.append(f"重複: {route1}")
                elif route1.startswith(route2) or route2.startswith(route1):
                    conflicts.append(f"競合可能性: {route1} vs {route2}")
        return conflicts
    
    def _analyze_existing_functions(self):
        """既存関数の詳細分析"""
        try:
            with open('app.py', 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 重要な既存関数の確認
            key_functions = {
                "exam": "def exam():" in content,
                "start_exam": "def start_exam(" in content,
                "load_questions_from_lightweight_session": "def load_questions_from_lightweight_session" in content,
                "safe_post_processing": "safe_post_processing" in content
            }
            
            return key_functions
            
        except Exception as e:
            return {"error": str(e)}
    
    def check_side_effects(self):
        """副作用の詳細チェック"""
        print("\n🔍 【副作用チェック】詳細分析")
        print("=" * 60)
        
        side_effects_analysis = {
            "import_conflicts": self._check_import_conflicts(),
            "function_name_conflicts": self._check_function_name_conflicts(),
            "variable_name_conflicts": self._check_variable_name_conflicts(),
            "session_variable_conflicts": self._check_session_variable_conflicts(),
            "route_parameter_conflicts": self._check_route_parameter_conflicts(),
            "memory_management_issues": self._check_memory_management()
        }
        
        self.debug_report["side_effects_check"] = side_effects_analysis
        return side_effects_analysis
    
    def _check_import_conflicts(self):
        """インポート競合チェック"""
        try:
            with open('app.py', 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 重複インポートチェック
            imports = re.findall(r'^(?:from\s+\w+\s+)?import\s+([^\n]+)', content, re.MULTILINE)
            import_counts = defaultdict(int)
            for imp in imports:
                import_counts[imp.strip()] += 1
            
            duplicates = {k: v for k, v in import_counts.items() if v > 1}
            
            return {
                "duplicate_imports": duplicates,
                "total_imports": len(imports),
                "utils_imports": len([i for i in imports if 'utils' in i])
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def _check_function_name_conflicts(self):
        """関数名競合チェック"""
        try:
            with open('app.py', 'r', encoding='utf-8') as f:
                content = f.read()
            
            functions = re.findall(r'def\s+(\w+)\s*\(', content)
            function_counts = defaultdict(int)
            for func in functions:
                function_counts[func] += 1
            
            duplicates = {k: v for k, v in function_counts.items() if v > 1}
            
            # 新実装関数と既存関数の競合チェック
            new_functions = ["get_department_questions_ultrasync", "exam_department_ultrasync", "departments_list_ultrasync"]
            existing_conflicts = []
            for new_func in new_functions:
                if new_func.replace("_ultrasync", "") in functions:
                    existing_conflicts.append(new_func)
            
            return {
                "duplicate_functions": duplicates,
                "total_functions": len(functions),
                "new_function_conflicts": existing_conflicts
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def _check_variable_name_conflicts(self):
        """変数名競合チェック"""
        try:
            with open('app.py', 'r', encoding='utf-8') as f:
                content = f.read()
            
            # グローバル変数の確認
            global_vars = re.findall(r'^(\w+)\s*=', content, re.MULTILINE)
            
            # 新実装の変数
            new_variables = ["CSV_JAPANESE_CATEGORIES"]
            conflicts = []
            
            for new_var in new_variables:
                if global_vars.count(new_var) > 1:
                    conflicts.append(new_var)
            
            return {
                "global_variables": len(set(global_vars)),
                "new_variable_conflicts": conflicts,
                "csv_categories_defined": "CSV_JAPANESE_CATEGORIES" in content
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def _check_session_variable_conflicts(self):
        """セッション変数競合チェック"""
        try:
            with open('app.py', 'r', encoding='utf-8') as f:
                content = f.read()
            
            # セッション変数の使用パターン
            session_vars = re.findall(r'session\[[\'"]([^\'"]+)[\'"]\]', content)
            session_var_counts = defaultdict(int)
            for var in session_vars:
                session_var_counts[var] += 1
            
            # 新実装で追加されるセッション変数
            new_session_vars = ["department_name"]
            
            return {
                "session_variables": dict(session_var_counts),
                "new_session_variables": new_session_vars,
                "session_usage_count": len(session_vars)
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def _check_route_parameter_conflicts(self):
        """ルートパラメータ競合チェック"""
        try:
            with open('app.py', 'r', encoding='utf-8') as f:
                content = f.read()
            
            # パラメータ付きルートの確認
            param_routes = re.findall(r'@app\.route\([\'"]([^\'"]*<[^>]+>[^\'"]*)[\'"]', content)
            
            # 新実装ルート
            new_route = "/exam_department/<department_name>"
            
            return {
                "parametered_routes": param_routes,
                "new_route_conflicts": [route for route in param_routes if "department" in route and route != new_route]
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def _check_memory_management(self):
        """メモリ管理問題チェック"""
        try:
            with open('app.py', 'r', encoding='utf-8') as f:
                content = f.read()
            
            memory_patterns = {
                "store_exam_data_calls": content.count("store_exam_data_in_memory"),
                "memory_decorator_usage": content.count("@memory_monitoring_decorator"),
                "session_clear_calls": content.count("session.clear()"),
                "gc_collect_calls": content.count("gc.collect()")
            }
            
            return memory_patterns
            
        except Exception as e:
            return {"error": str(e)}
    
    def detailed_implementation_analysis(self):
        """実装の詳細分析"""
        print("\n🔍 【詳細実装分析】新機能の統合度チェック")
        print("=" * 60)
        
        implementation_analysis = {
            "new_function_integration": self._analyze_new_function_integration(),
            "csv_category_mapping": self._analyze_csv_category_mapping(),
            "error_handling": self._analyze_error_handling(),
            "logging_consistency": self._analyze_logging_consistency(),
            "session_integration": self._analyze_session_integration()
        }
        
        self.debug_report["detailed_analysis"] = implementation_analysis
        return implementation_analysis
    
    def _analyze_new_function_integration(self):
        """新機能の統合度分析"""
        try:
            with open('app.py', 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 新実装関数の統合度チェック
            integration_check = {
                "uses_existing_utils": "from utils import" in content.split("def get_department_questions_ultrasync")[1].split("def exam_department_ultrasync")[0],
                "uses_existing_session_manager": "LightweightSessionManager.save_minimal_session" in content,
                "uses_existing_memory_storage": "store_exam_data_in_memory" in content.split("def exam_department_ultrasync")[1] if "def exam_department_ultrasync" in content else False,
                "redirects_to_existing_exam": "redirect(url_for('exam'))" in content.split("def exam_department_ultrasync")[1] if "def exam_department_ultrasync" in content else False
            }
            
            return integration_check
            
        except Exception as e:
            return {"error": str(e)}
    
    def _analyze_csv_category_mapping(self):
        """CSVカテゴリーマッピング分析"""
        try:
            with open('app.py', 'r', encoding='utf-8') as f:
                content = f.read()
            
            # CSVカテゴリーマッピングの確認
            if "CSV_JAPANESE_CATEGORIES" in content:
                csv_section = content.split("CSV_JAPANESE_CATEGORIES = {")[1].split("}")[0]
                
                # マッピングの解析
                mappings = re.findall(r'"([^"]+)":\s*"([^"]+)"', csv_section)
                
                return {
                    "mapping_count": len(mappings),
                    "basic_subject_mapped": any("基礎科目" in m[0] for m in mappings),
                    "specialist_subjects_count": len([m for m in mappings if m[0] != "基礎科目"]),
                    "japanese_only": all(not re.search(r'[a-zA-Z]', m[1]) for m in mappings),
                    "sample_mappings": mappings[:5]
                }
            else:
                return {"csv_categories_found": False}
                
        except Exception as e:
            return {"error": str(e)}
    
    def _analyze_error_handling(self):
        """エラーハンドリング分析"""
        try:
            with open('app.py', 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 新実装のエラーハンドリング確認
            new_implementation_section = ""
            if "def exam_department_ultrasync" in content:
                new_implementation_section = content.split("def exam_department_ultrasync")[1].split("def ")[0]
            
            error_handling = {
                "try_except_blocks": new_implementation_section.count("try:"),
                "specific_exceptions": new_implementation_section.count("except Exception as e:"),
                "error_template_usage": "render_template('error.html'" in new_implementation_section,
                "logger_error_usage": "logger.error" in new_implementation_section,
                "validation_checks": new_implementation_section.count("if") + new_implementation_section.count("not")
            }
            
            return error_handling
            
        except Exception as e:
            return {"error": str(e)}
    
    def _analyze_logging_consistency(self):
        """ログ一貫性分析"""
        try:
            with open('app.py', 'r', encoding='utf-8') as f:
                content = f.read()
            
            # ログレベルの使用状況
            log_levels = {
                "logger.info": content.count("logger.info"),
                "logger.error": content.count("logger.error"),
                "logger.warning": content.count("logger.warning"),
                "logger.debug": content.count("logger.debug")
            }
            
            # 新実装でのログ使用
            new_section = ""
            if "def get_department_questions_ultrasync" in content:
                new_section = content.split("def get_department_questions_ultrasync")[1]
            
            new_logging = {
                "info_logs": new_section.count("logger.info"),
                "error_logs": new_section.count("logger.error"),
                "warning_logs": new_section.count("logger.warning"),
                "uses_emoji_prefixes": "🎯" in new_section or "✅" in new_section or "❌" in new_section
            }
            
            return {
                "overall_logging": log_levels,
                "new_implementation_logging": new_logging
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def _analyze_session_integration(self):
        """セッション統合分析"""
        try:
            with open('app.py', 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 新実装でのセッション使用
            new_section = ""
            if "def exam_department_ultrasync" in content:
                new_section = content.split("def exam_department_ultrasync")[1].split("def ")[0]
            
            session_usage = {
                "session_assignments": new_section.count("session["),
                "session_modified_set": "session.modified = True" in new_section,
                "lightweight_session_usage": "LightweightSessionManager" in new_section,
                "memory_storage_usage": "store_exam_data_in_memory" in new_section,
                "existing_session_vars_used": ["exam_id", "exam_question_ids", "exam_current"]
            }
            
            # 既存セッション変数との互換性
            existing_session_vars = re.findall(r'session\[[\'"]([^\'"]+)[\'"]\]', content)
            new_session_vars = re.findall(r'session\[[\'"]([^\'"]+)[\'"]\]', new_section)
            
            session_usage["compatible_with_existing"] = all(var in existing_session_vars for var in new_session_vars if var != "department_name")
            
            return session_usage
            
        except Exception as e:
            return {"error": str(e)}
    
    def generate_improvement_recommendations(self):
        """改良推奨事項の生成"""
        print("\n🔍 【改良推奨事項】プログラム品質向上のために")
        print("=" * 60)
        
        recommendations = []
        
        # 俯瞰分析結果に基づく推奨事項
        overview = self.debug_report.get("overview", {})
        side_effects = self.debug_report.get("side_effects_check", {})
        detailed = self.debug_report.get("detailed_analysis", {})
        
        # 1. ルート競合チェック
        route_conflicts = overview.get("route_mapping", {}).get("route_conflicts", [])
        if route_conflicts:
            recommendations.append({
                "priority": "高",
                "category": "ルート競合",
                "issue": f"ルート競合が検出されました: {route_conflicts}",
                "recommendation": "競合するルートの整理またはルートパターンの変更を検討してください。",
                "action": "ルート設計の見直し"
            })
        
        # 2. 関数名重複チェック
        function_conflicts = side_effects.get("function_name_conflicts", {}).get("duplicate_functions", {})
        if function_conflicts:
            recommendations.append({
                "priority": "高",
                "category": "関数名重複",
                "issue": f"関数名の重複: {function_conflicts}",
                "recommendation": "重複する関数名を一意な名前に変更してください。",
                "action": "関数名の変更"
            })
        
        # 3. セッション管理一貫性
        session_integration = detailed.get("session_integration", {})
        if not session_integration.get("compatible_with_existing", True):
            recommendations.append({
                "priority": "中",
                "category": "セッション管理",
                "issue": "新実装のセッション変数が既存システムと非互換の可能性",
                "recommendation": "セッション変数の命名と使用方法を既存システムに合わせてください。",
                "action": "セッション統合の改善"
            })
        
        # 4. エラーハンドリング強化
        error_handling = detailed.get("error_handling", {})
        if error_handling.get("try_except_blocks", 0) < 2:
            recommendations.append({
                "priority": "中",
                "category": "エラーハンドリング",
                "issue": "新実装でのエラーハンドリングが不十分",
                "recommendation": "包括的なtry-catch文とエラーログを追加してください。",
                "action": "エラーハンドリングの強化"
            })
        
        # 5. メモリ管理
        memory_issues = side_effects.get("memory_management_issues", {})
        if memory_issues.get("store_exam_data_calls", 0) > 5:
            recommendations.append({
                "priority": "低",
                "category": "メモリ管理",
                "issue": "メモリストレージの頻繁な使用",
                "recommendation": "メモリ使用量の監視と適切なクリーンアップを実装してください。",
                "action": "メモリ管理の最適化"
            })
        
        # 6. CSV整合性チェック
        csv_mapping = detailed.get("csv_category_mapping", {})
        if not csv_mapping.get("japanese_only", True):
            recommendations.append({
                "priority": "高",
                "category": "データ整合性",
                "issue": "CSVカテゴリーマッピングに英語が含まれている可能性",
                "recommendation": "すべてのカテゴリー名を日本語に統一してください。",
                "action": "カテゴリー名の日本語化"
            })
        
        self.debug_report["improvement_recommendations"] = recommendations
        return recommendations
    
    def generate_debug_report(self):
        """総合デバッグレポート生成"""
        print("\n📋 【総合デバッグレポート】生成中...")
        
        # 全分析の実行
        overview = self.analyze_overall_architecture()
        side_effects = self.check_side_effects()
        detailed = self.detailed_implementation_analysis()
        recommendations = self.generate_improvement_recommendations()
        
        # レポート保存
        report_filename = f"ultrasync_comprehensive_debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(self.debug_report, f, ensure_ascii=False, indent=2)
        
        # サマリー表示
        print("\n" + "=" * 80)
        print("🎯 【ULTRASYNC総合デバッグ】最終サマリー")
        print("=" * 80)
        
        print(f"📊 全体構造:")
        print(f"  ✅ 総ルート数: {overview.get('app_py_structure', {}).get('total_routes', 'N/A')}")
        print(f"  ✅ 総関数数: {overview.get('app_py_structure', {}).get('total_functions', 'N/A')}")
        print(f"  ✅ ファイルサイズ: {overview.get('app_py_structure', {}).get('file_size', 'N/A')} 文字")
        
        print(f"\n🔍 副作用チェック:")
        route_conflicts = side_effects.get('route_parameter_conflicts', {}).get('new_route_conflicts', [])
        function_conflicts = side_effects.get('function_name_conflicts', {}).get('duplicate_functions', {})
        print(f"  {'✅' if not route_conflicts else '⚠️'} ルート競合: {len(route_conflicts)}件")
        print(f"  {'✅' if not function_conflicts else '⚠️'} 関数名重複: {len(function_conflicts)}件")
        
        print(f"\n📋 改良推奨事項:")
        high_priority = len([r for r in recommendations if r.get('priority') == '高'])
        medium_priority = len([r for r in recommendations if r.get('priority') == '中'])
        low_priority = len([r for r in recommendations if r.get('priority') == '低'])
        print(f"  🔴 高優先度: {high_priority}件")
        print(f"  🟡 中優先度: {medium_priority}件")
        print(f"  🟢 低優先度: {low_priority}件")
        
        if recommendations:
            print(f"\n🚨 重要な推奨事項:")
            for rec in recommendations[:3]:  # 上位3つ
                print(f"  [{rec['priority']}] {rec['category']}: {rec['recommendation']}")
        
        print(f"\n📋 詳細レポート保存: {report_filename}")
        
        return {
            "report_file": report_filename,
            "summary": {
                "total_routes": overview.get('app_py_structure', {}).get('total_routes', 0),
                "total_functions": overview.get('app_py_structure', {}).get('total_functions', 0),
                "route_conflicts": len(route_conflicts),
                "function_conflicts": len(function_conflicts),
                "recommendations": len(recommendations),
                "high_priority_issues": high_priority
            }
        }

def main():
    """メイン実行関数"""
    print("🔍 【ULTRASYNC総合デバッグ】開始")
    print("全体俯瞰・詳細分析・副作用防止・プログラム改良")
    print("=" * 80)
    
    debugger = UltraSyncComprehensiveDebugger()
    final_report = debugger.generate_debug_report()
    
    return final_report

if __name__ == "__main__":
    result = main()
    print(f"\n🎯 デバッグ完了: {result}")