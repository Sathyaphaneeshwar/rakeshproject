import psycopg2

DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'n8n',
    'user': 'n8n',
    'password': 'n8n'
}

def add_sector_columns():
    """Add sector and sub_sector columns to stocks table"""
    conn = None
    try:
        print("Connecting to database...")
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Add sector column if it doesn't exist
        print("Adding sector column...")
        cursor.execute("""
            ALTER TABLE stocks 
            ADD COLUMN IF NOT EXISTS sector VARCHAR(50);
        """)
        
        # Add sub_sector column if it doesn't exist
        print("Adding sub_sector column...")
        cursor.execute("""
            ALTER TABLE stocks 
            ADD COLUMN IF NOT EXISTS sub_sector VARCHAR(100);
        """)
        
        conn.commit()
        print("✓ Columns added successfully!")
        
        # Create index on sector
        print("Creating index on sector...")
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_sector ON stocks(sector);
        """)
        
        conn.commit()
        print("✓ Index created successfully!")
        
        cursor.close()
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn:
            conn.close()
            print("\nDatabase connection closed.")

if __name__ == "__main__":
    add_sector_columns()