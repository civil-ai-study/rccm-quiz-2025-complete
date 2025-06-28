#!/usr/bin/env python3
"""
RCCM カテゴリマッピング完全性ウルトラシンク調査スクリプト
CLAUDE.mdの指導に従い、カテゴリマッピングの完全性を徹底調査します。

🚨 ウルトラシンク修正案の実行
- 未定義カテゴリや不整合の特定
- URLエンコーディング問題の検出
- 日本語⇔英語変換処理の妥当性確認
- デバッグログから関連エラーの抽出
"""

import sys
import os
import csv
import re
import urllib.parse
from typing import Dict, List, Set, Any
from collections import defaultdict
import json
from datetime import datetime

# app.pyから部門マッピングを取得
sys.path.insert(0, '.')

def load_app_mappings():
    """app.pyから実際のマッピング定数を取得"""
    try:
        import app
        mapping = getattr(app, 'DEPARTMENT_TO_CATEGORY_MAPPING', {})
        reverse_mapping = getattr(app, 'CATEGORY_TO_DEPARTMENT_MAPPING', {})
        return mapping, reverse_mapping
    except Exception as e:
        print(f"❌ app.pyからのマッピング取得失敗: {e}")
        return {}, {}

def analyze_url_encoding_issues():
    """URLエンコーディング問題を分析"""
    issues = []
    
    # 造園部門で発生したURLエンコーディング問題のパターンを確認
    test_strings = [
        '造園',
        'landscape',
        '河川、砂防及び海岸・海洋',
        'civil_planning',
        '施工計画、施工設備及び積算',
        'construction_planning'
    ]
    
    for test_str in test_strings:
        encoded = urllib.parse.quote(test_str, safe='')
        decoded = urllib.parse.unquote(encoded)
        
        if encoded != test_str or decoded != test_str:
            issues.append({
                'original': test_str,
                'encoded': encoded,
                'decoded': decoded,
                'potential_issue': encoded != test_str
            })
    
    return issues

def load_csv_data():
    """全CSVファイルからデータを読み込み、カテゴリを収集"""
    csv_categories = set()
    file_categories = defaultdict(set)
    encoding_issues = []
    
    for filename in os.listdir('data'):
        if not filename.endswith('.csv'):
            continue
            
        filepath = os.path.join('data', filename)
        
        # 複数エンコーディングで試行
        for encoding in ['utf-8', 'shift_jis', 'cp932', 'utf-8-sig']:
            try:
                with open(filepath, 'r', encoding=encoding, errors='ignore') as f:
                    reader = csv.DictReader(f)
                    file_cats = set()
                    
                    for row in reader:
                        if 'category' in row and row['category'].strip():
                            category = row['category'].strip()
                            csv_categories.add(category)
                            file_cats.add(category)
                    
                    file_categories[filename] = file_cats
                    break
                    
            except Exception as e:
                if encoding == 'utf-8-sig':  # 最後のエンコーディング
                    encoding_issues.append({
                        'file': filename,
                        'error': str(e),
                        'encodings_tried': ['utf-8', 'shift_jis', 'cp932', 'utf-8-sig']
                    })
    
    return csv_categories, file_categories, encoding_issues

def analyze_mapping_completeness(app_mapping, csv_categories):
    """マッピングの完全性を分析"""
    issues = []
    
    # 1. app.pyで定義されているカテゴリ
    app_categories = set(app_mapping.values())
    
    # 2. CSVで実際に使用されているカテゴリ
    
    # 3. 未定義カテゴリ（CSVにあるがapp.pyにない）
    undefined_categories = csv_categories - app_categories
    
    # 4. 未使用カテゴリ（app.pyにあるがCSVにない）
    unused_categories = app_categories - csv_categories
    
    # 5. 部分マッチング問題の検出
    partial_matches = []
    for csv_cat in csv_categories:
        for app_cat in app_categories:
            if csv_cat != app_cat and (csv_cat in app_cat or app_cat in csv_cat):
                partial_matches.append({
                    'csv_category': csv_cat,
                    'app_category': app_cat,
                    'match_type': 'partial'
                })
    
    return {
        'undefined_categories': list(undefined_categories),
        'unused_categories': list(unused_categories),
        'partial_matches': partial_matches,
        'total_app_categories': len(app_categories),
        'total_csv_categories': len(csv_categories)
    }

