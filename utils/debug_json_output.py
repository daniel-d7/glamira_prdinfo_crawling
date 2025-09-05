#!/usr/bin/env python3
"""
Debug test to identify JSON output issues
"""

import os
import sys
import json
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from main import GlamiraScraper

def debug_json_output():
    """Debug JSON output issues step by step"""
    print("🔍 Debug: JSON Output Issues")
    print("=" * 40)
    
    # Configuration
    domains_file = "data/input_data/domains_cleaned.csv"
    products_file = "data/input_data/node1.csv"
    output_dir = "data/scraped"
    
    print(f"Output directory: {os.path.abspath(output_dir)}")
    print(f"Directory exists: {os.path.exists(output_dir)}")
    print(f"Directory writable: {os.access(output_dir, os.W_OK)}")
    
    # Test 1: Initialize scraper
    print("\n🧪 Test 1: Initialize scraper")
    try:
        scraper = GlamiraScraper(domains_file, products_file, output_dir)
        print("✓ Scraper initialized successfully")
        print(f"✓ Domains loaded: {len(scraper.domains_df)}")
        print(f"✓ Products loaded: {len(scraper.products_df)}")
    except Exception as e:
        print(f"❌ Failed to initialize scraper: {e}")
        return False
    
    # Test 2: Test save_product_data directly
    print("\n🧪 Test 2: Test save_product_data method")
    try:
        test_data = {
            "test": True,
            "domain": "test.glamira.com",
            "product_id": "debug123",
            "message": "This is a debug test"
        }
        
        print("Calling save_product_data...")
        scraper.save_product_data("test.glamira.com", "debug123", test_data)
        
        # Check if file exists
        expected_file = os.path.join(output_dir, "test.glamira.com_debug123.json")
        if os.path.exists(expected_file):
            print(f"✓ Test file created: {expected_file}")
            file_size = os.path.getsize(expected_file)
            print(f"✓ File size: {file_size} bytes")
            
            # Read and verify content
            with open(expected_file, 'r', encoding='utf-8') as f:
                saved_data = json.load(f)
            
            if saved_data == test_data:
                print("✓ File content matches expected data")
            else:
                print("❌ File content mismatch")
                print(f"Expected: {test_data}")
                print(f"Got: {saved_data}")
        else:
            print(f"❌ Test file not created: {expected_file}")
            
    except Exception as e:
        print(f"❌ Error in save_product_data test: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 3: Test with real data
    print("\n🧪 Test 3: Test with real domain/product")
    try:
        if len(scraper.domains_df) > 0 and len(scraper.products_df) > 0:
            test_domain = scraper.domains_df.iloc[0]['domains']
            test_product = str(scraper.products_df.iloc[0]['pid'])
            
            print(f"Testing with: {test_domain}/{test_product}")
            
            # Count existing files
            existing_files = [f for f in os.listdir(output_dir) if f.endswith('.json')]
            print(f"Existing JSON files: {len(existing_files)}")
            
            # Test the process
            print("Calling process_product_with_worker_id...")
            result = scraper.process_product_with_worker_id(test_domain, test_product, 1)
            
            print(f"Process result: {result}")
            
            # Check for new files
            new_files = [f for f in os.listdir(output_dir) if f.endswith('.json')]
            print(f"JSON files after test: {len(new_files)}")
            
            if len(new_files) > len(existing_files):
                newest_files = set(new_files) - set(existing_files)
                print(f"✓ New files created: {list(newest_files)}")
                
                for new_file in newest_files:
                    file_path = os.path.join(output_dir, new_file)
                    file_size = os.path.getsize(file_path)
                    print(f"  {new_file}: {file_size} bytes")
            else:
                print("❌ No new files created")
        else:
            print("❌ No test data available")
            
    except Exception as e:
        print(f"❌ Error in real data test: {e}")
        import traceback
        traceback.print_exc()
    
    # Clean up test files
    print("\n🧹 Cleaning up test files...")
    test_file = os.path.join(output_dir, "test.glamira.com_debug123.json")
    if os.path.exists(test_file):
        os.remove(test_file)
        print("✓ Test file removed")

if __name__ == "__main__":
    debug_json_output()
