import schedule
import time
from datetime import datetime
from scraper_parallel import main as run_scraper

def job():
    """Job to run every minute"""
    print("\n" + "="*80)
    print(f"⏰ Scheduled run at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80 + "\n")
    
    try:
        run_scraper()
    except Exception as e:
        print(f"✗ Scraper error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("📅 Scheduler started - Running every 1 minute")
    print("Press Ctrl+C to stop\n")
    
    # Run immediately on start
    job()
    
    # Schedule to run every minute
    schedule.every(1).minutes.do(job)
    
    # Keep running
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n⏹ Scheduler stopped by user")