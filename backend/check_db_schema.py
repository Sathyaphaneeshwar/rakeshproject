from database import get_db

conn = get_db()
cursor = conn.cursor()

cursor.execute("""
    SELECT column_name, data_type, character_maximum_length
    FROM information_schema.columns
    WHERE table_name = 'announcements'
    ORDER BY ordinal_position
""")

print("📋 Announcements Table Schema:\n")
print(f"{'Column Name':<30} {'Type':<20} {'Max Length':<15}")
print("="*70)

for row in cursor.fetchall():
    col_name = row['column_name']
    data_type = row['data_type']
    max_length = row['character_maximum_length'] or '-'
    print(f"{col_name:<30} {data_type:<20} {max_length:<15}")

cursor.close()
conn.close()