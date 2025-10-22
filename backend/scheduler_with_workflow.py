# scheduler_with_workflow.py
import schedule
import time
from datetime import datetime
from scraper import main as run_scraper
from pdf_downloader import process_announcements_pdfs
from workflow_processor import WorkflowProcessor
from rate_limited_llm import groq_client
import os
import json
from dotenv import load_dotenv

def complete_pipeline():
    """Run complete pipeline: Scrape → Download PDFs → Process with LLM"""
    
    print("\n" + "="*80)
    print(f"⏰ Complete Pipeline Run at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80 + "\n")
    
    try:
        # Step 1: Scrape new announcements
        print("📊 STEP 1: Scraping BSE for new announcements...")
        print("-"*80)
        run_scraper()
        print()
        
        # Step 2: Download PDFs for new announcements
        print("📥 STEP 2: Downloading PDFs...")
        print("-"*80)
        process_announcements_pdfs(limit=10)  # Download up to 10 PDFs
        print()
        
        # Step 3: Process announcements with LLM workflows
        print("🤖 STEP 3: Processing with LLM workflows...")
        print("-"*80)
        process_with_llm(limit=5)  # Process up to 5 announcements
        print()
        
        print("="*80)
        print("✅ Complete pipeline finished successfully!")
        print("="*80)
        
    except Exception as e:
        print(f"✗ Pipeline error: {e}")
        import traceback
        traceback.print_exc()

def process_with_llm(limit=5):
    """Process unprocessed announcements with LLM"""
    from database import get_db
    
    # Get unprocessed announcements
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, stock_code, title
        FROM announcements
        WHERE processed = FALSE 
        AND pdf_downloaded = TRUE
        ORDER BY announcement_date DESC
        LIMIT %s
    """, (limit,))
    
    announcements = cursor.fetchall()
    cursor.close()
    conn.close()
    
    if not announcements:
        print("  ✓ No unprocessed announcements found")
        return
    
    print(f"  Found {len(announcements)} unprocessed announcements\n")
    
    # Process each
    processor = WorkflowProcessor()
    success_count = 0
    
    for ann in announcements:
        print(f"  Processing: {ann['stock_code']} - {ann['title'][:50]}...")
        
        try:
            if processor.process_announcement(ann['id']):
                success_count += 1
                print(f"  ✓ Success\n")
            else:
                print(f"  ✗ Failed\n")
        except Exception as e:
            print(f"  ✗ Error: {e}\n")
    
    print(f"  Summary: {success_count}/{len(announcements)} processed successfully")

if __name__ == "__main__":
    print("📅 Complete Pipeline Scheduler Started")
    print("Running every 5 minutes (change as needed)")
    print("Press Ctrl+C to stop\n")
    
    # Run immediately on start
    complete_pipeline()
    
    # Schedule to run every 5 minutes
    schedule.every(1).minutes.do(complete_pipeline)
    
    # Keep running
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n⏹ Scheduler stopped by user")