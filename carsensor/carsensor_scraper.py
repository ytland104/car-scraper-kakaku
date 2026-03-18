#!/usr/bin/env python3
"""
カーセンサーエッジ 中古車データスクレイパー

指定されたURLから中古車データをスクレイピングしてCSVに出力します。
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time
import re
from typing import List, Dict, Optional

class CarsensorScraper:
    """カーセンサーエッジのスクレイパー"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ja,en-US;q=0.7,en;q=0.3',
        })
    
    def get_page(self, url: str) -> Optional[BeautifulSoup]:
        """ページを取得してBeautifulSoupオブジェクトを返す"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            print(f"Error fetching page: {e}")
            return None
    
    def extract_car_data(self, soup: BeautifulSoup) -> List[Dict]:
        """ページから中古車データを抽出"""
        cars = []
        
        # cassetteMainクラスの要素を全て取得（各車両のコンテナ）
        car_items = soup.find_all('div', class_='cassetteMain')
        print(f"Found {len(car_items)} car listings")
        
        for idx, car_item in enumerate(car_items, 1):
            try:
                car_data = {}
                
                # 車名
                title_elem = car_item.find('h3', class_='cassetteMain__title')
                if title_elem:
                    car_name_link = title_elem.find('a')
                    if car_name_link:
                        car_data['車名'] = car_name_link.get_text(strip=True)
                        car_data['詳細URL'] = 'https://www.carsensor.net' + car_name_link.get('href', '')
                    else:
                        car_data['車名'] = title_elem.get_text(strip=True)
                        car_data['詳細URL'] = ''
                else:
                    car_data['車名'] = ''
                    car_data['詳細URL'] = ''
                
                # サブテキスト（グレード情報など）
                sub_text_elem = car_item.find('p', class_='cassetteMain__subText')
                car_data['グレード・装備'] = sub_text_elem.get_text(strip=True) if sub_text_elem else ''
                
                # 支払総額
                total_price_elem = car_item.find('span', class_='totalPrice__mainPriceNum')
                if total_price_elem:
                    total_price_text = total_price_elem.get_text(strip=True)
                    car_data['支払総額(万円)'] = total_price_text
                else:
                    car_data['支払総額(万円)'] = ''
                
                # 車両本体価格
                base_price_elem = car_item.find('span', class_='basePrice__mainPriceNum')
                if base_price_elem:
                    base_price_text = base_price_elem.get_text(strip=True)
                    car_data['車両本体価格(万円)'] = base_price_text
                else:
                    car_data['車両本体価格(万円)'] = ''
                
                # 仕様情報（specListから抽出）
                spec_list = car_item.find('dl', class_='specList')
                if spec_list:
                    spec_boxes = spec_list.find_all('div', class_='specList__detailBox')
                    for spec_box in spec_boxes:
                        dt = spec_box.find('dt', class_='specList__title')
                        dd = spec_box.find('dd', class_='specList__data')
                        if dt and dd:
                            spec_title = dt.get_text(strip=True)
                            spec_data = dd.get_text(strip=True)
                            
                            if '年式' in spec_title:
                                car_data['年式'] = spec_data
                            elif '走行距離' in spec_title:
                                car_data['走行距離'] = spec_data
                            elif '車検' in spec_title:
                                car_data['車検'] = spec_data
                            elif '修復歴' in spec_title:
                                car_data['修復歴'] = spec_data
                            elif '保証' in spec_title:
                                car_data['保証'] = spec_data
                            elif '整備' in spec_title:
                                car_data['整備'] = spec_data
                            elif '排気量' in spec_title:
                                car_data['排気量'] = spec_data
                            elif 'ミッション' in spec_title:
                                car_data['ミッション'] = spec_data
                
                # ボディタイプと色
                body_info_list = car_item.find('ul', class_='carBodyInfoList')
                if body_info_list:
                    items = body_info_list.find_all('li', class_='carBodyInfoList__item')
                    for item in items:
                        text = item.get_text(strip=True)
                        if 'セダン' in text or 'クーペ' in text or 'SUV' in text:
                            car_data['ボディタイプ'] = text
                        elif any(color in text for color in ['白', '黒', '銀', '赤', '青', '緑', '黄', '茶', '灰']):
                            car_data['色'] = text
                
                # メーカー（固定値としてBMW）
                car_data['メーカー'] = 'BMW'
                car_data['車種'] = 'M3セダン'
                
                cars.append(car_data)
                print(f"  Extracted car {idx}: {car_data.get('車名', 'N/A')[:50]}")
                
            except Exception as e:
                print(f"  Error extracting car {idx}: {e}")
                continue
        
        return cars
    
    def scrape_cars(self, url: str, max_cars: int = 31) -> pd.DataFrame:
        """指定されたURLから中古車データをスクレイピング"""
        print(f"Scraping cars from: {url}")
        soup = self.get_page(url)
        
        if not soup:
            print("Failed to fetch page")
            return pd.DataFrame()
        
        cars = self.extract_car_data(soup)
        
        if not cars:
            print("No car data found. The page structure may have changed or data is loaded dynamically.")
            print("Please check the page structure manually.")
            return pd.DataFrame()
        
        df = pd.DataFrame(cars)
        return df[:max_cars] if len(df) > max_cars else df


def main():
    """メイン処理"""
    url = "https://www.carsensor.net/usedcar/bBM/s033/f002/index.html?ROUTEID=edge&SORT=1"
    
    scraper = CarsensorScraper()
    df = scraper.scrape_cars(url, max_cars=31)
    
    if not df.empty:
        output_file = f"carsensor_bmw_m3_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"\n✅ Data saved to: {output_file}")
        print(f"Total records: {len(df)}")
        print(df.head())
    else:
        print("\n❌ No data extracted. Please check the page structure.")


if __name__ == "__main__":
    main()

