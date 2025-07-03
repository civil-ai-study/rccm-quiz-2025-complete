#!/usr/bin/env python3
"""
RCCM試験問題集 クイックスタート
URL起動問題を解決するための簡単起動ツール
"""

import os
import sys
import time
import subprocess
from datetime import datetime

def main():
    """簡単起動"""
    print("🚀 RCCM試験問題集 クイックスタート")
    print("=" * 50)
    print(f"⏰ {datetime.now().strftime('%H:%M:%S')}")
    
    # 現在の設定を維持したまま起動
    port = 5005  # 元のポート番号を維持
    
    print(f"\n📍 アクセス情報")
    print(f"🌐 URL: http://localhost:{port}")
    print(f"📋 ブラウザで上記URLを開いてください")
    
    print(f"\n🚀 アプリケーション起動中...")
    print("💡 起動後すぐにURLアクセス可能です")
    print("🛑 停止: Ctrl+C\n")
    
    try:
        # 環境変数設定（元の設定を維持）
        os.environ['FLASK_ENV'] = 'development'
        
        # app.py実行
        subprocess.run([sys.executable, 'app.py'])
        
    except KeyboardInterrupt:
        print("\n🛑 停止しました")
    except Exception as e:
        print(f"\n❌ エラー: {e}")

if __name__ == "__main__":
    main()