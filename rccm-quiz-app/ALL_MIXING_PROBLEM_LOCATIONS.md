# 全問題混在の原因箇所リスト

## 検出された `load_questions()` 呼び出し箇所（25箇所）

これらすべてが問題混在を引き起こす可能性があります：

### 修正済み箇所
1. **行9354** - `quiz_department()` 関数内 ✅ 修正済み
2. **行9420** - `quiz_question()` 関数内 ✅ 修正済み

### 未修正の問題箇所（23箇所）

#### 高優先度（主要な問題表示機能）
3. **行4464** - `exam()` 関数内（specialist URLパラメーター処理）
4. **行5408** - `exam()` 関数内（緊急フォールバック処理）
5. **行6820** - 部門進捗計算処理
6. **行6874** - 部門データ存在チェック処理  
7. **行6962** - 問題種別カテゴリ処理
8. **行7119** - 不明な処理
9. **行7210** - 不明な処理
10. **行7303** - 不明な処理
11. **行7524** - 不明な処理
12. **行9314** - 不明な処理
13. **行9679** - `start_exam()` 関数内（全問題データ読み込み）
14. **行9691** - `start_exam()` 関数内（フォールバック処理）

#### 中優先度（サポート機能）
15. **行7107** - 不明な処理
16. **行7870** - 不明な処理
17. **行7888** - 不明な処理
18. **行7906** - 不明な処理
19. **行8091** - 不明な処理
20. **行8840** - 不明な処理
21. **行8923** - 不明な処理
22. **行10567** - モバイル最適化処理
23. **行10585** - モバイルキャッシュ処理
24. **行10718** - 不明な処理
25. **行12701** - 不明な処理
26. **行12706** - 不明な処理

## 修正が必要な理由

`load_questions()` 関数は **全問題データ** を読み込みます：
- 基礎科目 (4-1.csv)
- 全専門部門 (4-2_年度.csv) 
- 全年度データ

その後でフィルタリングしますが、以下の問題があります：
1. **IDベースの検索**で間違った問題を取得する可能性
2. **カテゴリマッピングの不整合**
3. **年度データの混在**
4. **部門マッピングテーブルの不一致**

## 必要な修正アプローチ

すべての箇所で `load_questions()` を以下に置き換える：
- 基礎科目の場合: `load_basic_questions_only()`
- 専門科目の場合: `get_department_questions_ultrasync(department, count)`

## 推定修正時間

- 各箇所の詳細調査: 1時間
- 修正実装: 3時間  
- テスト・検証: 2時間
- **合計: 6時間**

## 影響範囲

この修正により以下が解決される可能性：
- 森林土木部門で上水道問題が表示される問題
- 他の11部門でも発生している同様の混在問題
- 2週間継続している根本的な問題