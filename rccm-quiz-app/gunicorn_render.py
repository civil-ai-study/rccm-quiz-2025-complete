# Render.com最適化版 Gunicorn設定
import os

# Render環境変数からポート取得
bind = f"0.0.0.0:{os.environ.get('PORT', '10000')}"

# 無料プランに最適化（メモリ512MB制限）
workers = 1  # 最小限のワーカー数
worker_class = "sync"
threads = 2  # スレッド数を追加

# タイムアウト短縮（高速レスポンス）
timeout = 30
keepalive = 2

# 高速起動のためプリロード無効化
preload_app = False

# ログ設定（標準出力へ）
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Renderのヘルスチェック対応
def when_ready(server):
    print("🚀 RCCM Quiz App - Render Optimized Mode")
    print(f"✅ Ready on port {os.environ.get('PORT', '10000')}")
    print("⚡ Fast startup mode enabled")