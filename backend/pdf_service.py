from flask import Flask, request, jsonify
import PyPDF2
import io
import requests

app = Flask(__name__)

@app.route('/extract-pdf', methods=['POST'])
def extract_pdf():
    """Extract text from PDF - accepts either file upload or URL"""
    try:
        # DEBUG: Print what we received
        print("=" * 50)
        print("Request Content-Type:", request.content_type)
        print("Request JSON:", request.json)
        print("=" * 50)
        
        text = ""
        pages = 0
        
        # Check if PDF was uploaded directly
        if 'pdf' in request.files:
            pdf_file = request.files['pdf']
            pdf_content = pdf_file.read()
            
        # Or if PDF URL was provided
        elif request.json and 'pdf_url' in request.json:
            pdf_url = request.json['pdf_url']
            print(f"Downloading PDF from: {pdf_url}")
            
            # Download with proper headers
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                'Accept': 'application/pdf,*/*',
                'Referer': 'https://www.bseindia.com/'
            }
            
            response = requests.get(pdf_url, headers=headers, timeout=30, stream=True)
            response.raise_for_status()
            
            pdf_content = response.content
            print(f"Downloaded {len(pdf_content)} bytes")
            
            # Save for debugging (optional)
            with open('/tmp/test_pdf.pdf', 'wb') as f:
                f.write(pdf_content)
            print("Saved to /tmp/test_pdf.pdf for inspection")
            
        else:
            print("ERROR: No PDF provided!")
            return jsonify({'error': 'No PDF provided. Send JSON with pdf_url key.'}), 400
        
        # Try to read PDF
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_content))
        except Exception as pdf_error:
            print(f"PyPDF2 error: {pdf_error}")
            # Try alternative: pdfplumber (if installed)
            return jsonify({
                'error': f'PDF parsing failed: {str(pdf_error)}',
                'pdf_size': len(pdf_content),
                'success': False
            }), 500
        
        # Extract text from all pages
        for i, page in enumerate(pdf_reader.pages):
            try:
                page_text = page.extract_text()
                text += page_text + "\n"
                print(f"Page {i+1}: Extracted {len(page_text)} characters")
            except Exception as page_error:
                print(f"Error on page {i+1}: {page_error}")
                continue
        
        pages = len(pdf_reader.pages)
        
        return jsonify({
            'text': text.strip(),
            'pages': pages,
            'characters': len(text),
            'success': True
        })
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    print("📄 PDF Extraction Service starting on http://localhost:5001")
    app.run(host='0.0.0.0', port=5001, debug=True)