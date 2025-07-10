#!/usr/bin/env python3
"""
Production環境での完全な試験フロー分析
"""
import urllib.request
import urllib.parse
import json
import time
import re
import http.cookiejar

def analyze_complete_exam_flow():
    """Production環境で完全な試験フローを実行して分析"""
    base_url = "https://rccm-quiz-2025.onrender.com"
    
    results = {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'flow_analysis': {},
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
            'action': 'main_page_access',
            'url': base_url,
            'status': response.getcode(),
            'cookies': len(cookie_jar)
        })
        
        print(f"   Status: {response.getcode()}, Cookies: {len(cookie_jar)}")
        
        # Step 2: 試験シミュレーターページにアクセス
        print("Step 2: 試験シミュレーターページにアクセス...")
        simulator_url = f"{base_url}/exam_simulator"
        request = urllib.request.Request(simulator_url)
        request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        response = opener.open(request)
        simulator_html = response.read().decode('utf-8')
        
        results['steps'].append({
            'step': 2,
            'action': 'simulator_page_access',
            'url': simulator_url,
            'status': response.getcode(),
            'cookies': len(cookie_jar)
        })
        
        # Step 3: 基礎科目の試験を開始
        print("Step 3: 基礎科目の試験を開始...")
        basic_start_url = f"{base_url}/start_exam/基礎科目"
        
        post_data = urllib.parse.urlencode({
            'questions': '10',
            'year': '2024'
        }).encode('utf-8')
        
        request = urllib.request.Request(basic_start_url, data=post_data)
        request.add_header('Content-Type', 'application/x-www-form-urlencoded')
        request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        response = opener.open(request)
        basic_start_html = response.read().decode('utf-8')
        basic_final_url = response.geturl()
        
        results['steps'].append({
            'step': 3,
            'action': 'basic_exam_start',
            'url': basic_start_url,
            'final_url': basic_final_url,
            'status': response.getcode(),
            'cookies': len(cookie_jar),
            'html_length': len(basic_start_html)
        })
        
        print(f"   Status: {response.getcode()}, Final URL: {basic_final_url}")
        
        # Step 4: 基礎科目の試験後、exam_questionにアクセス
        print("Step 4: 基礎科目試験後、exam_questionにアクセス...")
        exam_question_url = f"{base_url}/exam_question"
        
        request = urllib.request.Request(exam_question_url)
        request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        try:
            response = opener.open(request)
            exam_question_html = response.read().decode('utf-8')
            exam_question_final_url = response.geturl()
            
            results['steps'].append({
                'step': 4,
                'action': 'exam_question_access',
                'url': exam_question_url,
                'final_url': exam_question_final_url,
                'status': response.getcode(),
                'cookies': len(cookie_jar),
                'html_length': len(exam_question_html)
            })
            
            print(f"   Status: {response.getcode()}, Final URL: {exam_question_final_url}")
            
            # 問題表示の詳細分析
            print("Step 5: 問題表示の詳細分析...")
            
            # タイトル確認
            title_match = re.search(r'<title[^>]*>(.*?)</title>', exam_question_html, re.IGNORECASE | re.DOTALL)
            title = title_match.group(1).strip() if title_match else None
            
            # 実際の問題ページかチェック
            is_actual_exam_page = (
                'exam-question-card' in exam_question_html or
                'question-text' in exam_question_html or
                'answer-options' in exam_question_html or
                'examAnswerForm' in exam_question_html
            )
            
            # 問題文を探す
            question_patterns = [
                r'<p\s+class="lead"[^>]*>(.*?)</p>',
                r'<div\s+class="question-text"[^>]*>(.*?)</div>',
                r'問題\s*\d+[^。]*。[^。]*。',
                r'次の.*?について.*?適切.*?選択',
                r'次の.*?について.*?正しい.*?選択'
            ]
            
            found_questions = []
            for pattern in question_patterns:
                matches = re.findall(pattern, exam_question_html, re.IGNORECASE | re.DOTALL)
                for match in matches:
                    clean_match = re.sub(r'<[^>]+>', '', match).strip()
                    if clean_match and len(clean_match) > 20:
                        found_questions.append({
                            'pattern': pattern,
                            'text': clean_match[:300]
                        })
            
            # 選択肢を探す
            option_patterns = [
                r'<input[^>]*type="radio"[^>]*name="answer"[^>]*value="([ABCD])"[^>]*>',
                r'<label[^>]*for="option([ABCD])"[^>]*>(.*?)</label>',
                r'<span\s+class="option-text"[^>]*>(.*?)</span>'
            ]
            
            found_options = []
            for pattern in option_patterns:
                matches = re.findall(pattern, exam_question_html, re.IGNORECASE | re.DOTALL)
                for match in matches:
                    if isinstance(match, tuple) and len(match) >= 2:
                        clean_text = re.sub(r'<[^>]+>', '', match[1]).strip()
                        if clean_text and len(clean_text) > 5:
                            found_options.append({
                                'pattern': pattern,
                                'option': match[0],
                                'text': clean_text[:200]
                            })
            
            # 進捗情報を探す
            progress_patterns = [
                r'問題\s*(\d+)\s*/\s*(\d+)',
                r'current_question_number.*?(\d+)',
                r'total_questions.*?(\d+)'
            ]
            
            found_progress = []
            for pattern in progress_patterns:
                matches = re.findall(pattern, exam_question_html, re.IGNORECASE)
                for match in matches:
                    found_progress.append({
                        'pattern': pattern,
                        'data': match
                    })
            
            # 結果をまとめる
            results['flow_analysis'] = {
                'exam_page_analysis': {
                    'title': title,
                    'is_actual_exam_page': is_actual_exam_page,
                    'html_length': len(exam_question_html),
                    'final_url': exam_question_final_url
                },
                'question_content': {
                    'found_questions': found_questions,
                    'question_count': len(found_questions),
                    'found_options': found_options,
                    'option_count': len(found_options),
                    'found_progress': found_progress
                },
                'page_structure': {
                    'has_exam_container': 'exam-container' in exam_question_html,
                    'has_exam_header': 'exam-header' in exam_question_html,
                    'has_question_card': 'exam-question-card' in exam_question_html,
                    'has_question_text': 'question-text' in exam_question_html,
                    'has_answer_options': 'answer-options' in exam_question_html,
                    'has_form_check': 'form-check' in exam_question_html,
                    'has_submit_button': 'submitBtn' in exam_question_html,
                    'has_exam_answer_form': 'examAnswerForm' in exam_question_html
                },
                'html_samples': {
                    'first_2000_chars': exam_question_html[:2000],
                    'question_area': '',
                    'form_area': ''
                }
            }
            
            # 問題エリアのサンプル
            question_area_match = re.search(r'<!-- 問題エリア -->(.*?)<!-- ナビゲーション -->', exam_question_html, re.IGNORECASE | re.DOTALL)
            if question_area_match:
                results['flow_analysis']['html_samples']['question_area'] = question_area_match.group(1)[:1000]
            
            # フォームエリアのサンプル
            form_area_match = re.search(r'<form[^>]*>(.*?)</form>', exam_question_html, re.IGNORECASE | re.DOTALL)
            if form_area_match:
                results['flow_analysis']['html_samples']['form_area'] = form_area_match.group(1)[:1000]
                
        except urllib.error.HTTPError as e:
            print(f"   HTTPError: {e.code}")
            error_response = e.read().decode('utf-8')
            results['steps'].append({
                'step': 4,
                'action': 'exam_question_access',
                'url': exam_question_url,
                'status': e.code,
                'error': error_response[:500]
            })
        
        # Step 6: 専門科目の試験も試してみる
        print("Step 6: 専門科目の試験を試行...")
        specialist_start_url = f"{base_url}/start_exam/河川、砂防及び海岸・海洋"
        
        post_data = urllib.parse.urlencode({
            'questions': '5',
            'year': '2016'
        }).encode('utf-8')
        
        request = urllib.request.Request(specialist_start_url, data=post_data)
        request.add_header('Content-Type', 'application/x-www-form-urlencoded')
        request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        response = opener.open(request)
        specialist_start_html = response.read().decode('utf-8')
        specialist_final_url = response.geturl()
        
        results['steps'].append({
            'step': 6,
            'action': 'specialist_exam_start',
            'url': specialist_start_url,
            'final_url': specialist_final_url,
            'status': response.getcode(),
            'cookies': len(cookie_jar),
            'html_length': len(specialist_start_html)
        })
        
        print(f"   Status: {response.getcode()}, Final URL: {specialist_final_url}")
        
        # Step 7: 専門科目試験後、exam_questionにアクセス
        print("Step 7: 専門科目試験後、exam_questionにアクセス...")
        request = urllib.request.Request(exam_question_url)
        request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        try:
            response = opener.open(request)
            specialist_exam_html = response.read().decode('utf-8')
            specialist_exam_final_url = response.geturl()
            
            results['steps'].append({
                'step': 7,
                'action': 'specialist_exam_question_access',
                'url': exam_question_url,
                'final_url': specialist_exam_final_url,
                'status': response.getcode(),
                'cookies': len(cookie_jar),
                'html_length': len(specialist_exam_html)
            })
            
            print(f"   Status: {response.getcode()}, Final URL: {specialist_exam_final_url}")
            
            # 専門科目の問題ページ分析
            specialist_is_actual_exam_page = (
                'exam-question-card' in specialist_exam_html or
                'question-text' in specialist_exam_html or
                'answer-options' in specialist_exam_html or
                'examAnswerForm' in specialist_exam_html
            )
            
            results['flow_analysis']['specialist_analysis'] = {
                'is_actual_exam_page': specialist_is_actual_exam_page,
                'html_length': len(specialist_exam_html),
                'final_url': specialist_exam_final_url,
                'first_1000_chars': specialist_exam_html[:1000]
            }
            
        except urllib.error.HTTPError as e:
            print(f"   HTTPError: {e.code}")
            results['steps'].append({
                'step': 7,
                'action': 'specialist_exam_question_access',
                'url': exam_question_url,
                'status': e.code,
                'error': e.read().decode('utf-8')[:500]
            })
        
        print("分析完了")
        
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
        results['flow_analysis']['error'] = str(e)
    
    return results

