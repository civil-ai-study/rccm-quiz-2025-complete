#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔥 本番環境HTML構造分析
本番環境で実際の問題内容抽出失敗の原因調査

目的:
1. 実際のHTMLレスポンス構造を詳細分析
2. 問題文が動的読み込みか静的表示かを確認
3. 適切な抽出手法を特定

対象: https://rccm-quiz-2025.onrender.com
"""

import requests
import json
import time
from datetime import datetime
import re
import urllib.parse
from typing import Dict, List, Optional, Tuple
import logging
# BeautifulSoup使用なしバージョン
import base64

# ログ設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ProductionHtmlStructureAnalysis:
    def __init__(self):
        self.base_url = "https://rccm-quiz-2025.onrender.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ja-JP,ja;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        })
        
        # 分析結果
        self.analysis_results = {
            'timestamp': datetime.now().isoformat(),
            'analysis_type': 'PRODUCTION_HTML_STRUCTURE_ANALYSIS',
            'target_url': self.base_url,
            'html_samples': {},
            'extraction_methods_tested': {},
            'dynamic_content_indicators': [],
            'static_content_found': [],
            'recommended_extraction_approach': '',
            'critical_findings': []
        }

    def capture_html_samples(self) -> Dict:
        """本番環境からのHTMLサンプル取得"""
        
        print("🔍 本番環境HTML構造解析開始")
        print("=" * 80)
        
        html_samples = {}
        
        try:
            # 1. ホームページのHTML構造
            print("📍 Step 1: ホームページHTML構造分析")
            home_response = self.session.get(self.base_url, timeout=30)
            
            if home_response.status_code == 200:
                html_samples['homepage'] = {
                    'url': self.base_url,
                    'status_code': home_response.status_code,
                    'content_length': len(home_response.text),
                    'raw_html': home_response.text[:5000],  # 最初の5000文字
                    'encoding': home_response.encoding,
                    'headers': dict(home_response.headers)
                }
                print(f"  ✅ ホームページ取得成功 (長さ: {len(home_response.text)}文字)")
            
            time.sleep(2)
            
            # 2. 基礎科目試験のHTML構造
            print("📍 Step 2: 基礎科目試験HTML構造分析")
            basic_url = f"{self.base_url}/start_exam/basic"
            basic_data = {'questions': '10'}
            
            basic_response = self.session.post(basic_url, data=basic_data, timeout=30, allow_redirects=True)
            
            if basic_response.status_code in [200, 302]:
                html_samples['basic_exam'] = {
                    'url': basic_url,
                    'data': basic_data,
                    'status_code': basic_response.status_code,
                    'content_length': len(basic_response.text),
                    'raw_html': basic_response.text[:10000],  # 最初の10000文字
                    'full_html': basic_response.text,  # 完全なHTML
                    'encoding': basic_response.encoding,
                    'headers': dict(basic_response.headers),
                    'redirect_history': [r.url for r in basic_response.history]
                }
                print(f"  ✅ 基礎科目試験取得成功 (長さ: {len(basic_response.text)}文字)")
            
            time.sleep(2)
            
            # 3. 専門科目試験のHTML構造 
            print("📍 Step 3: 専門科目試験HTML構造分析")
            specialist_url = f"{self.base_url}/start_exam/specialist"
            specialist_data = {
                'questions': '10',
                'category': '建設環境',
                'year': '2019'
            }
            
            specialist_response = self.session.post(specialist_url, data=specialist_data, timeout=30, allow_redirects=True)
            
            if specialist_response.status_code in [200, 302]:
                html_samples['specialist_exam'] = {
                    'url': specialist_url,
                    'data': specialist_data,
                    'status_code': specialist_response.status_code,
                    'content_length': len(specialist_response.text),
                    'raw_html': specialist_response.text[:10000],  # 最初の10000文字
                    'full_html': specialist_response.text,  # 完全なHTML
                    'encoding': specialist_response.encoding,
                    'headers': dict(specialist_response.headers),
                    'redirect_history': [r.url for r in specialist_response.history]
                }
                print(f"  ✅ 専門科目試験取得成功 (長さ: {len(specialist_response.text)}文字)")
            
        except Exception as e:
            print(f"💥 HTML取得エラー: {str(e)}")
            html_samples['error'] = str(e)
        
        return html_samples

    def analyze_html_structure_deep(self, html_content: str, content_name: str) -> Dict:
        """HTML構造の詳細分析"""
        
        print(f"🔬 {content_name} 詳細構造分析")
        
        analysis = {
            'content_name': content_name,
            'basic_stats': {},
            'dom_structure': {},
            'javascript_analysis': {},
            'form_analysis': {},
            'question_content_analysis': {},
            'dynamic_indicators': [],
            'extraction_recommendations': []
        }
        
        try:
            # 基本統計
            analysis['basic_stats'] = {
                'total_length': len(html_content),
                'line_count': html_content.count('\n'),
                'tag_count': html_content.count('<'),
                'script_tags': html_content.count('<script'),
                'form_tags': html_content.count('<form'),
                'div_tags': html_content.count('<div'),
                'encoding_detected': 'utf-8' if 'utf-8' in html_content.lower() else 'unknown'
            }
            
            # 正規表現でのDOM分析
            try:
                # HTMLタグの基本カウント
                title_match = re.search(r'<title[^>]*>(.*?)</title>', html_content, re.IGNORECASE | re.DOTALL)
                title = title_match.group(1) if title_match else 'No title'
                
                analysis['dom_structure'] = {
                    'title': title.strip(),
                    'meta_tags': len(re.findall(r'<meta[^>]*>', html_content, re.IGNORECASE)),
                    'script_tags': len(re.findall(r'<script[^>]*>', html_content, re.IGNORECASE)),
                    'form_tags': len(re.findall(r'<form[^>]*>', html_content, re.IGNORECASE)),
                    'div_tags': len(re.findall(r'<div[^>]*>', html_content, re.IGNORECASE)),
                    'p_tags': len(re.findall(r'<p[^>]*>', html_content, re.IGNORECASE)),
                    'span_tags': len(re.findall(r'<span[^>]*>', html_content, re.IGNORECASE)),
                    'input_tags': len(re.findall(r'<input[^>]*>', html_content, re.IGNORECASE)),
                    'button_tags': len(re.findall(r'<button[^>]*>', html_content, re.IGNORECASE))
                }
                
                # JavaScriptの分析
                script_blocks = re.findall(r'<script[^>]*>(.*?)</script>', html_content, re.IGNORECASE | re.DOTALL)
                external_scripts = re.findall(r'<script[^>]*src=', html_content, re.IGNORECASE)
                
                js_analysis = {
                    'script_count': len(script_blocks) + len(external_scripts),
                    'external_scripts': len(external_scripts),
                    'inline_scripts': len(script_blocks),
                    'ajax_indicators': 0,
                    'fetch_indicators': 0,
                    'jquery_usage': False,
                    'dynamic_content_loading': False
                }
                
                for script_content in script_blocks:
                    script_lower = script_content.lower()
                    if 'ajax' in script_lower or 'xmlhttprequest' in script_lower:
                        js_analysis['ajax_indicators'] += 1
                    if 'fetch(' in script_lower:
                        js_analysis['fetch_indicators'] += 1
                    if 'jquery' in script_lower or '$(' in script_lower:
                        js_analysis['jquery_usage'] = True
                    if any(indicator in script_lower for indicator in ['load', 'onload', 'domcontentloaded', 'ready']):
                        js_analysis['dynamic_content_loading'] = True
                
                analysis['javascript_analysis'] = js_analysis
                
                # フォーム分析
                form_matches = re.findall(r'<form[^>]*>(.*?)</form>', html_content, re.IGNORECASE | re.DOTALL)
                form_analysis = {
                    'form_count': len(form_matches),
                    'forms_details': []
                }
                
                for form_content in form_matches:
                    action_match = re.search(r'action=["\']([^"\']*)["\']', form_content, re.IGNORECASE)
                    method_match = re.search(r'method=["\']([^"\']*)["\']', form_content, re.IGNORECASE)
                    
                    form_detail = {
                        'action': action_match.group(1) if action_match else '',
                        'method': method_match.group(1) if method_match else '',
                        'inputs': len(re.findall(r'<input[^>]*>', form_content, re.IGNORECASE)),
                        'buttons': len(re.findall(r'<button[^>]*>', form_content, re.IGNORECASE)),
                        'has_submit': bool(re.search(r'type=["\']submit["\']', form_content, re.IGNORECASE))
                    }
                    form_analysis['forms_details'].append(form_detail)
                
                analysis['form_analysis'] = form_analysis
                
            except Exception as e:
                analysis['dom_structure']['error'] = str(e)
            
            # 問題コンテンツの直接検索
            question_patterns = [
                r'問題\s*\d+',
                r'問\s*\d+',
                r'Question\s*\d+',
                r'[①②③④⑤⑥⑦⑧⑨⑩]',
                r'選択肢',
                r'答え',
                r'解答'
            ]
            
            question_content = {
                'pattern_matches': {},
                'visible_text_analysis': {},
                'potential_question_blocks': []
            }
            
            for pattern in question_patterns:
                matches = re.findall(pattern, html_content, re.IGNORECASE)
                question_content['pattern_matches'][pattern] = len(matches)
            
            # 見えるテキストの抽出
            try:
                # スクリプトとスタイルタグを除去
                clean_html = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.IGNORECASE | re.DOTALL)
                clean_html = re.sub(r'<style[^>]*>.*?</style>', '', clean_html, flags=re.IGNORECASE | re.DOTALL)
                
                # HTMLタグを除去してテキストのみ抽出
                visible_text = re.sub(r'<[^>]+>', ' ', clean_html)
                visible_text = re.sub(r'\s+', ' ', visible_text).strip()  # 空白の正規化
                
                question_content['visible_text_analysis'] = {
                    'total_visible_text_length': len(visible_text),
                    'visible_text_sample': visible_text[:1000],
                    'contains_japanese': bool(re.search(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]', visible_text)),
                    'question_keywords_found': []
                }
                
                # 問題関連キーワードの検索
                question_keywords = ['問題', '問', '選択', '回答', '解答', '次の', 'について', 'である', 'ものは']
                for keyword in question_keywords:
                    if keyword in visible_text:
                        question_content['visible_text_analysis']['question_keywords_found'].append(keyword)
                
            except Exception as e:
                question_content['visible_text_analysis']['error'] = str(e)
            
            analysis['question_content_analysis'] = question_content
            
            # 動的コンテンツの指標
            dynamic_indicators = []
            
            if js_analysis.get('ajax_indicators', 0) > 0:
                dynamic_indicators.append('Ajax呼び出しの存在')
            if js_analysis.get('fetch_indicators', 0) > 0:
                dynamic_indicators.append('Fetch API使用の存在')
            if js_analysis.get('dynamic_content_loading'):
                dynamic_indicators.append('動的コンテンツ読み込みの存在')
            if 'onload' in html_content.lower():
                dynamic_indicators.append('onloadイベントの存在')
            
            analysis['dynamic_indicators'] = dynamic_indicators
            
            # 抽出推奨手法
            recommendations = []
            
            if len(dynamic_indicators) > 0:
                recommendations.append('ヘッドレスブラウザ(Selenium/Playwright)の使用を推奨')
                recommendations.append('JavaScript実行後のDOM取得が必要')
            else:
                recommendations.append('静的HTML解析で十分')
                recommendations.append('BeautifulSoup + 正規表現で抽出可能')
            
            if question_content['visible_text_analysis'].get('contains_japanese'):
                recommendations.append('日本語文字エンコーディング対応必須')
            
            analysis['extraction_recommendations'] = recommendations
            
        except Exception as e:
            analysis['error'] = str(e)
        
        return analysis

    def save_html_samples(self, html_samples: Dict):
        """HTMLサンプルをファイルに保存"""
        
        for sample_name, sample_data in html_samples.items():
            if 'full_html' in sample_data:
                filename = f"production_html_sample_{sample_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
                
                try:
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(sample_data['full_html'])
                    print(f"  📄 HTMLサンプル保存: {filename}")
                except Exception as e:
                    print(f"  ❌ HTMLサンプル保存失敗 {sample_name}: {str(e)}")

    def run_comprehensive_html_analysis(self):
        """包括的HTML構造分析の実行"""
        
        print("🔥 本番環境HTML構造分析開始")
        print("=" * 80)
        print("目的: 問題内容抽出失敗原因の特定")
        print("対象: https://rccm-quiz-2025.onrender.com")
        print("=" * 80)
        
        start_time = time.time()
        
        # Step 1: HTMLサンプル取得
        html_samples = self.capture_html_samples()
        self.analysis_results['html_samples'] = html_samples
        
        # Step 2: 各サンプルの詳細分析
        extraction_methods = {}
        
        for sample_name, sample_data in html_samples.items():
            if 'full_html' in sample_data:
                print(f"\n🔬 {sample_name} 詳細分析")
                print("-" * 60)
                
                analysis = self.analyze_html_structure_deep(sample_data['full_html'], sample_name)
                extraction_methods[sample_name] = analysis
                
                # 重要な発見事項の表示
                if analysis.get('dynamic_indicators'):
                    print(f"  🚨 動的コンテンツ指標: {len(analysis['dynamic_indicators'])}件")
                    for indicator in analysis['dynamic_indicators']:
                        print(f"    • {indicator}")
                
                if analysis.get('extraction_recommendations'):
                    print(f"  💡 抽出推奨手法:")
                    for rec in analysis['extraction_recommendations']:
                        print(f"    • {rec}")
                
                question_analysis = analysis.get('question_content_analysis', {})
                visible_analysis = question_analysis.get('visible_text_analysis', {})
                if visible_analysis.get('question_keywords_found'):
                    print(f"  ✅ 問題関連キーワード発見: {visible_analysis['question_keywords_found']}")
                else:
                    print(f"  ❌ 問題関連キーワード未発見")
        
        self.analysis_results['extraction_methods_tested'] = extraction_methods
        
        # Step 3: HTMLサンプルをファイルに保存
        print(f"\n💾 HTMLサンプル保存")
        print("-" * 60)
        self.save_html_samples(html_samples)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Step 4: 総合判定と推奨手法
        self.generate_analysis_report(duration)
        
        return self.analysis_results

    def generate_analysis_report(self, duration: float):
        """分析レポート生成"""
        
        print("\n" + "=" * 80)
        print("🔥 本番環境HTML構造分析結果")
        print("=" * 80)
        
        extraction_methods = self.analysis_results['extraction_methods_tested']
        
        print(f"📊 分析統計:")
        print(f"  分析対象サンプル: {len(extraction_methods)}")
        print(f"  分析実行時間: {duration:.1f}秒")
        print()
        
        # 動的コンテンツの判定
        dynamic_content_found = False
        static_content_with_questions = False
        
        all_dynamic_indicators = []
        all_recommendations = []
        
        for sample_name, analysis in extraction_methods.items():
            dynamic_indicators = analysis.get('dynamic_indicators', [])
            if dynamic_indicators:
                dynamic_content_found = True
                all_dynamic_indicators.extend(dynamic_indicators)
            
            recommendations = analysis.get('extraction_recommendations', [])
            all_recommendations.extend(recommendations)
            
            question_analysis = analysis.get('question_content_analysis', {})
            visible_analysis = question_analysis.get('visible_text_analysis', {})
            if visible_analysis.get('question_keywords_found'):
                static_content_with_questions = True
        
        # 重要な発見事項
        critical_findings = []
        
        if dynamic_content_found:
            critical_findings.append("動的コンテンツの存在を確認")
            print("🚨 重要発見: 動的コンテンツが検出されました")
            print("  動的指標:")
            for indicator in set(all_dynamic_indicators):
                print(f"    • {indicator}")
        
        if not static_content_with_questions:
            critical_findings.append("静的HTMLに問題文が含まれていない")
            print("🚨 重要発見: 静的HTMLに問題文が確認できません")
        else:
            critical_findings.append("静的HTMLに問題関連コンテンツが存在")
            print("✅ 発見: 静的HTMLに問題関連コンテンツが存在します")
        
        self.analysis_results['critical_findings'] = critical_findings
        
        print()
        
        # 推奨アプローチ
        if dynamic_content_found:
            recommended_approach = "ヘッドレスブラウザ(Selenium/Playwright)による動的コンテンツ取得"
            print("💡 推奨アプローチ: ヘッドレスブラウザの使用")
            print("  理由: JavaScript実行による動的コンテンツ読み込みが必要")
        else:
            recommended_approach = "静的HTML解析(BeautifulSoup + 正規表現)"
            print("💡 推奨アプローチ: 静的HTML解析")
            print("  理由: 動的コンテンツが検出されていない")
        
        self.analysis_results['recommended_extraction_approach'] = recommended_approach
        
        print()
        
        # 最終判定
        if dynamic_content_found and not static_content_with_questions:
            print("🎯 結論: 問題内容は動的に読み込まれている可能性が高い")
            print("  対策: ヘッドレスブラウザによる実ブラウザシミュレーションが必要")
            credibility_status = "DYNAMIC_CONTENT_CONFIRMED"
        elif static_content_with_questions:
            print("🎯 結論: 問題内容は静的HTMLに含まれている")
            print("  対策: 抽出手法の改善により解決可能")
            credibility_status = "STATIC_CONTENT_CONFIRMED"
        else:
            print("🎯 結論: 追加調査が必要")
            print("  対策: より詳細な分析とテスト手法の検討")
            credibility_status = "NEEDS_FURTHER_INVESTIGATION"
        
        # 詳細レポート保存
        report_filename = f"production_html_structure_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(self.analysis_results, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 詳細分析レポート: {report_filename}")
        print("\n🔒 本番環境HTML構造分析完了")

def main():
    """メイン実行関数"""
    print("🔥 本番環境HTML構造分析")
    print("問題内容抽出失敗原因の特定")
    print()
    
    analyzer = ProductionHtmlStructureAnalysis()
    results = analyzer.run_comprehensive_html_analysis()
    
    return results

if __name__ == "__main__":
    main()