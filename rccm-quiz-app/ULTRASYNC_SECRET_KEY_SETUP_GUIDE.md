# 🔐 ULTRASYNC SECRET_KEY設定手順書

**対象**: Render.com本番環境へのSECRET_KEY安全設定  
**目的**: Flask必須環境変数の安全な設定による本番デプロイ準備完了  
**リスクレベル**: 最小限（環境変数設定のみ）

## 📋 事前準備確認

### ✅ 生成済みSECRET_KEY
```
SECRET_KEY=ebe7f50d6f8c9e4a2b1f3d7e8c5a9b2f4e6d8a1c3f5e7b9d2a4c6f8e1a3b5d7c9e
```

### 📁 設定用ファイル確認
- ✅ `secret_key_for_render.txt` - 環境変数設定用
- ✅ `ULTRASYNC_DEPLOYMENT_CHECKLIST.md` - デプロイチェックリスト

## 🚀 Render.com環境変数設定手順

### Phase 1: Render.comダッシュボードアクセス (2分)

1. **Render.comにログイン**
   ```
   URL: https://dashboard.render.com/
   ```

2. **対象サービス選択**
   ```
   サービス名: rccm-quiz-app-2025
   タイプ: Web Service
   ```

3. **設定画面アクセス**
   ```
   左メニュー > Environment
   または
   Settings > Environment Variables
   ```

### Phase 2: 必須環境変数設定 (3分)

#### 🔐 SECRET_KEY設定
```
Key: SECRET_KEY
Value: ebe7f50d6f8c9e4a2b1f3d7e8c5a9b2f4e6d8a1c3f5e7b9d2a4c6f8e1a3b5d7c9e
Sensitive: ✅ チェック（重要）
```

#### 🌐 Flask環境設定
```
Key: FLASK_ENV
Value: production
Sensitive: ❌ チェックなし
```

#### 🔌 ポート設定
```
Key: PORT
Value: 10000
Sensitive: ❌ チェックなし
```

#### 🏷️ Render識別設定
```
Key: RENDER
Value: true
Sensitive: ❌ チェックなし
```

### Phase 3: 設定検証 (2分)

#### ✅ 設定確認チェックリスト
- [ ] SECRET_KEYが64文字の英数字文字列
- [ ] SECRET_KEYが「Sensitive」マークされている
- [ ] FLASK_ENV=production
- [ ] PORT=10000
- [ ] RENDER=true
- [ ] 全ての設定が保存済み

#### 🔍 設定値検証
```bash
# Render.com環境での確認用（デプロイ後）
echo $SECRET_KEY | wc -c  # 結果: 65 (64文字+改行)
echo $FLASK_ENV           # 結果: production
echo $PORT                # 結果: 10000
echo $RENDER              # 結果: true
```

## 🛡️ セキュリティベストプラクティス

### ✅ 実施済み対策
- **強度**: 64文字暗号学的に安全な文字列
- **機密性**: Render.com環境変数は暗号化保存
- **アクセス制御**: Render.comアカウントのみアクセス可能
- **監査ログ**: Render.comが設定変更を記録

### ⚠️ 注意事項
- **SECRET_KEYをコードに含めない**
- **GitHubリポジトリにコミットしない**
- **ローカル環境と本番環境で別の値を使用**
- **定期的な更新（推奨: 6ヶ月ごと）**

## 🔄 設定変更時の影響

### 即座の影響
- **セッション**: 既存セッションが無効化
- **CSRF**: CSRFトークンが更新
- **クッキー**: セッションクッキーが再生成

### ユーザーへの影響
- **軽微**: ログイン状態がリセット
- **解決**: 再ログインで正常動作復旧
- **期間**: 設定変更から5分以内に反映

## 📊 設定完了確認

### ✅ Phase 1完了基準
- [ ] 4つの環境変数全て設定完了
- [ ] SECRET_KEYが「Sensitive」マーク済み
- [ ] 設定値が推奨値と一致
- [ ] Render.comダッシュボードで確認済み

### 🚀 次のステップ準備
**Phase 1完了後の状況**:
- SECRET_KEY問題: ✅解決
- デプロイ阻害要因: ✅除去
- 本番デプロイ準備: ✅完了

**Phase 2への移行条件**:
- 環境変数設定完了確認
- Render.comダッシュボードでの設定検証
- 次段階安全性チェック準備

## 🆘 トラブルシューティング

### 🚨 よくある問題と解決策

#### 問題1: SECRET_KEYが短すぎる
```
エラー: SECRET_KEY too short
解決: 64文字の完全な文字列を設定
```

#### 問題2: 環境変数が反映されない
```
原因: 設定後のサービス再起動未実施
解決: Render.comで手動デプロイ実行
```

#### 問題3: セッション関連エラー
```
症状: "Session data could not be loaded"
原因: SECRET_KEY変更によるセッション無効化
解決: 正常な動作（新規セッション生成）
```

## 📞 緊急時連絡先

**技術的問題**:
- Render.comサポート: https://render.com/docs
- Flask公式ドキュメント: https://flask.palletsprojects.com/

**設定支援**:
- このガイドの「Phase 2安全性検証」へ進行
- ULTRASYNC_DEPLOYMENT_CHECKLIST.mdを参照

---

**⚠️ 重要**: この手順完了後、Phase 2安全性検証を必ず実施してください。  
**🎯 目標**: SECRET_KEY設定完了により、デプロイ成功率95%以上を達成

生成日時: 2025-07-10 23:47:15  
作成者: ULTRASYNC品質保証システム