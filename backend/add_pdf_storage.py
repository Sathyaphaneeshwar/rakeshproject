import psycopg2

DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'stock_announcements',
    'user': 'stocks',
    'password': 'admin123'
}

def add_pdf_column():
    """Add pdf_content column to store PDF files"""
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # Add pdf_content as BYTEA (binary data)
        cursor.execute("""
            ALTER TABLE announcements 
            ADD COLUMN IF NOT EXISTS pdf_content BYTEA
        """)
        
        # Add flag to track if PDF was downloaded
        cursor.execute("""
            ALTER TABLE announcements 
            ADD COLUMN IF NOT EXISTS pdf_downloaded BOOLEAN DEFAULT FALSE
        """)
        
        conn.commit()
        print("✓ Added pdf_content column (BYTEA)")
        print("✓ Added pdf_downloaded column (BOOLEAN)")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        conn.rollback()
        
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    add_pdf_column()