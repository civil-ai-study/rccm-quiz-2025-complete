# data_check.py - データ整合性確認スクリプト
import csv
import os
import glob

def validate_questions_data():
    """問題データの整合性を確認"""
    data_dir = 'data'
    
    if not os.path.exists(data_dir):
        print("❌ dataディレクトリが見つかりません")
        return False
    
    # 新形式のファイル構造確認
    basic_file = 'data/4-1.csv'
    specialist_files = glob.glob('data/4-2_*.csv')
    
    if not os.path.exists(basic_file):
        print("❌ 4-1.csv（基礎科目）が見つかりません")
        return False
    
    if not specialist_files:
        print("❌ 4-2_*.csv（専門科目）が見つかりません")
        return False
    
    print(f"✅ 基礎科目ファイル: {basic_file}")
    print(f"✅ 専門科目ファイル: {len(specialist_files)}個")
    
    all_files = [basic_file] + specialist_files
    total_questions = 0
    all_categories = set()
    all_ids = []
    
    try:
        # 各ファイルを検証
        for file_path in all_files:
            print(f"\n📁 検証中: {file_path}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            
            print(f"✅ CSVファイル読み込み成功: {len(rows)}行")
            total_questions += len(rows)
            
            # 必要列の確認
            required_columns = ['id', 'category', 'question', 'option_a', 'option_b', 
                              'option_c', 'option_d', 'correct_answer', 'explanation']
            
            if rows:
                columns = list(rows[0].keys())
            else:
                columns = []
            missing_columns = [col for col in required_columns if col not in columns]
            if missing_columns:
                print(f"❌ 不足している列: {missing_columns}")
                return False
            
            print("✅ 必要な列がすべて存在します")
            
            # データ内容の確認
            category_counts = {}
            for row in rows:
                category = row.get('category', '不明')
                category_counts[category] = category_counts.get(category, 0) + 1
                all_categories.add(category)
                all_ids.append(row.get('id', ''))
                
                # 正解選択肢の確認
                correct_answer = row.get('correct_answer', '')
                if correct_answer not in ['A', 'B', 'C', 'D', 'a', 'b', 'c', 'd']:
                    print(f"❌ 無効な正解選択肢: ID {row.get('id')} - {correct_answer}")
                    return False
            
            for category, count in category_counts.items():
                print(f"  - {category}: {count}問")
        
        # 全体統計
        print(f"\n📊 全体統計:")
        print(f"✅ 総問題数: {total_questions}問")
        print(f"✅ カテゴリ数: {len(all_categories)}個")
        print(f"✅ 専門部門: {sorted(all_categories)}")
        
        # ID重複確認
        duplicate_ids = []
        for id_val in set(all_ids):
            if all_ids.count(id_val) > 1:
                duplicate_ids.append(id_val)
        
        if duplicate_ids:
            print(f"⚠️ 重複ID発見: {duplicate_ids}")
        else:
            print("✅ ID重複なし")
        
        return True
        
    except Exception as e:
        print(f"❌ CSVファイル読み込みエラー: {e}")
        return False

if __name__ == '__main__':
    print("🔍 RCCM問題データ検証開始")
    validate_questions_data()
    print("🔍 検証完了") 