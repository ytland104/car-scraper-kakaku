#!/usr/bin/env python3
"""
Car Data Scraper Module

This module handles the loading of car maker data from allmaker_url1016.csv
and performs web scraping to gather detailed vehicle information from kakaku.com.
"""

import re
import pandas as pd
import requests
from time import sleep
from datetime import datetime
from bs4 import BeautifulSoup
from retry import retry
import random
import mojimoji
from tqdm import tqdm
import numpy as np
import os
import time
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import KFold, cross_val_score
import logging
from typing import Optional, Dict, List, Union
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configure logging with more detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
    handlers=[
        logging.FileHandler('car_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Constants
BASE_URL = "https://kakaku.com"
DEFAULT_OUTPUT_DIR = "/Users/yutaka/Documents/csv/expectedPrice"
REQUEST_TIMEOUT = 30  # seconds
MAX_RETRIES = 3
BACKOFF_FACTOR = 2


class ScrapingError(Exception):
    """Custom exception for scraping errors"""
    pass


class DataValidationError(Exception):
    """Custom exception for data validation errors"""
    pass


class CarDataScraper:
    """Main class for scraping car data from kakaku.com"""
    
    def __init__(self, csv_path: str = "allmaker_url1016.csv", output_dir: str = None):
        """
        Initialize CarDataScraper
        
        Args:
            csv_path: Path to the CSV file containing car maker data
            output_dir: Directory to save output files
        """
        self.csv_path = csv_path
        self.output_dir = output_dir or DEFAULT_OUTPUT_DIR
        self.filtered_df = None
        self.session = self._create_session()
        
        # Error tracking
        self.error_count = 0
        self.success_count = 0
        
    def _create_session(self) -> requests.Session:
        """
        Create a requests session with retry strategy
        
        Returns:
            Configured requests session
        """
        session = requests.Session()
        
        # Define retry strategy with compatibility for different urllib3 versions
        try:
            # Try new parameter name first (urllib3 >= 1.26.0)
            retry_strategy = Retry(
                total=MAX_RETRIES,
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=["HEAD", "GET", "OPTIONS"],
                backoff_factor=BACKOFF_FACTOR
            )
        except TypeError:
            # Fall back to old parameter name (urllib3 < 1.26.0)
            retry_strategy = Retry(
                total=MAX_RETRIES,
                status_forcelist=[429, 500, 502, 503, 504],
                method_whitelist=["HEAD", "GET", "OPTIONS"],
                backoff_factor=BACKOFF_FACTOR
            )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Set common headers
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        return session
        
    def load_and_filter_data(self, min_year: int = 2005, apply_filter: bool = True) -> pd.DataFrame:
        """
        Load and filter car data from CSV file
        
        Args:
            min_year: Minimum year for filtering (default: 2005)
            apply_filter: Whether to apply year-based filtering (default: True)
        
        Returns:
            Filtered DataFrame with car maker data
            
        Raises:
            FileNotFoundError: If CSV file doesn't exist
            DataValidationError: If data validation fails
        """
        try:
            logger.info(f"Loading data from {self.csv_path}")
            
            if not os.path.exists(self.csv_path):
                raise FileNotFoundError(f"CSV file not found: {self.csv_path}")
            
            # Load CSV data with error handling
            try:
                all_makers_df = pd.read_csv(self.csv_path)
            except pd.errors.EmptyDataError:
                raise DataValidationError(f"CSV file is empty: {self.csv_path}")
            except pd.errors.ParserError as e:
                raise DataValidationError(f"Error parsing CSV file: {e}")
            
            # Validate required columns
            required_columns = ['年', 'CarMaker']
            missing_columns = [col for col in required_columns if col not in all_makers_df.columns]
            if missing_columns:
                raise DataValidationError(f"Missing required columns: {missing_columns}")
            
            logger.info(f"Loaded {len(all_makers_df)} total records from CSV")
            
            # Extract model year from '年' column
            all_makers_df['model_year'] = all_makers_df['年'].str.extract(r'(\d{4})').astype(float)
            
            if apply_filter:
                # Apply custom filter for specific car makers
                def custom_filter(row):
                    try:
                        if row['CarMaker'] in ['日産', 'ホンダ', 'スバル', 'フェラーリ']:
                            return True
                        else:
                            return row['model_year'] >= min_year
                    except (KeyError, TypeError):
                        logger.warning(f"Error applying filter to row: {row}")
                        return False
                        
                # Apply filtering
                self.filtered_df = all_makers_df[all_makers_df.apply(custom_filter, axis=1)]
                logger.info(f"After filtering (min_year={min_year}): {len(self.filtered_df)} records")
            else:
                # No filtering applied
                self.filtered_df = all_makers_df
                logger.info(f"No filtering applied: {len(self.filtered_df)} records")
            
            if self.filtered_df.empty:
                raise DataValidationError("No data remaining after filtering")
            
            # Create maker index for reference
            filtered_df_makeindex = self.filtered_df['CarMaker'].drop_duplicates().reset_index(drop=True).reset_index()
            filtered_df_makeindex.columns = ['Index', 'CarMaker']
            
            logger.info(f"Successfully loaded {len(self.filtered_df)} records for {len(filtered_df_makeindex)} car makers")
            return self.filtered_df
            
        except Exception as e:
            logger.error(f"Error loading and filtering data: {e}")
            raise
    
    def load_data_without_filter(self) -> pd.DataFrame:
        """
        Load car data from CSV file without applying any filters
        
        Returns:
            DataFrame with all car data
            
        Raises:
            FileNotFoundError: If CSV file doesn't exist
            DataValidationError: If data validation fails
        """
        return self.load_and_filter_data(min_year=2005, apply_filter=False)
    
    def compare_csv_files(self, csv_path1: str, csv_path2: str) -> dict:
        """
        Compare two CSV files and show differences
        
        Args:
            csv_path1: Path to first CSV file
            csv_path2: Path to second CSV file
            
        Returns:
            Dictionary with comparison results
        """
        try:
            # Load both files
            df1 = pd.read_csv(csv_path1)
            df2 = pd.read_csv(csv_path2)
            
            # Basic statistics
            comparison = {
                'file1': {
                    'path': csv_path1,
                    'total_records': len(df1),
                    'unique_makers': df1['CarMaker'].nunique() if 'CarMaker' in df1.columns else 0,
                    'maker_counts': df1['CarMaker'].value_counts().to_dict() if 'CarMaker' in df1.columns else {}
                },
                'file2': {
                    'path': csv_path2,
                    'total_records': len(df2),
                    'unique_makers': df2['CarMaker'].nunique() if 'CarMaker' in df2.columns else 0,
                    'maker_counts': df2['CarMaker'].value_counts().to_dict() if 'CarMaker' in df2.columns else {}
                }
            }
            
            # Calculate differences
            comparison['differences'] = {
                'record_difference': len(df2) - len(df1),
                'maker_difference': comparison['file2']['unique_makers'] - comparison['file1']['unique_makers']
            }
            
            logger.info(f"CSV Comparison Results:")
            logger.info(f"  {csv_path1}: {len(df1)} records, {comparison['file1']['unique_makers']} makers")
            logger.info(f"  {csv_path2}: {len(df2)} records, {comparison['file2']['unique_makers']} makers")
            logger.info(f"  Difference: {comparison['differences']['record_difference']} records")
            
            return comparison
            
        except Exception as e:
            logger.error(f"Error comparing CSV files: {e}")
            return {'error': str(e)}
    
    def get_html(self, url: str, max_retries: int = MAX_RETRIES) -> Optional[BeautifulSoup]:
        """
        Get HTML content from URL with enhanced error handling
        
        Args:
            url: URL to fetch
            max_retries: Maximum number of retry attempts
            
        Returns:
            BeautifulSoup object or None if failed
        """
        if not url or not isinstance(url, str):
            logger.error(f"Invalid URL provided: {url}")
            return None
            
        for attempt in range(max_retries):
            try:
                logger.debug(f"Fetching URL (attempt {attempt + 1}/{max_retries}): {url}")
                
                response = self.session.get(url, timeout=REQUEST_TIMEOUT)
                response.raise_for_status()  # Raises HTTPError for bad responses
                
                if response.status_code == 200:
                    self.success_count += 1
                    logger.debug(f"Successfully fetched: {url}")
                    return BeautifulSoup(response.content, "html.parser")
                else:
                    logger.warning(f"Unexpected status code {response.status_code} for URL: {url}")
                    
            except requests.exceptions.Timeout:
                logger.warning(f"Timeout occurred for URL: {url} (attempt {attempt + 1})")
                self.error_count += 1
                
            except requests.exceptions.ConnectionError:
                logger.warning(f"Connection error for URL: {url} (attempt {attempt + 1})")
                self.error_count += 1
                
            except requests.exceptions.HTTPError as e:
                logger.warning(f"HTTP error {e.response.status_code} for URL: {url}")
                self.error_count += 1
                # Don't retry for 4xx errors (client errors)
                if 400 <= e.response.status_code < 500:
                    break
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"Request exception for URL {url}: {e}")
                self.error_count += 1
                
            except Exception as e:
                logger.error(f"Unexpected error fetching URL {url}: {e}")
                self.error_count += 1
                
            # Wait before retrying (exponential backoff)
            if attempt < max_retries - 1:
                wait_time = BACKOFF_FACTOR ** attempt + random.uniform(0.5, 1.5)
                logger.debug(f"Waiting {wait_time:.2f} seconds before retry")
                sleep(wait_time)
        
        logger.error(f"Failed to fetch URL after {max_retries} attempts: {url}")
        return None
    
    def car_model_detection(self, url: str) -> List[str]:
        """
        Extract maker and model IDs from URL with validation
        
        Args:
            url: Car listing URL
            
        Returns:
            List containing maker and model IDs
        """
        try:
            if not url or not isinstance(url, str):
                logger.warning(f"Invalid URL for model detection: {url}")
                return ["0", "0"]
                
            maker_pattern = r"Maker=(\d{1,2})"
            model_pattern = r"Model=(\d{4,5})"
            
            maker_matches = re.findall(maker_pattern, url)
            model_matches = re.findall(model_pattern, url)
            
            maker_id = maker_matches[-1] if maker_matches else "0"
            model_id = model_matches[-1] if model_matches else "0"
            
            if maker_id == "0" or model_id == "0":
                logger.warning(f"Could not extract maker/model from URL: {url}")
                
            return [maker_id, model_id]
            
        except Exception as e:
            logger.error(f"Error in car model detection for URL {url}: {e}")
            return ["0", "0"]
    
    def engine_category(self, pstr: str) -> str:
        """
        Extract engine category from string with validation
        
        Args:
            pstr: String containing engine information
            
        Returns:
            Engine category string
        """
        try:
            if not pstr or not isinstance(pstr, str):
                return "0"
                
            pattern = r"(\d{3}|\d{1}\.\d{1})"
            matches = re.findall(pattern, pstr)
            return matches[-1] if matches else "0"
            
        except Exception as e:
            logger.error(f"Error extracting engine category from '{pstr}': {e}")
            return "0"
    
    def parse_car_detail_info(self, car_url: str, maker: List[str]) -> Dict[str, Union[str, int, float]]:
        """
        Parse detailed car information from individual car page with enhanced error handling
        
        Args:
            car_url: URL of individual car listing
            maker: List containing maker and model IDs
            
        Returns:
            Dictionary containing car details
        """
        data = {}
        
        try:
            soup = self.get_html(car_url)
            
            if soup is None:
                logger.warning(f"Failed to get HTML for car details: {car_url}")
                return data
                
            # Basic information with safe extraction
            try:
                name_element = soup.find("h3")
                if name_element:
                    data["名称"] = mojimoji.zen_to_han(name_element.getText().strip())
                    data["Class_Category"] = self.engine_category(data["名称"])
                else:
                    logger.warning(f"No name element found for: {car_url}")
                    
            except Exception as e:
                logger.error(f"Error extracting name from {car_url}: {e}")
                
            data["Url"] = car_url
            data["Maker"] = maker[0] if len(maker) > 0 else "0"
            data["Model"] = maker[1] if len(maker) > 1 else "0"
            
            # Price information with safe extraction
            try:
                total_price_element = soup.find("span", {"class": "-total"})
                base_price_element = soup.find("span", {"class": "-base"})
                
                if total_price_element:
                    data["総額"] = total_price_element.getText().strip()
                if base_price_element:
                    data["価格"] = base_price_element.getText().strip()
                    
            except Exception as e:
                logger.error(f"Error extracting price information from {car_url}: {e}")
            
            # Specifications table with safe extraction
            try:
                spec_table = soup.find("table", {"class": "specList"})
                if spec_table:
                    for tr in spec_table.find_all("tr"):
                        th = tr.find("th")
                        td = tr.find("td")
                        if th and td:
                            key = th.getText().strip()
                            value = td.getText().strip()
                            if key and value:  # Only add non-empty values
                                data[key] = value
                                
            except Exception as e:
                logger.error(f"Error extracting specifications from {car_url}: {e}")
            
            # Options with safe extraction
            try:
                option_area = soup.find("div", {"class": "optionArea"})
                if option_area:
                    # Yes options
                    for li in option_area.find_all("li", {"class": "yes"}):
                        option_text = li.getText().strip()
                        if option_text:
                            data[option_text] = 1
                            
                    # No options (deleted)
                    for li in option_area.find_all("del"):
                        option_text = li.getText().strip()
                        if option_text:
                            data[option_text] = 0
                            
            except Exception as e:
                logger.error(f"Error extracting options from {car_url}: {e}")
            
            # Additional details with safe extraction
            try:
                dt_elements = soup.find_all("dt")
                dd_elements = soup.find_all("dd")
                
                for dt, dd in zip(dt_elements, dd_elements):
                    if dt and dd:
                        key = dt.getText().strip()
                        value = dd.getText().strip()
                        if key and value:
                            data[key] = value
                            
            except Exception as e:
                logger.error(f"Error extracting additional details from {car_url}: {e}")
            
            # Shop name with safe extraction
            try:
                shop_name_tag = soup.find("p", {"class": "shopName"})
                if shop_name_tag:
                    shop_link = shop_name_tag.find("a")
                    if shop_link:
                        data["ショップ名"] = shop_link.get_text(strip=True)
                        
            except Exception as e:
                logger.error(f"Error extracting shop name from {car_url}: {e}")
                
        except Exception as e:
            logger.error(f"Unexpected error parsing car details from {car_url}: {e}")
            
        return data
    
    def check_next_page(self, soup: BeautifulSoup) -> bool:
        """
        Check if there's a next page in pagination with safe handling
        
        Args:
            soup: BeautifulSoup object to check
            
        Returns:
            True if next page exists, False otherwise
        """
        try:
            if soup is None:
                logger.warning("Soup is None in check_next_page")
                return False
                
            next_element = soup.find("li", {"class": "next"})
            return next_element is not None
            
        except Exception as e:
            logger.error(f"Error checking next page: {e}")
            return False
    
    def extract_color_from_item(self, item) -> Optional[str]:
        """
        Extract color information from item with enhanced error handling
        
        Args:
            item: BeautifulSoup element containing color information
            
        Returns:
            Color string or None if not found
        """
        try:
            if item is None:
                return None
                
            color_item = item.find("li", class_=re.compile(r"color color\d+"))
            if color_item and "class" in color_item.attrs:
                color_classes = [
                    cls for cls in color_item["class"] 
                    if isinstance(cls, str) and cls.startswith("color") and len(cls) > 5
                ]
                if color_classes:
                    return color_classes[0][5:]  # Remove 'color' prefix
                    
        except Exception as e:
            logger.error(f"Error extracting color from item: {e}")
            
        return None
    
    def get_total_count_from_page(self, url: str) -> int:
        """
        Get total count of items from search results page
        
        Args:
            url: URL to check for total count
            
        Returns:
            Total count of items or 0 if not found
        """
        try:
            soup = self.get_html(url)
            if soup is None:
                return 0
            
            # Find total count element - adapt to kakaku.com structure
            count_elements = soup.find_all(text=re.compile(r'(\d+)件'))
            for element in count_elements:
                matches = re.findall(r'(\d+)件', element)
                if matches:
                    return int(matches[0])
                    
            # Alternative pattern - check page title or other elements
            title = soup.find("title")
            if title:
                title_text = title.get_text()
                matches = re.findall(r'(\d+)件', title_text)
                if matches:
                    return int(matches[0])
            
            return 0
            
        except Exception as e:
            logger.error(f"Error getting total count from {url}: {e}")
            return 0
    
    def build_url_with_age_filter(self, base_url: str, age_type: str) -> str:
        """
        Build URL with AgeType filter
        
        Args:
            base_url: Base URL without AgeType parameter
            age_type: Age type parameter (e.g., "2020" for 2020年式)
            
        Returns:
            URL with AgeType parameter added
        """
        try:
            if not base_url or not age_type:
                return base_url
                
            # Add AgeType parameter to URL
            separator = "&" if "?" in base_url else "/"
            if base_url.endswith("/"):
                separator = ""
            
            return f"{base_url}AgeType={age_type}{separator}"
            
        except Exception as e:
            logger.error(f"Error building URL with age filter: {e}")
            return base_url
    
    def get_optimal_age_ranges(self, base_url: str, year_start: int = 2010, year_end: int = 2025, max_items_per_range: int = 1000) -> List[List[int]]:
        """
        Get optimal age ranges that keep item count under the specified limit
        
        Args:
            base_url: Base URL to test
            year_start: Starting year
            year_end: Ending year
            max_items_per_range: Maximum items per age range
            
        Returns:
            List of age ranges, each range is [start_year, end_year]
        """
        age_ranges = []
        current_start = year_start
        
        try:
            logger.info(f"Calculating optimal age ranges for {base_url}")
            
            while current_start <= year_end:
                # Try expanding the range until we hit the limit
                range_end = current_start
                best_end = current_start
                
                for test_end in range(current_start, year_end + 1):
                    # Test this range
                    test_url = self.build_url_with_age_filter(base_url, f"{current_start}-{test_end}")
                    total_count = self.get_total_count_from_page(test_url)
                    
                    logger.debug(f"Testing range {current_start}-{test_end}: {total_count} items")
                    
                    if total_count <= max_items_per_range:
                        best_end = test_end
                    else:
                        break
                    
                    # Add small delay to avoid overwhelming the server
                    sleep(0.5)
                
                # Add this range
                age_ranges.append([current_start, best_end])
                logger.info(f"Added age range: {current_start}-{best_end}")
                
                # Move to next range
                current_start = best_end + 1
                
                # Safety check
                if len(age_ranges) > 20:  # Prevent infinite loops
                    logger.warning("Too many age ranges generated, stopping")
                    break
            
            if not age_ranges:
                # Fallback: single range
                age_ranges = [[year_start, year_end]]
                logger.warning(f"No optimal ranges found, using full range: {year_start}-{year_end}")
            
            logger.info(f"Generated {len(age_ranges)} optimal age ranges")
            return age_ranges
            
        except Exception as e:
            logger.error(f"Error calculating optimal age ranges: {e}")
            # Fallback: split into smaller chunks
            chunk_size = 3  # 3 years per chunk
            for start in range(year_start, year_end + 1, chunk_size):
                end = min(start + chunk_size - 1, year_end)
                age_ranges.append([start, end])
            
            return age_ranges
    
    def process_car_details_with_age_filter(self, final_df: pd.DataFrame) -> pd.DataFrame:
        """
        Enhanced car details processing with age-based filtering for complete data retrieval
        
        Args:
            final_df: DataFrame containing car URLs to process
            
        Returns:
            DataFrame with processed car details from all available data
        """
        if final_df is None or final_df.empty:
            logger.warning("Empty DataFrame provided to process_car_details_with_age_filter")
            return pd.DataFrame()
            
        # Validate required columns
        required_columns = ['Web Address', '新車価格', 'グレード名', '年', 'CarMaker', 'モデル名']
        missing_columns = [col for col in required_columns if col not in final_df.columns]
        if missing_columns:
            logger.error(f"Missing required columns in final_df: {missing_columns}")
            return pd.DataFrame()
        
        all_data = []
        originals = final_df['Web Address'].tolist()
        processed_count = 0
        failed_count = 0
        
        logger.info(f"Starting enhanced processing of {len(originals)} URLs with age filtering")
        
        for url_idx, url in enumerate(tqdm(originals, desc="Processing URLs with age filter")):
            try:
                if not url or pd.isna(url):
                    logger.warning(f"Skipping invalid URL at index {url_idx}: {url}")
                    failed_count += 1
                    continue
                    
                # Get base information for this URL
                url_matches = final_df[final_df['Web Address'] == url]
                if url_matches.empty:
                    logger.warning(f"No matching data found for URL: {url}")
                    failed_count += 1
                    continue
                    
                idx = url_matches.index[0]
                base_info = {
                    '新車価格': final_df.at[idx, "新車価格"],
                    'グレード名': final_df.at[idx, "グレード名"],
                    '年': final_df.at[idx, "年"],
                    'CarMaker': final_df.at[idx, 'CarMaker'],
                    'モデル名': final_df.at[idx, 'モデル名']
                }
                
                # Get total count without filter first
                total_without_filter = self.get_total_count_from_page(url)
                logger.info(f"URL {url_idx+1}/{len(originals)}: Total items without filter: {total_without_filter}")
                
                # If total count is manageable (≤1200), use original method
                if total_without_filter <= 1200:
                    logger.info(f"Using original method for URL with {total_without_filter} items")
                    url_data = self._process_single_url_original(url, base_info)
                    all_data.extend(url_data)
                else:
                    # Use age-based filtering for large datasets
                    logger.info(f"Using age-based filtering for URL with {total_without_filter} items")
                    age_ranges = self.get_optimal_age_ranges(url, max_items_per_range=1000)
                    
                    for age_range in age_ranges:
                        start_year, end_year = age_range
                        age_type = f"{start_year}-{end_year}" if start_year != end_year else str(start_year)
                        
                        filtered_url = self.build_url_with_age_filter(url, age_type)
                        filtered_count = self.get_total_count_from_page(filtered_url)
                        
                        logger.info(f"Processing age range {age_type}: {filtered_count} items")
                        
                        if filtered_count > 0:
                            range_data = self._process_single_url_original(filtered_url, base_info)
                            all_data.extend(range_data)
                            logger.info(f"Collected {len(range_data)} items from age range {age_type}")
                
                processed_count += 1
                
            except Exception as e:
                logger.error(f"Error processing URL {url}: {e}")
                failed_count += 1
                continue
        
        logger.info(f"Enhanced processing complete. Success: {processed_count}, Failed: {failed_count}, Total items: {len(all_data)}")
        
        if not all_data:
            logger.warning("No data was collected during enhanced processing")
            return pd.DataFrame()
            
        return pd.DataFrame(all_data)
    
    def _process_single_url_original(self, url: str, base_info: dict, max_pages: int = 200) -> List[dict]:
        """
        Process a single URL with the original pagination logic but higher page limit
        
        Args:
            url: URL to process
            base_info: Base information dictionary
            max_pages: Maximum number of pages to process
            
        Returns:
            List of dictionaries containing car data
        """
        url_data = []
        
        try:
            # Process pages for this URL with higher limit
            page_count = 0
            consecutive_empty_pages = 0
            max_consecutive_empty = 3  # Stop after 3 consecutive empty pages
            
            for page in range(1, max_pages + 1):
                try:
                    # Add controlled delay
                    sleep_time = random.uniform(1, 3)
                    sleep(sleep_time)
                    
                    current_url = f"{url}Page={page}/" if not url.endswith('/') else f"{url}Page={page}/"
                    soup = self.get_html(current_url)
                    
                    if soup is None:
                        logger.warning(f"Failed to get HTML for: {current_url}")
                        consecutive_empty_pages += 1
                        if consecutive_empty_pages >= max_consecutive_empty:
                            break
                        continue
                        
                    # Process items on this page
                    items = soup.find_all("div", {"class": "ucItemBox"})
                    if not items:
                        logger.debug(f"No items found on page {page} for URL: {current_url}")
                        consecutive_empty_pages += 1
                        if consecutive_empty_pages >= max_consecutive_empty:
                            break
                        continue
                    
                    # Reset consecutive empty pages counter
                    consecutive_empty_pages = 0
                    
                    for item in items:
                        try:
                            # Extract car URL
                            link_element = item.find("a")
                            if not link_element or not link_element.get("href"):
                                continue
                                
                            car_url = BASE_URL + link_element.get("href")
                            
                            # Get detailed info
                            detail_info = self.parse_car_detail_info(
                                car_url, 
                                self.car_model_detection(url)
                            )
                            
                            if detail_info:  # Only add if we got some data
                                # Add color information
                                color_info = self.extract_color_from_item(item)
                                detail_info['color'] = color_info
                                
                                # Add base information
                                detail_info.update(base_info)
                                
                                url_data.append(detail_info)
                                
                        except Exception as e:
                            logger.error(f"Error processing item in {current_url}: {e}")
                            continue
                    
                    page_count += 1
                    
                    # Check if there's a next page
                    if not self.check_next_page(soup):
                        logger.debug(f"No next page found after page {page} for URL: {url}")
                        break
                        
                except Exception as e:
                    logger.error(f"Error processing page {page} for URL {url}: {e}")
                    consecutive_empty_pages += 1
                    if consecutive_empty_pages >= max_consecutive_empty:
                        break
                    continue
            
            logger.debug(f"Processed {page_count} pages for URL, collected {len(url_data)} items")
            
        except Exception as e:
            logger.error(f"Error in _process_single_url_original for URL {url}: {e}")
            
        return url_data

    def process_car_details(self, final_df: pd.DataFrame, use_age_filter: bool = True) -> pd.DataFrame:
        """
        Process car details with optional age filtering (backward compatibility method)
        
        Args:
            final_df: DataFrame containing car URLs to process
            use_age_filter: Whether to use the enhanced age filtering method
            
        Returns:
            DataFrame with processed car details
        """
        if use_age_filter:
            logger.info("Using enhanced age filtering method for complete data retrieval")
            return self.process_car_details_with_age_filter(final_df)
        else:
            logger.info("Using original method with 60-page limit")
            return self._process_car_details_original(final_df)
    
    def _process_car_details_original(self, final_df: pd.DataFrame) -> pd.DataFrame:
        """
        Original car details processing method (kept for backward compatibility)
        
        Args:
            final_df: DataFrame containing car URLs to process
            
        Returns:
            DataFrame with processed car details (limited to 60 pages per URL)
        """
        if final_df is None or final_df.empty:
            logger.warning("Empty DataFrame provided to _process_car_details_original")
            return pd.DataFrame()
            
        # Validate required columns
        required_columns = ['Web Address', '新車価格', 'グレード名', '年', 'CarMaker', 'モデル名']
        missing_columns = [col for col in required_columns if col not in final_df.columns]
        if missing_columns:
            logger.error(f"Missing required columns in final_df: {missing_columns}")
            return pd.DataFrame()
        
        all_data = []
        originals = final_df['Web Address'].tolist()
        processed_count = 0
        failed_count = 0
        
        logger.info(f"Starting original processing of {len(originals)} URLs (limited to 60 pages each)")
        
        for url_idx, url in enumerate(tqdm(originals, desc="Processing URLs (original method)")):
            try:
                if not url or pd.isna(url):
                    logger.warning(f"Skipping invalid URL at index {url_idx}: {url}")
                    failed_count += 1
                    continue
                    
                # Get base information for this URL
                url_matches = final_df[final_df['Web Address'] == url]
                if url_matches.empty:
                    logger.warning(f"No matching data found for URL: {url}")
                    failed_count += 1
                    continue
                    
                idx = url_matches.index[0]
                base_info = {
                    '新車価格': final_df.at[idx, "新車価格"],
                    'グレード名': final_df.at[idx, "グレード名"],
                    '年': final_df.at[idx, "年"],
                    'CarMaker': final_df.at[idx, 'CarMaker'],
                    'モデル名': final_df.at[idx, 'モデル名']
                }
                
                # Use original method with 60-page limit
                url_data = self._process_single_url_original(url, base_info, max_pages=60)
                all_data.extend(url_data)
                
                processed_count += 1
                logger.debug(f"Processed URL {url_idx+1}/{len(originals)} with {len(url_data)} items")
                
            except Exception as e:
                logger.error(f"Error processing URL {url}: {e}")
                failed_count += 1
                continue
        
        logger.info(f"Original processing complete. Success: {processed_count}, Failed: {failed_count}, Total items: {len(all_data)}")
        
        if not all_data:
            logger.warning("No data was collected during original processing")
            return pd.DataFrame()
            
        return pd.DataFrame(all_data)
    
    def preprocess_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocess DataFrame with enhanced error handling and validation
        
        Args:
            df: Raw DataFrame to preprocess
            
        Returns:
            Preprocessed DataFrame
        """
        if df is None or df.empty:
            logger.warning("Empty DataFrame provided to preprocess_dataframe")
            return pd.DataFrame()
            
        try:
            logger.info(f"Starting preprocessing of DataFrame with {len(df)} rows")
            original_count = len(df)
            
            # Remove columns with extremely long names (likely corrupted)
            long_columns = [col for col in df.columns if len(str(col)) >= 100]
            if long_columns:
                logger.info(f"Removing {len(long_columns)} columns with long names")
                df.drop(long_columns, axis=1, inplace=True)
            
            # Handle year column variations
            if '年式／初度検査' in df.columns and '年式／初度登録' in df.columns:
                null_mask = df['年式／初度登録'].isnull()
                df.loc[null_mask, '年式／初度登録'] = df.loc[null_mask, '年式／初度検査']
            
            # Extract year with enhanced error handling
            def safe_extract_year(x):
                try:
                    if pd.isna(x) or not isinstance(x, str):
                        return np.nan
                    year_match = re.search(r"[0-9]{4}", x)
                    if year_match:
                        year = int(year_match.group())
                        # Validate year range
                        if 1950 <= year <= datetime.now().year + 1:
                            return year
                    return np.nan
                except Exception:
                    return np.nan
            
            if "年式／初度登録" in df.columns:
                df["年式"] = df["年式／初度登録"].apply(safe_extract_year)
            
            # Process price with enhanced error handling
            def safe_extract_price(x):
                try:
                    if pd.isna(x) or x == "応談":
                        return np.nan
                    if isinstance(x, str):
                        # Remove non-numeric characters except decimal point
                        price_str = re.sub(r'[^\d.]', '', x)
                        if price_str and price_str.replace('.', '', 1).isdigit():
                            return float(price_str)
                    elif isinstance(x, (int, float)):
                        return float(x)
                    return np.nan
                except Exception:
                    return np.nan
            
            if "価格" in df.columns:
                df["価格"] = df["価格"].apply(safe_extract_price)
            
            # Process mileage with enhanced error handling
            def safe_extract_mileage(x):
                try:
                    if pd.isna(x):
                        return 0
                    x_str = str(x)
                    numbers = re.findall(r"[0-9.]+", x_str)
                    if numbers:
                        value = float(numbers[0])
                        # If value contains "万", multiply by 10000
                        if "万" in x_str:
                            return value * 10000
                        return value
                    return 0
                except Exception:
                    return 0
            
            if "走行距離" in df.columns:
                df["走行距離"] = df["走行距離"].apply(safe_extract_mileage)
            
            # Process color with safe conversion
            if "color" in df.columns:
                def safe_convert_color(x):
                    try:
                        if pd.isna(x):
                            return np.nan
                        return float(x)
                    except (ValueError, TypeError):
                        return np.nan
                        
                df["color"] = df["color"].apply(safe_convert_color)
            
            # Process car inspection (車検) with enhanced logic
            def calculate_remaining_months(x):
                try:
                    if pd.isna(x) or x == '車検整備なし':
                        return 0
                    elif x == '車検整備付':
                        return 24
                    elif isinstance(x, str) and '/' in x:
                        parts = x.split('/')
                        if len(parts) >= 2:
                            year = int(parts[0])
                            month = int(parts[1])
                            future_date = datetime(year=year, month=month, day=1)
                            now = datetime.now()
                            if future_date > now:
                                return max(0, (future_date - now).days // 30)
                    return np.nan
                except Exception:
                    return np.nan
            
            if '車検' in df.columns:
                df['RemainingMonths'] = df['車検'].fillna('車検整備なし').apply(calculate_remaining_months)
            
            # Process boolean columns with safe conversion
            boolean_columns = ["未使用車", "禁煙車", "ワンオーナー"]
            for col in boolean_columns:
                if col in df.columns:
                    def safe_boolean_convert(x):
                        try:
                            return 1 if x == "○" else 0
                        except Exception:
                            return 0
                    df[col] = df[col].apply(safe_boolean_convert)
            
            # Process repair history with enhanced pattern matching
            if "修復歴" in df.columns:
                def safe_repair_history(x):
                    try:
                        if pd.isna(x):
                            return 0
                        return 1 if "修復歴あり" in str(x) else 0
                    except Exception:
                        return 0
                        
                df["修復歴"] = df["修復歴"].apply(safe_repair_history)
            
            # Filter out invalid years and clean data
            if "年式" in df.columns:
                # Remove clearly invalid years
                df = df[~((df["年式"] == 1991) | (df["年式"] < 1950) | (df["年式"] > datetime.now().year + 1))]
            
            # Remove rows with missing critical data
            critical_columns = ["価格", "年式"]
            existing_critical = [col for col in critical_columns if col in df.columns]
            if existing_critical:
                before_drop = len(df)
                df.dropna(subset=existing_critical, inplace=True)
                after_drop = len(df)
                logger.info(f"Dropped {before_drop - after_drop} rows with missing critical data")
            
            # Create category and mission columns safely
            if len(df.columns) > 0:
                def safe_extract_category(x):
                    try:
                        if pd.isna(x) or not isinstance(x, str):
                            return None
                        parts = x.split()
                        return parts[1] if len(parts) > 1 else None
                    except Exception:
                        return None
                        
                df["Category"] = df.iloc[:, 0].apply(safe_extract_category)
            
            if "ミッション" in df.columns:
                def safe_mission_convert(x):
                    try:
                        return 1 if x == "MT" else 0
                    except Exception:
                        return 0
                        
                df["Mission"] = df["ミッション"].apply(safe_mission_convert)
            
            # Clean grade names
            if 'グレード名' in df.columns:
                def clean_grade_name(x):
                    try:
                        if pd.isna(x):
                            return x
                        # Remove MT indicators and left-hand drive indicators
                        cleaned = re.sub(r'\s*[（(][Mm][Tt][)）]\s*|\s*[(（]左ハンドル[)）]\s*', '', str(x))
                        return cleaned.strip()
                    except Exception:
                        return x
                        
                df['グレード名'] = df['グレード名'].apply(clean_grade_name)
            
            final_count = len(df)
            logger.info(f"Preprocessing complete. Rows: {original_count} -> {final_count}")
            
            return df
            
        except Exception as e:
            logger.error(f"Error in preprocessing DataFrame: {e}")
            return df  # Return original DataFrame if preprocessing fails
    
    def filter_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Filter dataframe to keep only relevant columns
        
        Args:
            df: Preprocessed dataframe
            
        Returns:
            Filtered dataframe
        """
        keywords = [
            "名称", 'Url', "color", '新車価格', "価格", "総額", "色", "Class_Category",
            'グレード名', '年', "年式", "走行距離", "地域", 'モデル名',
            "Mission", "RemainingMonths", "修復歴", 'ワンオーナー', 'エアロパーツ', 
            'CarMaker', 'ショップ名', '排気量'
        ]
        
        cols_to_keep = [col for col in df.columns if col in keywords]
        df_rev = df[cols_to_keep]
        
        missing_counts = df_rev.isna().sum()
        if missing_counts.sum() > 0:
            df_rev = df_rev.dropna()
            logger.info("欠損値を含む行を削除しました。")
        else:
            logger.info("欠損値は存在しません。")
    
        return df_rev
    
    def label_encode_dataframe(self, dataframe: pd.DataFrame) -> tuple:
        """
        Label encode categorical columns
        
        Args:
            dataframe: Input dataframe
            
        Returns:
            Tuple of (encoded_dataframe, label_encoders_dict)
        """
        result_df = dataframe.copy()
        le_dict = {}
        
        for column in dataframe.select_dtypes(include=['object']).columns:
            le = LabelEncoder()
            result_df[column] = le.fit_transform(dataframe[column])
            le_dict[column] = le
        
        return result_df, le_dict
    
    def process_by_carmaker(self, carmaker_indices=None, start=None, end=None):
        """
        Process car data by manufacturer
        
        Args:
            carmaker_indices: List of specific carmaker indices to process
            start: Start index for range processing
            end: End index for range processing
        """
        if self.filtered_df is None:
            self.load_and_filter_data()
        
        carmakers = self.filtered_df['CarMaker'].unique()
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Determine target carmakers
        target_carmakers = []
        if carmaker_indices is not None:
            if isinstance(carmaker_indices, list):
                target_carmakers = [carmakers[i] for i in carmaker_indices 
                                  if 0 <= i < len(carmakers)]
            else:
                if 0 <= carmaker_indices < len(carmakers):
                    target_carmakers = [carmakers[carmaker_indices]]
        else:
            start = 0 if start is None else start
            end = len(carmakers) if end is None else end
            target_carmakers = carmakers[start:end]
        
        for carmaker in target_carmakers:
            carmaker_df = self.filtered_df[self.filtered_df['CarMaker'] == carmaker]
            logger.info(f"Processing {carmaker}")
            
            carmaker_data = self.process_car_details_with_age_filter(carmaker_df)
            if carmaker_data.empty:
                logger.warning(f"No data found for {carmaker}. Skipping.")
                continue
            
            processed_df = self.preprocess_dataframe(carmaker_data)
            filtered_df = self.filter_dataframe(processed_df)
            unique_names = filtered_df['モデル名'].unique()
            
            for name in unique_names:
                logger.info(f"Processing model: {name}")
                df_name = filtered_df[filtered_df['モデル名'] == name]
                
                # Prepare features for ML
                x = df_name.drop(['Url', '地域', 'CarMaker', '総額', '名称', '色', 'ショップ名', '排気量'], axis=1)
                dummies = pd.get_dummies(x, drop_first=True)
                
                imputer = SimpleImputer(strategy='mean')
                dummies_imputed = imputer.fit_transform(dummies)
                dummies_imputed_df = pd.DataFrame(dummies_imputed, columns=dummies.columns)
                
                encoded_df, le_dict = self.label_encode_dataframe(dummies_imputed_df)
                
                X = encoded_df.drop(columns='価格')
                y = encoded_df['価格']
                
                # Train regression model
                kf = KFold(n_splits=5, shuffle=True, random_state=42)
                reg = LinearRegression()
                X_imputed = imputer.fit_transform(X)
                
                if len(X) > kf.get_n_splits():
                    cv_scores = cross_val_score(reg, X_imputed, y, cv=kf, scoring='r2')
                else:
                    logger.warning(f"Not enough samples for K-Fold Cross-Validation in '{name}' dataset.")
                
                reg.fit(X_imputed, y)
                predicted = reg.predict(X_imputed)
                encoded_df['predicted_price'] = predicted.round(2)
                encoded_df['difference'] = (encoded_df['価格'] - encoded_df['predicted_price']).round(2)
                
                # Predict zero mileage price
                走行距離_feature_name = "走行距離"
                if 走行距離_feature_name in X.columns:
                    X_zero_mileage = X.copy()
                    X_zero_mileage[走行距離_feature_name] = 0
                    X_zero_mileage_imputed = imputer.transform(X_zero_mileage)
                    predicted_prices_zero_mileage = reg.predict(X_zero_mileage_imputed)
                    encoded_df['predicted_price_zero_mileage'] = predicted_prices_zero_mileage.round(2)
                
                # Merge results
                columns_to_keep = ['predicted_price', 'difference', 'predicted_price_zero_mileage']
                encoded_df = encoded_df[columns_to_keep]
                
                df_name = df_name.reset_index(drop=True)
                df_name.set_index(encoded_df.index, inplace=True)
                merged_df = pd.merge(df_name, encoded_df, left_index=True, right_index=True, how='inner')
                
                # Reorder columns
                column_order = [
                    '名称', '年式', 'グレード名', '年', '色', 'Class_Category', 'Url', 'Mission', '修復歴',
                    'difference', '新車価格', '価格', '総額', 'predicted_price', '走行距離', 
                    'predicted_price_zero_mileage', 'CarMaker', 'モデル名', 'ショップ名', '排気量'
                ]
                merged_df = merged_df.reindex(columns=column_order)
                
                # Save to CSV
                today_date = datetime.today().strftime('%Y%m%d')
                filename = f"{today_date}_{name}_withexpectedPrice.csv"
                file_path = os.path.join(self.output_dir, filename)
                merged_df.to_csv(file_path, index=False, encoding='utf-8-sig')
                logger.info(f"Saved {file_path}")

    def get_error_statistics(self) -> Dict[str, int]:
        """
        Get error and success statistics
        
        Returns:
            Dictionary containing error and success counts
        """
        total_requests = self.success_count + self.error_count
        success_rate = (self.success_count / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'total_requests': total_requests,
            'successful_requests': self.success_count,
            'failed_requests': self.error_count,
            'success_rate_percent': round(success_rate, 2)
        }
    
    def reset_statistics(self):
        """Reset error and success counters"""
        self.error_count = 0
        self.success_count = 0
        logger.info("Statistics counters reset")
    
    def log_statistics(self):
        """Log current statistics"""
        stats = self.get_error_statistics()
        logger.info(f"Request Statistics: {stats}")
    
    def safe_shutdown(self):
        """
        Safely shutdown the scraper, closing sessions and logging final stats
        """
        try:
            self.log_statistics()
            if hasattr(self, 'session'):
                self.session.close()
                logger.info("Session closed successfully")
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
    
    def validate_and_clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Additional validation and cleaning step
        
        Args:
            df: DataFrame to validate and clean
            
        Returns:
            Cleaned and validated DataFrame
        """
        if df is None or df.empty:
            logger.warning("Empty DataFrame provided for validation")
            return pd.DataFrame()
        
        try:
            logger.info(f"Validating DataFrame with {len(df)} rows")
            original_count = len(df)
            
            # Remove duplicate rows
            if len(df) > 0:
                before_dup = len(df)
                df = df.drop_duplicates()
                after_dup = len(df)
                if before_dup != after_dup:
                    logger.info(f"Removed {before_dup - after_dup} duplicate rows")
            
            # Validate price ranges (reasonable car prices)
            if '価格' in df.columns:
                before_price = len(df)
                # Remove cars with unreasonable prices (less than 10万円 or more than 1億円)
                df = df[(df['価格'] >= 10) & (df['価格'] <= 100000)]
                after_price = len(df)
                if before_price != after_price:
                    logger.info(f"Removed {before_price - after_price} rows with unreasonable prices")
            
            # Validate mileage (reasonable ranges)
            if '走行距離' in df.columns:
                before_mileage = len(df)
                # Remove cars with unreasonable mileage (more than 1,000,000 km)
                df = df[df['走行距離'] <= 1000000]
                after_mileage = len(df)
                if before_mileage != after_mileage:
                    logger.info(f"Removed {before_mileage - after_mileage} rows with unreasonable mileage")
            
            # Validate year ranges
            if '年式' in df.columns:
                current_year = datetime.now().year
                before_year = len(df)
                df = df[(df['年式'] >= 1950) & (df['年式'] <= current_year + 1)]
                after_year = len(df)
                if before_year != after_year:
                    logger.info(f"Removed {before_year - after_year} rows with invalid years")
            
            final_count = len(df)
            logger.info(f"Validation complete. Rows: {original_count} -> {final_count}")
            
            return df
            
        except Exception as e:
            logger.error(f"Error during validation: {e}")
            return df

    def list_available_carmakers(self) -> pd.DataFrame:
        """
        List all available car makers with their indices
        
        Returns:
            DataFrame with car maker information
        """
        if self.filtered_df is None:
            self.load_and_filter_data()
        
        carmakers = self.filtered_df['CarMaker'].unique()
        carmaker_counts = self.filtered_df['CarMaker'].value_counts()
        
        carmaker_info = pd.DataFrame({
            'Index': range(len(carmakers)),
            'CarMaker': carmakers,
            'Record_Count': [carmaker_counts[maker] for maker in carmakers]
        })
        
        logger.info(f"Found {len(carmakers)} car makers")
        return carmaker_info
    
    def display_carmaker_list(self):
        """
        Display formatted list of available car makers
        """
        carmaker_info = self.list_available_carmakers()
        
        print("\n" + "="*60)
        print(" 📋 Available Car Makers")
        print("="*60)
        
        for i in range(0, len(carmaker_info), 2):
            left = carmaker_info.iloc[i]
            right_text = ""
            if i + 1 < len(carmaker_info):
                right = carmaker_info.iloc[i + 1]
                right_text = f"[{right['Index']:2d}] {right['CarMaker']:15s} ({right['Record_Count']:3d})"
            
            left_text = f"[{left['Index']:2d}] {left['CarMaker']:15s} ({left['Record_Count']:3d})"
            print(f"{left_text:30s} {right_text}")
        
        print("="*60)
        print(f"Total: {len(carmaker_info)} car makers\n")
    
    def interactive_carmaker_selection(self) -> List[int]:
        """
        Interactive car maker selection interface
        
        Returns:
            List of selected car maker indices
        """
        self.display_carmaker_list()
        
        print("🔧 Car Maker Selection Options:")
        print("  1. Enter specific indices (e.g., 0,2,5,10)")
        print("  2. Enter range (e.g., 0-5)")
        print("  3. Enter multiple ranges (e.g., 0-2,5-7,10-12)")
        print("  4. Enter car maker names (e.g., トヨタ,日産,ホンダ)")
        print()
        
        while True:
            try:
                selection = input("Select car makers (or 'q' to quit): ").strip()
                
                if selection.lower() == 'q':
                    return []
                
                # Parse the selection
                selected_indices = self._parse_selection(selection)
                
                if selected_indices:
                    # Validate selection
                    carmaker_info = self.list_available_carmakers()
                    max_index = len(carmaker_info) - 1
                    
                    valid_indices = [i for i in selected_indices if 0 <= i <= max_index]
                    invalid_indices = [i for i in selected_indices if i not in valid_indices]
                    
                    if invalid_indices:
                        print(f"⚠️  Invalid indices: {invalid_indices} (max: {max_index})")
                        continue
                    
                    # Confirm selection
                    selected_makers = carmaker_info[carmaker_info['Index'].isin(valid_indices)]
                    print(f"\n✅ Selected {len(valid_indices)} car makers:")
                    for _, row in selected_makers.iterrows():
                        print(f"   [{row['Index']:2d}] {row['CarMaker']} ({row['Record_Count']} records)")
                    
                    confirm = input("\nProceed with this selection? (y/n): ").strip().lower()
                    if confirm in ['y', 'yes']:
                        return valid_indices
                    else:
                        continue
                else:
                    print("❌ No valid selection found. Please try again.")
                    
            except KeyboardInterrupt:
                print("\n🛑 Selection cancelled.")
                return []
            except Exception as e:
                print(f"❌ Error in selection: {e}")
                continue
    
    def _parse_selection(self, selection: str) -> List[int]:
        """
        Parse user selection string into list of indices
        
        Args:
            selection: User input string
            
        Returns:
            List of car maker indices
        """
        indices = []
        
        try:
            # Handle empty or whitespace-only input
            if not selection or not selection.strip():
                return []
                
            # Check if it's car maker names
            if any(char.isalpha() and ord(char) > 127 for char in selection):  # Contains Japanese characters
                return self._parse_carmaker_names(selection)
            
            # Parse numeric selections
            parts = selection.split(',')
            
            for part in parts:
                part = part.strip()
                
                # Skip empty parts
                if not part:
                    continue
                    
                if '-' in part:
                    # Range selection (e.g., "0-5")
                    start, end = map(int, part.split('-'))
                    indices.extend(range(start, end + 1))
                else:
                    # Single index
                    indices.append(int(part))
            
            return sorted(list(set(indices)))  # Remove duplicates and sort
                
        except Exception as e:
            logger.error(f"Error parsing selection '{selection}': {e}")
            return []
    
    def _parse_carmaker_names(self, names: str) -> List[int]:
        """
        Parse car maker names into indices
        
        Args:
            names: Comma-separated car maker names
            
        Returns:
            List of matching indices
        """
        carmaker_info = self.list_available_carmakers()
        selected_names = [name.strip() for name in names.split(',')]
        indices = []
        
        for name in selected_names:
            matches = carmaker_info[carmaker_info['CarMaker'].str.contains(name, na=False)]
            if not matches.empty:
                indices.extend(matches['Index'].tolist())
            else:
                print(f"⚠️  No match found for: {name}")
        
        return sorted(list(set(indices)))
    
    def load_carmaker_config(self, config_file: str) -> List[int]:
        """
        Load car maker selection from configuration file
        
        Args:
            config_file: Path to configuration file
            
        Returns:
            List of car maker indices
        """
        try:
            if not os.path.exists(config_file):
                logger.warning(f"Config file not found: {config_file}")
                return []
            
            with open(config_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            indices = []
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#'):  # Skip comments and empty lines
                    try:
                        # Remove inline comments (everything after #)
                        if '#' in line:
                            line = line.split('#')[0].strip()
                        
                        if not line:  # Skip if line becomes empty after removing comment
                            continue
                            
                        if line.isdigit():
                            indices.append(int(line))
                        elif '-' in line:
                            start, end = map(int, line.split('-'))
                            indices.extend(range(start, end + 1))
                        else:
                            # Try to parse as car maker name
                            name_indices = self._parse_carmaker_names(line)
                            indices.extend(name_indices)
                    except Exception as e:
                        logger.warning(f"Skipping invalid line in config: {line} ({e})")
            
            logger.info(f"Loaded {len(indices)} car maker indices from {config_file}")
            return sorted(list(set(indices)))
            
        except Exception as e:
            logger.error(f"Error loading config file: {e}")
            return []
    
    def save_carmaker_config(self, indices: List[int], config_file: str):
        """
        Save car maker selection to configuration file
        
        Args:
            indices: List of car maker indices
            config_file: Path to save configuration
        """
        try:
            carmaker_info = self.list_available_carmakers()
            
            with open(config_file, 'w', encoding='utf-8') as f:
                f.write("# Car Maker Selection Configuration\n")
                f.write(f"# Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("# Format: One index per line, ranges (0-5), or car maker names\n\n")
                
                for idx in indices:
                    maker_row = carmaker_info[carmaker_info['Index'] == idx]
                    if not maker_row.empty:
                        maker_name = maker_row.iloc[0]['CarMaker']
                        f.write(f"{idx}  # {maker_name}\n")
                    else:
                        f.write(f"{idx}\n")
            
            logger.info(f"Saved configuration to {config_file}")
            
        except Exception as e:
            logger.error(f"Error saving config file: {e}")
    
    def process_selected_carmakers(self, selection_method: str = "interactive", config_file: str = None, indices: List[int] = None):
        """
        Process car makers using various selection methods
        
        Args:
            selection_method: "interactive", "config", "indices", or "all"
            config_file: Path to configuration file (for "config" method)
            indices: List of indices (for "indices" method)
        """
        try:
            if selection_method == "interactive":
                selected_indices = self.interactive_carmaker_selection()
            elif selection_method == "config" and config_file:
                selected_indices = self.load_carmaker_config(config_file)
            elif selection_method == "indices" and indices:
                selected_indices = indices
            elif selection_method == "all":
                carmaker_info = self.list_available_carmakers()
                selected_indices = carmaker_info['Index'].tolist()
            else:
                logger.error(f"Invalid selection method: {selection_method}")
                return
            
            if not selected_indices:
                logger.info("No car makers selected. Exiting.")
                return
            
            # Option to save selection for future use
            if selection_method == "interactive":
                save_config = input("Save this selection for future use? (y/n): ").strip().lower()
                if save_config in ['y', 'yes']:
                    config_path = input("Enter config file path (default: carmaker_selection.txt): ").strip()
                    if not config_path:
                        config_path = "carmaker_selection.txt"
                    self.save_carmaker_config(selected_indices, config_path)
            
            # Process selected car makers
            logger.info(f"Starting processing of {len(selected_indices)} selected car makers")
            self.process_by_carmaker(carmaker_indices=selected_indices)
            
        except Exception as e:
            logger.error(f"Error in process_selected_carmakers: {e}")
            raise

    def test_age_filter_functionality(self, test_url: str = None):
        """
        Test the age filter functionality with a sample URL
        
        Args:
            test_url: URL to test (uses example Toyota Alphard URL if not provided)
        """
        if test_url is None:
            # Use the example URL from the user's question
            test_url = "https://kakaku.com/kuruma/used/spec/Maker=1/Model=30022/Generation=41869/UCGrade=31821/"
        
        logger.info(f"Testing age filter functionality with URL: {test_url}")
        
        try:
            # Test 1: Get total count without filter
            total_count = self.get_total_count_from_page(test_url)
            logger.info(f"Total items without filter: {total_count}")
            
            # Test 2: Test with AgeType=2020 filter
            filtered_url_2020 = self.build_url_with_age_filter(test_url, "2020")
            count_2020 = self.get_total_count_from_page(filtered_url_2020)
            logger.info(f"Items with AgeType=2020: {count_2020}")
            logger.info(f"Filtered URL: {filtered_url_2020}")
            
            # Test 3: Test with range filter
            filtered_url_range = self.build_url_with_age_filter(test_url, "2018-2022")
            count_range = self.get_total_count_from_page(filtered_url_range)
            logger.info(f"Items with AgeType=2018-2022: {count_range}")
            logger.info(f"Filtered URL: {filtered_url_range}")
            
            # Test 4: Get optimal age ranges
            if total_count > 1000:
                logger.info("Testing optimal age range calculation...")
                age_ranges = self.get_optimal_age_ranges(test_url, max_items_per_range=1000)
                logger.info(f"Optimal age ranges: {age_ranges}")
                
                total_filtered = 0
                for age_range in age_ranges:
                    start_year, end_year = age_range
                    age_type = f"{start_year}-{end_year}" if start_year != end_year else str(start_year)
                    range_url = self.build_url_with_age_filter(test_url, age_type)
                    range_count = self.get_total_count_from_page(range_url)
                    total_filtered += range_count
                    logger.info(f"Range {age_type}: {range_count} items")
                
                logger.info(f"Total items across all ranges: {total_filtered}")
                logger.info(f"Coverage: {total_filtered/total_count*100:.1f}%" if total_count > 0 else "Coverage: N/A")
            
            return {
                'total_count': total_count,
                'count_2020': count_2020,
                'count_range': count_range,
                'test_successful': True
            }
            
        except Exception as e:
            logger.error(f"Error during age filter test: {e}")
            return {
                'test_successful': False,
                'error': str(e)
            }


def main():
    """
    Enhanced main function with comprehensive error handling and flexible car maker selection
    """
    scraper = None
    
    try:
        logger.info("Starting Car Data Scraper with enhanced error handling")
        
        # Initialize scraper with updated output directory
        scraper = CarDataScraper(
            csv_path="allmaker_url20251031.csv",
            output_dir="output"  # Updated path
        )
        
        # Test the age filter functionality first
        print("\n🔧 Testing Age Filter Functionality...")
        test_results = scraper.test_age_filter_functionality()
        
        if test_results.get('test_successful'):
            print(f"✅ Age filter test completed successfully!")
            print(f"   Total items without filter: {test_results.get('total_count', 'N/A')}")
            print(f"   Items with AgeType=2020: {test_results.get('count_2020', 'N/A')}")
            print(f"   Items with range filter: {test_results.get('count_range', 'N/A')}")
        else:
            print(f"❌ Age filter test failed: {test_results.get('error', 'Unknown error')}")
        
        # Load data with error handling
        filtered_df = scraper.load_and_filter_data()
        
        # Interactive menu for selection
        print("\n🚗 Enhanced Car Data Scraper Options:")
        print("  1. Test age filter functionality only")
        print("  2. Interactive car maker selection (full processing)")
        print("  3. Quick test - Process specific car maker with age filter")
        print("  4. Compare old vs new method")
        
        print("  5. Compare CSV files (allmaker_url1016.csv vs allmaker_url20251022.csv)")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1":
            print("Age filter test already completed above.")
            
        elif choice == "2":
            # Example 1: Interactive selection
            print("🚗 Starting Interactive Car Maker Selection")
            scraper.process_selected_carmakers(selection_method="interactive")
            
        elif choice == "3":
            # Quick test with a specific car maker
            print("🚗 Quick Test - Processing first available car maker")
            carmaker_info = scraper.list_available_carmakers()
            if not carmaker_info.empty:
                first_carmaker_idx = carmaker_info.iloc[0]['Index']
                print(f"Processing: {carmaker_info.iloc[0]['CarMaker']}")
                scraper.process_selected_carmakers(
                    selection_method="indices", 
                    indices=[first_carmaker_idx]
                )
            else:
                print("No car makers available for testing.")
                
        elif choice == "4":
            # Compare methods
            print("🚗 Comparing Old vs New Processing Methods")
            carmaker_info = scraper.list_available_carmakers()
            if not carmaker_info.empty:
                first_carmaker_idx = carmaker_info.iloc[0]['Index']
                carmaker_name = carmaker_info.iloc[0]['CarMaker']
                print(f"Testing with: {carmaker_name}")
                
                # Test with new method
                carmaker_df = filtered_df[filtered_df['CarMaker'] == carmaker_name].head(1)  # Limit to 1 URL for testing
                if not carmaker_df.empty:
                    print("Testing new age-filtered method...")
                    new_data = scraper.process_car_details_with_age_filter(carmaker_df)
                    print(f"New method collected: {len(new_data)} items")
                    
                    print("Testing original method...")
                    old_data = scraper.process_car_details(carmaker_df, use_age_filter=False)
                    print(f"Original method collected: {len(old_data)} items")
                    
                    improvement = len(new_data) - len(old_data)
                    print(f"Improvement: {improvement} additional items ({improvement/len(old_data)*100:.1f}% increase)" if len(old_data) > 0 else "Improvement: N/A")
                else:
                    print("No data available for comparison test.")
            else:
                print("No car makers available for testing.")
        
        # Get statistics
        stats = scraper.get_error_statistics()
        print(f"\n📊 Scraping completed with {stats['success_rate_percent']}% success rate")
        
    except Exception as e:
        logger.error(f"Script execution failed: {e}")
    finally:
        # Always cleanup
        if 'scraper' in locals():
            scraper.safe_shutdown()


# Usage example
if __name__ == "__main__":
    # Example of using the improved scraper with flexible selection
    try:
        # Initialize with custom parameters
        scraper = CarDataScraper(
            csv_path="allmaker_url20251022.csv",
            output_dir="output"  # Updated path
        )
        
        # Test the age filter functionality first
        print("\n🔧 Testing Age Filter Functionality...")
        test_results = scraper.test_age_filter_functionality()
        
        if test_results.get('test_successful'):
            print(f"✅ Age filter test completed successfully!")
            print(f"   Total items without filter: {test_results.get('total_count', 'N/A')}")
            print(f"   Items with AgeType=2020: {test_results.get('count_2020', 'N/A')}")
            print(f"   Items with range filter: {test_results.get('count_range', 'N/A')}")
        else:
            print(f"❌ Age filter test failed: {test_results.get('error', 'Unknown error')}")
        
        # Load data with error handling
        filtered_df = scraper.load_and_filter_data()
        
        # Interactive menu for selection
        print("\n🚗 Enhanced Car Data Scraper Options:")
        print("  1. Test age filter functionality only")
        print("  2. Interactive car maker selection (full processing)")
        print("  3. Quick test - Process specific car maker with age filter")
        print("  4. Compare old vs new method")
        
        print("  5. Compare CSV files (allmaker_url1016.csv vs allmaker_url20251022.csv)")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1":
            print("Age filter test already completed above.")
            
        elif choice == "2":
            # Example 1: Interactive selection
            print("🚗 Starting Interactive Car Maker Selection")
            scraper.process_selected_carmakers(selection_method="interactive")
            
        elif choice == "3":
            # Quick test with a specific car maker
            print("🚗 Quick Test - Processing first available car maker")
            carmaker_info = scraper.list_available_carmakers()
            if not carmaker_info.empty:
                first_carmaker_idx = carmaker_info.iloc[0]['Index']
                print(f"Processing: {carmaker_info.iloc[0]['CarMaker']}")
                scraper.process_selected_carmakers(
                    selection_method="indices", 
                    indices=[first_carmaker_idx]
                )
            else:
                print("No car makers available for testing.")
                
        elif choice == "4":
            # Compare methods
            print("🚗 Comparing Old vs New Processing Methods")
            carmaker_info = scraper.list_available_carmakers()
            if not carmaker_info.empty:
                first_carmaker_idx = carmaker_info.iloc[0]['Index']
                carmaker_name = carmaker_info.iloc[0]['CarMaker']
                print(f"Testing with: {carmaker_name}")
                
                # Test with new method
                carmaker_df = filtered_df[filtered_df['CarMaker'] == carmaker_name].head(1)  # Limit to 1 URL for testing
                if not carmaker_df.empty:
                    print("Testing new age-filtered method...")
                    new_data = scraper.process_car_details_with_age_filter(carmaker_df)
                    print(f"New method collected: {len(new_data)} items")
                    
                    print("Testing original method...")
                    old_data = scraper.process_car_details(carmaker_df, use_age_filter=False)
                    print(f"Original method collected: {len(old_data)} items")
                    
                    improvement = len(new_data) - len(old_data)
                    print(f"Improvement: {improvement} additional items ({improvement/len(old_data)*100:.1f}% increase)" if len(old_data) > 0 else "Improvement: N/A")
                else:
                    print("No data available for comparison test.")
            else:
                print("No car makers available for testing.")
        
        # Get statistics
        stats = scraper.get_error_statistics()
        print(f"\n📊 Scraping completed with {stats['success_rate_percent']}% success rate")
        
    except Exception as e:
        logger.error(f"Script execution failed: {e}")
    finally:
        # Always cleanup
        if 'scraper' in locals():
            scraper.safe_shutdown() 