# backend/migrate_stocks.py
import psycopg2

# Old database (n8n)
OLD_DB = {
    'host': 'localhost',
    'port': 5432,
    'database': 'n8n',
    'user': 'n8n',
    'password': 'n8n'
}

# New database
NEW_DB = {
    'host': 'localhost',
    'port': 5432,
    'database': 'stock_announcements',
    'user': 'stocks',
    'password': 'admin123'
}

def migrate_stocks():
    """Copy stocks from old database to new database"""
    
    # Connect to old database
    old_conn = psycopg2.connect(**OLD_DB)
    old_cursor = old_conn.cursor()
    
    # Connect to new database
    new_conn = psycopg2.connect(**NEW_DB)
    new_cursor = new_conn.cursor()
    
    try:
        # Get all stocks from old database
        old_cursor.execute("""
            SELECT stock_code, stock_name, bse_url, sector, sub_sector, is_active
            FROM stocks
        """)
        stocks = old_cursor.fetchall()
        
        print(f"📊 Found {len(stocks)} stocks in old database")
        
        # Insert into new database
        count = 0
        for stock in stocks:
            try:
                new_cursor.execute("""
                    INSERT INTO stocks (stock_code, stock_name, bse_url, sector, sub_sector, is_active)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (stock_code) DO NOTHING
                """, stock)
                count += 1
            except Exception as e:
                print(f"  ✗ Error with {stock[0]}: {e}")
        
        new_conn.commit()
        print(f"✅ Migrated {count} stocks to new database")
        
        # Verify
        new_cursor.execute("SELECT COUNT(*) FROM stocks")
        new_count = new_cursor.fetchone()[0]
        print(f"📊 New database now has {new_count} stocks")
        
    except Exception as e:
        print(f"✗ Migration error: {e}")
        new_conn.rollback()
        
    finally:
        old_cursor.close()
        old_conn.close()
        new_cursor.close()
        new_conn.close()

if __name__ == "__main__":
    migrate_stocks()