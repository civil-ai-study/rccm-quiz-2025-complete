
import os
os.environ['PYTHONIOENCODING'] = 'utf-8'
from app import app

departments = ['basic', 'road', 'river', 'urban', 'garden', 'env', 'steel', 'soil', 'construction', 'water', 'forest', 'agri', 'tunnel']
success_count = 0

print('=== 全13部門のFlask検証テスト ===')
with app.test_client() as client:
    for dept in departments:
        try:
            response = client.get(f'/departments/{dept}/types')
            if response.status_code == 200:
                content = response.data.decode('utf-8', errors='ignore')
                if 'not found' in content.lower() or '見つかりません' in content:
                    print(f'ERROR {dept}: Department not found')
                elif '学習開始' in content or '問題種別選択' in content:
                    print(f'SUCCESS {dept}: Page loaded')
                    success_count += 1
                else:
                    print(f'UNKNOWN {dept}: Response unclear')
            else:
                print(f'HTTP_ERROR {dept}: Status {response.status_code}')
        except Exception as e:
            print(f'EXCEPTION {dept}: {str(e)[:50]}')

print(f'')
print(f'=== 最終結果 ===')  
print(f'成功部門数: {success_count}/13')
if success_count == 13:
    print('COMPLETE SUCCESS: 全13部門正常動作')
elif success_count >= 10:
    print('MOSTLY SUCCESS: 大部分の部門が正常動作')
else:
    print('NEEDS_WORK: 修正が必要')

