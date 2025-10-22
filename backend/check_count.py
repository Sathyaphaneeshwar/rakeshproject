from database import get_db

conn = get_db()
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) as count FROM announcements WHERE stock_code = '500325'")
count = cursor.fetchone()['count']

print(f'Announcements for stock 500325: {count}')

if count > 0:
    cursor.execute("SELECT id, title, submission_time FROM announcements WHERE stock_code = '500325' ORDER BY id DESC LIMIT 3")
    print('\nLatest 3:')
    for row in cursor.fetchall():
        print(f"  ID: {row['id']}, Title: {row['title'][:50]}, Submission: {row['submission_time']}")

cursor.close()
conn.close()