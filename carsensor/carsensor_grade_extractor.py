#!/usr/bin/env python3
"""
カーセンサー グレード一覧自動取得ツール

車名・モデル年式のURLから、グレード一覧を自動で取得するツール
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import json
from typing import List, Dict, Optional, Set
from urllib.parse import urljoin

class CarsensorGradeExtractor:
    """グレード一覧を抽出するクラス"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ja,en-US;q=0.7,en;q=0.3',
        })
        self.base_url = "https://www.carsensor.net"
    
    def get_page(self, url: str) -> Optional[BeautifulSoup]:
        """ページを取得"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            print(f"Error fetching page: {e}")
            return None
    
    def extract_grades_from_ui(self, soup: BeautifulSoup) -> List[Dict]:
        """ページ内のグレード選択UIからグレード一覧を抽出"""
        grades = []
        
        # 方法1: 「グレード絞り込み」セクションを探す
        grade_section = soup.find('h2', string=re.compile(r'グレード'))
        if grade_section:
            # グレードセクションの親要素を探す
            parent = grade_section.find_parent(['div', 'section'])
            if parent:
                # チェックボックスやリンクを探す
                checkboxes = parent.find_all(['input', 'a'], type='checkbox')
                links = parent.find_all('a', href=True)
                
                for cb in checkboxes:
                    label = cb.find_next('label')
                    if label:
                        grade_name = label.get_text(strip=True)
                        value = cb.get('value', '')
                        grades.append({
                            'name': grade_name,
                            'code': value,
                            'method': 'checkbox'
                        })
        
        # 方法2: グレード選択のリストを探す
        grade_lists = soup.find_all(['ul', 'ol'], class_=re.compile(r'grade|filter|option'))
        for ul in grade_lists:
            items = ul.find_all('li')
            for item in items:
                text = item.get_text(strip=True)
                link = item.find('a', href=True)
                if link:
                    href = link.get('href', '')
                    # URLからグレードコードを抽出
                    grade_code = self._extract_grade_code_from_url(href)
                    if text and text not in ['グレード', '選択', '全て']:
                        grades.append({
                            'name': text,
                            'code': grade_code,
                            'method': 'list_item',
                            'url': href
                        })
        
        return grades
    
    def extract_grades_from_car_listings(self, soup: BeautifulSoup) -> List[Dict]:
        """実際に表示されている車両データからグレード名を抽出"""
        grades = []
        grade_names: Set[str] = set()
        
        # 車両リストを取得
        car_items = soup.find_all('div', class_='cassetteMain')
        
        print(f"    Analyzing {len(car_items)} car listings...")
        
        for car_item in car_items:
            # 車名からグレード情報を抽出
            title_elem = car_item.find('h3', class_='cassetteMain__title')
            if title_elem:
                car_name = title_elem.get_text(strip=True)
                # 車名からグレード部分を抽出
                grade_name = self._extract_grade_from_car_name(car_name)
                if grade_name and grade_name not in grade_names:
                    grade_names.add(grade_name)
                    grades.append({
                        'name': grade_name,
                        'code': '',  # コードは不明
                        'method': 'extracted_from_listing',
                        'example_car_name': car_name[:100]
                    })
            
            # サブテキストからもグレード情報を抽出
            sub_text_elem = car_item.find('p', class_='cassetteMain__subText')
            if sub_text_elem:
                sub_text = sub_text_elem.get_text(strip=True)
                # サブテキストからもグレード情報を抽出可能
                # 特定のキーワードを含む場合
                grade_keywords = ['コンペティション', 'エグゼクティブ', 'ロイヤル', 'ラウンジ']
                for keyword in grade_keywords:
                    if keyword in sub_text and keyword not in grade_names:
                        grade_names.add(keyword)
                        grades.append({
                            'name': keyword,
                            'code': '',
                            'method': 'extracted_from_subtext',
                            'example_car_name': car_name[:100] if title_elem else ''
                        })
        
        return grades
    
    def _extract_grade_from_car_name(self, car_name: str) -> Optional[str]:
        """車名からグレード名を抽出"""
        # 車種名を除去（例: "M3セダン"を除去）
        # 残った部分がグレード名の可能性が高い
        
        # 車種名のパターンを除去
        patterns_to_remove = [
            r'^[A-Z0-9]+シリーズ\s*',
            r'^[A-Z0-9]+\s*',
            r'セダン\s*',
            r'クーペ\s*',
            r'SUV\s*',
            r'ワゴン\s*',
        ]
        
        grade_name = car_name
        for pattern in patterns_to_remove:
            grade_name = re.sub(pattern, '', grade_name, flags=re.IGNORECASE)
        
        # スペースや特殊文字で区切る
        parts = re.split(r'[\s　]+', grade_name.strip())
        
        if not parts or not parts[0]:
            return None
        
        # 一般的なグレード名のパターン
        # 1. 最初の部分がグレード名（例: "コンペティション M DCT"）
        # 2. 特定のキーワードを含む部分
        
        # グレード名として認識されるキーワード
        grade_keywords = [
            'コンペティション', 'Competition', 'Competition',
            'エグゼクティブ', 'Executive', 'Executive',
            'ロイヤル', 'Royal', 'Royal',
            'ラウンジ', 'Lounge', 'Lounge',
            'シート', 'Seat', 'Seat',
            'M', 'AMG', 'S-Line', 'Type', 'タイプ',
            'G', 'GT', 'GTS', 'Turbo', 'ターボ',
            'ハイブリッド', 'Hybrid', 'HYBRID',
            'プラグインハイブリッド', 'PHEV',
        ]
        
        # キーワードを含む部分を探す
        for i, part in enumerate(parts):
            for keyword in grade_keywords:
                if keyword in part:
                    # キーワードを含む部分とその前後を取得
                    start = max(0, i - 1)
                    end = min(len(parts), i + 2)
                    grade_name = ' '.join(parts[start:end])
                    if len(grade_name) > 2 and len(grade_name) < 100:
                        return grade_name
        
        # キーワードが見つからない場合、最初の2-3語を取得
        if len(parts[0]) > 50:
            # 長すぎる場合は最初の部分のみ
            grade_name = parts[0][:50]
        else:
            # 最初の2-3語を取得
            grade_name = ' '.join(parts[:3])
        
        # 空でない、かつ適切な長さの場合
        if len(grade_name) > 2 and len(grade_name) < 100:
            # 不要な文字を除去
            grade_name = re.sub(r'[^\w\s\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]', '', grade_name)
            return grade_name.strip()
        
        return None
    
    def _extract_grade_code_from_url(self, url: str) -> str:
        """URLからグレードコードを抽出"""
        match = re.search(r'[Gg]rade[=:](\w+)', url)
        if match:
            return match.group(1)
        
        match = re.search(r'[Gg](\d+)', url)
        if match:
            return match.group(1)
        
        return ''
    
    def get_grades_from_url(self, url: str, method: str = 'auto') -> List[Dict]:
        """
        指定URLからグレード一覧を取得
        
        Args:
            url: 車種・モデル年式のURL
            method: 抽出方法 ('auto', 'ui', 'listings', 'both')
                - 'auto': 自動で最適な方法を選択
                - 'ui': UI要素から抽出
                - 'listings': 車両リストから抽出
                - 'both': 両方の方法を試す
        
        Returns:
            グレード一覧のリスト
        """
        print(f"Extracting grades from: {url}")
        soup = self.get_page(url)
        
        if not soup:
            return []
        
        all_grades = []
        
        if method in ['auto', 'ui', 'both']:
            # UI要素から抽出
            ui_grades = self.extract_grades_from_ui(soup)
            if ui_grades:
                print(f"  Found {len(ui_grades)} grades from UI elements")
                all_grades.extend(ui_grades)
        
        if method in ['auto', 'listings', 'both']:
            # 車両リストから抽出
            listing_grades = self.extract_grades_from_car_listings(soup)
            if listing_grades:
                print(f"  Found {len(listing_grades)} unique grades from car listings")
                all_grades.extend(listing_grades)
        
        # 重複を除去（名前で比較）
        unique_grades = []
        seen_names = set()
        
        for grade in all_grades:
            name = grade['name']
            if name and name not in seen_names:
                seen_names.add(name)
                unique_grades.append(grade)
        
        return unique_grades
    
    def get_grades_for_model(self, maker_code: str, model_code: str, 
                            grade_code: str = None) -> List[Dict]:
        """
        指定された車種・モデル年式のグレード一覧を取得
        
        Args:
            maker_code: メーカーコード
            model_code: 車種コード
            grade_code: モデル年式コード（オプション）
        
        Returns:
            グレード一覧のリスト
        """
        if grade_code:
            url = f"{self.base_url}/usedcar/b{maker_code}/s{model_code}/f{grade_code}/index.html?ROUTEID=edge"
        else:
            url = f"{self.base_url}/usedcar/b{maker_code}/s{model_code}/index.html?ROUTEID=edge"
        
        return self.get_grades_from_url(url, method='both')
    
    def save_grades(self, grades: List[Dict], filename: str = None):
        """グレード一覧をJSONファイルに保存"""
        if not filename:
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"grades_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(grades, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Grades saved to: {filename}")
        return filename
    
    def export_grades_to_csv(self, grades: List[Dict], filename: str = None):
        """グレード一覧をCSVファイルにエクスポート"""
        if not grades:
            print("No grades to export")
            return None
        
        df = pd.DataFrame(grades)
        
        if not filename:
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"grades_{timestamp}.csv"
        
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"✅ Grades exported to: {filename}")
        return filename


def main():
    """使用例"""
    extractor = CarsensorGradeExtractor()
    
    # 例1: URLから直接グレードを取得
    print("=== Example 1: Extract grades from URL ===")
    url = "https://www.carsensor.net/usedcar/bBM/s033/f002/index.html?ROUTEID=edge"
    grades = extractor.get_grades_from_url(url, method='both')
    
    if grades:
        print(f"\nFound {len(grades)} unique grades:")
        for i, grade in enumerate(grades, 1):
            print(f"  {i}. {grade['name']} (code: {grade.get('code', 'N/A')}, method: {grade.get('method', 'N/A')})")
        
        # 保存
        extractor.save_grades(grades, 'bmw_m3_grades.json')
        extractor.export_grades_to_csv(grades, 'bmw_m3_grades.csv')
    else:
        print("No grades found")
    
    # 例2: コードからグレードを取得
    print("\n=== Example 2: Extract grades from codes ===")
    grades2 = extractor.get_grades_for_model('BM', '033', '002')
    
    if grades2:
        print(f"\nFound {len(grades2)} grades:")
        for grade in grades2[:10]:
            print(f"  - {grade['name']}")


if __name__ == "__main__":
    main()

