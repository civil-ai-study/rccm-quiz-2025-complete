# 🚀 RCCM Quiz Application - Production Deployment Guide

## 重要: 本番環境WSGIサーバー使用必須

### ❌ **開発サーバー（本番環境では使用禁止）**
```bash
# ❌ 本番環境では絶対に使用しないでください
python3 app.py
```

### ✅ **本番環境WSGI サーバー（推奨）**
```bash
# ✅ 本番環境ではこちらを使用
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 wsgi:application
```

---

## 🛡️ セキュア本番環境デプロイメント

### **1. 必須環境変数設定**

```bash
# 🔐 セキュリティ必須設定
export SECRET_KEY="your-cryptographically-secure-random-key-min-32-chars"
export FLASK_ENV="production"
export PORT="5000"

# 🔧 オプション設定
export GUNICORN_WORKERS="4"              # CPU cores * 2 + 1
export GUNICORN_LOG_LEVEL="info"         # info, warning, error
export WEB_CONCURRENCY="4"               # Heroku等のプラットフォーム用
```

### **2. 本番環境起動方法**

#### **方法1: 推奨起動スクリプト使用**
```bash
# 🚀 セキュア起動（推奨）
./start-production.sh

# 🧪 事前チェック
./start-production.sh check

# 🔧 開発モード（オートリロード）
./start-production.sh dev
```

#### **方法2: 直接Gunicorn実行**
```bash
# 🚀 基本起動
gunicorn -w 4 -b 0.0.0.0:5000 wsgi:application

# 🔧 詳細設定付き起動
gunicorn \
    --config gunicorn.conf.py \
    --bind 0.0.0.0:5000 \
    --workers 4 \
    --timeout 30 \
    --keepalive 60 \
    --max-requests 1000 \
    --preload \
    wsgi:application
```

#### **方法3: 設定ファイル使用**
```bash
# 📋 設定ファイル使用（推奨）
gunicorn --config gunicorn.conf.py wsgi:application
```

---

## 🌐 プラットフォーム別デプロイメント

### **Render.com**
```bash
# 🌐 Render用設定
export RENDER=true
export PORT=10000
gunicorn --config gunicorn.conf.py wsgi:application
```

### **Heroku**
```bash
# 🌐 Heroku用設定（Procfile使用）
web: gunicorn --config gunicorn.conf.py wsgi:application
```

### **VPS/Dedicated Server**
```bash
# 🌐 VPS用systemdサービス
sudo systemctl enable rccm-quiz-app
sudo systemctl start rccm-quiz-app
```

### **Docker**
```dockerfile
# 🐳 Dockerfile例
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000
CMD ["gunicorn", "--config", "gunicorn.conf.py", "wsgi:application"]
```

---

## 🔧 パフォーマンス設定

### **Worker プロセス数の決定**
```bash
# 🧮 CPU集約的アプリケーション
WORKERS = (CPU_CORES * 2) + 1

# 例: 4コアサーバー
export GUNICORN_WORKERS=9

# 🌐 I/O集約的アプリケーション（推奨）
WORKERS = CPU_CORES * 2

# 例: 4コアサーバー
export GUNICORN_WORKERS=8
```

### **メモリ使用量最適化**
```bash
# 🧠 メモリ効率設定
gunicorn \
    --workers 4 \
    --max-requests 1000 \        # メモリリーク防止
    --max-requests-jitter 100 \  # 再起動分散
    --preload \                  # メモリ効率向上
    wsgi:application
```

### **接続処理最適化**
```bash
# 🔗 接続設定
gunicorn \
    --timeout 30 \               # リクエストタイムアウト
    --keepalive 60 \             # Keep-Alive
    --worker-connections 1000 \  # 同時接続数
    wsgi:application
```

---

## 🛡️ セキュリティ設定