def check_reverse_mapping_consistency(forward_mapping, reverse_mapping):
    """順方向と逆方向のマッピングの整合性をチェック"""
    issues = []
    
    # 順方向マッピングから逆方向を再構築
    reconstructed_reverse = {v: k for k, v in forward_mapping.items()}
    
    # 不整合をチェック
    for jp_name, en_id in reverse_mapping.items():
        if jp_name not in reconstructed_reverse:
            issues.append({
                'type': 'reverse_orphan',
                'japanese_name': jp_name,
                'english_id': en_id,
                'description': '逆マッピングにあるが順方向マッピングに対応なし'
            })
        elif reconstructed_reverse[jp_name] != en_id:
            issues.append({
                'type': 'mapping_mismatch',
                'japanese_name': jp_name,
                'reverse_mapping_id': en_id,
                'forward_mapping_id': reconstructed_reverse[jp_name],
                'description': '順方向と逆方向のマッピングが不一致'
            })
    
    for jp_name, en_id in reconstructed_reverse.items():
        if jp_name not in reverse_mapping:
            issues.append({
                'type': 'forward_orphan',
                'japanese_name': jp_name,
                'english_id': en_id,
                'description': '順方向マッピングにあるが逆マッピングに対応なし'
            })
    
    return issues

def analyze_category_filtering_logic():
    """app.pyのカテゴリフィルタリングロジックを解析"""
    issues = []
    
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # カテゴリフィルタリング関連の箇所を抽出
        category_filter_patterns = [
            r'q\.get\([\'"]category[\'"]\)',
            r'category\s*==\s*',
            r'target_category',
            r'requested_category',
            r'部門フィルタ',
            r'カテゴリフィルタ'
        ]
        
        for pattern in category_filter_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                line_content = content.split('\n')[line_num - 1].strip()
                
                # 潜在的な問題をチェック
                if '==' in line_content and 'q.get(' in line_content:
                    if 'strip()' not in line_content:
                        issues.append({
                            'type': 'missing_strip',
                            'line': line_num,
                            'content': line_content,
                            'description': 'カテゴリ比較でstrip()が使用されていない可能性'
                        })
                    
                    if '.lower()' not in line_content and '.upper()' not in line_content:
                        issues.append({
                            'type': 'case_sensitive',
                            'line': line_num,
                            'content': line_content,
                            'description': '大文字小文字を考慮しない比較の可能性'
                        })
    
    except Exception as e:
        issues.append({
            'type': 'analysis_error',
            'description': f'コード解析エラー: {e}'
        })
    
    return issues

