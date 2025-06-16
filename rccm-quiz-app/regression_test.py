#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import time
import re

def regression_check():
    """修正前に動作していた機能の退行チェック"""
    
    base_url = 'http://localhost:5003'
    session = requests.Session()

    print('🔧 修正前機能退行チェック開始...')
    print('📋 各部門3問ずつテストして既存機能確認')

    # 11部門 (steel_concreteは別途詳細テスト済み)
    departments = [
        ('road', '道路'),
        ('river', '河川、砂防及び海岸・海洋'), 
        ('tunnel', 'トンネル'),
        ('urban_planning', '都市計画及び地方計画'),
        ('landscape', '造園'),
        ('construction_env', '建設環境'),
        ('soil_foundation', '土質及び基礎'),
        ('construction_planning', '施工計画、施工設備及び積算'),
        ('water_supply', '上水道及び工業用水道'),
        ('forestry', '森林土木'),
        ('agriculture', '農業土木')
    ]

    success_count = 0
    total_tests = len(departments) * 3

    for dept_key, dept_name in departments:
        print(f'\n📚 【{dept_name}】退行チェック')
        
        # 部門開始
        response = session.get(f'{base_url}/department_study/{dept_key}')
        if response.status_code != 200:
            print(f'❌ {dept_name}: 部門アクセス失敗')
            continue
        
        # 3問テスト
        for i in range(3):
            try:
                response = session.get(f'{base_url}/exam')
                if 'セッション情報が異常です' in response.text:
                    print(f'❌ {dept_name}: 問題{i+1} セッション異常')
                    break
                    
                # QID抽出
                qid_match = re.search(r'name="qid" value="(\d+)"', response.text)
                qid = qid_match.group(1) if qid_match else '0'
                
                # 解答送信
                answer_data = {'qid': qid, 'answer': 'A', 'elapsed': '1.5'}
                response = session.post(f'{base_url}/exam', data=answer_data)
                
                if response.status_code == 200 and 'セッション情報が異常です' not in response.text:
                    print(f'   ✅ 問題{i+1}: QID {qid} 正常')
                    success_count += 1
                else:
                    print(f'   ❌ 問題{i+1}: QID {qid} 異常')
                    break
                    
                time.sleep(0.1)
                
            except Exception as e:
                print(f'   ❌ 問題{i+1}: エラー - {str(e)}')
                break

    print(f'\n📊 退行チェック結果:')
    print(f'   ✅ 成功: {success_count}/{total_tests} 問題')
    print(f'   📈 成功率: {(success_count/total_tests)*100:.1f}%')

    # 特別なsteel_concrete再確認
    print(f'\n🔧 Steel_Concrete部門特別確認:')
    try:
        response = session.get(f'{base_url}/department_study/steel_concrete')
        if response.status_code == 200:
            print('   ✅ Steel_Concrete: アクセス正常')
            
            # 1問テスト
            response = session.get(f'{base_url}/exam')
            if 'セッション情報が異常です' not in response.text:
                qid_match = re.search(r'name="qid" value="(\d+)"', response.text)
                qid = qid_match.group(1) if qid_match else '0'
                print(f'   ✅ Steel_Concrete: 問題表示正常 (QID {qid})')
            else:
                print('   ❌ Steel_Concrete: セッション異常')
        else:
            print('   ❌ Steel_Concrete: アクセス失敗')
    except Exception as e:
        print(f'   ❌ Steel_Concrete: エラー - {str(e)}')

    if success_count >= total_tests * 0.95:  # 95%以上
        print('\n🎉 退行チェック成功: 既存機能正常動作')
        return True
    else:
        print('\n❌ 退行チェック失敗: 一部機能に問題')
        return False

if __name__ == '__main__':
    success = regression_check()
    if not success:
        exit(1)
    print('✅ 退行チェック完了')