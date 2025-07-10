#!/usr/bin/env python3
"""
Production環境の/exam_questionエンドポイントに直接アクセスして分析
"""
import urllib.request
import urllib.parse
import json
import time
import re
import http.cookiejar

def analyze_exam_question_endpoint():
    """Production環境の/exam_questionエンドポイントを分析"""
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
        # Step 1: メインページにアクセス
        print("Step 1: メインページにアクセス...")
        request = urllib.request.Request(base_url)
        request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        response = opener.open(request)
        main_page_html = response.read().decode('utf-8')
        
        results['steps'].append({
            'step': 1,
            'url': base_url,
            'status': response.getcode(),
            'cookies': len(cookie_jar)
        })
        
        # Step 2: 試験開始POST
        print("Step 2: 試験開始POSTリクエスト...")
        category = "河川、砂防及び海岸・海洋"
        start_url = f"{base_url}/start_exam/{urllib.parse.quote(category)}"
        
        post_data = urllib.parse.urlencode({
            'questions': '5',
            'year': '2016'
        }).encode('utf-8')
        
        request = urllib.request.Request(start_url, data=post_data)
        request.add_header('Content-Type', 'application/x-www-form-urlencoded')
        request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        response = opener.open(request)
        start_response_html = response.read().decode('utf-8')
        
        results['steps'].append({
            'step': 2,
            'url': start_url,
            'final_url': response.geturl(),
            'status': response.getcode(),
            'cookies': len(cookie_jar)
        })
        
        # Step 3: /exam_questionに直接アクセス
        print("Step 3: /exam_questionに直接アクセス...")
        exam_question_url = f"{base_url}/exam_question"
        
        request = urllib.request.Request(exam_question_url)
        request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        try:
            response = opener.open(request)
            exam_question_html = response.read().decode('utf-8')
            
            results['steps'].append({
                'step': 3,
                'url': exam_question_url,
                'status': response.getcode(),
                'cookies': len(cookie_jar),
                'html_length': len(exam_question_html)
            })
            
            print(f"   Status: {response.getcode()}")
            print(f"   HTML Length: {len(exam_question_html)}")
            
            # 詳細分析
            print("Step 4: 問題ページの詳細分析...")
            
            # タイトル
            title_match = re.search(r'<title[^>]*>(.*?)</title>', exam_question_html, re.IGNORECASE | re.DOTALL)
            title = title_match.group(1).strip() if title_match else None
            
            # 問題文を探す - より具体的なパターン
            question_patterns = [
                r'<p\s+class="lead"[^>]*>(.*?)</p>',
                r'<div\s+class="question-text"[^>]*>(.*?)</div>',
                r'{{ question\.question }}',
                r'問題\s*\d+',
                r'<p[^>]*>(.*?次の.*?について.*?)</p>',
                r'<p[^>]*>(.*?適切.*?選択.*?)</p>',
                r'<p[^>]*>(.*?正しい.*?選択.*?)</p>'
            ]
            
            found_questions = []
            for pattern in question_patterns:
                matches = re.findall(pattern, exam_question_html, re.IGNORECASE | re.DOTALL)
                for match in matches:
                    clean_match = re.sub(r'<[^>]+>', '', match).strip()
                    if clean_match and len(clean_match) > 5:
                        found_questions.append({
                            'pattern': pattern,
                            'text': clean_match[:200] + '...' if len(clean_match) > 200 else clean_match
                        })
            
            # 選択肢を探す
            option_patterns = [
                r'<input[^>]*type="radio"[^>]*name="answer"[^>]*value="([ABCD])"[^>]*>',
                r'<label[^>]*for="option([ABCD])"[^>]*>(.*?)</label>',
                r'{{ question\.option_([abcd]) }}',
                r'<span\s+class="option-text"[^>]*>(.*?)</span>'
            ]
            
            found_options = []
            for pattern in option_patterns:
                matches = re.findall(pattern, exam_question_html, re.IGNORECASE | re.DOTALL)
                for match in matches:
                    if isinstance(match, tuple) and len(match) >= 2:
                        clean_text = re.sub(r'<[^>]+>', '', match[1]).strip()
                        if clean_text and len(clean_text) > 3:
                            found_options.append({
                                'pattern': pattern,
                                'option': match[0],
                                'text': clean_text[:150] + '...' if len(clean_text) > 150 else clean_text
                            })
                    elif isinstance(match, str) and len(match) > 3:
                        found_options.append({
                            'pattern': pattern,
                            'option': 'template',
                            'text': match
                        })
            
            # Jinjaテンプレート変数を探す
            jinja_patterns = [
                r'{{ question\.(.*?) }}',
                r'{% .*? %}',
                r'{{ exam_info\.(.*?) }}',
                r'{{ (.*?) }}'
            ]
            
            found_jinja = []
            for pattern in jinja_patterns:
                matches = re.findall(pattern, exam_question_html, re.IGNORECASE)
                for match in matches:
                    found_jinja.append({
                        'pattern': pattern,
                        'variable': match
                    })
            
            # HTML構造チェック
            structure_checks = {
                'has_exam_container': 'exam-container' in exam_question_html,
                'has_exam_header': 'exam-header' in exam_question_html,
                'has_question_card': 'exam-question-card' in exam_question_html,
                'has_question_text': 'question-text' in exam_question_html,
                'has_answer_options': 'answer-options' in exam_question_html,
                'has_form_check': 'form-check' in exam_question_html,
                'has_option_text': 'option-text' in exam_question_html,
                'has_submit_button': 'submitBtn' in exam_question_html,
                'has_exam_answer_form': 'examAnswerForm' in exam_question_html,
                'has_jinja_templates': '{{' in exam_question_html,
                'has_exam_info': 'exam_info' in exam_question_html,
                'has_question_object': 'question.' in exam_question_html,
                'has_progress_bar': 'progress-bar' in exam_question_html
            }
            
            # 分析結果をまとめる
            results['analysis'] = {
                'basic_info': {
                    'status': response.getcode(),
                    'title': title,
                    'html_length': len(exam_question_html),
                    'is_template': '{{' in exam_question_html or '{%' in exam_question_html
                },
                'question_analysis': {
                    'found_questions': found_questions,
                    'question_count': len(found_questions)
                },
                'options_analysis': {
                    'found_options': found_options,
                    'option_count': len(found_options)
                },
                'jinja_analysis': {
                    'found_variables': found_jinja,
                    'variable_count': len(found_jinja)
                },
                'structure_analysis': structure_checks,
                'html_samples': {
                    'first_1000_chars': exam_question_html[:1000],
                    'question_area': '',
                    'form_area': ''
                }
            }
            
            # 問題エリアのサンプル
            question_area_match = re.search(r'<div[^>]*class="[^"]*question-text[^"]*"[^>]*>(.*?)</div>', exam_question_html, re.IGNORECASE | re.DOTALL)
            if question_area_match:
                results['analysis']['html_samples']['question_area'] = question_area_match.group(1)[:500]
            
            # フォームエリアのサンプル
            form_area_match = re.search(r'<form[^>]*id="examAnswerForm"[^>]*>(.*?)</form>', exam_question_html, re.IGNORECASE | re.DOTALL)
            if form_area_match:
                results['analysis']['html_samples']['form_area'] = form_area_match.group(1)[:500]
            
        except urllib.error.HTTPError as e:
            print(f"   HTTPError: {e.code}")
            error_response = e.read().decode('utf-8')
            results['steps'].append({
                'step': 3,
                'url': exam_question_url,
                'status': e.code,
                'error': error_response[:500]
            })
            
            results['analysis'] = {
                'error': {
                    'code': e.code,
                    'message': error_response[:500]
                }
            }
        
        print("分析完了")
        
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
        results['analysis']['error'] = str(e)
    
    return results

