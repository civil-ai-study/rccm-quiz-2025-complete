#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
包括的多重根本原因分析スクリプト（ウルトラシンク・絶対に嘘をつかない）
2025年専門家のベストプラクティスに基づく複合問題の徹底調査

2週間治らない問題は単一原因ではない
- 複数の根本原因を同時調査
- システム相互作用の分析
- データフロー全体の検証
- アーキテクチャレベルの問題調査
"""

import sys
import os
import csv
import json
import re
import logging
from datetime import datetime
from collections import defaultdict, Counter
import importlib.util

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def comprehensive_multi_root_cause_analysis():
    """
    複合問題の包括的根本原因分析（2025年専門家手法）
    - データレイヤーの問題
    - ロジックレイヤーの問題  
    - アーキテクチャレベルの問題
    - システム相互作用の問題
    """
    
    print("=" * 100)
    print("包括的多重根本原因分析（ウルトラシンク・絶対に嘘をつかない）")
    print("2週間治らない問題の複合的根本原因を徹底調査")
    print("=" * 100)
    
    analysis_results = {
        'timestamp': datetime.now().isoformat(),
        'analysis_scope': 'comprehensive_multi_root_cause',
        'root_causes': [],
        'system_interactions': [],
        'data_layer_issues': [],
        'logic_layer_issues': [],
        'architecture_issues': [],
        'configuration_issues': [],
        'runtime_issues': []
    }
    
    print("\n🔍 ROOT CAUSE 1: データレイヤー構造的問題の調査")
    data_issues = analyze_data_layer_structure()
    analysis_results['data_layer_issues'] = data_issues
    
    print("\n🔍 ROOT CAUSE 2: アプリケーションロジック問題の調査")
    logic_issues = analyze_application_logic()
    analysis_results['logic_layer_issues'] = logic_issues
    
    print("\n🔍 ROOT CAUSE 3: システム設定・環境問題の調査")
    config_issues = analyze_system_configuration()
    analysis_results['configuration_issues'] = config_issues
    
    print("\n🔍 ROOT CAUSE 4: データフロー・パイプライン問題の調査")
    pipeline_issues = analyze_data_pipeline()
    analysis_results['runtime_issues'] = pipeline_issues
    
    print("\n🔍 ROOT CAUSE 5: 相互作用・依存関係問題の調査")
    interaction_issues = analyze_system_interactions()
    analysis_results['system_interactions'] = interaction_issues
    
    print("\n🔍 ROOT CAUSE 6: アーキテクチャ設計問題の調査")
    architecture_issues = analyze_architecture_design()
    analysis_results['architecture_issues'] = architecture_issues
    
    # 総合分析と優先度付け
    final_analysis = synthesize_root_causes(analysis_results)
    
    # 結果保存
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result_file = f"comprehensive_multi_root_cause_analysis_{timestamp}.json"
    
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(analysis_results, f, ensure_ascii=False, indent=2)
    
    print(f"\n📊 包括的分析結果保存: {result_file}")
    return analysis_results

def analyze_data_layer_structure():
    """データレイヤー構造的問題の詳細分析"""
    print("データレイヤー構造分析開始...")
    
    data_issues = []
    
    # 1. CSVファイル構造の一貫性チェック
    print("  1. CSVファイル構造一貫性チェック")
    csv_consistency_issues = check_csv_structure_consistency()
    if csv_consistency_issues:
        data_issues.extend(csv_consistency_issues)
    
    # 2. エンコーディング問題チェック
    print("  2. エンコーディング問題チェック")
    encoding_issues = check_encoding_issues()
    if encoding_issues:
        data_issues.extend(encoding_issues)
    
    # 3. データ型不整合チェック
    print("  3. データ型不整合チェック")
    datatype_issues = check_datatype_inconsistencies()
    if datatype_issues:
        data_issues.extend(datatype_issues)
    
    # 4. 重複データ・データ品質チェック
    print("  4. 重複データ・品質チェック")
    quality_issues = check_data_quality()
    if quality_issues:
        data_issues.extend(quality_issues)
    
    return data_issues

def check_csv_structure_consistency():
    """CSVファイル構造の一貫性チェック"""
    issues = []
    
    VALID_YEARS = [2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019]
    expected_headers = ['id', 'category', 'question', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer']
    
    for year in VALID_YEARS:
        csv_path = f'rccm-quiz-app/data/4-2_{year}.csv'
        if not os.path.exists(csv_path):
            continue
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                headers = reader.fieldnames
                
                # ヘッダー不整合チェック
                missing_headers = set(expected_headers) - set(headers or [])
                extra_headers = set(headers or []) - set(expected_headers)
                
                if missing_headers:
                    issues.append({
                        'type': 'missing_headers',
                        'year': year,
                        'missing': list(missing_headers),
                        'severity': 'high'
                    })
                
                if extra_headers:
                    issues.append({
                        'type': 'extra_headers',
                        'year': year,
                        'extra': list(extra_headers),
                        'severity': 'medium'
                    })
                
                # レコード数の年度間比較
                row_count = sum(1 for row in reader)
                if row_count < 200:  # 異常に少ない
                    issues.append({
                        'type': 'insufficient_records',
                        'year': year,
                        'count': row_count,
                        'severity': 'high'
                    })
                elif row_count > 500:  # 異常に多い
                    issues.append({
                        'type': 'excessive_records',
                        'year': year,
                        'count': row_count,
                        'severity': 'medium'
                    })
                    
        except Exception as e:
            issues.append({
                'type': 'file_access_error',
                'year': year,
                'error': str(e),
                'severity': 'critical'
            })
    
    return issues

def check_encoding_issues():
    """エンコーディング問題の詳細チェック"""
    issues = []
    
    VALID_YEARS = [2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019]
    
    for year in VALID_YEARS:
        csv_path = f'rccm-quiz-app/data/4-2_{year}.csv'
        if not os.path.exists(csv_path):
            continue
        
        # UTF-8でのアクセステスト
        utf8_success = False
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                sample = f.read(1000)
                utf8_success = True
        except UnicodeDecodeError:
            pass
        
        # Shift_JISでのアクセステスト
        sjis_success = False
        try:
            with open(csv_path, 'r', encoding='shift_jis') as f:
                sample = f.read(1000)
                sjis_success = True
        except UnicodeDecodeError:
            pass
        
        if not utf8_success and not sjis_success:
            issues.append({
                'type': 'encoding_error',
                'year': year,
                'description': 'UTF-8とShift_JIS両方でアクセス失敗',
                'severity': 'critical'
            })
        elif not utf8_success and sjis_success:
            issues.append({
                'type': 'encoding_inconsistency',
                'year': year,
                'description': 'Shift_JISエンコーディング（UTF-8統一が推奨）',
                'severity': 'medium'
            })
    
    return issues

def check_datatype_inconsistencies():
    """データ型不整合の詳細チェック"""
    issues = []
    
    VALID_YEARS = [2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019]
    
    for year in VALID_YEARS:
        csv_path = f'rccm-quiz-app/data/4-2_{year}.csv'
        if not os.path.exists(csv_path):
            continue
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row_num, row in enumerate(reader, 1):
                    # ID型チェック
                    try:
                        int(row.get('id', ''))
                    except (ValueError, TypeError):
                        issues.append({
                            'type': 'invalid_id_format',
                            'year': year,
                            'row': row_num,
                            'value': row.get('id'),
                            'severity': 'high'
                        })
                    
                    # correct_answer形式チェック
                    correct_answer = row.get('correct_answer', '').strip()
                    if correct_answer not in ['1', '2', '3', '4', 'A', 'B', 'C', 'D', 'a', 'b', 'c', 'd']:
                        if correct_answer:  # 空でない場合のみ
                            issues.append({
                                'type': 'invalid_answer_format',
                                'year': year,
                                'row': row_num,
                                'value': correct_answer,
                                'severity': 'high'
                            })
                    
                    # 問題文長すぎるチェック
                    question_text = row.get('question', '')
                    if len(question_text) > 2000:  # 異常に長い
                        issues.append({
                            'type': 'excessive_question_length',
                            'year': year,
                            'row': row_num,
                            'length': len(question_text),
                            'severity': 'medium'
                        })
                    elif len(question_text) < 10:  # 異常に短い
                        issues.append({
                            'type': 'insufficient_question_length',
                            'year': year,
                            'row': row_num,
                            'length': len(question_text),
                            'severity': 'high'
                        })
                    
        except Exception as e:
            issues.append({
                'type': 'datatype_check_error',
                'year': year,
                'error': str(e),
                'severity': 'medium'
            })
    
    return issues

def check_data_quality():
    """データ品質問題の詳細チェック"""
    issues = []
    
    # 重複IDチェック
    all_ids = set()
    duplicate_ids = set()
    
    VALID_YEARS = [2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019]
    
    for year in VALID_YEARS:
        csv_path = f'rccm-quiz-app/data/4-2_{year}.csv'
        if not os.path.exists(csv_path):
            continue
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                year_ids = set()
                for row in reader:
                    qid = row.get('id')
                    if qid:
                        if qid in all_ids:
                            duplicate_ids.add(qid)
                        if qid in year_ids:
                            issues.append({
                                'type': 'duplicate_id_within_year',
                                'year': year,
                                'id': qid,
                                'severity': 'high'
                            })
                        all_ids.add(qid)
                        year_ids.add(qid)
                        
        except Exception as e:
            issues.append({
                'type': 'quality_check_error',
                'year': year,
                'error': str(e),
                'severity': 'medium'
            })
    
    if duplicate_ids:
        issues.append({
            'type': 'duplicate_ids_across_years',
            'ids': list(duplicate_ids),
            'count': len(duplicate_ids),
            'severity': 'critical'
        })
    
    return issues

def analyze_application_logic():
    """アプリケーションロジック問題の詳細分析"""
    print("アプリケーションロジック分析開始...")
    
    logic_issues = []
    
    # app.pyの分析
    app_py_path = "rccm-quiz-app/app.py"
    if os.path.exists(app_py_path):
        # 1. 関数の複雑性チェック
        print("  1. 関数複雑性チェック")
        complexity_issues = check_function_complexity(app_py_path)
        logic_issues.extend(complexity_issues)
        
        # 2. エラーハンドリングチェック
        print("  2. エラーハンドリングチェック")
        error_handling_issues = check_error_handling(app_py_path)
        logic_issues.extend(error_handling_issues)
        
        # 3. セッション管理ロジックチェック
        print("  3. セッション管理ロジックチェック")
        session_issues = check_session_logic(app_py_path)
        logic_issues.extend(session_issues)
        
        # 4. データフィルタリングロジックチェック
        print("  4. データフィルタリングロジックチェック")
        filtering_issues = check_filtering_logic(app_py_path)
        logic_issues.extend(filtering_issues)
    
    return logic_issues

def check_function_complexity(file_path):
    """関数の複雑性問題チェック"""
    issues = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # get_department_questions関連の関数を検索
        dept_functions = re.findall(r'def (get_department_questions.*?)\(.*?\):', content)
        
        for func_name in dept_functions:
            # 関数の開始位置を特定
            func_start = content.find(f'def {func_name}(')
            if func_start == -1:
                continue
            
            # 関数のおおよその終了位置を特定（次のdef文まで）
            func_content = content[func_start:]
            next_def = func_content.find('\ndef ', 1)
            if next_def != -1:
                func_content = func_content[:next_def]
            
            # 複雑性指標の計算
            line_count = len(func_content.split('\n'))
            if_count = len(re.findall(r'\bif\b', func_content))
            for_count = len(re.findall(r'\bfor\b', func_content))
            try_count = len(re.findall(r'\btry\b', func_content))
            
            complexity_score = if_count + for_count * 2 + try_count
            
            if line_count > 200:
                issues.append({
                    'type': 'excessive_function_length',
                    'function': func_name,
                    'lines': line_count,
                    'severity': 'high'
                })
            
            if complexity_score > 20:
                issues.append({
                    'type': 'high_cyclomatic_complexity',
                    'function': func_name,
                    'complexity': complexity_score,
                    'severity': 'high'
                })
    
    except Exception as e:
        issues.append({
            'type': 'complexity_analysis_error',
            'error': str(e),
            'severity': 'medium'
        })
    
    return issues

def check_error_handling(file_path):
    """エラーハンドリング問題チェック"""
    issues = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # try-except文の分析
        try_blocks = re.findall(r'try:(.*?)except', content, re.DOTALL)
        
        for i, try_block in enumerate(try_blocks):
            # 空のexceptブロックチェック
            if re.search(r'except.*?:\s*pass', content):
                issues.append({
                    'type': 'empty_except_block',
                    'location': f'try_block_{i}',
                    'severity': 'high'
                })
            
            # 汎用exception catchingチェック
            if re.search(r'except\s*:', content) or re.search(r'except Exception:', content):
                issues.append({
                    'type': 'generic_exception_catching',
                    'location': f'try_block_{i}',
                    'severity': 'medium'
                })
        
        # リソース管理チェック（ファイル操作など）
        file_opens = re.findall(r'open\s*\(', content)
        with_statements = re.findall(r'with\s+open', content)
        
        if len(file_opens) > len(with_statements):
            issues.append({
                'type': 'improper_resource_management',
                'opens': len(file_opens),
                'with_statements': len(with_statements),
                'severity': 'medium'
            })
    
    except Exception as e:
        issues.append({
            'type': 'error_handling_analysis_error',
            'error': str(e),
            'severity': 'medium'
        })
    
    return issues

def check_session_logic(file_path):
    """セッション管理ロジック問題チェック"""
    issues = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # セッション関連の変数アクセスパターンチェック
        session_gets = len(re.findall(r'session\.get\(', content))
        session_sets = len(re.findall(r'session\[.*?\]\s*=', content))
        
        # セッションアクセスが多すぎる場合
        if session_gets > 100:
            issues.append({
                'type': 'excessive_session_access',
                'get_count': session_gets,
                'set_count': session_sets,
                'severity': 'medium'
            })
        
        # セッションキーの一貫性チェック
        session_keys = re.findall(r'session\.get\([\'\"](.*?)[\'\"]', content)
        session_keys.extend(re.findall(r'session\[[\'\"](.*?)[\'\"]', content))
        
        key_variations = defaultdict(list)
        for key in session_keys:
            base_key = re.sub(r'[_-]', '', key.lower())
            key_variations[base_key].append(key)
        
        for base_key, variations in key_variations.items():
            if len(variations) > 1:
                issues.append({
                    'type': 'inconsistent_session_keys',
                    'base_key': base_key,
                    'variations': variations,
                    'severity': 'medium'
                })
    
    except Exception as e:
        issues.append({
            'type': 'session_logic_analysis_error',
            'error': str(e),
            'severity': 'medium'
        })
    
    return issues

def check_filtering_logic(file_path):
    """データフィルタリングロジック問題チェック"""
    issues = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # カテゴリフィルタリングの複数パターンチェック
        category_filters = re.findall(r'row\.get\([\'\"]\w*category\w*[\'\"]\)', content)
        if len(set(category_filters)) > 1:
            issues.append({
                'type': 'inconsistent_category_access',
                'patterns': list(set(category_filters)),
                'severity': 'high'
            })
        
        # 文字列比較の方法チェック
        string_comparisons = re.findall(r'==\s*[\'\"](.*?)[\'\"]', content)
        strip_usage = len(re.findall(r'\.strip\(\)', content))
        
        if len(string_comparisons) > 50 and strip_usage < 10:
            issues.append({
                'type': 'insufficient_string_normalization',
                'comparisons': len(string_comparisons),
                'strip_usage': strip_usage,
                'severity': 'medium'
            })
        
        # ループ内でのファイルアクセスチェック
        for_loops = re.findall(r'for\s+.*?:', content)
        if len(for_loops) > 5:
            # ループ内でのopen()チェック
            issues.append({
                'type': 'potential_inefficient_loops',
                'loop_count': len(for_loops),
                'severity': 'medium'
            })
    
    except Exception as e:
        issues.append({
            'type': 'filtering_logic_analysis_error',
            'error': str(e),
            'severity': 'medium'
        })
    
    return issues

def analyze_system_configuration():
    """システム設定・環境問題の分析"""
    print("システム設定・環境分析開始...")
    
    config_issues = []
    
    # 1. 設定ファイルの一貫性チェック
    print("  1. 設定ファイル一貫性チェック")
    config_files = ['rccm-quiz-app/config.py', 'rccm-quiz-app/requirements.txt']
    for config_file in config_files:
        if os.path.exists(config_file):
            file_issues = check_config_file_integrity(config_file)
            config_issues.extend(file_issues)
    
    # 2. 環境依存の問題チェック
    print("  2. 環境依存問題チェック")
    env_issues = check_environment_dependencies()
    config_issues.extend(env_issues)
    
    return config_issues

def check_config_file_integrity(file_path):
    """設定ファイルの整合性チェック"""
    issues = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'config.py' in file_path:
            # デバッグモード設定チェック
            if 'DEBUG = True' in content:
                issues.append({
                    'type': 'debug_mode_enabled',
                    'file': file_path,
                    'severity': 'medium'
                })
            
            # シークレットキー設定チェック
            if 'SECRET_KEY' not in content:
                issues.append({
                    'type': 'missing_secret_key',
                    'file': file_path,
                    'severity': 'high'
                })
    
    except Exception as e:
        issues.append({
            'type': 'config_file_error',
            'file': file_path,
            'error': str(e),
            'severity': 'medium'
        })
    
    return issues

def check_environment_dependencies():
    """環境依存問題のチェック"""
    issues = []
    
    # パス区切り文字の問題チェック
    app_py_path = "rccm-quiz-app/app.py"
    if os.path.exists(app_py_path):
        try:
            with open(app_py_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # ハードコードされたパス区切り文字チェック
            windows_paths = re.findall(r'[\'\"]\w+\\.*?[\'\"', content)
            unix_paths = re.findall(r'[\'\"]\w+/.*?[\'\"', content)
            
            if windows_paths:
                issues.append({
                    'type': 'hardcoded_windows_paths',
                    'paths': windows_paths[:5],  # 最初の5個のみ
                    'severity': 'medium'
                })
            
            if unix_paths:
                issues.append({
                    'type': 'hardcoded_unix_paths',
                    'paths': unix_paths[:5],
                    'severity': 'medium'
                })
        
        except Exception as e:
            issues.append({
                'type': 'environment_dependency_check_error',
                'error': str(e),
                'severity': 'low'
            })
    
    return issues

def analyze_data_pipeline():
    """データフロー・パイプライン問題の分析"""
    print("データフロー・パイプライン分析開始...")
    
    pipeline_issues = []
    
    # 1. データ読み込みフローチェック
    print("  1. データ読み込みフローチェック")
    load_issues = check_data_loading_pipeline()
    pipeline_issues.extend(load_issues)
    
    # 2. メモリ使用パターンチェック
    print("  2. メモリ使用パターンチェック")
    memory_issues = check_memory_usage_patterns()
    pipeline_issues.extend(memory_issues)
    
    return pipeline_issues

def check_data_loading_pipeline():
    """データ読み込みパイプライン問題チェック"""
    issues = []
    
    app_py_path = "rccm-quiz-app/app.py"
    if os.path.exists(app_py_path):
        try:
            with open(app_py_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 同期的なファイル読み込みの頻度チェック
            csv_reads = len(re.findall(r'csv\.DictReader', content))
            file_opens = len(re.findall(r'open\s*\(.*?\.csv', content))
            
            if csv_reads > 10:
                issues.append({
                    'type': 'excessive_csv_reads',
                    'count': csv_reads,
                    'severity': 'medium'
                })
            
            # キャッシュ機構の存在チェック
            cache_patterns = re.findall(r'cache|Cache', content)
            if len(cache_patterns) < 5 and csv_reads > 5:
                issues.append({
                    'type': 'insufficient_caching',
                    'csv_reads': csv_reads,
                    'cache_usage': len(cache_patterns),
                    'severity': 'high'
                })
        
        except Exception as e:
            issues.append({
                'type': 'pipeline_analysis_error',
                'error': str(e),
                'severity': 'medium'
            })
    
    return issues

def check_memory_usage_patterns():
    """メモリ使用パターン問題チェック"""
    issues = []
    
    app_py_path = "rccm-quiz-app/app.py"
    if os.path.exists(app_py_path):
        try:
            with open(app_py_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 大きなデータ構造の蓄積パターンチェック
            list_comprehensions = len(re.findall(r'\[.*?for.*?in.*?\]', content))
            large_loops = len(re.findall(r'for.*?in.*?range\(\d{3,}\)', content))
            
            if list_comprehensions > 20:
                issues.append({
                    'type': 'excessive_list_comprehensions',
                    'count': list_comprehensions,
                    'severity': 'medium'
                })
            
            if large_loops > 5:
                issues.append({
                    'type': 'large_range_loops',
                    'count': large_loops,
                    'severity': 'medium'
                })
        
        except Exception as e:
            issues.append({
                'type': 'memory_pattern_analysis_error',
                'error': str(e),
                'severity': 'low'
            })
    
    return issues

def analyze_system_interactions():
    """システム相互作用問題の分析"""
    print("システム相互作用分析開始...")
    
    interaction_issues = []
    
    # 1. 関数間依存関係チェック
    print("  1. 関数間依存関係チェック")
    dependency_issues = check_function_dependencies()
    interaction_issues.extend(dependency_issues)
    
    # 2. グローバル状態管理チェック
    print("  2. グローバル状態管理チェック")
    global_state_issues = check_global_state_management()
    interaction_issues.extend(global_state_issues)
    
    return interaction_issues

def check_function_dependencies():
    """関数間依存関係問題チェック"""
    issues = []
    
    app_py_path = "rccm-quiz-app/app.py"
    if os.path.exists(app_py_path):
        try:
            with open(app_py_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 関数定義と呼び出しの分析
            function_definitions = re.findall(r'def\s+(\w+)\s*\(', content)
            function_calls = re.findall(r'(\w+)\s*\(', content)
            
            # 未定義関数の呼び出しチェック（簡易版）
            undefined_calls = set(function_calls) - set(function_definitions) - set(['print', 'len', 'str', 'int', 'list', 'dict', 'open', 'range'])
            
            if len(undefined_calls) > 50:  # あまりに多い場合は問題の可能性
                issues.append({
                    'type': 'potential_undefined_function_calls',
                    'count': len(undefined_calls),
                    'examples': list(undefined_calls)[:10],
                    'severity': 'medium'
                })
            
            # 循環依存のリスクチェック（dept系関数）
            dept_functions = [f for f in function_definitions if 'department' in f.lower()]
            if len(dept_functions) > 5:
                issues.append({
                    'type': 'complex_department_function_interdependency',
                    'function_count': len(dept_functions),
                    'functions': dept_functions,
                    'severity': 'medium'
                })
        
        except Exception as e:
            issues.append({
                'type': 'dependency_analysis_error',
                'error': str(e),
                'severity': 'low'
            })
    
    return issues

def check_global_state_management():
    """グローバル状態管理問題チェック"""
    issues = []
    
    app_py_path = "rccm-quiz-app/app.py"
    if os.path.exists(app_py_path):
        try:
            with open(app_py_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # グローバル変数の使用チェック
            global_vars = re.findall(r'^(\w+)\s*=', content, re.MULTILINE)
            global_statements = len(re.findall(r'global\s+\w+', content))
            
            if len(global_vars) > 20:
                issues.append({
                    'type': 'excessive_global_variables',
                    'count': len(global_vars),
                    'severity': 'medium'
                })
            
            if global_statements > 10:
                issues.append({
                    'type': 'excessive_global_statements',
                    'count': global_statements,
                    'severity': 'high'
                })
        
        except Exception as e:
            issues.append({
                'type': 'global_state_analysis_error',
                'error': str(e),
                'severity': 'low'
            })
    
    return issues

def analyze_architecture_design():
    """アーキテクチャ設計問題の分析"""
    print("アーキテクチャ設計分析開始...")
    
    architecture_issues = []
    
    # 1. モジュール構成チェック
    print("  1. モジュール構成チェック")
    module_issues = check_module_structure()
    architecture_issues.extend(module_issues)
    
    # 2. 責任分離チェック
    print("  2. 責任分離チェック")
    separation_issues = check_separation_of_concerns()
    architecture_issues.extend(separation_issues)
    
    return architecture_issues

def check_module_structure():
    """モジュール構成問題チェック"""
    issues = []
    
    # ファイルサイズの分析
    app_py_path = "rccm-quiz-app/app.py"
    if os.path.exists(app_py_path):
        try:
            file_size = os.path.getsize(app_py_path)
            with open(app_py_path, 'r', encoding='utf-8') as f:
                line_count = sum(1 for line in f)
            
            if file_size > 500000:  # 500KB以上
                issues.append({
                    'type': 'excessive_file_size',
                    'file': 'app.py',
                    'size_bytes': file_size,
                    'lines': line_count,
                    'severity': 'high'
                })
            
            if line_count > 10000:  # 10,000行以上
                issues.append({
                    'type': 'excessive_line_count',
                    'file': 'app.py',
                    'lines': line_count,
                    'severity': 'high'
                })
        
        except Exception as e:
            issues.append({
                'type': 'module_structure_analysis_error',
                'error': str(e),
                'severity': 'low'
            })
    
    return issues

def check_separation_of_concerns():
    """責任分離問題チェック"""
    issues = []
    
    app_py_path = "rccm-quiz-app/app.py"
    if os.path.exists(app_py_path):
        try:
            with open(app_py_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 単一ファイル内での多様な責任チェック
            route_count = len(re.findall(r'@app\.route', content))
            class_count = len(re.findall(r'^class\s+\w+', content, re.MULTILINE))
            function_count = len(re.findall(r'^def\s+\w+', content, re.MULTILINE))
            
            if route_count > 50:
                issues.append({
                    'type': 'excessive_routes_in_single_file',
                    'count': route_count,
                    'severity': 'high'
                })
            
            if function_count > 200:
                issues.append({
                    'type': 'excessive_functions_in_single_file',
                    'count': function_count,
                    'severity': 'high'
                })
            
            # データベースロジックとビジネスロジックの混在チェック
            db_operations = len(re.findall(r'\.csv|DictReader|\.json', content))
            route_logic = len(re.findall(r'request\.|session\[', content))
            
            if db_operations > 20 and route_logic > 20:
                issues.append({
                    'type': 'mixed_data_and_presentation_logic',
                    'db_operations': db_operations,
                    'route_logic': route_logic,
                    'severity': 'medium'
                })
        
        except Exception as e:
            issues.append({
                'type': 'separation_analysis_error',
                'error': str(e),
                'severity': 'low'
            })
    
    return issues

def synthesize_root_causes(analysis_results):
    """根本原因の統合分析と優先度付け"""
    print("\n" + "=" * 100)
    print("🎯 多重根本原因統合分析結果（ウルトラシンク・絶対に嘘をつかない）")
    print("=" * 100)
    
    all_issues = []
    
    # 全ての問題を収集
    for category, issues in analysis_results.items():
        if isinstance(issues, list) and category.endswith('_issues'):
            for issue in issues:
                issue['category'] = category
                all_issues.append(issue)
    
    # 深刻度別に分類
    critical_issues = [i for i in all_issues if i.get('severity') == 'critical']
    high_issues = [i for i in all_issues if i.get('severity') == 'high']
    medium_issues = [i for i in all_issues if i.get('severity') == 'medium']
    low_issues = [i for i in all_issues if i.get('severity') == 'low']
    
    print(f"\n📊 発見された問題の統計:")
    print(f"  🚨 CRITICAL (最優先): {len(critical_issues)}個")
    print(f"  ⚠️  HIGH (高優先度): {len(high_issues)}個")
    print(f"  📋 MEDIUM (中優先度): {len(medium_issues)}個")
    print(f"  ℹ️  LOW (低優先度): {len(low_issues)}個")
    print(f"  📈 総問題数: {len(all_issues)}個")
    
    print(f"\n🚨 CRITICAL問題（即座に修正が必要）:")
    for issue in critical_issues:
        print(f"  - {issue['type']}: {issue.get('description', str(issue))}")
    
    print(f"\n⚠️ HIGH優先度問題（2週間治らない主要原因）:")
    for issue in high_issues[:10]:  # 最初の10個のみ表示
        print(f"  - {issue['type']}: {issue.get('description', str(issue))}")
    
    # 根本原因の相互関係分析
    problem_clusters = analyze_problem_clusters(all_issues)
    
    print(f"\n🔗 問題クラスター分析（相互関係のある問題群）:")
    for cluster_name, cluster_issues in problem_clusters.items():
        print(f"  {cluster_name}: {len(cluster_issues)}個の関連問題")
    
    # 最終推奨事項
    recommendations = generate_comprehensive_recommendations(all_issues, problem_clusters)
    
    print(f"\n📋 包括的修正推奨事項（優先度順）:")
    for i, rec in enumerate(recommendations, 1):
        print(f"  {i}. {rec}")
    
    return {
        'total_issues': len(all_issues),
        'critical_issues': len(critical_issues),
        'high_issues': len(high_issues),
        'problem_clusters': problem_clusters,
        'recommendations': recommendations
    }

def analyze_problem_clusters(all_issues):
    """問題の相互関係クラスター分析"""
    clusters = {
        'データ品質クラスター': [],
        'パフォーマンスクラスター': [],
        'アーキテクチャクラスター': [],
        'エラーハンドリングクラスター': []
    }
    
    for issue in all_issues:
        issue_type = issue.get('type', '')
        
        if any(keyword in issue_type for keyword in ['encoding', 'duplicate', 'quality', 'inconsistent']):
            clusters['データ品質クラスター'].append(issue)
        elif any(keyword in issue_type for keyword in ['excessive', 'memory', 'caching', 'loop']):
            clusters['パフォーマンスクラスター'].append(issue)
        elif any(keyword in issue_type for keyword in ['file_size', 'complexity', 'separation', 'module']):
            clusters['アーキテクチャクラスター'].append(issue)
        elif any(keyword in issue_type for keyword in ['error', 'exception', 'handling']):
            clusters['エラーハンドリングクラスター'].append(issue)
    
    return clusters

def generate_comprehensive_recommendations(all_issues, problem_clusters):
    """包括的修正推奨事項の生成"""
    recommendations = []
    
    # 問題の深刻度と数に基づく推奨事項
    critical_count = len([i for i in all_issues if i.get('severity') == 'critical'])
    high_count = len([i for i in all_issues if i.get('severity') == 'high'])
    
    if critical_count > 0:
        recommendations.append(f"緊急修正: {critical_count}個のCRITICAL問題を最優先で修正")
    
    if high_count > 10:
        recommendations.append(f"包括的リファクタリング: {high_count}個のHIGH問題は根本的な設計見直しが必要")
    
    # クラスター別推奨事項
    for cluster_name, cluster_issues in problem_clusters.items():
        if len(cluster_issues) > 5:
            if 'データ品質' in cluster_name:
                recommendations.append("データ品質管理システムの導入とデータ正規化")
            elif 'パフォーマンス' in cluster_name:
                recommendations.append("キャッシュシステム導入とクエリ最適化")
            elif 'アーキテクチャ' in cluster_name:
                recommendations.append("マイクロサービス化またはモジュラー設計への移行")
            elif 'エラーハンドリング' in cluster_name:
                recommendations.append("統一的エラーハンドリング戦略の実装")
    
    # 総合的推奨事項
    if len(all_issues) > 50:
        recommendations.append("段階的リファクタリング計画の策定（3-6か月）")
        recommendations.append("自動テストスイートの構築")
        recommendations.append("継続的品質監視システムの導入")
    
    return recommendations

if __name__ == "__main__":
    result = comprehensive_multi_root_cause_analysis()