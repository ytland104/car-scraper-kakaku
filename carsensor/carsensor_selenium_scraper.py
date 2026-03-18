#!/usr/bin/env python3
"""
カーセンサーエッジ Seleniumスクレイパー

ポップアップを操作して車種・グレードを選択する方法
JavaScriptで動的に生成されるページに対応
"""

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("Selenium is not installed. Install it with: pip install selenium")

import pandas as pd
from datetime import datetime
import time
from typing import List, Dict, Optional
from carsensor_scraper import CarsensorScraper
from bs4 import BeautifulSoup

class CarsensorSeleniumScraper:
    """Seleniumを使用してポップアップを操作するスクレイパー"""
    
    def __init__(self, headless: bool = True, wait_time: int = 10):
        """
        Args:
            headless: ヘッドレスモードで実行するか
            wait_time: 要素が表示されるまでの待機時間（秒）
        """
        if not SELENIUM_AVAILABLE:
            raise ImportError("Selenium is required. Install with: pip install selenium")
        
        self.base_scraper = CarsensorScraper()
        self.wait_time = wait_time
        self.driver = None
        self.setup_driver(headless)
    
    def setup_driver(self, headless: bool = True):
        """Seleniumドライバーをセットアップ"""
        chrome_options = Options()
        if headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
        except Exception as e:
            print(f"Error setting up Chrome driver: {e}")
            print("Make sure ChromeDriver is installed and in PATH")
            raise
    
    def close(self):
        """ドライバーを閉じる"""
        if self.driver:
            self.driver.quit()
    
    def wait_for_element(self, by, value, timeout: int = None):
        """要素が表示されるまで待機"""
        timeout = timeout or self.wait_time
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
        except TimeoutException:
            return None
    
    def select_maker(self, maker_name: str):
        """メーカーを選択"""
        # メーカー選択のポップアップを開く
        # 実際のセレクタはサイトの構造に応じて調整が必要
        try:
            # 例: メーカー選択ボタンをクリック
            maker_button = self.wait_for_element(By.CSS_SELECTOR, '[data-maker-select]')
            if maker_button:
                maker_button.click()
                time.sleep(1)
            
            # メーカー名で選択
            maker_option = self.wait_for_element(
                By.XPATH, f"//a[contains(text(), '{maker_name}')]"
            )
            if maker_option:
                maker_option.click()
                time.sleep(1)
                return True
        except Exception as e:
            print(f"Error selecting maker: {e}")
            return False
    
    def select_car_model(self, model_name: str):
        """車種を選択"""
        try:
            # 車種選択のポップアップを開く
            model_button = self.wait_for_element(By.CSS_SELECTOR, '[data-model-select]')
            if model_button:
                model_button.click()
                time.sleep(1)
            
            # 車種名で選択
            model_option = self.wait_for_element(
                By.XPATH, f"//a[contains(text(), '{model_name}')]"
            )
            if model_option:
                model_option.click()
                time.sleep(1)
                return True
        except Exception as e:
            print(f"Error selecting car model: {e}")
            return False
    
    def select_grade(self, grade_name: str):
        """グレード/年式を選択"""
        try:
            # グレード選択のポップアップを開く
            grade_button = self.wait_for_element(By.CSS_SELECTOR, '[data-grade-select]')
            if grade_button:
                grade_button.click()
                time.sleep(1)
            
            # グレード名で選択
            grade_option = self.wait_for_element(
                By.XPATH, f"//a[contains(text(), '{grade_name}')]"
            )
            if grade_option:
                grade_option.click()
                time.sleep(2)  # ページが読み込まれるまで待機
                return True
        except Exception as e:
            print(f"Error selecting grade: {e}")
            return False
    
    def scrape_with_popup_selection(self, maker_name: str, model_name: str, 
                                   grade_name: str = None, max_cars: int = None) -> pd.DataFrame:
        """
        ポップアップで選択してスクレイピング
        
        Args:
            maker_name: メーカー名（例: 'BMW'）
            model_name: 車種名（例: 'M3セダン'）
            grade_name: グレード/年式名（例: '2014年02月～2018年12月'）
            max_cars: 最大取得台数
        
        Returns:
            スクレイピング結果のDataFrame
        """
        try:
            # 検索ページを開く
            url = "https://www.carsensor.net/usedcar/index.html?ROUTEID=edge"
            self.driver.get(url)
            time.sleep(2)
            
            # メーカーを選択
            if not self.select_maker(maker_name):
                print(f"Failed to select maker: {maker_name}")
                return pd.DataFrame()
            
            # 車種を選択
            if not self.select_car_model(model_name):
                print(f"Failed to select car model: {model_name}")
                return pd.DataFrame()
            
            # グレードを選択（指定されている場合）
            if grade_name:
                if not self.select_grade(grade_name):
                    print(f"Failed to select grade: {grade_name}")
                    return pd.DataFrame()
            
            # ページのHTMLを取得してスクレイピング
            html = self.driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            cars = self.base_scraper.extract_car_data(soup)
            
            if not cars:
                return pd.DataFrame()
            
            df = pd.DataFrame(cars)
            return df[:max_cars] if max_cars and len(df) > max_cars else df
            
        except Exception as e:
            print(f"Error during scraping: {e}")
            return pd.DataFrame()


def main():
    """使用例（Seleniumが必要）"""
    if not SELENIUM_AVAILABLE:
        print("Selenium is not available. Install it first.")
        return
    
    scraper = CarsensorSeleniumScraper(headless=False)  # デバッグ時はFalse
    
    try:
        # ポップアップで選択してスクレイピング
        df = scraper.scrape_with_popup_selection(
            maker_name='BMW',
            model_name='M3セダン',
            grade_name='2014年02月～2018年12月',
            max_cars=31
        )
        
        if not df.empty:
            output_file = f"carsensor_selenium_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            df.to_csv(output_file, index=False, encoding='utf-8-sig')
            print(f"✅ Saved: {output_file} ({len(df)} records)")
    finally:
        scraper.close()


if __name__ == "__main__":
    main()

