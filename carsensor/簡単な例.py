#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
カーセンサー スクレイピング 最も簡単な例

このファイルを実行するだけで、すぐに使えます
"""

# ============================================
# 例1: 最も簡単 - URLから直接スクレイピング
# ============================================
def 例1_簡単なスクレイピング():
    """既にURLが分かっている場合"""
    from carsensor_url_pattern_scraper import CarsensorURLPatternScraper
    
    print("【例1】URLから直接スクレイピング")
    print("-" * 50)
    
    scraper = CarsensorURLPatternScraper()
    
    # BMW M3セダンの例
    df = scraper.scrape_by_url_pattern(
        maker_code='BM',      # BMW
        model_code='033',     # M3セダン
        grade_code='002',     # 2014年02月～2018年12月モデル
        max_cars=10           # 10台だけ取得
    )
    
    if not df.empty:
        print(f"✅ {len(df)}台のデータを取得しました")
        df.to_csv('結果1.csv', index=False, encoding='utf-8-sig')
        print("💾 結果1.csv に保存しました")
    else:
        print("❌ データが取得できませんでした")


# ============================================
# 例2: グレード一覧を取得
# ============================================
def 例2_グレード一覧取得():
    """URLからグレード一覧を自動取得"""
    from carsensor_grade_extractor import CarsensorGradeExtractor
    
    print("\n【例2】グレード一覧を自動取得")
    print("-" * 50)
    
    extractor = CarsensorGradeExtractor()
    
    # URLからグレードを取得
    url = "https://www.carsensor.net/usedcar/bBM/s033/f002/index.html?ROUTEID=edge"
    grades = extractor.get_grades_from_url(url)
    
    if grades:
        print(f"✅ {len(grades)}個のグレードが見つかりました:")
        for i, grade in enumerate(grades, 1):
            print(f"  {i}. {grade['name']}")
        extractor.save_grades(grades, 'グレード一覧.json')
        print("💾 グレード一覧.json に保存しました")
    else:
        print("❌ グレードが見つかりませんでした")


# ============================================
# 例3: 辞書を作成（トヨタ アルファードなど）
# ============================================
def 例3_辞書作成():
    """辞書を作成してグレードを自動取得"""
    from carsensor_dictionary_manual import CarsensorDictionaryManager
    
    print("\n【例3】辞書を作成（BMW M3セダンの例）")
    print("-" * 50)
    
    manager = CarsensorDictionaryManager()
    manager.dictionary = {
        'maker_code': 'BM',
        'maker_name': 'BMW',
        'models': {}
    }
    
    # 車種を追加
    manager.add_model('BM', 'M3セダン', '033')
    print("✅ 車種を追加: M3セダン")
    
    # モデル年式を追加
    manager.add_model_year('033', '2014年02月～2018年12月', '002')
    print("✅ モデル年式を追加: 2014年02月～2018年12月")
    
    # グレードを自動取得
    print("\n🔍 グレードを自動取得中...")
    num = manager.auto_fill_grades('BM', '033', '002')
    
    if num > 0:
        print(f"✅ {num}個のグレードを追加しました")
        manager.save_dictionary('辞書例.json')
        print("💾 辞書例.json に保存しました")
    else:
        print("❌ グレードが見つかりませんでした")


# ============================================
# メイン処理
# ============================================
if __name__ == "__main__":
    print("=" * 60)
    print("🚗 カーセンサー スクレイピング 簡単な例")
    print("=" * 60)
    print("\n実行する例を選んでください:")
    print("  1. 簡単なスクレイピング（URLが分かっている場合）")
    print("  2. グレード一覧を取得")
    print("  3. 辞書を作成")
    print("  4. 全て実行")
    
    choice = input("\n選択 (1-4): ").strip()
    
    if choice == '1':
        例1_簡単なスクレイピング()
    elif choice == '2':
        例2_グレード一覧取得()
    elif choice == '3':
        例3_辞書作成()
    elif choice == '4':
        例1_簡単なスクレイピング()
        例2_グレード一覧取得()
        例3_辞書作成()
    else:
        print("無効な選択です")

