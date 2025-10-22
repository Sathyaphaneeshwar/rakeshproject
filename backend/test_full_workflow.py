# test_full_workflow.py
from database import get_db
from workflow_processor import WorkflowProcessor

def find_test_announcement():
    """Find an unprocessed announcement with PDF"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, stock_code, title, pdf_downloaded
        FROM announcements
        WHERE processed = FALSE 
        AND pdf_downloaded = TRUE
        LIMIT 1
    """)
    
    ann = cursor.fetchone()
    cursor.close()
    conn.close()
    
    return ann

if __name__ == "__main__":
    print("🧪 Testing Complete Workflow\n")
    
    # Find a test announcement
    ann = find_test_announcement()
    
    if not ann:
        print("❌ No unprocessed announcements with PDFs found")
        print("Run pdf_downloader.py first to download some PDFs")
    else:
        print(f"Found announcement: {ann['title'][:60]}...")
        print(f"ID: {ann['id']}\n")
        
        # Process it
        processor = WorkflowProcessor()
        success = processor.process_announcement(ann['id'])
        
        if success:
            print("\n✅ Workflow completed successfully!")
        else:
            print("\n❌ Workflow failed")