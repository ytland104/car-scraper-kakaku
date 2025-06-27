#!/usr/bin/env python3
"""
Usage Examples for Enhanced Car Data Scraper

This file demonstrates various ways to select and process car makers
using the improved CarDataScraper with flexible selection methods.
"""

from car_scraper import CarDataScraper
import logging

def example_interactive_selection():
    """
    Example 1: Interactive car maker selection
    """
    print("🚗 Example 1: Interactive Car Maker Selection")
    print("-" * 50)
    
    scraper = CarDataScraper(
        csv_path="allmaker_url1016.csv",
        output_dir="car_scraper/output"
    )
    
    # Load data first
    scraper.load_and_filter_data()
    
    # Interactive selection - user can choose from displayed list
    scraper.process_selected_carmakers(selection_method="interactive")
    
    # Cleanup
    scraper.safe_shutdown()

def example_config_file_selection():
    """
    Example 2: Use configuration file for car maker selection
    """
    print("🚗 Example 2: Configuration File Selection")
    print("-" * 50)
    
    # First, create a sample config file
    sample_config = """# Car Maker Selection Configuration
# Generated on: 2024-01-15 10:30:00
# Format: One index per line, ranges (0-5), or car maker names

0   # トヨタ
2   # 日産
5   # ホンダ
10-12  # Range selection
# 15  # This line is commented out
"""
    
    with open("my_carmakers.txt", "w", encoding="utf-8") as f:
        f.write(sample_config)
    
    scraper = CarDataScraper(
        csv_path="allmaker_url1016.csv",
        output_dir="car_scraper/output"
    )
    
    # Load data
    scraper.load_and_filter_data()
    
    # Process using config file
    scraper.process_selected_carmakers(
        selection_method="config", 
        config_file="my_carmakers.txt"
    )
    
    # Cleanup
    scraper.safe_shutdown()

def example_direct_indices_selection():
    """
    Example 3: Direct specification of car maker indices
    """
    print("🚗 Example 3: Direct Indices Selection")
    print("-" * 50)
    
    scraper = CarDataScraper(
        csv_path="allmaker_url1016.csv",
        output_dir="car_scraper/output"
    )
    
    # Load data
    scraper.load_and_filter_data()
    
    # First, check what car makers are available
    carmaker_info = scraper.list_available_carmakers()
    print("Available car makers:")
    print(carmaker_info.head(10))
    
    # Select specific indices directly
    selected_indices = [0, 2, 5, 8, 10]  # Example selection
    
    scraper.process_selected_carmakers(
        selection_method="indices", 
        indices=selected_indices
    )
    
    # Cleanup
    scraper.safe_shutdown()

def example_list_carmakers_only():
    """
    Example 4: Just list available car makers without processing
    """
    print("🚗 Example 4: List Available Car Makers")
    print("-" * 50)
    
    scraper = CarDataScraper(csv_path="allmaker_url1016.csv")
    
    # Load data
    scraper.load_and_filter_data()
    
    # Display formatted list
    scraper.display_carmaker_list()
    
    # Or get as DataFrame for further processing
    carmaker_df = scraper.list_available_carmakers()
    print(f"\nTotal car makers: {len(carmaker_df)}")
    print(f"Total records: {carmaker_df['Record_Count'].sum()}")

def example_batch_processing():
    """
    Example 5: Batch processing with predefined groups
    """
    print("🚗 Example 5: Batch Processing with Groups")
    print("-" * 50)
    
    scraper = CarDataScraper(
        csv_path="allmaker_url1016.csv",
        output_dir="car_scraper/output"
    )
    
    # Load data
    scraper.load_and_filter_data()
    
    # Define different groups for processing
    groups = {
        "japanese_luxury": [0, 1, 2],     # Example: Lexus, Infiniti, Acura
        "european_brands": [10, 11, 12],  # Example: BMW, Mercedes, Audi
        "sports_cars": [20, 21, 22],      # Example: Porsche, Ferrari, Lamborghini
    }
    
    for group_name, indices in groups.items():
        print(f"\n📁 Processing group: {group_name}")
        try:
            scraper.process_selected_carmakers(
                selection_method="indices", 
                indices=indices
            )
            print(f"✅ Completed processing {group_name}")
        except Exception as e:
            print(f"❌ Error processing {group_name}: {e}")
            continue
    
    # Cleanup
    scraper.safe_shutdown()

def main():
    """
    Main function to run examples
    """
    print("🚗 Car Data Scraper - Usage Examples")
    print("=" * 60)
    
    examples = {
        "1": ("Interactive Selection", example_interactive_selection),
        "2": ("Configuration File", example_config_file_selection),
        "3": ("Direct Indices", example_direct_indices_selection),
        "4": ("List Car Makers Only", example_list_carmakers_only),
        "5": ("Batch Processing", example_batch_processing),
    }
    
    print("\nAvailable examples:")
    for key, (name, _) in examples.items():
        print(f"  {key}. {name}")
    
    while True:
        try:
            choice = input("\nSelect example (1-5) or 'q' to quit: ").strip()
            
            if choice.lower() == 'q':
                print("👋 Goodbye!")
                break
                
            if choice in examples:
                name, func = examples[choice]
                print(f"\n🚀 Running: {name}")
                func()
                print(f"✅ Completed: {name}")
            else:
                print("❌ Invalid choice. Please select 1-5.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error running example: {e}")

if __name__ == "__main__":
    # Set logging level for examples
    logging.getLogger('car_scraper').setLevel(logging.INFO)
    
    main() 