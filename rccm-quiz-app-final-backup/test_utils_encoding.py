#!/usr/bin/env python3
"""
utils.pyのエンコーディング検出をテスト
副作用なしでutils.pyの動作を確認
"""

import sys
import os

# 現在のディレクトリをパスに追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_utils_encoding():
    """utils.pyのエンコーディング検出テスト"""
    print("🔍 utils.py エンコーディング検出テスト")
    print("=" * 50)
    
    try:
        # utils.pyをインポート
        from utils import load_questions_improved
        print("✅ utils.py インポート成功")
        
        # 基礎科目読み込みテスト
        print("\n1. 基礎科目(4-1.csv)読み込みテスト...")
        try:
            basic_questions = load_questions_improved('data/4-1.csv')
            print(f"✅ 成功: 基礎科目 {len(basic_questions)}問読み込み")
            if basic_questions:
                sample = basic_questions[0]
                print(f"   サンプル問題ID: {sample.get('id')}")
                print(f"   カテゴリ: {sample.get('category')}")
        except Exception as e:
            print(f"❌ 失敗: 基礎科目読み込みエラー - {e}")
            import traceback
            traceback.print_exc()
        
        # 専門科目読み込みテスト
        print("\n2. 専門科目(4-2_2019.csv)読み込みテスト...")
        try:
            specialist_questions = load_questions_improved('data/4-2_2019.csv')
            print(f"✅ 成功: 専門科目 {len(specialist_questions)}問読み込み")
            if specialist_questions:
                sample = specialist_questions[0]
                print(f"   サンプル問題ID: {sample.get('id')}")
                print(f"   カテゴリ: {sample.get('category')}")
        except Exception as e:
            print(f"❌ 失敗: 専門科目読み込みエラー - {e}")
            import traceback
            traceback.print_exc()
        
        # 統合読み込みテスト
        print("\n3. 統合読み込み(load_rccm_data_files)テスト...")
        try:
            from utils import load_rccm_data_files
            all_questions = load_rccm_data_files('data')
            print(f"✅ 成功: 統合読み込み {len(all_questions)}問")
            
            basic_count = sum(1 for q in all_questions if q.get('question_type') == 'basic')
            specialist_count = sum(1 for q in all_questions if q.get('question_type') == 'specialist')
            print(f"   基礎科目: {basic_count}問")
            print(f"   専門科目: {specialist_count}問")
            
        except Exception as e:
            print(f"❌ 失敗: 統合読み込みエラー - {e}")
            import traceback
            traceback.print_exc()
    
    except ImportError as e:
        print(f"❌ utils.py インポートエラー: {e}")
        return False
    except Exception as e:
        print(f"❌ 予期しないエラー: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 50)
    print("🎯 テスト完了")

if __name__ == "__main__":
    test_utils_encoding()