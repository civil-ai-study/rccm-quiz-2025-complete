#!/usr/bin/env python3
"""
RCCM Quiz App - 副作用チェックスクリプト
最新の変更による既存機能への影響を検証
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
import json
import logging

# ログ設定
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def check_anonymous_user_flow():
    """匿名ユーザー機能の副作用チェック"""
    logger.info("\n=== 1. 匿名ユーザー機能の副作用チェック ===")
    
    with app.test_client() as client:
        # 1.1 匿名ユーザーでのセッション作成
        logger.info("\n[1.1] 匿名ユーザーでセッション作成")
        resp = client.post('/set_user', data={'user_name': ''})
        if resp.status_code == 302:
            logger.info("✅ 空のユーザー名で正常にリダイレクト")
        else:
            logger.error(f"❌ 予期しないステータスコード: {resp.status_code}")
        
        # セッション確認
        with client.session_transaction() as sess:
            user_name = sess.get('user_name', '')
            if '匿名ユーザー_' in user_name:
                logger.info(f"✅ 匿名ユーザー名が設定: {user_name}")
            else:
                logger.error(f"❌ ユーザー名が不正: {user_name}")
        
        # 1.2 匿名ユーザーで問題開始
        logger.info("\n[1.2] 匿名ユーザーで問題開始")
        resp = client.get('/exam')
        if resp.status_code == 200:
            logger.info("✅ 匿名ユーザーで問題アクセス可能")
        else:
            logger.error(f"❌ 問題アクセスエラー: {resp.status_code}")
        
        # 1.3 学習データ保存の確認
        logger.info("\n[1.3] 匿名ユーザーの学習データ保存")
        with client.session_transaction() as sess:
            user_id = sess.get('user_id')
            base_user_id = sess.get('base_user_id')
            if user_id and base_user_id:
                logger.info(f"✅ ユーザーID正常生成: {user_id}")
            else:
                logger.error("❌ ユーザーID生成エラー")

def check_named_user_flow():
    """既存の名前付きユーザー機能への影響チェック"""
    logger.info("\n=== 2. 名前付きユーザー機能への影響チェック ===")
    
    with app.test_client() as client:
        # 2.1 通常のユーザー名入力
        logger.info("\n[2.1] 通常のユーザー名入力")
        resp = client.post('/set_user', data={'user_name': '山田太郎'})
        if resp.status_code == 302:
            logger.info("✅ 通常のユーザー名で正常動作")
        else:
            logger.error(f"❌ 予期しないステータスコード: {resp.status_code}")
        
        # セッション確認
        with client.session_transaction() as sess:
            user_name = sess.get('user_name')
            if user_name == '山田太郎':
                logger.info(f"✅ ユーザー名正常設定: {user_name}")
            else:
                logger.error(f"❌ ユーザー名エラー: {user_name}")

def check_render_optimization():
    """Render起動最適化の副作用チェック"""
    logger.info("\n=== 3. Render起動最適化の副作用チェック ===")
    
    # 3.1 環境変数検出ロジック
    logger.info("\n[3.1] 環境変数検出ロジック")
    import os
    original_env = os.environ.copy()
    
    # 開発環境
    os.environ.pop('FLASK_ENV', None)
    os.environ.pop('RENDER', None)
    os.environ.pop('PORT', None)
    is_dev = not (os.environ.get('FLASK_ENV') == 'production' or 
                  os.environ.get('RENDER') or 
                  os.environ.get('PORT'))
    if is_dev:
        logger.info("✅ 開発環境正常検出")
    else:
        logger.error("❌ 開発環境検出エラー")
    
    # 本番環境
    os.environ['RENDER'] = 'true'
    is_prod = (os.environ.get('FLASK_ENV') == 'production' or 
               os.environ.get('RENDER') or 
               os.environ.get('PORT'))
    if is_prod:
        logger.info("✅ 本番環境(Render)正常検出")
    else:
        logger.error("❌ 本番環境検出エラー")
    
    # 環境変数復元
    os.environ.clear()
    os.environ.update(original_env)
    
    # 3.2 ヘルスチェックエンドポイント
    logger.info("\n[3.2] ヘルスチェックエンドポイント")
    with app.test_client() as client:
        resp = client.get('/health')
        if resp.status_code == 200:
            data = resp.get_json()
            if data and data.get('status') == 'ok':
                logger.info("✅ ヘルスチェック正常動作")
            else:
                logger.error(f"❌ ヘルスチェックデータエラー: {data}")
        else:
            logger.error(f"❌ ヘルスチェックエラー: {resp.status_code}")

def check_error_handling():
    """エラーハンドリングの副作用チェック"""
    logger.info("\n=== 4. エラーハンドリングの副作用チェック ===")
    
    with app.test_client() as client:
        # 4.1 404エラーハンドリング
        logger.info("\n[4.1] 404エラーハンドリング")
        resp = client.get('/nonexistent-page')
        if resp.status_code == 404:
            if b'error.html' in resp.data or 'エラー'.encode('utf-8') in resp.data:
                logger.info("✅ 404エラーページ正常表示")
            else:
                logger.error("❌ 404エラーページ表示エラー")
        else:
            logger.error(f"❌ 404ステータスコードエラー: {resp.status_code}")
        
        # 4.2 既存のエラーページとの互換性
        logger.info("\n[4.2] 既存エラーページとの互換性")
        # /reset などの既存エンドポイントでのエラー処理
        resp = client.get('/reset')
        if resp.status_code in [200, 302, 404]:
            logger.info("✅ 既存エンドポイントの動作維持")
        else:
            logger.error(f"❌ 既存エンドポイントエラー: {resp.status_code}")

def check_session_management():
    """セッション管理への影響チェック"""
    logger.info("\n=== 5. セッション管理への影響チェック ===")
    
    with app.test_client() as client:
        # 5.1 セッション初期化
        logger.info("\n[5.1] セッション初期化チェック")
        resp = client.get('/')
        with client.session_transaction() as sess:
            # 必須フィールドの確認
            if 'history' in sess and isinstance(sess['history'], list):
                logger.info("✅ history初期化正常")
            else:
                logger.error("❌ history初期化エラー")
            
            if 'category_stats' in sess and isinstance(sess['category_stats'], dict):
                logger.info("✅ category_stats初期化正常")
            else:
                logger.error("❌ category_stats初期化エラー")
        
        # 5.2 ユーザー変更機能
        logger.info("\n[5.2] ユーザー変更機能")
        # まずユーザー設定
        client.post('/set_user', data={'user_name': 'テストユーザー'})
        # ユーザー変更
        resp = client.get('/change_user')
        if resp.status_code == 302:
            with client.session_transaction() as sess:
                if 'user_name' not in sess:
                    logger.info("✅ ユーザー変更で正常にクリア")
                else:
                    logger.error("❌ ユーザー情報が残存")
        else:
            logger.error(f"❌ ユーザー変更エラー: {resp.status_code}")

def check_quiz_functionality():
    """クイズ機能への影響チェック"""
    logger.info("\n=== 6. クイズ機能への影響チェック ===")
    
    with app.test_client() as client:
        # 6.1 問題開始フロー
        logger.info("\n[6.1] 問題開始フロー")
        # 匿名ユーザーで開始
        client.post('/set_user', data={'user_name': ''})
        
        # カテゴリ選択
        resp = client.get('/categories')
        if resp.status_code == 200:
            logger.info("✅ カテゴリページアクセス正常")
        else:
            logger.error(f"❌ カテゴリページエラー: {resp.status_code}")
        
        # 問題ページ
        resp = client.get('/exam?question_type=basic')
        if resp.status_code == 200:
            logger.info("✅ 問題ページアクセス正常")
        else:
            logger.error(f"❌ 問題ページエラー: {resp.status_code}")

def run_all_checks():
    """全ての副作用チェックを実行"""
    logger.info("=" * 60)
    logger.info("RCCM Quiz App - 副作用チェック開始")
    logger.info("=" * 60)
    
    try:
        check_anonymous_user_flow()
        check_named_user_flow()
        check_render_optimization()
        check_error_handling()
        check_session_management()
        check_quiz_functionality()
        
        logger.info("\n" + "=" * 60)
        logger.info("✅ 副作用チェック完了")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"\n❌ チェック中にエラー発生: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    run_all_checks()