#!/usr/bin/env python3
"""
Production環境でセッションを正しく作成してからHTMLレスポンスを分析
"""
import urllib.request
import urllib.parse
import json
import time
import re
import http.cookiejar

def analyze_production_html_with_session():
    """Production環境でセッションを維持しながらHTMLレスポンスを分析"""
    base_url = "https://rccm-quiz-2025.onrender.com"
    
    results = {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'analysis': {},
        'steps': []
    }
    
    # Cookieを管理するためのjar
    cookie_jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))
    
    try:
        # Step 1: メインページにアクセスしてセッションを開始
        print("Step 1: メインページにアクセス...")
        request = urllib.request.Request(base_url)
        request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        
        response = opener.open(request)
        main_page_html = response.read().decode('utf-8')
        
        results['steps'].append({
            'step': 1,
            'url': base_url,
            'status': response.getcode(),
            'cookies': len(cookie_jar),
            'html_length': len(main_page_html)
        })
        
        print(f"   Status: {response.getcode()}, Cookies: {len(cookie_jar)}")
        
        # Step 2: 試験開始POSTリクエスト
        print("Step 2: 試験開始POSTリクエスト...")
        category = "河川、砂防及び海岸・海洋"
        start_url = f"{base_url}/start_exam/{urllib.parse.quote(category)}"
        
        post_data = urllib.parse.urlencode({
            'questions': '5',
            'year': '2016'
        }).encode('utf-8')
        
        request = urllib.request.Request(start_url, data=post_data)
        request.add_header('Content-Type', 'application/x-www-form-urlencoded')
        request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        
        response = opener.open(request)
        start_response_html = response.read().decode('utf-8')
        final_url = response.geturl()
        
        results['steps'].append({
            'step': 2,
            'url': start_url,
            'final_url': final_url,
            'status': response.getcode(),
            'cookies': len(cookie_jar),
            'html_length': len(start_response_html)
        })
        
        print(f"   Status: {response.getcode()}")
        print(f"   Final URL: {final_url}")
        print(f"   Cookies: {len(cookie_jar)}")
        
        # Step 3: HTMLの詳細分析
        print("Step 3: HTMLの詳細分析...")
        
        # タイトル抽出
        title_match = re.search(r'<title[^>]*>(.*?)</title>', start_response_html, re.IGNORECASE | re.DOTALL)
        title = title_match.group(1).strip() if title_match else None
        
        # 問題文を探す
        question_text_patterns = [
            r'<p class="lead">(.*?)</p>',
            r'<p[^>]*class="[^"]*question[^"]*"[^>]*>(.*?)</p>',
            r'<div[^>]*class="[^"]*question[^"]*"[^>]*>(.*?)</div>',
            r'question\s*:\s*["\']([^"\']{20,})["\']',
            r'"question":\s*"([^"]{20,})"'
        ]
        
        found_questions = []
        for pattern in question_text_patterns:
            matches = re.findall(pattern, start_response_html, re.IGNORECASE | re.DOTALL)
            for match in matches:
                clean_match = re.sub(r'<[^>]+>', '', match).strip()
                if clean_match and len(clean_match) > 20:
                    found_questions.append({
                        'pattern': pattern,
                        'text': clean_match[:300] + '...' if len(clean_match) > 300 else clean_match
                    })
        
        # 選択肢を探す
        option_patterns = [
            r'<input[^>]*type="radio"[^>]*name="answer"[^>]*value="([ABCD])"',
            r'<label[^>]*for="option([ABCD])"[^>]*>(.*?)</label>',
            r'option_([abcd])["\']:\s*["\']([^"\']{5,})["\']',
            r'"option_([abcd])":\s*"([^"]{5,})"'
        ]
        
        found_options = []
        for pattern in option_patterns:
            matches = re.findall(pattern, start_response_html, re.IGNORECASE | re.DOTALL)
            for match in matches:
                if isinstance(match, tuple) and len(match) >= 2:
                    clean_text = re.sub(r'<[^>]+>', '', match[1] if len(match) > 1 else match[0]).strip()
                    if clean_text and len(clean_text) > 3:
                        found_options.append({
                            'pattern': pattern,
                            'option': match[0],
                            'text': clean_text[:200] + '...' if len(clean_text) > 200 else clean_text
                        })
        
        # フォームを探す
        form_matches = re.findall(r'<form[^>]*>(.*?)</form>', start_response_html, re.IGNORECASE | re.DOTALL)
        forms_info = []
        
        for form_html in form_matches:
            action_match = re.search(r'action\s*=\s*["\']([^"\']*)["\']', form_html, re.IGNORECASE)
            method_match = re.search(r'method\s*=\s*["\']([^"\']*)["\']', form_html, re.IGNORECASE)
            
            forms_info.append({
                'action': action_match.group(1) if action_match else '',
                'method': method_match.group(1) if method_match else '',
                'has_radio': 'type="radio"' in form_html.lower(),
                'has_submit': 'type="submit"' in form_html.lower()
            })
        
        # JavaScriptの問題データを探す
        js_data_patterns = [
            r'var\s+question\s*=\s*({[^}]+})',
            r'const\s+question\s*=\s*({[^}]+})',
            r'question\s*:\s*({[^}]+})',
            r'"question":\s*"([^"]{20,})"',
            r'question_data\s*=\s*({[^}]+})'
        ]
        
        found_js_data = []
        for pattern in js_data_patterns:
            matches = re.findall(pattern, start_response_html, re.IGNORECASE | re.DOTALL)
            for match in matches:
                found_js_data.append({
                    'pattern': pattern,
                    'data': match[:500] + '...' if len(match) > 500 else match
                })
        
        # 分析結果をまとめる
        results['analysis'] = {
            'basic_info': {
                'final_url': final_url,
                'title': title,
                'html_length': len(start_response_html),
                'has_exam_form': any(form['has_radio'] for form in forms_info)
            },
            'question_detection': {
                'found_questions': found_questions,
                'question_count': len(found_questions)
            },
            'options_detection': {
                'found_options': found_options,
                'option_count': len(found_options)
            },
            'forms_info': forms_info,
            'js_data': found_js_data,
            'html_structure': {
                'has_exam_question_class': 'exam-question' in start_response_html,
                'has_question_text_class': 'question-text' in start_response_html,
                'has_answer_options_class': 'answer-options' in start_response_html,
                'has_form_check_class': 'form-check' in start_response_html,
                'has_card_body': 'card-body' in start_response_html
            }
        }
        
        # HTMLサンプルを保存
        results['html_samples'] = {
            'first_1000_chars': start_response_html[:1000],
            'question_area_sample': '',
            'form_area_sample': ''
        }
        
        # 問題エリアのサンプルを抽出
        question_area_match = re.search(r'<div[^>]*class="[^"]*question[^"]*"[^>]*>(.*?)</div>', start_response_html, re.IGNORECASE | re.DOTALL)
        if question_area_match:
            results['html_samples']['question_area_sample'] = question_area_match.group(1)[:500]
        
        # フォームエリアのサンプルを抽出
        form_area_match = re.search(r'<form[^>]*>(.*?)</form>', start_response_html, re.IGNORECASE | re.DOTALL)
        if form_area_match:
            results['html_samples']['form_area_sample'] = form_area_match.group(1)[:500]
        
        print("Step 3: 分析完了")
        
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
        results['analysis']['error'] = str(e)
    
    return results

