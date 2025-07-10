#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 本番環境API直接検証スクリプト
実際の問題取得APIを直接呼び出して混在を確認
"""

import requests
import json
from datetime import datetime
import time

class ProductionAPIVerification:
    def __init__(self):
        self.base_url = "https://rccm-quiz-2025.onrender.com"
        self.session = requests.Session()
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'verification_type': 'PRODUCTION_API_VERIFICATION',
            'tests': []
        }
    
    def start_exam_session(self, exam_type, category=None, year=None):
        """試験セッションを開始"""
        print(f"\n🚀 試験開始: {exam_type}, カテゴリー: {category}, 年度: {year}")
        
        # POSTデータの準備
        data = {
            'questions': '10',  # 10問
        }
        
        if category:
            data['category'] = category
        if year:
            data['year'] = str(year)
        
        # URLの構築
        if exam_type == 'basic':
            url = f"{self.base_url}/start_exam/basic"
        elif exam_type == 'specialist' and category:
            # 部門名をURLエンコード
            url = f"{self.base_url}/start_exam/specialist"
        else:
            url = f"{self.base_url}/start_exam/{exam_type}"
        
        try:
            # POSTリクエストで試験開始
            response = self.session.post(url, data=data, allow_redirects=False)
            
            if response.status_code == 302:  # リダイレクト
                print(f"✅ 試験開始成功 - リダイレクト先: {response.headers.get('Location')}")
                
                # リダイレクト先にアクセス
                redirect_url = response.headers.get('Location')
                if redirect_url:
                    if not redirect_url.startswith('http'):
                        redirect_url = self.base_url + redirect_url
                    
                    exam_response = self.session.get(redirect_url)
                    if exam_response.status_code == 200:
                        return self.extract_question_data(exam_response.text)
            else:
                print(f"❌ 試験開始失敗: ステータス {response.status_code}")
                
        except Exception as e:
            print(f"❌ エラー: {e}")
        
        return None
    
    def extract_question_data(self, html_content):
        """HTMLから問題データを抽出"""
        import re
        
        # 問題文パターン
        question_patterns = [
            r'<div[^>]*class="[^"]*question-text[^"]*"[^>]*>(.*?)</div>',
            r'<p[^>]*class="[^"]*question[^"]*"[^>]*>(.*?)</p>',
            r'id="question"[^>]*>(.*?)<',
            r'問題[：:]\s*(.*?)<',
            r'<div[^>]*>問\d+[：:]\s*(.*?)</div>'
        ]
        
        # カテゴリー/種別パターン
        category_patterns = [
            r'カテゴリー[：:]\s*([^<\n]+)',
            r'部門[：:]\s*([^<\n]+)',
            r'科目[：:]\s*([^<\n]+)',
            r'分野[：:]\s*([^<\n]+)'
        ]
        
        # 年度パターン
        year_patterns = [
            r'(\d{4})年度',
            r'年度[：:]\s*(\d{4})',
            r'(\d{4})年'
        ]
        
        extracted_data = {
            'questions': [],
            'categories': [],
            'years': [],
            'raw_text_sample': html_content[:1000]
        }
        
        # 問題文抽出
        for pattern in question_patterns:
            matches = re.findall(pattern, html_content, re.DOTALL)
            for match in matches:
                clean_text = re.sub(r'<[^>]+>', '', match).strip()
                if clean_text and len(clean_text) > 10:
                    extracted_data['questions'].append(clean_text[:200])
        
        # カテゴリー抽出
        for pattern in category_patterns:
            matches = re.findall(pattern, html_content)
            extracted_data['categories'].extend(matches)
        
        # 年度抽出
        for pattern in year_patterns:
            matches = re.findall(pattern, html_content)
            extracted_data['years'].extend(matches)
        
        return extracted_data
    
    def analyze_exam_api(self):
        """試験APIのエンドポイントを分析"""
        print("\n🔍 試験APIエンドポイント分析")
        
        # JavaScriptファイルからAPIエンドポイントを探す
        js_urls = [
            f"{self.base_url}/static/js/main.js",
            f"{self.base_url}/static/js/exam.js",
            f"{self.base_url}/static/js/quiz.js"
        ]
        
        api_endpoints = []
        
        for js_url in js_urls:
            try:
                response = self.session.get(js_url)
                if response.status_code == 200:
                    # APIエンドポイントパターンを検索
                    import re
                    patterns = [
                        r'["\']/(api/[^"\']+)["\']',
                        r'["\']/(exam/[^"\']+)["\']',
                        r'["\']/(quiz/[^"\']+)["\']',
                        r'fetch\(["\']([^"\']+)["\']',
                        r'axios\.[a-z]+\(["\']([^"\']+)["\']'
                    ]
                    
                    for pattern in patterns:
                        matches = re.findall(pattern, response.text)
                        api_endpoints.extend(matches)
                        
            except Exception as e:
                print(f"  ❌ {js_url}: {e}")
        
        # 重複を除去
        api_endpoints = list(set(api_endpoints))
        
        if api_endpoints:
            print(f"  ✅ 発見されたAPIエンドポイント:")
            for endpoint in api_endpoints[:10]:  # 最初の10個
                print(f"    - {endpoint}")
        
        return api_endpoints
    
    def test_specific_scenario(self, test_name, exam_type, category, year, expected_type):
        """特定のシナリオをテスト"""
        print(f"\n📋 テスト: {test_name}")
        
        result = {
            'test_name': test_name,
            'exam_type': exam_type,
            'category': category,
            'year': year,
            'expected_type': expected_type,
            'success': False,
            'data': None
        }
        
        # 試験開始
        data = self.start_exam_session(exam_type, category, year)
        
        if data:
            result['data'] = data
            result['success'] = True
            
            print(f"  📊 抽出結果:")
            if data['questions']:
                print(f"    - 問題数: {len(data['questions'])}")
                print(f"    - 最初の問題: {data['questions'][0][:100]}...")
            if data['categories']:
                print(f"    - カテゴリー: {', '.join(set(data['categories']))}")
            if data['years']:
                print(f"    - 年度: {', '.join(set(data['years']))}")
        else:
            print("  ❌ データ取得失敗")
        
        self.results['tests'].append(result)
        
        # レート制限回避
        time.sleep(2)
        
        return result
    
    def run_verification(self):
        """本番環境での検証実行"""
        print("="*60)
        print("🔍 本番環境API直接検証")
        print("="*60)
        
        # APIエンドポイント分析
        self.analyze_exam_api()
        
        # テストケース実行
        test_cases = [
            # ユーザー報告のケース
            {
                'name': '土質・基礎2016年専門科目（ユーザー報告）',
                'exam_type': 'specialist',
                'category': 'soil_foundation',
                'year': '2016',
                'expected': 'specialist'
            },
            # 基礎科目テスト
            {
                'name': '基礎科目（4-1）',
                'exam_type': 'basic',
                'category': None,
                'year': None,
                'expected': 'basic'
            },
            # 他の専門科目テスト
            {
                'name': '道路部門2019年専門科目',
                'exam_type': 'specialist',
                'category': 'road',
                'year': '2019',
                'expected': 'specialist'
            }
        ]
        
        for test in test_cases:
            self.test_specific_scenario(
                test['name'],
                test['exam_type'],
                test['category'],
                test['year'],
                test['expected']
            )
        
        # レポート生成
        self.generate_report()
    
    def generate_report(self):
        """検証レポート生成"""
        print("\n" + "="*60)
        print("📊 本番環境検証レポート")
        print("="*60)
        
        success_count = sum(1 for t in self.results['tests'] if t['success'])
        total_count = len(self.results['tests'])
        
        print(f"\nテスト結果: {success_count}/{total_count} 成功")
        
        # 詳細結果
        for test in self.results['tests']:
            print(f"\n{test['test_name']}:")
            if test['success'] and test['data']:
                if test['data']['questions']:
                    print(f"  ✅ {len(test['data']['questions'])}個の問題を抽出")
                else:
                    print(f"  ⚠️ 問題を抽出できませんでした")
            else:
                print(f"  ❌ テスト失敗")
        
        # JSONファイルに保存
        filename = f"production_api_verification_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        print(f"\n📄 詳細レポート保存: {filename}")

def main():
    verifier = ProductionAPIVerification()
    verifier.run_verification()

if __name__ == "__main__":
    main()