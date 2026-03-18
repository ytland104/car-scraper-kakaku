# カーセンサー 車種辞書作成ガイド

## 概要

トヨタのアルファード、ヴェルファイアのように、車種・モデル年式（20系、30系、40系）・グレードの階層構造を持つ辞書を作成する方法を説明します。

## 辞書の構造

```json
{
  "maker_code": "TO",
  "maker_name": "トヨタ",
  "models": {
    "model_code": {
      "name": "アルファード",
      "code": "model_code",
      "model_years": {
        "my_code": {
          "name": "40系",
          "code": "my_code",
          "grades": {
            "grade_code": {
              "name": "エグゼクティブラウンジ",
              "code": "grade_code"
            }
          }
        }
      }
    }
  }
}
```

## コードの見つけ方

### ステップ1: メーカーコードを確認

カーセンサーのURLから確認：
- `https://www.carsensor.net/usedcar/bTO/` → `TO` = トヨタ
- `https://www.carsensor.net/usedcar/bBM/` → `BM` = BMW

### ステップ2: 車種コードを確認

1. カーセンサーのサイトでメーカーを選択
2. 車種一覧ページのURLを確認
   - 例: `https://www.carsensor.net/usedcar/bTO/s001/` → `001` = 車種コード
3. アルファードやヴェルファイアのリンクをクリックしてURLを確認

### ステップ3: モデル年式コードを確認

1. 車種ページでモデル年式（20系、30系、40系）を選択
2. URLを確認
   - 例: `https://www.carsensor.net/usedcar/bTO/s001/f001/` → `f001` = モデル年式コード

### ステップ4: グレードコードを確認

1. モデル年式ページでグレードを選択（ある場合）
2. URLを確認
   - グレードがURLに反映される場合は、そのコードを使用

## 辞書作成方法

### 方法1: 手動で辞書を作成

```python
from carsensor_dictionary_manual import CarsensorDictionaryManager

# 辞書マネージャーを作成
manager = CarsensorDictionaryManager()

# 辞書を初期化
manager.dictionary = {
    'maker_code': 'TO',
    'maker_name': 'トヨタ',
    'models': {}
}

# アルファードを追加
manager.add_model('TO', 'アルファード', '001')  # 実際のコードに置き換え

# 40系を追加
manager.add_model_year('001', '40系', '001')  # 実際のコードに置き換え

# グレードを追加
manager.add_grade('001', '001', 'エグゼクティブラウンジ', '001')
manager.add_grade('001', '001', 'エグゼクティブシート', '002')
manager.add_grade('001', '001', 'ロイヤルラウンジ', '003')

# 30系を追加
manager.add_model_year('001', '30系', '002')
manager.add_grade('001', '002', 'エグゼクティブラウンジ', '001')

# ヴェルファイアを追加
manager.add_model('TO', 'ヴェルファイア', '002')
manager.add_model_year('002', '40系', '001')
manager.add_grade('002', '001', 'エグゼクティブラウンジ', '001')

# 辞書を保存
manager.save_dictionary('toyota_alphard_vellfire.json')

# CSVにエクスポート
manager.export_to_flat_csv('toyota_alphard_vellfire.csv')
```

### 方法2: JSONファイルを直接編集

1. テンプレートを作成：
```python
from carsensor_dictionary_manual import create_dictionary_template
import json

template = create_dictionary_template()
with open('dictionary_template.json', 'w', encoding='utf-8') as f:
    json.dump(template, f, ensure_ascii=False, indent=2)
```

2. `dictionary_template.json`を編集して実際のコードを入力

3. 辞書を読み込んで使用：
```python
manager = CarsensorDictionaryManager()
manager.load_dictionary('dictionary_template.json')
```

## 辞書を使用したスクレイピング

### 全URLをスクレイピング

```python
from carsensor_dictionary_manual import CarsensorDictionaryManager

# 辞書を読み込み
manager = CarsensorDictionaryManager()
manager.load_dictionary('toyota_alphard_vellfire.json')

# 辞書に基づいて全てのURLをスクレイピング
combined_df = manager.scrape_all_from_dictionary(
    output_dir='output/toyota',
    max_cars_per_url=100
)
```

### 特定の車種のみスクレイピング

```python
# スクレイピングURL一覧を取得
urls = manager.get_all_scraping_urls()

# アルファードのみフィルタリング
alphard_urls = [u for u in urls if 'アルファード' in u['model_name']]

# 各URLをスクレイピング
from carsensor_url_pattern_scraper import CarsensorURLPatternScraper
scraper = CarsensorURLPatternScraper()

for url_info in alphard_urls:
    df = scraper.scrape_by_url_pattern(
        maker_code=url_info['maker_code'],
        model_code=url_info['model_code'],
        grade_code=url_info['grade_code'] or None
    )
    # 処理...
```

## 実践例：トヨタ アルファード・ヴェルファイア

### 完全な辞書例

```python
toyota_dict = {
    'maker_code': 'TO',
    'maker_name': 'トヨタ',
    'models': {
        'alphard_code': {  # 実際のコードに置き換え
            'name': 'アルファード',
            'code': 'alphard_code',
            'model_years': {
                '40系_code': {  # 実際のコードに置き換え
                    'name': '40系',
                    'code': '40系_code',
                    'grades': {
                        'exec_lounge_code': {
                            'name': 'エグゼクティブラウンジ',
                            'code': 'exec_lounge_code'
                        },
                        'exec_seat_code': {
                            'name': 'エグゼクティブシート',
                            'code': 'exec_seat_code'
                        },
                        'royal_lounge_code': {
                            'name': 'ロイヤルラウンジ',
                            'code': 'royal_lounge_code'
                        }
                    }
                },
                '30系_code': {
                    'name': '30系',
                    'code': '30系_code',
                    'grades': {
                        'exec_lounge_code': {
                            'name': 'エグゼクティブラウンジ',
                            'code': 'exec_lounge_code'
                        }
                    }
                },
                '20系_code': {
                    'name': '20系',
                    'code': '20系_code',
                    'grades': {}
                }
            }
        },
        'vellfire_code': {
            'name': 'ヴェルファイア',
            'code': 'vellfire_code',
            'model_years': {
                '40系_code': {
                    'name': '40系',
                    'code': '40系_code',
                    'grades': {}
                }
            }
        }
    }
}
```

## 注意事項

1. **コードの確認**: 実際のカーセンサーのサイトでコードを確認してください
2. **URL構造の変更**: サイトの構造が変更された場合、コードも変更される可能性があります
3. **サーバー負荷**: 大量のスクレイピングを行う場合は、適切な待機時間を設けてください
4. **データの正確性**: 辞書のコードが正しいか、実際にスクレイピングして確認してください

## トラブルシューティング

### コードが見つからない場合

1. ブラウザの開発者ツールを使用して、実際のURLを確認
2. ページのソースコードを確認して、リンクの構造を分析
3. カーセンサーのサイトマップを確認

### スクレイピングが失敗する場合

1. URLが正しいか確認
2. ページが存在するか確認
3. サイトの構造が変更されていないか確認