if __name__ == "__main__":
    results = analyze_production_html_with_session()
    
    # 結果を保存
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    filename = f"production_session_analysis_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n分析結果を {filename} に保存しました")
    
    # 結果サマリーを表示
    print("\n=== 分析結果サマリー ===")
    if 'basic_info' in results['analysis']:
        info = results['analysis']['basic_info']
        print(f"最終URL: {info['final_url']}")
        print(f"タイトル: {info['title']}")
        print(f"HTML長: {info['html_length']} 文字")
        print(f"試験フォーム存在: {info['has_exam_form']}")
    
    if 'question_detection' in results['analysis']:
        q_info = results['analysis']['question_detection']
        print(f"\n問題文検出: {q_info['question_count']} 件")
        for i, q in enumerate(q_info['found_questions'][:2]):
            print(f"  {i+1}. {q['text']}")
    
    if 'options_detection' in results['analysis']:
        o_info = results['analysis']['options_detection']
        print(f"\n選択肢検出: {o_info['option_count']} 件")
        for i, o in enumerate(o_info['found_options'][:3]):
            print(f"  {i+1}. {o['option']}: {o['text']}")
    
    if 'html_structure' in results['analysis']:
        struct = results['analysis']['html_structure']
        print(f"\nHTML構造:")
        for key, value in struct.items():
            print(f"  {key}: {value}")
    
    if 'html_samples' in results and results['html_samples']['first_1000_chars']:
        print(f"\nHTMLサンプル（最初の500文字）:")
        print(results['html_samples']['first_1000_chars'][:500])