#!/usr/bin/env python3
"""
Start scraping script with proper JSON output
"""

import os
import sys
import logging
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from main import GlamiraScraper

def main():
    """Run batch scraping with proper JSON output"""
    print("Glamira Scraper - Batch Testing Mode")
    print("=" * 40)
    
    # Configuration
    domains_file = "data/input_data/domains_cleaned.csv"
    products_file = "data/input_data/node1.csv"
    output_dir = "data/scraped"  # This will save JSON files directly to data/scraped/
    max_workers = 3
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/scraping.log'),
            logging.StreamHandler()
        ]
    )
    
    try:
        print(f"Domains file: {domains_file}")
        print(f"Products file: {products_file}")
        print(f"Output directory: {output_dir}")
        print(f"Max workers: {max_workers}")
        
        # Initialize scraper
        print("\nInitializing scraper...")
        scraper = GlamiraScraper(domains_file, products_file, output_dir)
        
        print(f"✓ Loaded {len(scraper.domains_df)} domains")
        print(f"✓ Loaded {len(scraper.products_df)} products")
        print(f"✓ Found {len(scraper.proxy_configs)} proxy configurations")
        print(f"✓ Output directory: {os.path.abspath(output_dir)}")
        
        # Count existing JSON files
        existing_files = len([f for f in os.listdir(output_dir) if f.endswith('.json')])
        print(f"✓ Existing JSON files: {existing_files}")
        
        print(f"\nStarting scraping with {max_workers} workers...")
        print("-" * 40)
        
        # Run scraping
        completed, failed = scraper.run_scraping(max_workers)
        
        # Count new JSON files
        new_files = len([f for f in os.listdir(output_dir) if f.endswith('.json')])
        created_files = new_files - existing_files
        
        print(f"\nScraping Summary:")
        print(f"Completed: {completed}")
        print(f"Failed: {failed}")
        print(f"Total: {completed + failed}")
        print(f"JSON files created: {created_files}")
        print(f"Total JSON files: {new_files}")
        
        if created_files > 0:
            print(f"\n✓ JSON files successfully created in: {os.path.abspath(output_dir)}")
            # Show some examples
            json_files = [f for f in os.listdir(output_dir) if f.endswith('.json')]
            print("Example files:")
            for i, filename in enumerate(sorted(json_files)[-5:]):  # Show last 5 files
                file_path = os.path.join(output_dir, filename)
                file_size = os.path.getsize(file_path)
                print(f"  {filename} ({file_size} bytes)")
        else:
            print(f"\n⚠️  No JSON files were created. Check logs for errors.")
        
        return completed, failed
        
    except Exception as e:
        print(f"\n❌ Error during scraping: {e}")
        import traceback
        traceback.print_exc()
        return 0, 1

if __name__ == "__main__":
    main()
