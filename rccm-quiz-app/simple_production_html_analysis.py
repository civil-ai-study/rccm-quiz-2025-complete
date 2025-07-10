#!/usr/bin/env python3
"""
Production環境のHTMLレスポンス分析スクリプト（簡易版）
"""
import urllib.request
import urllib.parse
import json
import time
import re

def analyze_production_html():
    """Production環境のHTMLレスポンスを分析"""
    base_url = "https://rccm-quiz-2025.onrender.com"
    
    results = {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'analysis': {}
    }
    
    try:
        # POSTデータを準備
        category = "河川、砂防及び海岸・海洋"
        start_url = f"{base_url}/start_exam/{urllib.parse.quote(category)}"
        
        post_data = urllib.parse.urlencode({
            'questions': '5',
            'year': '2016'
        }).encode('utf-8')
        
        # リクエストヘッダを設定
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        print(f"POSTリクエストを送信中: {start_url}")
        
        # POSTリクエストを送信
        request = urllib.request.Request(start_url, data=post_data, headers=headers)
        
        try:
            response = urllib.request.urlopen(request)
            html_content = response.read().decode('utf-8')
            status_code = response.getcode()
            final_url = response.geturl()
            
            print(f"ステータスコード: {status_code}")
            print(f"最終URL: {final_url}")
            
        except urllib.error.HTTPError as e:
            print(f"HTTPエラー: {e.code}")
            html_content = e.read().decode('utf-8')
            status_code = e.code
            final_url = start_url
        
        # 基本情報を記録
        results['analysis']['basic_info'] = {
            'status_code': status_code,
            'final_url': final_url,
            'html_length': len(html_content)
        }
        
        # HTMLの構造を分析
        print("HTMLの構造を分析中...")
        
        # タイトルを抽出
        title_match = re.search(r'<title[^>]*>(.*?)</title>', html_content, re.IGNORECASE | re.DOTALL)
        title = title_match.group(1).strip() if title_match else None
        results['analysis']['basic_info']['title'] = title
        
        # 問題文らしき要素を探す
        question_patterns = [
            r'問題\s*\d+',
            r'次の.*?について',
            r'適切.*?選択',
            r'正しい.*?選択',
            r'<p[^>]*>([^<]{50,})</p>',  # 長めのp要素
            r'<div[^>]*>([^<]{50,})</div>'  # 長めのdiv要素
        ]
        
        question_candidates = []
        for pattern in question_patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE | re.DOTALL)
            for match in matches:
                clean_match = re.sub(r'<[^>]+>', '', match).strip()
                if clean_match and len(clean_match) > 10:
                    question_candidates.append({
                        'pattern': pattern,
                        'text': clean_match[:200] + '...' if len(clean_match) > 200 else clean_match
                    })
        
        results['analysis']['question_candidates'] = question_candidates[:10]
        
        # フォーム要素を分析
        form_matches = re.findall(r'<form[^>]*>.*?</form>', html_content, re.IGNORECASE | re.DOTALL)
        forms_info = []
        
        for form_html in form_matches:
            action_match = re.search(r'action\s*=\s*["\']([^"\']*)["\']', form_html, re.IGNORECASE)
            method_match = re.search(r'method\s*=\s*["\']([^"\']*)["\']', form_html, re.IGNORECASE)
            
            input_matches = re.findall(r'<input[^>]*>', form_html, re.IGNORECASE)
            inputs_info = []
            
            for input_html in input_matches:
                type_match = re.search(r'type\s*=\s*["\']([^"\']*)["\']', input_html, re.IGNORECASE)
                name_match = re.search(r'name\s*=\s*["\']([^"\']*)["\']', input_html, re.IGNORECASE)
                value_match = re.search(r'value\s*=\s*["\']([^"\']*)["\']', input_html, re.IGNORECASE)
                
                inputs_info.append({
                    'type': type_match.group(1) if type_match else '',
                    'name': name_match.group(1) if name_match else '',
                    'value': value_match.group(1) if value_match else ''
                })
            
            forms_info.append({
                'action': action_match.group(1) if action_match else '',
                'method': method_match.group(1) if method_match else '',
                'inputs': inputs_info
            })
        
        results['analysis']['forms'] = forms_info
        
        # 選択肢（ラジオボタン、チェックボックス）を分析
        radio_matches = re.findall(r'<input[^>]*type\s*=\s*["\']radio["\'][^>]*>', html_content, re.IGNORECASE)
        checkbox_matches = re.findall(r'<input[^>]*type\s*=\s*["\']checkbox["\'][^>]*>', html_content, re.IGNORECASE)
        
        radio_names = []
        for radio in radio_matches:
            name_match = re.search(r'name\s*=\s*["\']([^"\']*)["\']', radio, re.IGNORECASE)
            if name_match:
                radio_names.append(name_match.group(1))
        
        results['analysis']['choices'] = {
            'radio_count': len(radio_matches),
            'checkbox_count': len(checkbox_matches),
            'radio_names': list(set(radio_names))
        }
        
        # エラーの検出
        error_patterns = [
            r'405\s*Method\s*Not\s*Allowed',
            r'404\s*Not\s*Found',
            r'500\s*Internal\s*Server\s*Error',
            r'Redirecting\.\.\.',
            r'Error',
            r'エラー'
        ]
        
        detected_errors = []
        for pattern in error_patterns:
            if re.search(pattern, html_content, re.IGNORECASE):
                detected_errors.append(pattern)
        
        results['analysis']['errors'] = detected_errors
        
        # HTMLサンプルを保存
        results['analysis']['html_sample'] = html_content[:2000]
        
        # より詳細なHTML構造分析
        # 特定のクラス名やIDを持つ要素を探す
        class_id_patterns = [
            r'class\s*=\s*["\']([^"\']*question[^"\']*)["\']',
            r'class\s*=\s*["\']([^"\']*problem[^"\']*)["\']',
            r'class\s*=\s*["\']([^"\']*quiz[^"\']*)["\']',
            r'class\s*=\s*["\']([^"\']*exam[^"\']*)["\']',
            r'id\s*=\s*["\']([^"\']*question[^"\']*)["\']',
            r'id\s*=\s*["\']([^"\']*problem[^"\']*)["\']'
        ]
        
        special_elements = []
        for pattern in class_id_patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            special_elements.extend(matches)
        
        results['analysis']['special_elements'] = list(set(special_elements))
        
        print("分析完了")
        
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
        results['analysis']['error'] = str(e)
    
    return results

if __name__ == "__main__":
    results = analyze_production_html()
    
    # 結果を保存
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    filename = f"simple_production_html_analysis_{timestamp}.json"
    
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
    
    if 'question_candidates' in results['analysis']:
        print(f"\n問題候補: {len(results['analysis']['question_candidates'])} 件")
        for i, candidate in enumerate(results['analysis']['question_candidates'][:3]):
            print(f"  {i+1}. {candidate['text']}")
    
    if 'choices' in results['analysis']:
        choices = results['analysis']['choices']
        print(f"\n選択肢: ラジオボタン {choices['radio_count']} 個, チェックボックス {choices['checkbox_count']} 個")
        if choices['radio_names']:
            print(f"ラジオボタン名: {choices['radio_names']}")
    
    if 'errors' in results['analysis'] and results['analysis']['errors']:
        print(f"\n検出されたエラー: {results['analysis']['errors']}")
    
    if 'html_sample' in results['analysis']:
        print(f"\nHTMLサンプル（最初の500文字）:")
        print(results['analysis']['html_sample'][:500])