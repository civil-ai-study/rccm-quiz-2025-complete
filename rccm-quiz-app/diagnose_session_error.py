#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
【ULTRASYNC段階11】セッションエラー診断
詳細なエラー分析とデバッグ情報収集
"""

import requests
import json
import re
from datetime import datetime

def diagnose_session_error():
    """セッションエラーの詳細診断"""
    print("🔍 【ULTRASYNC段階11】セッションエラー詳細診断開始")
    print("=" * 60)
    
    base_url = "https://rccm-quiz-2025.onrender.com"
    session = requests.Session()
    
    try:
        # ホームページアクセス
        print("📋 ステップ1: ホームページアクセス")
        response = session.get(f"{base_url}/")
        print(f"   ステータス: {response.status_code}")
        print(f"   セッションCookie: {len(str(session.cookies.get_dict()))} 文字")
        
        # 基礎科目開始 - 詳細情報取得
        print("\n📋 ステップ2: 基礎科目開始 - 詳細診断")
        response = session.get(f"{base_url}/exam?question_type=basic")
        print(f"   ステータス: {response.status_code}")
        print(f"   レスポンスサイズ: {len(response.content)} bytes")
        print(f"   Content-Type: {response.headers.get('Content-Type')}")
        
        # エラーメッセージの詳細抽出
        if "エラー" in response.text:
            print("\n🚨 エラー詳細分析:")
            
            # エラーメッセージを抽出
            error_patterns = [
                r'<p[^>]*><strong>(.*?)</strong></p>',
                r'<div[^>]*class="alert[^"]*"[^>]*>(.*?)</div>',
                r'<h4[^>]*>.*?エラー.*?</h4>',
                r'無効な.*?です',
                r'問題データの取得に失敗しました',
                r'セッションエラーが発生しました'
            ]
            
            for i, pattern in enumerate(error_patterns):
                matches = re.findall(pattern, response.text, re.DOTALL | re.IGNORECASE)
                if matches:
                    print(f"   パターン{i+1}: {matches}")
            
            # HTMLの特定部分を抽出
            if 'error.html' in response.url or 'エラー' in response.text:
                # エラー画面のタイトルを抽出
                title_match = re.search(r'<title>(.*?)</title>', response.text)
                if title_match:
                    print(f"   ページタイトル: {title_match.group(1)}")
                
                # エラーメッセージを詳細抽出
                content_match = re.search(r'<div[^>]*class="card-body"[^>]*>(.*?)</div>', response.text, re.DOTALL)
                if content_match:
                    content = re.sub(r'<[^>]+>', '', content_match.group(1))
                    content = re.sub(r'\s+', ' ', content).strip()
                    print(f"   エラー内容: {content[:200]}...")
        
        # セッション情報の詳細確認
        print("\n📋 ステップ3: セッション情報詳細確認")
        cookies = session.cookies.get_dict()
        print(f"   Cookie数: {len(cookies)}")
        for name, value in cookies.items():
            print(f"   {name}: {len(value)} 文字")
            if name == 'rccm_session':
                print(f"      値の先頭: {value[:50]}...")
        
        # 問題データ直接アクセステスト
        print("\n📋 ステップ4: 問題データ直接アクセステスト")
        response = session.get(f"{base_url}/exam")
        print(f"   ステータス: {response.status_code}")
        
        if response.status_code == 200:
            # 正常な問題ページかチェック
            if 'name="qid"' in response.text and 'name="answer"' in response.text:
                print("   ✅ 正常な問題ページを確認")
                
                # 問題IDを抽出
                qid_match = re.search(r'name="qid"[^>]*value="(\d+)"', response.text)
                if qid_match:
                    print(f"   問題ID: {qid_match.group(1)}")
                
                # 進捗情報を抽出
                progress_match = re.search(r'(\d+)/(\d+)', response.text)
                if progress_match:
                    print(f"   進捗: {progress_match.group(1)}/{progress_match.group(2)}")
            
            elif "エラー" in response.text:
                print("   ❌ エラーページが表示されています")
            else:
                print("   ⚠️ 不明なページ形式")
        
        # セッション復旧テスト
        print("\n📋 ステップ5: セッション復旧テスト")
        # 新しいセッションで再試行
        new_session = requests.Session()
        response = new_session.get(f"{base_url}/exam?question_type=basic&count=10")
        print(f"   新セッション ステータス: {response.status_code}")
        
        if "エラー" not in response.text and 'name="qid"' in response.text:
            print("   ✅ 新セッションで正常動作")
        else:
            print("   ❌ 新セッションでも同じ問題")
        
        # データベース/ファイル確認テスト
        print("\n📋 ステップ6: データ確認テスト")
        # healthチェック
        response = session.get(f"{base_url}/health_simple")
        print(f"   ヘルスチェック: {response.status_code}")
        
        if response.status_code == 200:
            try:
                health_data = response.json()
                print(f"   ヘルス状態: {health_data}")
            except:
                print(f"   ヘルス応答: {response.text[:100]}")
        
        # 診断結果サマリー
        print("\n" + "=" * 60)
        print("🔍 【ULTRASYNC段階11】診断結果サマリー")
        print("=" * 60)
        
        diagnosis = {
            "timestamp": datetime.now().isoformat(),
            "home_page_access": "OK",
            "session_cookie_size": len(str(session.cookies.get_dict())),
            "exam_start_error": "エラー" in response.text,
            "health_check": "OK" if response.status_code == 200 else "NG"
        }
        
        # 詳細レポート保存
        report_filename = f"session_error_diagnosis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_filename, 'w', encoding='utf-8') as f:
            json.dump(diagnosis, f, ensure_ascii=False, indent=2)
        
        print(f"📋 診断レポート保存: {report_filename}")
        
        # 問題の特定
        if diagnosis["exam_start_error"]:
            print("\n🚨 問題特定: 試験開始時にエラーが発生")
            print("💡 推定原因:")
            print("   1. データファイルの読み込み問題")
            print("   2. セッション初期化の問題") 
            print("   3. 軽量セッション管理の実装問題")
            print("   4. 問題データの構造不整合")
        else:
            print("\n✅ 問題は特定の条件でのみ発生する可能性")
        
    except Exception as e:
        print(f"\n❌ 診断エラー: {e}")

if __name__ == "__main__":
    diagnose_session_error()