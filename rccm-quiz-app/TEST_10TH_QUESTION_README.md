# 10問目の最終問題判定テスト

10問のクイズセッションで10問目の`is_last_question`判定が正しく動作するかをテストするためのツール群です。

## 前提条件

- Flask アプリケーション（app.py）が http://localhost:5000 で起動していること
- セッション継続性が修正済みであること

## テスト方法

### 1. 自動テスト（推奨）

#### 方法A: セッション状態を直接操作

```bash
# 必要な依存関係をインストール（初回のみ）
pip install beautifulsoup4

# テスト実行
python test_10th_question_final.py
```

このテストは：
- 新しいセッションを開始
- `exam_current`を8（9問目のインデックス）に直接設定
- 9問目に回答して10問目の判定をテスト
- 複数のシナリオ（基礎科目、専門科目、異なる問題数）でテスト

#### 方法B: 自動連続回答

```bash
# 必要な依存関係をインストール（初回のみ）
pip install beautifulsoup4

# テスト実行
python auto_10_questions.py
```

このテストは：
- 新しいセッションを開始
- 1問目から10問目まで自動で回答
- 各問題の回答後にフィードバックを確認
- 10問目で最終問題判定が正しく動作するかチェック

### 2. 手動テスト

#### ブラウザでの手動テスト

1. ブラウザで http://localhost:5000 にアクセス
2. 基礎科目で10問のセッションを開始
3. 8問回答後、以下のAPIで9問目にジャンプ：

```bash
# セッション情報確認
curl -c cookies.txt "http://localhost:5000/debug/session"

# exam_currentを8に設定（9問目のインデックス）
curl -b cookies.txt -X POST -H "Content-Type: application/json" \
     -d '{"exam_current": 8}' \
     "http://localhost:5000/debug/set_current"
```

4. ブラウザで次の問題に進む
5. 9問目に回答
6. フィードバック画面で「最終問題です」の表示を確認

#### curlコマンドでの手動テスト

```bash
# 手動テストコマンド例の表示
./manual_test_commands.sh

# 実際のテスト実行
./manual_test_commands.sh run
```

## 追加されたAPIエンドポイント

### POST /debug/set_current

セッションの`exam_current`を直接設定するためのAPIエンドポイント。

**リクエスト例:**
```bash
curl -X POST -H "Content-Type: application/json" \
     -d '{"exam_current": 9}' \
     "http://localhost:5000/debug/set_current"
```

**レスポンス例:**
```json
{
  "success": true,
  "old_current": 0,
  "new_current": 9,
  "total_questions": 10,
  "message": "exam_current を 9 に設定しました（10問目）"
}
```

### GET /debug/session

現在のセッション状態を確認。

**レスポンス例:**
```json
{
  "exam_question_ids": [1234, 5678, 9012, ...],
  "exam_current": 0,
  "exam_category": "基礎科目",
  "selected_question_type": "basic",
  "selected_department": "",
  "selected_year": null
}
```

## 期待される動作

### 正常な場合

1. **9問目まで**: `is_last_question = false`、次の問題ボタンが表示される
2. **10問目**: `is_last_question = true`、次の問題ボタンが表示されない
3. **フィードバック画面**: 「最終問題です」「お疲れ様でした」等の表示

### 異常な場合

1. 10問目で`is_last_question = false`になる
2. 10問目で次の問題ボタンが表示される
3. 9問目以前で最終問題と判定される

## トラブルシューティング

### サーバー接続エラー

```
✗ サーバーに接続できません: 404
```

解決方法: Flask アプリケーション（app.py）を起動してください。

### セッション開始失敗

```
✗ セッション開始失敗: 500
```

解決方法: 
1. 問題データファイルが正しく配置されているか確認
2. サーバーログでエラー詳細を確認

### BeautifulSoup4 モジュールエラー

```
ModuleNotFoundError: No module named 'bs4'
```

解決方法:
```bash
pip install beautifulsoup4
```

## ファイル説明

- `test_10th_question_final.py`: セッション状態を直接操作する高速テスト
- `auto_10_questions.py`: 1問目から10問目まで自動回答するテスト
- `manual_test_commands.sh`: 手動テスト用のコマンド例
- `TEST_10TH_QUESTION_README.md`: このファイル

## 注意事項

- テスト実行前にセッションがクリアされる場合があります
- 複数のブラウザタブでセッションを使い回すとテスト結果に影響する可能性があります
- デバッグAPIは本番環境では無効化することを推奨します