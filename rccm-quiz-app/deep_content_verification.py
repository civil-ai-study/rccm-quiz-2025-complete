#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 深層混在問題検証スクリプト
本番環境での実際の問題内容を確認し、4-1/4-2の混在を検証

過去の検証の問題点：
1. 動的読み込みのため、HTMLからは問題内容を取得できない
2. Seleniumなどのブラウザ自動化が必要
3. 実際のユーザー操作をシミュレートする必要がある

新しいアプローチ：
1. ローカル環境での実際の動作確認
2. app.pyのロジックを直接テスト
3. 実際のCSVデータを確認
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# app.pyから必要な関数をインポート
try:
    from app import (
        load_questions, 
        get_mixed_questions, 
        normalize_department_name,
        get_department_category,
        get_user_session_size
    )
    print("✅ app.pyから関数をインポート成功")
except ImportError as e:
    print(f"❌ インポートエラー: {e}")
    print("ローカル環境でのみ実行可能です")
    sys.exit(1)

import json
from datetime import datetime
from collections import defaultdict

class DeepContentVerification:
    def __init__(self):
        self.verification_results = {
            'timestamp': datetime.now().isoformat(),
            'verification_type': 'DEEP_CONTENT_VERIFICATION',
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'contamination_found': [],
            'detailed_results': []
        }
        
    def load_and_analyze_data(self):
        """実際のCSVデータを読み込んで分析"""
        print("\n📊 実際のデータ分析開始")
        
        all_questions = load_questions()
        print(f"✅ 全問題数: {len(all_questions)}")
        
        # 問題種別ごとに分類
        basic_questions = [q for q in all_questions if q.get('question_type') == 'basic']
        specialist_questions = [q for q in all_questions if q.get('question_type') == 'specialist']
        
        print(f"📚 基礎科目（4-1）: {len(basic_questions)}問")
        print(f"📚 専門科目（4-2）: {len(specialist_questions)}問")
        
        # カテゴリー別の内訳
        basic_categories = defaultdict(int)
        specialist_categories = defaultdict(int)
        
        for q in basic_questions:
            basic_categories[q.get('category', 'なし')] += 1
            
        for q in specialist_questions:
            specialist_categories[q.get('category', 'なし')] += 1
            
        print("\n🔍 基礎科目のカテゴリー内訳:")
        for cat, count in basic_categories.items():
            print(f"  - {cat}: {count}問")
            
        print("\n🔍 専門科目のカテゴリー内訳:")
        for cat, count in specialist_categories.items():
            print(f"  - {cat}: {count}問")
            
        return all_questions, basic_questions, specialist_questions
    
    def simulate_user_selection(self, all_questions, department, year, question_type):
        """ユーザーの選択をシミュレート"""
        print(f"\n🎯 シミュレーション: {department} / {year}年 / {question_type}")
        
        # セッションをシミュレート
        mock_session = {
            'selected_question_type': question_type,
            'selected_department': department,
            'selected_year': year,
            'history': [],
            'quiz_settings': {'questions_per_session': 10}
        }
        
        # get_mixed_questions関数を直接呼び出し
        selected_questions = get_mixed_questions(
            mock_session,
            all_questions,
            '全体',
            session_size=10,
            department=department,
            question_type=question_type,
            year=year
        )
        
        return selected_questions
    
    def verify_no_contamination(self, selected_questions, expected_type, test_name):
        """選択された問題に混在がないか確認"""
        contamination = []
        
        for q in selected_questions:
            actual_type = q.get('question_type', '')
            if actual_type != expected_type:
                contamination.append({
                    'question_id': q.get('id'),
                    'question': q.get('question', '')[:50] + '...',
                    'expected_type': expected_type,
                    'actual_type': actual_type,
                    'category': q.get('category', ''),
                    'year': q.get('year', '')
                })
        
        test_result = {
            'test_name': test_name,
            'expected_type': expected_type,
            'selected_count': len(selected_questions),
            'contamination_count': len(contamination),
            'passed': len(contamination) == 0,
            'contamination_details': contamination
        }
        
        self.verification_results['total_tests'] += 1
        if test_result['passed']:
            self.verification_results['passed_tests'] += 1
            print(f"✅ {test_name}: 合格 - {len(selected_questions)}問選択、混在なし")
        else:
            self.verification_results['failed_tests'] += 1
            self.verification_results['contamination_found'].extend(contamination)
            print(f"❌ {test_name}: 失敗 - {len(contamination)}問の混在検出！")
            for c in contamination[:3]:  # 最初の3つを表示
                print(f"   🚨 ID:{c['question_id']} - {c['actual_type']}が混入（期待: {c['expected_type']}）")
        
        self.verification_results['detailed_results'].append(test_result)
        return test_result['passed']
    
    def run_comprehensive_tests(self):
        """包括的なテストを実行"""
        print("\n" + "="*60)
        print("🔍 深層混在問題検証開始")
        print("="*60)
        
        # データ読み込み
        all_questions, basic_questions, specialist_questions = self.load_and_analyze_data()
        
        # テストケース1: 基礎科目選択時の検証
        print("\n📋 テストケース1: 基礎科目（4-1）選択時の検証")
        basic_selected = self.simulate_user_selection(all_questions, '', None, 'basic')
        self.verify_no_contamination(basic_selected, 'basic', '基礎科目選択')
        
        # テストケース2: 土質・基礎部門の2016年専門科目選択
        print("\n📋 テストケース2: 土質・基礎部門2016年専門科目（ユーザー報告ケース）")
        soil_2016 = self.simulate_user_selection(all_questions, 'soil_foundation', '2016', 'specialist')
        self.verify_no_contamination(soil_2016, 'specialist', '土質・基礎2016年専門科目')
        
        # 実際の問題内容も確認
        if soil_2016:
            print("\n🔍 選択された問題の詳細（最初の3問）:")
            for i, q in enumerate(soil_2016[:3]):
                print(f"\n問題{i+1}:")
                print(f"  ID: {q.get('id')}")
                print(f"  種別: {q.get('question_type')}")
                print(f"  カテゴリー: {q.get('category')}")
                print(f"  年度: {q.get('year')}")
                print(f"  問題文: {q.get('question', '')[:80]}...")
        
        # テストケース3: 各部門での専門科目選択
        departments = [
            'road', 'river_sand', 'city_planning', 'landscape',
            'construction_env', 'steel_concrete', 'soil_foundation',
            'construction_planning', 'water_supply', 'forest_civil',
            'agricultural_civil', 'tunnel'
        ]
        
        print("\n📋 テストケース3: 全部門での専門科目選択検証")
        for dept in departments:
            dept_questions = self.simulate_user_selection(all_questions, dept, '2019', 'specialist')
            self.verify_no_contamination(dept_questions, 'specialist', f'{dept}専門科目')
        
        # 最終レポート
        self.generate_report()
    
    def generate_report(self):
        """検証レポートの生成"""
        print("\n" + "="*60)
        print("📊 深層混在問題検証レポート")
        print("="*60)
        
        print(f"\n総テスト数: {self.verification_results['total_tests']}")
        print(f"✅ 合格: {self.verification_results['passed_tests']}")
        print(f"❌ 失敗: {self.verification_results['failed_tests']}")
        
        if self.verification_results['contamination_found']:
            print(f"\n🚨 混在検出数: {len(self.verification_results['contamination_found'])}")
            print("\n混在の詳細:")
            for c in self.verification_results['contamination_found'][:10]:  # 最初の10件
                print(f"  - ID:{c['question_id']} ({c['actual_type']}) が {c['expected_type']} に混入")
        else:
            print("\n✅ 混在は検出されませんでした")
        
        # JSONファイルに保存
        filename = f"deep_content_verification_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.verification_results, f, ensure_ascii=False, indent=2)
        print(f"\n📄 詳細レポート保存: {filename}")

def main():
    """メイン実行"""
    verifier = DeepContentVerification()
    verifier.run_comprehensive_tests()

if __name__ == "__main__":
    main()