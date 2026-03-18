#!/usr/bin/env python3
"""
カーセンサー スクレイピング クイックスタートガイド

実際に動作する簡単な例を示します
"""

from carsensor_grade_extractor import CarsensorGradeExtractor
from carsensor_dictionary_manual import CarsensorDictionaryManager
from carsensor_url_pattern_scraper import CarsensorURLPatternScraper

def example_1_simple_scraping():
    """例1: 最も簡単な方法 - 既知のURLから直接スクレイピング"""
    print("=" * 60)
    print("例1: 既知のURLから直接スクレイピング")
    print("=" * 60)
    
    scraper = CarsensorURLPatternScraper()
    
    # BMW M3セダンの例（既に分かっているURL）
    df = scraper.scrape_by_url_pattern(
        maker_code='BM',      # BMW
        model_code='033',     # M3セダン
        grade_code='002',     # 2014年02月～2018年12月モデル
        max_cars=10           # 最初の10台だけ
    )
    
    if not df.empty:
        print(f"\n✅ {len(df)}台のデータを取得しました")
        print("\n最初の3台:")
        print(df[['車名', '支払総額(万円)', '年式', '走行距離']].head(3))
        
        # CSVに保存
        output_file = 'example1_result.csv'
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"\n💾 データを保存しました: {output_file}")
    else:
        print("❌ データが取得できませんでした")


def example_2_extract_grades():
    """例2: URLからグレード一覧を自動取得"""
    print("\n" + "=" * 60)
    print("例2: URLからグレード一覧を自動取得")
    print("=" * 60)
    
    extractor = CarsensorGradeExtractor()
    
    # BMW M3セダンのページからグレードを取得
    url = "https://www.carsensor.net/usedcar/bBM/s033/f002/index.html?ROUTEID=edge"
    grades = extractor.get_grades_from_url(url, method='both')
    
    if grades:
        print(f"\n✅ {len(grades)}個のグレードが見つかりました:")
        for i, grade in enumerate(grades, 1):
            print(f"  {i}. {grade['name']}")
        
        # JSONに保存
        extractor.save_grades(grades, 'example2_grades.json')
    else:
        print("❌ グレードが見つかりませんでした")


def example_3_build_dictionary():
    """例3: 辞書を作成してグレードを自動取得"""
    print("\n" + "=" * 60)
    print("例3: 辞書を作成してグレードを自動取得")
    print("=" * 60)
    
    manager = CarsensorDictionaryManager()
    
    # 辞書を初期化
    manager.dictionary = {
        'maker_code': 'BM',
        'maker_name': 'BMW',
        'models': {}
    }
    
    # 車種を追加
    manager.add_model('BM', 'M3セダン', '033')
    print("✅ 車種を追加: M3セダン (code: 033)")
    
    # モデル年式を追加
    manager.add_model_year('033', '2014年02月～2018年12月', '002')
    print("✅ モデル年式を追加: 2014年02月～2018年12月 (code: 002)")
    
    # グレードを自動取得
    print("\n🔍 グレードを自動取得中...")
    num_grades = manager.auto_fill_grades('BM', '033', '002')
    
    if num_grades > 0:
        print(f"✅ {num_grades}個のグレードを追加しました")
        
        # 辞書を保存
        manager.save_dictionary('example3_dictionary.json')
        manager.export_to_flat_csv('example3_dictionary.csv')
        
        print("\n📋 辞書の内容:")
        for model_code, model_data in manager.dictionary['models'].items():
            print(f"  車種: {model_data['name']}")
            for my_code, my_data in model_data['model_years'].items():
                print(f"    モデル年式: {my_data['name']}")
                for grade_code, grade_data in my_data.get('grades', {}).items():
                    print(f"      グレード: {grade_data['name']}")
    else:
        print("❌ グレードが見つかりませんでした")


