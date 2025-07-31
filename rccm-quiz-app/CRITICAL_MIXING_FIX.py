#!/usr/bin/env python3
# 🚨 緊急修正: 混在問題完全根絶パッチ

"""
重大発見：app.pyの3527行目付近で混在検出・除外処理があるが、
処理タイミングが遅すぎて一部が漏れる可能性がある。

根本原因：
1. 問題選択時点でのフィルタリングが不完全
2. 最終段階での除外処理に依存している
3. Department → Category マッピングの一貫性に問題

完全修正方針：
1. 問題選択の最初の段階で厳格フィルタリング
2. 二重チェック機構の実装
3. 混在検出時の完全停止
"""

import sys
import os

# app.pyの混在防止強化修正
def generate_mixing_prevention_patch():
    """混在問題完全根絶のためのパッチコード生成"""
    
    patch_code = '''
# 🚨 CRITICAL MIXING PREVENTION PATCH - 混在問題完全根絶
# このパッチをget_mixed_questions関数の先頭に挿入

def validate_department_category_consistency():
    """部門→カテゴリマッピングの一貫性を完全検証"""
    # 全問題データをロード
    all_questions = load_questions()
    
    # 実際のCSVカテゴリ名を抽出
    actual_categories = set()
    for q in all_questions:
        if q.get('question_type') == 'specialist':
            cat = q.get('category')
            if cat:
                actual_categories.add(cat)
    
    # マッピング不整合チェック
    mapping_categories = set(DEPARTMENT_TO_CATEGORY_MAPPING.values())
    
    # 不整合検出
    unmapped_categories = actual_categories - mapping_categories
    invalid_mappings = mapping_categories - actual_categories
    
    if unmapped_categories:
        logger.critical(f"🚨 CRITICAL: CSVにあるがマッピングにないカテゴリ: {unmapped_categories}")
        return False
    
    if invalid_mappings:
        logger.critical(f"🚨 CRITICAL: マッピングにあるがCSVにないカテゴリ: {invalid_mappings}")
        return False
    
    return True

def strict_department_filter(questions, department, question_type):
    """厳格な部門フィルタリング - 混在完全防止"""
    if not department or question_type != 'specialist':
        return questions
    
    # 正規化部門名取得
    normalized_dept = normalize_department_name(department)
    if not normalized_dept:
        logger.error(f"🚨 無効部門名: {department}")
        return []
    
    # カテゴリ名取得
    target_category = DEPARTMENT_TO_CATEGORY_MAPPING.get(normalized_dept)
    if not target_category:
        logger.error(f"🚨 マッピング不在: {normalized_dept}")
        return []
    
    # 厳格フィルタリング
    filtered = []
    rejected = []
    
    for q in questions:
        q_category = q.get('category', '')
        q_type = q.get('question_type', '')
        
        # 完全一致チェック
        if q_type == 'specialist' and q_category == target_category:
            filtered.append(q)
        else:
            rejected.append({
                'id': q.get('id'),
                'expected_category': target_category,
                'actual_category': q_category,
                'question_type': q_type
            })
    
    if rejected:
        logger.warning(f"🔍 厳格フィルタで除外: {len(rejected)}問")
        for r in rejected[:3]:  # 最初の3件をログ
            logger.warning(f"  除外問題ID{r['id']}: 期待={r['expected_category']}, 実際={r['actual_category']}")
    
    logger.info(f"✅ 厳格部門フィルタ完了: {department} → {target_category} = {len(filtered)}問")
    return filtered

def final_mixing_validation(selected_questions, department, question_type, year=None):
    """最終混在検証 - 1問でも混在があれば完全停止"""
    if not selected_questions:
        return []
    
    if question_type != 'specialist' or not department:
        return selected_questions
    
    # 期待カテゴリ取得
    normalized_dept = normalize_department_name(department)
    target_category = DEPARTMENT_TO_CATEGORY_MAPPING.get(normalized_dept) if normalized_dept else None
    
    if not target_category:
        logger.error(f"🚨 最終検証: 無効部門 {department}")
        return []
    
    # 混在検出
    mixing_detected = []
    valid_questions = []
    
    for q in selected_questions:
        q_category = q.get('category', '')
        q_type = q.get('question_type', '')
        q_year = q.get('year')
        
        # カテゴリチェック
        if q_type != 'specialist':
            mixing_detected.append(f"問題ID{q.get('id')}: 専門科目以外({q_type})")
            continue
            
        if q_category != target_category:
            mixing_detected.append(f"問題ID{q.get('id')}: カテゴリ不一致(期待:{target_category}, 実際:{q_category})")
            continue
        
        # 年度チェック
        if year:
            try:
                target_year = int(year)
                if not q_year or int(q_year) != target_year:
                    mixing_detected.append(f"問題ID{q.get('id')}: 年度不一致(期待:{target_year}, 実際:{q_year})")
                    continue
            except (ValueError, TypeError):
                mixing_detected.append(f"問題ID{q.get('id')}: 年度データ不正({q_year})")
                continue
        
        valid_questions.append(q)
    
    # 混在が1つでもあれば完全停止
    if mixing_detected:
        logger.critical(f"🚨 CRITICAL MIXING DETECTED: {len(mixing_detected)}件")
        for mix in mixing_detected:
            logger.critical(f"  {mix}")
        logger.critical(f"🚨 混在検出により問題選択を完全停止")
        return []  # 空リストを返して混在を防止
    
    logger.info(f"✅ 最終混在検証完了: 全{len(valid_questions)}問が純粋")
    return valid_questions

# パッチ適用関数
def apply_mixing_prevention_patch():
    """混在防止パッチの適用"""
    
    # 1. 部門→カテゴリマッピング一貫性検証
    if not validate_department_category_consistency():
        logger.critical("🚨 CRITICAL: マッピング不整合により処理停止")
        return []
    
    # 2. 厳格フィルタリングの適用
    # available_questions = strict_department_filter(available_questions, department, question_type)
    
    # 3. 最終混在検証の適用
    # selected_questions = final_mixing_validation(selected_questions, department, question_type, year)
    
    return True
'''
    
    return patch_code

