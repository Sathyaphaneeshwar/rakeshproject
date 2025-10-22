import psycopg2
from psycopg2.extras import RealDictCursor

DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'n8n',
    'user': 'n8n',
    'password': 'n8n'
}

def check_database():
    """Check database contents"""
    conn = psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)
    cursor = conn.cursor()
    
    print("="*60)
    print("DATABASE INSPECTION")
    print("="*60)
    
    # List all tables
    print("\n📊 TABLES:")
    cursor.execute("""
        SELECT tablename 
        FROM pg_tables 
        WHERE schemaname = 'public'
    """)
    tables = cursor.fetchall()
    for table in tables:
        print(f"  - {table['tablename']}")
    
    # Check stocks table
    print("\n📈 STOCKS TABLE:")
    cursor.execute("SELECT COUNT(*) as count FROM stocks")
    print(f"  Total stocks: {cursor.fetchone()['count']}")
    
    cursor.execute("SELECT COUNT(*) as count FROM stocks WHERE is_active = TRUE")
    print(f"  Active stocks: {cursor.fetchone()['count']}")
    
    cursor.execute("SELECT * FROM stocks LIMIT 3")
    print("\n  Sample stocks:")
    for stock in cursor.fetchall():
        print(f"    {stock}")
    
    # Check announcements table
    print("\n📢 ANNOUNCEMENTS TABLE:")
    cursor.execute("SELECT COUNT(*) as count FROM announcements")
    print(f"  Total announcements: {cursor.fetchone()['count']}")
    
    cursor.execute("SELECT COUNT(*) as count FROM announcements WHERE processed = TRUE")
    processed = cursor.fetchone()['count']
    cursor.execute("SELECT COUNT(*) as count FROM announcements WHERE processed = FALSE")
    unprocessed = cursor.fetchone()['count']
    print(f"  Processed: {processed}")
    print(f"  Unprocessed: {unprocessed}")