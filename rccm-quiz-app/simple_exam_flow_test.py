#!/usr/bin/env python3
"""
Production環境での簡単な試験フロー分析（エンコーディング問題回避）
"""
import urllib.request
import urllib.parse
import json
import time
import re
import http.cookiejar

def test_exam_flow():
    """シンプルな試験フロー分析"""
    base_url = "https://rccm-quiz-2025.onrender.com"
    
    results = {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'steps': [],
        'analysis': {}
    }
    
    # Cookieを管理
    cookie_jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))
    
    try:
        # Step 1: メインページ
        print("Step 1: メインページアクセス...")
        request = urllib.request.Request(base_url)
        request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        response = opener.open(request)
        main_html = response.read().decode('utf-8')
        
        results['steps'].append({
            'step': 1,
            'url': base_url,
            'status': response.getcode(),
            'cookies': len(cookie_jar)
        })
        
        # Step 2: 基礎科目を開始
        print("Step 2: 基礎科目開始...")
        # URLエンコーディングを使用
        basic_category = urllib.parse.quote("基礎科目")
        start_url = f"{base_url}/start_exam/{basic_category}"
        
        post_data = urllib.parse.urlencode({
            'questions': '5',
            'year': '2024'
        }).encode('utf-8')
        
        request = urllib.request.Request(start_url, data=post_data)
        request.add_header('Content-Type', 'application/x-www-form-urlencoded')
        request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        response = opener.open(request)
        start_html = response.read().decode('utf-8')
        final_url = response.geturl()
        
        results['steps'].append({
            'step': 2,
            'url': start_url,
            'final_url': final_url,
            'status': response.getcode(),
            'html_length': len(start_html)
        })
        
        print(f"   Status: {response.getcode()}")
        print(f"   Final URL: {final_url}")
        
        # Step 3: exam_questionアクセス
        print("Step 3: exam_questionアクセス...")
        exam_q_url = f"{base_url}/exam_question"
        
        request = urllib.request.Request(exam_q_url)
        request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        try:
            response = opener.open(request)
            exam_html = response.read().decode('utf-8')
            exam_final_url = response.geturl()
            
            results['steps'].append({
                'step': 3,
                'url': exam_q_url,
                'final_url': exam_final_url,
                'status': response.getcode(),
                'html_length': len(exam_html)
            })
            
            print(f"   Status: {response.getcode()}")
            print(f"   Final URL: {exam_final_url}")
            
            # HTMLを分析
            is_exam_page = any(keyword in exam_html for keyword in [
                'exam-question-card', 'question-text', 'answer-options', 
                'examAnswerForm', '問題 1', 'option_a', 'option_b'
            ])
            
            # 問題文を探す
            question_matches = re.findall(r'問題.*?[。？]', exam_html)
            question_texts = [q[:100] for q in question_matches if len(q) > 10]
            
            # 選択肢を探す
            option_matches = re.findall(r'選択.*?[。？]', exam_html)
            option_texts = [o[:50] for o in option_matches if len(o) > 5]
            
            results['analysis'] = {
                'is_exam_page': is_exam_page,
                'html_length': len(exam_html),
                'final_url': exam_final_url,
                'found_questions': question_texts,
                'found_options': option_texts,
                'html_sample': exam_html[:1000],
                'structure_check': {
                    'has_exam_container': 'exam-container' in exam_html,
                    'has_question_card': 'exam-question-card' in exam_html,
                    'has_form': '<form' in exam_html,
                    'has_radio_inputs': 'type="radio"' in exam_html,
                    'has_jinja': '{{' in exam_html
                }
            }
            
        except urllib.error.HTTPError as e:
            error_text = e.read().decode('utf-8')
            results['steps'].append({
                'step': 3,
                'url': exam_q_url,
                'status': e.code,
                'error': error_text[:200]
            })
            
            results['analysis'] = {
                'error': f"HTTP {e.code}: {error_text[:200]}"
            }
        
        print("分析完了")
        
    except Exception as e:
        results['analysis']['error'] = str(e)
        print(f"エラー: {str(e)}")
    
    return results

if __name__ == "__main__":
    results = test_exam_flow()
    
    # 結果を保存
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    filename = f"simple_exam_flow_test_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n結果を {filename} に保存しました")
    
    # サマリー表示
    print("\n=== 分析結果サマリー ===")
    for step in results['steps']:
        print(f"Step {step['step']}: {step.get('url', 'N/A')}")
        if 'final_url' in step:
            print(f"  Final URL: {step['final_url']}")
        print(f"  Status: {step['status']}")
        if 'html_length' in step:
            print(f"  HTML Length: {step['html_length']}")
        print()
    
    if 'analysis' in results:
        analysis = results['analysis']
        if 'error' in analysis:
            print(f"エラー: {analysis['error']}")
        else:
            print(f"試験ページ判定: {analysis.get('is_exam_page', False)}")
            print(f"HTML長: {analysis.get('html_length', 0)}")
            print(f"最終URL: {analysis.get('final_url', 'N/A')}")
            print(f"検出問題文: {len(analysis.get('found_questions', []))} 件")
            print(f"検出選択肢: {len(analysis.get('found_options', []))} 件")
            
            if analysis.get('structure_check'):
                struct = analysis['structure_check']
                print(f"\n構造チェック:")
                for key, value in struct.items():
                    print(f"  {key}: {value}")
            
            if analysis.get('html_sample'):
                print(f"\nHTMLサンプル（最初の500文字）:")
                print(analysis['html_sample'][:500])