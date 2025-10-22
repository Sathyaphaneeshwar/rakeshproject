import psycopg2

conn = psycopg2.connect(
    host='localhost',
    port=5432,
    database='n8n',
    user='n8n',
    password='n8n'
)

cursor = conn.cursor()

cursor.execute("""
    INSERT INTO announcements (id, stock_code, title, description, category, pdf_link, announcement_date, announcement_time, unique_hash)
    VALUES (999, '544172', 'Test Announcement', 'This is a test', 'Company Update', 
            'https://www.bseindia.com/xml-data/corpfiling/AttachLive/b90d791a-3a85-413c-8f62-4c57bdfb3c65.pdf',
            '2025-10-11', '15:30:00', 'test-hash-999')
    ON CONFLICT (id) DO NOTHING;
""")

conn.commit()
print("✓ Test row inserted!")