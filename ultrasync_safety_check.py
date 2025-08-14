#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ウルトラシンク安全性確認：既存機能の詳細動作検証
目的: 副作用ゼロを保証するための現状機能完全把握
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'rccm-quiz-app'))

from app import app

def test_existing_system_safety():
    """既存システムの安全性確認テスト"""
    print("=== ウルトラシンク安全性確認テスト ===")
    print("目的: 副作用ゼロを保証するための現状機能把握\n")
    
    safety_results = {
        'department_access': 0,
        'quiz_functionality': 0,
        'session_management': 0,
        'data_integrity': 0,
        'error_handling': 0
    }
    
    with app.test_client() as client:
        
        # 1. 部門アクセス機能確認
        print("【1. 部門アクセス機能確認】")
        test_departments = ['basic', 'road', 'river', 'urban', 'tunnel']
        
        for dept in test_departments:
            response = client.get(f'/departments/{dept}/types')
            if response.status_code == 200:
                print(f"  成功 {dept}部門: アクセス正常")
                safety_results['department_access'] += 1
            else:
                print(f"  エラー {dept}部門: エラー ({response.status_code})")
        
        # 2. クイズ機能確認
        print("\n【2. クイズ機能確認】")
        for dept in ['road', 'river']:
            # 部門選択→問題開始フロー
            response = client.get(f'/departments/{dept}/types')
            if response.status_code == 200:
                # 専門問題選択
                start_response = client.get(f'/start_exam/specialist_{dept}', follow_redirects=True)
                if start_response.status_code == 200:
                    # 問題画面確認
                    exam_response = client.get('/exam')
                    if exam_response.status_code == 200:
                        response_text = exam_response.get_data(as_text=True)
                        if "問題" in response_text and "question_id" in response_text:
                            print(f"  成功 {dept}部門: クイズ機能正常")
                            safety_results['quiz_functionality'] += 1
                        else:
                            print(f"  エラー {dept}部門: クイズ画面異常")
                    else:
                        print(f"  エラー {dept}部門: exam画面アクセス失敗")
                else:
                    print(f"  エラー {dept}部門: 専門問題選択失敗")
            else:
                print(f"  エラー {dept}部門: 部門アクセス失敗")
        
        # 3. セッション管理確認
        print("\n【3. セッション管理確認】")
        session_test = client.get('/departments/road/types')
        if session_test.status_code == 200:
            # セッション継続性確認
            start_response = client.get('/start_exam/specialist_road', follow_redirects=True)
            if start_response.status_code == 200:
                exam1 = client.get('/exam')
                if exam1.status_code == 200:
                    print("  成功 セッション作成・継続正常")
                    safety_results['session_management'] += 1
                else:
                    print("  エラー セッション継続失敗")
            else:
                print("  エラー セッション作成失敗")
        
        # 4. データ整合性確認
        print("\n【4. データ整合性確認】")
        try:
            # CSVデータアクセス確認
            from utils import load_questions
            questions = load_questions()
            if questions and len(questions) > 0:
                print(f"  成功 CSVデータ読み込み正常: {len(questions)}問")
                
                # カテゴリ分布確認
                categories = {}
                for q in questions:
                    cat = q.get('category', '不明')
                    categories[cat] = categories.get(cat, 0) + 1
                
                if len(categories) >= 12:  # 12部門以上
                    print(f"  成功 カテゴリ分布正常: {len(categories)}カテゴリ")
                    safety_results['data_integrity'] += 1
                else:
                    print(f"  警告 カテゴリ数不足: {len(categories)}カテゴリ")
            else:
                print("  エラー CSVデータ読み込み失敗")
        except Exception as e:
            print(f"  ❌ データ整合性確認エラー: {str(e)}")
        
        # 5. エラーハンドリング確認
        print("\n【5. エラーハンドリング確認】")
        # 存在しない部門アクセス
        error_response = client.get('/departments/nonexistent/types')
        if error_response.status_code in [404, 500]:
            print("  ✅ 不正アクセス時のエラーハンドリング正常")
            safety_results['error_handling'] += 1
        else:
            print("  ❌ エラーハンドリング異常")
    
    # 安全性評価
    print("\n=== 安全性評価結果 ===")
    total_score = sum(safety_results.values())
    max_score = len(safety_results) * 2  # 各項目最大2点
    
    for category, score in safety_results.items():
        status = "✅" if score >= 1 else "❌"
        print(f"{status} {category}: {score}点")
    
    safety_percentage = (total_score / max_score) * 100
    print(f"\n総合安全性スコア: {total_score}/{max_score} ({safety_percentage:.1f}%)")
    
    if safety_percentage >= 80:
        print("🛡️ 安全性評価: 優秀 - 修正作業を安全に実行可能")
        return True
    elif safety_percentage >= 60:
        print("⚠️ 安全性評価: 注意 - 慎重な修正が必要")
        return True
    else:
        print("🚨 安全性評価: 危険 - 修正作業を一時停止推奨")
        return False

if __name__ == "__main__":
    safety_ok = test_existing_system_safety()
    
    print(f"\n=== 最終判定 ===")
    if safety_ok:
        print("✅ ウルトラシンク修正作業の続行が安全")
        print("推奨: 段階3（英語ID変換システム依存箇所特定）に進行")
    else:
        print("❌ 修正作業は危険 - 現状の問題解決が優先")
        print("推奨: 既存問題の修正完了まで修正作業を延期")
    
    sys.exit(0 if safety_ok else 1)