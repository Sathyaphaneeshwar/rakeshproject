import concurrent.futures
import time
from scraper import scrape_stock, get_active_stocks

def main():
    """Scrape all active stocks in parallel"""
    print("🚀 Starting parallel scraper...\n")
    
    stocks = get_active_stocks()
    print(f"📋 Found {len(stocks)} active stocks to scrape\n")
    
    if not stocks:
        print("⚠ No active stocks found!")
        return
    
    start_time = time.time()
    
    # Scrape up to 5 stocks simultaneously
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        # Submit all scraping tasks
        futures = {
            executor.submit(scrape_stock, code, name, url): code 
            for code, name, url in stocks
        }
        
        # Wait for all to complete
        for future in concurrent.futures.as_completed(futures):
            stock_code = futures[future]
            try:
                future.result()
            except Exception as e:
                print(f"✗ Error scraping {stock_code}: {e}")
    
    elapsed = time.time() - start_time
    print(f"\n✅ Scraping completed in {elapsed:.2f} seconds!")
    print(f"⚡ Average: {elapsed/len(stocks):.2f}s per stock")

if __name__ == "__main__":
    main()