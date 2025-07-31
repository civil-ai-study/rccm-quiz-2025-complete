#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚨 CRITICAL DIAGNOSIS: 全13部門問題混在バグ緊急診断スクリプト
=================================================================

【緊急事態】
森林土木部門で上水道問題が表示される深刻な問題混在バグを完全診断・修正

【診断対象】
- 全13部門の問題選択ロジック
- CSV_JAPANESE_CATEGORIES マッピング精度
- get_department_questions_ultrasync関数の動作
- load_questions関数のフィルタリング精度

【予想される問題】
1. 部門マッピングの不整合
2. 問題フィルタリングロジックの欠陥
3. セッション状態での部門情報混在
4. CSVデータの部門カテゴリ不整合

Created: 2025-07-27
Purpose: 根本原因特定と緊急修正
"""

import sys
import os
import json
import random
from datetime import datetime

# パスを追加してapp.pyから関数をインポート
sys.path.append('./rccm-quiz-app')
sys.path.append('.')

try:
    from rccm_quiz_app.app import (
        CSV_JAPANESE_CATEGORIES,
        get_department_questions_ultrasync,
        load_questions,
        load_basic_questions_only,
        logger
    )
    print("app.py からの関数インポート成功")
except ImportError as e:
    try:
        # フォールバック: 直接app.pyをインポート
        import importlib.util
        spec = importlib.util.spec_from_file_location("app", "app.py")
        app_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(app_module)
        
        CSV_JAPANESE_CATEGORIES = app_module.CSV_JAPANESE_CATEGORIES
        get_department_questions_ultrasync = app_module.get_department_questions_ultrasync
        load_questions = app_module.load_questions
        load_basic_questions_only = app_module.load_basic_questions_only
        logger = app_module.logger
        
        print("app.py 直接インポート成功")
    except Exception as e2:
        print(f"app.py インポートエラー: {e2}")
        sys.exit(1)

class CriticalDepartmentMixingDiagnostic:
    """部門問題混在バグの完全診断クラス"""
    
    def __init__(self):
        self.diagnosis_results = {
            'timestamp': datetime.now().isoformat(),
            'departments_tested': 0,
            'critical_issues_found': [],
            'department_results': {},
            'mapping_issues': [],
            'filtering_issues': [],
            'recommendations': []
        }
        
        # 全13部門リスト
        self.all_departments = [
            '基礎科目', '道路', '河川・砂防', '都市計画', '造園',
            '建設環境', '鋼構造・コンクリート', '土質・基礎', '施工計画',
            '上下水道', '森林土木', '農業土木', 'トンネル'
        ]
        
        print(f"🔍 診断開始: {len(self.all_departments)}部門を対象")
    
    def diagnose_mapping_accuracy(self):
        """CSV_JAPANESE_CATEGORIES マッピングの精度診断"""
        print("\n🔍 STEP 1: 部門マッピング精度診断")
        print("=" * 60)
        
        mapping_issues = []
        
        for department in self.all_departments:
            print(f"\n📋 部門: {department}")
            
            # マッピング存在確認
            if department not in CSV_JAPANESE_CATEGORIES:
                issue = f"マッピング不足: {department} がCSV_JAPANESE_CATEGORIESに存在しない"
                mapping_issues.append(issue)
                print(f"   ❌ {issue}")
                continue
                
            csv_category = CSV_JAPANESE_CATEGORIES[department]
            print(f"   ✅ マッピング: {department} -> {csv_category}")
            
            # 重複マッピング確認
            duplicate_depts = [k for k, v in CSV_JAPANESE_CATEGORIES.items() 
                             if v == csv_category and k != department]
            if duplicate_depts:
                issue = f"重複マッピング: {csv_category} に複数部門 {duplicate_depts + [department]}"
                mapping_issues.append(issue)
                print(f"   ⚠️ {issue}")
        
        self.diagnosis_results['mapping_issues'] = mapping_issues
        print(f"\n📊 マッピング診断結果: {len(mapping_issues)}件の問題を検出")
        
        return mapping_issues
    
    def diagnose_question_filtering(self):
        """問題フィルタリングロジックの診断"""
        print("\n🔍 STEP 2: 問題フィルタリング精度診断") 
        print("=" * 60)
        
        filtering_issues = []
        
        try:
            # 全問題データを読み込み
            all_questions = load_questions()
            print(f"✅ 全問題読み込み成功: {len(all_questions)}問")
            
            # 部門別カテゴリ分析
            categories_found = set()
            for question in all_questions:
                category = question.get('category', '不明')
                categories_found.add(category)
            
            print(f"📊 検出されたカテゴリ: {len(categories_found)}種類")
            for category in sorted(categories_found):
                count = sum(1 for q in all_questions if q.get('category') == category)
                print(f"   - {category}: {count}問")
            
            # 各部門での問題選択テスト
            for department in self.all_departments:
                print(f"\n🧪 部門テスト: {department}")
                
                try:
                    # 問題選択を実行
                    selected_questions = get_department_questions_ultrasync(department, 5)
                    
                    if not selected_questions:
                        issue = f"{department}: 問題が選択されない"
                        filtering_issues.append(issue)
                        print(f"   ❌ {issue}")
                        continue
                    
                    # 選択された問題のカテゴリ分析
                    selected_categories = set()
                    expected_category = CSV_JAPANESE_CATEGORIES.get(department, '不明')
                    
                    for q in selected_questions:
                        q_category = q.get('category', '不明')
                        selected_categories.add(q_category)
                        
                        # 期待カテゴリと異なる場合は詳細ログ
                        if q_category != expected_category:
                            issue = f"{department}: 期待カテゴリ'{expected_category}' ≠ 実際'{q_category}' (問題ID: {q.get('id')})"
                            filtering_issues.append(issue)
                            print(f"   ❌ 混在問題: ID{q.get('id')} - {q.get('question', '')[:50]}...")
                    
                    if len(selected_categories) == 1 and expected_category in selected_categories:
                        print(f"   ✅ 正常: 全{len(selected_questions)}問が'{expected_category}'")
                    else:
                        print(f"   ❌ 混在: 期待'{expected_category}' 実際{selected_categories}")
                        
                except Exception as e:
                    issue = f"{department}: 問題選択例外 - {str(e)}"
                    filtering_issues.append(issue)
                    print(f"   ❌ {issue}")
                    
        except Exception as e:
            issue = f"全問題読み込み失敗: {str(e)}"
            filtering_issues.append(issue)
            print(f"❌ {issue}")
        
        self.diagnosis_results['filtering_issues'] = filtering_issues
        print(f"\n📊 フィルタリング診断結果: {len(filtering_issues)}件の問題を検出")
        
        return filtering_issues
    
    def test_forest_civil_engineering_specifically(self):
        """森林土木部門の詳細診断（問題報告の焦点）"""
        print("\n🔍 STEP 3: 森林土木部門詳細診断") 
        print("=" * 60)
        
        department = '森林土木'
        critical_issues = []
        
        print(f"🎯 重点診断対象: {department}")
        
        # マッピング確認
        if department in CSV_JAPANESE_CATEGORIES:
            expected_category = CSV_JAPANESE_CATEGORIES[department]
            print(f"✅ マッピング確認: {department} -> {expected_category}")
        else:
            critical_issues.append(f"{department}のマッピングが存在しない")
            print(f"❌ マッピング不足: {department}")
            return critical_issues
        
        # 複数回の問題選択テスト（ランダム性確認）
        for test_round in range(5):
            print(f"\n🧪 テストラウンド {test_round + 1}/5")
            
            try:
                selected_questions = get_department_questions_ultrasync(department, 3)
                
                if not selected_questions:
                    critical_issues.append(f"ラウンド{test_round + 1}: {department}で問題が選択されない")
                    continue
                
                for i, question in enumerate(selected_questions):
                    q_id = question.get('id', '不明')
                    q_category = question.get('category', '不明')
                    q_text = question.get('question', '')[:80] + '...'
                    
                    print(f"   問題{i+1}: ID{q_id} | カテゴリ: {q_category}")
                    print(f"           内容: {q_text}")
                    
                    if q_category != expected_category:
                        critical_issues.append(
                            f"ラウンド{test_round + 1}: {department}で異カテゴリ問題 "
                            f"ID{q_id} '{q_category}' (期待: '{expected_category}')"
                        )
                        print(f"   ❌ 混在検出: 期待'{expected_category}' ≠ 実際'{q_category}'")
                    else:
                        print(f"   ✅ 正常: カテゴリ一致")
                        
            except Exception as e:
                critical_issues.append(f"ラウンド{test_round + 1}: {department}選択例外 - {str(e)}")
                print(f"   ❌ 例外: {e}")
        
        self.diagnosis_results['forest_civil_issues'] = critical_issues
        print(f"\n📊 森林土木詳細診断結果: {len(critical_issues)}件の重要問題を検出")
        
        return critical_issues
    
    def generate_fix_recommendations(self):
        """修正推奨事項の生成"""
        print("\n🔍 STEP 4: 修正推奨事項生成") 
        print("=" * 60)
        
        recommendations = []
        
        # マッピング問題の修正推奨
        if self.diagnosis_results['mapping_issues']:
            recommendations.append({
                'category': 'マッピング修正',
                'priority': 'HIGH',
                'action': 'CSV_JAPANESE_CATEGORIES辞書の完全性確認と修正',
                'details': self.diagnosis_results['mapping_issues']
            })
        
        # フィルタリング問題の修正推奨
        if self.diagnosis_results['filtering_issues']:
            recommendations.append({
                'category': 'フィルタリング修正',
                'priority': 'CRITICAL',
                'action': 'get_department_questions_ultrasync関数の問題選択ロジック修正',
                'details': self.diagnosis_results['filtering_issues'][:5]  # 最初の5件
            })
        
        # 森林土木特有問題の修正推奨
        if self.diagnosis_results.get('forest_civil_issues'):
            recommendations.append({
                'category': '森林土木緊急修正',
                'priority': 'CRITICAL',
                'action': '森林土木部門の問題選択ロジック完全見直し',
                'details': self.diagnosis_results['forest_civil_issues']
            })
        
        # 全般的な改善推奨
        recommendations.append({
            'category': '予防的改善',
            'priority': 'MEDIUM',
            'action': '全部門での定期的な整合性チェック実装',
            'details': ['自動テスト追加', 'セッション状態検証強化', 'エラーログ改善']
        })
        
        self.diagnosis_results['recommendations'] = recommendations
        
        for rec in recommendations:
            print(f"\n🎯 推奨事項: {rec['category']} [{rec['priority']}]")
            print(f"   アクション: {rec['action']}")
            if isinstance(rec['details'], list):
                for detail in rec['details'][:3]:  # 最初の3件表示
                    print(f"   - {detail}")
                if len(rec['details']) > 3:
                    print(f"   ... 他{len(rec['details']) - 3}件")
        
        return recommendations
    
    def save_diagnosis_report(self):
        """診断レポートをJSONファイルに保存"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"critical_department_mixing_diagnosis_report_{timestamp}.json"
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(self.diagnosis_results, f, ensure_ascii=False, indent=2)
            print(f"\n💾 診断レポート保存完了: {report_file}")
            return report_file
        except Exception as e:
            print(f"❌ レポート保存エラー: {e}")
            return None
    
    def run_complete_diagnosis(self):
        """完全診断の実行"""
        print("🚨 CRITICAL DEPARTMENT MIXING DIAGNOSIS 開始")
        print("=" * 80)
        
        try:
            # ステップ1: マッピング診断
            mapping_issues = self.diagnose_mapping_accuracy()
            
            # ステップ2: フィルタリング診断
            filtering_issues = self.diagnose_question_filtering()
            
            # ステップ3: 森林土木詳細診断
            forest_issues = self.test_forest_civil_engineering_specifically()
            
            # ステップ4: 修正推奨事項生成
            recommendations = self.generate_fix_recommendations()
            
            # 結果サマリー
            total_issues = len(mapping_issues) + len(filtering_issues) + len(forest_issues)
            
            print(f"\n" + "=" * 80)
            print("🚨 CRITICAL DIAGNOSIS 完了")
            print("=" * 80)
            print(f"📊 総検出問題数: {total_issues}件")
            print(f"   - マッピング問題: {len(mapping_issues)}件")
            print(f"   - フィルタリング問題: {len(filtering_issues)}件") 
            print(f"   - 森林土木問題: {len(forest_issues)}件")
            print(f"🎯 修正推奨事項: {len(recommendations)}件")
            
            # レポート保存
            report_file = self.save_diagnosis_report()
            
            return {
                'total_issues': total_issues,
                'report_file': report_file,
                'critical_level': 'HIGH' if total_issues > 10 else 'MEDIUM' if total_issues > 5 else 'LOW'
            }
            
        except Exception as e:
            print(f"❌ 診断実行エラー: {e}")
            import traceback
            traceback.print_exc()
            return {'error': str(e)}

def main():
    """メイン実行関数"""
    print("🚨 RCCM Quiz App - Critical Department Mixing Diagnostic")
    print("=" * 80)
    
    diagnostic = CriticalDepartmentMixingDiagnostic()
    result = diagnostic.run_complete_diagnosis()
    
    if 'error' in result:
        print(f"\n❌ 診断失敗: {result['error']}")
        return 1
    
    print(f"\n✅ 診断完了")
    print(f"📊 問題レベル: {result['critical_level']}")
    if result.get('report_file'):
        print(f"📄 詳細レポート: {result['report_file']}")
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)