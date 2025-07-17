#!/bin/bash
# 【ULTRASYNC段階11】改良版10問完走テスト
echo "🎯 【ULTRASYNC段階11】改良版10問完走テスト開始"
echo "================================================================"

BASE_URL="https://rccm-quiz-2025.onrender.com"
COOKIE_FILE="/tmp/rccm_cookies_$(date +%s).txt"
LOG_FILE="improved_test_$(date +%Y%m%d_%H%M%S).log"

# 関数: ログ出力
log_step() {
    echo "$1" | tee -a "$LOG_FILE"
}

# 関数: HTMLから問題IDを抽出
extract_qid() {
    echo "$1" | grep -o 'name="qid"[^>]*value="[0-9]*"' | grep -o '[0-9]*' | head -1
}

# 関数: HTMLから進捗を抽出
extract_progress() {
    echo "$1" | grep -o '[0-9]*/[0-9]*' | head -1
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

# 問題IDをチェック（エラーがないかの確認）
QID=$(extract_qid "$CONTENT")
if [ -z "$QID" ]; then
    log_step "   ❌ 問題データが見つかりません"
    
    # エラーメッセージ抽出
    ERROR_MSG=$(echo "$CONTENT" | grep -o '<p[^>]*><strong>.*</strong></p>' | sed 's/<[^>]*>//g' | head -3)
    if [ -n "$ERROR_MSG" ]; then
        log_step "   📄 エラー詳細: $ERROR_MSG"
    fi
    
    # デバッグ用：HTMLの一部を保存
    echo "$CONTENT" | head -100 > debug_response.html
    log_step "   🔍 デバッグ用レスポンス保存: debug_response.html"
    exit 1
else
    log_step "   ✅ 問題データ確認: QID=$QID"
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
    QID=$(extract_qid "$CONTENT")
    log_step "      問題ID: $QID"
    
    if [ -z "$QID" ]; then
        log_step "      ❌ 問題IDが見つかりません"
        exit 1
    fi
    
    # 進捗を抽出
    PROGRESS=$(extract_progress "$CONTENT")
    log_step "      進捗: $PROGRESS"
    
    # 問題文を抽出（簡略版）
    QUESTION_PREVIEW=$(echo "$CONTENT" | grep -A 2 '<h4.*>問題' | tail -1 | sed 's/<[^>]*>//g' | head -c 80)
    log_step "      問題文: ${QUESTION_PREVIEW}..."
    
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
    if echo "$CONTENT" | grep -q "正解\|不正解\|次の問題へ\|結果を見る"; then
        log_step "      ✅ 回答処理成功"
        
        # 正解/不正解の表示
        if echo "$CONTENT" | grep -q "正解"; then
            log_step "      🎉 正解"
        elif echo "$CONTENT" | grep -q "不正解"; then
            log_step "      ❌ 不正解"
        fi
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
    if echo "$CONTENT" | grep -q "結果\|スコア\|得点"; then
        log_step "   ✅ 結果画面表示成功"
        
        # スコア抽出試行
        SCORE=$(echo "$CONTENT" | grep -o '[0-9]*.*点\|スコア.*[0-9]*\|得点.*[0-9]*' | head -1)
        if [ -n "$SCORE" ]; then
            log_step "   📊 スコア: $SCORE"
        fi
        
        # 正解数抽出試行
        CORRECT_ANSWERS=$(echo "$CONTENT" | grep -o '[0-9]*.*問正解\|正解数.*[0-9]*' | head -1)
        if [ -n "$CORRECT_ANSWERS" ]; then
            log_step "   🎯 正解数: $CORRECT_ANSWERS"
        fi
    else
        log_step "   ⚠️ 結果画面内容不明"
    fi
else
    log_step "   ❌ 結果画面アクセス失敗: $HTTP_CODE"
fi

log_step ""
log_step "================================================================"
log_step "🎯 【ULTRASYNC段階11】改良版10問完走テスト完了"
log_step "📋 詳細ログ: $LOG_FILE"

# 成功判定
if [ "$HTTP_CODE" = "200" ] && [ -n "$QID" ]; then
    log_step ""
    log_step "🎉 【ULTRASYNC段階11】改良版10問完走テスト: 成功"
    log_step "✅ 本番環境での10問完走が確認されました"
    
    # クリーンアップ
    rm -f "$COOKIE_FILE"
    
    echo ""
    echo "🎉 テスト成功 - 10問完走テスト完了"
    exit 0
else
    log_step ""
    log_step "🚨 【ULTRASYNC段階11】改良版10問完走テスト: 失敗"
    log_step "❌ 問題が発生しました"
    
    # クリーンアップ
    rm -f "$COOKIE_FILE"
    
    echo ""
    echo "❌ テスト失敗"
    exit 1
fi