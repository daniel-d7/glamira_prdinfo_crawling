"""
Full-scale Glamira product scraping script
This will process all 553,000 domain-product combinations
"""

from main import GlamiraScraper
import logging
import time
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/glamira_full_scraping.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def run_full_scraping():
    """Run the full-scale scraping operation"""
    
    print("=" * 60)
    print("🚀 GLAMIRA FULL-SCALE PRODUCT SCRAPER")
    print("=" * 60)
    print()
    
    # Configuration
    domains_file = "data/input_data/domains_cleaned.csv"
    products_file = "data/input_data/node1.csv"
    output_dir = "data/scraped/output"
    max_workers = 3
    
    start_time = time.time()
    
    try:
        # Initialize scraper
        scraper = GlamiraScraper(domains_file, products_file, output_dir)
        
        # Show stats
        domains_count = len(scraper.domains_df)
        products_count = len(scraper.products_df)
        total_combinations = domains_count * products_count
        
        print(f"📊 SCOPE:")
        print(f"   Domains: {domains_count}")
        print(f"   Products: {products_count}")
        print(f"   Total combinations: {total_combinations:,}")
        print(f"   Workers: {max_workers}")
        print()
        
        # Estimate time
        # Based on test: ~3-5 seconds per product with retries
        estimated_seconds = total_combinations * 4  # Conservative estimate
        estimated_hours = estimated_seconds / 3600
        
        print(f"⏱️ ESTIMATED TIME:")
        print(f"   ~{estimated_hours:.1f} hours ({estimated_seconds/86400:.1f} days)")
        print()
        
        # Ask for confirmation
        response = input("Do you want to proceed with full scraping? (yes/no): ").lower()
        if response not in ['yes', 'y']:
            print("❌ Scraping cancelled.")
            return
        
        print(f"🏁 Starting full scraping at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("   You can monitor progress with: python monitor.py")
        print("   Press Ctrl+C to stop (progress will be saved)")
        print()
        
        # Run scraping
        completed, failed = scraper.run_scraping(max_workers)
        
        # Final stats
        end_time = time.time()
        duration = end_time - start_time
        duration_hours = duration / 3600
        
        print()
        print("=" * 60)
        print("🏆 FINAL RESULTS")
        print("=" * 60)
        print(f"✅ Completed: {completed:,}")
        print(f"❌ Failed: {failed:,}")
        print(f"📊 Total processed: {completed + failed:,}")
        print(f"🎯 Success rate: {completed/(completed+failed)*100:.1f}%" if (completed+failed) > 0 else "No attempts")
        print(f"⏱️ Duration: {duration_hours:.1f} hours")
        print(f"⚡ Rate: {(completed+failed)/duration_hours:.0f} products/hour" if duration_hours > 0 else "N/A")
        print()
        print("📁 Check 'data/scraped/output/' folder for JSON files")
        print("📊 Checkpoint database has been automatically cleared")
        print("📋 Check 'logs/glamira_full_scraping.log' for full logs")
        
        return completed, failed
        
    except KeyboardInterrupt:
        print("\n⏸️ Scraping interrupted by user")
        print("✅ Progress has been saved to checkpoint.db")
        print("🔄 You can resume by running this script again")
        return 0, 0
        
    except Exception as e:
        logger.error(f"Critical error in full scraping: {e}")
        print(f"\n❌ Critical error: {e}")
        return 0, 0

if __name__ == "__main__":
    run_full_scraping()
