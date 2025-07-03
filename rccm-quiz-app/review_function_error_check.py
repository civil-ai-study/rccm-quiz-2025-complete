#!/usr/bin/env python3
"""
復習機能エラーチェックテスト
現在実装されている機能の動作確認
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta

# ログ設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_app_structure():
    """アプリケーションファイル構造確認"""
    logger.info("🔍 アプリケーション構造確認開始")
    
    required_files = [
        'app.py',
        'config.py',
        'utils.py',
        'requirements.txt'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        logger.error(f"❌ 必要なファイルが見つかりません: {missing_files}")
        return False
    
    logger.info("✅ 必要なファイルが確認されました")
    return True

def check_bookmark_functionality():
    """ブックマーク機能テスト"""
    logger.info("📚 ブックマーク機能確認開始")
    
    try:
        # app.pyからブックマーク関連のルートを確認
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # ブックマーク関連のルート確認
        bookmark_routes = [
            '@app.route(\'/api/bookmark\'',
            '@app.route(\'/api/bookmarks\'',
            '@app.route(\'/bookmark\'',
            '@app.route(\'/bookmarks\')'
        ]
        
        found_routes = []
        for route in bookmark_routes:
            if route in content:
                found_routes.append(route)
        
        logger.info(f"✅ ブックマークルート確認: {len(found_routes)}/4 件発見")
        for route in found_routes:
            logger.info(f"  - {route}")
        
        if len(found_routes) < 3:
            logger.warning("⚠️ ブックマーク機能が不完全な可能性があります")
            return False
            
        return True
        
    except Exception as e:
        logger.error(f"❌ ブックマーク機能確認エラー: {e}")
        return False

def check_srs_configuration():
    """SRS設定確認"""
    logger.info("🔄 SRS設定確認開始")
    
    try:
        # config.pyからSRS設定を確認
        with open('config.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # SRS関連の設定確認
        srs_checks = [
            'class SRSConfig',
            'INTERVALS',
            'MAX_REVIEW_RATIO'
        ]
        
        found_configs = []
        for check in srs_checks:
            if check in content:
                found_configs.append(check)
        
        logger.info(f"✅ SRS設定確認: {len(found_configs)}/3 件発見")
        for config in found_configs:
            logger.info(f"  - {config}")
        
        # 間隔設定の詳細確認
        if 'INTERVALS' in content:
            intervals_start = content.find('INTERVALS = {')
            if intervals_start != -1:
                intervals_end = content.find('}', intervals_start)
                intervals_content = content[intervals_start:intervals_end+1]
                logger.info(f"📊 間隔設定詳細: {intervals_content[:100]}...")
        
        return len(found_configs) >= 2
        
    except Exception as e:
        logger.error(f"❌ SRS設定確認エラー: {e}")
        return False

def check_review_data_structure():
    """復習データ構造確認"""
    logger.info("💾 復習データ構造確認開始")
    
    try:
        # user_dataディレクトリの確認
        if os.path.exists('user_data'):
            logger.info("✅ user_dataディレクトリが存在します")
            
            # サンプルユーザーデータファイルがあるか確認
            user_files = [f for f in os.listdir('user_data') if f.endswith('.json')]
            logger.info(f"📊 ユーザーデータファイル数: {len(user_files)}")
            
            # サンプルファイルの中身を確認
            if user_files:
                sample_file = user_files[0]
                with open(f'user_data/{sample_file}', 'r', encoding='utf-8') as f:
                    sample_data = json.load(f)
                
                # 復習関連フィールドの確認
                review_fields = ['srs_data', 'bookmarks', 'last_review']
                found_fields = []
                for field in review_fields:
                    if field in sample_data:
                        found_fields.append(field)
                
                logger.info(f"✅ 復習データフィールド: {len(found_fields)}/{len(review_fields)}")
                for field in found_fields:
                    logger.info(f"  - {field}: {type(sample_data[field])}")
                
                return len(found_fields) > 0
        else:
            logger.warning("⚠️ user_dataディレクトリが存在しません")
            return False
        
    except Exception as e:
        logger.error(f"❌ 復習データ構造確認エラー: {e}")
        return False

def check_question_data_availability():
    """問題データ利用可能性確認"""
    logger.info("📋 問題データ確認開始")
    
    try:
        data_dir = 'data'
        if not os.path.exists(data_dir):
            logger.error("❌ dataディレクトリが存在しません")
            return False
        
        # CSV ファイルの確認
        csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
        logger.info(f"📊 CSVファイル数: {len(csv_files)}")
        
        if len(csv_files) == 0:
            logger.error("❌ 問題データファイルが見つかりません")
            return False
        
        # 各ファイルの基本情報確認
        for csv_file in csv_files[:5]:  # 最初の5ファイルのみ確認
            file_path = os.path.join(data_dir, csv_file)
            file_size = os.path.getsize(file_path)
            logger.info(f"  - {csv_file}: {file_size} bytes")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 問題データ確認エラー: {e}")
        return False

def check_cache_initialization():
    """キャッシュ初期化状況確認"""
    logger.info("⚡ キャッシュ初期化確認開始")
    
    try:
        # app.pyからキャッシュ関連のコードを確認
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        cache_checks = [
            'cache_manager',
            'init_cache',
            'REDIS_CACHE_INTEGRATION',
            'メモリキャッシュフォールバック'
        ]
        
        found_cache = []
        for check in cache_checks:
            if check in content:
                found_cache.append(check)
        
        logger.info(f"✅ キャッシュ関連コード: {len(found_cache)}/4 件発見")
        for item in found_cache:
            logger.info(f"  - {item}")
        
        # redis_cache.pyの存在確認
        if os.path.exists('redis_cache.py'):
            logger.info("✅ redis_cache.py ファイルが存在します")
            
            with open('redis_cache.py', 'r', encoding='utf-8') as f:
                redis_content = f.read()
            
            if 'RedisCacheManager' in redis_content:
                logger.info("✅ RedisCacheManager クラスが実装されています")
            
        return len(found_cache) >= 2
        
    except Exception as e:
        logger.error(f"❌ キャッシュ初期化確認エラー: {e}")
        return False

def simulate_review_functionality():
    """復習機能シミュレーション"""
    logger.info("🎮 復習機能シミュレーション開始")
    
    try:
        # 模擬的なSRSデータ作成
        mock_srs_data = {
            "q_001": {
                "level": 2,
                "last_review": (datetime.now() - timedelta(days=7)).isoformat(),
                "next_review": datetime.now().isoformat(),
                "correct_count": 2,
                "incorrect_count": 1
            },
            "q_002": {
                "level": 0,
                "last_review": (datetime.now() - timedelta(days=1)).isoformat(),
                "next_review": datetime.now().isoformat(),
                "correct_count": 0,
                "incorrect_count": 2
            }
        }
        
        logger.info("✅ 模擬SRSデータ作成完了")
        logger.info(f"📊 復習対象問題数: {len(mock_srs_data)}")
        
        # 復習スケジュール計算テスト
        current_time = datetime.now()
        due_questions = []
        
        for q_id, data in mock_srs_data.items():
            next_review = datetime.fromisoformat(data['next_review'])
            if next_review <= current_time:
                due_questions.append(q_id)
        
        logger.info(f"✅ 復習期限到来問題: {len(due_questions)}")
        for q_id in due_questions:
            logger.info(f"  - {q_id}: レベル{mock_srs_data[q_id]['level']}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 復習機能シミュレーションエラー: {e}")
        return False

def run_comprehensive_review_check():
    """総合復習機能チェック実行"""
    logger.info("🚀 総合復習機能チェック開始")
    
    checks = [
        ("アプリケーション構造", check_app_structure),
        ("ブックマーク機能", check_bookmark_functionality),
        ("SRS設定", check_srs_configuration),
        ("復習データ構造", check_review_data_structure),
        ("問題データ", check_question_data_availability),
        ("キャッシュ初期化", check_cache_initialization),
        ("復習機能シミュレーション", simulate_review_functionality)
    ]
    
    results = {}
    total_checks = len(checks)
    passed_checks = 0
    
    logger.info(f"📋 実行予定チェック数: {total_checks}")
    
    for check_name, check_function in checks:
        logger.info(f"\n📊 {check_name} チェック実行中...")
        try:
            result = check_function()
            results[check_name] = result
            if result:
                passed_checks += 1
                logger.info(f"✅ {check_name}: 合格")
            else:
                logger.warning(f"⚠️ {check_name}: 要改善")
        except Exception as e:
            logger.error(f"❌ {check_name}: エラー - {e}")
            results[check_name] = False
    
    # 最終結果レポート
    logger.info("\n" + "="*60)
    logger.info("📊 復習機能エラーチェック 最終結果")
    logger.info("="*60)
    
    success_rate = (passed_checks / total_checks) * 100
    logger.info(f"📈 総合合格率: {passed_checks}/{total_checks} ({success_rate:.1f}%)")
    
    for check_name, result in results.items():
        status = "✅ 合格" if result else "❌ 不合格"
        logger.info(f"  {check_name}: {status}")
    
    # 推奨アクション
    logger.info("\n🎯 推奨アクション:")
    if success_rate >= 80:
        logger.info("✅ 復習機能は基本的に正常に実装されています")
        if success_rate < 100:
            logger.info("💡 軽微な改善を行うことで品質向上が可能です")
    elif success_rate >= 60:
        logger.info("⚠️ 復習機能に改善が必要な部分があります")
        logger.info("🔧 優先的に対処すべき問題があります")
    else:
        logger.info("❌ 復習機能に重大な問題があります")
        logger.info("🚨 緊急対処が必要です")
    
    # 不合格項目の詳細
    failed_checks = [name for name, result in results.items() if not result]
    if failed_checks:
        logger.info(f"\n🔧 要改善項目 ({len(failed_checks)}件):")
        for item in failed_checks:
            logger.info(f"  - {item}")
    
    return success_rate >= 80

if __name__ == "__main__":
    logger.info("🔥 復習機能エラーチェックテスト開始")
    logger.info(f"⏰ 開始時刻: {datetime.now()}")
    
    success = run_comprehensive_review_check()
    
    logger.info(f"\n⏰ 完了時刻: {datetime.now()}")
    
    if success:
        logger.info("🎉 復習機能エラーチェック完了: 正常")
        sys.exit(0)
    else:
        logger.info("⚠️ 復習機能エラーチェック完了: 要改善")
        sys.exit(1)