if __name__ == "__main__":
    results = analyze_exam_question_endpoint()
    
    # 結果を保存
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    filename = f"production_exam_question_analysis_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n分析結果を {filename} に保存しました")
    
    # 結果サマリーを表示
    print("\n=== 分析結果サマリー ===")
    
    for step in results['steps']:
        print(f"Step {step['step']}: {step['url']} -> Status: {step['status']}")
    
    if 'analysis' in results:
        if 'error' in results['analysis']:
            print(f"\nエラー: {results['analysis']['error']}")
        elif 'basic_info' in results['analysis']:
            info = results['analysis']['basic_info']
            print(f"\n基本情報:")
            print(f"  ステータス: {info['status']}")
            print(f"  タイトル: {info['title']}")
            print(f"  HTML長: {info['html_length']} 文字")
            print(f"  テンプレート: {info['is_template']}")
            
            if 'question_analysis' in results['analysis']:
                q_info = results['analysis']['question_analysis']
                print(f"\n問題文: {q_info['question_count']} 件")
                for i, q in enumerate(q_info['found_questions'][:2]):
                    print(f"  {i+1}. {q['text']}")
            
            if 'options_analysis' in results['analysis']:
                o_info = results['analysis']['options_analysis']
                print(f"\n選択肢: {o_info['option_count']} 件")
                for i, o in enumerate(o_info['found_options'][:3]):
                    print(f"  {i+1}. {o['option']}: {o['text']}")
            
            if 'structure_analysis' in results['analysis']:
                struct = results['analysis']['structure_analysis']
                print(f"\nHTML構造:")
                important_keys = ['has_jinja_templates', 'has_question_object', 'has_answer_options', 'has_form_check']
                for key in important_keys:
                    if key in struct:
                        print(f"  {key}: {struct[key]}")
            
            if 'html_samples' in results['analysis'] and results['analysis']['html_samples']['first_1000_chars']:
                print(f"\nHTMLサンプル（最初の500文字）:")
                print(results['analysis']['html_samples']['first_1000_chars'][:500])