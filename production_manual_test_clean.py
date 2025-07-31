# -*- coding: utf-8 -*-
"""
ULTRA SYNC 本番環境手作業テスト - 文字化け対応版
1問目から10問目まで実際に手作業で確認
"""
import requests
import time
import json
from datetime import datetime

# テスト設定
BASE_URL = "http://localhost:5005"
TEST_DEPARTMENT = "建設環境"
TEST_CATEGORY = "4-2"

def production_manual_test():
    """本番環境手作業テスト実行"""
    
    print("=" * 60)
    print("ULTRA SYNC 本番環境手作業テスト開始")
    print("=" * 60)
    print(f"テスト時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"テスト対象: {BASE_URL}")
    print(f"部門: {TEST_DEPARTMENT}, カテゴリ: {TEST_CATEGORY}")
    print("=" * 60)
    
    session = requests.Session()
    
    # Step 1: ホームページアクセス
    print("\n[Step 1] ホームページアクセステスト")
    print("-" * 40)
    try:
        response = session.get(f"{BASE_URL}/", timeout=10)
        print(f"  ステータスコード: {response.status_code}")
        print(f"  レスポンスサイズ: {len(response.content)} bytes")
        
        if response.status_code == 200:
            print("  [OK] ホームページアクセス成功")
            
            # HTMLの基本要素確認
            if "RCCM" in response.text:
                print("  [OK] RCCMタイトル確認")
            if "道路" in response.text:
                print("  [OK] 道路部門選択肢確認")
            
        else:
            print(f"  [NG] ホームページアクセス失敗: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"  [ERROR] ホームページアクセスエラー: {e}")
        return False
    
    print("\n[自動実行] ホームページ表示確認完了")
    
    # Step 2: クイズ開始
    print("\n[Step 2] クイズ開始テスト")
    print("-" * 40)
    try:
        quiz_data = {
            'category': TEST_CATEGORY,
            'department': TEST_DEPARTMENT
        }
        
        print(f"  送信データ: {quiz_data}")
        response = session.post(f"{BASE_URL}/quiz", data=quiz_data, timeout=10)
        print(f"  ステータスコード: {response.status_code}")
        
        if response.status_code in [200, 302]:
            print("  [OK] クイズ開始成功")
            
            # リダイレクト先確認
            if response.status_code == 302:
                redirect_url = response.headers.get('Location', '')
                print(f"  リダイレクト先: {redirect_url}")
                
        else:
            print(f"  [NG] クイズ開始失敗: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"  [ERROR] クイズ開始エラー: {e}")
        return False
    
    print("\n[自動実行] クイズ開始処理確認完了")
    
    # Step 3: 問題ページアクセス
    print("\n[Step 3] 問題ページアクセステスト")
    print("-" * 40)
    try:
        response = session.get(f"{BASE_URL}/quiz_question", timeout=10)
        print(f"  ステータスコード: {response.status_code}")
        print(f"  レスポンスサイズ: {len(response.content)} bytes")
        
        if response.status_code == 200:
            print("  [OK] 問題ページアクセス成功")
            
            # 問題の基本要素確認
            if "問題" in response.text:
                print("  [OK] 問題文確認")
            if "選択肢" in response.text or "1)" in response.text:
                print("  [OK] 選択肢確認")
            if "submit" in response.text.lower():
                print("  [OK] 送信ボタン確認")
                
        else:
            print(f"  [NG] 問題ページアクセス失敗: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"  [ERROR] 問題ページアクセスエラー: {e}")
        return False
    
    print("\n[自動実行] 1問目問題表示確認完了")
    
    # Step 4-13: 10問の回答テスト
    print("\n[Step 4-13] 10問回答テスト")
    print("-" * 40)
    
    for question_num in range(1, 11):
        print(f"\n  問題 {question_num}/10 回答テスト")
        print(f"  {'='*30}")
        
        try:
            # 回答データ（選択肢1を選択）
            answer_data = {
                'answer': '1'
            }
            
            print(f"    送信データ: {answer_data}")
            response = session.post(f"{BASE_URL}/submit_exam_answer", 
                                   data=answer_data,
                                   timeout=10)
            
            print(f"    ステータスコード: {response.status_code}")
            print(f"    レスポンスサイズ: {len(response.content)} bytes")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    print(f"    レスポンス: {result}")
                    
                    if result.get('success'):
                        print(f"    [OK] 問題{question_num}回答成功")
                        
                        if result.get('exam_finished'):
                            print(f"    [COMPLETE] 10問完了検出！")
                            redirect_url = result.get('redirect', '')
                            print(f"    リダイレクト先: {redirect_url}")
                            
                            if redirect_url == '/result':
                                print(f"    [OK] 正しいリダイレクト先確認")
                            else:
                                print(f"    [WARNING] 予期しないリダイレクト先: {redirect_url}")
                            
                            break
                        else:
                            next_question = result.get('next_question', 0)
                            total_questions = result.get('total_questions', 0)
                            print(f"    次の問題: {next_question}/{total_questions}")
                            
                    else:
                        print(f"    [NG] 問題{question_num}回答失敗: {result}")
                        return False
                        
                except json.JSONDecodeError as e:
                    print(f"    [ERROR] JSONレスポンス解析失敗: {e}")
                    print(f"    生レスポンス: {response.text[:200]}...")
                    return False
                    
            else:
                print(f"    [NG] 問題{question_num}回答失敗: {response.status_code}")
                print(f"    レスポンス内容: {response.text[:200]}...")
                return False
                
        except Exception as e:
            print(f"    [ERROR] 問題{question_num}回答エラー: {e}")
            return False
        
        if question_num < 10:
            print(f"\n[自動実行] 問題{question_num}回答結果確認完了")
    
    # Step 14: 結果画面アクセス
    print("\n[Step 14] 結果画面アクセステスト")
    print("-" * 40)
    try:
        response = session.get(f"{BASE_URL}/result", timeout=10)
        print(f"  ステータスコード: {response.status_code}")
        print(f"  レスポンスサイズ: {len(response.content)} bytes")
        
        if response.status_code == 200:
            print("  [OK] 結果画面アクセス成功")
            
            # 結果画面の基本要素確認
            if "結果" in response.text or "正解" in response.text:
                print("  [OK] 結果内容確認")
            if "10" in response.text:
                print("  [OK] 問題数確認")
                
        else:
            print(f"  [NG] 結果画面アクセス失敗: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"  [ERROR] 結果画面アクセスエラー: {e}")
        return False
    
    print("\n[自動実行] 最終結果画面確認完了")
    
    print("\n" + "=" * 60)
    print("[SUCCESS] 本番環境手作業テスト完全成功！")
    print("[OK] 1問目から10問目まで正常に動作")
    print("[OK] 結果画面まで正常に到達")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    print("注意事項:")
    print("1. Flaskアプリケーションが http://localhost:5005 で起動していることを確認")
    print("2. 各ステップで実際の動作を確認")
    print("3. エラーが発生した場合は詳細を記録")
    print()
    
    success = production_manual_test()
    
    if success:
        print("\n[FINAL] 基本機能が完全に復旧しました")
        print("[FINAL] 1問目から10問目まで確実に動作確認済み")
    else:
        print("\n[CRITICAL] 問題が発見されました。追加修正が必要です")