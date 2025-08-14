#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
道路部門問題表示デバッグ - レスポンス内容確認
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'rccm-quiz-app'))

from app import app

def debug_exam_response():
    """道路部門の問題表示レスポンスをデバッグ"""
    print("道路部門問題表示デバッグ開始")
    
    with app.test_client() as client:
        # 道路部門セッション開始
        print("Step 1: 道路部門セッション開始")
        response = client.get('/start_exam/specialist_road', follow_redirects=True)
        print(f"セッション開始レスポンス状態: {response.status_code}")
        
        # 問題画面アクセス
        print("Step 2: 問題画面アクセス")
        exam_response = client.get('/exam')
        print(f"問題画面レスポンス状態: {exam_response.status_code}")
        
        if exam_response.status_code == 200:
            response_text = exam_response.get_data(as_text=True)
            print(f"レスポンス文字数: {len(response_text)}")
            
            # キーワード検索
            keywords = ["問題", "/10", "道路", "カテゴリ", "question_id", "form"]
            for keyword in keywords:
                count = response_text.count(keyword)
                print(f"キーワード '{keyword}': {count}回出現")
            
            # HTMLタグ確認
            if "<html" in response_text:
                print("HTMLページとして表示されています")
            if "<form" in response_text:
                print("フォーム要素が含まれています")
            if "question_id" in response_text:
                print("question_idフィールドが含まれています")
                
            # 最初の500文字を安全に表示
            print("レスポンス最初の部分（ASCII変換）:")
            try:
                safe_text = response_text[:500].encode('ascii', errors='replace').decode('ascii')
                print(safe_text)
            except:
                print("レスポンステキスト表示でエラー発生")
        else:
            print(f"問題画面アクセス失敗: {exam_response.status_code}")

if __name__ == "__main__":
    debug_exam_response()