"""
Test the updated scraper with field filtering on a single product
"""
from main import GlamiraScraper
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_filtered_scraper():
    """Test the updated scraper with field filtering"""
    
    print("🧪 Testing updated scraper with field filtering...")
    
    # Initialize scraper (but we'll only test the extraction method)
    scraper = GlamiraScraper("data/input_data/domains_cleaned.csv", "data/input_data/node1.csv", "data/scraped/output_test")
    
    # Test with a known working domain and product
    domain = "glamira.at"
    product_id = "110474"
    
    success, data = scraper.fetch_product_data(domain, product_id)
    
    if success and data:
        print("✅ Successfully fetched and filtered data!")
        print(f"📊 Fields extracted: {data.get('_metadata', {}).get('fields_extracted', 'Unknown')}")
        print(f"📋 Available fields: {list(data.keys())}")
        
        # Save test result
        filename = f"test_filtered_{domain}_{product_id}.json"
        filepath = f"data/scraped/output_test/{filename}"
        
        import json
        import os
        os.makedirs("data/scraped/output_test", exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved filtered data to: {filepath}")
        
        return True
    else:
        print("❌ Failed to fetch data")
        return False

if __name__ == "__main__":
    test_filtered_scraper()
