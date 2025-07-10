#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 実データでの4-1/4-2混在検証
実際のCSVファイルを使用して混在問題を確認
"""

import csv
import json
from datetime import datetime
from collections import defaultdict

class RealDataVerification:
    def __init__(self):
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'verification_type': 'REAL_DATA_VERIFICATION',
            'data_analysis': {},
            'contamination_tests': [],
            'summary': {}
        }
    
    def load_41_data(self):
        """4-1（基礎科目）データの読み込み"""
        questions_41 = []
        try:
            with open('data/4-1.csv', 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # question_typeを追加
                    row['question_type'] = 'basic'
                    questions_41.append(row)
            print(f"✅ 4-1.csv から {len(questions_41)} 問読み込み完了")
        except Exception as e:
            print(f"❌ 4-1.csv 読み込みエラー: {e}")
        
        return questions_41
    
    def load_42_data(self, year='2016'):
        """4-2（専門科目）データの読み込み"""
        questions_42 = []
        try:
            filename = f'data/4-2_{year}.csv'
            with open(filename, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # question_typeを追加
                    row['question_type'] = 'specialist'
                    questions_42.append(row)
            print(f"✅ {filename} から {len(questions_42)} 問読み込み完了")
        except Exception as e:
            print(f"❌ {filename} 読み込みエラー: {e}")
        
        return questions_42
    
    def analyze_data(self, questions_41, questions_42):
        """データ分析"""
        print("\n📊 データ分析")
        
        # 4-1の分析
        categories_41 = defaultdict(int)
        for q in questions_41:
            categories_41[q.get('category', 'なし')] += 1
        
        print("\n4-1（基礎科目）のカテゴリー分布:")
        for cat, count in categories_41.items():
            print(f"  - {cat}: {count}問")
        
        # 4-2の分析
        categories_42 = defaultdict(int)
        for q in questions_42:
            categories_42[q.get('category', 'なし')] += 1
        
        print("\n4-2（専門科目）のカテゴリー分布:")
        for cat, count in sorted(categories_42.items(), key=lambda x: x[1], reverse=True):
            print(f"  - {cat}: {count}問")
        
        self.results['data_analysis'] = {
            '4-1_total': len(questions_41),
            '4-1_categories': dict(categories_41),
            '4-2_total': len(questions_42),
            '4-2_categories': dict(categories_42)
        }
    
    def simulate_get_mixed_questions(self, all_questions, question_type, category, year):
        """get_mixed_questions関数のシミュレーション（実データ版）"""
        selected = []
        
        for q in all_questions:
            # 問題種別フィルタ
            if question_type and q.get('question_type', '') != question_type:
                continue
            
            # カテゴリーフィルタ
            if category and q.get('category', '') != category:
                continue
            
            # 年度フィルタ
            if year and str(q.get('year', '')) != str(year):
                continue
            
            selected.append(q)
            
            # 10問で打ち切り
            if len(selected) >= 10:
                break
        
        return selected
    
    def check_contamination(self, selected_questions, expected_type, test_name):
        """混在チェック"""
        contamination = []
        
        for q in selected_questions:
            actual_type = q.get('question_type', '')
            if actual_type != expected_type:
                contamination.append({
                    'id': q.get('id', 'なし'),
                    'category': q.get('category', 'なし'),
                    'year': q.get('year', 'なし'),
                    'question': q.get('question', '')[:100] + '...',
                    'expected_type': expected_type,
                    'actual_type': actual_type
                })
        
        result = {
            'test_name': test_name,
            'selected_count': len(selected_questions),
            'expected_type': expected_type,
            'contamination_count': len(contamination),
            'passed': len(contamination) == 0,
            'contamination_details': contamination
        }
        
        self.results['contamination_tests'].append(result)
        
        if result['passed']:
            print(f"✅ {test_name}: 合格 ({len(selected_questions)}問選択、混在なし)")
        else:
            print(f"❌ {test_name}: 失敗 ({len(contamination)}問の混在検出！)")
            for c in contamination[:3]:
                print(f"   🚨 ID:{c['id']} - {c['actual_type']}が混入")
                print(f"      カテゴリー: {c['category']}, 問題: {c['question'][:50]}...")
        
        return result
    
    def run_verification(self):
        """検証実行"""
        print("="*80)
        print("🔍 実データでの4-1/4-2混在検証")
        print("="*80)
        
        # データ読み込み
        questions_41 = self.load_41_data()
        questions_42_2016 = self.load_42_data('2016')
        
        # 全問題結合
        all_questions = questions_41 + questions_42_2016
        print(f"\n✅ 全問題数: {len(all_questions)} (4-1: {len(questions_41)}, 4-2_2016: {len(questions_42_2016)})")
        
        # データ分析
        self.analyze_data(questions_41, questions_42_2016)
        
        print("\n" + "="*80)
        print("📊 混在テスト開始")
        print("="*80)
        
        # テストケース1: 基礎科目選択
        print("\n📋 テストケース1: 基礎科目（4-1）選択")
        basic_selected = self.simulate_get_mixed_questions(
            all_questions, 'basic', None, None
        )
        self.check_contamination(basic_selected, 'basic', '基礎科目選択')
        
        # テストケース2: 土質・基礎2016年専門科目（ユーザー報告ケース）
        print("\n📋 テストケース2: 土質・基礎2016年専門科目（ユーザー報告）")
        soil_2016 = self.simulate_get_mixed_questions(
            all_questions, 'specialist', '土質及び基礎', '2016'
        )
        self.check_contamination(soil_2016, 'specialist', '土質・基礎2016年専門科目')
        
        # 選択された問題の詳細表示
        if soil_2016:
            print(f"\n🔍 土質・基礎2016年で選択された{len(soil_2016)}問の詳細:")
            for i, q in enumerate(soil_2016[:5]):  # 最初の5問
                print(f"\n問題{i+1}:")
                print(f"  ID: {q.get('id')}")
                print(f"  種別: {q.get('question_type')}")
                print(f"  カテゴリー: {q.get('category')}")
                print(f"  年度: {q.get('year')}")
                print(f"  問題: {q.get('question')[:100]}...")
        
        # テストケース3: 専門科目全般（年度なし）で基礎が混入するか
        print("\n📋 テストケース3: 専門科目全般選択（混在リスク高）")
        specialist_all = self.simulate_get_mixed_questions(
            all_questions, 'specialist', None, None
        )
        self.check_contamination(specialist_all, 'specialist', '専門科目全般')
        
        # テストケース4: 道路部門2016年
        print("\n📋 テストケース4: 道路部門2016年専門科目")
        road_2016 = self.simulate_get_mixed_questions(
            all_questions, 'specialist', '道路', '2016'
        )
        self.check_contamination(road_2016, 'specialist', '道路2016年専門科目')
        
        # レポート生成
        self.generate_report()
    
    def generate_report(self):
        """検証レポート生成"""
        print("\n" + "="*80)
        print("📊 実データ混在検証レポート")
        print("="*80)
        
        # テスト結果集計
        total_tests = len(self.results['contamination_tests'])
        passed_tests = sum(1 for t in self.results['contamination_tests'] if t['passed'])
        failed_tests = total_tests - passed_tests
        
        self.results['summary'] = {
            'total_tests': total_tests,
            'passed': passed_tests,
            'failed': failed_tests,
            'all_contaminations': []
        }
        
        print(f"\n総テスト数: {total_tests}")
        print(f"✅ 合格: {passed_tests}")
        print(f"❌ 失敗: {failed_tests}")
        
        # 混在詳細
        all_contaminations = []
        for test in self.results['contamination_tests']:
            if test['contamination_count'] > 0:
                all_contaminations.extend(test['contamination_details'])
        
        if all_contaminations:
            print(f"\n🚨 検出された混在問題:")
            for c in all_contaminations:
                print(f"\n混在ID: {c['id']}")
                print(f"  期待: {c['expected_type']}")
                print(f"  実際: {c['actual_type']}")
                print(f"  カテゴリー: {c['category']}")
                print(f"  問題: {c['question'][:80]}...")
        
        self.results['summary']['all_contaminations'] = all_contaminations
        
        # JSONレポート保存
        filename = f"real_data_verification_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        print(f"\n📄 詳細レポート保存: {filename}")

def main():
    verifier = RealDataVerification()
    verifier.run_verification()

if __name__ == "__main__":
    main()