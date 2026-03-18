# カーセンサーエッジ スクレイピングガイド

## 概要

カーセンサーのサイトでは、ポップアップで車種・グレードを選択しますが、URLパターンを解析することで、直接アクセスしてデータを収集できます。

## URL構造の理解

カーセンサーのURLは以下のパターンです：

```
https://www.carsensor.net/usedcar/b{メーカーコード}/s{車種コード}/f{グレードコード}/index.html?ROUTEID=edge&SORT={ソート順}
```

### 例：
- `https://www.carsensor.net/usedcar/bBM/s033/f002/index.html?ROUTEID=edge&SORT=1`
  - `bBM` = BMW（メーカーコード）
  - `s033` = M3セダン（車種コード）
  - `f002` = 2014年02月～2018年12月モデル（グレード/年式コード）
  - `SORT=1` = 価格順（高い順）

## 推奨アプローチ

カーセンサーのポップアップで選択される車種・グレードごとにデータを収集するには、以下の3つの方法があります：

### 方法1: URLパターンを直接使用（推奨・最も確実）

URLパターンが分かっていれば、直接URLを構築してアクセスする方法が最も確実です。

### 方法2: 既知のコードリストを使用

メーカーコード・車種コード・グレードコードのリストを事前に用意して使用します。

### 方法3: Seleniumでポップアップを操作

JavaScriptで動的に生成されるポップアップを操作する方法（高度・時間がかかる）

---

## 使用方法

### 方法1: URLパターンを直接使用

#### 1-1. 特定の車種・グレードをスクレイピング

```python
from carsensor_url_pattern_scraper import CarsensorURLPatternScraper

scraper = CarsensorURLPatternScraper()

# BMW M3セダン 2014年02月～2018年12月モデルをスクレイピング
df = scraper.scrape_by_url_pattern(
    maker_code='BM',      # BMW
    model_code='033',     # M3セダン
    grade_code='002',     # 2014年02月～2018年12月モデル
    sort=1,               # 価格順（高い順）
    max_cars=31           # 最大31台
)

# CSVに保存
df.to_csv('bmw_m3_grade002.csv', index=False, encoding='utf-8-sig')
```

#### 1-2. 複数のグレードを一括スクレイピング

```python
# BMW M3セダンの複数グレードを一括スクレイピング
grade_codes = ['001', '002', '003']  # グレードコードのリスト
results = scraper.scrape_multiple_grades(
    maker_code='BM',
    model_code='033',
    grade_codes=grade_codes,
    output_dir='output/carsensor',  # 出力ディレクトリ
    max_cars_per_grade=50           # グレードごとの最大台数
)

# 結果は辞書形式で返される
# key: グレードコード, value: DataFrame
for grade_code, df in results.items():
    print(f"Grade {grade_code}: {len(df)} cars")
```

### 方法2: コード辞書を使用

```python
from carsensor_url_pattern_scraper import CarsensorURLPatternScraper, CAR_CODES

scraper = CarsensorURLPatternScraper()

# コード辞書から情報を取得
bmw_info = CAR_CODES['BMW']
m3_info = bmw_info['models']['M3セダン']

# 各グレードをスクレイピング
for grade_name, grade_code in m3_info['grades'].items():
    print(f"Scraping {grade_name}...")
    df = scraper.scrape_by_url_pattern(
        maker_code=bmw_info['code'],
        model_code=m3_info['code'],
        grade_code=grade_code
    )
    # 処理...
```

### 方法3: Seleniumでポップアップを操作（高度）

```python
from carsensor_selenium_scraper import CarsensorSeleniumScraper

# Seleniumを使用（ChromeDriverが必要）
scraper = CarsensorSeleniumScraper(headless=False)

try:
    # ポップアップで選択してスクレイピング
    df = scraper.scrape_with_popup_selection(
        maker_name='BMW',
        model_name='M3セダン',
        grade_name='2014年02月～2018年12月',
        max_cars=31
    )
    
    if not df.empty:
        df.to_csv('output.csv', index=False, encoding='utf-8-sig')
finally:
    scraper.close()  # 必ず閉じる
```

