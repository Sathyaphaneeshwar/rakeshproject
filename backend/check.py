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
    SELECT id, title, processed, llm_summary
    FROM announcements 
    WHERE id = 999;
""")

result = cursor.fetchone()

if result:
    print(f"✓ Found announcement {result[0]}")
    print(f"  Title: {result[1]}")
    print(f"  Processed: {result[2]}")
    print(f"  Summary: {result[3][:200]}..." if result[3] else "  Summary: None")
else:
    print("✗ No announcement found")