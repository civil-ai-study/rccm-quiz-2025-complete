#!/usr/bin/env python3
"""
RCCM Quiz App 根本的な構造問題分析ツール
設計上の欠陥を特定し、テスト失敗の根本原因を調査
"""

import sys
import os
import re
from collections import defaultdict

def analyze_department_mapping():
    """DEPARTMENT_TO_CATEGORY_MAPPINGの重複と設計問題を分析"""
    print("=== 1. DEPARTMENT_TO_CATEGORY_MAPPING 分析 ===")
    
    # app.pyからマッピングを抽出
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print("❌ app.py が見つかりません")
        return
    
    # マッピング定義を抽出
    mapping_pattern = r'DEPARTMENT_TO_CATEGORY_MAPPING\s*=\s*\{([^}]+)\}'
    match = re.search(mapping_pattern, content, re.DOTALL)
    
    if not match:
        print("❌ DEPARTMENT_TO_CATEGORY_MAPPING定義が見つかりません")
        return
    
    mapping_text = match.group(1)
    
    # 各行を解析
    mapping_dict = {}
    value_to_keys = defaultdict(list)
    
    lines = mapping_text.split('\n')
    for line in lines:
        line = line.strip()
        if line.startswith('#') or not line:
            continue
        
        # 'key': 'value' 形式を抽出
        match = re.search(r"'([^']+)':\s*'([^']+)'", line)
        if match:
            key, value = match.groups()
            mapping_dict[key] = value
            value_to_keys[value].append(key)
    
    print(f"マッピング項目数: {len(mapping_dict)}")
    print()
    
    # 重複値の検出
    print("=== 重複マッピングの検出 ===")
    duplicates_found = False
    for value, keys in value_to_keys.items():
        if len(keys) > 1:
            print(f"❌ 重複: '{value}' → {keys}")
            duplicates_found = True
    
    if not duplicates_found:
        print("✅ 重複マッピングなし")
    
    print()
    
    # 逆マッピングの問題
    print("=== CATEGORY_TO_DEPARTMENT_MAPPING 逆マッピング問題 ===")
    print("問題: 重複する値がある場合、逆マッピングで最後の値が残る")
    
    reverse_mapping = {v: k for k, v in mapping_dict.items()}
    print(f"正方向マッピング: {len(mapping_dict)}項目")
    print(f"逆方向マッピング: {len(reverse_mapping)}項目")
    
    if len(mapping_dict) != len(reverse_mapping):
        lost_count = len(mapping_dict) - len(reverse_mapping)
        print(f"❌ 逆マッピングで{lost_count}項目が失われます")
        
        # どのキーが失われるかを特定
        for value, keys in value_to_keys.items():
            if len(keys) > 1:
                kept_key = reverse_mapping[value]
                lost_keys = [k for k in keys if k != kept_key]
                print(f"  '{value}': 保持='{kept_key}', 失われる={lost_keys}")
    
    return mapping_dict, value_to_keys

def analyze_validation_function():
    """validate_exam_parameters関数の実装問題を分析"""
    print("\n=== 2. validate_exam_parameters 関数分析 ===")
    
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print("❌ app.py が見つかりません")
        return
    
    # 関数の定義を抽出
    func_pattern = r'def validate_exam_parameters\([^)]*\):(.*?)(?=\ndef\s|\Z)'
    match = re.search(func_pattern, content, re.DOTALL)
    
    if not match:
        print("❌ validate_exam_parameters関数が見つかりません")
        return
    
    func_code = match.group(1)
    
    # 問題のあるパターンを検出
    issues = []
    
    # 1. 重複マッピングを前提とした検証
    if 'valid_department_names = list(DEPARTMENT_TO_CATEGORY_MAPPING.values())' in func_code:
        issues.append("重複値を含むマッピングから検証リストを作成")
    
    # 2. 英語IDと日本語名の混在許可
    if 'not in valid_departments and' in func_code and 'not in valid_department_names' in func_code:
        issues.append("英語IDと日本語名の両方を許可（曖昧性）")
    
    # 3. 型変換の不整合
    if 'int(kwargs[' in func_code:
        issues.append("型変換処理が含まれる（入力データの不整合を示唆）")
    
    print("検出された設計問題:")
    for i, issue in enumerate(issues, 1):
        print(f"  {i}. {issue}")
    
    if not issues:
        print("✅ 明らかな設計問題は検出されませんでした")

def analyze_get_mixed_questions():
    """get_mixed_questions関数の部門フィルタリング問題を分析"""
    print("\n=== 3. get_mixed_questions 部門フィルタリング分析 ===")
    
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print("❌ app.py が見つかりません")
        return
    
    # 関数の定義を抽出
    func_pattern = r'def get_mixed_questions\([^)]*\):(.*?)(?=\ndef\s|\Z)'
    match = re.search(func_pattern, content, re.DOTALL)
    
    if not match:
        print("❌ get_mixed_questions関数が見つかりません")
        return
    
    func_code = match.group(1)
    
    # 部門フィルタリングのロジックを分析
    issues = []
    
    # 1. 複数の変換ポイント
    conversion_count = func_code.count('DEPARTMENT_TO_CATEGORY_MAPPING')
    if conversion_count > 1:
        issues.append(f"部門→カテゴリ変換が{conversion_count}箇所で実行（一貫性リスク）")
    
    # 2. target_categoryの再代入
    if 'target_category = department' in func_code:
        issues.append("target_categoryが複数回代入される（予期しない動作）")
    
    # 3. フォールバック処理の複雑性
    if '部分一致' in func_code or 'フォールバック' in func_code:
        issues.append("複雑なフォールバック処理（エラーの隠蔽リスク）")
    
    # 4. 年度とカテゴリの混在フィルタリング
    if 'if year and' in func_code and 'if requested_category' in func_code:
        issues.append("年度フィルタとカテゴリフィルタが分離（重複適用リスク）")
    
    print("検出された設計問題:")
    for i, issue in enumerate(issues, 1):
        print(f"  {i}. {issue}")
    
    if not issues:
        print("✅ 明らかな設計問題は検出されませんでした")

