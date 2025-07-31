# -*- coding: utf-8 -*-
"""
ULTRA SYNC 緊急診断テスト
アプリケーションの応答性確認
"""
import requests
import time
import socket

def check_app_responsiveness():
    """アプリケーション応答性診断"""
    print("ULTRA SYNC 緊急診断テスト開始")
    print("=" * 40)
    
    # 1. ポート接続テスト
    print("1. ポート接続テスト")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('localhost', 5005))
        sock.close()
        
        if result == 0:
            print("  ポート5005: 接続可能")
        else:
            print(f"  ポート5005: 接続失敗 ({result})")
            return False
    except Exception as e:
        print(f"  ポート接続エラー: {e}")
        return False
    
    # 2. HTTP応答テスト (短時間)
    print("2. HTTP応答テスト")
    try:
        session = requests.Session()
        start_time = time.time()
        response = session.get('http://localhost:5005/', timeout=15)
        response_time = time.time() - start_time
        
        print(f"  応答時間: {response_time:.2f}秒")
        print(f"  ステータス: {response.status_code}")
        print(f"  サイズ: {len(response.content)} bytes")
        
        if response.status_code == 200:
            print("  HTTP応答: 正常")
            
            # 重要な要素確認
            content = response.text
            elements = {
                'RCCM': 'RCCM' in content,
                '道路部門': '道路' in content,
                'フォーム': 'form' in content.lower(),
                'クイズ': 'quiz' in content.lower() or 'クイズ' in content
            }
            
            print("  要素確認:")
            for element, found in elements.items():
                status = "OK" if found else "NG"
                print(f"    {element}: {status}")
                
            return True
        else:
            print(f"  HTTP応答エラー: {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print("  HTTP応答: タイムアウト (15秒)")
        return False
    except Exception as e:
        print(f"  HTTP応答エラー: {e}")
        return False

def quick_quiz_start_test():
    """クイズ開始の簡易テスト"""
    print("\n3. クイズ開始簡易テスト")
    try:
        session = requests.Session()
        
        # ホームページアクセス
        response = session.get('http://localhost:5005/', timeout=10)
        if response.status_code != 200:
            print("  ホームページアクセス失敗")
            return False
        
        # クイズ開始
        quiz_data = {
            'category': '4-2',
            'department': '道路'
        }
        
        start_time = time.time()
        response = session.post('http://localhost:5005/quiz', data=quiz_data, timeout=10)
        response_time = time.time() - start_time
        
        print(f"  クイズ開始応答時間: {response_time:.2f}秒")
        print(f"  ステータス: {response.status_code}")
        
        if response.status_code in [200, 302]:
            print("  クイズ開始: 成功")
            return True
        else:
            print(f"  クイズ開始失敗: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"  クイズ開始エラー: {e}")
        return False

if __name__ == "__main__":
    # 診断実行
    http_ok = check_app_responsiveness()
    quiz_ok = quick_quiz_start_test() if http_ok else False
    
    print("\n" + "=" * 40)
    print("ULTRA SYNC 診断結果")
    print("=" * 40)
    print(f"HTTP応答: {'OK' if http_ok else 'NG'}")
    print(f"クイズ開始: {'OK' if quiz_ok else 'NG'}")
    
    if http_ok and quiz_ok:
        print("\n基本機能正常 - 手作業テスト実行可能")
    elif http_ok:
        print("\nHTTP応答OK - クイズ機能に問題あり")
    else:
        print("\nHTTP応答NG - アプリケーション確認必要")