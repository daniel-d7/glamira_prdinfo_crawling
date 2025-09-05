"""
Starter script to begin the Glamira product scraping process.
This will start with a small subset and gradually scale up.
"""

from main import GlamiraScraper
import pandas as pd
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/glamira_scraping.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def start_scraping_batch(batch_size=50):
    """Start scraping with a small batch first"""
    
    # Configuration
    domains_file = "data/input_data/domains_cleaned.csv"
    products_file = "data/input_data/node1.csv"
    output_dir = "data/scraped/output"
    max_workers = 3
    
    try:
        # Initialize scraper
        scraper = GlamiraScraper(domains_file, products_file, output_dir)
        
        # Load data to check sizes
        domains_count = len(scraper.domains_df)
        products_count = len(scraper.products_df)
        total_combinations = domains_count * products_count
        
        logger.info(f"Total combinations to process: {total_combinations}")
        logger.info(f"Starting with first {batch_size} combinations")
        
        # Create limited datasets for initial run
        if batch_size < total_combinations:
            # Take first few domains and products for testing
            test_domains = min(5, domains_count)  # Max 5 domains
            test_products = min(batch_size // test_domains, products_count)  # Distribute products
            
            logger.info(f"Using {test_domains} domains and {test_products} products for initial batch")
            
            # Backup original data
            original_domains = scraper.domains_df.copy()
            original_products = scraper.products_df.copy()
            
            # Limit for testing
            scraper.domains_df = scraper.domains_df.head(test_domains)
            scraper.products_df = scraper.products_df.head(test_products)
        
        # Run scraping
        completed, failed = scraper.run_scraping(max_workers)
        
        logger.info(f"\nBatch Summary:")
        logger.info(f"Completed: {completed}")
        logger.info(f"Failed: {failed}")
        logger.info(f"Success rate: {completed/(completed+failed)*100:.1f}%" if (completed+failed) > 0 else "No attempts")
        
        # If successful and we want to continue with more
        if completed > 0 and batch_size < total_combinations:
            logger.info("\nFirst batch completed successfully!")
            logger.info("You can now run the full scraper with main.py or increase batch_size")
        
        return completed, failed
        
    except Exception as e:
        logger.error(f"Error in scraping: {e}")
        return 0, 0

def main():
    """Main entry point"""
    print("=== Glamira Product Data Scraper ===")
    print("Starting with a small batch to test the setup...")
    
    # Start with a small batch
    completed, failed = start_scraping_batch(batch_size=20)
    
    if completed > 0:
        print(f"\n✅ Successfully scraped {completed} products!")
        print("📁 Check the 'data/scraped/output/' folder for JSON files")
        print("📊 Check 'checkpoint.db' for progress tracking")
        print("📋 Check 'logs/glamira_scraping.log' for detailed logs")
        print("\nTo run the full scraper for all products, run: python scripts/run_full_scraping.py")
        print("To clear checkpoint database manually, run: python scripts/checkpoint_manager.py")
    else:
        print(f"\n❌ No products were successfully scraped.")
        print("This might be due to:")
        print("- Anti-bot protection (403 errors)")
        print("- Network issues")
        print("- Invalid product IDs")
        print("📋 Check 'logs/glamira_scraping.log' for detailed error information")

if __name__ == "__main__":
    main()
