#!/bin/bash
# RCCM試験問題集アプリ - 企業環境デプロイメントスクリプト

set -e

echo "RCCM試験問題集アプリ - 企業環境デプロイメント開始"
echo "=================================================="

# 環境変数設定
export FLASK_ENV=${FLASK_ENV:-enterprise}
export WORKERS=${WORKERS:-4}
export MAX_CONCURRENT_USERS=${MAX_CONCURRENT_USERS:-100}

# 色付きログ出力
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 前提条件チェック
check_prerequisites() {
    log_info "前提条件をチェック中..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Dockerがインストールされていません"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Composeがインストールされていません"
        exit 1
    fi
    
    log_info "前提条件チェック完了"
}

# 必要なディレクトリ作成
setup_directories() {
    log_info "ディレクトリを作成中..."
    
    mkdir -p data user_data logs backups ssl
    chmod 755 data user_data logs backups
    
    log_info "ディレクトリ作成完了"
}

# 既存コンテナ停止・削除
cleanup_containers() {
    log_info "既存のコンテナを停止・削除中..."
    
    docker-compose down --remove-orphans 2>/dev/null || true
    docker system prune -f 2>/dev/null || true
    
    log_info "クリーンアップ完了"
}

# アプリケーションビルド
build_application() {
    log_info "アプリケーションをビルド中..."
    
    docker-compose build --no-cache
    
    log_info "ビルド完了"
}

# データバックアップ
backup_data() {
    if [ -d "user_data" ] && [ "$(ls -A user_data)" ]; then
        log_info "既存データをバックアップ中..."
        
        backup_dir="backups/backup_$(date +%Y%m%d_%H%M%S)"
        mkdir -p "$backup_dir"
        cp -r user_data/* "$backup_dir/"
        
        log_info "バックアップ完了: $backup_dir"
    fi
}

# アプリケーション起動
start_application() {
    log_info "アプリケーションを起動中..."
    
    # 基本サービス起動
    docker-compose up -d rccm-app
    
    # ヘルスチェック
    log_info "ヘルスチェック中..."
    for i in {1..30}; do
        if curl -f http://localhost:5000/ &>/dev/null; then
            log_info "アプリケーション起動成功"
            break
        fi
        echo -n "."
        sleep 2
    done
    
    if ! curl -f http://localhost:5000/ &>/dev/null; then
        log_error "アプリケーション起動失敗"
        docker-compose logs rccm-app
        exit 1
    fi
}

# Nginx起動（オプション）
start_nginx() {
    if [ "$USE_NGINX" = "true" ]; then
        log_info "Nginxを起動中..."
        docker-compose --profile nginx up -d nginx
        log_info "Nginx起動完了"
    fi
}

# デプロイメント情報表示
show_deployment_info() {
    echo ""
    log_info "デプロイメント完了!"
    echo "=================================================="
    echo "アプリケーションURL: http://localhost:5000"
    echo "管理ダッシュボード: http://localhost:5000/enterprise/dashboard"
    echo "API エンドポイント: http://localhost:5000/api/enterprise/users"
    echo ""
    echo "ログ確認: docker-compose logs -f rccm-app"
    echo "停止: docker-compose down"
    echo "=================================================="
}

# メイン実行
main() {
    check_prerequisites
    setup_directories
    backup_data
    cleanup_containers
    build_application
    start_application
    start_nginx
    show_deployment_info
}

# スクリプト実行
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi