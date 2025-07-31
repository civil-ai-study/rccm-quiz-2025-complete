
def load_csv_safe_enhanced(file_path):
    """
    Phase4エンコーディング問題対応強化版CSV読み込み
    """
    if not os.path.exists(file_path):
        print(f"ERROR: ファイルが存在しません: {file_path}")
        return None
    
    # UTF-8優先の強化エンコーディング試行順序
    encodings_to_try = [
        'utf-8-sig',  # UTF-8 with BOM
        'utf-8',      # UTF-8 without BOM
        'cp932',      # Windows Japanese
        'shift_jis',  # Shift JIS
        'euc-jp',     # EUC-JP
        'iso-2022-jp' # ISO-2022-JP
    ]
    
    for encoding in encodings_to_try:
        try:
            # エンコーディング指定で読み込み
            df = pd.read_csv(file_path, encoding=encoding)
            
            # 日本語文字が正しく読み込まれているか検証
            if not df.empty:
                # サンプル文字列で日本語検証
                sample_text = str(df.iloc[0, 0]) if len(df.columns) > 0 else ""
                if any(ord(char) > 127 for char in sample_text):
                    print(f"OK: {file_path} 日本語エンコーディング成功 ({encoding})")
                else:
                    print(f"OK: {file_path} ASCII読み込み成功 ({encoding})")
                
            return df
            
        except UnicodeDecodeError as e:
            print(f"WARNING: {file_path} エンコーディング {encoding} 失敗: Unicode Decode Error")
            continue
        except Exception as e:
            print(f"WARNING: {file_path} エンコーディング {encoding} 失敗: {e}")
            continue
    
    print(f"ERROR: {file_path} すべてのエンコーディング失敗")
    return None
