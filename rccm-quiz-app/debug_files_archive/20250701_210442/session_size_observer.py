#!/usr/bin/env python3
"""
🔍 get_user_session_size()観察デバッグ - 専門家推奨手法
Flask専門家推奨：既存機能肯定→観察型テスト→問題特定
"""

import sys
import os

# Add the current directory to Python path for imports
sys.path.insert(0, '/mnt/c/Users/z285/Desktop/rccm-quiz-app/rccm-quiz-app')

def observe_get_user_session_size():
    """get_user_session_size()関数の観察型デバッグ"""
    print("🔍 get_user_session_size()観察デバッグ開始")
    print("専門家推奨：既存機能肯定→観察型テスト")
    print("=" * 60)
    
    try:
        # Import the app and function
        from app import app, get_user_session_size
        
        print("✅ アプリとget_user_session_size関数インポート成功")
        
        # Create test app context
        with app.app_context():
            with app.test_client() as client:
                
                # Test scenarios - 専門家推奨：session_transaction使用
                test_scenarios = [
                    {"name": "空セッション", "session_data": {}},
                    {"name": "デフォルト設定なし", "session_data": {"other_data": "test"}},
                    {"name": "10問設定", "session_data": {"quiz_settings": {"questions_per_session": 10}}},
                    {"name": "20問設定", "session_data": {"quiz_settings": {"questions_per_session": 20}}},
                    {"name": "30問設定", "session_data": {"quiz_settings": {"questions_per_session": 30}}},
                    {"name": "無効値設定", "session_data": {"quiz_settings": {"questions_per_session": "invalid"}}},
                    {"name": "範囲外値設定", "session_data": {"quiz_settings": {"questions_per_session": 999}}},
                ]
                
                print(f"\n📋 テストシナリオ数: {len(test_scenarios)}")
                
                for i, scenario in enumerate(test_scenarios, 1):
                    print(f"\n🔍 シナリオ {i}: {scenario['name']}")
                    print("-" * 40)
                    
                    # 専門家推奨：session_transaction使用でセッション設定
                    with client.session_transaction() as test_session:
                        # セッションをクリア
                        test_session.clear()
                        
                        # テストデータを設定
                        for key, value in scenario['session_data'].items():
                            test_session[key] = value
                        
                        print(f"  📝 セッション設定: {dict(test_session)}")
                        
                        # get_user_session_size()を観察
                        try:
                            result = get_user_session_size(test_session)
                            print(f"  ✅ get_user_session_size() 結果: {result}")
                            
                            # 結果の妥当性確認
                            if result in [10, 20, 30]:
                                print(f"  ✅ 妥当な値: {result}")
                            elif result == 10:  # デフォルト値
                                print(f"  📋 デフォルト値: {result}")
                            else:
                                print(f"  ⚠️ 予期しない値: {result}")
                                
                        except Exception as func_error:
                            print(f"  ❌ 関数実行エラー: {func_error}")
                
                # 実際のWebリクエストでの動作確認
                print(f"\n🌐 実際のWebリクエストでの動作確認")
                print("-" * 40)
                
                # 設定ページでの問題数設定
                for question_count in [10, 20, 30]:
                    print(f"\n  🔍 {question_count}問設定テスト")
                    
                    # 設定ページにPOST
                    response = client.post('/settings', 
                                         data={'questions_per_session': question_count})
                    
                    print(f"    POST /settings: {response.status_code}")
                    
                    # セッション内容確認（専門家推奨：print(session)）
                    with client.session_transaction() as session:
                        print(f"    セッション内容: {dict(session)}")
                        
                        # get_user_session_size()の結果確認
                        try:
                            size_result = get_user_session_size(session)
                            print(f"    get_user_session_size(): {size_result}")
                            
                            if size_result == question_count:
                                print(f"    ✅ 期待値一致: {size_result}")
                            else:
                                print(f"    ❌ 期待値不一致: 期待{question_count}, 実際{size_result}")
                                
                        except Exception as e:
                            print(f"    ❌ 関数エラー: {e}")
                
    except ImportError as e:
        print(f"❌ インポートエラー: {e}")
        print("アプリの起動が必要な可能性があります")
    except Exception as e:
        print(f"❌ 予期しないエラー: {e}")
    
    print(f"\n" + "=" * 60)
    print("✅ get_user_session_size()観察デバッグ完了")
    print("\n📊 観察結果:")
    print("  - 既存機能維持: コード変更なし")
    print("  - 専門家手法: session_transaction()使用")
    print("  - Flask推奨: print(session)でセッション内容確認")

if __name__ == "__main__":
    observe_get_user_session_size()