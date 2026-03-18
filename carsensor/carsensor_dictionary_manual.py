#!/usr/bin/env python3
"""
カーセンサーエッジ 車種辞書 手動作成ツール

既知のURLパターンや手動で確認した情報から、
車種・モデル・グレードの階層辞書を作成・管理するツール
"""

import json
import pandas as pd
from datetime import datetime
from typing import Dict, List
from carsensor_url_pattern_scraper import CarsensorURLPatternScraper
from carsensor_grade_extractor import CarsensorGradeExtractor

# トヨタ アルファード・ヴェルファイアの辞書例
# 実際のコードはカーセンサーのサイトで確認が必要
TOYOTA_ALPHARD_VELLFIRE_DICT = {
    'maker_code': 'TO',
    'maker_name': 'トヨタ',
    'models': {
        'alphard': {
            'name': 'アルファード',
            'code': '',  # 実際のコードを入力
            'model_years': {
                '40系': {
                    'name': '40系',
                    'grades': {
                        'executive_lounge': {
                            'name': 'エグゼクティブラウンジ',
                            'code': ''  # 実際のコードを入力
                        },
                        'executive_seat': {
                            'name': 'エグゼクティブシート',
                            'code': ''
                        },
                        'royal_lounge': {
                            'name': 'ロイヤルラウンジ',
                            'code': ''
                        }
                    }
                },
                '30系': {
                    'name': '30系',
                    'grades': {
                        'executive_lounge': {
                            'name': 'エグゼクティブラウンジ',
                            'code': ''
                        },
                        'executive_seat': {
                            'name': 'エグゼクティブシート',
                            'code': ''
                        }
                    }
                },
                '20系': {
                    'name': '20系',
                    'grades': {
                        'executive_lounge': {
                            'name': 'エグゼクティブラウンジ',
                            'code': ''
                        }
                    }
                }
            }
        },
        'vellfire': {
            'name': 'ヴェルファイア',
            'code': '',  # 実際のコードを入力
            'model_years': {
                '40系': {
                    'name': '40系',
                    'grades': {
                        'executive_lounge': {
                            'name': 'エグゼクティブラウンジ',
                            'code': ''
                        },
                        'executive_seat': {
                            'name': 'エグゼクティブシート',
                            'code': ''
                        }
                    }
                },
                '30系': {
                    'name': '30系',
                    'grades': {
                        'executive_lounge': {
                            'name': 'エグゼクティブラウンジ',
                            'code': ''
                        }
                    }
                }
            }
        }
    }
}


