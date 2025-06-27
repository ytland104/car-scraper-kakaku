#!/usr/bin/env python3
"""
Simple script to run the car scraper with different options
"""

from car_scraper import CarDataScraper

def main():
    # スクレイパーを初期化
    scraper = CarDataScraper(
        csv_path="allmaker_url1016.csv",
        output_dir="output"
    )
    
    try:
        # データを読み込み
        print("📊 Loading data...")
        scraper.load_and_filter_data()
        
        # カーメーカー一覧を表示
        print("\n📋 Available car makers:")
        scraper.display_carmaker_list()
        
        # 使い方の例を表示
        print("\n🔧 Usage Examples:")
        print("1. Interactive selection:")
        print("   scraper.process_selected_carmakers(selection_method='interactive')")
        print("\n2. Direct indices:")
        print("   scraper.process_selected_carmakers(selection_method='indices', indices=[0, 1, 2])")
        print("\n3. Config file:")
        print("   scraper.process_selected_carmakers(selection_method='config', config_file='my_selection.txt')")
        
        # 実際の選択と実行
        choice = input("\nDo you want to start processing? (y/n): ").strip().lower()
        if choice in ['y', 'yes']:
            # 対話式選択を開始
            scraper.process_selected_carmakers(selection_method="interactive")
        else:
            print("👋 Exiting without processing.")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        scraper.safe_shutdown()

if __name__ == "__main__":
    main() 