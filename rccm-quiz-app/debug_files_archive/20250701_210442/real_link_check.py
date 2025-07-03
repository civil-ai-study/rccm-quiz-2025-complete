import sys
sys.path.append('/mnt/c/Users/z285/Desktop/rccm-quiz-app/rccm-quiz-app')
from app import app

# ヘルプページにある全リンク
help_links = [
    '/exam?type=basic',
    '/categories', 
    '/review',
    '/',
    '/social_learning',
    '/leaderboard', 
    '/statistics',
    '/srs_stats',
    '/api_integration',
    '/admin',
    '/health_check',
    '/force_reset',
    '/ai_dashboard',
    '/advanced_analytics'
]

print('=== 実際のレスポンス内容チェック（エラー画面検出） ===')

with app.test_client() as client:
    for i, link in enumerate(help_links, 1):
        try:
            resp = client.get(link)
            status = resp.status_code
            content = resp.data.decode('utf-8', errors='ignore')
            
            # エラー画面の判定
            is_error_page = False
            error_details = []
            
            # エラーページの特徴を検出
            if 'エラーが発生しました' in content:
                is_error_page = True
                error_details.append('エラーメッセージあり')
            
            if 'BuildError' in content:
                is_error_page = True
                error_details.append('URLビルドエラー')
                
            if 'TemplateNotFound' in content:
                is_error_page = True
                error_details.append('テンプレート未発見')
                
            if 'AttributeError' in content:
                is_error_page = True
                error_details.append('属性エラー')
                
            if 'KeyError' in content:
                is_error_page = True
                error_details.append('キーエラー')
                
            if 'Internal Server Error' in content:
                is_error_page = True
                error_details.append('サーバー内部エラー')
                
            if 'Traceback' in content:
                is_error_page = True
                error_details.append('Pythonトレースバック')
            
            # ページタイトルでも判定
            if '<title>' in content:
                title_start = content.find('<title>') + 7
                title_end = content.find('</title>', title_start)
                if title_start > 6 and title_end > title_start:
                    title = content[title_start:title_end]
                    if 'エラー' in title or 'Error' in title:
                        is_error_page = True
                        error_details.append(f'エラータイトル: {title}')
            
            # 結果表示
            if is_error_page:
                print(f'{i:2d}. {link:<30} ❌ エラー画面 [{", ".join(error_details)}]')
                
                # エラー詳細の一部を表示
                if 'BuildError' in content:
                    build_error_start = content.find('BuildError')
                    error_excerpt = content[build_error_start:build_error_start+200]
                    print(f'     詳細: {error_excerpt}...')
                    
            elif status == 403:
                print(f'{i:2d}. {link:<30} 🔒 認証必要（正常）')
            elif status == 302:
                location = resp.headers.get('Location', '不明')
                print(f'{i:2d}. {link:<30} ✅ リダイレクト → {location}')
            elif status == 200:
                # 正常なページか確認
                if '<html' in content and '<!DOCTYPE' in content:
                    print(f'{i:2d}. {link:<30} ✅ 正常なページ')
                else:
                    print(f'{i:2d}. {link:<30} ⚠️  HTMLじゃない可能性')
            else:
                print(f'{i:2d}. {link:<30} ⚠️  ステータス: {status}')
                
        except Exception as e:
            print(f'{i:2d}. {link:<30} ❌ 例外エラー: {str(e)}')

print('\n=== エラー画面検出チェック完了 ===')