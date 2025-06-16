# 🚀 エンタープライズ級プロダクション設定（数百人同時使用対応）
import multiprocessing
import os

# 基本設定
bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2 + 1  # CPU数 x 2 + 1
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50

# 堅牢性設定
timeout = 120
keepalive = 2
graceful_timeout = 30
preload_app = True

# ログ設定
accesslog = "/var/log/gunicorn/access.log"
errorlog = "/var/log/gunicorn/error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# プロセス管理
pid = "/var/run/gunicorn/gunicorn.pid"
user = "www-data"
group = "www-data"

# セキュリティ
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# パフォーマンス
worker_tmp_dir = "/dev/shm"
forwarded_allow_ips = "*"
secure_scheme_headers = {
    'X-FORWARDED-PROTOCOL': 'ssl',
    'X-FORWARDED-PROTO': 'https',
    'X-FORWARDED-SSL': 'on'
}

# 自動再起動設定
reload = False  # プロダクションでは無効
reload_engine = "auto"

# メモリ管理
max_worker_memory = 200  # MB
worker_memory_limit = 250 * 1024 * 1024  # 250MB

def when_ready(server):
    """サーバー起動完了時"""
    print("🚀 RCCM試験アプリ - エンタープライズモード起動完了")
    print(f"⚡ ワーカープロセス数: {workers}")
    print(f"🔗 バインドアドレス: {bind}")
    print("📊 数百人同時アクセス対応準備完了")

def worker_int(worker):
    """ワーカープロセス中断時"""
    print(f"🔄 ワーカープロセス {worker.pid} が中断されました - 自動復旧中")

def on_exit(server):
    """サーバー終了時"""
    print("🛑 RCCM試験アプリ - 正常終了")