### 3. メーカー一覧を取得

```python
# 利用可能なメーカー一覧を取得
makers = scraper.get_maker_list()
for maker in makers:
    print(f"{maker['name']}: {maker['code']}")
```

### 4. 車種一覧を取得

```python
# 指定メーカーの車種一覧を取得
models = scraper.get_car_model_list('BM')  # BMW
for model in models:
    print(f"{model['name']}: {model['code']} ({model['count']}台)")
```

### 5. グレード一覧を取得

```python
# 指定車種のグレード/年式一覧を取得
grades = scraper.get_grade_list('BM', '033')  # BMW M3セダン
for grade in grades:
    print(f"{grade['name']}: {grade['code']}")
```

## メーカーコード一覧（主要）

| メーカー | コード |
|---------|--------|
| BMW | BM |
| メルセデスベンツ | MB |
| アウディ | AU |
| レクサス | LX |
| トヨタ | TO |
| 日産 | NS |
| ホンダ | HD |

## 車種コードの見つけ方

1. **ブラウザで確認する方法**:
   - カーセンサーのサイトで車種を選択
   - URLから `s` の後の数字を確認（例: `/s033/` → `033`）

2. **プログラムで取得する方法**:
   ```python
   models = scraper.get_car_model_list('BM')
   for model in models:
       if 'M3' in model['name']:
           print(f"Found: {model['name']} - Code: {model['code']}")
   ```

## グレードコードの見つけ方

1. **ブラウザで確認する方法**:
   - カーセンサーのサイトでグレード/年式を選択
   - URLから `f` の後の数字を確認（例: `/f002/` → `002`）

2. **プログラムで取得する方法**:
   ```python
   grades = scraper.get_grade_list('BM', '033')
   for grade in grades:
       print(f"{grade['name']}: {grade['code']}")
   ```

## 実践例：複数車種を一括スクレイピング

```python
from carsensor_batch_scraper import CarsensorBatchScraper
import pandas as pd

scraper = CarsensorBatchScraper()

# スクレイピング対象の車種リスト
target_models = [
    {'maker': 'BM', 'model': '033', 'grade': '002'},  # BMW M3セダン 2014-2018
    {'maker': 'BM', 'model': '033', 'grade': '001'},  # BMW M3セダン 2008-2014
    # 追加の車種...
]

all_data = []

for target in target_models:
    print(f"\nScraping {target['maker']} - {target['model']} - {target['grade']}")
    df = scraper.scrape_by_grade(
        maker_code=target['maker'],
        model_code=target['model'],
        grade_code=target['grade'],
        max_cars=100
    )
    
    if not df.empty:
        df['メーカーコード'] = target['maker']
        df['車種コード'] = target['model']
        df['グレードコード'] = target['grade']
        all_data.append(df)
    
    # サーバー負荷を軽減
    time.sleep(2)

# 全データを結合
if all_data:
    combined_df = pd.concat(all_data, ignore_index=True)
    combined_df.to_csv('all_cars_combined.csv', index=False, encoding='utf-8-sig')
    print(f"\n✅ Total records: {len(combined_df)}")
```

## 注意事項

1. **サーバー負荷**: リクエスト間に適切な待機時間を設けてください（`time.sleep(1-2)`）

2. **レート制限**: 過度なリクエストはIPアドレスのブロックにつながる可能性があります

3. **データの正確性**: サイトの構造が変更された場合、スクレイパーを更新する必要があります

4. **利用規約**: サイトの利用規約を確認し、遵守してください

## トラブルシューティング

### グレードが見つからない場合

```python
# グレードコードを指定せずにメインページをスクレイピング
df = scraper.scrape_by_grade('BM', '033', grade_code=None)
```

### URLが直接アクセスできない場合

一部のページはJavaScriptで動的に生成される可能性があります。その場合は、Seleniumなどのブラウザ自動化ツールの使用を検討してください。

## 関連ファイル

- `carsensor_scraper.py`: 単一URL用のスクレイパー
- `carsensor_batch_scraper.py`: バッチ処理用のスクレイパー（本ガイドで説明）

