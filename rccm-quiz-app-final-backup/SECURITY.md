# 🛡️ RCCM Quiz Application Security Guide

## セキュリティ強化実装 - CLAUDE.md準拠

### 🚨 修正された重大なセキュリティリスク

#### **1. 危険な本番環境設定の修正**

**❌ 修正前（セキュリティリスク）:**
```python
app.run(debug=True, host='0.0.0.0')  # 危険：全IPからアクセス可能 + デバッグ情報露出
```

**✅ 修正後（セキュア）:**
```python
# 🛡️ 環境別セキュア設定
if is_production:
    host = '0.0.0.0'      # 本番：必要最小限
    debug_mode = False    # 本番：デバッグ無効
else:
    host = '127.0.0.1'    # 開発：ローカルのみ
    debug_mode = True     # 開発：デバッグ有効
```

#### **2. SECRET_KEY の安全な管理**

**❌ 修正前:**
```python
SECRET_KEY = 'hardcoded-key'  # 危険：ハードコード
```

**✅ 修正後:**
```python
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    if os.environ.get('FLASK_ENV') == 'production':
        raise ValueError("Production環境ではSECRET_KEYの環境変数設定が必須です")
```

### 🛡️ 実装されたセキュリティ機能

#### **1. セッションセキュリティ強化**
```python
SESSION_COOKIE_SECURE = True          # HTTPS必須（本番）
SESSION_COOKIE_HTTPONLY = True        # XSS防止
SESSION_COOKIE_SAMESITE = 'Lax'       # CSRF防止
PERMANENT_SESSION_LIFETIME = 3600     # 1時間でセッション期限切れ
```

#### **2. CSRF保護**
```python
WTF_CSRF_ENABLED = True               # CSRFトークン
WTF_CSRF_TIME_LIMIT = 3600           # CSRF トークン有効期限
```

#### **3. セキュリティヘッダー**
```python
SECURITY_HEADERS = {
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'X-XSS-Protection': '1; mode=block',
    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
    'Referrer-Policy': 'strict-origin-when-cross-origin',
    'Permissions-Policy': 'geolocation=(), microphone=(), camera=()'
}
```

### 🔧 本番環境デプロイメント

#### **1. 必須環境変数設定**
```bash
# 本番環境で必須
export SECRET_KEY="your-cryptographically-secure-random-key"
export FLASK_ENV="production"
export PORT="10000"  # または適切なポート

# 推奨追加設定
export SESSION_COOKIE_DOMAIN="your-domain.com"
export TRUSTED_HOSTS="your-domain.com,www.your-domain.com"
```

#### **2. 推奨WSGIサーバー設定（Gunicorn）**
```bash
# セキュアなGunicorn設定
gunicorn \
    --bind 0.0.0.0:$PORT \
    --workers 4 \
    --timeout 30 \
    --keepalive 60 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --limit-request-line 4096 \
    --limit-request-fields 100 \
    --limit-request-field-size 8190 \
    app:app
```

#### **3. リバースプロキシ設定（nginx）**
```nginx
# nginx セキュリティ設定例
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    # SSL設定
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    
    # セキュリティヘッダー
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    
    # アプリケーションへのプロキシ
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 🔍 セキュリティ検証

#### **1. 開発時セキュリティチェック**
```bash
# セキュリティ依存関係チェック
pip install safety
safety check

# セキュリティ設定確認
python3 run_comprehensive_tests.py --validate-environment
```

#### **2. 本番前セキュリティ監査**
```bash
# セキュリティヘッダー確認
curl -I https://your-domain.com

# SSL設定確認
openssl s_client -connect your-domain.com:443 -servername your-domain.com
```

### 🚨 セキュリティ警告と対策

#### **1. 開発環境の注意点**
- ❌ 開発環境で `debug=True` をそのまま本番で使用しない
- ❌ ハードコードされたSECRET_KEYを本番で使用しない
- ❌ `host='0.0.0.0'` を無条件に使用しない

#### **2. 本番環境の必須対策**
- ✅ 環境変数でSECRET_KEYを管理
- ✅ HTTPS通信の強制
- ✅ WSGIサーバー（Gunicorn等）の使用
- ✅ リバースプロキシ（nginx等）の設置
- ✅ 定期的なセキュリティアップデート

#### **3. 継続的セキュリティ管理**
- ✅ 依存関係の定期的な脆弱性チェック
- ✅ セキュリティログの監視
- ✅ セッション管理の監査
- ✅ CSRF攻撃の監視

### 📋 セキュリティチェックリスト

#### **デプロイ前必須チェック**
- [ ] SECRET_KEY環境変数設定済み
- [ ] FLASK_ENV=production設定済み
- [ ] debug=False確認済み
- [ ] HTTPS設定完了
- [ ] セキュリティヘッダー確認済み
- [ ] CSRF保護有効化確認済み
- [ ] セッション設定確認済み
- [ ] WSGIサーバー設定完了
- [ ] ファイアウォール設定完了
- [ ] 監視・ログ設定完了

#### **運用中定期チェック**
- [ ] セキュリティアップデート適用
- [ ] 脆弱性スキャン実行
- [ ] ログ監視確認
- [ ] セッション管理監査
- [ ] バックアップ確認

### 🔗 関連リソース

- [Flask Security Best Practices](https://flask.palletsprojects.com/en/2.3.x/security/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Flask-WTF Documentation](https://flask-wtf.readthedocs.io/)
- [Gunicorn Security](https://docs.gunicorn.org/en/stable/settings.html#security)

---

**🛡️ セキュリティ実装完了**  
**準拠**: CLAUDE.md セキュリティ要件  
**最終更新**: 2025-06-30  
**ステータス**: 本番環境対応セキュリティ強化済み