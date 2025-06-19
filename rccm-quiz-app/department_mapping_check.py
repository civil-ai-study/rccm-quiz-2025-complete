#!/usr/bin/env python3
"""
部門マッピングの調査 - 実際のデータと設定の不一致を調査
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils import load_rccm_data_files
from config import DataConfig, RCCMConfig
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def investigate_department_mapping():
    """部門マッピングの詳細調査"""
    logger.info("🔍 部門マッピング調査開始")
    
    # 1. 実際のデータから部門名を抽出
    data_dir = os.path.dirname(DataConfig.QUESTIONS_CSV)
    all_questions = load_rccm_data_files(data_dir)
    
    logger.info(f"総問題数: {len(all_questions)}")
    
    # 実際のデータの部門名を収集
    actual_departments = set()
    department_counts = {}
    
    for q in all_questions:
        dept = q.get('department', 'MISSING')
        actual_departments.add(dept)
        
        if dept not in department_counts:
            department_counts[dept] = 0
        department_counts[dept] += 1
    
    logger.info(f"\n📊 実際のデータに存在する部門名:")
    for dept in sorted(actual_departments):
        count = department_counts.get(dept, 0)
        logger.info(f"  '{dept}': {count}問")
    
    # 2. 設定ファイルの部門定義を確認
    logger.info(f"\n⚙️ config.py で定義されている部門ID:")
    for dept_id, info in RCCMConfig.DEPARTMENTS.items():
        logger.info(f"  '{dept_id}': {info['name']}")
    
    # 3. マッピングの不一致を検出
    logger.info(f"\n🚨 マッピング不一致の検出:")
    
    config_dept_ids = set(RCCMConfig.DEPARTMENTS.keys())
    
    # データに存在するが設定にない部門
    data_only = actual_departments - config_dept_ids
    if data_only:
        logger.error(f"❌ データにあるが設定にない部門: {data_only}")
    
    # 設定にあるがデータにない部門
    config_only = config_dept_ids - actual_departments
    if config_only:
        logger.error(f"❌ 設定にあるがデータにない部門: {config_only}")
        
        # 具体的に何問取得できるかテスト
        for missing_dept in config_only:
            logger.info(f"\n🔍 部門'{missing_dept}'の問題検索テスト:")
            
            # 専門科目でフィルタリング
            specialist_questions = [q for q in all_questions 
                                  if q.get('question_type') == 'specialist']
            logger.info(f"  専門科目総数: {len(specialist_questions)}問")
            
            # 部門でフィルタリング
            dept_questions = [q for q in specialist_questions 
                            if q.get('department') == missing_dept]
            logger.info(f"  部門'{missing_dept}'の問題: {len(dept_questions)}問")
            
            # 類似する部門名を検索
            similar_depts = []
            for actual_dept in actual_departments:
                if (missing_dept in actual_dept or 
                    actual_dept in missing_dept or
                    any(word in actual_dept for word in missing_dept.split('_'))):
                    similar_depts.append(actual_dept)
            
            if similar_depts:
                logger.info(f"  類似部門名: {similar_depts}")
                for similar in similar_depts:
                    similar_count = len([q for q in specialist_questions 
                                       if q.get('department') == similar])
                    logger.info(f"    '{similar}': {similar_count}問")
    
    # 4. 正常にマッピングされている部門
    correct_mapping = config_dept_ids & actual_departments
    if correct_mapping:
        logger.info(f"\n✅ 正常にマッピングされている部門:")
        for dept in sorted(correct_mapping):
            count = department_counts.get(dept, 0)
            logger.info(f"  '{dept}': {count}問")

def test_specific_department_filtering():
    """特定部門のフィルタリングテスト"""
    logger.info(f"\n🧪 特定部門フィルタリングテスト")
    
    data_dir = os.path.dirname(DataConfig.QUESTIONS_CSV)
    all_questions = load_rccm_data_files(data_dir)
    
    # 問題のあった civil_planning を詳しく調査
    target_dept = 'civil_planning'
    
    logger.info(f"\n🎯 部門'{target_dept}'の詳細調査:")
    
    # フィルタリング段階を詳しく追跡
    logger.info(f"1. 全問題数: {len(all_questions)}")
    
    # 専門科目フィルタ
    specialist_questions = []
    for q in all_questions:
        if q.get('question_type') == 'specialist':
            specialist_questions.append(q)
    logger.info(f"2. 専門科目問題数: {len(specialist_questions)}")
    
    # 部門フィルタ
    dept_questions = []
    for q in specialist_questions:
        q_dept = q.get('department', 'MISSING')
        if q_dept == target_dept:
            dept_questions.append(q)
    
    logger.info(f"3. 部門'{target_dept}'問題数: {len(dept_questions)}")
    
    if len(dept_questions) == 0:
        logger.error(f"❌ 部門'{target_dept}'の問題が0問です！")
        
        # 他の部門名候補を検索
        logger.info(f"4. 河川・砂防・海岸関連の部門名を検索:")
        keywords = ['河川', '砂防', '海岸', '海洋', 'river', 'civil', 'coastal']
        
        found_depts = set()
        for q in specialist_questions:
            q_dept = q.get('department', '')
            for keyword in keywords:
                if keyword in q_dept.lower():
                    found_depts.add(q_dept)
        
        if found_depts:
            logger.info(f"   関連部門名: {found_depts}")
            for found_dept in found_depts:
                count = len([q for q in specialist_questions 
                           if q.get('department') == found_dept])
                logger.info(f"     '{found_dept}': {count}問")
        else:
            logger.error(f"   河川・砂防関連の部門名が見つかりません")

if __name__ == '__main__':
    logger.info("🚨" * 30)
    logger.info("部門マッピング不一致調査")
    logger.info("🚨" * 30)
    
    investigate_department_mapping()
    test_specific_department_filtering()
    
    logger.info(f"\n調査完了")