def example_4_scrape_from_dictionary():
    """例4: 辞書を使って一括スクレイピング"""
    print("\n" + "=" * 60)
    print("例4: 辞書を使って一括スクレイピング")
    print("=" * 60)
    
    # まず辞書を作成（例3と同じ）
    manager = CarsensorDictionaryManager()
    manager.dictionary = {
        'maker_code': 'BM',
        'maker_name': 'BMW',
        'models': {}
    }
    
    manager.add_model('BM', 'M3セダン', '033')
    manager.add_model_year('033', '2014年02月～2018年12月', '002')
    manager.auto_fill_grades('BM', '033', '002')
    
    # 辞書に基づいてスクレイピング
    print("\n🚗 辞書に基づいてスクレイピング中...")
    combined_df = manager.scrape_all_from_dictionary(
        output_dir='output/example4',
        max_cars_per_url=5  # 各グレードから5台ずつ
    )
    
    if not combined_df.empty:
        print(f"\n✅ 合計 {len(combined_df)}台のデータを取得しました")
        print(f"💾 データは output/example4/ に保存されました")
    else:
        print("❌ データが取得できませんでした")


def show_usage_guide():
    """使い方ガイドを表示"""
    print("\n" + "=" * 60)
    print("📖 使い方ガイド")
    print("=" * 60)
    print("""
【基本的な流れ】

1. URLが分かっている場合:
   → example_1_simple_scraping() を実行
   → 直接スクレイピングできます

2. グレード一覧を取得したい場合:
   → example_2_extract_grades() を実行
   → URLからグレード一覧を自動取得

3. 辞書を作成したい場合:
   → example_3_build_dictionary() を実行
   → 車種・モデル年式を追加して、グレードを自動取得

4. 辞書を使って一括スクレイピング:
   → example_4_scrape_from_dictionary() を実行
   → 辞書に基づいて全グレードをスクレイピング

【コードの見つけ方】

1. カーセンサーのサイトを開く
2. 車種を選択してURLを確認
   - 例: /usedcar/bBM/s033/ → BM=メーカー, 033=車種コード
3. モデル年式を選択してURLを確認
   - 例: /usedcar/bBM/s033/f002/ → 002=モデル年式コード

【トヨタ アルファード・ヴェルファイアの場合】

1. まず実際のコードを確認:
   - https://www.carsensor.net/usedcar/bTO/index.html?ROUTEID=edge
   - アルファードやヴェルファイアのリンクをクリック
   - URLからコードを確認

2. コードが分かったら:
   manager.add_model('TO', 'アルファード', '実際のコード')
   manager.add_model_year('実際のコード', '40系', '実際のコード')
   manager.auto_fill_grades('TO', '実際のコード', '実際のコード')
""")


def main():
    """メイン処理 - 全ての例を実行"""
    print("\n" + "=" * 60)
    print("🚗 カーセンサー スクレイピング クイックスタート")
    print("=" * 60)
    
    # 使い方ガイドを表示
    show_usage_guide()
    
    print("\n" + "=" * 60)
    print("実行する例を選択してください:")
    print("=" * 60)
    print("1. 既知のURLから直接スクレイピング（最も簡単）")
    print("2. URLからグレード一覧を自動取得")
    print("3. 辞書を作成してグレードを自動取得")
    print("4. 辞書を使って一括スクレイピング")
    print("5. 全て実行")
    print("0. 終了")
    
    choice = input("\n選択してください (0-5): ").strip()
    
    if choice == '1':
        example_1_simple_scraping()
    elif choice == '2':
        example_2_extract_grades()
    elif choice == '3':
        example_3_build_dictionary()
    elif choice == '4':
        example_4_scrape_from_dictionary()
    elif choice == '5':
        example_1_simple_scraping()
        example_2_extract_grades()
        example_3_build_dictionary()
        # example_4は時間がかかるのでスキップ
        print("\n例4は時間がかかるためスキップしました")
    elif choice == '0':
        print("終了します")
    else:
        print("無効な選択です")


if __name__ == "__main__":
    main()

