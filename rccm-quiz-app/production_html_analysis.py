#!/usr/bin/env python3
"""
Production環境のHTMLレスポンス分析スクリプト
"""
import requests
import json
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote
import time

def analyze_production_html():
    """Production環境のHTMLレスポンスを分析"""
    base_url = "https://rccm-quiz-2025.onrender.com"
    
    # セッションを開始
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })
    
    results = {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'analysis': {}
    }
    
    try:
        # 1. メインページにアクセス
        print("1. メインページにアクセス中...")
        main_response = session.get(base_url)
        print(f"   Status: {main_response.status_code}")
        
        # 2. 試験開始ページへのPOSTリクエスト
        category = "河川、砂防及び海岸・海洋"
        start_url = f"{base_url}/start_exam/{quote(category)}"
        
        print(f"2. 試験開始ページにPOSTリクエスト送信中...")
        print(f"   URL: {start_url}")
        
        post_data = {
            'questions': '5',
            'year': '2016'
        }
        
        start_response = session.post(start_url, data=post_data, allow_redirects=True)
        print(f"   Status: {start_response.status_code}")
        print(f"   Final URL: {start_response.url}")
        
        # HTMLを解析
        soup = BeautifulSoup(start_response.text, 'html.parser')
        
        # 3. HTMLの基本構造を分析
        results['analysis']['basic_info'] = {
            'status_code': start_response.status_code,
            'final_url': start_response.url,
            'title': soup.title.string if soup.title else None,
            'html_length': len(start_response.text)
        }
        
        # 4. 問題表示部分を特定
        print("3. 問題表示部分を分析中...")
        
        # 一般的な問題表示要素を探す
        question_elements = []
        
        # 問題文を含む可能性のある要素を探す
        potential_question_tags = [
            'div', 'p', 'span', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'section', 'article', 'main'
        ]
        
        for tag in potential_question_tags:
            elements = soup.find_all(tag)
            for elem in elements:
                text = elem.get_text(strip=True)
                if text and (
                    '問題' in text or 
                    '次の' in text or 
                    'について' in text or
                    '選択' in text or
                    '正しい' in text or
                    '適切' in text or
                    len(text) > 50  # 長めのテキストは問題文の可能性
                ):
                    question_elements.append({
                        'tag': tag,
                        'class': elem.get('class', []),
                        'id': elem.get('id', ''),
                        'text_preview': text[:100] + '...' if len(text) > 100 else text
                    })
        
        results['analysis']['question_elements'] = question_elements[:10]  # 上位10件
        
        # 5. フォーム要素を分析
        print("4. フォーム要素を分析中...")
        forms = soup.find_all('form')
        form_info = []
        
        for form in forms:
            inputs = form.find_all(['input', 'select', 'textarea'])
            form_info.append({
                'action': form.get('action', ''),
                'method': form.get('method', ''),
                'inputs': [
                    {
                        'type': inp.get('type', ''),
                        'name': inp.get('name', ''),
                        'value': inp.get('value', ''),
                        'id': inp.get('id', '')
                    } for inp in inputs
                ]
            })
        
        results['analysis']['forms'] = form_info
        
        # 6. 選択肢を分析
        print("5. 選択肢を分析中...")
        radio_inputs = soup.find_all('input', {'type': 'radio'})
        checkbox_inputs = soup.find_all('input', {'type': 'checkbox'})
        
        results['analysis']['choices'] = {
            'radio_count': len(radio_inputs),
            'checkbox_count': len(checkbox_inputs),
            'radio_names': list(set([r.get('name', '') for r in radio_inputs if r.get('name')])),
            'checkbox_names': list(set([c.get('name', '') for c in checkbox_inputs if c.get('name')]))
        }
        
        # 7. 特定のクラスやIDを持つ要素を分析
        print("6. 特定のクラス/ID要素を分析中...")
        special_elements = {}
        
        # よく使われるクラス名/ID名
        target_identifiers = [
            'question', 'problem', 'quiz', 'exam', 'choice', 'answer',
            'option', 'selection', 'content', 'main', 'container'
        ]
        
        for identifier in target_identifiers:
            # クラス名で検索
            by_class = soup.find_all(class_=re.compile(identifier, re.I))
            # ID名で検索
            by_id = soup.find_all(id=re.compile(identifier, re.I))
            
            if by_class or by_id:
                special_elements[identifier] = {
                    'by_class_count': len(by_class),
                    'by_id_count': len(by_id),
                    'sample_class': by_class[0].get('class', []) if by_class else [],
                    'sample_id': by_id[0].get('id', '') if by_id else ''
                }
        
        results['analysis']['special_elements'] = special_elements
        
        # 8. HTMLの生サンプルを保存
        print("7. HTMLサンプルを保存中...")
        sample_html = start_response.text[:5000]  # 最初の5000文字
        results['analysis']['html_sample'] = sample_html
        
        # 9. エラーメッセージをチェック
        error_indicators = ['error', 'Error', 'ERROR', '405', '404', '500', 'not found', 'forbidden']
        has_error = any(indicator in start_response.text for indicator in error_indicators)
        results['analysis']['has_error'] = has_error
        
        if has_error:
            print("   ⚠️  エラーの可能性が検出されました")
        
        print("8. 分析完了")
        
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
        results['analysis']['error'] = str(e)
    
    return results

if __name__ == "__main__":
    results = analyze_production_html()
    
    # 結果を保存
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    filename = f"production_html_analysis_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n分析結果を {filename} に保存しました")
    
    # 重要な結果を表示
    print("\n=== 分析結果サマリー ===")
    if 'basic_info' in results['analysis']:
        info = results['analysis']['basic_info']
        print(f"ステータスコード: {info['status_code']}")
        print(f"最終URL: {info['final_url']}")
        print(f"タイトル: {info['title']}")
        print(f"HTML長: {info['html_length']} 文字")
    
    if 'question_elements' in results['analysis']:
        print(f"\n問題要素候補: {len(results['analysis']['question_elements'])} 件")
        for i, elem in enumerate(results['analysis']['question_elements'][:3]):
            print(f"  {i+1}. {elem['tag']} (class: {elem['class']}) - {elem['text_preview']}")
    
    if 'choices' in results['analysis']:
        choices = results['analysis']['choices']
        print(f"\n選択肢: ラジオボタン {choices['radio_count']} 個, チェックボックス {choices['checkbox_count']} 個")
        if choices['radio_names']:
            print(f"ラジオボタン名: {choices['radio_names']}")