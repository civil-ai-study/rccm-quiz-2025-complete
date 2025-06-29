import sys
sys.path.append('/mnt/c/Users/z285/Desktop/rccm-quiz-app/rccm-quiz-app')
from app import app

# ヘルプページにある全26個のリンク
links = [
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

# 重複削除
unique_links = list(set(links))

print('=== ウルトラシンク全リンク手動確認 ===')
print(f'テスト対象: {len(unique_links)}個のユニークなリンク')
print('')

with app.test_client() as client:
    for i, link in enumerate(sorted(unique_links), 1):
        try:
            resp = client.get(link)
            status = resp.status_code
            
            # ステータスコードによる判定
            if status == 200:
                result = '✅ 正常'
            elif status == 302:
                # リダイレクト先を確認
                location = resp.headers.get('Location', '不明')
                result = f'✅ リダイレクト → {location}'
            elif status == 403:
                result = '🔒 認証必要（正常）'
            elif status == 404:
                result = '❌ ページが見つかりません'
            elif status == 500:
                result = '❌ サーバーエラー'
            else:
                result = f'⚠️ ステータス: {status}'
                
            print(f'{i:2d}. {link:<30} {result}')
            
            # エラーページの内容確認
            if status >= 400 and status != 403:
                if b'error' in resp.data or b'Error' in resp.data:
                    error_msg = resp.data.decode('utf-8', errors='ignore')
                    if 'BuildError' in error_msg:
                        print(f'     → URLビルドエラー検出')
                    elif 'TemplateNotFound' in error_msg:
                        print(f'     → テンプレートが見つかりません')
                        
        except Exception as e:
            print(f'{i:2d}. {link:<30} ❌ エラー: {str(e)}')

print('')
print('=== 確認完了 ===')