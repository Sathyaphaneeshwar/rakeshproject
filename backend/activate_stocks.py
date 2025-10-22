# activate_stocks.py
import psycopg2

DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'n8n',
    'user': 'n8n',
    'password': 'n8n'
}

def activate_stocks(stock_codes):
    """Activate specific stocks for scraping"""
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    for code in stock_codes:
        cursor.execute("UPDATE stocks SET is_active = TRUE WHERE stock_code = %s", (code,))
        print(f"✓ Activated: {code}")
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"\n✓ Activated {len(stock_codes)} stocks")

if __name__ == "__main__":
    # Activate a few stocks for testing
    test_stocks = [
        "544172",  # Indegene
        "500002",  # ABB India
        "500325",  # Reliance
        "500180",  # HDFC Bank
        "500209",  # Infosys
    ]
    
    activate_stocks(test_stocks)