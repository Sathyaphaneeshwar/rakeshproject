import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port=5432,
    database='n8n',
    user='n8n',
    password='n8n'
)

cursor = conn.cursor()

# Delete recent announcements from one stock using a subquery
cursor.execute("""
    DELETE FROM announcements 
    WHERE id IN (
        SELECT id FROM announcements
        WHERE stock_code = '544172' 
        AND announcement_date >= '2025-10-01'
        LIMIT 5
    );
""")

deleted = cursor.rowcount
conn.commit()

print(f"✓ Deleted {deleted} announcements - they'll be re-scraped as 'new'")

cursor.close()
conn.close()