#!/usr/bin/env python3
"""
CSVファイルの違いを確認するテストスクリプト
問題：CSVファイルを変更しても対象車種数が変化しない理由を調査
"""

import sys
import os

# 現在のディレクトリをPythonパスに追加
sys.path.append('.')

try:
    from car_scraper import CarDataScraper
    print("✅ CarDataScraper のインポートに成功しました")
except ImportError as e:
    print(f"❌ インポートエラー: {e}")
    print("必要なライブラリがインストールされていない可能性があります")
    sys.exit(1)

def test_csv_differences():
    """2つのCSVファイルの違いをテストする"""
    
    print("="*60)
    print("🔍 CSVファイルの違いを確認するテスト")
    print("="*60)
    
    csv_files = [
        "allmaker_url1016.csv",
        "allmaker_url20251022.csv"
    ]
    
    results = {}
    
    for csv_file in csv_files:
        print(f"\n📁 テスト中: {csv_file}")
        print("-" * 40)
        
        if not os.path.exists(csv_file):
            print(f"❌ ファイルが見つかりません: {csv_file}")
            continue
            
        try:
            # 1. フィルターなしでデータを読み込み
            print("1️⃣ フィルターなしでデータを読み込み...")
            scraper = CarDataScraper(csv_path=csv_file)
            df_no_filter = scraper.load_data_without_filter()
            
            print(f"   総レコード数: {len(df_no_filter):,}")
            print(f"   カーメーカー数: {df_no_filter['CarMaker'].nunique()}")
            
            # 2. デフォルトフィルター（2005年以降）でデータを読み込み
            print("2️⃣ デフォルトフィルター（2005年以降）でデータを読み込み...")
            df_filtered = scraper.load_and_filter_data(min_year=2005, apply_filter=True)
            
            print(f"   フィルター後レコード数: {len(df_filtered):,}")
            print(f"   フィルター後カーメーカー数: {df_filtered['CarMaker'].nunique()}")
            
            # 3. フィルター前後の比較
            filtered_out = len(df_no_filter) - len(df_filtered)
            print(f"   フィルターで除外されたレコード数: {filtered_out:,}")
            print(f"   フィルター除外率: {filtered_out/len(df_no_filter)*100:.1f}%")
            
            # 4. カーメーカー別の詳細
            print("3️⃣ カーメーカー別レコード数（上位5位）:")
            maker_counts = df_no_filter['CarMaker'].value_counts()
            for i, (maker, count) in enumerate(maker_counts.head().items()):
                print(f"   {i+1}. {maker}: {count:,}件")
            
            # 結果を保存
            results[csv_file] = {
                'total_records': len(df_no_filter),
                'filtered_records': len(df_filtered),
                'unique_makers': df_no_filter['CarMaker'].nunique(),
                'filtered_makers': df_filtered['CarMaker'].nunique(),
                'filtered_out': filtered_out,
                'filter_rate': filtered_out/len(df_no_filter)*100
            }
            
        except Exception as e:
            print(f"❌ エラーが発生しました: {e}")
            continue
    
    # 5. 2つのCSVファイルの比較
    if len(results) == 2:
        print("\n" + "="*60)
        print("📊 2つのCSVファイルの比較結果")
        print("="*60)
        
        file1 = csv_files[0]
        file2 = csv_files[1]
        
        if file1 in results and file2 in results:
            r1 = results[file1]
            r2 = results[file2]
            
            print(f"\n📈 総レコード数の比較:")
            print(f"   {file1}: {r1['total_records']:,}")
            print(f"   {file2}: {r2['total_records']:,}")
            print(f"   差分: {r2['total_records'] - r1['total_records']:+,}")
            
            print(f"\n📈 フィルター後レコード数の比較:")
            print(f"   {file1}: {r1['filtered_records']:,}")
            print(f"   {file2}: {r2['filtered_records']:,}")
            print(f"   差分: {r2['filtered_records'] - r1['filtered_records']:+,}")
            
            print(f"\n📈 カーメーカー数の比較:")
            print(f"   {file1}: {r1['unique_makers']}")
            print(f"   {file2}: {r2['unique_makers']}")
            print(f"   差分: {r2['unique_makers'] - r1['unique_makers']:+}")
            
            print(f"\n📈 フィルター除外率の比較:")
            print(f"   {file1}: {r1['filter_rate']:.1f}%")
            print(f"   {file2}: {r2['filter_rate']:.1f}%")
            
            # 結論
            print(f"\n🎯 結論:")
            if r1['filtered_records'] == r2['filtered_records']:
                print("   ✅ フィルター後のレコード数が同じ → フィルター条件が原因")
                print("   💡 解決策: min_yearパラメータを調整するか、apply_filter=Falseを使用")
            else:
                print("   ✅ フィルター後のレコード数が異なる → CSVファイルの違いが反映されている")
    
    print("\n" + "="*60)
    print("🔧 推奨される使用方法")
    print("="*60)
    print("1. フィルターなしで全データを読み込み:")
    print("   scraper.load_data_without_filter()")
    print()
    print("2. 年数制限を調整:")
    print("   scraper.load_and_filter_data(min_year=2010, apply_filter=True)")
    print()
    print("3. CSVファイルを比較:")
    print("   scraper.compare_csv_files('file1.csv', 'file2.csv')")

if __name__ == "__main__":
    test_csv_differences()
