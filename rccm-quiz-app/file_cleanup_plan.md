# 🗂️ ファイル整理計画 - プログラム本体保護

## ✅ **絶対保持するプログラム本体ファイル**

### 📋 **メインアプリケーション**
- `app.py` - メインFlaskアプリケーション
- `config.py` - 設定ファイル
- `utils.py` - ユーティリティ関数
- `wsgi.py` - WSGI設定
- `data_manager.py` - データ管理
- `data_check.py` - データ整合性チェック

### 📋 **機能モジュール**
- `adaptive_learning.py` - 適応学習システム
- `admin_dashboard.py` - 管理ダッシュボード
- `advanced_analytics.py` - 高度分析
- `advanced_personalization.py` - パーソナライゼーション
- `ai_analyzer.py` - AI分析
- `api_integration.py` - API統合
- `exam_simulator.py` - 試験シミュレータ
- `gamification.py` - ゲーミフィケーション
- `learning_optimizer.py` - 学習最適化
- `mobile_features.py` - モバイル機能
- `multimodal_learning.py` - マルチモーダル学習
- `social_learning.py` - ソーシャル学習
- `redis_cache.py` - Redisキャッシュ
- `memory_leak_monitor.py` - メモリ監視

### 📋 **Ultra Sync 最終実装版**
- `ultra_sync_session_cleanup.py` - セッション管理
- `ultra_sync_accessibility_test.py` - アクセシビリティテスト
- `ultra_sync_encoding_unification.py` - エンコーディング統一
- `ultra_sync_unified_session_manager.py` - 統合セッション管理
- `ultra_sync_memory_monitoring_integration.py` - メモリ監視統合
- `ultra_sync_error_loop_prevention.py` - エラーループ防止

### 📋 **ディレクトリ構造**
- `templates/` - 全HTMLテンプレート（44ファイル）
- `data/` - CSVデータファイル（14ファイル）
- `config/` - 設定ディレクトリ
- `api_data/` - API関連データ
- `personalization_data/` - パーソナライゼーションデータ
- `debug_files_archive/` - アーカイブ済みデバッグファイル（保持）

### 📋 **デプロイメント・設定ファイル**
- `Dockerfile`, `Dockerfile.redis` - Docker設定
- `docker-compose.yml`, `docker-compose.redis.yml` - Docker Compose
- `requirements*.txt` - 依存関係（全種類）
- `Procfile` - Heroku設定
- `render.yaml` - Render設定
- `railway.toml` - Railway設定
- `gunicorn.conf.py` - Gunicorn設定
- `nginx.conf` - Nginx設定
- `supervisord.conf` - Supervisor設定
- `redis.conf` - Redis設定

### 📋 **重要ドキュメント**
- `CLAUDE.md` - 開発ガイドライン
- `README*.md` - プロジェクト説明
- `DEPLOYMENT.md` - デプロイ手順
- `SECURITY.md` - セキュリティ情報
- 配布用手順書類（全て）

## ❌ **削除対象の一時ファイル**

### 🗑️ **テスト用HTMLファイル（テンプレート以外）**
- `*_q[1-9].html`, `*_q10.html` - 個別問題ページ
- `*_results.html`, `*_session.html` - 結果・セッションページ
- `road_*.html`, `basic_*.html`, `soil_*.html` など部門別テストページ
- `*_2019.html` - 年度別テストページ

### 🗑️ **一時的なテストスクリプト**
- `test_*.py` - テストスクリプト（本体機能以外）
- `debug_*.py` - デバッグスクリプト
- `comprehensive_*.py` - 包括テストスクリプト
- `manual_*.py` - 手動テストスクリプト
- `final_*.py` - 最終テストスクリプト

### 🗑️ **ログ・レポートファイル**
- `*.log` - ログファイル
- `*_report_*.json` - テストレポート
- `*_results*.json` - テスト結果
- `screenshot_*.png` - スクリーンショット

### 🗑️ **一時・キャッシュファイル**
- `*cookies.txt`, `cookie.txt` - クッキーファイル
- `*.backup` - バックアップファイル
- `flask_session/` - Flaskセッション
- session_backups/, recovery_backups/ - セッションバックアップ

## 🛡️ **安全削除手順**
1. 削除前にリスト確認
2. 重要ファイル除外確認
3. バックアップ作成
4. 段階的削除実行