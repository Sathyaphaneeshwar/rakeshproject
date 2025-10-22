import psycopg2

DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'n8n',
    'user': 'n8n',
    'password': 'n8n'
}

def add_stock(stock_code, stock_name, sector, sub_sector=None):
    """Add a stock to monitor with sector information"""
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Create BSE URL
        bse_url = f"https://www.bseindia.com/stock-share-price/{stock_name.lower().replace(' ', '-')}/{stock_code.upper()}/{stock_code}/corp-announcements/"
        
        cursor.execute("""
            INSERT INTO stocks (stock_code, stock_name, bse_url, sector, sub_sector, is_active)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (stock_code) DO UPDATE 
            SET sector = EXCLUDED.sector, sub_sector = EXCLUDED.sub_sector;
        """, (stock_code, stock_name, bse_url, sector, sub_sector, True))
        
        conn.commit()
        print(f"✓ Added stock: {stock_code} - {stock_name} | Sector: {sector}")
        
        cursor.close()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn:
            conn.close()
if __name__ == "__main__":
    # Add stocks with sector information
    add_stock("544172", "indegene-ltd/INDGN", "Healthcare", "Pharma Services")