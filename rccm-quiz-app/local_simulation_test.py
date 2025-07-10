#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 ローカルシミュレーション検証
app.pyの実際のロジックをシミュレートして混在を確認
"""

import json
from datetime import datetime
import csv

class LocalSimulationTest:
    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'verification_type': 'LOCAL_SIMULATION_TEST',
            'tests': [],
            'contamination_found': []
        }
    
    def load_questions_from_csv(self):
        """CSVファイルから問題を直接読み込み"""
        questions = []
        try:
            with open('data/questions.csv', 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    questions.append(row)
            print(f"✅ CSVから{len(questions)}問読み込み完了")
        except Exception as e:
            print(f"❌ CSV読み込みエラー: {e}")
            # Shift-JISで再試行
            try:
                with open('data/questions.csv', 'r', encoding='shift_jis') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        questions.append(row)
                print(f"✅ Shift-JISで{len(questions)}問読み込み完了")
            except Exception as e2:
                print(f"❌ Shift-JIS読み込みもエラー: {e2}")
        
        return questions
    
    def analyze_question_types(self, questions):
        """問題種別を分析"""
        type_count = {}
        category_by_type = {}
        
        for q in questions:
            q_type = q.get('question_type', 'unknown')
            category = q.get('Category', q.get('category', 'unknown'))
            
            # 問題種別カウント
            type_count[q_type] = type_count.get(q_type, 0) + 1
            
            # 問題種別ごとのカテゴリー
            if q_type not in category_by_type:
                category_by_type[q_type] = {}
            category_by_type[q_type][category] = category_by_type[q_type].get(category, 0) + 1
        
        print("\n📊 問題種別分析:")
        for q_type, count in type_count.items():
            print(f"  {q_type}: {count}問")
            if q_type in category_by_type:
                print(f"    カテゴリー内訳:")
                for cat, cat_count in category_by_type[q_type].items():
                    print(f"      - {cat}: {cat_count}問")
    
    def simulate_get_mixed_questions(self, questions, question_type, department, year):
        """get_mixed_questions関数のシミュレーション"""
        selected = []
        
        for q in questions:
            # 問題種別フィルタ
            if question_type and q.get('question_type', '') != question_type:
                continue
            
            # 基礎科目の場合、年度がないことを確認
            if question_type == 'basic' and q.get('year'):
                continue
            
            # 専門科目の場合、年度があることを確認
            if question_type == 'specialist' and not q.get('year'):
                continue
            
            # カテゴリーフィルタ（部門）
            if department == 'soil_foundation' and q.get('Category', '') != '土質及び基礎':
                continue
            
            # 年度フィルタ
            if year and str(q.get('year', '')) != str(year):
                continue
            
            selected.append(q)
            
            # 10問で打ち切り
            if len(selected) >= 10:
                break
        
        return selected
    
    def check_contamination(self, questions, expected_type, test_name):
        """混在チェック"""
        contamination = []
        
        for q in questions:
            actual_type = q.get('question_type', 'unknown')
            if actual_type != expected_type:
                contamination.append({
                    'id': q.get('ID', q.get('id', 'unknown')),
                    'question': q.get('Question', q.get('question', ''))[:100],
                    'expected_type': expected_type,
                    'actual_type': actual_type,
                    'category': q.get('Category', q.get('category', '')),
                    'year': q.get('year', '')
                })
        
        result = {
            'test_name': test_name,
            'total_questions': len(questions),
            'contamination_count': len(contamination),
            'passed': len(contamination) == 0,
            'contamination_details': contamination
        }
        
        if result['passed']:
            print(f"✅ {test_name}: 合格 ({len(questions)}問、混在なし)")
        else:
            print(f"❌ {test_name}: 失敗 ({len(contamination)}問の混在検出！)")
            for c in contamination[:3]:
                print(f"   🚨 {c['actual_type']}が混入: {c['question'][:50]}...")
        
        self.results['tests'].append(result)
        if contamination:
            self.results['contamination_found'].extend(contamination)
        
        return result['passed']
    
    def run_tests(self):
        """テスト実行"""
        print("="*60)
        print("🔍 ローカルシミュレーション検証")
        print("="*60)
        
        # 問題読み込み
        questions = self.load_questions_from_csv()
        if not questions:
            print("❌ 問題データが読み込めませんでした")
            return
        
        # 問題分析
        self.analyze_question_types(questions)
        
        # 実際の問題を表示
        print("\n📋 実際の問題サンプル（最初の5問）:")
        for i, q in enumerate(questions[:5]):
            print(f"\n問題{i+1}:")
            print(f"  ID: {q.get('ID', 'なし')}")
            print(f"  カテゴリー: {q.get('Category', 'なし')}")
            print(f"  問題種別: {q.get('question_type', 'なし')}")
            print(f"  年度: {q.get('year', 'なし')}")
            print(f"  問題: {q.get('Question', '')[:100]}...")
        
        print("\n" + "="*60)
        print("📊 混在テスト開始")
        print("="*60)
        
        # テストケース1: 基礎科目
        print("\n📋 テストケース1: 基礎科目（4-1）")
        basic_questions = self.simulate_get_mixed_questions(questions, 'basic', None, None)
        self.check_contamination(basic_questions, 'basic', '基礎科目選択')
        
        # テストケース2: 土質・基礎2016年専門科目（ユーザー報告ケース）
        print("\n📋 テストケース2: 土質・基礎2016年専門科目")
        soil_2016 = self.simulate_get_mixed_questions(questions, 'specialist', 'soil_foundation', '2016')
        self.check_contamination(soil_2016, 'specialist', '土質・基礎2016年専門科目')
        
        # 選択された問題の詳細表示
        if soil_2016:
            print("\n🔍 土質・基礎2016年で選択された問題:")
            for i, q in enumerate(soil_2016[:3]):
                print(f"\n  問題{i+1}:")
                print(f"    種別: {q.get('question_type', 'なし')}")
                print(f"    カテゴリー: {q.get('Category', 'なし')}")
                print(f"    年度: {q.get('year', 'なし')}")
                print(f"    問題: {q.get('Question', '')[:100]}...")
        
        # レポート生成
        self.generate_report()
    
    def generate_report(self):
        """レポート生成"""
        print("\n" + "="*60)
        print("📊 ローカルシミュレーション検証レポート")
        print("="*60)
        
        total_tests = len(self.results['tests'])
        passed_tests = sum(1 for t in self.results['tests'] if t['passed'])
        failed_tests = total_tests - passed_tests
        
        print(f"\n総テスト数: {total_tests}")
        print(f"✅ 合格: {passed_tests}")
        print(f"❌ 失敗: {failed_tests}")
        
        if self.results['contamination_found']:
            print(f"\n🚨 混在検出総数: {len(self.results['contamination_found'])}")
            print("\n混在の詳細:")
            for c in self.results['contamination_found']:
                print(f"  - ID:{c['id']} - {c['actual_type']}が{c['expected_type']}に混入")
                print(f"    カテゴリー: {c['category']}, 年度: {c['year']}")
                print(f"    問題: {c['question'][:80]}...")
        
        # レポート保存
        filename = f"local_simulation_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        print(f"\n📄 詳細レポート保存: {filename}")

def main():
    tester = LocalSimulationTest()
    tester.run_tests()

if __name__ == "__main__":
    main()