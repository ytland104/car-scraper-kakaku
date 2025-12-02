# 🚗 Enhanced Car Data Scraper

価格.comから車両データを効率的にスクレイピングする強化されたツールです。37のカーメーカーから任意に選択して処理できる柔軟な選択機能を搭載しています。

## 🚀 **簡単な使い方（推奨）**

### **1. カーメーカー一覧確認**
```bash
python3 -c "
from car_scraper import CarDataScraper
scraper = CarDataScraper()
scraper.display_carmaker_list()
"
```

### **2. 対話式でカーメーカー選択・処理**
```bash
python3 car_scraper.py
# メニューから選択肢2を選ぶ
```

### **3. 特定カーメーカーのみ処理**
```bash
python3 -c "
from car_scraper import CarDataScraper
scraper = CarDataScraper()
# トヨタ（インデックス0）のみ処理
scraper.process_by_carmaker(carmaker_indices=[0])
"
```

## 📁 **プロジェクト構造**

```
car_scraper/
├── car_scraper.py          # 🎯 メイン実行ファイル
├── allmaker_url1016.csv    # 📊 車両データソース
├── config/                  # ⚙️ 設定ファイル
│   ├── carmaker_selection.txt          # 現在の選択設定
│   ├── carmaker_selection_japanese.txt # 国産メーカー設定
│   ├── carmaker_selection_luxury.txt   # 高級車設定
│   └── README.md                       # 設定ファイル説明
├── output/                  # 📤 出力結果保存先
└── logs/                    # 📝 ログファイル
```

## 🔧 **詳細な使用方法**

### **対話式選択（最も簡単）**
```python
from car_scraper import CarDataScraper

scraper = CarDataScraper(csv_path="allmaker_url20251031.csv")
scraper.process_selected_carmakers(selection_method="interactive")

```

対話式選択では以下の入力方法をサポート：
- **個別指定**: `0,2,5,10`
- **範囲指定**: `0-5`
- **複数範囲**: `0-2,5-7,10-12`
- **メーカー名**: `トヨタ,日産,ホンダ`

### **設定ファイル使用**
```python
# 国産メーカーのみ処理
scraper.process_selected_carmakers(
    selection_method="config", 
    config_file="config/carmaker_selection_japanese.txt"
)
```

### **直接指定**
```python
# 特定のインデックスを直接指定
# selected_indices = [13,33,1,26]
selected_indices = [0,1,9,21,36]
scraper.process_selected_carmakers(
    selection_method="indices", 
    indices=selected_indices
)
```

## 📊 **カーメーカー一覧**

利用可能なカーメーカー（インデックス順）：
- `[ 0]` AMG (96件)
- `[ 1]` BMW (132件)
- `[ 2]` アウディ (155件)
- `[13]` トヨタ (496件) ← 最多
- `[21]` ホンダ (69件)
- `[33]` レクサス (259件)
- `[36]` 日産 (45件)

**全37カーメーカー**の詳細は実行時に確認できます。

## 🎯 **実行オプション**

### **メインメニュー（car_scraper.py実行時）**
1. **Test age filter functionality only** - 年齢フィルター機能テスト
2. **Interactive car maker selection** - 対話式カーメーカー選択（推奨）
3. **Quick test** - 特定カーメーカーのクイックテスト
4. **Compare old vs new method** - 新旧メソッド比較

## 📤 **出力設定**

```python
scraper = CarDataScraper(
    csv_path="allmaker_url1016.csv",
    output_dir="output"  # カスタム出力先
)
```

## 🛡️ **エラーハンドリング**

- **リトライ機構**: 失敗したリクエストの自動再試行
- **タイムアウト処理**: 長時間応答しないリクエストの処理
- **データ検証**: 不正なデータの検出と除外
- **詳細ログ**: 処理状況の詳細な記録

## 📈 **パフォーマンス**

- 改良されたHTTPセッション管理
- 効率的なエラー処理とリトライ
- 詳細な進捗追跡
- メモリ使用量の最適化

## 🚨 **注意事項**

1. **レート制限**: 適切な間隔でリクエストを送信
2. **データ量**: 多数のメーカーを選択する場合は十分な時間を確保
3. **ネットワーク**: 安定したインターネット接続が必要
4. **保存先**: 十分なディスク容量を確保

---

**🎯 基本的には `python3 car_scraper.py` を実行して、対話式で選択するのが最も簡単です！** 