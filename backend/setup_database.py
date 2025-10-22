import psycopg2

# Database connection details
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'n8n',
    'user': 'n8n',
    'password': 'n8n'
}

def create_tables():
    """Create necessary tables"""
    
    conn = None
    try:
        print("Connecting to database...")
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # 1. Create stocks table
        print("\nCreating 'stocks' table...")
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
            );
        """)
        
        # 2. Create announcements table
        print("Creating 'announcements' table...")
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
            );
        """)
        
        conn.commit()
        print("✓ Tables created successfully!")
        
        # 3. Create indexes
        print("\nCreating indexes...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_stock_code ON announcements(stock_code);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_announcement_date ON announcements(announcement_date);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_unique_hash ON announcements(unique_hash);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_processed ON announcements(processed);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sector ON stocks(sector);")  # NEW
        
        
        conn.commit()
        print("✓ Indexes created successfully!")
        
        cursor.close()
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn:
            conn.close()
            print("\nDatabase connection closed.")

if __name__ == "__main__":
    create_tables()