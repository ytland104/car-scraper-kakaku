# カーセンサー スクレイピング ツール

カーセンサーエッジから中古車データをスクレイピングするためのツール集です。

## 📁 ファイル構成

### メインツール

- **`carsensor_scraper.py`** - 基本的なスクレイパー（単一URL用）
- **`carsensor_url_pattern_scraper.py`** - URLパターンから直接スクレイピング（推奨）
- **`carsensor_batch_scraper.py`** - バッチ処理用スクレイパー
- **`carsensor_selenium_scraper.py`** - Seleniumを使用したスクレイパー（ポップアップ操作）

### グレード・辞書ツール

- **`carsensor_grade_extractor.py`** - グレード一覧自動取得ツール
- **`carsensor_dictionary_manual.py`** - 辞書作成・管理ツール（推奨）
- **`carsensor_dictionary_builder.py`** - 辞書自動構築ツール
- **`find_car_codes.py`** - 車種コード検索ツール

### ガイド・ドキュメント

- **`カーセンサー使い方README.md`** - 使い方のまとめ（まずはこれを読む）
- **`簡単な使い方.md`** - 詳細な使い方ガイド
- **`carsensor_scraping_guide.md`** - スクレイピングガイド
- **`grade_extraction_guide.md`** - グレード抽出ガイド
- **`dictionary_creation_guide.md`** - 辞書作成ガイド

### クイックスタート

- **`簡単な例.py`** - すぐに使える簡単な例
- **`quick_start_guide.py`** - 対話形式のクイックスタート

## 🚀 すぐに始める

### 最も簡単な方法

```bash
python 簡単な例.py
```

### 基本的な使い方

```python
from carsensor_url_pattern_scraper import CarsensorURLPatternScraper

scraper = CarsensorURLPatternScraper()
df = scraper.scrape_by_url_pattern('BM', '033', '002', max_cars=31)
df.to_csv('result.csv', index=False, encoding='utf-8-sig')
```

## 📖 詳細な使い方

詳細は **`カーセンサー使い方README.md`** を参照してください。

## 📝 使用例

### 例1: 単一URLからスクレイピング

```python
from carsensor_url_pattern_scraper import CarsensorURLPatternScraper

scraper = CarsensorURLPatternScraper()
df = scraper.scrape_by_url_pattern('BM', '033', '002', max_cars=31)
```

### 例2: グレード一覧を自動取得

```python
from carsensor_grade_extractor import CarsensorGradeExtractor

extractor = CarsensorGradeExtractor()
url = "https://www.carsensor.net/usedcar/bBM/s033/f002/index.html?ROUTEID=edge"
grades = extractor.get_grades_from_url(url)
```

### 例3: 辞書を作成

```python
from carsensor_dictionary_manual import CarsensorDictionaryManager

manager = CarsensorDictionaryManager()
manager.dictionary = {'maker_code': 'TO', 'maker_name': 'トヨタ', 'models': {}}
manager.add_model('TO', 'アルファード', '実際のコード')
manager.add_model_year('実際のコード', '40系', '実際のコード')
manager.auto_fill_grades('TO', '実際のコード', '実際のコード')
```

## 🔍 コードの見つけ方

カーセンサーのサイトで車種を選択して、URLからコードを確認します。

例: `https://www.carsensor.net/usedcar/bBM/s033/f002/index.html`
- `bBM` = BMW（メーカーコード: BM）
- `s033` = M3セダン（車種コード: 033）
- `f002` = 2014年02月～2018年12月モデル（モデル年式コード: 002）

## ⚠️ 注意事項

1. **コードの確認**: 実際のカーセンサーのサイトでコードを確認してください
2. **サーバー負荷**: 大量のスクレイピングは避け、適切な待機時間を設けてください
3. **利用規約**: サイトの利用規約を確認してください







