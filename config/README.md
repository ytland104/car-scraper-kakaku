# 📁 Config Files

このフォルダには、カーメーカー選択の設定ファイルが含まれています。

## 🚗 利用可能な設定ファイル

### 1. `carmaker_selection.txt`
現在の選択設定（AMG、BMW、その他選択済み）

### 2. `carmaker_selection_japanese.txt`
国産メーカーのみを選択する設定
- スズキ、スバル、ダイハツ、トヨタ、ホンダ、マツダ、レクサス、三菱、日産

### 3. `carmaker_selection_luxury.txt`
高級車ブランドのみを選択する設定
- アストンマーチン、フェラーリ、ベントレー、ポルシェ、マクラーレン、マセラティ、メルセデス、ランボルギーニ

### 4. `carmaker_selection_amg_bmw.txt`
AMGとBMWのみを選択する設定

### 5. `scheduler_config.yml`
スケジュール実行の設定ファイル

### 6. `environment_setup.sh`
環境設定用のシェルスクリプト

## 🔧 使用方法

```python
from car_scraper import CarDataScraper

scraper = CarDataScraper()

# 設定ファイルから読み込み
scraper.process_selected_carmakers(
    selection_method="config", 
    config_file="config/carmaker_selection_japanese.txt"
)
```

## 📝 カスタム設定の作成

新しい設定ファイルを作成する場合：

```text
# カスタム設定例
# コメント行は#で始める

0   # トヨタ
2   # 日産
5   # ホンダ
10-12  # 範囲指定
```

## ⚠️ 注意事項

- 設定ファイルはUTF-8エンコーディングで保存してください
- インデックス番号は0から始まります
- 範囲指定は「開始-終了」の形式で記述してください




