#!/bin/bash
# ウルトラ高速起動スクリプト

echo "🚀 RCCM試験アプリ - ウルトラ高速起動モード"
echo "================================"

# 環境変数設定
export RCCM_LAZY_LOAD=true
export FLASK_ENV=development

echo "✅ 遅延読み込みモード: 有効"
echo "✅ 起動時のデータ読み込み: スキップ"
echo ""

# アプリ起動
python3 app.py