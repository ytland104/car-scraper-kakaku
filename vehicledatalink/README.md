# Car List Scraping Module

価格.com（kakaku.com）から自動車の車種・グレード・新車価格などの情報をスクレイピングして、CSV形式で保存するPythonモジュールです。

## 概要

このモジュールは、Jupyter Notebookから抽出された2つのモジュールを統合・整理したものです。指定されたCSVファイルから車両URLを読み込み、価格.comの各ページから詳細な車両データを取得して、構造化されたデータとして保存します。

## 機能

- CSVファイルから車両URLを読み込み
- データのクリーニング（重複削除、不要な文字列の削除）
- メーカーごとのURLグループ化
- Webスクレイピングによる車両データの収集
  - グレード名
  - 新車価格
  - モデル年
  - 掲載台数
  - Web Address（詳細ページURL）
- 全メーカーのデータを統合してCSVに出力

## インストール

### 必要なライブラリ

```bash
pip install -r requirements.txt
```

または個別にインストール：

```bash
pip install pandas requests beautifulsoup4
```

### 主な依存ライブラリ

- `pandas` (>=2.0.0): データ処理とCSVファイルの読み書き
- `requests` (>=2.31.0): HTTPリクエスト
- `beautifulsoup4` (>=4.12.0): HTMLパース

## ファイル構成

```
vehicledatalink/
├── Carlistscraping.py       # メインスクリプト
├── vehicle_data__.csv        # 入力CSVファイル（車両URL情報）
├── allmaker_urlYYYYMMDD.csv  # 出力CSVファイル（スクレイピング結果、日付付き）
├── requirements.txt          # 依存ライブラリのリスト
└── README.md                 # このファイル
```

## 入力ファイルの形式

`vehicle_data__.csv` には以下のカラムが必要です：

- `Maker`: メーカー名（例: トヨタ、ホンダ、BMW）
- `CarName`: 車名
- `URL`: 価格.comの車両ページURL
- `Unnamed: 4`: フィルタリング用フラグ（1.0 = 有効なデータ）

## 使用方法

### 基本的な使用方法

```bash
python Carlistscraping.py
```

### プログラムから呼び出す場合

```python
from Carlistscraping import load_and_clean_vehicle_data, scrape_all_makers

# CSVから車両データを読み込み
maker_urls = load_and_clean_vehicle_data("vehicle_data__.csv")

# 全メーカーのデータをスクレイピング
all_makers_df = scrape_all_makers(maker_urls)

# 結果を保存
all_makers_df.to_csv("output.csv", index=False, encoding="utf-8")
```

### 特定のメーカーのみをスクレイピング

```python
from Carlistscraping import scrape_maker_vehicles, load_and_clean_vehicle_data

# データ読み込み
maker_urls = load_and_clean_vehicle_data("vehicle_data__.csv")

# BMWのみをスクレイピング
if 'BMW' in maker_urls:
    bmw_df = scrape_maker_vehicles(maker_urls['BMW'], 'BMW')
    bmw_df.to_csv("bmw_vehicles.csv", index=False)
```

## 出力データの形式

出力されるCSVファイルには以下のカラムが含まれます：

| カラム名 | 説明 |
|---------|------|
| グレード名 | 車両のグレード名 |
| 新車価格 | 新車時の価格（万円単位、floatに変換済み） |
| Web Address | 詳細ページのURL |
| model | 元のモデル名（年モデル情報を含む） |
| モデル名 | 年モデルを除いたモデル名 |
| 年 | 年モデル（例: 2023年モデル） |
| CarMaker | メーカー名 |

## 主要な関数

### `load_and_clean_vehicle_data(csv_path: str) -> dict`

CSVファイルから車両データを読み込み、クリーニングを行います。

**引数:**
- `csv_path`: CSVファイルのパス

**戻り値:**
- メーカーごとのURLリストを含む辞書

### `get_html(url: str) -> BeautifulSoup`

