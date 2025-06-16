#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import time

def test_navigation_links():
    """全ナビゲーションリンク手作業テスト"""
    
    base_url = 'http://localhost:5003'
    session = requests.Session()

    print('🔧 全ナビゲーションリンクテスト開始...')

    # テストする主要ページリスト
    navigation_tests = [
        # メインナビゲーション
        ('/', 'ホームページ'),
        ('/categories', '部門別ページ'),
        ('/statistics', '解答結果分析'),
        ('/review', '復習リスト'),
        ('/reset', 'リセットページ'),
        ('/help', 'ヘルプページ'),
        
        # 12部門別ページ
        ('/department_study/road', '道路部門'),
        ('/department_study/river', '河川、砂防及び海岸・海洋部門'),
        ('/department_study/tunnel', 'トンネル部門'),
        ('/department_study/urban_planning', '都市計画及び地方計画部門'),
        ('/department_study/landscape', '造園部門'),
        ('/department_study/construction_env', '建設環境部門'),
        ('/department_study/steel_concrete', '鋼構造及びコンクリート部門'),
        ('/department_study/soil_foundation', '土質及び基礎部門'),
        ('/department_study/construction_planning', '施工計画、施工設備及び積算部門'),
        ('/department_study/water_supply', '上水道及び工業用水道部門'),
        ('/department_study/forestry', '森林土木部門'),
        ('/department_study/agriculture', '農業土木部門'),
        ('/department_study/basic', '基礎科目(4-1)'),
        
        # 試験関連ページ
        ('/exam', '試験ページ'),
        
        # API エンドポイント
        ('/api/questions/random', 'ランダム問題API'),
        
        # プロフェッショナル機能
        ('/admin', '管理者ダッシュボード'),
        ('/social_learning', 'ソーシャル学習'),
        ('/api_integration', 'API統合'),
    ]

    success_count = 0
    total_count = len(navigation_tests)
    
    print(f'📊 合計 {total_count} ページをテスト中...\n')

    for path, name in navigation_tests:
        try:
            print(f'[{success_count + 1:2d}/{total_count}] 🔍 {name}: {path}')
            
            response = session.get(f'{base_url}{path}', timeout=10)
            
            # ステータスコードチェック
            if response.status_code == 200:
                print(f'     ✅ {name}: 200 OK')
                success_count += 1
            elif response.status_code == 302:
                print(f'     ✅ {name}: 302 リダイレクト (正常)')
                success_count += 1
            elif response.status_code == 404:
                print(f'     ⚠️ {name}: 404 未実装/存在しない')
            elif response.status_code == 500:
                print(f'     ❌ {name}: 500 サーバーエラー')
            else:
                print(f'     ⚠️ {name}: {response.status_code}')
                
            # セッションエラーチェック
            if 'セッション情報が異常です' in response.text:
                print(f'     ❌ {name}: セッションエラー検出')
            elif 'Error' in response.text and response.status_code == 500:
                print(f'     ❌ {name}: エラーページ検出')
            
            time.sleep(0.1)  # サーバー負荷軽減
            
        except requests.exceptions.Timeout:
            print(f'     ❌ {name}: タイムアウト')
        except requests.exceptions.ConnectionError:
            print(f'     ❌ {name}: 接続エラー')
        except Exception as e:
            print(f'     ❌ {name}: エラー - {str(e)}')

    print(f'\n📊 ナビゲーションテスト結果:')
    print(f'   ✅ 成功: {success_count}/{total_count} ページ')
    print(f'   📈 成功率: {(success_count/total_count)*100:.1f}%')
    
    # 特別なテスト: フォーム送信テスト
    print(f'\n🔧 フォーム送信テスト:')
    
    # リセット機能テスト
    try:
        response = session.post(f'{base_url}/reset', data={'confirm': 'yes'})
        if response.status_code in [200, 302]:
            print('     ✅ リセット機能: 正常動作')
        else:
            print(f'     ⚠️ リセット機能: {response.status_code}')
    except Exception as e:
        print(f'     ❌ リセット機能: エラー - {str(e)}')

    # 重要ページの詳細チェック
    print(f'\n🔧 重要ページ詳細チェック:')
    
    critical_pages = [
        ('/', ['RCCM', '試験', '問題集']),
        ('/categories', ['部門', '選択', 'department']),
        ('/statistics', ['統計', '分析', 'statistics']),
    ]
    
    for path, keywords in critical_pages:
        try:
            response = session.get(f'{base_url}{path}')
            if response.status_code == 200:
                content_found = any(keyword in response.text for keyword in keywords)
                if content_found:
                    print(f'     ✅ {path}: コンテンツ正常')
                else:
                    print(f'     ⚠️ {path}: コンテンツ不完全')
            else:
                print(f'     ❌ {path}: アクセス失敗')
        except Exception as e:
            print(f'     ❌ {path}: エラー - {str(e)}')

    if success_count >= total_count * 0.8:  # 80%以上成功
        print('\n🎉 ナビゲーションテスト成功！')
        return True
    else:
        print('\n❌ ナビゲーションテスト失敗 (成功率が低い)')
        return False

if __name__ == '__main__':
    success = test_navigation_links()
    if not success:
        exit(1)
    print('✅ ナビゲーションテスト完了')