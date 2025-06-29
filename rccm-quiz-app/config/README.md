# RCCM Quiz App 設定ファイル管理

## 📝 部門マッピング設定 (`department_mapping.json`)

### 概要
RCCM Quiz Appの部門名とカテゴリ名の対応関係を定義する設定ファイルです。外部設定化により、ソースコード修正なしに部門設定を変更できます。

### 設定構造

#### `department_to_category_mapping`
部門名（英語）とカテゴリ名（日本語）の基本マッピング
```json
{
  "road": "道路",
  "tunnel": "トンネル",
  "river": "河川、砂防及び海岸・海洋"
}
```

#### `legacy_department_aliases`
旧部門名から新部門名への変換設定（後方互換性）
```json
{
  "civil_planning": "river",
  "urban_planning": "urban"
}
```

#### `department_details`
各部門の詳細情報
```json
{
  "road": {
    "full_name": "道路部門",
    "question_type": "specialist",
    "exam_code": "4-2",
    "priority": 1
  }
}
```

### 設定変更手順

1. **設定ファイル編集**
   ```bash
   # 設定ファイルを開く
   nano config/department_mapping.json
   ```

2. **新部門追加例**
   ```json
   {
     "department_to_category_mapping": {
       "existing_dept": "既存カテゴリ",
       "new_dept": "新しいカテゴリ"
     }
   }
   ```

3. **設定反映**
   - アプリケーション再起動不要
   - 自動リロード機能により即座に反映
   - エラー時は自動的に旧設定でフォールバック

### 検証ルール

#### 必須要件
- `department_to_category_mapping`セクション必須
- 各部門名は一意のカテゴリに対応
- 重複カテゴリは検証エラー

#### 推奨事項
- `meta`セクションでバージョン管理
- `validation_rules`で制約定義
- `department_details`で詳細情報管理

### 運用ベストプラクティス

#### 1. バージョン管理
```json
{
  "meta": {
    "version": "1.0.1",
    "last_updated": "2025-06-29",
    "changelog": "新部門追加: 情報システム"
  }
}
```

#### 2. 変更履歴記録
```bash
# Git での管理推奨
git add config/department_mapping.json
git commit -m "部門設定更新: 新部門追加"
```

#### 3. テスト環境での事前検証
```bash
# 設定検証スクリプト実行
python3 ultra_sync_department_config_manager.py
```

### トラブルシューティング

#### 設定エラー時の対処
1. **JSON構文エラー**
   - 設定ファイルのJSON構文確認
   - オンラインJSONバリデーター使用

2. **検証エラー**
   ```bash
   # 設定検証実行
   python3 ultra_sync_department_config_manager.py
   ```

3. **フォールバック動作**
   - エラー時は自動的にハードコード設定使用
   - ログで詳細エラー確認可能

#### ログ確認
```bash
# アプリケーションログ確認
tail -f rccm_app.log | grep department
```

### API エンドポイント

#### 設定状態確認
```bash
# 現在の設定状態確認
curl http://localhost:5000/api/department/config/status
```

#### 強制リロード
```bash
# 設定強制リロード
curl -X POST http://localhost:5000/api/department/config/reload
```

### 開発者向け情報

#### 設定管理クラス
- `UltraSyncDepartmentConfigManager`: メイン設定管理
- `UltraSyncAppIntegrationPatch`: app.py統合パッチ

#### 主要メソッド
```python
# 部門→カテゴリ変換
get_category_by_department(department)

# 部門名正規化
normalize_department_name(department)

# 設定リロード
reload_config()
```

#### 統合方法
```python
# 既存app.pyとの統合
from ultra_sync_app_integration_patch import apply_integration_patch
patch_system = apply_integration_patch()
```

### セキュリティ考慮事項

1. **ファイル権限**
   ```bash
   # 設定ファイル権限設定
   chmod 644 config/department_mapping.json
   ```

2. **バックアップ**
   ```bash
   # 定期バックアップ推奨
   cp config/department_mapping.json config/department_mapping.json.backup
   ```

3. **変更監査**
   - Git履歴で変更追跡
   - 重要変更時は事前承認推奨

## サポート

設定に関する質問や問題は、開発チームまでお問い合わせください。

---

*RCCM Quiz App Development Team*  
*Last Updated: 2025-06-29*