指定されたURLからHTMLを取得し、BeautifulSoupオブジェクトを返します。

**引数:**
- `url`: スクレイピング対象のURL

**戻り値:**
- BeautifulSoupオブジェクト（失敗時はNone）

### `parse_vehicle_data(url: str, maker_name: str) -> pd.DataFrame`

指定されたURLから車両データを解析してDataFrameを返します。

**引数:**
- `url`: スクレイピング対象のURL
- `maker_name`: メーカー名

**戻り値:**
- 車両データを含むDataFrame（失敗時はNone）

### `scrape_maker_vehicles(vehicle_urls: list, maker_name: str) -> pd.DataFrame`

指定されたメーカーの車両データを全てスクレイピングします。

**引数:**
- `vehicle_urls`: スクレイピング対象のURLリスト
- `maker_name`: メーカー名

**戻り値:**
- 全車両データを含むDataFrame

### `scrape_all_makers(maker_urls: dict) -> pd.DataFrame`

全メーカーの車両データをスクレイピングします。

**引数:**
- `maker_urls`: メーカーごとのURLリストを含む辞書

**戻り値:**
- 全メーカーの車両データを含むDataFrame

### `main()`

メイン処理関数。CSVファイルから車両データを読み込み、スクレイピングを実行して結果をCSVファイルに保存します。

## 設定

スクリプト内の定数を変更することで動作をカスタマイズできます：

```python
INPUT_CSV = "vehicle_data__.csv"                                      # 入力CSVファイル名
OUTPUT_CSV = f"allmaker_url{datetime.now().strftime('%Y%m%d')}.csv"  # 出力CSVファイル名（日付付き）
MIN_SLEEP_TIME = 1                                                    # 最小待機時間（秒）
MAX_SLEEP_TIME = 3                                                    # 最大待機時間（秒）
```

出力ファイル名には実行日の日付が自動的に付与されます（例: `allmaker_url20241021.csv`）。

## 注意事項

1. **アクセス頻度**: サーバーへの負荷を考慮して、各リクエスト間に1〜3秒のランダムな待機時間を設けています。

2. **robots.txt**: スクレイピングを行う際は、対象サイトの`robots.txt`とサービス利用規約を確認してください。

3. **エラーハンドリング**: ネットワークエラーやHTTPエラーが発生した場合、そのURLをスキップして次のURLに進みます。

4. **データの正確性**: Webページの構造が変更された場合、スクレイピングが正常に動作しない可能性があります。

5. **文字エンコーディング**: 日本語を含むデータを扱うため、UTF-8エンコーディングを使用しています。

## トラブルシューティング

### エラー: `FileNotFoundError: vehicle_data__.csv`

入力CSVファイルが見つかりません。ファイルがスクリプトと同じディレクトリにあることを確認してください。

### エラー: `HTTP 403/404`

アクセスが拒否されたか、ページが見つかりませんでした。URLが正しいか、サイトのアクセス制限がないか確認してください。

### スクレイピングが途中で止まる

ネットワークエラーやサーバーの応答遅延が原因の可能性があります。`MIN_SLEEP_TIME`と`MAX_SLEEP_TIME`を増やすことで改善する場合があります。

## ライセンス

このスクリプトは個人使用を目的としています。商用利用する場合は、対象サイトの利用規約を確認してください。

## 開発履歴

- **v1.1** (2024-10-21): 出力ファイル名の改善
  - 出力CSVファイル名に実行日の日付を自動付与
  - ファイル名形式: `allmaker_urlYYYYMMDD.csv`

- **v1.0** (2024-10-16): Jupyter Notebookから2つのモジュールを統合し、コードを整理
  - 関数の分離とドキュメント化
  - 型ヒントの追加
  - エラーハンドリングの改善
  - 定数の定義
  - メイン処理の構造化
  - 未使用のimportを削除

## 作成者

このモジュールはJupyter Notebookの2つのセルから抽出・統合されたものです。

