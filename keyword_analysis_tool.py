#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
キーワード分析ツール (森林土木部門専用)
==============================
上水道・森林関連キーワードの効果的な検出と分析
大規模テストでの精密な問題カテゴリ・内容チェック
cp932エラー完全回避・ASCII出力専用
"""

import sys
import os
import json
import re
from datetime import datetime
from collections import Counter, defaultdict

# Add app directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class KeywordAnalyzer:
    """キーワード分析エンジン（森林土木部門特化）"""
    
    def __init__(self):
        # 拡張キーワードデータベース
        self.keyword_db = {
            'water_primary': [
                '上水道', '工業用水道', '浄水場', '配水池', '給水管',
                '水処理', '取水', '送水', '導水', '配水'
            ],
            'water_secondary': [
                '水道管', '配管', '漏水', '水圧', '水質', '水源',
                '井戸', '地下水', '流量', '浄化', '消毒', '飲料水'
            ],
            'forest_primary': [
                '森林', '森林土木', '林道', '治山', '造林', '林業',
                '間伐', '伐採', '植林', '育林'
            ],
            'forest_secondary': [
                '山林', '保安林', '森林経営', '森林管理', '林地',
                '樹木', '立木', '森林資源', '木材', '林産'
            ],
            'suspicious': [
                '施設', '管路', '構造物', '設計', '施工',
                '維持管理', '品質管理', '計画', '事業'
            ]
        }
        
        self.analysis_results = {
            'timestamp': '',
            'total_questions': 0,
            'keyword_frequency': {},
            'category_breakdown': {},
            'mixing_patterns': [],
            'risk_assessment': 'unknown'
        }
    
    def ascii_print(self, message, prefix="[INFO]"):
        """ASCII専用出力（cp932エラー完全回避）"""
        try:
            # 日本語→英語変換テーブル
            jp_to_en = {
                '森林土木': 'Forest-Civil',
                '上水道': 'Water-Supply', 
                '問題': 'Question',
                '分析': 'Analysis',
                '検出': 'Detection',
                '混在': 'Mixing',
                'キーワード': 'Keyword',
                '結果': 'Result',
                '確認': 'Confirmed',
                'エラー': 'Error',
                '警告': 'Warning',
                '成功': 'Success'
            }
            
            safe_msg = message
            for jp, en in jp_to_en.items():
                safe_msg = safe_msg.replace(jp, en)
            
            # ASCII変換
            ascii_msg = safe_msg.encode('ascii', 'replace').decode('ascii')
            print(f"{prefix} {ascii_msg}")
            
        except Exception:
            print(f"{prefix} [Output Error - Fallback Mode]")
    
    def analyze_question_keywords(self, question_data):
        """個別問題のキーワード分析"""
        question_text = question_data.get('question', '')
        category = question_data.get('category', '')
        full_content = f"{category} {question_text}"
        
        analysis = {
            'content': full_content,
            'water_primary_hits': [],
            'water_secondary_hits': [],
            'forest_primary_hits': [],
            'forest_secondary_hits': [],
            'suspicious_hits': [],
            'risk_level': 0,
            'mixing_type': 'none'
        }
        
        # 各カテゴリのキーワードマッチング
        for keyword in self.keyword_db['water_primary']:
            if keyword in full_content:
                analysis['water_primary_hits'].append(keyword)
                analysis['risk_level'] += 3  # 高リスク
        
        for keyword in self.keyword_db['water_secondary']:
            if keyword in full_content:
                analysis['water_secondary_hits'].append(keyword)
                analysis['risk_level'] += 2  # 中リスク
        
        for keyword in self.keyword_db['forest_primary']:
            if keyword in full_content:
                analysis['forest_primary_hits'].append(keyword)
        
        for keyword in self.keyword_db['forest_secondary']:
            if keyword in full_content:
                analysis['forest_secondary_hits'].append(keyword)
        
        for keyword in self.keyword_db['suspicious']:
            if keyword in full_content:
                analysis['suspicious_hits'].append(keyword)
                analysis['risk_level'] += 1  # 低リスク
        
        # 混在タイプ判定
        has_water = analysis['water_primary_hits'] or analysis['water_secondary_hits']
        has_forest = analysis['forest_primary_hits'] or analysis['forest_secondary_hits']
        
        if has_water and has_forest:
            analysis['mixing_type'] = 'water_forest_hybrid'
        elif has_water and not has_forest:
            analysis['mixing_type'] = 'pure_water_content'
        elif not has_water and has_forest:
            analysis['mixing_type'] = 'pure_forest_content'
        elif analysis['suspicious_hits']:
            analysis['mixing_type'] = 'ambiguous_content'
        else:
            analysis['mixing_type'] = 'unclassified'
        
        return analysis
    
    def run_comprehensive_analysis(self, target_questions=25):
        """包括的キーワード分析実行"""
        self.ascii_print("=== Comprehensive Keyword Analysis ===")
        self.ascii_print(f"Target: {target_questions} questions from Forest-Civil department")
        
        self.analysis_results['timestamp'] = datetime.now().isoformat()
        
        try:
            # 問題取得
            self.ascii_print("Loading questions from application...")
            from app import get_department_questions_ultrasync
            
            questions = get_department_questions_ultrasync('森林土木', target_questions)
            
            if not questions:
                self.ascii_print("No questions retrieved", "[ERROR]")
                return False
            
            self.analysis_results['total_questions'] = len(questions)
            self.ascii_print(f"Retrieved {len(questions)} questions", "[OK]")
            
            # 分析実行
            self.ascii_print("Running keyword analysis...")
            
            all_keywords = Counter()
            category_stats = defaultdict(int)
            mixing_patterns = []
            high_risk_questions = []
            
            for i, question in enumerate(questions):
                analysis = self.analyze_question_keywords(question)
                
                # カテゴリ統計
                category = question.get('category', 'unknown')
                category_stats[category] += 1
                
                # キーワード頻度
                for keyword in (analysis['water_primary_hits'] + 
                              analysis['water_secondary_hits'] + 
                              analysis['forest_primary_hits'] + 
                              analysis['forest_secondary_hits'] + 
                              analysis['suspicious_hits']):
                    all_keywords[keyword] += 1
                
                # 混在パターン記録
                if analysis['mixing_type'] != 'pure_forest_content':
                    pattern = {
                        'question_num': i + 1,
                        'category': category,
                        'mixing_type': analysis['mixing_type'],
                        'risk_level': analysis['risk_level'],
                        'keywords': {
                            'water_primary': analysis['water_primary_hits'],
                            'water_secondary': analysis['water_secondary_hits'],
                            'forest_primary': analysis['forest_primary_hits'],
                            'forest_secondary': analysis['forest_secondary_hits'],
                            'suspicious': analysis['suspicious_hits']
                        }
                    }
                    mixing_patterns.append(pattern)
                
                # 高リスク問題
                if analysis['risk_level'] >= 5:
                    high_risk_questions.append({
                        'question_num': i + 1,
                        'risk_level': analysis['risk_level'],
                        'mixing_type': analysis['mixing_type']
                    })
                
                # 進捗表示（最初の10問のみ詳細）
                if i < 10:
                    self.ascii_print(f"Q{i+1}: {analysis['mixing_type']} (risk: {analysis['risk_level']})")
            
            # 結果保存
            self.analysis_results['keyword_frequency'] = dict(all_keywords)
            self.analysis_results['category_breakdown'] = dict(category_stats)
            self.analysis_results['mixing_patterns'] = mixing_patterns
            
            # 結果表示
            self.ascii_print("")
            self.ascii_print("=== Analysis Results ===")
            self.ascii_print(f"Questions analyzed: {len(questions)}")
            self.ascii_print(f"Mixing patterns found: {len(mixing_patterns)}")
            self.ascii_print(f"High-risk questions: {len(high_risk_questions)}")
            
            self.ascii_print("")
            self.ascii_print("Top keywords found:")
            for keyword, count in all_keywords.most_common(10):
                self.ascii_print(f"  {keyword}: {count} times")
            
            self.ascii_print("")
            self.ascii_print("Category distribution:")
            for category, count in category_stats.items():
                self.ascii_print(f"  {category}: {count} questions")
            
            # リスク評価
            water_mixing_count = sum(1 for p in mixing_patterns 
                                   if p['mixing_type'] in ['pure_water_content', 'water_forest_hybrid'])
            
            if water_mixing_count > 0:
                self.analysis_results['risk_assessment'] = 'HIGH_RISK'
                self.ascii_print("")
                self.ascii_print("=== HIGH RISK: Water supply mixing detected ===", "[CRITICAL]")
                self.ascii_print(f"Found {water_mixing_count} questions with water supply content")
                
                for pattern in mixing_patterns[:5]:  # 上位5件表示
                    if pattern['mixing_type'] in ['pure_water_content', 'water_forest_hybrid']:
                        keywords = []
                        keywords.extend(pattern['keywords']['water_primary'])
                        keywords.extend(pattern['keywords']['water_secondary'])
                        self.ascii_print(f"  Q{pattern['question_num']}: {', '.join(keywords[:3])}")
                
                return False
            
            elif len(mixing_patterns) > len(questions) * 0.2:  # 20%以上が疑わしい
                self.analysis_results['risk_assessment'] = 'MEDIUM_RISK'
                self.ascii_print("")
                self.ascii_print("=== MEDIUM RISK: Suspicious patterns detected ===", "[WARNING]")
                self.ascii_print(f"Found {len(mixing_patterns)} questionable questions")
                return False
            
            else:
                self.analysis_results['risk_assessment'] = 'LOW_RISK'
                self.ascii_print("")
                self.ascii_print("=== LOW RISK: Forest content appears pure ===", "[OK]")
                forest_pure_count = len(questions) - len(mixing_patterns)
                self.ascii_print(f"Pure forest content: {forest_pure_count}/{len(questions)} questions")
                return True
        
        except Exception as e:
            self.ascii_print(f"Analysis failed: {str(e)}", "[ERROR]")
            self.analysis_results['risk_assessment'] = 'ANALYSIS_ERROR'
            return False
    
    def save_analysis_results(self):
        """分析結果の保存"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"keyword_analysis_{timestamp}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.analysis_results, f, ensure_ascii=False, indent=2)
            
            self.ascii_print(f"Analysis saved to: {filename}", "[OK]")
            return filename
        
        except Exception as e:
            self.ascii_print(f"Save failed: {str(e)}", "[ERROR]")
            return None

def main():
    """メイン実行関数"""
    print("Forest Civil Engineering Department - Keyword Analysis Tool")
    print("CP932 Error Prevention & Comprehensive Mixing Detection")
    print("=" * 80)
    
    analyzer = KeywordAnalyzer()
    
    # 大規模分析実行
    success = analyzer.run_comprehensive_analysis(30)  # 30問で分析
    
    # 結果保存
    result_file = analyzer.save_analysis_results()
    
    # 最終結果
    print("\n" + "=" * 80)
    if success:
        analyzer.ascii_print("FINAL RESULT: Forest department content appears clean", "[SUCCESS]")
        analyzer.ascii_print("No significant water supply mixing detected", "[SUCCESS]")
    else:
        analyzer.ascii_print("FINAL RESULT: Water mixing or suspicious patterns detected", "[WARNING]")
        analyzer.ascii_print("Further investigation and cleanup required", "[WARNING]")
    
    if result_file:
        analyzer.ascii_print(f"Detailed analysis: {result_file}")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())