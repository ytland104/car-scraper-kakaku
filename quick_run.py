#!/usr/bin/env python3
"""
Quick script to run specific car makers by index
"""

from car_scraper import CarDataScraper

def main():
    # 実行したいカーメーカーのインデックスをここで指定
    selected_indices = [1]  # ここを変更してください
    
    print(f"🚗 Processing car makers with indices: {selected_indices}")
    
    # スクレイパーを初期化
    scraper = CarDataScraper(
        csv_path="allmaker_url1016.csv",
        output_dir="/Users/yutaka/Documents/csv/expectedPrice"
    )   
    
    try:
        # データを読み込み
        print("📊 Loading data...")
        scraper.load_and_filter_data()
        
        # 選択されたカーメーカーの情報を表示
        carmaker_info = scraper.list_available_carmakers()
        print("\n✅ Selected car makers:")
        for idx in selected_indices:
            if idx < len(carmaker_info):
                maker_row = carmaker_info.iloc[idx]
                print(f"   [{idx:2d}] {maker_row['CarMaker']} ({maker_row['Record_Count']} records)")
            else:
                print(f"   ❌ Invalid index: {idx}")
        
        # 確認
        confirm = input("\nProceed with processing? (y/n): ").strip().lower()
        if confirm in ['y', 'yes']:
            # 処理開始
            scraper.process_selected_carmakers(
                selection_method="indices",
                indices=selected_indices
            )
            print("✅ Processing completed!")
        else:
            print("👋 Processing cancelled.")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        scraper.safe_shutdown()

if __name__ == "__main__":
    main() 