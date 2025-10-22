import psycopg2

DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'stock_announcements',
    'user': 'stocks',
    'password': 'admin123'
}

def add_transcript_columns():
    """Add transcript-related columns"""
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        # Transcript link detected by LLM
        cursor.execute("ALTER TABLE announcements ADD COLUMN IF NOT EXISTS transcript_link TEXT")
        
        # Diarized transcript (contains text + speakers) - this is all we need
        cursor.execute("ALTER TABLE announcements ADD COLUMN IF NOT EXISTS transcript_diarized JSONB")
        
        # Workflow type (transcription / simple_summary / etc)
        cursor.execute("ALTER TABLE announcements ADD COLUMN IF NOT EXISTS workflow_type VARCHAR(50)")
        
        conn.commit()
        print("✓ Added transcript_link column")
        print("✓ Added transcript_diarized column (JSONB)")
        print("✓ Added workflow_type column")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        conn.rollback()
        
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    add_transcript_columns()