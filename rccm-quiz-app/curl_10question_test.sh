#!/bin/bash
# 【ULTRASYNC段階11】curl版10問完走テスト
echo "🎯 【ULTRASYNC段階11】curl版10問完走テスト開始"
echo "=" * 60

BASE_URL="https://rccm-quiz-2025.onrender.com"
COOKIE_FILE="/tmp/rccm_cookies.txt"
LOG_FILE="curl_test_$(date +%Y%m%d_%H%M%S).log"

# 関数: ログ出力
log_step() {
    echo "$1" | tee -a "$LOG_FILE"
}

# ステップ1: ホームページアクセス（セッション開始）
log_step "📋 ステップ1: ホームページアクセス"
RESPONSE=$(curl -s -c "$COOKIE_FILE" -w "HTTP_CODE:%{http_code}" "$BASE_URL/")
HTTP_CODE=$(echo "$RESPONSE" | tail -n1 | cut -d: -f2)
log_step "   ステータス: $HTTP_CODE"

if [ "$HTTP_CODE" != "200" ]; then
    log_step "   ❌ ホームページアクセス失敗"
    exit 1
fi

# ステップ2: 基礎科目試験開始
log_step ""
log_step "📋 ステップ2: 基礎科目試験開始"
RESPONSE=$(curl -s -b "$COOKIE_FILE" -c "$COOKIE_FILE" -w "HTTP_CODE:%{http_code}" "$BASE_URL/exam?question_type=basic")
HTTP_CODE=$(echo "$RESPONSE" | tail -n1 | cut -d: -f2)
CONTENT=$(echo "$RESPONSE" | head -n -1)
log_step "   ステータス: $HTTP_CODE"

if [ "$HTTP_CODE" != "200" ]; then
    log_step "   ❌ 試験開始失敗: $HTTP_CODE"
    exit 1
fi

# エラーチェック
if echo "$CONTENT" | grep -q "エラー\|問題データの取得に失敗しました"; then
    log_step "   ❌ エラーページが表示されました"
    echo "$CONTENT" | grep -o '<p[^>]*><strong>.*</strong></p>' | head -3 >> "$LOG_FILE"
    exit 1
fi

# ステップ3-12: 10問連続回答
log_step ""
log_step "📋 ステップ3-12: 10問連続回答テスト"

ANSWERS=("A" "B" "C" "D" "A" "B" "C" "D" "A" "B")

for i in {1..10}; do
    log_step ""
    log_step "   🔍 問題 $i/10"
    
    # 現在の問題を取得
    RESPONSE=$(curl -s -b "$COOKIE_FILE" -c "$COOKIE_FILE" -w "HTTP_CODE:%{http_code}" "$BASE_URL/exam")
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1 | cut -d: -f2)
    CONTENT=$(echo "$RESPONSE" | head -n -1)
    
    log_step "      問題取得ステータス: $HTTP_CODE"
    
    if [ "$HTTP_CODE" != "200" ]; then
        log_step "      ❌ 問題取得失敗: $HTTP_CODE"
        exit 1
    fi
    
    # 問題IDを抽出
    QID=$(echo "$CONTENT" | grep -o 'name="qid"[^>]*value="[0-9]*"' | grep -o '[0-9]*' | head -1)
    log_step "      問題ID: $QID"
    
    if [ -z "$QID" ]; then
        log_step "      ❌ 問題IDが見つかりません"
        exit 1
    fi
    
    # 進捗を抽出
    PROGRESS=$(echo "$CONTENT" | grep -o '[0-9]*/[0-9]*' | head -1)
    log_step "      進捗: $PROGRESS"
    
    # 問題文を抽出（最初の100文字）
    QUESTION=$(echo "$CONTENT" | grep -o '<h4[^>]*>問題[0-9]*</h4>\s*<p[^>]*>.*</p>' | sed 's/<[^>]*>//g' | head -c 100)
    log_step "      問題文: ${QUESTION}..."
    
    # 回答送信
    ANSWER=${ANSWERS[$((i-1))]}
    log_step "      回答送信: $ANSWER"
    
    RESPONSE=$(curl -s -b "$COOKIE_FILE" -c "$COOKIE_FILE" -w "HTTP_CODE:%{http_code}" \
        -X POST \
        -d "answer=$ANSWER" \
        -d "qid=$QID" \
        -d "elapsed=30" \
        "$BASE_URL/exam")
    
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1 | cut -d: -f2)
    CONTENT=$(echo "$RESPONSE" | head -n -1)
    log_step "      回答送信ステータス: $HTTP_CODE"
    
    if [ "$HTTP_CODE" != "200" ] && [ "$HTTP_CODE" != "302" ]; then
        log_step "      ❌ 回答送信失敗: $HTTP_CODE"
        exit 1
    fi
    
    # 結果確認
    if echo "$CONTENT" | grep -q "正解\|不正解\|次の問題へ"; then
        log_step "      ✅ 回答処理成功"
    else
        log_step "      ⚠️ 回答結果不明"
    fi
    
    sleep 1  # 1秒待機
done

# ステップ13: 最終結果確認
log_step ""
log_step "📋 ステップ13: 最終結果確認"
RESPONSE=$(curl -s -b "$COOKIE_FILE" -w "HTTP_CODE:%{http_code}" "$BASE_URL/result")
HTTP_CODE=$(echo "$RESPONSE" | tail -n1 | cut -d: -f2)
CONTENT=$(echo "$RESPONSE" | head -n -1)
log_step "   ステータス: $HTTP_CODE"

if [ "$HTTP_CODE" = "200" ]; then
    if echo "$CONTENT" | grep -q "結果\|スコア"; then
        log_step "   ✅ 結果画面表示成功"
        
        # スコア抽出試行
        SCORE=$(echo "$CONTENT" | grep -o 'スコア[^0-9]*[0-9]*' | head -1)
        if [ -n "$SCORE" ]; then
            log_step "   📊 $SCORE"
        fi
    else
        log_step "   ⚠️ 結果画面内容不明"
    fi
else
    log_step "   ❌ 結果画面アクセス失敗: $HTTP_CODE"
fi

log_step ""
log_step "=" * 60
log_step "🎯 【ULTRASYNC段階11】curl版10問完走テスト完了"
log_step "📋 詳細ログ: $LOG_FILE"
log_step "🍪 Cookie: $COOKIE_FILE"

# クリーンアップ
rm -f "$COOKIE_FILE"

echo "テスト完了"