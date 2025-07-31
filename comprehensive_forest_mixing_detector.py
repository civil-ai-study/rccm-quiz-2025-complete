#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
森林土木部門上水道混在検出システム (cp932エラー回避版)
=================================================
1. ユニコード文字を使わずにテスト結果を表示
2. 20問以上の大規模テストで確実にチェック
3. 上水道・森林キーワードの効果的検出
4. テスト結果を確実に保存・検証
"""

import sys
import os
import json
import re
from datetime import datetime
from collections import defaultdict, Counter

# Add app directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class ForestMixingDetector:
    """森林土木部門の上水道問題混在検出器（cp932対応）"""
    
    def __init__(self):
        # ASCII文字のみ使用（cp932エラー回避）
        self.status_symbols = {
            'success': '[OK]',
            'error': '[ERROR]',
            'warning': '[WARNING]',
            'info': '[INFO]',
            'mixing': '[MIXING]',
            'forest': '[FOREST]'
        }
        
        # 拡張されたキーワードセット
        self.water_keywords = [
            '上水道', '工業用水道', '浄水', '配水', '給水', '水処理', 
            '取水', '送水', '導水', '水道管', '配水管', '給水管',
            '浄水場', '配水池', '水質', '水源', '井戸', '地下水',
            '水圧', '漏水', '水量', '流量', '浄化', '消毒',
            '水道事業', '上水', '生活用水', '飲料水'
        ]
        
        self.forest_keywords = [
            '森林', '林道', '治山', '木材', '森林土木', '造林', '林業',
            '山林', '植林', '間伐', '伐採', '育林', '保安林',
            '森林経営', '森林管理', '林地', '樹木', '立木', '森林資源',
            '森林生態', '森林保護', '森林施業', '林産', '木質',
            '緑化', '植生', '山地災害', '土砂災害'
        ]
        
        # 疑似キーワード（混在の可能性があるキーワード）
        self.suspicious_keywords = [
            '管路', '配管', '施設', '構造物', '設計', '施工',
            '維持管理', '品質管理', '安全管理', '環境', '計画'
        ]
        
        self.test_results = {
            'timestamp': '',
            'department': '森林土木',
            'total_questions': 0,
            'questions_analyzed': [],
            'mixing_detected': [],
            'forest_content': [],
            'suspicious_content': [],
            'category_stats': {},
            'keyword_stats': {},
            'final_assessment': ''
        }
    
    def print_safe(self, message, status='info'):
        """cp932エラーを回避した安全な出力"""
        symbol = self.status_symbols.get(status, '[INFO]')
        try:
            # ASCII文字のみで出力を構成
            safe_message = self._make_ascii_safe(message)
            print(f"{symbol} {safe_message}")
        except UnicodeEncodeError:
            # フォールバック: エラーを起こす文字を置換
            safe_message = message.encode('ascii', 'replace').decode('ascii')
            print(f"{symbol} {safe_message}")
    
    def _make_ascii_safe(self, text):
        """テキストをASCII安全にする"""
        # 日本語文字をローマ字表記に変換（主要なもののみ）
        replacements = {
            '森林土木': 'Shinrin-Doboku',
            '上水道': 'Jyousuidou',
            '問題': 'Question',
            '検出': 'Detection',
            '混在': 'Mixing',
            '成功': 'Success',
            'エラー': 'Error',
            '警告': 'Warning'
        }
        
        result = text
        for jp, en in replacements.items():
            result = result.replace(jp, en)
        
        return result
    
    def analyze_question_content(self, question, question_num):
        """問題内容の詳細分析"""
        analysis = {
            'number': question_num,
            'category': question.get('category', ''),
            'question_text': question.get('question', ''),
            'water_keywords_found': [],
            'forest_keywords_found': [],
            'suspicious_keywords_found': [],
            'mixing_risk': 'low',
            'content_preview': ''
        }
        
        full_text = f"{analysis['category']} {analysis['question_text']}"
        analysis['content_preview'] = full_text[:150] + "..." if len(full_text) > 150 else full_text
        
        # 上水道キーワード検出
        for keyword in self.water_keywords:
            if keyword in full_text:
                analysis['water_keywords_found'].append(keyword)
        
        # 森林キーワード検出
        for keyword in self.forest_keywords:
            if keyword in full_text:
                analysis['forest_keywords_found'].append(keyword)
        
        # 疑似キーワード検出
        for keyword in self.suspicious_keywords:
            if keyword in full_text:
                analysis['suspicious_keywords_found'].append(keyword)
        
        # 混在リスク評価
        if analysis['water_keywords_found']:
            if analysis['forest_keywords_found']:
                analysis['mixing_risk'] = 'medium'  # 両方のキーワードが存在
            else:
                analysis['mixing_risk'] = 'high'    # 上水道キーワードのみ
        elif analysis['suspicious_keywords_found'] and not analysis['forest_keywords_found']:
            analysis['mixing_risk'] = 'medium'      # 疑似キーワードのみ
        
        return analysis
    
    def run_comprehensive_test(self, target_questions=25):
        """包括的な混在検出テスト実行"""
        self.print_safe("=== Comprehensive Forest Mixing Detection Test ===")
        self.print_safe(f"Target: {target_questions} questions from Shinrin-Doboku department")
        self.print_safe("")
        
        self.test_results['timestamp'] = datetime.now().isoformat()
        
        try:
            # アプリケーションから問題を取得
            self.print_safe("Loading questions from application...", 'info')
            
            # 動的インポート（エラー処理付き）
            try:
                from app import get_department_questions_ultrasync
                self.print_safe("Successfully imported question function", 'success')
            except ImportError as e:
                self.print_safe(f"Import error: {str(e)}", 'error')
                return False
            
            # 問題取得
            questions = get_department_questions_ultrasync('森林土木', target_questions)
            
            if not questions:
                self.print_safe("No questions retrieved from Shinrin-Doboku department", 'error')
                return False
            
            self.test_results['total_questions'] = len(questions)
            self.print_safe(f"Retrieved {len(questions)} questions", 'success')
            
            # 問題分析開始
            self.print_safe("")
            self.print_safe("=== Detailed Question Analysis ===")
            
            mixing_count = 0
            forest_count = 0
            suspicious_count = 0
            category_counter = Counter()
            keyword_counter = Counter()
            
            for i, question in enumerate(questions):
                analysis = self.analyze_question_content(question, i + 1)
                self.test_results['questions_analyzed'].append(analysis)
                
                # カテゴリ統計
                category_counter[analysis['category']] += 1
                
                # キーワード統計
                for keyword in analysis['water_keywords_found']:
                    keyword_counter[f"WATER: {keyword}"] += 1
                for keyword in analysis['forest_keywords_found']:
                    keyword_counter[f"FOREST: {keyword}"] += 1
                
                # 結果表示
                self.print_safe(f"Q{i+1}: {analysis['category']}")
                
                if analysis['water_keywords_found']:
                    mixing_count += 1
                    self.test_results['mixing_detected'].append(analysis)
                    keywords_str = ", ".join(analysis['water_keywords_found'])
                    self.print_safe(f"  WATER MIXING DETECTED: {keywords_str}", 'mixing')
                
                if analysis['forest_keywords_found']:
                    forest_count += 1
                    self.test_results['forest_content'].append(analysis)
                    keywords_str = ", ".join(analysis['forest_keywords_found'])
                    self.print_safe(f"  Forest content: {keywords_str}", 'forest')
                
                if analysis['mixing_risk'] in ['medium', 'high'] and analysis['suspicious_keywords_found']:
                    suspicious_count += 1
                    self.test_results['suspicious_content'].append(analysis)
                    keywords_str = ", ".join(analysis['suspicious_keywords_found'])
                    self.print_safe(f"  Suspicious content: {keywords_str}", 'warning')
                
                if i < 5:  # 最初の5問のみ詳細表示
                    self.print_safe(f"  Preview: {analysis['content_preview'][:100]}...")
                
                self.print_safe("")
            
            # 統計情報保存
            self.test_results['category_stats'] = dict(category_counter)
            self.test_results['keyword_stats'] = dict(keyword_counter)
            
            # 結果サマリー表示
            self.print_safe("=== Test Results Summary ===")
            self.print_safe(f"Total questions analyzed: {len(questions)}")
            self.print_safe(f"Water mixing detected: {mixing_count} questions")
            self.print_safe(f"Forest content found: {forest_count} questions")
            self.print_safe(f"Suspicious content: {suspicious_count} questions")
            
            self.print_safe("")
            self.print_safe("Category distribution:")
            for category, count in category_counter.most_common():
                self.print_safe(f"  {category}: {count} questions")
            
            # 最終評価
            if mixing_count > 0:
                self.test_results['final_assessment'] = 'MIXING_DETECTED'
                self.print_safe("")
                self.print_safe("=== CRITICAL: WATER SUPPLY MIXING DETECTED ===", 'error')
                self.print_safe(f"Found {mixing_count} water supply questions in forest department")
                
                for mixing in self.test_results['mixing_detected']:
                    keywords_str = ", ".join(mixing['water_keywords_found'])
                    self.print_safe(f"  Q{mixing['number']}: {keywords_str}")
                
                return False
            
            elif suspicious_count > len(questions) * 0.3:  # 30%以上が疑わしい場合
                self.test_results['final_assessment'] = 'HIGH_SUSPICION'
                self.print_safe("")
                self.print_safe("=== WARNING: HIGH SUSPICION OF MIXING ===", 'warning')
                self.print_safe(f"Found {suspicious_count} suspicious questions (>{30}% of total)")
                return False
            
            else:
                self.test_results['final_assessment'] = 'NO_MIXING'
                self.print_safe("")
                self.print_safe("=== RESULT: NO WATER SUPPLY MIXING DETECTED ===", 'success')
                self.print_safe(f"Forest content purity: {forest_count}/{len(questions)} questions")
                return True
        
        except Exception as e:
            self.print_safe(f"Test execution error: {str(e)}", 'error')
            self.test_results['final_assessment'] = 'TEST_ERROR'
            self.test_results['error'] = str(e)
            return False
    
    def save_results(self):
        """テスト結果の安全な保存"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"comprehensive_forest_mixing_test_{timestamp}.json"
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.test_results, f, ensure_ascii=False, indent=2)
            
            self.print_safe(f"Test results saved to: {filename}", 'success')
            return filename
        
        except Exception as e:
            self.print_safe(f"Failed to save results: {str(e)}", 'error')
            return None
    
    def generate_report(self):
        """テスト結果レポート生成"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"forest_mixing_report_{timestamp}.txt"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("Forest Civil Engineering Department - Water Supply Mixing Detection Report\n")
                f.write("=" * 80 + "\n\n")
                
                f.write(f"Test Date: {self.test_results['timestamp']}\n")
                f.write(f"Department: {self.test_results['department']}\n")
                f.write(f"Questions Analyzed: {self.test_results['total_questions']}\n")
                f.write(f"Final Assessment: {self.test_results['final_assessment']}\n\n")
                
                if self.test_results['mixing_detected']:
                    f.write("WATER SUPPLY MIXING DETECTED:\n")
                    f.write("-" * 40 + "\n")
                    for mixing in self.test_results['mixing_detected']:
                        f.write(f"Question {mixing['number']}: {mixing['category']}\n")
                        f.write(f"Keywords: {', '.join(mixing['water_keywords_found'])}\n")
                        f.write(f"Preview: {mixing['content_preview']}\n\n")
                
                f.write("CATEGORY STATISTICS:\n")
                f.write("-" * 40 + "\n")
                for category, count in self.test_results['category_stats'].items():
                    f.write(f"{category}: {count} questions\n")
                
                f.write("\nKEYWORD STATISTICS:\n")
                f.write("-" * 40 + "\n")
                for keyword, count in self.test_results['keyword_stats'].items():
                    f.write(f"{keyword}: {count} occurrences\n")
            
            self.print_safe(f"Report generated: {filename}", 'success')
            return filename
        
        except Exception as e:
            self.print_safe(f"Failed to generate report: {str(e)}", 'error')
            return None

def main():
    """メイン実行関数"""
    print("Comprehensive Forest Civil Engineering Mixing Detection System")
    print("CP932 Error Prevention & Large Scale Testing")
    print("=" * 80)
    
    detector = ForestMixingDetector()
    
    # 大規模テスト実行（25問）
    success = detector.run_comprehensive_test(25)
    
    # 結果保存
    json_file = detector.save_results()
    report_file = detector.generate_report()
    
    # 最終結果
    print("\n" + "=" * 80)
    if success:
        detector.print_safe("FINAL RESULT: No water supply mixing detected in forest department", 'success')
        detector.print_safe("Forest department content purity confirmed", 'success')
    else:
        detector.print_safe("FINAL RESULT: Water supply mixing detected or high suspicion", 'error')
        detector.print_safe("Further investigation required", 'warning')
    
    if json_file:
        detector.print_safe(f"Detailed results: {json_file}")
    if report_file:
        detector.print_safe(f"Analysis report: {report_file}")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())