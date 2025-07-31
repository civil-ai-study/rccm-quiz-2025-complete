#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚨 CRITICAL FIX: 部門問題混在バグ緊急修正
=============================================

【緊急修正対象】
森林土木部門で上水道問題が表示される致命的バグを即座に修正

【修正方針】
1. get_department_questions_ultrasync関数の完全書き換え
2. 問題選択ロジックの厳密化
3. 部門カテゴリマッピングの強化
4. フィルタリング精度の向上

【適用方法】
app.pyの該当関数を以下のコードで置換する

Created: 2025-07-27
Purpose: 緊急修正実装
"""

def get_department_questions_ultrasync_FIXED(department_name, question_count=10):
    """
    🔥 CRITICAL FIX: 部門問題混在バグ完全修正版
    各部門で正確な問題のみを選択する厳密実装
    """
    import random
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        # 🛡️ STEP 1: 厳密な部門マッピング確認
        CSV_JAPANESE_CATEGORIES = {
            "基礎科目": "共通",
            "道路": "道路",
            "河川・砂防": "河川、砂防及び海岸・海洋", 
            "都市計画": "都市計画及び地方計画",
            "造園": "造園",
            "建設環境": "建設環境",
            "鋼構造・コンクリート": "鋼構造及びコンクリート",
            "土質・基礎": "土質及び基礎",
            "施工計画": "施工計画、施工設備及び積算",
            "上下水道": "上水道及び工業用水道",
            "森林土木": "森林土木", 
            "農業土木": "農業土木",
            "トンネル": "トンネル"
        }
        
        if department_name not in CSV_JAPANESE_CATEGORIES:
            logger.error(f"❌ CRITICAL: 未対応部門 - {department_name}")
            return []
        
        target_category = CSV_JAPANESE_CATEGORIES[department_name]
        logger.info(f"🎯 CRITICAL FIX: 部門={department_name} -> カテゴリ={target_category}")
        
        # 🛡️ STEP 2: 基礎科目の特別処理
        if target_category == "共通":
            try:
                # 基礎科目専用の厳密読み込み
                basic_questions = []
                from utils import load_csv_data
                
                # 4-1データのみを読み込み
                basic_data = load_csv_data('data/4-1.csv')
                for row in basic_data:
                    if row.get('category') == '共通':
                        basic_questions.append({
                            'id': 10000 + int(row.get('id', 0)),
                            'question': row.get('question', ''),
                            'choices': {
                                'A': row.get('choice_a', ''),
                                'B': row.get('choice_b', ''),
                                'C': row.get('choice_c', ''),
                                'D': row.get('choice_d', '')
                            },
                            'correct_answer': row.get('correct_answer', ''),
                            'category': '共通',
                            'question_type': 'basic',
                            'year': int(row.get('year', 0))
                        })
                
                if len(basic_questions) >= question_count:
                    selected = random.sample(basic_questions, question_count)
                    logger.info(f"✅ CRITICAL FIX: 基礎科目選択成功 - {len(selected)}問")
                    return selected
                else:
                    logger.warning(f"⚠️ CRITICAL: 基礎科目不足 - {len(basic_questions)}/{question_count}")
                    return basic_questions
                    
            except Exception as e:
                logger.error(f"❌ CRITICAL: 基礎科目読み込みエラー - {e}")
                return []
        
        # 🛡️ STEP 3: 専門科目の厳密処理
        else:
            try:
                specialist_questions = []
                from utils import load_csv_data
                
                # 年度別に専門科目データを厳密に読み込み
                VALID_YEARS = [2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019]
                
                for year in VALID_YEARS:
                    try:
                        year_data = load_csv_data(f'data/4-2_{year}.csv')
                        for row in year_data:
                            row_category = row.get('category', '').strip()
                            
                            # 🔥 CRITICAL: 厳密なカテゴリマッチング
                            if row_category == target_category:
                                specialist_questions.append({
                                    'id': 20000 + int(row.get('id', 0)),
                                    'question': row.get('question', ''),
                                    'choices': {
                                        'A': row.get('choice_a', ''),
                                        'B': row.get('choice_b', ''),
                                        'C': row.get('choice_c', ''),
                                        'D': row.get('choice_d', '')
                                    },
                                    'correct_answer': row.get('correct_answer', ''),
                                    'category': target_category,
                                    'question_type': 'specialist',
                                    'year': year
                                })
                                
                    except Exception as year_error:
                        logger.warning(f"⚠️ {year}年度読み込み失敗: {year_error}")
                        continue
                
                # 🛡️ STEP 4: 厳密な結果検証
                if specialist_questions:
                    # カテゴリ統一性の最終確認
                    categories_found = set(q.get('category') for q in specialist_questions)
                    if len(categories_found) != 1 or target_category not in categories_found:
                        logger.error(f"❌ CRITICAL: カテゴリ混在検出 - 期待:{target_category}, 実際:{categories_found}")
                        # 不正な問題を除外
                        specialist_questions = [q for q in specialist_questions if q.get('category') == target_category]
                    
                    if len(specialist_questions) >= question_count:
                        selected = random.sample(specialist_questions, question_count)
                        logger.info(f"✅ CRITICAL FIX: {department_name}選択成功 - {len(selected)}問 (全{len(specialist_questions)}問中)")
                        
                        # 最終検証: 選択された問題が全て正しいカテゴリか確認
                        for q in selected:
                            if q.get('category') != target_category:
                                logger.error(f"❌ CRITICAL: 混在問題検出 ID:{q.get('id')} 期待:{target_category} 実際:{q.get('category')}")
                        
                        return selected
                    else:
                        logger.warning(f"⚠️ CRITICAL: {department_name}問題不足 - {len(specialist_questions)}/{question_count}")
                        return specialist_questions
                else:
                    logger.error(f"❌ CRITICAL: {department_name}で問題が見つからない")
                    return []
                    
            except Exception as e:
                logger.error(f"❌ CRITICAL: {department_name}専門科目読み込みエラー - {e}")
                return []
                
    except Exception as e:
        logger.error(f"❌ CRITICAL FIX: 全体例外 - {e}")
        return []

def apply_critical_fix():
    """
    🚨 CRITICAL FIX適用: app.pyの該当関数を置換
    """
    import os
    import shutil
    from datetime import datetime
    
    app_file = 'app.py'
    
    if not os.path.exists(app_file):
        print(f"❌ {app_file} が見つかりません")
        return False
    
    try:
        # バックアップ作成
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f'app.py.backup_critical_fix_{timestamp}'
        shutil.copy2(app_file, backup_file)
        print(f"✅ バックアップ作成: {backup_file}")
        
        # app.pyを読み込み
        with open(app_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 既存の関数を置換
        function_start = content.find('def get_department_questions_ultrasync(')
        if function_start == -1:
            print("❌ 対象関数が見つかりません")
            return False
        
        # 次の関数またはクラスの開始を探す
        lines = content[function_start:].split('\\n')
        function_end_line = 1
        
        for i, line in enumerate(lines[1:], 1):
            if (line.strip().startswith('def ') or 
                line.strip().startswith('class ') or 
                line.strip().startswith('@')):
                function_end_line = i
                break
        
        function_end = function_start + len('\\n'.join(lines[:function_end_line]))
        
        # 新しい関数コードで置換
        new_function_code = '''def get_department_questions_ultrasync(department_name, question_count=10):
    """
    🔥 CRITICAL FIX: 部門問題混在バグ完全修正版
    各部門で正確な問題のみを選択する厳密実装
    """
    try:
        # 🛡️ STEP 1: 厳密な部門マッピング確認
        if department_name not in CSV_JAPANESE_CATEGORIES:
            logger.error(f"❌ CRITICAL: 未対応部門 - {department_name}")
            return []
        
        target_category = CSV_JAPANESE_CATEGORIES[department_name]
        logger.info(f"🎯 CRITICAL FIX: 部門={department_name} -> カテゴリ={target_category}")
        
        # 🛡️ STEP 2: 基礎科目の特別処理
        if target_category == "共通":
            try:
                # 基礎科目専用の厳密読み込み
                basic_questions = []
                basic_data = load_csv_data('data/4-1.csv')
                for row in basic_data:
                    if row.get('category') == '共通':
                        basic_questions.append({
                            'id': 10000 + int(row.get('id', 0)),
                            'question': row.get('question', ''),
                            'choices': {
                                'A': row.get('choice_a', ''),
                                'B': row.get('choice_b', ''),
                                'C': row.get('choice_c', ''),
                                'D': row.get('choice_d', '')
                            },
                            'correct_answer': row.get('correct_answer', ''),
                            'category': '共通',
                            'question_type': 'basic',
                            'year': int(row.get('year', 0))
                        })
                
                if len(basic_questions) >= question_count:
                    selected = random.sample(basic_questions, question_count)
                    logger.info(f"✅ CRITICAL FIX: 基礎科目選択成功 - {len(selected)}問")
                    return selected
                else:
                    logger.warning(f"⚠️ CRITICAL: 基礎科目不足 - {len(basic_questions)}/{question_count}")
                    return basic_questions
                    
            except Exception as e:
                logger.error(f"❌ CRITICAL: 基礎科目読み込みエラー - {e}")
                return []
        
        # 🛡️ STEP 3: 専門科目の厳密処理
        else:
            try:
                specialist_questions = []
                
                # 年度別に専門科目データを厳密に読み込み
                for year in VALID_YEARS:
                    try:
                        year_data = load_csv_data(f'data/4-2_{year}.csv')
                        for row in year_data:
                            row_category = row.get('category', '').strip()
                            
                            # 🔥 CRITICAL: 厳密なカテゴリマッチング
                            if row_category == target_category:
                                specialist_questions.append({
                                    'id': 20000 + int(row.get('id', 0)),
                                    'question': row.get('question', ''),
                                    'choices': {
                                        'A': row.get('choice_a', ''),
                                        'B': row.get('choice_b', ''),
                                        'C': row.get('choice_c', ''),
                                        'D': row.get('choice_d', '')
                                    },
                                    'correct_answer': row.get('correct_answer', ''),
                                    'category': target_category,
                                    'question_type': 'specialist',
                                    'year': year
                                })
                                
                    except Exception as year_error:
                        logger.warning(f"⚠️ {year}年度読み込み失敗: {year_error}")
                        continue
                
                # 🛡️ STEP 4: 厳密な結果検証
                if specialist_questions:
                    # カテゴリ統一性の最終確認
                    categories_found = set(q.get('category') for q in specialist_questions)
                    if len(categories_found) != 1 or target_category not in categories_found:
                        logger.error(f"❌ CRITICAL: カテゴリ混在検出 - 期待:{target_category}, 実際:{categories_found}")
                        # 不正な問題を除外
                        specialist_questions = [q for q in specialist_questions if q.get('category') == target_category]
                    
                    if len(specialist_questions) >= question_count:
                        selected = random.sample(specialist_questions, question_count)
                        logger.info(f"✅ CRITICAL FIX: {department_name}選択成功 - {len(selected)}問 (全{len(specialist_questions)}問中)")
                        
                        # 最終検証: 選択された問題が全て正しいカテゴリか確認
                        for q in selected:
                            if q.get('category') != target_category:
                                logger.error(f"❌ CRITICAL: 混在問題検出 ID:{q.get('id')} 期待:{target_category} 実際:{q.get('category')}")
                        
                        return selected
                    else:
                        logger.warning(f"⚠️ CRITICAL: {department_name}問題不足 - {len(specialist_questions)}/{question_count}")
                        return specialist_questions
                else:
                    logger.error(f"❌ CRITICAL: {department_name}で問題が見つからない")
                    return []
                    
            except Exception as e:
                logger.error(f"❌ CRITICAL: {department_name}専門科目読み込みエラー - {e}")
                return []
                
    except Exception as e:
        logger.error(f"❌ CRITICAL FIX: 全体例外 - {e}")
        return []'''
        
        # 置換実行
        new_content = content[:function_start] + new_function_code + content[function_end:]
        
        # ファイルに書き込み
        with open(app_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✅ CRITICAL FIX適用完了: {app_file}")
        print(f"📄 バックアップ: {backup_file}")
        return True
        
    except Exception as e:
        print(f"❌ CRITICAL FIX適用エラー: {e}")
        return False

if __name__ == "__main__":
    print("🚨 CRITICAL DEPARTMENT MIXING FIX")
    print("=" * 50)
    
    # 修正適用
    if apply_critical_fix():
        print("✅ 修正完了: app.pyが更新されました")
        print("🔄 サーバーを再起動して変更を反映してください")
    else:
        print("❌ 修正失敗: 手動で修正が必要です")