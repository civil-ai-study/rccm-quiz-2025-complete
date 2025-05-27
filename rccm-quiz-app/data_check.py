# data_check.py - データ整合性確認スクリプト
import pandas as pd
import os

def validate_questions_data():
    """問題データの整合性を確認"""
    csv_path = 'data/questions.csv'
    
    if not os.path.exists(csv_path):
        print("❌ questions.csv が見つかりません")
        return False
    
    try:
        df = pd.read_csv(csv_path)
        print(f"✅ CSVファイル読み込み成功: {len(df)}行")
        
        # 必要列の確認
        required_columns = ['id', 'category', 'question', 'option_a', 'option_b', 
                          'option_c', 'option_d', 'correct_answer', 'explanation']
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            print(f"❌ 不足している列: {missing_columns}")
            return False
        
        print("✅ 必要な列がすべて存在します")
        
        # データ内容の確認
        print(f"📊 カテゴリ別問題数:")
        category_counts = df['category'].value_counts()
        for category, count in category_counts.items():
            print(f"  - {category}: {count}問")
        
        # 重複ID確認
        duplicate_ids = df[df['id'].duplicated()]
        if not duplicate_ids.empty:
            print(f"⚠️  重複ID発見: {duplicate_ids['id'].tolist()}")
        else:
            print("✅ ID重複なし")
        
        # 正解選択肢の確認
        invalid_answers = df[~df['correct_answer'].isin(['A', 'B', 'C', 'D'])]
        if not invalid_answers.empty:
            print(f"❌ 無効な正解選択肢: {invalid_answers[['id', 'correct_answer']].to_dict('records')}")
        else:
            print("✅ 正解選択肢は正常です")
        
        return True
        
    except Exception as e:
        print(f"❌ CSVファイル読み込みエラー: {e}")
        return False

if __name__ == '__main__':
    print("🔍 RCCM問題データ検証開始")
    validate_questions_data()
    print("🔍 検証完了") 