class CarsensorDictionaryManager:
    """車種辞書を管理するクラス"""
    
    def __init__(self, dictionary: Dict = None):
        self.dictionary = dictionary or {}
        self.scraper = CarsensorURLPatternScraper()
        self.grade_extractor = CarsensorGradeExtractor()
    
    def save_dictionary(self, filename: str):
        """辞書をJSONファイルに保存"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.dictionary, f, ensure_ascii=False, indent=2)
        print(f"✅ Dictionary saved to: {filename}")
    
    def load_dictionary(self, filename: str):
        """辞書をJSONファイルから読み込み"""
        with open(filename, 'r', encoding='utf-8') as f:
            self.dictionary = json.load(f)
        print(f"✅ Dictionary loaded from: {filename}")
        return self.dictionary
    
    def add_model(self, maker_code: str, model_name: str, model_code: str):
        """車種を追加"""
        if 'maker_code' not in self.dictionary:
            self.dictionary['maker_code'] = maker_code
        
        if 'models' not in self.dictionary:
            self.dictionary['models'] = {}
        
        self.dictionary['models'][model_code] = {
            'name': model_name,
            'code': model_code,
            'model_years': {}
        }
    
    def add_model_year(self, model_code: str, my_name: str, my_code: str):
        """モデル年式を追加"""
        if 'models' not in self.dictionary:
            self.dictionary['models'] = {}
        
        if model_code not in self.dictionary['models']:
            self.dictionary['models'][model_code] = {
                'model_years': {}
            }
        
        self.dictionary['models'][model_code]['model_years'][my_code] = {
            'name': my_name,
            'code': my_code,
            'grades': {}
        }
    
    def add_grade(self, model_code: str, my_code: str, grade_name: str, grade_code: str):
        """グレードを追加"""
        if 'models' not in self.dictionary:
            return
        
        if model_code not in self.dictionary['models']:
            return
        
        if 'model_years' not in self.dictionary['models'][model_code]:
            self.dictionary['models'][model_code]['model_years'] = {}
        
        if my_code not in self.dictionary['models'][model_code]['model_years']:
            self.dictionary['models'][model_code]['model_years'][my_code] = {
                'grades': {}
            }
        
        if 'grades' not in self.dictionary['models'][model_code]['model_years'][my_code]:
            self.dictionary['models'][model_code]['model_years'][my_code]['grades'] = {}
        
        self.dictionary['models'][model_code]['model_years'][my_code]['grades'][grade_code] = {
            'name': grade_name,
            'code': grade_code
        }
    
    def auto_fill_grades(self, maker_code: str, model_code: str, my_code: str):
        """
        指定されたモデル年式のグレード一覧を自動取得して辞書に追加
        
        Args:
            maker_code: メーカーコード
            model_code: 車種コード
            my_code: モデル年式コード
        """
        print(f"\nAuto-filling grades for {maker_code}-{model_code}-{my_code}...")
        
        # グレード一覧を取得
        grades = self.grade_extractor.get_grades_for_model(maker_code, model_code, my_code)
        
        if not grades:
            print(f"  No grades found")
            return
        
        print(f"  Found {len(grades)} grades")
        
        # 辞書に追加
        for i, grade in enumerate(grades, 1):
            grade_name = grade['name']
            # コードがない場合は連番を使用
            grade_code = grade.get('code') or f'grade_{i:03d}'
            
            self.add_grade(model_code, my_code, grade_name, grade_code)
            print(f"    Added: {grade_name} (code: {grade_code})")
        
        return len(grades)
    
    def export_to_flat_csv(self, filename: str = None):
        """辞書をフラットなCSV形式でエクスポート"""
        rows = []
        
        maker_code = self.dictionary.get('maker_code', '')
        maker_name = self.dictionary.get('maker_name', '')
        
        for model_code, model_data in self.dictionary.get('models', {}).items():
            model_name = model_data.get('name', '')
            
            model_years = model_data.get('model_years', {})
            
            if not model_years:
                rows.append({
                    'メーカーコード': maker_code,
                    'メーカー名': maker_name,
                    '車種コード': model_code,
                    '車種名': model_name,
                    'モデル年式コード': '',
                    'モデル年式名': '',
                    'グレードコード': '',
                    'グレード名': ''
                })
            else:
                for my_code, my_data in model_years.items():
                    my_name = my_data.get('name', '')
                    grades = my_data.get('grades', {})
                    
                    if not grades:
                        rows.append({
                            'メーカーコード': maker_code,
                            'メーカー名': maker_name,
                            '車種コード': model_code,
                            '車種名': model_name,
                            'モデル年式コード': my_code,
                            'モデル年式名': my_name,
                            'グレードコード': '',
                            'グレード名': ''
                        })
                    else:
                        for grade_code, grade_data in grades.items():
                            grade_name = grade_data.get('name', '')
                            rows.append({
                                'メーカーコード': maker_code,
                                'メーカー名': maker_name,
                                '車種コード': model_code,
                                '車種名': model_name,
                                'モデル年式コード': my_code,
                                'モデル年式名': my_name,
                                'グレードコード': grade_code,
                                'グレード名': grade_name
                            })
        
        df = pd.DataFrame(rows)
        
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            maker_code = self.dictionary.get('maker_code', 'unknown')
            filename = f"carsensor_dictionary_{maker_code}_{timestamp}.csv"
        
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"✅ CSV exported to: {filename}")
        return filename
    
    def get_all_scraping_urls(self) -> List[Dict]:
        """辞書から全てのスクレイピングURLを生成"""
        urls = []
        
        maker_code = self.dictionary.get('maker_code', '')
        
        for model_code, model_data in self.dictionary.get('models', {}).items():
            model_name = model_data.get('name', '')
            
            for my_code, my_data in model_data.get('model_years', {}).items():
                my_name = my_data.get('name', '')
                grades = my_data.get('grades', {})
                
                if grades:
                    # グレードごとにURLを生成
                    for grade_code, grade_data in grades.items():
                        grade_name = grade_data.get('name', '')
                        url = self.scraper.build_url(maker_code, model_code, grade_code)
                        urls.append({
                            'maker_code': maker_code,
                            'model_code': model_code,
                            'model_name': model_name,
                            'model_year_code': my_code,
                            'model_year_name': my_name,
                            'grade_code': grade_code,
                            'grade_name': grade_name,
                            'url': url
                        })
                else:
                    # グレードがない場合はモデル年式コードを使用
                    url = self.scraper.build_url(maker_code, model_code, my_code)
                    urls.append({
                        'maker_code': maker_code,
                        'model_code': model_code,
                        'model_name': model_name,
                        'model_year_code': my_code,
                        'model_year_name': my_name,
                        'grade_code': '',
                        'grade_name': '',
                        'url': url
                    })
        
        return urls
    
    def scrape_all_from_dictionary(self, output_dir: str = "output", 
                                  max_cars_per_url: int = None) -> pd.DataFrame:
        """辞書に基づいて全てのURLをスクレイピング"""
        urls = self.get_all_scraping_urls()
        all_data = []
        
        print(f"\n=== Scraping {len(urls)} URLs from dictionary ===")
        
        for i, url_info in enumerate(urls, 1):
            print(f"\n[{i}/{len(urls)}] {url_info['model_name']} - {url_info['model_year_name']} - {url_info['grade_name']}")
            
            df = self.scraper.scrape_by_url_pattern(
                maker_code=url_info['maker_code'],
                model_code=url_info['model_code'],
                grade_code=url_info['grade_code'] or None,
                max_cars=max_cars_per_url
            )
            
            if not df.empty:
                # メタデータを追加
                df['メーカーコード'] = url_info['maker_code']
                df['車種コード'] = url_info['model_code']
                df['車種名'] = url_info['model_name']
                df['モデル年式コード'] = url_info['model_year_code']
                df['モデル年式名'] = url_info['model_year_name']
                df['グレードコード'] = url_info['grade_code']
                df['グレード名'] = url_info['grade_name']
                
                all_data.append(df)
                
                # 個別ファイルに保存
                import os
                os.makedirs(output_dir, exist_ok=True)
                filename = f"{url_info['maker_code']}_{url_info['model_code']}_{url_info['grade_code'] or url_info['model_year_code']}_{datetime.now().strftime('%Y%m%d')}.csv"
                filepath = os.path.join(output_dir, filename)
                df.to_csv(filepath, index=False, encoding='utf-8-sig')
                print(f"  ✅ Saved: {filepath} ({len(df)} records)")
            
            # サーバー負荷を軽減
            import time
            time.sleep(2)
        
        # 全データを結合
        if all_data:
            combined_df = pd.concat(all_data, ignore_index=True)
            combined_file = os.path.join(output_dir, f"all_cars_combined_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
            combined_df.to_csv(combined_file, index=False, encoding='utf-8-sig')
            print(f"\n✅ Combined data saved to: {combined_file} ({len(combined_df)} total records)")
            return combined_df
        
        return pd.DataFrame()


def create_dictionary_template():
    """辞書テンプレートを作成"""
    template = {
        'maker_code': 'TO',  # メーカーコード（例: TO=トヨタ, BM=BMW）
        'maker_name': 'トヨタ',
        'models': {
            'model_code_1': {  # 車種コード（例: '001'）
                'name': '車種名',
                'code': 'model_code_1',
                'model_years': {
                    'my_code_1': {  # モデル年式コード（例: '001'）
                        'name': 'モデル年式名（例: 40系）',
                        'code': 'my_code_1',
                        'grades': {
                            'grade_code_1': {  # グレードコード（例: '001'）
                                'name': 'グレード名',
                                'code': 'grade_code_1'
                            }
                        }
                    }
                }
            }
        }
    }
    
    return template


def main():
    """使用例"""
    # 例1: テンプレートから辞書を作成
    print("=== Example 1: Creating dictionary from template ===")
    manager = CarsensorDictionaryManager(create_dictionary_template())
    
    # 例2: 既存の辞書を読み込み
    # manager = CarsensorDictionaryManager()
    # manager.load_dictionary('toyota_alphard_vellfire.json')
    
    # 例3: 手動で辞書を構築 + グレード自動取得
    print("\n=== Example 2: Building dictionary with auto-grade extraction ===")
    manager2 = CarsensorDictionaryManager()
    manager2.dictionary = {
        'maker_code': 'BM',
        'maker_name': 'BMW',
        'models': {}
    }
    
    # BMW M3セダンを追加
    manager2.add_model('BM', 'M3セダン', '033')
    
    # モデル年式を追加
    manager2.add_model_year('033', '2014年02月～2018年12月', '002')
    
    # グレードを自動取得して追加
    manager2.auto_fill_grades('BM', '033', '002')
    
    # 辞書を保存
    manager2.save_dictionary('bmw_m3_auto.json')
    
    # CSVにエクスポート
    manager2.export_to_flat_csv('bmw_m3_auto.csv')
    
    # スクレイピングURL一覧を取得
    urls = manager2.get_all_scraping_urls()
    print(f"\n=== Generated {len(urls)} scraping URLs ===")
    for url_info in urls:
        print(f"  {url_info['url']}")
    
    # 例4: トヨタの例（コードが分かっている場合）
    print("\n=== Example 3: Toyota Alphard/Vellfire (manual codes required) ===")
    manager3 = CarsensorDictionaryManager()
    manager3.dictionary = {
        'maker_code': 'TO',
        'maker_name': 'トヨタ',
        'models': {}
    }
    
    # アルファードを追加（実際のコードを入力）
    # manager3.add_model('TO', 'アルファード', '123')  # 実際のコードに置き換え
    # manager3.add_model_year('123', '40系', '001')  # 実際のコードに置き換え
    # 
    # # グレードを自動取得
    # manager3.auto_fill_grades('TO', '123', '001')


if __name__ == "__main__":
    main()

