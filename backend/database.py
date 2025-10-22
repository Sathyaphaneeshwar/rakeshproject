# backend/database.py
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

# Database config - using new independent database
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'stock_announcements',
    'user': 'stocks',
    'password': 'admin123'
}

def get_db():
    """Get database connection"""
    return psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)

def get_unprocessed_announcements(limit=10):
    """Get announcements that haven't been processed by LLM yet"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT id, stock_code, title, description, category, 
                   pdf_link, announcement_date, announcement_time
            FROM announcements 
            WHERE processed = FALSE 
            AND pdf_link IS NOT NULL
            ORDER BY announcement_date DESC
            LIMIT %s
        """, (limit,))
        
        announcements = cursor.fetchall()
        print(f"📋 Found {len(announcements)} unprocessed announcements")
        return announcements
        
    finally:
        cursor.close()
        conn.close()

def update_announcement_with_llm(announcement_id, llm_summary, processed=True):
    """Update announcement with LLM summary"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE announcements 
            SET llm_summary = %s, 
                processed = %s,
                created_at = %s
            WHERE id = %s
            RETURNING id
        """, (llm_summary, processed, datetime.now(), announcement_id))
        
        updated = cursor.fetchone()
        conn.commit()
        
        if updated:
            print(f"  ✓ Updated announcement ID {announcement_id}")
            return True
        else:
            print(f"  ✗ Announcement ID {announcement_id} not found")
            return False
        
    except Exception as e:
        print(f"  ✗ Database error: {e}")
        conn.rollback()
        return False
        
    finally:
        cursor.close()
        conn.close()

def get_active_stocks():
    """Get all active stocks from database"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT stock_code, stock_name, bse_url FROM stocks WHERE is_active = TRUE")
        stocks = cursor.fetchall()
        return stocks
    finally:
        cursor.close()
        conn.close()

def test_connection():
    """Test database connection"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        print("✓ Database connection successful")
        return True
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False
    
if __name__ == "__main__":
    print("Testing database connection...\n")
    test_connection()

    # Check table status
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) as count FROM stocks")
    stock_count = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM announcements")
    announcement_count = cursor.fetchone()['count']
    
    print(f"📊 Stocks: {stock_count}")
    print(f"📢 Announcements: {announcement_count}")
    
    cursor.close()
    conn.close()