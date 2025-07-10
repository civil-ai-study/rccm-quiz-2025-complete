# RCCM専門部門名調査レポート

## 調査概要
app.pyファイルとtemplatesフォルダ内のファイルを詳しく調査し、実際にフロントエンドで使用されている12専門部門の正確な名前を特定しました。

## 1. DEPARTMENT_TO_CATEGORY_MAPPINGの内容

app.pyで定義されているDEPARTMENT_TO_CATEGORY_MAPPINGから、以下の12専門部門が確認されました：

```python
DEPARTMENT_TO_CATEGORY_MAPPING = {
    'road': '道路',
    'tunnel': 'トンネル', 
    'civil_planning': '河川、砂防及び海岸・海洋',
    'urban_planning': '都市計画及び地方計画',
    'landscape': '造園',
    'construction_env': '建設環境',
    'steel_concrete': '鋼構造及びコンクリート',
    'soil_foundation': '土質及び基礎',
    'construction_planning': '施工計画、施工設備及び積算',
    'water_supply': '上水道及び工業用水道',
    'forestry': '森林土木',
    'agriculture': '農業土木',
    'basic': '共通'  # 基礎科目
}
```

## 2. RCCMConfig.DEPARTMENTSの内容

config.pyで定義されているRCCMConfig.DEPARTMENTSから、12専門部門の詳細情報が確認されました：

```python
DEPARTMENTS = {
    'road': {'name': '道路', 'icon': '🛣️'},
    'tunnel': {'name': 'トンネル', 'icon': '🚇'},
    'civil_planning': {'name': '河川、砂防及び海岸・海洋', 'icon': '🌊'},
    'urban_planning': {'name': '都市計画及び地方計画', 'icon': '🏙️'},
    'landscape': {'name': '造園', 'icon': '🌸'},
    'construction_env': {'name': '建設環境', 'icon': '🌱'},
    'steel_concrete': {'name': '鋼構造及びコンクリート', 'icon': '🏗️'},
    'soil_foundation': {'name': '土質及び基礎', 'icon': '🪨'},
    'construction_planning': {'name': '施工計画、施工設備及び積算', 'icon': '📋'},
    'water_supply': {'name': '上水道及び工業用水道', 'icon': '💧'},
    'forestry': {'name': '森林土木', 'icon': '🌲'},
    'agriculture': {'name': '農業土木', 'icon': '🌾'},
    'basic': {'name': '共通', 'icon': '📚'}  # 基礎科目
}
```

## 3. テンプレートファイルで使用されている部門名

templates/departments.htmlで確認されたフロントエンド表示：
- 部門情報は`departments.items()`でループ処理
- 各部門の`dept_info.name`が表示名として使用
- 部門選択UI では日本語名称が表示される

## 4. start_examルートで受け付けている部門名のパターン

app.pyのstart_examルートで確認された処理：
- URLパラメータ`department`で部門指定
- `normalize_department_name()`関数で正規化
- `LEGACY_DEPARTMENT_ALIASES`で旧名称をサポート
- 英語キー（例：`road`）から日本語カテゴリ（例：`道路`）への変換

## 5. 4-2_*.csvファイル内で使用されているカテゴリー名

4-2_2016.csvファイルの分析結果：

```
各部門の問題数分布：
- 道路: 30問
- トンネル: 30問  
- 河川、砂防及び海岸・海洋: 30問
- 土質及び基礎: 30問
- 鋼構造及びコンクリート: 30問
- 河川、砂防及び海岸・海洋: 30問
- 都市計画及び地方計画: 30問
- 建設環境: 30問
- 造園: 30問
- 森林土木: 30問
- 農業土木: 30問
- 上水道及び工業用水道: 30問
- 施工計画、施工設備及び積算: 31問
```

## 結論：真の12専門部門名

### 英語キー → 日本語カテゴリ名のマッピング

1. **`road`** → **`道路`**
2. **`tunnel`** → **`トンネル`**
3. **`civil_planning`** → **`河川、砂防及び海岸・海洋`**
4. **`urban_planning`** → **`都市計画及び地方計画`**
5. **`landscape`** → **`造園`**
6. **`construction_env`** → **`建設環境`**
7. **`steel_concrete`** → **`鋼構造及びコンクリート`**
8. **`soil_foundation`** → **`土質及び基礎`**
9. **`construction_planning`** → **`施工計画、施工設備及び積算`**
10. **`water_supply`** → **`上水道及び工業用水道`**
11. **`forestry`** → **`森林土木`**
12. **`agriculture`** → **`農業土木`**

### 基礎科目
- **`basic`** → **`共通`** (4-1必須科目)

## テストで使用すべき部門名

### start_examルート用（英語キー）
- `road`, `tunnel`, `civil_planning`, `urban_planning`, `landscape`, `construction_env`, `steel_concrete`, `soil_foundation`, `construction_planning`, `water_supply`, `forestry`, `agriculture`, `basic`

### 問題フィルタリング用（日本語カテゴリ名）
- `道路`, `トンネル`, `河川、砂防及び海岸・海洋`, `都市計画及び地方計画`, `造園`, `建設環境`, `鋼構造及びコンクリート`, `土質及び基礎`, `施工計画、施工設備及び積算`, `上水道及び工業用水道`, `森林土木`, `農業土木`, `共通`

## 重要な発見

1. **一意性**: 全12部門が一意に定義されている
2. **一貫性**: 英語キー、日本語名、CSVカテゴリ名が一致している
3. **完全性**: 全部門に対応する問題データが存在する
4. **旧名称サポート**: LEGACY_DEPARTMENT_ALIASESで互換性を維持
5. **エラーハンドリング**: 無効な部門名に対する適切な処理

この情報を元に、正確な部門名でのテストを実施できます。