#!/bin/bash
# RCCM試験問題集 - 自動復旧サーバー起動スクリプト

echo "🚀 RCCM試験問題集サーバー起動中..."

# 既存プロセス確認・停止
echo "📋 既存プロセス確認中..."
if pgrep -f "python3.*app.py" > /dev/null; then
    echo "⚠️  既存のサーバープロセスを停止中..."
    pkill -f "python3.*app.py"
    sleep 2
fi

# ポート確認・解放
echo "🔍 ポート5003確認中..."
if lsof -ti:5003 > /dev/null 2>&1; then
    echo "⚠️  ポート5003を解放中..."
    lsof -ti:5003 | xargs kill -9 2>/dev/null || true
    sleep 1
fi

# ログディレクトリ作成
mkdir -p logs

# サーバー起動（自動復旧付き）
echo "🔄 サーバー起動中（自動復旧モード）..."
while true; do
    echo "$(date): サーバー起動試行..."
    python3 app.py > logs/app_$(date +%Y%m%d_%H%M%S).log 2>&1 &
    
    # 起動確認（最大30秒待機）
    for i in {1..30}; do
        if curl -s -o /dev/null -w "%{http_code}" http://localhost:5003/ | grep -q "200"; then
            echo "✅ サーバー起動成功！ http://172.18.44.152:5003"
            echo "📊 プロセス情報: $(pgrep -f 'python3.*app.py')"
            break 2
        fi
        sleep 1
    done
    
    echo "❌ 起動失敗。5秒後に再試行..."
    pkill -f "python3.*app.py" 2>/dev/null || true
    sleep 5
done

echo "🎯 RCCMサーバー運用開始"