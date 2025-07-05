# ULTRATHIN Performance Test - Zero Side Effects

## 概要
このスクリプトは、ULTRATHIN区対応のRCCMクイズアプリケーションに対して、**副作用を一切起こさない**安全なパフォーマンステストを実行します。

## 安全保証
- ✅ 副作用を一切起こさない
- ✅ 既存システムに変更を加えない
- ✅ 負荷をかけすぎない（最大5同時接続）
- ✅ データ破壊は絶対に行わない
- ✅ メモリリークを起こさない

## 使用方法

### 1. 基本実行
```bash
python3 ultrathin_performance_test_zero_sideeffects.py
```

### 2. カスタムURL指定
```python
from ultrathin_performance_test_zero_sideeffects import UltraThinPerformanceTest

# カスタムURLでテスト実行
test = UltraThinPerformanceTest(base_url="http://your-app-url:5000")
results = test.run_comprehensive_test()
```

## 測定項目

### 1. 応答時間測定
- **ホームページ応答時間**: `/` エンドポイントの応答時間
- **部門選択応答時間**: `/departments` エンドポイントの応答時間
- **静的ファイル配信時間**: CSS、JS、アイコンファイルの応答時間
- **セッション作成時間**: 新規セッション作成時の応答時間

### 2. メモリ使用量監視
- **アプリケーション起動時メモリ**: ベースラインメモリ使用量
- **セッション作成時メモリ増加**: セッション作成による増加量
- **ガベージコレクション効果**: GC実行前後のメモリ変化
- **メモリリーク検出**: テスト期間中のメモリ使用量変化

### 3. 軽負荷テスト
- **同時接続数**: 最大5接続（軽負荷設定）
- **継続時間**: 最大30秒間のテスト
- **成功率**: リクエスト成功率の測定
- **スループット**: 1秒あたりのリクエスト処理数

### 4. リソース使用量測定
- **CPU使用率**: プロセスおよびシステムCPU使用率
- **CSVファイル読み込み時間**: 間接的測定
- **レスポンス生成時間**: 各エンドポイントのレスポンス時間

## 出力結果

### 1. コンソール出力
リアルタイムでテスト進行状況と結果概要を表示

### 2. テキストレポート
`ultrathin_performance_report_YYYYMMDD_HHMMSS.txt`
- 測定結果の概要
- 各テストの詳細結果
- エラーや警告の一覧

### 3. JSON詳細結果
`ultrathin_performance_results_YYYYMMDD_HHMMSS.json`
- 全測定データの詳細
- 各測定値のタイムスタンプ
- 統計情報

### 4. ログファイル
`ultrathin_performance_test.log`
- 実行ログ
- エラーログ
- デバッグ情報

## 実行例

```bash
$ python3 ultrathin_performance_test_zero_sideeffects.py

🚀 ULTRATHIN Performance Test Starting...
⚡ Zero Side Effects Mode - Safe Testing Guaranteed
--------------------------------------------------
2025-07-05 15:30:00,123 - INFO - UltraThin Performance Test initialized - Zero Side Effects Mode
2025-07-05 15:30:00,125 - INFO - Starting comprehensive performance test...
2025-07-05 15:30:00,126 - INFO - Running Homepage Response...
2025-07-05 15:30:01,234 - INFO - Completed Homepage Response
...

============================================================
ULTRATHIN Performance Test Report (Zero Side Effects)
============================================================
Test Date: 2025-07-05 15:30:45
Base URL: http://localhost:5000

TEST SUMMARY
--------------------
Total Duration: 45.23 seconds
Memory Change: +2.34 MB
Tests Run: 8

RESPONSE TIME RESULTS
-------------------------
homepage_response: 123.45ms (Status: 200)
departments_response: 156.78ms (Status: 200)

Static Files:
  static_enhanced_ui.css: 45.67ms
  static_main.js: 67.89ms
  static_favicon.ico: 23.45ms

MEMORY MONITORING
-----------------
Baseline: 125.67 MB
Average: 127.34 MB
Variation: 3.45 MB

LIGHT LOAD TEST
---------------
Total Requests: 20
Success Rate: 100.0%
Avg Response Time: 134.56ms
Requests/Second: 4.23

============================================================
Test completed with zero side effects guarantee
============================================================

📄 Report saved to: ultrathin_performance_report_20250705_153045.txt
✅ All tests completed successfully with zero side effects
```

## 注意事項

### 実行前の確認
1. アプリケーションが起動していることを確認
2. 必要なライブラリがインストールされていることを確認
   ```bash
   pip install requests psutil
   ```

### 安全機能
- **自動停止**: 異常検出時の自動停止
- **リソース制限**: CPU・メモリ使用量の上限設定
- **タイムアウト**: 各リクエストのタイムアウト設定
- **例外処理**: 全ての処理に例外処理を実装

### トラブルシューティング
1. **接続エラー**: アプリケーションの起動状態を確認
2. **権限エラー**: 実行権限を確認
3. **メモリ不足**: システムメモリ使用量を確認

## ライセンス
このスクリプトは、RCCMクイズアプリケーションのパフォーマンス監視専用です。