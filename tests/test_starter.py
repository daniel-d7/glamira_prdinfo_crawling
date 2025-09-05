import pandas as pd
import requests
from bs4 import BeautifulSoup
import json
import os
import time
import sqlite3
import re
import logging
from typing import Tuple, Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/scraping_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def test_scraping():
    """Test the scraping with just a few products"""
    
    # Test with first 3 domains and first 5 products
    domains_df = pd.read_csv("data/input_data/domains_cleaned.csv")
    products_df = pd.read_csv("data/input_data/node1.csv")
    
    test_domains = domains_df.head(3)['domains'].tolist()
    test_products = products_df.head(5)['pid'].astype(str).tolist()
    
    output_dir = "data/scraped/output_test"
    os.makedirs(output_dir, exist_ok=True)
    
    logger.info(f"Testing with {len(test_domains)} domains and {len(test_products)} products")
    logger.info(f"Domains: {test_domains}")
    logger.info(f"Products: {test_products}")
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })
    
    success_count = 0
    
    for domain in test_domains:
        for product_id in test_products:
            url = f"https://{domain}/catalog/product/view/id/{product_id}"
            
            try:
                logger.info(f"Testing: {url}")
                response = session.get(url, timeout=10)
                
                logger.info(f"Status: {response.status_code} for {url}")
                
                if response.status_code == 200:
                    # Save basic info regardless of react_data
                    result = {
                        "url": url,
                        "domain": domain,
                        "product_id": product_id,
                        "status_code": response.status_code,
                        "page_size": len(response.text),
                        "timestamp": time.time()
                    }
                    
                    # Try to extract any data
                    soup = BeautifulSoup(response.text, 'html.parser')
                    title = soup.find('title')
                    if title:
                        result["page_title"] = title.text.strip()
                    
                    # Look for any script with substantial content
                    scripts = soup.find_all('script')
                    script_info = []
                    
                    for i, script in enumerate(scripts):
                        if script.string and len(script.string) > 100:
                            content = script.string
                            info = {
                                "index": i,
                                "size": len(content),
                                "has_json": '{' in content and '}' in content,
                                "has_product": 'product' in content.lower(),
                                "preview": content[:200]
                            }
                            script_info.append(info)
                    
                    result["scripts_info"] = script_info
                    
                    # Save result
                    filename = f"test_{domain}_{product_id}.json"
                    filepath = os.path.join(output_dir, filename)
                    
                    with open(filepath, 'w', encoding='utf-8') as f:
                        json.dump(result, f, indent=2, ensure_ascii=False)
                    
                    success_count += 1
                    logger.info(f"Saved test result to {filepath}")
                
                # Add delay between requests
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"Error testing {url}: {e}")
    
    logger.info(f"Test completed. Successfully processed {success_count} URLs")
    return success_count > 0

if __name__ == "__main__":
    test_scraping()
