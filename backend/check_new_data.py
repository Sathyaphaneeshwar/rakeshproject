from database import get_db

conn = get_db()
cursor = conn.cursor()

cursor.execute("""
    SELECT title, description, submission_time 
    FROM announcements 
    WHERE stock_code = '500325' 
    ORDER BY id DESC 
    LIMIT 3
""")

print("Latest 3 announcements from Reliance (500325):\n")
for row in cursor.fetchall():
    print('Title:', row['title'][:60])
    print('Description:', row['description'][:200] if row['description'] else 'None')
    print('Submission Time:', row['submission_time'])
    print('='*80)

cursor.close()
conn.close()