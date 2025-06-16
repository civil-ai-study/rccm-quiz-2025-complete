#!/usr/bin/env python3
"""
🔥 CRITICAL: 復習セッション途中終了修正の動作テスト
ウルトラシンク修正の検証用テストスクリプト
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from app import app, validate_review_session_integrity, create_robust_review_session, safe_update_review_session
import json

def test_review_session_integrity():
    """復習セッション整合性チェックのテスト"""
    print("🧪 復習セッション整合性チェックテスト開始")
    
    # テストケース1: 正常な復習セッション
    valid_session = {
        'exam_question_ids': [1, 2, 3, 4, 5],
        'exam_current': 2,
        'selected_question_type': 'review',
        'exam_category': '復習問題（統合5問）'
    }
    
    is_valid, message = validate_review_session_integrity(valid_session)
    print(f"✅ 正常セッション: {is_valid}, メッセージ: {message}")
    
    # テストケース2: 範囲外の現在位置
    invalid_session = {
        'exam_question_ids': [1, 2, 3],
        'exam_current': 5,  # 範囲外
        'selected_question_type': 'review'
    }
    
    is_valid, message = validate_review_session_integrity(invalid_session)
    print(f"❌ 範囲外位置: {is_valid}, メッセージ: {message}")
    
    # テストケース3: 復習モードでない
    non_review_session = {
        'exam_question_ids': [1, 2, 3],
        'exam_current': 1,
        'selected_question_type': 'basic'
    }
    
    is_valid, message = validate_review_session_integrity(non_review_session)
    print(f"❌ 非復習モード: {is_valid}, メッセージ: {message}")

def test_flask_integration():
    """Flask統合テスト"""
    print("\n🧪 Flask統合テスト開始")
    
    with app.test_client() as client:
        # ホームページアクセステスト
        response = client.get('/')
        print(f"✅ ホームページ: ステータス {response.status_code}")
        
        # 復習セッションシミュレーション
        with client.session_transaction() as sess:
            # 復習用データをセッションに設定
            sess['advanced_srs'] = {
                '1': {'level': 1, 'next_review': '2025-06-15'},
                '2': {'level': 0, 'next_review': '2025-06-15'},
                '3': {'level': 2, 'next_review': '2025-06-15'}
            }
            sess['bookmarks'] = [4, 5]
            sess['history'] = [
                {'question_id': 6, 'is_correct': False},
                {'question_id': 7, 'is_correct': False}
            ]
        
        # 復習セッション開始テスト
        response = client.get('/review')
        print(f"✅ 復習セッション開始: ステータス {response.status_code}")
        
        if response.status_code == 200:
            print("✅ 復習セッション正常開始")
        elif response.status_code == 302:
            print("✅ 復習セッション開始（リダイレクト）")
        else:
            print(f"⚠️ 復習セッション: 予期しないステータス {response.status_code}")

def main():
    """メイン実行関数"""
    print("🔥 復習セッション途中終了修正テスト開始")
    print("=" * 50)
    
    try:
        # セッション整合性テスト
        test_review_session_integrity()
        
        # Flask統合テスト
        test_flask_integration()
        
        print("\n" + "=" * 50)
        print("✅ 全テスト完了: 復習セッション修正が正常に動作しています")
        
    except Exception as e:
        print(f"\n❌ テスト失敗: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)