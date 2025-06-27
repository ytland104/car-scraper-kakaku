# 🚗 Enhanced Car Data Scraper

価格.comから車両データを効率的にスクレイピングする強化されたツールです。40以上のカーメーカーから任意に選択して処理できる柔軟な選択機能を搭載しています。

## ✨ 新機能

### 🔧 柔軟なカーメーカー選択機能

従来の固定的な処理範囲指定から、以下の方法でカーメーカーを選択できるようになりました：

1. **対話式選択** - メニューから選択
2. **設定ファイル** - 再利用可能な設定
3. **直接指定** - スクリプトでの自動化
4. **全処理** - すべてのメーカーを処理

## 🚀 使用方法

### 基本的な使い方

```python
from car_scraper import CarDataScraper

# スクレイパーを初期化
scraper = CarDataScraper(
    csv_path="allmaker_url1016.csv",
    output_dir="car_scraper/output"
)

# データを読み込み
scraper.load_and_filter_data()

# 対話式でカーメーカーを選択
scraper.process_selected_carmakers(selection_method="interactive")
```

### 方法1: 対話式選択（推奨）

```python
# 利用可能なカーメーカー一覧を表示
scraper.display_carmaker_list()

# 対話式で選択
scraper.process_selected_carmakers(selection_method="interactive")
```

対話式選択では以下の入力方法をサポート：
- **個別指定**: `0,2,5,10`
- **範囲指定**: `0-5`
- **複数範囲**: `0-2,5-7,10-12`
- **メーカー名**: `トヨタ,日産,ホンダ`

### 方法2: 設定ファイル使用

設定ファイル（例：`my_carmakers.txt`）を作成：
```text
# Car Maker Selection Configuration
# Format: One index per line, ranges (0-5), or car maker names

0   # トヨタ
2   # 日産
5   # ホンダ
10-12  # Range selection
# 15  # This line is commented out
```

使用方法：
```python
scraper.process_selected_carmakers(
    selection_method="config", 
    config_file="my_carmakers.txt"
)
```

### 方法3: 直接指定（スクリプト用）

```python
# 特定のインデックスを直接指定
selected_indices = [0, 2, 5, 8, 10]
scraper.process_selected_carmakers(
    selection_method="indices", 
    indices=selected_indices
)
```

### 方法4: バッチ処理

```python
# グループ別に処理
groups = {
    "japanese_luxury": [0, 1, 2],
    "european_brands": [10, 11, 12],
    "sports_cars": [20, 21, 22],
}

for group_name, indices in groups.items():
    scraper.process_selected_carmakers(
        selection_method="indices", 
        indices=indices
    )
```

## 📁 出力フォルダ設定

保存先フォルダは初期化時に指定できます：

```python
scraper = CarDataScraper(
    csv_path="allmaker_url1016.csv",
    output_dir="your/custom/output/path"  # カスタムパス
)
```

デフォルト: `car_scraper/output`

## 🔍 カーメーカー一覧確認

処理せずにカーメーカー一覧だけを確認：

```python
# フォーマットされた一覧を表示
scraper.display_carmaker_list()

# DataFrameとして取得
carmaker_info = scraper.list_available_carmakers()
print(carmaker_info)
```

## 💾 設定の保存と再利用

対話式選択後に設定を保存して再利用可能：

```python
# 対話式選択時に保存オプションが表示されます
scraper.process_selected_carmakers(selection_method="interactive")
# → "Save this selection for future use? (y/n)"

# 保存された設定を使用
scraper.process_selected_carmakers(
    selection_method="config", 
    config_file="saved_selection.txt"
)
```

## 📊 実行統計とエラー追跡

```python
# 統計情報を取得
stats = scraper.get_error_statistics()
print(f"Success Rate: {stats['success_rate_percent']}%")
print(f"Total Requests: {stats['total_requests']}")
print(f"Failed Requests: {stats['failed_requests']}")

# ログ出力
scraper.log_statistics()

# 統計をリセット
scraper.reset_statistics()
```

## 🛡️ エラーハンドリング強化

- **リトライ機構**: 失敗したリクエストの自動再試行
- **タイムアウト処理**: 長時間応答しないリクエストの処理
- **データ検証**: 不正なデータの検出と除外
- **詳細ログ**: 処理状況の詳細な記録

## 🎯 使用例

完全な使用例は `usage_example.py` を参照してください：

```bash
python usage_example.py
```

## ⚙️ 設定例

### 日本のメーカーのみ処理
```text
# japanese_makers.txt
0   # トヨタ
1   # 日産
2   # ホンダ
3   # マツダ
4   # スバル
```

### 高級車ブランドのみ
```text
# luxury_brands.txt
15-18  # European luxury brands
25-28  # Premium sports cars
```

### カスタムグループ
```python
# 自分だけの選択を保存
my_selection = [0, 5, 10, 15, 20, 25, 30]
scraper.save_carmaker_config(my_selection, "my_custom_selection.txt")
```

## 🚨 注意事項

1. **レート制限**: 適切な間隔でリクエストを送信
2. **データ量**: 多数のメーカーを選択する場合は十分な時間を確保
3. **ネットワーク**: 安定したインターネット接続が必要
4. **保存先**: 十分なディスク容量を確保

## 📈 パフォーマンス

- 改良されたHTTPセッション管理
- 効率的なエラー処理とリトライ
- 詳細な進捗追跡
- メモリ使用量の最適化

---

**📝 詳細な技術仕様やトラブルシューティングについては、コード内のドキュメンテーションを参照してください。** 