def extract_log_category_errors():
    """ログファイルからカテゴリ関連エラーを抽出"""
    log_errors = []
    
    if not os.path.exists('rccm_app.log'):
        return log_errors
    
    try:
        with open('rccm_app.log', 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        # エラーパターン
        error_patterns = [
            r'カテゴリ.*エラー',
            r'部門.*エラー',
            r'mapping.*error',
            r'カテゴリマッチング失敗',
            r'部門マッチング失敗',
            r'WARNING.*カテゴリ',
            r'WARNING.*部門',
            r'エンコード.*エラー',
            r'KeyError.*category',
            r'ValueError.*department'
        ]
        
        for i, line in enumerate(lines[-1000:], len(lines) - 1000):  # 最新1000行から検索
            for pattern in error_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    log_errors.append({
                        'line_number': i + 1,
                        'content': line.strip(),
                        'pattern_matched': pattern
                    })
    
    except Exception as e:
        log_errors.append({
            'error': f'ログ解析エラー: {e}'
        })
    
    return log_errors

def generate_ultra_sync_fixes(analysis_results):
    """ウルトラシンク修正案を生成"""
    fixes = []
    
    # 未定義カテゴリの修正案
    if analysis_results['mapping_completeness']['undefined_categories']:
        fixes.append({
            'priority': 'HIGH',
            'type': 'ADD_MISSING_MAPPINGS',
            'description': '未定義カテゴリをマッピングに追加',
            'categories': analysis_results['mapping_completeness']['undefined_categories'],
            'implementation': 'DEPARTMENT_TO_CATEGORY_MAPPINGに追加定義が必要'
        })
    
    # マッピング不整合の修正案
    if analysis_results['mapping_consistency']:
        fixes.append({
            'priority': 'CRITICAL',
            'type': 'FIX_MAPPING_INCONSISTENCY',
            'description': '順方向と逆方向マッピングの不整合を修正',
            'issues': analysis_results['mapping_consistency'],
            'implementation': 'マッピング定数の再同期が必要'
        })
    
    # URLエンコーディング問題の修正案
    if any(issue['potential_issue'] for issue in analysis_results['url_encoding']):
        fixes.append({
            'priority': 'MEDIUM',
            'type': 'URL_ENCODING_SAFETY',
            'description': 'URLエンコーディング対応の強化',
            'implementation': 'urllib.parse.unquote()の適用とエンコーディング正規化'
        })
    
    # コードロジック改善案
    if analysis_results['code_logic_issues']:
        fixes.append({
            'priority': 'MEDIUM',
            'type': 'CODE_LOGIC_IMPROVEMENT',
            'description': 'カテゴリフィルタリングロジックの改善',
            'issues': analysis_results['code_logic_issues'],
            'implementation': 'strip()とlower()の追加、厳密な比較の実装'
        })
    
    return fixes

def generate_verification_tests():
    """検証テスト案を生成"""
    tests = [
        {
            'name': 'マッピング完全性テスト',
            'description': '全カテゴリがマッピングに定義されているかテスト',
            'code_snippet': '''
def test_mapping_completeness():
    csv_categories = load_all_csv_categories()
    app_categories = set(DEPARTMENT_TO_CATEGORY_MAPPING.values())
    undefined = csv_categories - app_categories
    assert len(undefined) == 0, f"未定義カテゴリ: {undefined}"
            '''
        },
        {
            'name': 'URLエンコーディングテスト',
            'description': 'URL経由での部門指定が正常動作するかテスト',
            'code_snippet': '''
def test_url_encoding():
    test_departments = ['造園', '河川、砂防及び海岸・海洋']
    for dept in test_departments:
        encoded = urllib.parse.quote(dept)
        # アプリでデコードして正常処理されるかテスト
        assert process_department_param(encoded) == dept
            '''
        },
        {
            'name': '逆マッピング整合性テスト',
            'description': '順方向と逆方向マッピングの整合性テスト',
            'code_snippet': '''
def test_reverse_mapping():
    for en_id, jp_name in DEPARTMENT_TO_CATEGORY_MAPPING.items():
        assert CATEGORY_TO_DEPARTMENT_MAPPING[jp_name] == en_id
            '''
        },
        {
            'name': '実際の問題選択フローテスト',
            'description': '各部門で正しいカテゴリの問題のみが選択されるかテスト',
            'code_snippet': '''
def test_category_filtering():
    for dept_id, expected_category in DEPARTMENT_TO_CATEGORY_MAPPING.items():
        questions = get_mixed_questions(department=dept_id, question_type='specialist')
        categories = {q.get('category') for q in questions}
        assert categories == {expected_category}, f"混在検出: {categories}"
            '''
        }
    ]
    
    return tests

def main():
    print("🔥 RCCM カテゴリマッピング完全性ウルトラシンク調査")
    print("=" * 60)
    print()
    
    # 1. アプリケーションマッピングの取得
    print("📋 1. アプリケーションマッピング分析")
    app_mapping, reverse_mapping = load_app_mappings()
    print(f"   順方向マッピング: {len(app_mapping)}件")
    print(f"   逆方向マッピング: {len(reverse_mapping)}件")
    print()
    
    # 2. CSVデータの分析
    print("📋 2. CSVデータ分析")
    csv_categories, file_categories, encoding_issues = load_csv_data()
    print(f"   検出カテゴリ数: {len(csv_categories)}")
    print(f"   処理ファイル数: {len(file_categories)}")
    print(f"   エンコーディング問題: {len(encoding_issues)}件")
    print()
    
    # 3. マッピング完全性分析
    print("📋 3. マッピング完全性分析")
    mapping_completeness = analyze_mapping_completeness(app_mapping, csv_categories)
    print(f"   未定義カテゴリ: {len(mapping_completeness['undefined_categories'])}件")
    print(f"   未使用カテゴリ: {len(mapping_completeness['unused_categories'])}件")
    print(f"   部分マッチ問題: {len(mapping_completeness['partial_matches'])}件")
    print()
    
    # 4. マッピング整合性分析
    print("📋 4. マッピング整合性分析")
    mapping_consistency = check_reverse_mapping_consistency(app_mapping, reverse_mapping)
    print(f"   マッピング不整合: {len(mapping_consistency)}件")
    print()
    
    # 5. URLエンコーディング分析
    print("📋 5. URLエンコーディング分析")
    url_encoding_issues = analyze_url_encoding_issues()
    print(f"   エンコーディング問題: {len(url_encoding_issues)}件")
    print()
    
    # 6. コードロジック分析
    print("📋 6. コードロジック分析")
    code_logic_issues = analyze_category_filtering_logic()
    print(f"   ロジック問題: {len(code_logic_issues)}件")
    print()
    
    # 7. ログエラー分析
    print("📋 7. ログエラー分析")
    log_errors = extract_log_category_errors()
    print(f"   ログエラー: {len(log_errors)}件")
    print()
    
    # 結果統合
    analysis_results = {
        'mapping_completeness': mapping_completeness,
        'mapping_consistency': mapping_consistency,
        'url_encoding': url_encoding_issues,
        'code_logic_issues': code_logic_issues,
        'log_errors': log_errors,
        'csv_categories': list(csv_categories),
        'file_categories': dict(file_categories),
        'encoding_issues': encoding_issues
    }
    
    # 8. ウルトラシンク修正案の生成
    print("🚨 8. ウルトラシンク修正案")
    fixes = generate_ultra_sync_fixes(analysis_results)
    for i, fix in enumerate(fixes, 1):
        print(f"   {i}. [{fix['priority']}] {fix['type']}")
        print(f"      {fix['description']}")
    print()
    
    # 9. 検証テスト案の生成
    print("🧪 9. 検証テスト案")
    tests = generate_verification_tests()
    for i, test in enumerate(tests, 1):
        print(f"   {i}. {test['name']}")
        print(f"      {test['description']}")
    print()
    
    # 詳細レポート出力
    report_filename = f'ultra_sync_category_mapping_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'analysis_results': analysis_results,
        'ultra_sync_fixes': fixes,
        'verification_tests': tests,
        'summary': {
            'total_issues': len(mapping_completeness['undefined_categories']) + 
                          len(mapping_consistency) + 
                          len(code_logic_issues) + 
                          len(log_errors),
            'critical_issues': len([f for f in fixes if f['priority'] == 'CRITICAL']),
            'high_issues': len([f for f in fixes if f['priority'] == 'HIGH']),
            'medium_issues': len([f for f in fixes if f['priority'] == 'MEDIUM'])
        }
    }
    
    with open(report_filename, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"📄 詳細レポート: {report_filename}")
    print()
    
    # 最終判定
    total_issues = report['summary']['total_issues']
    critical_issues = report['summary']['critical_issues']
    
    if total_issues == 0:
        print("✅ カテゴリマッピングの完全性: 問題なし")
    elif critical_issues > 0:
        print(f"❌ CRITICAL問題検出: {critical_issues}件の重大な問題があります")
    else:
        print(f"⚠️  軽微な問題検出: {total_issues}件の改善可能な箇所があります")
    
    return analysis_results, fixes, tests

if __name__ == '__main__':
    main()