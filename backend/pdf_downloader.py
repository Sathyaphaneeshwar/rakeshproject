
import requests
import psycopg2
from psycopg2.extras import RealDictCursor
from config import DB_CONFIG

def get_db():
    """Get database connection"""
    return psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)

def download_pdf(pdf_url):
    """Download PDF from URL and return binary content"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'application/pdf,*/*',
            'Referer': 'https://www.bseindia.com/'
        }
        
        response = requests.get(pdf_url, headers=headers, timeout=30)
        response.raise_for_status()
        
        return response.content
        
    except Exception as e:
        print(f"    ✗ Download error: {e}")
        return None

def save_pdf_to_db(announcement_id, pdf_content):
    """Save PDF binary content to database"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE announcements 
            SET pdf_content = %s,
                pdf_downloaded = TRUE
            WHERE id = %s
        """, (psycopg2.Binary(pdf_content), announcement_id))
        
        conn.commit()
        return True
        
    except Exception as e:
        print(f"    ✗ DB save error: {e}")
        conn.rollback()
        return False
        
    finally:
        cursor.close()
        conn.close()

def process_announcements_pdfs(limit=10):
    """Download PDFs for announcements that don't have them yet"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Get announcements with PDF links but no downloaded PDF
    cursor.execute("""
        SELECT id, stock_code, title, pdf_link
        FROM announcements
        WHERE pdf_link IS NOT NULL 
        AND pdf_downloaded = FALSE
        LIMIT %s
    """, (limit,))
    
    announcements = cursor.fetchall()
    cursor.close()
    conn.close()
    
    if not announcements:
        print("✓ No announcements need PDF download")
        return
    
    print(f"📥 Downloading PDFs for {len(announcements)} announcements...\n")
    
    success_count = 0
    for ann in announcements:
        print(f"📄 {ann['stock_code']} - {ann['title'][:50]}...")
        
        # Download PDF
        pdf_content = download_pdf(ann['pdf_link'])
        
        if pdf_content:
            print(f"    ✓ Downloaded {len(pdf_content)} bytes")
            
            # Save to database
            if save_pdf_to_db(ann['id'], pdf_content):
                print(f"    ✓ Saved to database")
                success_count += 1
        
        print()
    
    print(f"✅ Downloaded and saved {success_count}/{len(announcements)} PDFs")

if __name__ == "__main__":
    process_announcements_pdfs(limit=5)  # Start with just 5 to test