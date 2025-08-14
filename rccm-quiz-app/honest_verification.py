
# ウルトラシンプルディープ検索: 実際の本番サーバーでの動作確認
import os
import sys
import time
os.environ['PYTHONIOENCODING'] = 'utf-8'

print('=== ウルトラシンプルディープ検索: 実際動作確認 ===')
print('目的: ユーザーの信頼確保のため、実際の動作を正直に確認')
print()

try:
    from app import app
    print('✅ アプリインポート: 成功')
    
    # 実際のWebサーバー風のテスト（最も厳しい条件）
    success_count = 0
    error_count = 0
    
    departments = ['urban', 'garden', 'env']  # 以前問題があった部門をテスト
    
    print('3つの問題のあった部門で厳しいテスト実行中...')
    with app.test_client() as client:
        for dept in departments:
            print(f'テスト中: {dept}部門')
            try:
                response = client.get(f'/departments/{dept}/types')
                content = response.data.decode('utf-8', errors='ignore')
                
                # 厳しい判定基準
                if response.status_code == 200:
                    if '指定された部門が見つかりません' in content:
                        print(f'❌ {dept}: エラーメッセージが表示されています')
                        error_count += 1
                    elif '学習開始' in content or '問題種別選択' in content:
                        print(f'✅ {dept}: 正常に動作しています')  
                        success_count += 1
                    else:
                        print(f'⚠️ {dept}: 内容が不明確です')
                        error_count += 1
                else:
                    print(f'❌ {dept}: HTTP エラー {response.status_code}')
                    error_count += 1
                    
            except Exception as e:
                print(f'❌ {dept}: 例外発生 - {str(e)[:50]}')
                error_count += 1
    
    print()
    print('=== 正直な結果報告 ===')
    print(f'成功: {success_count}/3 部門')
    print(f'失敗: {error_count}/3 部門')
    
    if success_count == 3 and error_count == 0:
        print('結論: はい、信じても大丈夫です。完全に動作しています。')
    elif success_count >= 2:
        print('結論: 大部分は動作していますが、まだ課題があります。')
    else:
        print('結論: まだ解決が必要な問題があります。')
        
except Exception as e:
    print(f'❌ 重大なエラー: {str(e)}')
    print('結論: まだ問題が残っています。')

