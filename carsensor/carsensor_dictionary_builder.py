#!/usr/bin/env python3
"""
カーセンサーエッジ 車種辞書ビルダー

車種・モデル・グレードの階層構造を持つ辞書を自動生成するツール
トヨタのアルファード、ヴェルファイアなどの複雑な階層構造に対応
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import re
import time
from typing import Dict, List, Optional
from datetime import datetime
from urllib.parse import urljoin

class CarsensorDictionaryBuilder:
    """カーセンサーの車種辞書を構築するクラス"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ja,en-US;q=0.7,en;q=0.3',
        })
        self.base_url = "https://www.carsensor.net"
        self.dictionary = {}
    
    def get_page(self, url: str) -> Optional[BeautifulSoup]:
        """ページを取得"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def extract_maker_code_from_url(self, url: str) -> Optional[str]:
        """URLからメーカーコードを抽出"""
        match = re.search(r'/b([A-Z]+)/', url)
        return match.group(1) if match else None
    
    def extract_model_code_from_url(self, url: str) -> Optional[str]:
        """URLから車種コードを抽出"""
        match = re.search(r'/s(\d+)/', url)
        return match.group(1) if match else None
    
    def extract_grade_code_from_url(self, url: str) -> Optional[str]:
        """URLからグレードコードを抽出"""
        match = re.search(r'/f(\d+)/', url)
        return match.group(1) if match else None
    
    def get_car_models_for_maker(self, maker_code: str) -> List[Dict]:
        """指定メーカーの車種一覧を取得"""
        url = f"{self.base_url}/usedcar/b{maker_code}/index.html?ROUTEID=edge"
        soup = self.get_page(url)
        
        if not soup:
            return []
        
        models = []
        
        # 様々なパターンで車種リンクを探す
        # パターン1: /usedcar/b{MAKER}/s{CODE}/ のリンク
        links = soup.find_all('a', href=re.compile(r'/usedcar/b[A-Z]+/s\d+'))
        
        for link in links:
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            # 車種コードを抽出
            model_code = self.extract_model_code_from_url(href)
            if not model_code:
                continue
            
            # 台数を抽出（例: "アルファード(123)" -> 123）
            count_match = re.search(r'\((\d+)\)', text)
            count = int(count_match.group(1)) if count_match else 0
            
            # 車種名をクリーンアップ
            model_name = re.sub(r'\(\d+\)', '', text).strip()
            
            models.append({
                'name': model_name,
                'code': model_code,
                'count': count,
                'url': urljoin(self.base_url, href) if href.startswith('/') else href
            })
        
        return models
    
    def get_model_years_for_car(self, maker_code: str, model_code: str) -> List[Dict]:
        """指定車種のモデル年式（20系、30系など）を取得"""
        url = f"{self.base_url}/usedcar/b{maker_code}/s{model_code}/index.html?ROUTEID=edge"
        soup = self.get_page(url)
        
        if not soup:
            return []
        
        model_years = []
        
        # パターン1: /usedcar/b{MAKER}/s{CODE}/f{GRADE}/ のリンク（グレード/年式）
        grade_links = soup.find_all('a', href=re.compile(r'/usedcar/b[A-Z]+/s\d+/f\d+'))
        
        for link in grade_links:
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            grade_code = self.extract_grade_code_from_url(href)
            if not grade_code:
                continue
            
            model_years.append({
                'name': text,
                'code': grade_code,
                'url': urljoin(self.base_url, href) if href.startswith('/') else href
            })
        
        # パターン2: lpSummary__itemクラス（年式選択肢）
        if not model_years:
            model_items = soup.find_all('a', class_='lpSummary__item')
            for item in model_items:
                img = item.find('img', alt=True)
                if img:
                    alt_text = img.get('alt', '')
                    href = item.get('href', '')
                    
                    # カタログリンクの場合はスキップ
                    if '/catalog/' in href:
                        continue
                    
                    # URLからグレードコードを抽出
                    grade_code = self.extract_grade_code_from_url(href)
                    
                    model_years.append({
                        'name': alt_text,
                        'code': grade_code or '',
                        'url': urljoin(self.base_url, href) if href.startswith('/') else href
                    })
        
        return model_years
    
    def get_grades_for_model_year(self, maker_code: str, model_code: str, 
                                 grade_code: str) -> List[Dict]:
        """指定モデル年式のグレード一覧を取得"""
        url = f"{self.base_url}/usedcar/b{maker_code}/s{model_code}/f{grade_code}/index.html?ROUTEID=edge"
        soup = self.get_page(url)
        
        if not soup:
            return []
        
        grades = []
        
        # ページからグレード情報を抽出
        # 実際のページ構造に応じて調整が必要
        # ここでは、ページタイトルやメタ情報からグレードを推測
        
        # ページタイトルから情報を取得
        title = soup.find('title')
        if title:
            title_text = title.get_text()
            # タイトルからグレード情報を抽出する処理を追加可能
        
        return grades
    
    def build_dictionary_for_maker(self, maker_code: str, maker_name: str = None) -> Dict:
        """指定メーカーの完全な辞書を構築"""
        print(f"\n=== Building dictionary for {maker_name or maker_code} ===")
        
        maker_dict = {
            'maker_code': maker_code,
            'maker_name': maker_name or maker_code,
            'models': {}
        }
        
        # 車種一覧を取得
        models = self.get_car_models_for_maker(maker_code)
        print(f"Found {len(models)} car models")
        
        for model in models:
            model_name = model['name']
            model_code = model['code']
            
            print(f"\n  Processing: {model_name} (code: {model_code})")
            
            model_dict = {
                'name': model_name,
                'code': model_code,
                'count': model['count'],
                'model_years': {}
            }
            
            # モデル年式一覧を取得
            model_years = self.get_model_years_for_car(maker_code, model_code)
            print(f"    Found {len(model_years)} model years/grades")
            
            for my in model_years:
                my_name = my['name']
                my_code = my['code']
                
                model_dict['model_years'][my_code or 'main'] = {
                    'name': my_name,
                    'code': my_code,
                    'url': my['url']
                }
            
            maker_dict['models'][model_code] = model_dict
            
            # サーバー負荷を軽減
            time.sleep(1)
        
        return maker_dict
    
    def build_dictionary_for_specific_models(self, maker_code: str, 
                                           target_model_names: List[str]) -> Dict:
        """特定の車種のみの辞書を構築（アルファード、ヴェルファイアなど）"""
        print(f"\n=== Building dictionary for specific models ===")
        
        maker_dict = {
            'maker_code': maker_code,
            'models': {}
        }
        
        # まず全車種を取得
        all_models = self.get_car_models_for_maker(maker_code)
        print(f"Found {len(all_models)} total car models")
        
        # 対象車種をフィルタリング
        target_models = []
        for model in all_models:
            for target_name in target_model_names:
                if target_name in model['name']:
                    target_models.append(model)
                    print(f"  Found target: {model['name']} (code: {model['code']})")
                    break
        
        # 対象車種の詳細を取得
        for model in target_models:
            model_name = model['name']
            model_code = model['code']
            
            print(f"\n  Processing: {model_name} (code: {model_code})")
            
            model_dict = {
                'name': model_name,
                'code': model_code,
                'count': model['count'],
                'model_years': {}
            }
            
            # モデル年式一覧を取得
            model_years = self.get_model_years_for_car(maker_code, model_code)
            print(f"    Found {len(model_years)} model years/grades")
            
            for my in model_years:
                my_name = my['name']
                my_code = my['code']
                
                model_dict['model_years'][my_code or 'main'] = {
                    'name': my_name,
                    'code': my_code,
                    'url': my['url']
                }
            
            maker_dict['models'][model_code] = model_dict
            
            time.sleep(1)
        
        return maker_dict
    
    def save_dictionary(self, dictionary: Dict, filename: str = None):
        """辞書をJSONファイルに保存"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            maker_code = dictionary.get('maker_code', 'unknown')
            filename = f"carsensor_dictionary_{maker_code}_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(dictionary, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ Dictionary saved to: {filename}")
        return filename
    
    def load_dictionary(self, filename: str) -> Dict:
        """辞書をJSONファイルから読み込み"""
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def export_to_csv(self, dictionary: Dict, filename: str = None):
        """辞書をCSV形式でエクスポート（フラットな構造）"""
        rows = []
        
        maker_code = dictionary.get('maker_code', '')
        maker_name = dictionary.get('maker_name', '')
        
        for model_code, model_data in dictionary.get('models', {}).items():
            model_name = model_data.get('name', '')
            model_count = model_data.get('count', 0)
            
            model_years = model_data.get('model_years', {})
            
            if not model_years:
                # モデル年式がない場合
                rows.append({
                    'メーカーコード': maker_code,
                    'メーカー名': maker_name,
                    '車種コード': model_code,
                    '車種名': model_name,
                    '台数': model_count,
                    'モデル年式コード': '',
                    'モデル年式名': '',
                    'グレードコード': '',
                    'グレード名': ''
                })
            else:
                # 各モデル年式ごとに行を作成
                for my_code, my_data in model_years.items():
                    my_name = my_data.get('name', '')
                    
                    rows.append({
                        'メーカーコード': maker_code,
                        'メーカー名': maker_name,
                        '車種コード': model_code,
                        '車種名': model_name,
                        '台数': model_count,
                        'モデル年式コード': my_code,
                        'モデル年式名': my_name,
                        'グレードコード': '',
                        'グレード名': ''
                    })
        
        df = pd.DataFrame(rows)
        
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            maker_code = dictionary.get('maker_code', 'unknown')
            filename = f"carsensor_dictionary_{maker_code}_{timestamp}.csv"
        
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"✅ CSV exported to: {filename}")
        return filename


def main():
    """使用例"""
    builder = CarsensorDictionaryBuilder()
    
    # 例1: トヨタのアルファードとヴェルファイアのみの辞書を構築
    print("=== Example 1: Building dictionary for Alphard and Vellfire ===")
    toyota_dict = builder.build_dictionary_for_specific_models(
        maker_code='TO',  # トヨタ
        target_model_names=['アルファード', 'ヴェルファイア', 'アルファ', 'ヴェル']
    )
    
    if toyota_dict.get('models'):
        # JSON形式で保存
        json_file = builder.save_dictionary(toyota_dict, 'toyota_alphard_vellfire.json')
        
        # CSV形式でエクスポート
        csv_file = builder.export_to_csv(toyota_dict, 'toyota_alphard_vellfire.csv')
        
        # 辞書の構造を表示
        print("\n=== Dictionary Structure ===")
        for model_code, model_data in toyota_dict['models'].items():
            print(f"\n{model_data['name']} (code: {model_code}, {model_data['count']} cars)")
            for my_code, my_data in model_data['model_years'].items():
                print(f"  - {my_data['name']} (code: {my_code})")
    else:
        print("No models found. The page structure may have changed.")
        print("Please check the maker code and try manual URL inspection.")


if __name__ == "__main__":
    main()

