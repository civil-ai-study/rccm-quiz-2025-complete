#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本番環境ルート発見テスト - 実際のエンドポイント確認
"""

import requests
import json
from datetime import datetime

def discover_production_routes():
    """本番環境で実際に動作するルートを発見"""
    base_url = "https://rccm-quiz-2025.onrender.com"
    session = requests.Session()
    
    routes_to_test = [
        # 基本ルート
        "/",
        "/exam",
        "/help",
        "/statistics",
        "/categories",
        "/review",
        "/reset",
        "/settings",
        
        # 想定される試験関連ルート
        "/quiz",
        "/start_exam",
        "/start_exam/基礎科目",
        "/exam/基礎科目",
        "/exam/道路",
        "/quiz/start",
        "/begin_exam",
        "/select_department",
        
        # 部門別ルート
        "/departments",
        "/departments/基礎科目",
        
        # API系
        "/api/health",
        "/health",
        "/health/simple",
        
        # その他
        "/manifest.json",
        "/static/js/app.js"
    ]
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'base_url': base_url,
        'route_discovery': {},
        'working_routes': [],
        'failed_routes': [],
        'potential_endpoints': []
    }
    
    print(f"🔍 本番環境ルート発見開始: {base_url}")
    print("=" * 60)
    
    for route in routes_to_test:
        try:
            url = f"{base_url}{route}"
            print(f"テスト中: {route}", end=" ... ")
            
            response = session.get(url, timeout=10)
            
            result_data = {
                'route': route,
                'status_code': response.status_code,
                'content_length': len(response.text),
                'content_type': response.headers.get('content-type', ''),
                'working': response.status_code == 200
            }
            
            if response.status_code == 200:
                print(f"✅ {response.status_code}")
                results['working_routes'].append(route)
                
                # HTMLページの場合、内容を少し確認
                if 'text/html' in response.headers.get('content-type', ''):
                    content_sample = response.text[:300]
                    if 'RCCM' in content_sample:
                        result_data['contains_rccm'] = True
                    if 'form' in content_sample.lower():
                        result_data['has_form'] = True
                    if '部門' in content_sample:
                        result_data['has_department'] = True
                        
            elif response.status_code == 404:
                print(f"❌ 404")
                results['failed_routes'].append(route)
            elif response.status_code == 302:
                print(f"🔄 302 -> {response.headers.get('Location', 'Unknown')}")
                result_data['redirect_location'] = response.headers.get('Location', '')
                results['potential_endpoints'].append(route)
            else:
                print(f"⚠️ {response.status_code}")
                
            results['route_discovery'][route] = result_data
            
        except Exception as e:
            print(f"❌ エラー: {e}")
            results['route_discovery'][route] = {
                'route': route,
                'error': str(e),
                'working': False
            }
            results['failed_routes'].append(route)
    
    # 動作しているルートから試験開始方法を推測
    print("\n" + "=" * 60)
    print("📊 発見結果サマリー:")
    print(f"✅ 動作ルート: {len(results['working_routes'])}")
    print(f"❌ 失敗ルート: {len(results['failed_routes'])}")
    print(f"🔄 リダイレクト: {len(results['potential_endpoints'])}")
    
    print("\n🎯 動作確認済みルート:")
    for route in results['working_routes']:
        route_data = results['route_discovery'][route]
        features = []
        if route_data.get('has_form'):
            features.append("フォーム有り")
        if route_data.get('has_department'):
            features.append("部門選択")
        if route_data.get('contains_rccm'):
            features.append("RCCM関連")
        
        feature_text = f" [{', '.join(features)}]" if features else ""
        print(f"  {route}{feature_text}")
    
    # /examページを詳しく調査
    if "/exam" in results['working_routes']:
        print("\n🔍 /exam ページ詳細調査...")
        try:
            exam_response = session.get(f"{base_url}/exam")
            exam_content = exam_response.text
            
            # フォーム送信先を探す
            import re
            form_actions = re.findall(r'action=["\']([^"\']+)["\']', exam_content)
            if form_actions:
                print(f"  📝 フォーム送信先: {form_actions}")
                for action in form_actions:
                    if action not in results['potential_endpoints']:
                        results['potential_endpoints'].append(action)
            
            # ボタンやリンクのhrefを探す
            links = re.findall(r'href=["\']([^"\']+)["\']', exam_content)
            internal_links = [link for link in links if link.startswith('/') and not link.startswith('//')]
            
            if internal_links:
                print(f"  🔗 内部リンク: {internal_links[:5]}...")  # 最初の5つだけ表示
                
        except Exception as e:
            print(f"  ❌ /exam 調査エラー: {e}")
    
    return results

def test_exam_submission():
    """実際の試験開始を試行"""
    base_url = "https://rccm-quiz-2025.onrender.com"
    session = requests.Session()
    
    print("\n🧪 実際の試験開始テスト...")
    
    # まず/examページでフォームデータを確認
    try:
        exam_response = session.get(f"{base_url}/exam")
        if exam_response.status_code == 200:
            print("✅ /examページ取得成功")
            
            # CSRFトークンを探す
            import re
            csrf_match = re.search(r'name="csrf_token"[^>]*value="([^"]*)"', exam_response.text)
            csrf_token = csrf_match.group(1) if csrf_match else ""
            
            # フォーム送信をテスト
            form_data = {
                'exam_type': '基礎科目',
                'questions_count': '10'
            }
            
            if csrf_token:
                form_data['csrf_token'] = csrf_token
                print(f"  🔐 CSRFトークン: {csrf_token[:20]}...")
            
            # POSTテスト
            print("  📤 POSTリクエスト送信中...")
            post_response = session.post(f"{base_url}/exam", data=form_data)
            
            print(f"  📥 レスポンス: {post_response.status_code}")
            
            if post_response.status_code == 302:
                redirect_url = post_response.headers.get('Location', '')
                print(f"  🔄 リダイレクト先: {redirect_url}")
                
                # リダイレクト先にアクセス
                if redirect_url:
                    if redirect_url.startswith('/'):
                        follow_url = f"{base_url}{redirect_url}"
                    else:
                        follow_url = redirect_url
                    
                    follow_response = session.get(follow_url)
                    print(f"  ✅ リダイレクト先レスポンス: {follow_response.status_code}")
                    
                    if follow_response.status_code == 200:
                        # 問題ページかどうか確認
                        if '問題' in follow_response.text or 'Question' in follow_response.text:
                            print("  🎯 問題ページ表示成功！")
                            return True
                        else:
                            print("  ⚠️ 問題ページではない可能性")
                            print(f"  📄 内容サンプル: {follow_response.text[:200]}...")
                
            elif post_response.status_code == 200:
                print("  📄 200レスポンス（リダイレクトなし）")
                if '問題' in post_response.text:
                    print("  🎯 問題ページ直接表示成功！")
                    return True
                
    except Exception as e:
        print(f"  ❌ 試験開始テストエラー: {e}")
    
    return False

if __name__ == "__main__":
    # ルート発見
    discovery_results = discover_production_routes()
    
    # 実際の試験開始テスト
    exam_success = test_exam_submission()
    
    # 結果保存
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    result_file = f"production_route_discovery_{timestamp}.json"
    
    final_results = {
        **discovery_results,
        'exam_submission_test': {
            'success': exam_success,
            'timestamp': datetime.now().isoformat()
        }
    }
    
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(final_results, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 結果保存: {result_file}")
    print(f"🎯 実ユーザーテスト: {'成功' if exam_success else '要調査'}")