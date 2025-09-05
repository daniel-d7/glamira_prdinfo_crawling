#!/usr/bin/env python3
"""
Quick test to verify JSON output is working
"""

import os
import sys
import json
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from main import GlamiraScraper

def quick_test():
    """Quick test of JSON output functionality"""
    print("Quick JSON Output Test")
    print("=" * 25)
    
    # Configuration
    domains_file = "data/input_data/domains_cleaned.csv"
    products_file = "data/input_data/node1.csv"
    output_dir = "data/scraped"
    
    try:
        # Initialize scraper
        scraper = GlamiraScraper(domains_file, products_file, output_dir)
        print(f"✓ Scraper initialized")
        print(f"✓ Output directory: {os.path.abspath(output_dir)}")
        
        # Check if CSV files have data
        if len(scraper.domains_df) == 0:
            print("❌ No domains found in CSV file")
            return False
        
        if len(scraper.products_df) == 0:
            print("❌ No products found in CSV file")
            return False
        
        # Get test data
        test_domain = scraper.domains_df.iloc[0]['domains']
        test_product = str(scraper.products_df.iloc[0]['pid'])
        
        print(f"✓ Test domain: {test_domain}")
        print(f"✓ Test product: {test_product}")
        
        # Count existing files
        existing_files = len([f for f in os.listdir(output_dir) if f.endswith('.json')])
        print(f"✓ Existing JSON files: {existing_files}")
        
        # Test direct save functionality
        test_data = {
            "domain": test_domain,
            "product_id": test_product,
            "test_data": True,
            "message": "This is a test JSON output",
            "status": "test_successful"
        }
        
        print(f"\nTesting direct save...")
        scraper.save_product_data(test_domain, test_product, test_data)
        
        # Check if file was created
        expected_filename = f"{test_domain}_{test_product}.json"
        expected_path = os.path.join(output_dir, expected_filename)
        
        if os.path.exists(expected_path):
            file_size = os.path.getsize(expected_path)
            print(f"✓ JSON file created: {expected_filename} ({file_size} bytes)")
            
            # Verify content
            with open(expected_path, 'r', encoding='utf-8') as f:
                saved_data = json.load(f)
            
            if saved_data == test_data:
                print("✓ JSON content verified successfully")
                print("\nJSON Output Test: PASSED ✅")
                return True
            else:
                print("❌ JSON content mismatch")
                return False
        else:
            print(f"❌ JSON file not created at: {expected_path}")
            print(f"Directory contents: {os.listdir(output_dir)}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Glamira Scraper - JSON Output Verification")
    print("=" * 45)
    
    result = quick_test()
    
    if result:
        print("\n🎉 JSON output is working correctly!")
        print("You can now run full scraping with:")
        print("  python scripts/start_scraping.py")
    else:
        print("\n⚠️  JSON output test failed. Check configuration.")
    
    print(f"\nOutput directory: {os.path.abspath('data/scraped')}")
