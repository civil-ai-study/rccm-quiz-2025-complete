# RCCM試験問題集アプリ - 企業環境用Docker設定
FROM python:3.11-slim

# メタデータ
LABEL maintainer="RCCM App Development Team"
LABEL description="RCCM Exam Quiz Application for Enterprise"
LABEL version="3.0.0"

# 作業ディレクトリ設定
WORKDIR /app

# システムパッケージの更新とインストール
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python依存関係のインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Gunicornのインストール（本番環境用）
RUN pip install gunicorn

# アプリケーションファイルのコピー
COPY . .

# 必要なディレクトリの作成
RUN mkdir -p /app/data /app/user_data /app/logs /app/backups

# ポート設定
EXPOSE 5000

# 環境変数設定
ENV FLASK_ENV=production
ENV FLASK_HOST=0.0.0.0
ENV FLASK_PORT=5000
ENV WORKERS=4
ENV DATA_DIR=/app/data
ENV LOG_FILE=/app/logs/rccm_app.log

# ヘルスチェック
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/ || exit 1

# 非rootユーザーでの実行（セキュリティ）
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

# 起動コマンド
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "--keep-alive", "5", "app:app"]