import psycopg2

DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'stock_announcements',
    'user': 'stocks',
    'password': 'admin123'
}

def add_column():
    """Add submission_time column to announcements table"""
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # Add submission_time column
        cursor.execute("""
            ALTER TABLE announcements 
            ADD COLUMN IF NOT EXISTS submission_time TIMESTAMP
        """)
        
        conn.commit()
        print("✓ Added submission_time column")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        conn.rollback()
        
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    add_column()