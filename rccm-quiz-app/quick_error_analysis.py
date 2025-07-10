#!/usr/bin/env python3
"""
🚨 エラー内容の詳細分析
試験開始時のエラーページ内容を詳細に確認
"""
import subprocess
import json
import re
from datetime import datetime

def analyze_error_response():
    """エラーレスポンスの詳細分析"""
    base_url = 'https://rccm-quiz-2025.onrender.com'
    
    print("🚨 試験開始エラーの詳細分析")
    print("=" * 50)
    
    try:
        # セッション初期化
        subprocess.run([
            'curl', '-s', '-c', '/tmp/error_analysis_session.txt', 
            '--max-time', '10', base_url
        ], capture_output=True, text=True, timeout=15)
        
        # 基礎科目で試験開始を試行
        result = subprocess.run([
            'curl', '-s', '-L',
            '-b', '/tmp/error_analysis_session.txt',
            '-X', 'POST', '-d', 'questions=10&year=2024',
            '--max-time', '20', f"{base_url}/start_exam/基礎科目"
        ], capture_output=True, text=True, timeout=25)
        
        content = result.stdout
        
        if not content:
            print("❌ レスポンスが空です")
            return
        
        print(f"✅ レスポンス取得成功 ({len(content)}文字)")
        
        # タイトルの抽出
        title_match = re.search(r'<title[^>]*>(.*?)</title>', content, re.IGNORECASE | re.DOTALL)
        if title_match:
            title = title_match.group(1).strip()
            print(f"📋 ページタイトル: {title}")
        
        # エラーメッセージの抽出
        error_patterns = [
            r'<h[1-6][^>]*[^>]*エラー[^<]*</h[1-6]>',
            r'<div[^>]*error[^>]*>([^<]+)</div>',
            r'<p[^>]*>([^<]*エラー[^<]*)</p>',
            r'<span[^>]*>([^<]*問題が発生[^<]*)</span>'
        ]
        
        print("\n🔍 エラーメッセージ:")
        for pattern in error_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
            for match in matches:
                clean_match = re.sub(r'<[^>]+>', '', str(match)).strip()
                if clean_match:
                    print(f"   • {clean_match}")
        
        # 本文の重要部分を抽出
        body_start = content.find('<body')
        if body_start != -1:
            body_content = content[body_start:body_start+2000]
            
            # HTMLタグを除去して読みやすくする
            clean_text = re.sub(r'<script[^>]*>.*?</script>', '', body_content, flags=re.DOTALL)
            clean_text = re.sub(r'<style[^>]*>.*?</style>', '', clean_text, flags=re.DOTALL)
            clean_text = re.sub(r'<[^>]+>', '\n', clean_text)
            clean_text = re.sub(r'\n+', '\n', clean_text)
            
            print("\n📄 エラーページの主要内容:")
            for line in clean_text.split('\n')[:20]:
                line = line.strip()
                if line and len(line) > 5:
                    print(f"   {line}")
        
        # 結果を保存
        with open('error_analysis_results.json', 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'title': title if 'title' in locals() else "",
                'content_length': len(content),
                'raw_content': content[:2000],  # 最初の2000文字のみ保存
                'analysis': "試験開始時にエラーページが表示される"
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\n📋 詳細結果保存: error_analysis_results.json")
        
    except Exception as e:
        print(f"❌ エラー分析中にエラー: {str(e)}")

def test_simple_pages():
    """シンプルなページのテスト"""
    base_url = 'https://rccm-quiz-2025.onrender.com'
    
    print("\n🔍 基本ページのテスト")
    print("=" * 30)
    
    test_pages = [
        ('ホーム', ''),
        ('部門選択', '/departments'),
        ('ヘルプ', '/help'),
        ('設定', '/settings')
    ]
    
    for page_name, path in test_pages:
        try:
            result = subprocess.run([
                'curl', '-s', '-w', '%{http_code}', '-o', '/dev/null',
                '--max-time', '10', f"{base_url}{path}"
            ], capture_output=True, text=True, timeout=15)
            
            status_code = int(result.stdout.strip())
            status = '✅' if status_code == 200 else '❌'
            print(f"{status} {page_name}: HTTP {status_code}")
            
        except Exception as e:
            print(f"❌ {page_name}: エラー {str(e)}")

if __name__ == '__main__':
    analyze_error_response()
    test_simple_pages()