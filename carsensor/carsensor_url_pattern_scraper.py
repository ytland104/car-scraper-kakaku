#!/usr/bin/env python3
"""
カーセンサーエッジ URLパターン直接アクセススクレイパー

ポップアップで選択される車種・グレードを、URLパターンから直接構築してアクセスする方法
最も確実で効率的な方法
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time
import re
from typing import List, Dict, Optional
from carsensor_scraper import CarsensorScraper

class CarsensorURLPatternScraper:
    """URLパターンから直接アクセスするスクレイパー"""
    
    def __init__(self):
        self.base_scraper = CarsensorScraper()
        self.base_url = "https://www.carsensor.net"
    
    def build_url(self, maker_code: str, model_code: str, grade_code: str = None, 
                 sort: int = 1) -> str:
        """
        URLを構築
        
        Args:
            maker_code: メーカーコード（例: 'BM' = BMW）
            model_code: 車種コード（例: '033' = M3セダン）
            grade_code: グレードコード（例: '002' = 2014年02月～2018年12月モデル）
            sort: ソート順（1=価格高い順, 2=価格安い順, など）
        
        Returns:
            構築されたURL
        """
        if grade_code:
            url = f"{self.base_url}/usedcar/b{maker_code}/s{model_code}/f{grade_code}/index.html?ROUTEID=edge&SORT={sort}"
        else:
            url = f"{self.base_url}/usedcar/b{maker_code}/s{model_code}/index.html?ROUTEID=edge&SORT={sort}"
        return url
    
    def scrape_by_url_pattern(self, maker_code: str, model_code: str, 
                            grade_code: str = None, sort: int = 1, 
                            max_cars: int = None) -> pd.DataFrame:
        """
        URLパターンから直接スクレイピング
        
        Args:
            maker_code: メーカーコード
            model_code: 車種コード
            grade_code: グレードコード（オプション）
            sort: ソート順
            max_cars: 最大取得台数
        
        Returns:
            スクレイピング結果のDataFrame
        """
        url = self.build_url(maker_code, model_code, grade_code, sort)
        return self.base_scraper.scrape_cars(url, max_cars)
    
    def scrape_multiple_grades(self, maker_code: str, model_code: str, 
                              grade_codes: List[str], output_dir: str = "output",
                              max_cars_per_grade: int = None) -> Dict[str, pd.DataFrame]:
        """
        複数のグレードを一括スクレイピング
        
        Args:
            maker_code: メーカーコード
            model_code: 車種コード
            grade_codes: グレードコードのリスト
            output_dir: 出力ディレクトリ
            max_cars_per_grade: グレードごとの最大台数
        
        Returns:
            グレードコードをキーとするDataFrameの辞書
        """
        results = {}
        
        for grade_code in grade_codes:
            print(f"\nScraping {maker_code}-{model_code}-{grade_code}...")
            df = self.scrape_by_url_pattern(
                maker_code, model_code, grade_code, 
                max_cars=max_cars_per_grade
            )
            
            if not df.empty:
                # メタデータを追加
                df['メーカーコード'] = maker_code
                df['車種コード'] = model_code
                df['グレードコード'] = grade_code
                
                results[grade_code] = df
                
                # ファイルに保存
                import os
                os.makedirs(output_dir, exist_ok=True)
                filename = f"{maker_code}_{model_code}_{grade_code}_{datetime.now().strftime('%Y%m%d')}.csv"
                filepath = os.path.join(output_dir, filename)
                df.to_csv(filepath, index=False, encoding='utf-8-sig')
                print(f"  ✅ Saved: {filepath} ({len(df)} records)")
            
            # サーバー負荷を軽減
            time.sleep(2)
        
        return results


# 主要メーカー・車種・グレードコードの例
CAR_CODES = {
    'BMW': {
        'code': 'BM',
        'models': {
            'M3セダン': {
                'code': '033',
                'grades': {
                    '2021年1月～生産中': '003',
                    '2014年02月～2018年12月': '002',
                    '2008年03月～2014年01月': '001',
                }
            },
            '3シリーズ': {
                'code': '011',
                'grades': {}  # グレードコードは実際のページで確認が必要
            }
        }
    },
    'メルセデスベンツ': {
        'code': 'MB',
        'models': {
            'Cクラス': {
                'code': '001',
                'grades': {}
            }
        }
    },
    'アウディ': {
        'code': 'AU',
        'models': {
            'A4': {
                'code': '001',
                'grades': {}
            }
        }
    }
}


def main():
    """使用例"""
    scraper = CarsensorURLPatternScraper()
    
    # 例1: 特定の車種・グレードをスクレイピング
    print("=== Example 1: Scrape specific grade ===")
    df = scraper.scrape_by_url_pattern(
        maker_code='BM',
        model_code='033',
        grade_code='002',
        max_cars=31
    )
    
    if not df.empty:
        output_file = f"bmw_m3_grade002_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"✅ Saved: {output_file} ({len(df)} records)")
    
    # 例2: 複数のグレードを一括スクレイピング
    print("\n=== Example 2: Scrape multiple grades ===")
    grade_codes = ['001', '002', '003']  # M3セダンの全グレード
    results = scraper.scrape_multiple_grades(
        maker_code='BM',
        model_code='033',
        grade_codes=grade_codes,
        output_dir='output/carsensor',
        max_cars_per_grade=50
    )
    
    print(f"\n✅ Completed: {len(results)} grades scraped")
    
    # 例3: コード辞書を使用
    print("\n=== Example 3: Using code dictionary ===")
    bmw_info = CAR_CODES['BMW']
    m3_info = bmw_info['models']['M3セダン']
    
    print(f"BMW M3セダン:")
    print(f"  メーカーコード: {bmw_info['code']}")
    print(f"  車種コード: {m3_info['code']}")
    print(f"  利用可能なグレード:")
    for grade_name, grade_code in m3_info['grades'].items():
        print(f"    {grade_name}: {grade_code}")


if __name__ == "__main__":
    main()

