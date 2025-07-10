#!/usr/bin/env python3
# 🛡️ ULTRASYNC テンプレート応答分析

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
import re

def analyze_template_response():
    """実際に/examルートが返すテンプレートを分析"""
    
    print('🛡️ ULTRASYNC テンプレート応答分析開始')
    print('=' * 50)
    
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess.clear()
        
        try:
            # セッション初期化
            start_data = {'questions': '10', 'year': '2024'}
            start_response = client.post('/start_exam/基礎科目', data=start_data, follow_redirects=False)
            print(f'セッション初期化: {start_response.status_code}')
            
            # /examルートアクセス
            exam_response = client.get('/exam')
            print(f'/exam応答: {exam_response.status_code}')
            
            content = exam_response.data.decode('utf-8')
            print(f'応答サイズ: {len(content)} bytes')
            print('=' * 50)
            
            # HTMLの先頭を確認
            print('HTML先頭部分:')
            print(content[:500])
            print('=' * 50)
            
            # テンプレート名の推定
            if '<title>' in content:
                title_match = re.search(r'<title>(.*?)</title>', content)
                if title_match:
                    title = title_match.group(1)
                    print(f'ページタイトル: {title}')
            
            # extends確認
            if 'base.html' in content[:200]:
                print('✅ base.htmlを継承')
            else:
                print('❌ base.htmlを継承していない')
            
            # エラー画面の確認
            error_indicators = [
                'error.html',
                'エラーが発生しました',
                'Error',
                'Something went wrong',
                'Internal Server Error',
                '500',
                '404',
                '問題が見つかりません'
            ]
            
            found_errors = []
            for indicator in error_indicators:
                if indicator in content:
                    found_errors.append(indicator)
            
            if found_errors:
                print(f'❌ エラー画面の可能性: {found_errors}')
            else:
                print('✅ エラー画面ではない')
            
            # exam.html特有の要素確認
            exam_elements = [
                'questionForm',
                'name="answer"',
                'name="qid"',
                'option-item',
                'selectOption',
                'current_no',
                'total_questions'
            ]
            
            exam_elements_found = []
            for element in exam_elements:
                if element in content:
                    exam_elements_found.append(element)
            
            print(f'exam.html要素発見: {exam_elements_found}')
            
            # どのテンプレートが表示されているかを推定
            if len(exam_elements_found) >= 3:
                print('✅ 結論: exam.htmlが正常に表示されている')
            elif 'エラー' in content or 'Error' in content:
                print('❌ 結論: エラーページが表示されている')
                
                # エラー内容の詳細抽出
                error_content = re.findall(r'エラー[^<]*', content)
                if error_content:
                    print(f'エラー内容: {error_content}')
            else:
                print('❌ 結論: 不明なページが表示されている')
                
                # HTMLの特徴的な部分を抽出
                body_match = re.search(r'<body[^>]*>(.*?)</body>', content, re.DOTALL)
                if body_match:
                    body_content = body_match.group(1)[:300]
                    print(f'Body内容（先頭300文字）:\n{body_content}')
            
            print('=' * 50)
            print('完全なHTML出力:')
            print(content)
            
        except Exception as e:
            print(f'分析中にエラー: {e}')
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    analyze_template_response()