import requests
import json

FIRECRAWL_URL = "http://localhost:3002"
bse_url = "https://www.bseindia.com/stock-share-price/indegene-ltd/INDGN/544172/corp-announcements/"

payload = {
    "url": bse_url,
    "formats": ["markdown", "html"],
    "waitFor": 5000,
    "timeout": 90000,
    "onlyMainContent": True,
    # Add this to extract only specific elements
    "includeTags": ["table", "a"]  # Only get tables and links
}

print("Scraping BSE announcements table...")
response = requests.post(f"{FIRECRAWL_URL}/v1/scrape", json=payload, timeout=120)

if response.status_code == 200:
    data = response.json()
    
    # Save the response
    with open('bse_announcements.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Data saved to bse_announcements.json")
    
    # Check what we got
    html = data.get('data', {}).get('html', '')
    
    # Find PDF links
    if '.pdf' in html.lower():
        print("✓ PDF links found!")
        # Count PDFs
        pdf_count = html.lower().count('.pdf')
        print(f"  Found approximately {pdf_count} PDF references")
    else:
        print("⚠ No PDF links found")
        
else:
    print(f"Error {response.status_code}: {response.json()}")