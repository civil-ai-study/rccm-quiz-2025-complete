#!/usr/bin/env python3
"""
データディレクトリパス問題の検証
CLAUDE.md準拠の徹底調査
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_data_dir_paths():
    """データディレクトリパスの問題を検証"""
    print("🔍 データディレクトリパス問題検証")
    print("=" * 60)
    
    try:
        from config import DataConfig
        
        print("1. 現在のapp.pyロジック検証")
        print("-" * 30)
        
        # app.pyの現在のロジック
        current_data_dir = os.path.dirname(DataConfig.QUESTIONS_CSV)
        print(f"DataConfig.QUESTIONS_CSV: {DataConfig.QUESTIONS_CSV}")
        print(f"app.py data_dir: {current_data_dir}")
        print(f"data_dir存在: {os.path.exists(current_data_dir)}")
        
        # ディレクトリ内容確認
        if os.path.exists(current_data_dir):
            files = os.listdir(current_data_dir)
            csv_files = [f for f in files if f.endswith('.csv')]
            print(f"data_dir内のCSVファイル: {len(csv_files)}個")
            print(f"CSVファイル例: {csv_files[:5]}")
        else:
            print("❌ data_dirが存在しません")
        
        print("\n2. 正しいパス検証")
        print("-" * 30)
        
        # 正しいパス（現在のディレクトリのdata）
        correct_data_dir = 'data'
        print(f"正しいdata_dir: {correct_data_dir}")
        print(f"正しいdata_dir存在: {os.path.exists(correct_data_dir)}")
        print(f"絶対パス: {os.path.abspath(correct_data_dir)}")
        
        if os.path.exists(correct_data_dir):
            files = os.listdir(correct_data_dir)
            csv_files = [f for f in files if f.endswith('.csv')]
            print(f"正しいdata_dir内のCSVファイル: {len(csv_files)}個")
            print(f"CSVファイル例: {csv_files[:5]}")
        
        print("\n3. utils.py読み込みテスト（正しいパス使用）")
        print("-" * 30)
        
        try:
            from utils import load_rccm_data_files
            questions = load_rccm_data_files(correct_data_dir)
            print(f"✅ 成功: 正しいパスで{len(questions)}問読み込み")
            
            basic_count = sum(1 for q in questions if q.get('question_type') == 'basic')
            specialist_count = sum(1 for q in questions if q.get('question_type') == 'specialist')
            print(f"   基礎科目: {basic_count}問")
            print(f"   専門科目: {specialist_count}問")
            
        except Exception as e:
            print(f"❌ 失敗: 正しいパスでも読み込みエラー - {e}")
        
        print("\n4. app.pyの現在パスでのテスト")
        print("-" * 30)
        
        try:
            from utils import load_rccm_data_files
            questions = load_rccm_data_files(current_data_dir)
            print(f"✅ 成功: app.pyパスで{len(questions)}問読み込み")
        except Exception as e:
            print(f"❌ 失敗: app.pyパスで読み込みエラー - {e}")
            print(f"   これが「処理中に問題が発生しました」の原因です")
        
        print("\n" + "=" * 60)
        print("🎯 結論:")
        if os.path.exists(correct_data_dir) and not os.path.exists(current_data_dir):
            print("❌ CRITICAL: app.pyのdata_dirパスが間違っています")
            print(f"修正必要: data_dir = '{correct_data_dir}'")
            return False
        else:
            print("✅ データディレクトリパスは正常")
            return True
            
    except Exception as e:
        print(f"❌ 検証エラー: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_data_dir_paths()