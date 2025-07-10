#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔥 本番環境コンテンツエンコーディング分析
バイナリデータで返される問題の原因調査

発見された問題:
- HTMLファイルがバイナリデータとして保存されている
- 文字エンコーディングの問題でテキストが読めない
- gzip圧縮またはその他の圧縮が影響している可能性

対策アプローチ:
1. レスポンスヘッダーの詳細分析
2. Content-Encodingの確認
3. 適切なデコード手法の特定
"""

import requests
import json
import time
from datetime import datetime
import re
import gzip
import zlib
import base64
from typing import Dict, List, Optional, Tuple
import logging

# ログ設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ProductionContentEncodingAnalysis:
    def __init__(self):
        self.base_url = "https://rccm-quiz-2025.onrender.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ja-JP,ja;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',  # 明示的に圧縮を受け入れ
            'Connection': 'keep-alive',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        })
        
        # 分析結果
        self.analysis_results = {
            'timestamp': datetime.now().isoformat(),
            'analysis_type': 'PRODUCTION_CONTENT_ENCODING_ANALYSIS',
            'target_url': self.base_url,
            'encoding_tests': {},
            'decoding_attempts': {},
            'successful_extractions': [],
            'critical_findings': []
        }

    def analyze_response_encoding(self, response: requests.Response, test_name: str) -> Dict:
        """レスポンスエンコーディングの詳細分析"""
        
        print(f"🔬 {test_name} エンコーディング分析")
        
        encoding_analysis = {
            'test_name': test_name,
            'status_code': response.status_code,
            'headers': dict(response.headers),
            'encoding_detected': response.encoding,
            'content_length': len(response.content),
            'text_length': len(response.text),
            'is_binary': False,
            'compression_detected': None,
            'charset_from_headers': None,
            'decoding_attempts': []
        }
        
        # ヘッダーからの情報抽出
        content_type = response.headers.get('content-type', '')
        content_encoding = response.headers.get('content-encoding', '')
        
        encoding_analysis['charset_from_headers'] = content_type
        encoding_analysis['compression_detected'] = content_encoding
        
        print(f"  📊 基本情報:")
        print(f"    Status: {response.status_code}")
        print(f"    Content-Type: {content_type}")
        print(f"    Content-Encoding: {content_encoding}")
        print(f"    Content-Length: {len(response.content)} bytes")
        print(f"    Response Encoding: {response.encoding}")
        
        # バイナリ判定
        try:
            response.content.decode('utf-8')
            encoding_analysis['is_binary'] = False
        except UnicodeDecodeError:
            encoding_analysis['is_binary'] = True
            print(f"  🚨 バイナリデータ検出")
        
        # 様々なデコード試行
        decoding_methods = [
            ('utf-8', lambda x: x.decode('utf-8')),
            ('shift_jis', lambda x: x.decode('shift_jis')),
            ('euc-jp', lambda x: x.decode('euc-jp')),
            ('iso-2022-jp', lambda x: x.decode('iso-2022-jp')),
            ('gzip+utf-8', lambda x: gzip.decompress(x).decode('utf-8')),
            ('deflate+utf-8', lambda x: zlib.decompress(x).decode('utf-8')),
            ('latin1+utf-8', lambda x: x.decode('latin1').encode('latin1').decode('utf-8'))
        ]
        
        for method_name, decode_func in decoding_methods:
            try:
                decoded_content = decode_func(response.content)
                
                # 日本語文字の存在確認
                japanese_found = bool(re.search(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]', decoded_content))
                
                # 問題関連キーワードの確認
                question_keywords = ['問題', '問', '選択', '回答', '解答', 'Question']
                keywords_found = [kw for kw in question_keywords if kw in decoded_content]
                
                decoding_result = {
                    'method': method_name,
                    'success': True,
                    'decoded_length': len(decoded_content),
                    'japanese_detected': japanese_found,
                    'question_keywords_found': keywords_found,
                    'sample_text': decoded_content[:500] if decoded_content else '',
                    'html_tags_found': bool(re.search(r'<[^>]+>', decoded_content))
                }
                
                encoding_analysis['decoding_attempts'].append(decoding_result)
                
                if keywords_found or japanese_found:
                    print(f"  ✅ {method_name} 成功: 日本語={japanese_found}, キーワード={len(keywords_found)}個")
                    if keywords_found:
                        print(f"    発見キーワード: {keywords_found}")
                else:
                    print(f"  ⚠️ {method_name} 部分成功: 内容確認必要")
                
            except Exception as e:
                decoding_result = {
                    'method': method_name,
                    'success': False,
                    'error': str(e)
                }
                encoding_analysis['decoding_attempts'].append(decoding_result)
                print(f"  ❌ {method_name} 失敗: {str(e)}")
        
        return encoding_analysis

    def test_different_request_methods(self) -> Dict:
        """異なるリクエスト方法でのテスト"""
        
        print("🧪 複数リクエスト方法テスト")
        print("=" * 60)
        
        tests = {}
        
        # テスト1: Accept-Encodingなし
        print("📍 Test 1: Accept-Encodingヘッダーなし")
        session_no_encoding = requests.Session()
        session_no_encoding.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ja-JP,ja;q=0.9,en;q=0.8'
            # Accept-Encodingを意図的に除外
        })
        
        try:
            specialist_data = {
                'questions': '10',
                'category': '建設環境',
                'year': '2019'
            }
            
            response1 = session_no_encoding.post(
                f"{self.base_url}/start_exam/specialist", 
                data=specialist_data, 
                timeout=30, 
                allow_redirects=True
            )
            
            tests['no_compression'] = self.analyze_response_encoding(response1, "圧縮なしリクエスト")
            
        except Exception as e:
            tests['no_compression'] = {'error': str(e)}
            print(f"  💥 圧縮なしリクエスト失敗: {str(e)}")
        
        time.sleep(2)
        
        # テスト2: 明示的にidentity要求
        print("\n📍 Test 2: identity encoding明示")
        session_identity = requests.Session()
        session_identity.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ja-JP,ja;q=0.9,en;q=0.8',
            'Accept-Encoding': 'identity'  # 圧縮なしを明示
        })
        
        try:
            response2 = session_identity.post(
                f"{self.base_url}/start_exam/specialist", 
                data=specialist_data, 
                timeout=30, 
                allow_redirects=True
            )
            
            tests['identity_encoding'] = self.analyze_response_encoding(response2, "identity encoding")
            
        except Exception as e:
            tests['identity_encoding'] = {'error': str(e)}
            print(f"  💥 identity encodingリクエスト失敗: {str(e)}")
        
        time.sleep(2)
        
        # テスト3: gzipのみ
        print("\n📍 Test 3: gzip圧縮のみ")
        session_gzip = requests.Session()
        session_gzip.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ja-JP,ja;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip'  # gzipのみ
        })
        
        try:
            response3 = session_gzip.post(
                f"{self.base_url}/start_exam/specialist", 
                data=specialist_data, 
                timeout=30, 
                allow_redirects=True
            )
            
            tests['gzip_only'] = self.analyze_response_encoding(response3, "gzip圧縮のみ")
            
        except Exception as e:
            tests['gzip_only'] = {'error': str(e)}
            print(f"  💥 gzip圧縮のみリクエスト失敗: {str(e)}")
        
        time.sleep(2)
        
        # テスト4: 基礎科目での比較
        print("\n📍 Test 4: 基礎科目での比較")
        try:
            basic_data = {'questions': '10'}
            
            response4 = self.session.post(
                f"{self.base_url}/start_exam/basic", 
                data=basic_data, 
                timeout=30, 
                allow_redirects=True
            )
            
            tests['basic_exam'] = self.analyze_response_encoding(response4, "基礎科目試験")
            
        except Exception as e:
            tests['basic_exam'] = {'error': str(e)}
            print(f"  💥 基礎科目試験失敗: {str(e)}")
        
        return tests

    def extract_successful_content(self, tests: Dict) -> List[Dict]:
        """成功したデコードからコンテンツを抽出"""
        
        print("\n🎯 成功したデコード結果からコンテンツ抽出")
        print("=" * 60)
        
        successful_extractions = []
        
        for test_name, test_result in tests.items():
            if 'decoding_attempts' not in test_result:
                continue
            
            for attempt in test_result['decoding_attempts']:
                if (attempt.get('success') and 
                    (attempt.get('question_keywords_found') or attempt.get('japanese_detected'))):
                    
                    print(f"✅ {test_name} - {attempt['method']} で成功")
                    
                    decoded_text = attempt.get('sample_text', '')
                    
                    # 問題文パターンの詳細検索
                    question_patterns = [
                        r'問題\s*(\d+)\s*[:：.．]\s*([^問]{50,500})',
                        r'問\s*(\d+)\s*[:：.．]\s*([^問]{50,500})',
                        r'(\d+)\s*[:：.．]\s*([^0-9]{50,500})',
                        r'Question\s*(\d+)\s*[:：.．]\s*([^Q]{50,500})'
                    ]
                    
                    questions_found = []
                    for pattern in question_patterns:
                        matches = re.findall(pattern, decoded_text, re.DOTALL)
                        for match in matches:
                            questions_found.append({
                                'number': match[0],
                                'content': match[1].strip()[:200],
                                'pattern': pattern
                            })
                    
                    # 選択肢パターンの検索
                    choice_patterns = [
                        r'[①②③④⑤]([^①②③④⑤]{10,100})',
                        r'[１２３４５]\.([^１２３４５]{10,100})',
                        r'[ア-オ]\.([^ア-オ]{10,100})'
                    ]
                    
                    choices_found = []
                    for pattern in choice_patterns:
                        matches = re.findall(pattern, decoded_text)
                        choices_found.extend([choice.strip() for choice in matches if len(choice.strip()) > 5])
                    
                    extraction_result = {
                        'test_name': test_name,
                        'decoding_method': attempt['method'],
                        'questions_extracted': questions_found,
                        'choices_extracted': choices_found[:10],  # 最初の10個
                        'japanese_content_confirmed': attempt.get('japanese_detected', False),
                        'html_structure_confirmed': attempt.get('html_tags_found', False),
                        'extraction_confidence': 'HIGH' if questions_found else 'MEDIUM' if choices_found else 'LOW'
                    }
                    
                    successful_extractions.append(extraction_result)
                    
                    print(f"  📝 問題抽出: {len(questions_found)}個")
                    print(f"  📝 選択肢抽出: {len(choices_found)}個")
                    print(f"  📊 信頼度: {extraction_result['extraction_confidence']}")
                    
                    if questions_found:
                        print(f"  📄 問題例: {questions_found[0]['content'][:100]}...")
        
        return successful_extractions

    def run_comprehensive_encoding_analysis(self):
        """包括的エンコーディング分析の実行"""
        
        print("🔥 本番環境コンテンツエンコーディング分析開始")
        print("=" * 80)
        print("目的: バイナリデータで返される問題の原因調査")
        print("対象: https://rccm-quiz-2025.onrender.com")
        print("=" * 80)
        
        start_time = time.time()
        
        # Step 1: 複数リクエスト方法でのテスト
        encoding_tests = self.test_different_request_methods()
        self.analysis_results['encoding_tests'] = encoding_tests
        
        # Step 2: 成功したデコード結果からコンテンツ抽出
        successful_extractions = self.extract_successful_content(encoding_tests)
        self.analysis_results['successful_extractions'] = successful_extractions
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Step 3: 結果分析と推奨手法の特定
        self.generate_encoding_analysis_report(duration)
        
        return self.analysis_results

    def generate_encoding_analysis_report(self, duration: float):
        """エンコーディング分析レポート生成"""
        
        print("\n" + "=" * 80)
        print("🔥 本番環境コンテンツエンコーディング分析結果")
        print("=" * 80)
        
        encoding_tests = self.analysis_results['encoding_tests']
        successful_extractions = self.analysis_results['successful_extractions']
        
        print(f"📊 分析統計:")
        print(f"  実行テスト数: {len(encoding_tests)}")
        print(f"  成功デコード数: {len(successful_extractions)}")
        print(f"  分析実行時間: {duration:.1f}秒")
        print()
        
        # 重要な発見事項
        critical_findings = []
        
        # デコード成功率
        total_attempts = 0
        successful_attempts = 0
        
        for test_name, test_result in encoding_tests.items():
            if 'decoding_attempts' in test_result:
                total_attempts += len(test_result['decoding_attempts'])
                successful_attempts += sum(1 for attempt in test_result['decoding_attempts'] if attempt.get('success'))
        
        success_rate = (successful_attempts / total_attempts) * 100 if total_attempts > 0 else 0
        
        print(f"🎯 デコード成功率: {success_rate:.1f}% ({successful_attempts}/{total_attempts})")
        print()
        
        # 最適なデコード手法の特定
        decoding_methods_success = {}
        
        for extraction in successful_extractions:
            method = extraction['decoding_method']
            confidence = extraction['extraction_confidence']
            
            if method not in decoding_methods_success:
                decoding_methods_success[method] = {
                    'count': 0,
                    'high_confidence': 0,
                    'questions_found': 0
                }
            
            decoding_methods_success[method]['count'] += 1
            if confidence == 'HIGH':
                decoding_methods_success[method]['high_confidence'] += 1
            decoding_methods_success[method]['questions_found'] += len(extraction['questions_extracted'])
        
        if decoding_methods_success:
            print("🏆 最適デコード手法:")
            
            # 成功率でソート
            sorted_methods = sorted(
                decoding_methods_success.items(), 
                key=lambda x: (x[1]['high_confidence'], x[1]['questions_found']), 
                reverse=True
            )
            
            best_method = sorted_methods[0][0] if sorted_methods else None
            
            for method, stats in sorted_methods:
                status = "🥇" if method == best_method else "🥈" if stats['high_confidence'] > 0 else "🥉"
                print(f"  {status} {method}: 成功{stats['count']}回, 高信頼{stats['high_confidence']}回, 問題{stats['questions_found']}個")
            
            critical_findings.append(f"最適デコード手法: {best_method}")
            
            # 推奨アプローチ
            if best_method:
                if 'gzip' in best_method:
                    recommended_approach = "gzip圧縮解除 + UTF-8デコード"
                    critical_findings.append("gzip圧縮が原因")
                elif 'deflate' in best_method:
                    recommended_approach = "deflate圧縮解除 + UTF-8デコード"
                    critical_findings.append("deflate圧縮が原因")
                elif 'latin1' in best_method:
                    recommended_approach = "文字エンコーディング変換(latin1→utf-8)"
                    critical_findings.append("文字エンコーディング問題が原因")
                else:
                    recommended_approach = f"{best_method}による直接デコード"
                    critical_findings.append("標準的なエンコーディング問題")
                
                print(f"\n💡 推奨アプローチ: {recommended_approach}")
        else:
            print("❌ 成功したデコード手法なし")
            critical_findings.append("全てのデコード手法が失敗")
            recommended_approach = "ヘッドレスブラウザでの動的取得を検討"
        
        # 問題内容の確認
        total_questions = sum(len(ext['questions_extracted']) for ext in successful_extractions)
        total_choices = sum(len(ext['choices_extracted']) for ext in successful_extractions)
        
        if total_questions > 0:
            print(f"\n📝 問題内容確認:")
            print(f"  抽出問題数: {total_questions}個")
            print(f"  抽出選択肢数: {total_choices}個")
            critical_findings.append(f"問題内容抽出成功: {total_questions}問")
            
            # 問題サンプル表示
            for extraction in successful_extractions[:2]:  # 最初の2つ
                if extraction['questions_extracted']:
                    question = extraction['questions_extracted'][0]
                    print(f"  📄 問題例({extraction['decoding_method']}): {question['content'][:150]}...")
        else:
            print(f"\n❌ 問題内容が抽出できませんでした")
            critical_findings.append("問題内容抽出失敗")
        
        self.analysis_results['critical_findings'] = critical_findings
        
        print()
        
        # 最終判定
        if total_questions > 0:
            print("🏆 結論: エンコーディング問題が特定され、解決可能")
            print(f"  対策: {recommended_approach}を実装")
            credibility_status = "ENCODING_PROBLEM_SOLVED"
        elif successful_extractions:
            print("⚠️ 結論: 部分的な成功、さらなる調整が必要")
            print("  対策: デコード手法の最適化が必要")
            credibility_status = "PARTIAL_SUCCESS"
        else:
            print("🚨 結論: エンコーディング問題が深刻、代替手法が必要")
            print("  対策: ヘッドレスブラウザによる動的取得を検討")
            credibility_status = "ENCODING_PROBLEM_CRITICAL"
        
        # 詳細レポート保存
        report_filename = f"production_content_encoding_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(self.analysis_results, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 詳細エンコーディング分析レポート: {report_filename}")
        print("\n🔒 本番環境コンテンツエンコーディング分析完了")

def main():
    """メイン実行関数"""
    print("🔥 本番環境コンテンツエンコーディング分析")
    print("バイナリデータ問題の原因調査と解決策の特定")
    print()
    
    analyzer = ProductionContentEncodingAnalysis()
    results = analyzer.run_comprehensive_encoding_analysis()
    
    return results

if __name__ == "__main__":
    main()