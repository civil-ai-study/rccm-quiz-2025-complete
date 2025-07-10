#!/usr/bin/env python3
"""
🚀 拡張本番環境テスト - 全13部門 + 詳細機能テスト
"""
import subprocess
import time
import json
from datetime import datetime

def run_extended_tests():
    print('🔍 拡張本番環境テスト実行（テスト24-50）')
    print('=' * 50)
    
    base_url = 'https://rccm-quiz-2025.onrender.com'
    test_count = 24
    results = []
    
    # テスト24-35: 全12部門 + 基礎科目のテスト
    all_departments = [
        '基礎科目', '道路', '河川・砂防', '都市計画', '造園', 
        '建設環境', '鋼構造・コンクリート', '土質・基礎', 
        '施工計画', '上下水道', '森林土木', '農業土木', 'トンネル'
    ]
    
    for dept in all_departments:
        try:
            result = subprocess.run([
                'curl', '-s', '-w', '%{http_code}', '-o', '/dev/null',
                '-X', 'POST', '-d', 'questions=5&year=2024',
                '--max-time', '15', f'{base_url}/start_exam/{dept}'
            ], capture_output=True, text=True, timeout=20)
            
            status = int(result.stdout.strip())
            success = status in [200, 302]
            status_icon = 'OK' if success else 'NG'
            print(f'[{status_icon}] テスト{test_count}/50: {dept}部門試験開始 (HTTP {status})')
            
            results.append({
                'test_number': test_count,
                'test_name': f'{dept}部門試験開始',
                'success': success,
                'status_code': status
            })
            test_count += 1
            
        except Exception as e:
            print(f'[NG] テスト{test_count}/50: {dept}部門試験開始 (エラー: {e})')
            results.append({
                'test_number': test_count,
                'test_name': f'{dept}部門試験開始',
                'success': False,
                'error': str(e)
            })
            test_count += 1
    
    # テスト37-42: 異なる問題数でのテスト
    question_counts = [5, 10, 15, 20, 25, 30]
    for count in question_counts:
        try:
            result = subprocess.run([
                'curl', '-s', '-w', '%{http_code}', '-o', '/dev/null',
                '-X', 'POST', '-d', f'questions={count}&year=2024',
                '--max-time', '15', f'{base_url}/start_exam/基礎科目'
            ], capture_output=True, text=True, timeout=20)
            
            status = int(result.stdout.strip())
            success = status in [200, 302]
            status_icon = 'OK' if success else 'NG'
            print(f'[{status_icon}] テスト{test_count}/50: {count}問設定テスト (HTTP {status})')
            
            results.append({
                'test_number': test_count,
                'test_name': f'{count}問設定テスト',
                'success': success,
                'status_code': status
            })
            test_count += 1
            
        except Exception as e:
            print(f'[NG] テスト{test_count}/50: {count}問設定テスト (エラー: {e})')
            results.append({
                'test_number': test_count,
                'test_name': f'{count}問設定テスト',
                'success': False,
                'error': str(e)
            })
            test_count += 1
    
    # テスト43-47: 異なる年度でのテスト
    years = [2016, 2017, 2018, 2019, 2024]
    for year in years:
        try:
            result = subprocess.run([
                'curl', '-s', '-w', '%{http_code}', '-o', '/dev/null',
                '-X', 'POST', '-d', f'questions=10&year={year}',
                '--max-time', '15', f'{base_url}/start_exam/道路'
            ], capture_output=True, text=True, timeout=20)
            
            status = int(result.stdout.strip())
            success = status in [200, 302]
            status_icon = 'OK' if success else 'NG'
            print(f'[{status_icon}] テスト{test_count}/50: {year}年度テスト (HTTP {status})')
            
            results.append({
                'test_number': test_count,
                'test_name': f'{year}年度テスト',
                'success': success,
                'status_code': status
            })
            test_count += 1
            
        except Exception as e:
            print(f'[NG] テスト{test_count}/50: {year}年度テスト (エラー: {e})')
            results.append({
                'test_number': test_count,
                'test_name': f'{year}年度テスト',
                'success': False,
                'error': str(e)
            })
            test_count += 1
    
    # テスト48-50: 連続セッションテスト
    for i in range(3):
        try:
            # セッション開始
            result1 = subprocess.run([
                'curl', '-s', '-c', f'/tmp/session_{i}.txt',
                '--max-time', '15', base_url
            ], capture_output=True, text=True, timeout=20)
            
            # 試験開始
            result2 = subprocess.run([
                'curl', '-s', '-b', f'/tmp/session_{i}.txt', 
                '-w', '%{http_code}', '-o', '/dev/null',
                '-X', 'POST', '-d', 'questions=5&year=2024',
                '--max-time', '15', f'{base_url}/start_exam/基礎科目'
            ], capture_output=True, text=True, timeout=20)
            
            status = int(result2.stdout.strip())
            success = status in [200, 302]
            status_icon = 'OK' if success else 'NG'
            print(f'[{status_icon}] テスト{test_count}/50: 連続セッション{i+1} (HTTP {status})')
            
            results.append({
                'test_number': test_count,
                'test_name': f'連続セッション{i+1}',
                'success': success,
                'status_code': status
            })
            test_count += 1
            
        except Exception as e:
            print(f'[NG] テスト{test_count}/50: 連続セッション{i+1} (エラー: {e})')
            results.append({
                'test_number': test_count,
                'test_name': f'連続セッション{i+1}',
                'success': False,
                'error': str(e)
            })
            test_count += 1
    
    # 結果サマリー
    print('\n' + '=' * 50)
    print('📊 拡張テスト結果サマリー')
    print('=' * 50)
    
    total_extended = len(results)
    successful_extended = sum(1 for r in results if r['success'])
    
    print(f'拡張テスト数: {total_extended}')
    print(f'成功: {successful_extended}')
    print(f'失敗: {total_extended - successful_extended}')
    print(f'成功率: {successful_extended/total_extended*100:.1f}%')
    
    # 失敗したテストの詳細
    failed_tests = [r for r in results if not r['success']]
    if failed_tests:
        print('\n[NG] 失敗したテスト:')
        for test in failed_tests:
            print(f'   • テスト{test["test_number"]}: {test["test_name"]}')
            if 'error' in test:
                print(f'     エラー: {test["error"]}')
            elif 'status_code' in test:
                print(f'     HTTP: {test["status_code"]}')
    
    # 詳細結果保存
    with open('extended_test_results.json', 'w', encoding='utf-8') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'extended_tests': {
                'total': total_extended,
                'successful': successful_extended,
                'failed': total_extended - successful_extended,
                'success_rate': successful_extended/total_extended*100
            },
            'results': results
        }, f, indent=2, ensure_ascii=False)
    
    print(f'\n📋 詳細結果: extended_test_results.json')
    
    return successful_extended == total_extended

if __name__ == '__main__':
    success = run_extended_tests()
    if success:
        print('\n🎉 全拡張テスト成功！')
    else:
        print('\n⚠️  一部テストで問題が検出されました。')