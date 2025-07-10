#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
【直接修正】基礎科目データ読み込みテスト
Flaskなしで基礎科目データの読み込みを直接テスト
"""

import sys
import os
import logging

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_basic_data_loading():
    """基礎科目データ読み込みテスト"""
    print("🔍 【直接修正】基礎科目データ読み込みテスト開始")
    print("=" * 60)
    
    try:
        # 1. 基本的なファイル存在確認
        print("1️⃣ ファイル存在確認...")
        data_file = "data/4-1.csv"
        
        if not os.path.exists(data_file):
            print(f"   ❌ {data_file} が見つかりません")
            return False
        
        print(f"   ✅ {data_file} 存在確認")
        
        # ファイルサイズ確認
        file_size = os.path.getsize(data_file)
        print(f"   ✅ ファイルサイズ: {file_size} bytes")
        
        # 2. CSVファイルの直接読み込みテスト
        print("2️⃣ CSVファイル直接読み込み...")
        
        # Python標準のcsvモジュールで読み込み
        import csv
        
        questions = []
        encodings_to_try = ['utf-8', 'shift_jis', 'cp932', 'utf-8-sig']
        
        for encoding in encodings_to_try:
            try:
                print(f"   - エンコーディング {encoding} で試行...")
                with open(data_file, 'r', encoding=encoding, errors='ignore') as f:
                    reader = csv.DictReader(f)
                    questions = list(reader)
                    print(f"   ✅ {encoding} で成功: {len(questions)}行読み込み")
                    break
            except Exception as e:
                print(f"   ❌ {encoding} 失敗: {e}")
                continue
        
        if not questions:
            print("   ❌ 全てのエンコーディングで読み込み失敗")
            return False
        
        # 3. データ構造確認
        print("3️⃣ データ構造確認...")
        
        if len(questions) > 0:
            first_question = questions[0]
            print(f"   ✅ 問題数: {len(questions)}問")
            print(f"   ✅ フィールド: {list(first_question.keys())}")
            
            # 必須フィールドの確認
            required_fields = ['id', 'question', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer']
            missing_fields = [field for field in required_fields if field not in first_question]
            
            if missing_fields:
                print(f"   ❌ 不足フィールド: {missing_fields}")
                return False
            
            print("   ✅ 必須フィールド確認完了")
            
            # サンプル問題表示
            print(f"   📋 サンプル問題:")
            print(f"      ID: {first_question.get('id', 'N/A')}")
            print(f"      問題: {first_question.get('question', 'N/A')[:50]}...")
            print(f"      正解: {first_question.get('correct_answer', 'N/A')}")
        
        # 4. utilsモジュールでの読み込みテスト
        print("4️⃣ utilsモジュール読み込みテスト...")
        
        try:
            # utilsモジュールの関数を直接テスト
            sys.path.append('.')  # カレントディレクトリをパスに追加
            
            # 一部の関数を個別にテスト
            print("   - utils.pyインポート...")
            from utils import load_basic_questions_only
            print("   ✅ utils.py正常インポート")
            
            print("   - load_basic_questions_only関数実行...")
            basic_questions = load_basic_questions_only('data')
            print(f"   ✅ 基礎科目読み込み完了: {len(basic_questions)}問")
            
            if len(basic_questions) > 0:
                sample_q = basic_questions[0]
                print(f"   📋 utils経由サンプル:")
                print(f"      question_type: {sample_q.get('question_type', 'N/A')}")
                print(f"      department: {sample_q.get('department', 'N/A')}")
                print(f"      category: {sample_q.get('category', 'N/A')}")
                
                return True
            else:
                print("   ❌ utils経由で問題データ0件")
                return False
            
        except ImportError as e:
            print(f"   ❌ utilsインポートエラー: {e}")
            print("   💡 utils.pyに依存関係の問題がある可能性")
            return False
            
        except Exception as e:
            print(f"   ❌ utils実行エラー: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    except Exception as e:
        print(f"❌ テスト実行エラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """メイン実行"""
    print("🎯 【直接修正】基礎科目データ読み込み問題の診断")
    print("📋 目標: データ読み込みが正常か、何が問題かを特定")
    
    success = test_basic_data_loading()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ データ読み込み成功: 基礎科目データは正常")
        print("📋 結果: データ読み込み部分に問題なし")
        print("💡 次のステップ: Flask app内での処理を確認")
    else:
        print("❌ データ読み込み失敗: 問題を発見")
        print("📋 次のステップ: 上記エラー内容に基づいて修正")
        print("💡 対策: データファイルまたはutils.pyの修正が必要")

if __name__ == "__main__":
    main()