import sys
sys.path.append('/mnt/c/Users/z285/Desktop/rccm-quiz-app/rccm-quiz-app')
from app import app

# リダイレクトするリンクを追跡
redirect_links = ['/social_learning', '/leaderboard']

print('=== リダイレクト先の実際の画面チェック ===')

with app.test_client() as client:
    for link in redirect_links:
        print(f'\n--- {link} の確認 ---')
        
        # 最初のリクエスト
        resp1 = client.get(link)
        print(f'1. {link} → ステータス: {resp1.status_code}')
        
        if resp1.status_code == 302:
            location = resp1.headers.get('Location', '')
            print(f'   リダイレクト先: {location}')
            
            # リダイレクト先にアクセス
            if location.startswith('/'):
                resp2 = client.get(location)
                print(f'2. {location} → ステータス: {resp2.status_code}')
                
                content = resp2.data.decode('utf-8', errors='ignore')
                
                # エラーページかチェック
                if 'エラーが発生しました' in content:
                    print('   ❌ エラーページ表示')
                elif 'BuildError' in content:
                    print('   ❌ URLビルドエラー')
                elif 'TemplateNotFound' in content:
                    print('   ❌ テンプレート未発見')
                elif '<html' in content and '<!DOCTYPE' in content:
                    # ページタイトルを取得
                    if '<title>' in content:
                        title_start = content.find('<title>') + 7
                        title_end = content.find('</title>', title_start)
                        if title_start > 6 and title_end > title_start:
                            title = content[title_start:title_end]
                            print(f'   ✅ 正常なページ (タイトル: {title})')
                        else:
                            print('   ✅ 正常なページ (タイトル不明)')
                    else:
                        print('   ✅ 正常なページ')
                else:
                    print('   ⚠️  不明な内容')
        else:
            print('   リダイレクトなし')

print('\n=== 追加確認: ヘルプページから直接アクセス ===')

# ヘルプページを取得してリンクを確認
help_resp = client.get('/help')
print(f'ヘルプページ: ステータス {help_resp.status_code}')

if help_resp.status_code == 200:
    help_content = help_resp.data.decode('utf-8', errors='ignore')
    
    # グループ参加リンクを検索
    if 'href="/social_learning"' in help_content:
        print('✅ グループ参加リンクあり: /social_learning')
    else:
        print('❌ グループ参加リンクが見つからない')
        
    # ランキングリンクを検索  
    if 'href="/leaderboard"' in help_content:
        print('✅ ランキングリンクあり: /leaderboard')
    else:
        print('❌ ランキングリンクが見つからない')