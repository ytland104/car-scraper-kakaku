# グレード一覧自動取得ガイド

## 概要

車名・モデル年式のURLから、グレード一覧を自動で取得する方法を説明します。

## 基本的な使い方

### 方法1: URLから直接グレードを取得

```python
from carsensor_grade_extractor import CarsensorGradeExtractor

extractor = CarsensorGradeExtractor()

# URLからグレード一覧を取得
url = "https://www.carsensor.net/usedcar/bBM/s033/f002/index.html?ROUTEID=edge"
grades = extractor.get_grades_from_url(url, method='both')

# 結果を表示
for grade in grades:
    print(f"{grade['name']} (method: {grade['method']})")

# JSON/CSVに保存
extractor.save_grades(grades, 'grades.json')
extractor.export_grades_to_csv(grades, 'grades.csv')
```

### 方法2: コードからグレードを取得

```python
# メーカーコード、車種コード、モデル年式コードから取得
grades = extractor.get_grades_for_model(
    maker_code='BM',      # BMW
    model_code='033',     # M3セダン
    grade_code='002'   # 2014年02月～2018年12月モデル
)
```

## 辞書作成ツールとの統合

### 自動でグレードを取得して辞書に追加

```python
from carsensor_dictionary_manual import CarsensorDictionaryManager

manager = CarsensorDictionaryManager()
manager.dictionary = {
    'maker_code': 'BM',
    'maker_name': 'BMW',
    'models': {}
}

# 車種とモデル年式を追加
manager.add_model('BM', 'M3セダン', '033')
manager.add_model_year('033', '2014年02月～2018年12月', '002')

# グレードを自動取得して追加
manager.auto_fill_grades('BM', '033', '002')

# 辞書を保存
manager.save_dictionary('bmw_m3_with_grades.json')
```

## 抽出方法の選択

`get_grades_from_url()`の`method`パラメータで抽出方法を選択できます：

- **`'auto'`**: 自動で最適な方法を選択（デフォルト）
- **`'ui'`**: UI要素（チェックボックス、リンクなど）から抽出
- **`'listings'`**: 実際に表示されている車両リストから抽出
- **`'both'`**: 両方の方法を試して統合

```python
# UI要素から抽出
grades_ui = extractor.get_grades_from_url(url, method='ui')

# 車両リストから抽出
grades_listings = extractor.get_grades_from_url(url, method='listings')

# 両方から抽出
grades_both = extractor.get_grades_from_url(url, method='both')
```

## 実践例：トヨタ アルファード

```python
from carsensor_dictionary_manual import CarsensorDictionaryManager

manager = CarsensorDictionaryManager()
manager.dictionary = {
    'maker_code': 'TO',
    'maker_name': 'トヨタ',
    'models': {}
}

# アルファードを追加（実際のコードを確認して入力）
manager.add_model('TO', 'アルファード', '123')  # 実際のコード

# 40系を追加
manager.add_model_year('123', '40系', '001')  # 実際のコード

# グレードを自動取得
print("Auto-filling grades for Alphard 40系...")
num_grades = manager.auto_fill_grades('TO', '123', '001')
print(f"Added {num_grades} grades")

# 30系も追加
manager.add_model_year('123', '30系', '002')
manager.auto_fill_grades('TO', '123', '002')

# 辞書を保存
manager.save_dictionary('toyota_alphard_auto.json')
manager.export_to_flat_csv('toyota_alphard_auto.csv')
```

## グレード抽出の仕組み

### 1. UI要素からの抽出

ページ内のグレード選択UI（チェックボックス、リンクなど）からグレード一覧を取得します。

- 「グレード絞り込み」セクションを探す
- チェックボックスやリンクからグレード名を抽出

### 2. 車両リストからの抽出

実際に表示されている車両データからグレード名を抽出します。

- 各車両の車名からグレード部分を抽出
- サブテキストからもグレード情報を抽出
- 一意なグレード名のリストを作成

### 3. グレード名の抽出ロジック

車名からグレード名を抽出する際のロジック：

1. 車種名を除去（例: "M3セダン"を除去）
2. グレードキーワードを探す（例: "コンペティション", "エグゼクティブ"）
3. キーワードを含む部分をグレード名として抽出

## 注意事項

1. **コードの確認**: 車種コードとモデル年式コードは事前に確認が必要です
2. **抽出精度**: 車両リストからの抽出は、実際に表示されている車両に依存します
3. **グレードコード**: 自動抽出ではグレードコードが取得できない場合があります（連番で代替）
4. **ページ構造の変更**: サイトの構造が変更された場合、抽出ロジックの調整が必要です

## トラブルシューティング

### グレードが見つからない場合

1. URLが正しいか確認
2. ページに実際に車両が表示されているか確認
3. `method='both'`で両方の方法を試す
4. 手動でグレードを追加する

### 抽出されたグレード名が不正確な場合

1. 抽出ロジックを調整（`_extract_grade_from_car_name`メソッド）
2. 手動でグレード名を修正
3. 辞書を直接編集

## 関連ファイル

- `carsensor_grade_extractor.py`: グレード抽出ツール
- `carsensor_dictionary_manual.py`: 辞書管理ツール（グレード自動取得機能付き）

