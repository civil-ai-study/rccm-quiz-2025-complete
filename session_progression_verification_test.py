#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Ultra Simple Deep Search: セッション継続システム実証テスト
目的: 道路部門で1問→2問→3問と実際に進捗するかFlask test clientで厳密検証
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'rccm-quiz-app'))

from app import app
import re

def session_progression_verification_test():
    """Ultra Simple Deep Search: セッション継続システム実証テスト"""
    print("=== Ultra Simple Deep Search: Session Progression Verification Test ===")
    
    with app.test_client() as client:
        # ステップ1: 道路部門のセッション開始
        print("\n1. 道路部門セッション開始テスト")
        response = client.get('/departments/road/start?mode=random&count=10')
        
        if response.status_code != 200:
            print(f"❌ セッション開始失敗: status={response.status_code}")
            return False
        
        # 1問目のページか確認
        html = response.get_data(as_text=True)
        if '問題 1/10' in html or '1/10' in html:
            print("✅ 1問目表示成功: 進捗表示「1/10」確認")
        else:
            print("❌ 1問目表示失敗: 進捗表示が見つからない")
            print("レスポンス内容（最初の200文字）:", html[:200])
            return False
        
        # 1問目の問題IDを抽出
        qid_match = re.search(r'name="qid"\s+value="([^"]+)"', html)
        if not qid_match:
            print("❌ 問題ID抽出失敗")
            return False
        
        qid1 = qid_match.group(1)
        print(f"✅ 1問目問題ID: {qid1}")
        
        # ステップ2: 1問目回答送信
        print("\n2. 1問目回答送信テスト")
        answer_data = {
            'qid': qid1,
            'answer': 'A',
            'elapsed': '30.5'
        }
        
        post_response = client.post('/exam', data=answer_data)
        
        if post_response.status_code != 200:
            print(f"❌ 1問目回答送信失敗: status={post_response.status_code}")
            return False
        
        post_html = post_response.get_data(as_text=True)
        
        # フィードバック画面から「次の問題へ (2/10)」ボタン確認
        if '次の問題へ (2/10)' in post_html or '2/10' in post_html:
            print("✅ 1問目回答処理成功: 「次の問題へ (2/10)」ボタン確認")
        else:
            print("❌ 1問目回答処理失敗: 2/10進捗表示が見つからない")
            print("フィードバック内容（最初の300文字）:", post_html[:300])
            return False
        
        # ステップ3: 2問目への遷移
        print("\n3. 2問目遷移テスト")
        
        # 次の問題へのリンクを探す
        next_link_match = re.search(r'href="([^"]*exam[^"]*)"', post_html)
        if not next_link_match:
            print("❌ 次の問題リンク抽出失敗")
            return False
        
        next_url = next_link_match.group(1)
        print(f"✅ 次の問題URL: {next_url}")
        
        # 2問目にアクセス
        response2 = client.get(next_url)
        
        if response2.status_code != 200:
            print(f"❌ 2問目アクセス失敗: status={response2.status_code}")
            return False
        
        html2 = response2.get_data(as_text=True)
        
        # 2問目の進捗確認
        if '問題 2/10' in html2 or '2/10' in html2:
            print("✅ 2問目表示成功: 進捗表示「2/10」確認")
        else:
            print("❌ 2問目表示失敗: 進捗表示「2/10」が見つからない")
            print("2問目内容（最初の200文字）:", html2[:200])
            return False
        
        # 2問目の問題ID抽出
        qid2_match = re.search(r'name="qid"\s+value="([^"]+)"', html2)
        if not qid2_match:
            print("❌ 2問目問題ID抽出失敗")
            return False
        
        qid2 = qid2_match.group(1)
        print(f"✅ 2問目問題ID: {qid2}")
        
        # ステップ4: 2問目回答送信
        print("\n4. 2問目回答送信テスト")
        answer_data2 = {
            'qid': qid2,
            'answer': 'B',
            'elapsed': '25.0'
        }
        
        post_response2 = client.post('/exam', data=answer_data2)
        
        if post_response2.status_code != 200:
            print(f"❌ 2問目回答送信失敗: status={post_response2.status_code}")
            return False
        
        post_html2 = post_response2.get_data(as_text=True)
        
        # 3問目への進捗確認
        if '次の問題へ (3/10)' in post_html2 or '3/10' in post_html2:
            print("✅ 2問目回答処理成功: 「次の問題へ (3/10)」ボタン確認")
        else:
            print("❌ 2問目回答処理失敗: 3/10進捗表示が見つからない")
            print("2問目フィードバック内容（最初の300文字）:", post_html2[:300])
            return False
        
        # ステップ5: 3問目への遷移テスト
        print("\n5. 3問目遷移テスト")
        
        next_link_match2 = re.search(r'href="([^"]*exam[^"]*)"', post_html2)
        if not next_link_match2:
            print("❌ 3問目リンク抽出失敗")
            return False
        
        next_url2 = next_link_match2.group(1)
        response3 = client.get(next_url2)
        
        if response3.status_code != 200:
            print(f"❌ 3問目アクセス失敗: status={response3.status_code}")
            return False
        
        html3 = response3.get_data(as_text=True)
        
        if '問題 3/10' in html3 or '3/10' in html3:
            print("✅ 3問目表示成功: 進捗表示「3/10」確認")
            print("🎉 セッション継続システム動作確認完了！")
            
            # 分野混在チェック
            if '道路' in html3:
                print("✅ 分野確認: 道路部門問題が正しく表示されている")
            else:
                print("⚠️ 分野混在の可能性: 道路以外の問題が表示されている可能性")
            
            return True
        else:
            print("❌ 3問目表示失敗: 進捗表示「3/10」が見つからない")
            print("3問目内容（最初の200文字）:", html3[:200])
            return False

if __name__ == "__main__":
    success = session_progression_verification_test()
    if success:
        print("\n🎯 【セッション継続システムの根本修正】タスク完了")
        print("✅ exam_currentの増分動作が正常に機能している")
        print("✅ Progress表示が1/10→2/10→3/10と正しく更新されている")
        print("✅ 次のタスク（道路部門10問完走テスト）に進む準備完了")
    else:
        print("\n❌ セッション継続システムに問題があります")
        print("詳細調査と修正が必要です")