# 🚀 RCCM試験問題集2025 - 一般配布用EXE化完全手順

## 📋 事前準備（Windows PCで実行）

### 1. Python環境セットアップ
```bash
# Python 3.11をダウンロード・インストール
# https://www.python.org/downloads/windows/
# ✅ "Add Python to PATH" をチェック

# PowerShellまたはコマンドプロンプトで確認
python --version
pip --version
```

### 2. 必要パッケージインストール
```bash
pip install pyinstaller
pip install flask pandas numpy jinja2 werkzeug itsdangerous click chardet
```

## 🔧 EXE化実行手順

### 3. アプリケーションファイル準備
```
📁 rccm-app-build/
├── app.py              # メインアプリケーション
├── config.py           # 設定ファイル
├── utils.py            # ユーティリティ
├── data_manager.py     # データ管理
├── 📁 templates/       # HTMLテンプレート
├── 📁 data/           # CSVファイル（3,883問）
├── 📁 static/         # CSS/JSファイル
└── build_exe.spec     # PyInstaller設定
```

### 4. EXE化実行
```bash
# アプリケーションフォルダに移動
cd rccm-app-build

# PyInstallerでEXE作成（オールインワン版）
pyinstaller --onefile --windowed --add-data "templates;templates" --add-data "data;data" --add-data "static;static" --add-data "config.py;." --add-data "utils.py;." --add-data "data_manager.py;." --name "RCCM試験問題集2025" app.py

# または、specファイル使用
pyinstaller build_exe.spec
```

### 5. 実行ファイル確認
```
📁 dist/
└── RCCM試験問題集2025.exe  # 配布用EXEファイル（約100-200MB）
```

## 📦 配布パッケージ作成

### 6. 最終配布フォルダ構成
```
📁 RCCM試験問題集2025_配布用/
├── 🚀 RCCM試験問題集2025.exe    # メインアプリケーション
├── 📖 使い方ガイド.pdf           # 図解マニュアル
├── 📋 README.txt                # 重要事項
├── 📞 サポート連絡先.txt         # 困った時の連絡先
└── 🔧 トラブル対処法.txt         # よくある問題の解決法
```

### 7. ZIP圧縮・配布
```bash
# フォルダ全体をZIP圧縮
# ファイル名例：RCCM試験問題集2025_v1.0.zip
# サイズ予想：200-300MB
```

## 🎯 一般ユーザー向け使用手順書

### ユーザー操作（3ステップ）
```
📥 ステップ1：ダウンロード
OneDriveリンクから「RCCM試験問題集2025_v1.0.zip」をダウンロード

📂 ステップ2：解凍
ZIPファイルを右クリック → 「すべて展開」

🚀 ステップ3：起動
「RCCM試験問題集2025.exe」をダブルクリック
→ ブラウザが自動で開いて完了！
```

## ⚠️ トラブル対策

### Windows Defender対策
```
EXEファイル初回実行時の警告対処：
1. 「WindowsによってPCが保護されました」表示
2. 「詳細情報」をクリック
3. 「実行」をクリック
4. 以降は警告なしで実行可能
```

### ポート競合対策
```python
# app.pyに追加（自動ポート検出）
import socket

def find_free_port():
    for port in range(5003, 5010):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(('localhost', port))
            sock.close()
            return port
        except:
            continue
    return 5003

if __name__ == '__main__':
    port = find_free_port()
    print(f"RCCM試験問題集2025を起動中... http://localhost:{port}")
    # ブラウザ自動オープン
    import webbrowser
    import threading
    import time
    
    def open_browser():
        time.sleep(2)
        webbrowser.open(f'http://localhost:{port}')
    
    threading.Thread(target=open_browser).start()
    app.run(host='127.0.0.1', port=port, debug=False)
```

## 📧 配布時のメール例文

```
件名：RCCM試験問題集2025のご提供

お疲れ様です。

RCCM試験対策アプリケーションをお送りします。

【ダウンロード】
以下のリンクからダウンロードしてください：
[OneDriveリンク]

【使用方法】
1. ZIPファイルをダウンロード
2. 右クリック→「すべて展開」
3. 「RCCM試験問題集2025.exe」をダブルクリック

【特徴】
✅ 3,883問完全収録
✅ AI学習支援機能
✅ インストール不要
✅ オフライン動作

何かご不明な点がございましたら、
お気軽にご連絡ください。

【サポート】
Email: [あなたのメールアドレス]
```

## 🎉 配布完了！

これで**完全にセルフコンテインド**なRCCM試験問題集が完成です！
歯医者の先生方も迷うことなく使用できます。