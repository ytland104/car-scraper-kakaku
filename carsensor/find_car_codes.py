#!/usr/bin/env python3
"""
カーセンサー 車種コード検索ツール

カーセンサーのサイトから実際の車種コード、モデル年式コード、グレードコードを
見つけるためのヘルパーツール
"""

import requests
from bs4 import BeautifulSoup
import re
from typing import List, Dict, Optional

class CarCodeFinder:
    """車種コードを検索するクラス"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.base_url = "https://www.carsensor.net"
    
    def get_page(self, url: str) -> Optional[BeautifulSoup]:
        """ページを取得"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            print(f"Error: {e}")
            return None
    
    def find_maker_code(self, maker_name: str) -> Optional[str]:
        """メーカー名からメーカーコードを検索"""
        # 主要メーカーのコード辞書
        maker_codes = {
            'トヨタ': 'TO',
            'TOYOTA': 'TO',
            'BMW': 'BM',
            'メルセデスベンツ': 'MB',
            'ベンツ': 'MB',
            'MERCEDES': 'MB',
            'アウディ': 'AU',
            'AUDI': 'AU',
            'レクサス': 'LX',
            'LEXUS': 'LX',
            '日産': 'NS',
            'NISSAN': 'NS',
            'ホンダ': 'HD',
            'HONDA': 'HD'
        }
        
        for key, code in maker_codes.items():
            if key in maker_name.upper() or maker_name.upper() in key:
                return code
        
        return None
    
    def find_car_model(self, maker_code: str, car_name: str) -> List[Dict]:
        """車種名から車種コードを検索"""
        url = f"{self.base_url}/usedcar/b{maker_code}/index.html?ROUTEID=edge"
        soup = self.get_page(url)
        
        if not soup:
            return []
        
        results = []
        
        # 全てのリンクを確認
        links = soup.find_all('a', href=True)
        
        for link in links:
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            # 車種リンクを探す（/usedcar/b{MAKER}/s{CODE}/）
            if re.search(r'/usedcar/b[A-Z]+/s\d+', href):
                if car_name in text:
                    match = re.search(r'/s(\d+)/', href)
                    if match:
                        code = match.group(1)
                        results.append({
                            'name': text,
                            'code': code,
                            'url': href if href.startswith('http') else f"{self.base_url}{href}"
                        })
        
        return results
    
    def find_model_years(self, maker_code: str, model_code: str) -> List[Dict]:
        """モデル年式コードを検索"""
        url = f"{self.base_url}/usedcar/b{maker_code}/s{model_code}/index.html?ROUTEID=edge"
        soup = self.get_page(url)
        
        if not soup:
            return []
        
        results = []
        
        # パターン1: /usedcar/b{MAKER}/s{CODE}/f{GRADE}/ のリンク
        links = soup.find_all('a', href=re.compile(r'/usedcar/b[A-Z]+/s\d+/f\d+'))
        
        for link in links:
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            match = re.search(r'/f(\d+)/', href)
            if match:
                code = match.group(1)
                results.append({
                    'name': text,
                    'code': code,
                    'url': href if href.startswith('http') else f"{self.base_url}{href}"
                })
        
        # パターン2: lpSummary__itemクラス
        if not results:
            items = soup.find_all('a', class_='lpSummary__item')
            for item in items:
                img = item.find('img', alt=True)
                if img:
                    alt_text = img.get('alt', '')
                    href = item.get('href', '')
                    
                    if '/catalog/' not in href:
                        match = re.search(r'/f(\d+)/', href)
                        code = match.group(1) if match else ''
                        results.append({
                            'name': alt_text,
                            'code': code,
                            'url': href if href.startswith('http') else f"{self.base_url}{href}"
                        })
        
        return results
    
    def print_car_info(self, maker_name: str, car_name: str):
        """車種情報を表示"""
        print(f"\n=== Searching for {maker_name} {car_name} ===")
        
        # メーカーコードを取得
        maker_code = self.find_maker_code(maker_name)
        if not maker_code:
            print(f"❌ Maker code not found for: {maker_name}")
            print("Available makers: トヨタ, BMW, メルセデスベンツ, アウディ, レクサス, 日産, ホンダ")
            return
        
        print(f"✅ Maker code: {maker_code}")
        
        # 車種コードを検索
        models = self.find_car_model(maker_code, car_name)
        if not models:
            print(f"❌ Car model not found: {car_name}")
            print(f"\nPlease check the URL manually:")
            print(f"  {self.base_url}/usedcar/b{maker_code}/index.html?ROUTEID=edge")
            return
        
        print(f"\n✅ Found {len(models)} matching car model(s):")
        for model in models:
            print(f"  - {model['name']}: code={model['code']}")
            print(f"    URL: {model['url']}")
            
            # モデル年式を検索
            model_years = self.find_model_years(maker_code, model['code'])
            if model_years:
                print(f"    Model years ({len(model_years)}):")
                for my in model_years:
                    print(f"      - {my['name']}: code={my['code']}")
            else:
                print(f"    (No model years found - may need manual inspection)")


def main():
    """使用例"""
    finder = CarCodeFinder()
    
    # 例1: アルファードを検索
    finder.print_car_info('トヨタ', 'アルファード')
    
    # 例2: ヴェルファイアを検索
    finder.print_car_info('トヨタ', 'ヴェルファイア')
    
    # 例3: BMW M3を検索
    # finder.print_car_info('BMW', 'M3')


if __name__ == "__main__":
    main()

