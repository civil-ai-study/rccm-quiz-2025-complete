# RCCM問題集アプリ Ultimate Edition 🏗️
## 📊 テスト状況

![完走テスト](https://img.shields.io/badge/完走テスト-100%25-brightgreen)
![ペルソナテスト](https://img.shields.io/badge/ペルソナテスト-実行済み-blue)
![スクリーンショット比較](https://img.shields.io/badge/視覚的比較-96.67%25-green)
![セキュリティ](https://img.shields.io/badge/セキュリティ-修正済み-green)

**最終更新**: 2025-07-03 09:42:07

## 概要

RCCM試験対策アプリの完璧版です。
問題4-1（基礎択一問題）を中心に、効率的な学習を支援します。

### 主な特徴

- 🚀 **AI学習推奨システム** - 弱点分野を自動分析し、最適な学習プランを提案
- 📊 **詳細な統計分析** - 分野別・難易度別の学習進捗を可視化
- 💾 **LocalStorage対応** - 学習データを永続的に保存
- 📱 **PWA対応** - オフラインでも学習可能、ホーム画面に追加可能
- 🎨 **美しいUI/UX** - グラデーション、アニメーション、レスポンシブデザイン

## 技術スタック

### フロントエンド
- **HTML5** - セマンティックな構造
- **CSS3** - グラデーション、アニメーション、Flexbox/Grid
- **JavaScript (ES6+)** - モダンな記法、非同期処理
- **Papa Parse** - CSV解析
- **Chart.js** - データ可視化

### バックエンド（オプション）
- **Python Flask** - 軽量なWebフレームワーク
- **CSV** - 問題データ管理

### PWA技術
- **Service Worker** - オフライン対応、キャッシュ管理
- **Web App Manifest** - アプリのような体験
- **Push Notifications** - 学習リマインダー

## インストール方法

### 1. 基本セットアップ（静的ファイルのみ）

```bash
# プロジェクトフォルダ作成
mkdir rccm-quiz-app
cd rccm-quiz-app

# ファイル配置
├── index.html          # メインHTMLファイル
├── manifest.json       # PWAマニフェスト
├── sw.js              # Service Worker
├── data/
│   └── questions.csv  # 問題データ
└── icons/             # アイコンファイル
```

### 2. Python Flask版セットアップ

```bash
# 仮想環境作成
python -m venv venv

# 仮想環境有効化
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

# 必要なパッケージインストール
pip install flask

# アプリ起動
python app.py
```

### 3. 問題データの準備

`data/questions.csv`に100問の問題データが含まれています。
フォーマット：
```csv
id,category,question,option_a,option_b,option_c,option_d,correct_answer,explanation,reference,difficulty
```

## 使用方法

### 基本的な学習フロー

1. **ホーム画面**
   - 学習統計の確認
   - 今日の目標進捗
   - AI学習推奨の確認

2. **学習開始**
   - 「AI学習開始」ボタンで自動的に最適な問題を出題
   - 分野別学習も可能

3. **問題解答**
   - 4択から選択
   - 解答後に詳細な解説を表示
   - 正答率と解答時間を記録

4. **統計確認**
   - 分野別正答率
   - 学習トレンド
   - 弱点分野の特定

### 高度な機能

#### 🎯 弱点集中学習
正答率70%未満の分野を自動で抽出し、集中的に学習

#### 📥 データエクスポート
学習データをJSON形式でダウンロード可能

#### 🔄 オフライン対応
Service Workerにより、オフラインでも学習継続可能

## カスタマイズ方法

### 問題データの追加・編集

1. `data/questions.csv`を編集
2. 各フィールドを適切に入力
3. 文字コードはUTF-8（BOM付き）を推奨

### デザインのカスタマイズ

CSS変数を使用しているため、簡単にカラーテーマを変更可能：

```css
:root {
    --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    --success-gradient: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
    /* その他のカラー定義 */
}
```

### 機能の追加

`script.js`部分に新しい機能を追加可能：

```javascript
// 新機能の例
function addCustomFeature() {
    // カスタム機能の実装
}
```

## トラブルシューティング

### 問題が表示されない
- CSVファイルのパスを確認
- ブラウザのコンソールでエラーを確認
- CSVファイルの文字コードを確認（UTF-8推奨）

### LocalStorageが動作しない
- ブラウザの設定でLocalStorageが有効になっているか確認
- プライベートブラウジングモードでは動作しない場合があります

### PWAがインストールできない
- HTTPSで配信されているか確認
- manifest.jsonが正しく読み込まれているか確認
- Service Workerが正しく登録されているか確認

## ライセンス

このプロジェクトは教育目的で作成されています。
RCCM試験の過去問題の著作権は建設コンサルタンツ協会に帰属します。

## 貢献方法

1. Forkする
2. Feature branchを作成 (`git checkout -b feature/AmazingFeature`)
3. 変更をコミット (`git commit -m 'Add some AmazingFeature'`)
4. Branchにプッシュ (`git push origin feature/AmazingFeature`)
5. Pull Requestを作成

## 謝辞

- 建設コンサルタンツ協会
- RCCM資格試験受験者の皆様
- オープンソースコミュニティ

---

**注意事項**
- 本アプリは学習支援を目的としており、実際の試験問題とは異なる場合があります
- 最新の技術基準・法令については、必ず公式資料を確認してください
- 社内利用の場合は、所属組織の規定に従ってください

## 更新履歴

### v1.0.0 (2025-01-01)
- 初回リリース
- 100問の問題データ実装
- PWA対応
- AI学習推奨システム実装 