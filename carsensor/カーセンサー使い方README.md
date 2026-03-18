# カーセンサー スクレイピング 使い方

## 🎯 すぐに始める

### 最も簡単な方法

```bash
python 簡単な例.py
```

対話形式で例を選択できます。

## 📖 3つの使い方

### 1️⃣ URLが分かっている場合（最も簡単）

カーセンサーのサイトで車種を選択して、URLからコードを確認します。

```python
from carsensor_url_pattern_scraper import CarsensorURLPatternScraper

scraper = CarsensorURLPatternScraper()

# データを取得
df = scraper.scrape_by_url_pattern(
    maker_code='BM',      # BMW
    model_code='033',     # M3セダン
    grade_code='002',     # 2014年02月～2018年12月モデル
    max_cars=31
)

# CSVに保存
df.to_csv('result.csv', index=False, encoding='utf-8-sig')
```

### 2️⃣ グレード一覧を自動取得

URLからグレード一覧を自動で取得します。

```python
from carsensor_grade_extractor import CarsensorGradeExtractor

extractor = CarsensorGradeExtractor()
url = "https://www.carsensor.net/usedcar/bBM/s033/f002/index.html?ROUTEID=edge"
grades = extractor.get_grades_from_url(url)

for grade in grades:
    print(grade['name'])
```

### 3️⃣ 辞書を作成（トヨタ アルファード・ヴェルファイアなど）

複数の車種・モデル年式・グレードを管理する辞書を作成します。

```python
from carsensor_dictionary_manual import CarsensorDictionaryManager

manager = CarsensorDictionaryManager()
manager.dictionary = {
    'maker_code': 'TO',
    'maker_name': 'トヨタ',
    'models': {}
}

# 車種を追加
manager.add_model('TO', 'アルファード', '実際のコード')

# モデル年式を追加
manager.add_model_year('実際のコード', '40系', '実際のコード')

# グレードを自動取得
manager.auto_fill_grades('TO', '実際のコード', '実際のコード')

# 保存
manager.save_dictionary('toyota_alphard.json')
```

## 🔍 コードの見つけ方

### ステップ1: カーセンサーのサイトを開く

例: `https://www.carsensor.net/usedcar/bTO/index.html?ROUTEID=edge`（トヨタ）

### ステップ2: 車種を選択してURLを確認

アルファードのリンクをクリック
- URL例: `/usedcar/bTO/s123/`
- `bTO` = トヨタ（メーカーコード: TO）
- `s123` = アルファード（車種コード: 123）

### ステップ3: モデル年式を選択してURLを確認

40系を選択
- URL例: `/usedcar/bTO/s123/f001/`
- `f001` = 40系（モデル年式コード: 001）

## 📁 ファイル一覧

| ファイル | 説明 |
|---------|------|
| `簡単な例.py` | すぐに使える簡単な例 |
| `quick_start_guide.py` | 対話形式のクイックスタート |
| `carsensor_url_pattern_scraper.py` | URLパターンから直接スクレイピング |
| `carsensor_grade_extractor.py` | グレード一覧自動取得 |
| `carsensor_dictionary_manual.py` | 辞書作成・管理ツール |
| `簡単な使い方.md` | 詳細な使い方ガイド |

## 🚀 実践例

### 例: BMW M3セダンのデータを取得

```python
from carsensor_url_pattern_scraper import CarsensorURLPatternScraper

scraper = CarsensorURLPatternScraper()
df = scraper.scrape_by_url_pattern('BM', '033', '002', max_cars=31)
df.to_csv('bmw_m3.csv', index=False, encoding='utf-8-sig')
print(f"✅ {len(df)}台のデータを取得しました")
```

### 例: トヨタ アルファードの全グレードを取得

```python
from carsensor_dictionary_manual import CarsensorDictionaryManager

manager = CarsensorDictionaryManager()
manager.dictionary = {'maker_code': 'TO', 'maker_name': 'トヨタ', 'models': {}}

# コードを確認してから実行
manager.add_model('TO', 'アルファード', '実際のコード')
manager.add_model_year('実際のコード', '40系', '実際のコード')
manager.auto_fill_grades('TO', '実際のコード', '実際のコード')
manager.save_dictionary('alphard.json')
```

## ⚠️ 注意事項

1. **コードの確認**: 実際のカーセンサーのサイトでコードを確認してください
2. **サーバー負荷**: 大量のスクレイピングは避け、適切な待機時間を設けてください
3. **利用規約**: サイトの利用規約を確認してください

## 📞 困ったときは

1. `python 簡単な例.py` を実行
2. `簡単な使い方.md` を読む
3. `quick_start_guide.py` を実行