def identify_mixing_root_causes():
    """混在問題の根本原因特定"""
    causes = {
        "immediate_causes": [
            "get_mixed_questions関数でのフィルタリング処理の不完全性",
            "部門→カテゴリマッピングの一貫性チェック不足", 
            "最終段階での混在検出に依存した設計"
        ],
        "root_causes": [
            "問題選択時点での厳格チェック不在",
            "二重検証機構の欠如",
            "マッピングデータの整合性検証不足",
            "エラー時のフォールバック処理による混在許容"
        ],
        "critical_fixes_required": [
            "問題選択の最初の段階での厳格フィルタリング実装",
            "混在検出時の完全停止機構",
            "部門→カテゴリマッピングの完全一貫性保証",
            "フォールバック処理での混在防止"
        ]
    }
    
    return causes

if __name__ == "__main__":
    print("🚨 CRITICAL MIXING PREVENTION ANALYSIS")
    print("="*60)
    
    # 根本原因分析
    causes = identify_mixing_root_causes()
    
    print("📊 混在問題根本原因:")
    for category, items in causes.items():
        print(f"\n{category.upper()}:")
        for item in items:
            print(f"  - {item}")
    
    # パッチコード生成
    patch = generate_mixing_prevention_patch()
    
    print(f"\n🔧 生成されたパッチコード長: {len(patch)}文字")
    print("\n次のステップ:")
    print("1. app.pyのget_mixed_questions関数を修正")
    print("2. 厳格フィルタリング処理を先頭に追加")
    print("3. 最終混在検証処理を最後に追加") 
    print("4. 全12部門での完全テスト実行")
    
    print("\n🎯 修正完了後の期待結果:")
    print("- 混在率: 0% (完全根絶)")
    print("- 部門分離: 100%保証")
    print("- エラー時混在: 完全防止")