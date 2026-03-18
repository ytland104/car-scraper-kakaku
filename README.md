# 🚗 Enhanced Car Data Scraper

価格.comから車両データを効率的にスクレイピングする強化されたツールです。37のカーメーカーから任意に選択して処理できる柔軟な選択機能を搭載しています。

## 🐍 **仮想環境（推奨）**

このプロジェクトは **`/Users/yutaka/myenv/venv`** の仮想環境で動かす想定です。

### 手動で実行するとき
```bash
source /Users/yutaka/myenv/venv/bin/activate
cd /path/to/car_scraper   # または car_scraper_link
python main.py
```

国産メーカー設定（`mainbrand.txt`）でそのまま走ります。

### 仮想環境をまだ作っていない場合
```bash
python3 -m venv /Users/yutaka/myenv/venv
source /Users/yutaka/myenv/venv/bin/activate
pip install -r requirements.txt
```
既に `myenv/venv` を他プロジェクトと共有している場合は、そのまま `source` して `main.py` を実行すれば大丈夫です。

### cron（run_scheduler.sh）
`run_scheduler.sh` は **同じ仮想環境の python を直接指定**して動かします（cron では `source activate` が効きにくいため）。  
別の venv を使う場合は環境変数で上書きできます:
```bash
export CAR_SCRAPER_VENV=/path/to/your/venv
./run_scheduler.sh
```

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
├── main.py                 # 🎯 手動実行用エントリ（国産メーカー config で実行）
├── run_scheduler.sh        # ⏰ cron 用エントリ（仮想環境を利用）
├── car_scraper.py          # メインスクレイパーモジュール
├── scheduled_scraper.py    # 定期実行用ラッパー（cron から run_scheduler.sh 経由で利用）
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
from car_scraper import CarDataScraper
# 国産メーカーのみ処理
scraper = CarDataScraper()
scraper.process_selected_carmakers(selection_method="config", config_file="mainbrand.txt")
```

### **直接指定**
```python
from car_scraper import CarDataScraper
# 特定のインデックスを直接指定
# selected_indices = [13,33,1,26]
selected_indices = [0,1,9,21,36]
scraper = CarDataScraper()
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

## ⏰ **定期実行（cron）**

他プロジェクトと同様に、**cron からは `run_scheduler.sh` を叩く**方式にしています。

1. **実行権限を付与**
   ```bash
   chmod +x run_scheduler.sh
   ```
2. **cron の設定**（`crontab -e`）
   - `scripts/cron_template.txt` または `scripts/cron_fixed.txt` の内容をコピー
   - `BASE=` を、実際のプロジェクトパス（またはシンボリックリンク `car_scraper_link`）に合わせる

**cron が動かないときのチェックリスト**

- `car_scraper_link` を使っている場合、シンボリックリンクが正しくプロジェクトを指しているか
- `run_scheduler.sh` がプロジェクトルートにあり、実行権限があるか
- `logs/` が存在するか（`run_scheduler.sh` が自動作成します）
- macOS: システム環境設定 → プライバシーとセキュリティ → **フルディスクアクセス** に Terminal や cron を追加しているか

## 🖥️ **バックグラウンド実行**

このスクレイパーは **requests + BeautifulSoup のみ** 使用しており、ブラウザ（Selenium）は使っていません。  
そのため **ディスプレイ不要で、cron やバックグラウンドで問題なく動作** します（ヘッドレス対応は不要です）。

## 🚨 **注意事項**

1. **レート制限**: 適切な間隔でリクエストを送信
2. **データ量**: 多数のメーカーを選択する場合は十分な時間を確保
3. **ネットワーク**: 安定したインターネット接続が必要
4. **保存先**: 十分なディスク容量を確保

---

**🎯 基本的には `python3 car_scraper.py` を実行して、対話式で選択するのが最も簡単です！** 