### **リバースプロキシ設定（nginx）**
```nginx
# /etc/nginx/sites-available/rccm-quiz-app
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # SSL設定
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;

    # セキュリティヘッダー
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;

    # アプリケーション
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # タイムアウト設定
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }

    # 静的ファイル（オプション）
    location /static/ {
        alias /path/to/app/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### **Systemd サービス設定**
```ini
# /etc/systemd/system/rccm-quiz-app.service
[Unit]
Description=RCCM Quiz Application (Gunicorn)
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/path/to/app
Environment=FLASK_ENV=production
Environment=SECRET_KEY=your-secret-key
Environment=PORT=5000
ExecStart=/path/to/venv/bin/gunicorn --config gunicorn.conf.py wsgi:application
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

---

## 📊 監視とログ

### **ログ設定**
```bash
# 📊 ログ出力設定
gunicorn \
    --access-logfile /var/log/rccm-quiz-app/access.log \
    --error-logfile /var/log/rccm-quiz-app/error.log \
    --log-level info \
    wsgi:application
```

### **ヘルスチェック**
```python
# health_check.py
import requests
import sys

def health_check():
    try:
        response = requests.get('http://localhost:5000/health', timeout=10)
        if response.status_code == 200:
            print("✅ Application is healthy")
            sys.exit(0)
        else:
            print(f"❌ Health check failed: {response.status_code}")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Health check error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    health_check()
```

### **パフォーマンス監視**
```bash
# 🔍 リソース監視
htop
netstat -tlnp | grep :5000
curl -s http://localhost:5000/metrics  # メトリクス取得（実装済み）
```

---

## 🚀 デプロイメント チェックリスト

### **デプロイ前チェック**
- [ ] **SECRET_KEY環境変数設定済み**
- [ ] **FLASK_ENV=production設定済み**
- [ ] **Gunicornインストール済み**
- [ ] **wsgi.py設定確認済み**
- [ ] **gunicorn.conf.py設定確認済み**
- [ ] **セキュリティ設定確認済み**
- [ ] **SSL証明書設定済み（本番）**
- [ ] **リバースプロキシ設定済み（本番）**
- [ ] **ファイアウォール設定済み**
- [ ] **監視・ログ設定済み**

### **デプロイ後検証**
- [ ] **アプリケーション起動確認**
- [ ] **ヘルスチェック実行**
- [ ] **セキュリティヘッダー確認**
- [ ] **パフォーマンステスト実行**
- [ ] **ログ出力確認**
- [ ] **エラーページ確認**
- [ ] **SSL設定確認（本番）**

---

## 🔧 トラブルシューティング

### **よくある問題と解決方法**

#### **1. ポート使用中エラー**
```bash
# 🔍 ポート使用状況確認
sudo netstat -tlnp | grep :5000
sudo lsof -i :5000

# 🔧 プロセス終了
sudo kill -9 [PID]
```

#### **2. 権限エラー**
```bash
# 🔧 ファイル権限設定
chmod +x start-production.sh
chmod 644 gunicorn.conf.py
chown www-data:www-data /path/to/app
```

#### **3. メモリ不足**
```bash
# 🧠 メモリ使用量確認
free -h
ps aux --sort=-%mem | head

# 🔧 Worker数調整
export GUNICORN_WORKERS=2  # 減少
```

#### **4. SSL証明書エラー**
```bash
# 🔐 証明書確認
openssl x509 -in cert.pem -text -noout
openssl verify cert.pem
```

---

## 📚 関連リソース

- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [Flask Deployment Options](https://flask.palletsprojects.com/en/2.3.x/deploying/)
- [nginx Configuration](https://nginx.org/en/docs/)
- [Systemd Service Configuration](https://www.freedesktop.org/software/systemd/man/systemd.service.html)

---

**🚀 本番環境デプロイメント完了**  
**重要**: 開発サーバー（`python3 app.py`）は本番環境では絶対に使用しないでください  
**推奨**: Gunicorn WSGIサーバーを使用してください（`gunicorn -w 4 -b 0.0.0.0:5000 wsgi:application`）