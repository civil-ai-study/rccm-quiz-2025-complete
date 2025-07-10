#!/usr/bin/env python3
# 🛡️ ULTRASYNC デプロイ診断ツール

import requests
import json
import time
from datetime import datetime

def ultrasync_deployment_diagnostic():
    """
    デプロイ状況の詳細診断
    副作用ゼロで安全に実行
    """
    
    print('🛡️ ULTRASYNC デプロイ診断開始')
    print('=' * 60)
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache'
    })
    
    base_url = 'https://rccm-quiz-2025.onrender.com'
    
    results = {}
    
    try:
        # 1. 基本接続性テスト
        print('1. 基本接続性テスト')
        response = session.get(base_url, timeout=30)
        results['homepage'] = {
            'status': response.status_code,
            'response_time': response.elapsed.total_seconds(),
            'headers': dict(response.headers)
        }
        print(f'  ホームページ: {response.status_code} ({response.elapsed.total_seconds():.2f}秒)')
        
        # 2. 基礎科目ルートの詳細テスト
        print('2. 基礎科目ルートの詳細テスト')
        
        # 2-1. GETリクエスト（パラメータなし）
        print('  2-1. GETリクエスト（パラメータなし）')
        get_response = session.get(f'{base_url}/start_exam/基礎科目', timeout=30, allow_redirects=True)
        results['basic_get'] = {
            'status': get_response.status_code,
            'final_url': get_response.url,
            'redirects': len(get_response.history),
            'content_length': len(get_response.text)
        }
        print(f'    応答: {get_response.status_code}')
        print(f'    最終URL: {get_response.url}')
        print(f'    リダイレクト数: {len(get_response.history)}')
        
        # 2-2. POSTリクエスト（適切なパラメータ）
        print('  2-2. POSTリクエスト（適切なパラメータ）')
        post_data = {
            'questions': '10',
            'category': '基礎科目',
            'year': '2024'
        }
        post_response = session.post(f'{base_url}/start_exam/基礎科目', 
                                   data=post_data, timeout=30, allow_redirects=True)
        results['basic_post'] = {
            'status': post_response.status_code,
            'final_url': post_response.url,
            'redirects': len(post_response.history),
            'content_length': len(post_response.text)
        }
        print(f'    応答: {post_response.status_code}')
        print(f'    最終URL: {post_response.url}')
        print(f'    リダイレクト数: {len(post_response.history)}')
        
        # 3. ルートの存在確認
        print('3. ルートの存在確認')
        routes_to_check = [
            '/exam',
            '/exam_simulator',
            '/start_exam/basic',
            '/start_exam/foundation'
        ]
        
        for route in routes_to_check:
            try:
                route_response = session.get(f'{base_url}{route}', timeout=15)
                results[f'route_{route}'] = {
                    'status': route_response.status_code,
                    'exists': route_response.status_code != 404
                }
                print(f'  {route}: {route_response.status_code}')
            except Exception as e:
                print(f'  {route}: エラー - {e}')
                results[f'route_{route}'] = {'status': 'error', 'error': str(e)}
        
        # 4. レスポンスヘッダーの分析
        print('4. レスポンスヘッダーの分析')
        cache_headers = ['Cache-Control', 'ETag', 'Last-Modified', 'Expires']
        for header in cache_headers:
            if header in get_response.headers:
                print(f'  {header}: {get_response.headers[header]}')
        
        # 5. Content-Typeとエンコーディング
        print('5. Content-Typeとエンコーディング')
        content_type = get_response.headers.get('Content-Type', 'unknown')
        print(f'  Content-Type: {content_type}')
        
        # 6. 最終URL分析
        print('6. 最終URL分析')
        if '/exam_simulator' in get_response.url:
            print('  ❌ 問題: exam_simulatorにリダイレクト（修正が反映されていない）')
        elif '/exam' in get_response.url:
            print('  ✅ 正常: examルートにリダイレクト')
        else:
            print(f'  ⚠️ 不明: 予期しないURL - {get_response.url}')
        
        # 7. デプロイ時刻の推定
        print('7. デプロイ時刻の推定')
        if 'Date' in get_response.headers:
            server_time = get_response.headers['Date']
            print(f'  サーバー時刻: {server_time}')
        
        # 8. 結果保存
        results['diagnostic_time'] = datetime.now().isoformat()
        results['summary'] = {
            'homepage_ok': results['homepage']['status'] == 200,
            'basic_get_redirects_to_exam_simulator': '/exam_simulator' in results['basic_get']['final_url'],
            'post_works': results['basic_post']['status'] == 200,
            'modification_reflected': '/exam_simulator' not in results['basic_get']['final_url']
        }
        
        with open('ultrasync_deployment_diagnostic_results.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print('\n' + '=' * 60)
        print('🛡️ ULTRASYNC 診断完了')
        print(f'結果保存: ultrasync_deployment_diagnostic_results.json')
        
        return results
        
    except Exception as e:
        print(f'診断中にエラー: {e}')
        return None

if __name__ == '__main__':
    results = ultrasync_deployment_diagnostic()
    
    if results:
        summary = results['summary']
        print('\n📊 診断サマリー:')
        print(f'  ホームページ: {"✅" if summary["homepage_ok"] else "❌"}')
        print(f'  修正反映: {"✅" if summary["modification_reflected"] else "❌"}')
        print(f'  POSTリクエスト: {"✅" if summary["post_works"] else "❌"}')
        
        if not summary['modification_reflected']:
            print('\n⚠️ 修正が反映されていません。さらなる調査が必要です。')
    else:
        print('\n❌ 診断失敗')