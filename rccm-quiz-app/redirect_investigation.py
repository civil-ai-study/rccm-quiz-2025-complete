#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
リダイレクト問題の徹底調査
"""

from app import app
import sys

def investigate_redirect_issue():
    """302リダイレクトの詳細調査"""
    print("=== リダイレクト問題調査開始 ===")
    
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess['user_name'] = 'テストユーザー'
        
        # 道路部門のリダイレクトを詳細調査
        print("\n1. 道路部門アクセス調査...")
        response = client.get('/quiz_department/道路')
        print(f"   ステータス: {response.status_code}")
        print(f"   リダイレクト先: {response.headers.get('Location', 'なし')}")
        
        # リダイレクト先を追跡
        if response.status_code == 302:
            location = response.headers.get('Location')
            if location:
                print(f"\n2. リダイレクト先を追跡: {location}")
                follow_response = client.get(location)
                print(f"   追跡後ステータス: {follow_response.status_code}")
                
                if follow_response.status_code == 200:
                    html_content = follow_response.data.decode('utf-8', errors='ignore')
                    print(f"   内容プレビュー: {html_content[:300]}...")
                    
                    # エラーメッセージを探す
                    if 'error' in html_content.lower() or 'エラー' in html_content:
                        print("   エラーページにリダイレクトされています！")
                        # エラー内容を抽出
                        start = html_content.find('<div')
                        end = html_content.find('</div>', start) + 6
                        if start != -1 and end != -1:
                            error_section = html_content[start:end]
                            print(f"   エラー内容: {error_section}")
        
        # 試験開始もテスト
        print("\n3. 試験開始テスト...")
        start_response = client.post('/start_exam/道路', data={'questions': '10'})
        print(f"   試験開始ステータス: {start_response.status_code}")
        
        if start_response.status_code == 500:
            print("   500エラー発生！内部エラーの詳細を調査...")
            error_content = start_response.data.decode('utf-8', errors='ignore')
            # エラーメッセージを抽出
            if 'error' in error_content.lower():
                lines = error_content.split('\n')
                for i, line in enumerate(lines):
                    if 'error' in line.lower() and i < len(lines) - 1:
                        print(f"   エラー詳細: {line.strip()} {lines[i+1].strip()}")
                        break
        
        # セッション状態も確認
        print("\n4. セッション状態確認...")
        with client.session_transaction() as sess:
            print(f"   selected_question_type: {sess.get('selected_question_type', 'なし')}")
            print(f"   selected_department: {sess.get('selected_department', 'なし')}")
            print(f"   user_name: {sess.get('user_name', 'なし')}")

def test_direct_exam_access():
    """直接exam URLアクセステスト"""
    print("\n=== 直接exam URLアクセステスト ===")
    
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess['user_name'] = 'テストユーザー'
            # セッションを手動設定
            sess['selected_question_type'] = 'specialist'
            sess['selected_department'] = '道路'
        
        # 直接examページにアクセス
        print("1. 直接examページアクセス...")
        exam_response = client.get('/exam')
        print(f"   ステータス: {exam_response.status_code}")
        
        if exam_response.status_code == 200:
            html = exam_response.data.decode('utf-8', errors='ignore')
            if '問題' in html:
                print("   SUCCESS: 問題が表示されています")
            else:
                print("   ERROR: 問題が表示されていません")
                print(f"   内容: {html[:500]}...")
        else:
            print(f"   ERROR: examページでエラー - {exam_response.status_code}")

if __name__ == "__main__":
    print("ULTRA SYNC: File logging disabled - Console only, PermissionError resolved")
    investigate_redirect_issue()
    test_direct_exam_access()