if __name__ == "__main__":
    results = analyze_complete_exam_flow()
    
    # 結果を保存
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    filename = f"complete_exam_flow_analysis_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n分析結果を {filename} に保存しました")
    
    # 結果サマリーを表示
    print("\n=== 完全試験フロー分析結果 ===")
    
    for step in results['steps']:
        print(f"Step {step['step']}: {step['action']}")
        print(f"  URL: {step['url']}")
        if 'final_url' in step:
            print(f"  Final URL: {step['final_url']}")
        print(f"  Status: {step['status']}")
        print(f"  Cookies: {step.get('cookies', 'N/A')}")
        if 'html_length' in step:
            print(f"  HTML Length: {step['html_length']}")
        print()
    
    if 'flow_analysis' in results:
        analysis = results['flow_analysis']
        
        if 'exam_page_analysis' in analysis:
            exam_info = analysis['exam_page_analysis']
            print(f"基礎科目試験ページ分析:")
            print(f"  タイトル: {exam_info['title']}")
            print(f"  実際の試験ページ: {exam_info['is_actual_exam_page']}")
            print(f"  HTML長: {exam_info['html_length']}")
            print(f"  最終URL: {exam_info['final_url']}")
            print()
        
        if 'question_content' in analysis:
            content = analysis['question_content']
            print(f"問題コンテンツ分析:")
            print(f"  検出された問題文: {content['question_count']} 件")
            print(f"  検出された選択肢: {content['option_count']} 件")
            print(f"  検出された進捗情報: {len(content['found_progress'])} 件")
            
            if content['found_questions']:
                print(f"  サンプル問題文:")
                for i, q in enumerate(content['found_questions'][:1]):
                    print(f"    {i+1}. {q['text']}")
            
            if content['found_options']:
                print(f"  サンプル選択肢:")
                for i, o in enumerate(content['found_options'][:2]):
                    print(f"    {i+1}. {o['option']}: {o['text']}")
            print()
        
        if 'specialist_analysis' in analysis:
            specialist = analysis['specialist_analysis']
            print(f"専門科目試験ページ分析:")
            print(f"  実際の試験ページ: {specialist['is_actual_exam_page']}")
            print(f"  HTML長: {specialist['html_length']}")
            print(f"  最終URL: {specialist['final_url']}")
            print()
    
    print("分析完了")