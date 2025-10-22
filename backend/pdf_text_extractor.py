# backend/pdf_text_extractor.py
import PyPDF2
import io
from database import get_db

def extract_text_from_pdf_binary(pdf_binary):
    """Extract text from PDF binary content"""
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_binary))
        
        text = ""
        for page in pdf_reader.pages:
            try:
                text += page.extract_text() + "\n"
            except:
                continue
        
        return text.strip()
        
    except Exception as e:
        print(f"    ✗ PDF extraction error: {e}")
        return None

def get_pdf_text_for_announcement(announcement_id):
    """Get PDF text for a specific announcement"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT pdf_content 
        FROM announcements 
        WHERE id = %s AND pdf_content IS NOT NULL
    """, (announcement_id,))
    
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if not result or not result['pdf_content']:
        return None
    
    # Extract text from binary PDF
    return extract_text_from_pdf_binary(bytes(result['pdf_content']))

def test_extraction():
    """Test PDF text extraction on first announcement with PDF"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, stock_code, title 
        FROM announcements 
        WHERE pdf_content IS NOT NULL 
        LIMIT 1
    """)
    
    ann = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if ann:
        print(f"Testing extraction on: {ann['title'][:50]}...\n")
        text = get_pdf_text_for_announcement(ann['id'])
        
        if text:
            print(f"✓ Extracted {len(text)} characters")
            print(f"\nFirst 500 characters:\n{text[:500]}")
        else:
            print("✗ Failed to extract text")
    else:
        print("No announcements with PDFs found")

if __name__ == "__main__":
    test_extraction()