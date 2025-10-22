# backend/setup_new_database.py
import psycopg2

# New database config
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'stock_announcements',
    'user': 'stocks',
    'password': 'admin123'
}

def create_tables():
    """Create all necessary tables"""
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        print("🔧 Setting up database...\n")
        
        # Create stocks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stocks (
                id SERIAL PRIMARY KEY,
                stock_code VARCHAR(20) UNIQUE NOT NULL,
                stock_name VARCHAR(100),
                bse_url TEXT,
                sector VARCHAR(50),
                sub_sector VARCHAR(100),
                is_active BOOLEAN DEFAULT TRUE,
                last_scraped_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✓ Created stocks table")
        
        # Create announcements table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS announcements (
                id SERIAL PRIMARY KEY,
                stock_code VARCHAR(20) NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                category VARCHAR(100),
                pdf_link TEXT,
                announcement_date DATE,
                announcement_time TIME,
                announcement_datetime TIMESTAMP,
                unique_hash VARCHAR(64) UNIQUE NOT NULL,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                processed BOOLEAN DEFAULT FALSE,
                llm_summary TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (stock_code) REFERENCES stocks(stock_code)
            )
        """)
        print("✓ Created announcements table")
        
        # Create indexes for better performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_stock_code ON announcements(stock_code)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_processed ON announcements(processed)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_announcement_date ON announcements(announcement_date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sector ON stocks(sector)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_unique_hash ON announcements(unique_hash)")
        print("✓ Created indexes")
        
        conn.commit()
        
        # Show table counts
        cursor.execute("SELECT COUNT(*) FROM stocks")
        stock_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM announcements")
        announcement_count = cursor.fetchone()[0]
        
        print(f"\n📊 Database Status:")
        print(f"   Stocks: {stock_count}")
        print(f"   Announcements: {announcement_count}")
        print("\n✅ Database setup complete!")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        conn.rollback()
        
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    create_tables()