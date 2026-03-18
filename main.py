from car_scraper import CarDataScraper
# 国産メーカーのみ処理
scraper = CarDataScraper()
scraper.process_selected_carmakers(selection_method="config", config_file="mainbrand.txt")