def analyze_csv_department_consistency():
    """CSVファイル内の部門名とアプリ内部の整合性を分析"""
    print("\n=== 4. CSVファイルと部門名整合性分析 ===")
    
    # app.pyからマッピングを取得
    mapping_dict, _ = analyze_department_mapping()
    if not mapping_dict:
        print("❌ マッピング情報が取得できませんでした")
        return
    
    expected_categories = set(mapping_dict.values())
    print(f"アプリ内期待カテゴリ: {sorted(expected_categories)}")
    print()
    
    # CSVファイルの実際のカテゴリを確認
    import csv
    
    csv_categories = set()
    csv_files = [f for f in os.listdir('data') if f.endswith('.csv')]
    
    for csv_file in csv_files:
        try:
            with open(f'data/{csv_file}', 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if 'category' in row and row['category'].strip():
                        csv_categories.add(row['category'].strip())
        except Exception as e:
            print(f"⚠️ {csv_file}読み込みエラー: {e}")
    
    print(f"CSV内実際のカテゴリ: {sorted(csv_categories)}")
    print()
    
    # 不整合を検出
    missing_in_csv = expected_categories - csv_categories
    extra_in_csv = csv_categories - expected_categories
    
    if missing_in_csv:
        print(f"❌ アプリで期待されているがCSVにないカテゴリ: {missing_in_csv}")
    
    if extra_in_csv:
        print(f"❌ CSVにあるがアプリで未定義のカテゴリ: {extra_in_csv}")
    
    if not missing_in_csv and not extra_in_csv:
        print("✅ CSVとアプリの部門名は整合しています")

def analyze_root_causes():
    """根本原因の特定"""
    print("\n=== 5. 根本原因分析 ===")
    
    root_causes = [
        {
            "title": "重複マッピング設計欠陥",
            "description": "DEPARTMENT_TO_CATEGORY_MAPPINGで同一値への複数キーマッピング",
            "impact": "逆マッピング時に情報が失われ、部門の曖昧性が発生",
            "severity": "高"
        },
        {
            "title": "入力パラメータの曖昧性",
            "description": "英語IDと日本語名の両方を受け入れる設計",
            "impact": "予期しない部門変換やフィルタリング失敗",
            "severity": "中"
        },
        {
            "title": "フィルタリングロジックの複雑性",
            "description": "複数箇所での部門変換と条件分岐",
            "impact": "テストが困難で、エッジケースでの予期しない動作",
            "severity": "中"
        },
        {
            "title": "エラーハンドリングの不足",
            "description": "フォールバック処理がエラーを隠蔽",
            "impact": "問題の早期発見ができず、デバッグが困難",
            "severity": "中"
        }
    ]
    
    for i, cause in enumerate(root_causes, 1):
        print(f"{i}. {cause['title']} [重要度: {cause['severity']}]")
        print(f"   問題: {cause['description']}")
        print(f"   影響: {cause['impact']}")
        print()

def generate_fix_recommendations():
    """修正推奨事項の生成"""
    print("=== 6. 修正推奨事項 ===")
    
    recommendations = [
        {
            "priority": "最高",
            "title": "部門マッピングの一意性確保",
            "actions": [
                "DEPARTMENT_TO_CATEGORY_MAPPINGから重複する値を削除",
                "各カテゴリに対して単一のキーのみを定義",
                "旧キーは廃止して新しい統一されたキーに移行"
            ]
        },
        {
            "priority": "高",
            "title": "入力検証の厳格化",
            "actions": [
                "英語IDのみを内部的に使用",
                "日本語名は表示のみに使用",
                "入力時に英語IDに正規化"
            ]
        },
        {
            "priority": "高",
            "title": "フィルタリングロジックの単純化",
            "actions": [
                "部門変換を単一箇所に集約",
                "フィルタリング条件を明確に分離",
                "フォールバック処理を削除または明示的エラーに変更"
            ]
        },
        {
            "priority": "中",
            "title": "テスト設計の改善",
            "actions": [
                "各部門での単体テスト追加",
                "エッジケースのテストカバレッジ向上",
                "統合テストでの部門間混在チェック"
            ]
        }
    ]
    
    for rec in recommendations:
        print(f"【{rec['priority']}】{rec['title']}")
        for action in rec['actions']:
            print(f"  - {action}")
        print()

def main():
    """メイン実行"""
    print("RCCM Quiz App 根本的構造問題分析")
    print("=" * 50)
    
    analyze_department_mapping()
    analyze_validation_function()
    analyze_get_mixed_questions()
    analyze_csv_department_consistency()
    analyze_root_causes()
    generate_fix_recommendations()
    
    print("=" * 50)
    print("分析完了")

if __name__ == '__main__':
    main()