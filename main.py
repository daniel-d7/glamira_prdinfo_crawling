import pandas as pd
import requests
from bs4 import BeautifulSoup
import json
import os
import time
import sqlite3
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
from urllib.parse import urljoin
from typing import Tuple, Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/scraping.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class GlamiraScraper:
    def __init__(self, domains_file: str, products_file: str, output_dir: str):
        self.domains_file = domains_file
        self.products_file = products_file
        self.output_dir = output_dir
        self.db_path = "checkpoint.db"
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize database
        self.init_database()
        
        # Load data
        self.domains_df = pd.read_csv(self.domains_file)
        self.products_df = pd.read_csv(self.products_file)
        
        logger.info(f"Loaded {len(self.domains_df)} domains and {len(self.products_df)} products")
    
    def init_database(self):
        """Initialize SQLite database for checkpoints"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS checkpoints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                domain TEXT NOT NULL,
                product_id TEXT NOT NULL,
                status TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(domain, product_id)
            )
        ''')
        conn.commit()
        conn.close()
    
    def clear_checkpoint_database(self):
        """Clear all checkpoints from the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM checkpoints')
            conn.commit()
            conn.close()
            logger.info("Checkpoint database cleared successfully")
        except Exception as e:
            logger.error(f"Error clearing checkpoint database: {e}")
    
    def get_checkpoint_stats(self):
        """Get statistics about the checkpoint database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get total counts by status
            cursor.execute('SELECT status, COUNT(*) FROM checkpoints GROUP BY status')
            stats = dict(cursor.fetchall())
            
            # Get total count
            cursor.execute('SELECT COUNT(*) FROM checkpoints')
            total = cursor.fetchone()[0]
            
            conn.close()
            return stats, total
        except Exception as e:
            logger.error(f"Error getting checkpoint stats: {e}")
            return {}, 0
    
    def save_checkpoint(self, domain: str, product_id: str, status: str):
        """Save checkpoint to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO checkpoints (domain, product_id, status)
            VALUES (?, ?, ?)
        ''', (domain, product_id, status))
        conn.commit()
        conn.close()
    
    def is_processed(self, domain: str, product_id: str) -> bool:
        """Check if combination has been successfully processed"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT status FROM checkpoints 
            WHERE domain = ? AND product_id = ? AND status = 'success'
        ''', (domain, product_id))
        result = cursor.fetchone()
        conn.close()
        return result is not None
    
    def extract_react_data(self, html_content: str) -> Optional[dict]:
        """Extract react_data from HTML content and filter for specific fields"""
        
        # Define the specific fields we want to extract
        desired_fields = [
            "product_id", "name", "sku", "attribute_set_id", "attribute_set", 
            "type_id", "price", "min_price", "max_price", "min_price_format", 
            "max_price_format", "gold_weight", "none_metal_weight", "fixed_silver_weight", 
            "material_design", "qty", "collection", "collection_id", "product_type", 
            "product_type_value", "category", "category_name", "store_code", 
            "platinum_palladium_info_in_alloy", "bracelet_without_chain", 
            "show_popup_quantity_eternity", "visible_contents", "gender"
        ]
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Look for script tags containing react_data or product data
            scripts = soup.find_all('script', type='text/javascript')
            
            for script in scripts:
                script_content = script.string if script.string else ""
                if not script_content:
                    continue
                
                # Multiple patterns to look for based on the screenshot
                patterns = [
                    # Standard react_data pattern
                    r'var\s+react_data\s*=\s*({.*?});',
                    r'window\.react_data\s*=\s*({.*?});',
                    
                    # Product data patterns from the screenshot
                    r'"product_id":\s*"?\d+"?.*?({[^}]*"product_id"[^}]*})',
                    r'({[^}]*"product_id"[^}]*"name"[^}]*})',
                    
                    # Look for large JSON objects that might contain product data
                    r'var\s+\w+\s*=\s*({.*?"product_id".*?});',
                    r'window\.\w+\s*=\s*({.*?"product_id".*?});',
                    
                    # Generic large JSON objects
                    r'=\s*({.*?"attribute_set_id".*?});',
                    r'=\s*({.*?"price".*?"sku".*?});'
                ]
                
                for pattern in patterns:
                    matches = re.finditer(pattern, script_content, re.DOTALL)
                    for match in matches:
                        try:
                            json_str = match.group(1)
                            data = json.loads(json_str)
                            
                            # Validate that this looks like product data
                            if isinstance(data, dict):
                                # Check for common product fields
                                product_indicators = ['product_id', 'sku', 'name', 'price', 'attribute_set_id']
                                if any(indicator in str(data).lower() for indicator in product_indicators):
                                    logger.info("Found product data in script")
                                    
                                    # Filter data to only include desired fields
                                    filtered_data = {}
                                    for field in desired_fields:
                                        if field in data:
                                            filtered_data[field] = data[field]
                                    
                                    # Add metadata for tracking
                                    filtered_data['_metadata'] = {
                                        'extraction_timestamp': time.time(),
                                        'fields_extracted': len(filtered_data) - 1,  # -1 for metadata
                                        'total_fields_available': len(data)
                                    }
                                    
                                    logger.info(f"Filtered data: {len(filtered_data)-1}/{len(desired_fields)} desired fields found")
                                    return filtered_data
                        except json.JSONDecodeError:
                            continue
            
            # If no direct patterns found, look for any large JSON structures
            script_text = ' '.join(script.string or '' for script in scripts)
            
            # Try to find any JSON object that contains product-related keywords
            json_pattern = r'{[^{}]*(?:{[^{}]*}[^{}]*)*}'
            potential_jsons = re.findall(json_pattern, script_text)
            
            for json_candidate in potential_jsons:
                if len(json_candidate) > 100:  # Only consider substantial JSON objects
                    try:
                        data = json.loads(json_candidate)
                        if isinstance(data, dict):
                            # Check if it contains product-related data
                            data_str = json.dumps(data).lower()
                            if any(keyword in data_str for keyword in ['product', 'sku', 'price', 'name']):
                                logger.info("Found potential product data")
                                
                                # Filter data to only include desired fields
                                filtered_data = {}
                                for field in desired_fields:
                                    if field in data:
                                        filtered_data[field] = data[field]
                                
                                if filtered_data:  # Only return if we found some desired fields
                                    # Add metadata for tracking
                                    filtered_data['_metadata'] = {
                                        'extraction_timestamp': time.time(),
                                        'fields_extracted': len(filtered_data) - 1,
                                        'total_fields_available': len(data)
                                    }
                                    
                                    logger.info(f"Filtered data: {len(filtered_data)-1}/{len(desired_fields)} desired fields found")
                                    return filtered_data
                    except json.JSONDecodeError:
                        continue
                        
        except Exception as e:
            logger.error(f"Error extracting react_data: {e}")
        
        return None
    
    def fetch_product_data(self, domain: str, product_id: str) -> Tuple[bool, Optional[dict]]:
        """Fetch product data with retries for 403 errors"""
        url = f"https://{domain}/catalog/product/view/id/{product_id}"
        
        # Rotate user agents
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.59'
        ]
        
        for attempt in range(5):  # Retry up to 5 times
            try:
                # Use a different session for each attempt
                session = requests.Session()
                
                # Rotate user agent
                ua = user_agents[attempt % len(user_agents)]
                
                session.headers.update({
                    'User-Agent': ua,
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Cache-Control': 'max-age=0'
                })
                
                # Add referrer for non-first attempts
                if attempt > 0:
                    session.headers['Referer'] = f"https://{domain}/"
                
                logger.info(f"Fetching {url} (attempt {attempt + 1}/5) with UA: {ua[:50]}...")
                
                # Add random delay between attempts
                if attempt > 0:
                    delay = (2 ** attempt) + (attempt * 2)  # Progressive delay
                    logger.info(f"Waiting {delay} seconds before retry...")
                    time.sleep(delay)
                
                # Use a reasonable timeout
                response = session.get(url, timeout=20, allow_redirects=True)
                
                logger.info(f"Response: {response.status_code} for {url}")
                
                if response.status_code == 200:
                    logger.info(f"Successfully fetched {url}")
                    
                    # Wait 3 seconds for page to load
                    time.sleep(3)
                    
                    react_data = self.extract_react_data(response.text)
                    if react_data:
                        logger.info(f"Found react_data for {url}")
                        return True, react_data
                    else:
                        logger.warning(f"No react_data found for {url}")
                        # Still save the page content for debugging if needed
                        return True, {
                            "url": url,
                            "domain": domain,
                            "product_id": product_id,
                            "status": "no_react_data",
                            "page_title": self.extract_page_title(response.text),
                            "page_size": len(response.text),
                            "timestamp": time.time()
                        }
                
                elif response.status_code == 403:
                    logger.warning(f"Got 403 for {url}, attempt {attempt + 1}/5")
                    # Don't give up immediately on 403, continue with next attempt
                    continue
                
                elif response.status_code == 404:
                    logger.warning(f"Product not found (404) for {url}")
                    return True, {
                        "url": url,
                        "domain": domain,
                        "product_id": product_id,
                        "status": "not_found",
                        "timestamp": time.time()
                    }
                
                elif response.status_code in [429, 503]:  # Rate limited or service unavailable
                    logger.warning(f"Rate limited ({response.status_code}) for {url}")
                    if attempt < 4:
                        delay = (2 ** attempt) * 5  # Longer delay for rate limiting
                        logger.info(f"Rate limited, waiting {delay} seconds...")
                        time.sleep(delay)
                    continue
                
                else:
                    logger.error(f"HTTP {response.status_code} for {url}")
                    if attempt < 4:
                        time.sleep(3)
                    continue
                    
            except requests.exceptions.Timeout:
                logger.warning(f"Timeout for {url}, attempt {attempt + 1}/5")
                if attempt < 4:
                    time.sleep(5)
                continue
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Request error for {url}: {e}")
                if attempt < 4:
                    time.sleep(3)
                continue
        
        logger.error(f"Failed to fetch {url} after 5 attempts")
        return False, {
            "url": url,
            "domain": domain,
            "product_id": product_id,
            "status": "failed_all_attempts",
            "timestamp": time.time()
        }
    
    def extract_page_title(self, html_content: str) -> str:
        """Extract page title for debugging purposes"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            title = soup.find('title')
            return title.text.strip() if title else "No title"
        except:
            return "Error extracting title"
    
    def save_product_data(self, domain: str, product_id: str, data: dict):
        """Save product data to JSON file"""
        filename = f"{domain}_{product_id}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved data to {filepath}")
        except Exception as e:
            logger.error(f"Error saving {filepath}: {e}")
            raise
    
    def process_product(self, domain: str, product_id: str) -> bool:
        """Process a single domain-product combination"""
        try:
            # Check if already processed
            if self.is_processed(domain, product_id):
                logger.info(f"Skipping {domain}/{product_id} - already processed")
                return True
            
            # Fetch data
            success, data = self.fetch_product_data(domain, product_id)
            
            if success and data:
                # Save data
                self.save_product_data(domain, product_id, data)
                
                # Save checkpoint
                self.save_checkpoint(domain, product_id, 'success')
                logger.info(f"Successfully processed {domain}/{product_id}")
                return True
            else:
                # Save failed checkpoint
                self.save_checkpoint(domain, product_id, 'failed')
                logger.error(f"Failed to process {domain}/{product_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error processing {domain}/{product_id}: {e}")
            self.save_checkpoint(domain, product_id, 'error')
            return False
    
    def run_scraping(self, max_workers: int = 3):
        """Run the scraping process with concurrent workers"""
        tasks = []
        
        # Create all domain-product combinations
        for _, domain_row in self.domains_df.iterrows():
            domain = domain_row['domains']
            for _, product_row in self.products_df.iterrows():
                product_id = str(product_row['pid'])
                tasks.append((domain, product_id))
        
        logger.info(f"Starting scraping with {max_workers} workers for {len(tasks)} tasks")
        
        completed = 0
        failed = 0
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_task = {
                executor.submit(self.process_product, domain, product_id): (domain, product_id)
                for domain, product_id in tasks
            }
            
            # Process completed tasks
            for future in as_completed(future_to_task):
                domain, product_id = future_to_task[future]
                try:
                    success = future.result()
                    if success:
                        completed += 1
                    else:
                        failed += 1
                except Exception as e:
                    logger.error(f"Task {domain}/{product_id} generated an exception: {e}")
                    failed += 1
                
                if (completed + failed) % 100 == 0:
                    logger.info(f"Progress: {completed} completed, {failed} failed, {len(tasks) - completed - failed} remaining")
        
        logger.info(f"Scraping completed: {completed} successful, {failed} failed")
        
        # Show final statistics
        stats, total = self.get_checkpoint_stats()
        logger.info(f"Final checkpoint stats: {stats}")
        
        # Clear checkpoint database if scraping is fully completed
        if total > 0:
            logger.info("Clearing checkpoint database...")
            self.clear_checkpoint_database()
            logger.info("Checkpoint database cleared. Ready for next run.")
        
        return completed, failed

def main():
    # Configuration
    domains_file = "data/input_data/domains_cleaned.csv"
    products_file = "data/input_data/node1.csv"
    output_dir = "data/scraped/output"
    max_workers = 3
    
    # Initialize scraper
    scraper = GlamiraScraper(domains_file, products_file, output_dir)
    
    # Run scraping
    completed, failed = scraper.run_scraping(max_workers)
    
    print(f"\nScraping Summary:")
    print(f"Completed: {completed}")
    print(f"Failed: {failed}")
    print(f"Total: {completed + failed}")

if __name__ == "__main__":
    main()