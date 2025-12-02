"""
Car List Scraping Module

価格.comから車両データをスクレイピングして、
車種・グレード・新車価格などの情報を収集するモジュール。
"""

import random
from datetime import datetime
from time import sleep

import pandas as pd
import requests
from bs4 import BeautifulSoup

# Constants
INPUT_CSV = "vehicle_data___.csv"
OUTPUT_CSV = f"allmaker_url{datetime.now().strftime('%Y%m%d')}.csv"
MIN_SLEEP_TIME = 1
MAX_SLEEP_TIME = 3

def load_and_clean_vehicle_data(csv_path: str) -> dict:
    """
    CSVファイルから車両データを読み込み、クリーニングを行う。
    
    Args:
        csv_path: CSVファイルのパス
        
    Returns:
        メーカーごとのURLリストを含む辞書
    """
    # Read vehicle data from CSV file
    vehicle_urls = pd.read_csv(csv_path, encoding="utf-8")
    
    # Remove duplicates based on 'URL' and filter by 'Unnamed: 4' column
    cleaned_vehicle_urls = vehicle_urls.drop_duplicates('URL')
    cleaned_vehicle_urls = cleaned_vehicle_urls[cleaned_vehicle_urls['Unnamed: 4'] == 1.0]
    
    # Clean 'CarName' column by replacing 'の中古車'
    cleaned_vehicle_urls['CarName'] = cleaned_vehicle_urls['CarName'].str.replace('の中古車', '')
    
    # Filter and clean data
    filter_df = cleaned_vehicle_urls.copy()
    filter_df['Maker'] = filter_df['Maker'].str.replace(r'\s*\([^)]*\)', '', regex=True)
    filter_df['CarName'] = filter_df.apply(
        lambda row: row['CarName'].replace(row['Maker'], ''), axis=1
    )
    filter_df['CarName'] = filter_df['CarName'].str.replace('の中古車', '').str.strip()
    
    # Display unique makers
    print("Found makers:", filter_df['Maker'].unique())
    
    # Group DataFrame by 'Maker' and create a dictionary of lists of URLs
    maker_urls = filter_df.groupby('Maker')['URL'].apply(list).to_dict()
    
    return maker_urls


def get_html(url: str) -> BeautifulSoup:
    """
    指定されたURLからHTMLを取得し、BeautifulSoupオブジェクトを返す。
    
    Args:
        url: スクレイピング対象のURL
        
    Returns:
        BeautifulSoupオブジェクト、または失敗時にNone
    """
    try:
        r = requests.get(url)
        if r.status_code == 200:
            return BeautifulSoup(r.content, "html.parser")
        else:
            print(f"Failed to fetch data: HTTP {r.status_code}")
            return None
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return None

def parse_vehicle_data(url: str, maker_name: str) -> pd.DataFrame:
    """
    指定されたURLから車両データを解析してDataFrameを返す。
    
    Args:
        url: スクレイピング対象のURL
        maker_name: メーカー名
        
    Returns:
        車両データを含むDataFrame、または失敗時にNone
    """
    soup = get_html(url)
    if soup is None:
        return None

    # ランダムな待機時間でサーバー負荷を軽減
    sleep_time = random.uniform(MIN_SLEEP_TIME, MAX_SLEEP_TIME)
    sleep(sleep_time)
    
    # グレードボックスとモデル名を取得
    grade_boxes = soup.select('.gradeBox')
    model_names = [model.text.strip() for model in soup.select('.modelName .modelNameInner a')]
    dfs = []

    # 各グレードボックスからデータを抽出
    for idx, box in enumerate(grade_boxes):
        headers = [th.text.strip() for th in box.select('th')]
        headers.append('Web Address')
        data = []

        # 各行のデータを抽出
        for row in box.select('tr')[1:]:
            cells = [td.text.strip() for td in row.select('td')]
            grade_name_link = row.select_one('.gradeName a')
            web_address = grade_name_link['href'] if grade_name_link else 'N/A'
            cells.append("https://kakaku.com" + str(web_address))
            data.append(cells)

        # DataFrameを作成してモデル名を追加
        df = pd.DataFrame(data, columns=headers)
        df['model'] = model_names[idx]
        print(f"Processing model: {df['model'].iloc[0] if not df.empty else 'N/A'}")
        dfs.append(df)

    # 全てのDataFrameを結合して整形
    final_df = pd.concat(dfs, ignore_index=True)
    final_df['新車価格'] = final_df['新車価格'].str.replace('万円', '').astype(float)
    final_df['モデル名'] = final_df['model'].str.extract(r'^(.*?)\s\d+年モデル')[0]
    final_df['年'] = final_df['model'].str.extract(r'(\d+年モデル)')[0]
    final_df['グレード名'] = final_df['グレード名\xa0(掲載台数)'].str.replace(r'\(\d+\)', '', regex=True).str.strip()
    final_df['CarMaker'] = maker_name

    return final_df

def scrape_maker_vehicles(vehicle_urls: list, maker_name: str) -> pd.DataFrame:
    """
    指定されたメーカーの車両データを全てスクレイピングする。
    
    Args:
        vehicle_urls: スクレイピング対象のURLリスト
        maker_name: メーカー名
        
    Returns:
        全車両データを含むDataFrame
    """
    all_dfs = []

    for url in vehicle_urls:
        try:
            df = parse_vehicle_data(url, maker_name)
            if df is not None and not df.empty:
                all_dfs.append(df)
        except Exception as e:
            print(f"Error processing URL {url}: {e}")
            continue

    combined_df = pd.concat(all_dfs, ignore_index=True) if all_dfs else pd.DataFrame()
    print(f"Completed scraping for {maker_name}")
    return combined_df


def scrape_all_makers(maker_urls: dict) -> pd.DataFrame:
    """
    全メーカーの車両データをスクレイピングする。
    
    Args:
        maker_urls: メーカーごとのURLリストを含む辞書
        
    Returns:
        全メーカーの車両データを含むDataFrame
    """
    all_makers_df = pd.DataFrame()
    
    for maker, urls in maker_urls.items():
        print(f"\nProcessing maker: {maker}")
        combined_df = scrape_maker_vehicles(urls, maker)
        
        if not combined_df.empty:
            all_makers_df = pd.concat([all_makers_df, combined_df], ignore_index=True)
    
    return all_makers_df


def main():
    """
    メイン処理：CSVファイルから車両データを読み込み、
    スクレイピングを実行して結果をCSVファイルに保存する。
    """
    print("=== Car List Scraping Started ===")
    
    # CSVファイルから車両データを読み込み
    print(f"Loading vehicle data from {INPUT_CSV}...")
    maker_urls = load_and_clean_vehicle_data(INPUT_CSV)
    
    # 全メーカーのデータをスクレイピング
    print(f"Starting scraping for {len(maker_urls)} makers...")
    all_makers_df = scrape_all_makers(maker_urls)
    
    # 結果をCSVファイルに保存
    print(f"\nSaving results to {OUTPUT_CSV}...")
    all_makers_df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")
    
    print(f"=== Scraping Completed ===")
    print(f"Total records: {len(all_makers_df)}")
    print(all_makers_df.head())


if __name__ == "__main__":
    main()