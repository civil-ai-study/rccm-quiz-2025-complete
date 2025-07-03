#!/bin/bash
#
# 10問目テスト用の手動コマンド例
# サーバーがhttp://localhost:5000で起動していることが前提
#

BASE_URL="http://localhost:5000"

echo "=== 10問目の最終問題判定 手動テストコマンド ==="
echo
echo "1. セッション情報確認:"
echo "curl -c cookies.txt \"$BASE_URL/debug/session\""
echo
echo "2. クイズセッション開始（基礎科目10問）:"
echo "curl -c cookies.txt -b cookies.txt \"$BASE_URL/exam?question_type=basic&count=10\""
echo
echo "3. セッション情報再確認:"
echo "curl -b cookies.txt \"$BASE_URL/debug/session\" | jq"
echo
echo "4. exam_currentを9（10問目のインデックス）に設定:"
echo "curl -b cookies.txt -X POST -H \"Content-Type: application/json\" -d '{\"exam_current\": 9}' \"$BASE_URL/debug/set_current\" | jq"
echo
echo "5. 10問目を表示（これが最終問題になるはず）:"
echo "curl -b cookies.txt \"$BASE_URL/exam?next=1\""
echo
echo "6. 10問目に回答（最終問題判定が動作するはず）:"
echo "curl -b cookies.txt -X POST -d 'qid=<問題ID>&answer=A' \"$BASE_URL/exam\""
echo
echo "注意："
echo "- <問題ID>は手順5で取得した実際の問題IDに置き換えてください"
echo "- jqコマンドがない場合は | jq を削除してください"
echo "- セッションをクリアしたい場合: curl -b cookies.txt \"$BASE_URL/debug/clear_session\""
echo

# 実際のテスト実行例
if [ "$1" = "run" ]; then
    echo "=== 実際のテスト実行 ==="
    
    # セッションクリア
    echo "セッションクリア..."
    curl -s -c cookies.txt "$BASE_URL/debug/clear_session"
    echo
    
    # セッション開始
    echo "セッション開始..."
    curl -s -c cookies.txt -b cookies.txt "$BASE_URL/exam?question_type=basic&count=10" > /dev/null
    echo "セッション開始完了"
    
    # セッション情報確認
    echo "セッション情報:"
    SESSION_INFO=$(curl -s -b cookies.txt "$BASE_URL/debug/session")
    echo $SESSION_INFO
    
    # exam_currentを8（9問目）に設定
    echo "exam_currentを8に設定..."
    curl -s -b cookies.txt -X POST -H "Content-Type: application/json" -d '{"exam_current": 8}' "$BASE_URL/debug/set_current"
    echo
    
    # 問題IDを取得
    QUESTION_IDS=$(echo $SESSION_INFO | grep -o '"exam_question_ids":\[[^]]*\]' | grep -o '\[.*\]')
    echo "問題ID一覧: $QUESTION_IDS"
    
    echo
    echo "手動で以下を実行してください:"
    echo "1. ブラウザで http://localhost:5000/exam?next=1 にアクセス"
    echo "2. 9問目の問題に回答"
    echo "3. フィードバック画面で「最終問題です」等の表示を確認"
    
    # クッキーファイルクリーンアップ
    rm -f cookies.txt
fi