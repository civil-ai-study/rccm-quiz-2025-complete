#!/usr/bin/env python3
"""
🔍 包括的エラーハンティングシステム
様々な手法でエラーを徹底的に発見する
"""

import os
import re
import csv
import json
import time
import subprocess
from collections import defaultdict, Counter

class ErrorHunter:
    def __init__(self, project_dir):
        self.project_dir = project_dir
        self.errors = []
        self.warnings = []
        
    def add_error(self, category, message, severity="ERROR"):
        self.errors.append({
            'category': category,
            'message': message,
            'severity': severity,
            'timestamp': time.time()
        })
        
    def hunt_template_errors(self):
        """テンプレートファイルのエラー検出"""
        print("🔍 テンプレートエラーハンティング")
        
        template_dir = os.path.join(self.project_dir, 'templates')
        
        for file in os.listdir(template_dir):
            if file.endswith('.html'):
                file_path = os.path.join(template_dir, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # 未定義変数の可能性
                undefined_vars = re.findall(r'{{\s*(\w+)(?:\.\w+)*\s*}}', content)
                var_counts = Counter(undefined_vars)
                
                # 1回しか使われない変数（typoの可能性）
                single_use = [var for var, count in var_counts.items() if count == 1]
                if single_use:
                    self.add_error("TEMPLATE", f"{file}: 1回のみ使用変数（typo可能性）: {single_use[:3]}")
                    
                # 閉じタグ不整合
                open_tags = re.findall(r'<(\w+)[^>]*>', content)
                close_tags = re.findall(r'</(\w+)>', content)
                
                tag_diff = set(open_tags) - set(close_tags)
                if tag_diff:
                    self.add_error("TEMPLATE", f"{file}: 閉じタグなし: {list(tag_diff)[:3]}")
                    
                # JavaScriptエラーの可能性
                js_console = re.findall(r'console\.(log|error|warn)', content)
                if js_console:
                    self.add_error("TEMPLATE", f"{file}: 本番用console残存: {len(js_console)}箇所")
    
    def hunt_route_conflicts(self):
        """ルート競合エラー検出"""
        print("🔍 ルート競合エラーハンティング")
        
        app_file = os.path.join(self.project_dir, 'app.py')
        with open(app_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # ルート定義を抽出
        routes = re.findall(r'@app\.route\([\'"]([^\'\"]+)[\'"](?:,\s*methods=\[([^\]]+)\])?\)', content)
        
        route_map = defaultdict(list)
        for route, methods in routes:
            methods_list = methods.split(',') if methods else ['GET']
            for method in methods_list:
                method = method.strip().strip('\'"')
                route_map[route].append(method)
        
        # 重複ルート検出
        for route, methods in route_map.items():
            method_counts = Counter(methods)
            duplicates = [method for method, count in method_counts.items() if count > 1]
            if duplicates:
                self.add_error("ROUTE", f"重複ルート: {route} - {duplicates}")
                
        # 似たようなルートパターン（typoの可能性）
        route_list = list(route_map.keys())
        for i, route1 in enumerate(route_list):
            for route2 in route_list[i+1:]:
                if self.similarity_ratio(route1, route2) > 0.8:
                    self.add_error("ROUTE", f"類似ルート（typo可能性）: {route1} vs {route2}")
    
    def hunt_session_inconsistencies(self):
        """セッション不整合エラー検出"""
        print("🔍 セッション不整合エラーハンティング")
        
        app_file = os.path.join(self.project_dir, 'app.py')
        with open(app_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # セッション変数の使用パターン
        session_reads = re.findall(r'session\.get\([\'"]([^\'"]+)[\'"]', content)
        session_writes = re.findall(r'session\[[\'"]([^\'"]+)[\'"]\]\s*=', content)
        
        read_only = set(session_reads) - set(session_writes)
        write_only = set(session_writes) - set(session_reads)
        
        if read_only:
            self.add_error("SESSION", f"読み取り専用セッション変数: {list(read_only)[:5]}")
        if write_only:
            self.add_error("SESSION", f"書き込み専用セッション変数: {list(write_only)[:5]}")
            
        # デフォルト値の不整合
        session_defaults = {}
        for match in re.finditer(r'session\.get\([\'"]([^\'"]+)[\'"],\s*([^)]+)\)', content):
            var, default = match.groups()
            if var in session_defaults and session_defaults[var] != default:
                self.add_error("SESSION", f"セッション変数デフォルト値不整合: {var}")
            session_defaults[var] = default
    
    def hunt_data_corruption(self):
        """データ破損エラー検出"""
        print("🔍 データ破損エラーハンティング")
        
        data_dir = os.path.join(self.project_dir, 'data')
        
        # CSVファイルの整合性チェック
        expected_headers = {
            '4-1.csv': ['id', 'category', 'question', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer', 'explanation'],
            '4-2_*.csv': ['id', 'category', 'year', 'question', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer', 'explanation', 'reference', 'difficulty']
        }
        
        for file in os.listdir(data_dir):
            if file.endswith('.csv'):
                file_path = os.path.join(data_dir, file)
                try:
                    # エンコーディング検出
                    encodings = ['utf-8', 'shift_jis', 'cp932', 'utf-8-sig']
                    content = None
                    used_encoding = None
                    
                    for encoding in encodings:
                        try:
                            with open(file_path, 'r', encoding=encoding) as f:
                                content = f.read()
                                used_encoding = encoding
                                break
                        except UnicodeDecodeError:
                            continue
                    
                    if content is None:
                        self.add_error("DATA", f"{file}: エンコーディング読み取り不可")
                        continue
                        
                    # ヘッダー行チェック
                    lines = content.split('\n')
                    if len(lines) < 2:
                        self.add_error("DATA", f"{file}: データが空または不完全")
                        continue
                        
                    headers = [h.strip().lower() for h in lines[0].split(',')]
                    
                    # データ行の不整合チェック
                    for i, line in enumerate(lines[1:], 2):
                        if line.strip():
                            cols = line.split(',')
                            if len(cols) != len(headers):
                                self.add_error("DATA", f"{file}:{i}行目: カラム数不整合 (期待:{len(headers)}, 実際:{len(cols)})")
                                break  # 最初のエラーのみ報告
                                
                    # 文字化け検出
                    if '?' in content or '�' in content:
                        self.add_error("DATA", f"{file}: 文字化け検出 (エンコーディング: {used_encoding})")
                        
                except Exception as e:
                    self.add_error("DATA", f"{file}: 読み取りエラー - {e}")
    
    def hunt_logic_errors(self):
        """論理エラー検出"""
        print("🔍 論理エラーハンティング")
        
        app_file = os.path.join(self.project_dir, 'app.py')
        with open(app_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 無限ループの可能性
        while_loops = re.findall(r'while\s+.*?:', content)
        for loop in while_loops:
            if 'break' not in loop and 'return' not in loop:
                self.add_error("LOGIC", f"無限ループの可能性: {loop}")
                
        # デッドコード検出
        if_false = re.findall(r'if\s+False\s*:', content)
        if if_false:
            self.add_error("LOGIC", f"到達不能コード: {len(if_false)}箇所")
            
        # 変数使用前定義チェック
        lines = content.split('\n')
        in_function = False
        local_vars = set()
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if line.startswith('def '):
                in_function = True
                local_vars = set()
            elif line.startswith('class ') or (line.startswith('def ') and in_function):
                in_function = False
                
            if in_function:
                # 変数代入検出
                assignments = re.findall(r'(\w+)\s*=', line)
                local_vars.update(assignments)
                
                # 変数使用検出
                usage = re.findall(r'\b(\w+)\b', line)
                for var in usage:
                    if var not in local_vars and var not in ['self', 'session', 'request', 'app'] and var.islower():
                        self.add_error("LOGIC", f"行{line_num}: 未定義変数の可能性: {var}")
                        break  # 1行につき1エラーまで
    
    def hunt_performance_issues(self):
        """パフォーマンス問題検出"""
        print("🔍 パフォーマンス問題ハンティング")
        
        app_file = os.path.join(self.project_dir, 'app.py')
        with open(app_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # N+1クエリの可能性
        loops_with_db = re.findall(r'for\s+.*?:.*?(?:session\[|\.get\()', content, re.DOTALL)
        if loops_with_db:
            self.add_error("PERFORMANCE", f"N+1クエリの可能性: {len(loops_with_db)}箇所")
            
        # 大きなファイルの一括読み込み
        large_reads = re.findall(r'\.read\(\)', content)
        if large_reads:
            self.add_error("PERFORMANCE", f"大ファイル一括読み込み: {len(large_reads)}箇所")
            
        # 重複処理の可能性
        function_bodies = re.findall(r'def\s+(\w+).*?(?=def|\Z)', content, re.DOTALL)
        similar_functions = []
        for i, func1 in enumerate(function_bodies):
            for func2 in function_bodies[i+1:]:
                if self.similarity_ratio(func1, func2) > 0.7:
                    similar_functions.append((func1[:50], func2[:50]))
                    
        if similar_functions:
            self.add_error("PERFORMANCE", f"類似関数（重複処理可能性）: {len(similar_functions)}組")
    
    def similarity_ratio(self, s1, s2):
        """文字列類似度計算"""
        if not s1 or not s2:
            return 0
        common = sum(1 for a, b in zip(s1, s2) if a == b)
        return common / max(len(s1), len(s2))
    
    def generate_report(self):
        """エラーレポート生成"""
        print("\n" + "="*80)
        print("🎯 包括的エラーハンティング結果")
        print("="*80)
        
        error_by_category = defaultdict(list)
        for error in self.errors:
            error_by_category[error['category']].append(error)
            
        total_errors = len(self.errors)
        
        for category, errors in error_by_category.items():
            print(f"\n📂 {category}カテゴリ: {len(errors)}個のエラー")
            print("-" * 40)
            for error in errors[:5]:  # 最大5個まで表示
                print(f"❌ {error['message']}")
            if len(errors) > 5:
                print(f"... その他{len(errors)-5}個のエラー")
                
        print(f"\n📊 総エラー数: {total_errors}")
        
        if total_errors == 0:
            print("🎉 エラーは検出されませんでした")
            return True
        else:
            print("⚠️ 修正が必要なエラーが検出されました")
            return False

def main():
    project_dir = '/mnt/c/Users/ABC/Desktop/rccm-quiz-app/rccm-quiz-app'
    hunter = ErrorHunter(project_dir)
    
    # 様々な手法でエラーハンティング
    hunter.hunt_template_errors()
    hunter.hunt_route_conflicts()
    hunter.hunt_session_inconsistencies()
    hunter.hunt_data_corruption()
    hunter.hunt_logic_errors()
    hunter.hunt_performance_issues()
    
    # レポート生成
    success = hunter.generate_report()
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)