#!/usr/bin/env python3
"""
カーセンサーエッジ バッチスクレイパー

車種・グレードごとにデータを収集するためのスクレイパー
ポップアップで選択される車種・グレードをURLパターンから直接アクセスする方法を実装
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time
import re
from typing import List, Dict, Optional, Tuple
from urllib.parse import urljoin, urlparse, parse_qs
import json

class CarsensorBatchScraper:
    """カーセンサーエッジのバッチスクレイパー"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ja,en-US;q=0.7,en;q=0.3',
        })
        self.base_url = "https://www.carsensor.net"
    
    def get_page(self, url: str) -> Optional[BeautifulSoup]:
        """ページを取得してBeautifulSoupオブジェクトを返す"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            print(f"Error fetching page {url}: {e}")
            return None
    
    def get_maker_list(self) -> List[Dict[str, str]]:
        """メーカー一覧を取得"""
        url = f"{self.base_url}/usedcar/shashu/index.html?ROUTEID=edge"
        soup = self.get_page(url)
        
        if not soup:
            return []
        
        makers = []
        # メーカーへのリンクを探す（例: /usedcar/bBM/）
        maker_links = soup.find_all('a', href=re.compile(r'/usedcar/b[A-Z]+/'))
        
        for link in maker_links:
            href = link.get('href', '')
            text = link.get_text(strip=True)
            # URLからメーカーコードを抽出（例: /usedcar/bBM/ -> BM）
            match = re.search(r'/b([A-Z]+)/', href)
            if match:
                maker_code = match.group(1)
                makers.append({
                    'name': text,
                    'code': maker_code,
                    'url': urljoin(self.base_url, href)
                })
        
        return makers
    
    def get_car_model_list(self, maker_code: str) -> List[Dict[str, str]]:
        """指定メーカーの車種一覧を取得"""
        url = f"{self.base_url}/usedcar/b{maker_code}/index.html?ROUTEID=edge"
        soup = self.get_page(url)
        
        if not soup:
            return []
        
        models = []
        # 車種へのリンクを探す（例: /usedcar/bBM/s033/）
        model_links = soup.find_all('a', href=re.compile(r'/usedcar/b[A-Z]+/s\d+/'))
        
        for link in model_links:
            href = link.get('href', '')
            text = link.get_text(strip=True)
            # URLから車種コードを抽出（例: /usedcar/bBM/s033/ -> s033）
            match = re.search(r'/s(\d+)/', href)
            if match:
                model_code = match.group(1)
                # 台数を抽出（例: "M3セダン(32)" -> 32）
                count_match = re.search(r'\((\d+)\)', text)
                count = count_match.group(1) if count_match else '0'
                
                models.append({
                    'name': re.sub(r'\(\d+\)', '', text).strip(),
                    'code': model_code,
                    'count': count,
                    'url': urljoin(self.base_url, href)
                })
        
        return models
    
    def get_grade_list(self, maker_code: str, model_code: str) -> List[Dict[str, str]]:
        """指定車種のグレード/年式一覧を取得"""
        url = f"{self.base_url}/usedcar/b{maker_code}/s{model_code}/index.html?ROUTEID=edge"
        soup = self.get_page(url)
        
        if not soup:
            return []
        
        grades = []
        # グレード/年式へのリンクを探す（例: /usedcar/bBM/s033/f002/）
        grade_links = soup.find_all('a', href=re.compile(r'/usedcar/b[A-Z]+/s\d+/f\d+/'))
        
        for link in grade_links:
            href = link.get('href', '')
            text = link.get_text(strip=True)
            # URLからグレードコードを抽出（例: /usedcar/bBM/s033/f002/ -> f002）
            match = re.search(r'/f(\d+)/', href)
            if match:
                grade_code = match.group(1)
                grades.append({
                    'name': text,
                    'code': grade_code,
                    'url': urljoin(self.base_url, href)
                })
        
        # グレードリンクが見つからない場合、lpSummary__itemから年式情報を取得
        if not grades:
            model_items = soup.find_all('a', class_='lpSummary__item')
            for item in model_items:
                img = item.find('img', alt=True)
                if img:
                    alt_text = img.get('alt', '')
                    href = item.get('href', '')
                    # カタログリンクの場合はスキップ
                    if '/catalog/' not in href:
                        grades.append({
                            'name': alt_text,
                            'code': '',
                            'url': urljoin(self.base_url, href) if href.startswith('/') else href
                        })
        
        return grades
    
    def extract_car_data(self, soup: BeautifulSoup) -> List[Dict]:
        """ページから中古車データを抽出（既存のメソッドを再利用）"""
        cars = []
        
        # cassetteMainクラスの要素を全て取得（各車両のコンテナ）
        car_items = soup.find_all('div', class_='cassetteMain')
        
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
                
                # サブテキスト（グレード情報など）
                sub_text_elem = car_item.find('p', class_='cassetteMain__subText')
                car_data['グレード・装備'] = sub_text_elem.get_text(strip=True) if sub_text_elem else ''
                
                # 支払総額
                total_price_elem = car_item.find('span', class_='totalPrice__mainPriceNum')
                if total_price_elem:
                    car_data['支払総額(万円)'] = total_price_elem.get_text(strip=True)
                
                # 車両本体価格
                base_price_elem = car_item.find('span', class_='basePrice__mainPriceNum')
                if base_price_elem:
                    car_data['車両本体価格(万円)'] = base_price_elem.get_text(strip=True)
                
                # 仕様情報
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
                
                cars.append(car_data)
                
            except Exception as e:
                print(f"  Error extracting car {idx}: {e}")
                continue
        
        return cars
    
    def scrape_by_grade(self, maker_code: str, model_code: str, grade_code: str = None, 
                       sort: int = 1, max_cars: int = None) -> pd.DataFrame:
        """指定された車種・グレードのデータをスクレイピング"""
        if grade_code:
            url = f"{self.base_url}/usedcar/b{maker_code}/s{model_code}/f{grade_code}/index.html?ROUTEID=edge&SORT={sort}"
        else:
            url = f"{self.base_url}/usedcar/b{maker_code}/s{model_code}/index.html?ROUTEID=edge&SORT={sort}"
        
        print(f"Scraping: {url}")
        soup = self.get_page(url)
        
        if not soup:
            return pd.DataFrame()
        
        cars = self.extract_car_data(soup)
        
        if not cars:
            return pd.DataFrame()
        
        df = pd.DataFrame(cars)
        if max_cars:
            df = df[:max_cars]
        
        return df
    
    def scrape_all_grades(self, maker_code: str, model_code: str, 
                         output_dir: str = "output", max_cars_per_grade: int = None) -> Dict[str, pd.DataFrame]:
        """指定車種の全グレードをスクレイピング"""
        print(f"\n=== Scraping all grades for {maker_code} - {model_code} ===")
        
        # グレード一覧を取得
        grades = self.get_grade_list(maker_code, model_code)
        
        if not grades:
            print("No grades found. Trying to scrape main model page...")
            # グレードが見つからない場合、メインページをスクレイピング
            df = self.scrape_by_grade(maker_code, model_code, max_cars=max_cars_per_grade)
            return {'main': df} if not df.empty else {}
        
        results = {}
        for grade in grades:
            print(f"\nProcessing grade: {grade['name']} ({grade['code']})")
            df = self.scrape_by_grade(maker_code, model_code, grade['code'], 
                                     max_cars=max_cars_per_grade)
            
            if not df.empty:
                # メタデータを追加
                df['メーカーコード'] = maker_code
                df['車種コード'] = model_code
                df['グレード名'] = grade['name']
                df['グレードコード'] = grade['code']
                
                results[grade['code'] or 'main'] = df
                
                # ファイルに保存
                if output_dir:
                    import os
                    os.makedirs(output_dir, exist_ok=True)
                    filename = f"{maker_code}_{model_code}_{grade['code'] or 'main'}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                    filepath = os.path.join(output_dir, filename)
                    df.to_csv(filepath, index=False, encoding='utf-8-sig')
                    print(f"  Saved: {filepath} ({len(df)} records)")
            
            # サーバー負荷を軽減
            time.sleep(1)
        
        return results


def main():
    """メイン処理 - 使用例"""
    scraper = CarsensorBatchScraper()
    
    # 例1: 特定の車種・グレードをスクレイピング
    print("=== Example 1: Scrape specific grade ===")
    df = scraper.scrape_by_grade('BM', '033', '002', max_cars=31)
    if not df.empty:
        output_file = f"carsensor_bmw_m3_grade002_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"✅ Saved: {output_file} ({len(df)} records)")
    
    # 例2: 特定車種の全グレードをスクレイピング
    print("\n=== Example 2: Scrape all grades ===")
    results = scraper.scrape_all_grades('BM', '033', output_dir='output/carsensor', max_cars_per_grade=50)
    print(f"\n✅ Completed: {len(results)} grades scraped")
    
    # 例3: メーカー一覧を取得
    print("\n=== Example 3: Get maker list ===")
    makers = scraper.get_maker_list()
    print(f"Found {len(makers)} makers")
    for maker in makers[:5]:
        print(f"  {maker['name']}: {maker['code']}")
    
    # 例4: 車種一覧を取得
    if makers:
        print("\n=== Example 4: Get car model list ===")
        models = scraper.get_car_model_list(makers[0]['code'])
        print(f"Found {len(models)} models for {makers[0]['name']}")
        for model in models[:5]:
            print(f"  {model['name']}: {model['code']} ({model['count']} cars)")


if __name__ == "__main__":
    main()

