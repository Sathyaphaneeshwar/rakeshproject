import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

FIRECRAWL_URL = "http://localhost:3002"
BSE_URL = "https://www.bseindia.com/stock-share-price/reliance-industries-ltd/RELIANCE/500325/corp-announcements/"

payload = {
    "url": BSE_URL,
    "formats": ["html"],
    "waitFor": 5000,
    "timeout": 90000,
    "onlyMainContent": True
}

response = requests.post(f"{FIRECRAWL_URL}/v1/scrape", json=payload, timeout=120)

if response.status_code == 200:
    data = response.json()
    html_content = data.get('data', {}).get('html', '')
    
    soup = BeautifulSoup(html_content, 'html.parser')
    tables = soup.find_all('table', {'ng-repeat': 'cann in CorpannData.Table'})
    
    if tables:
        first = tables[0]
        
        print("Looking for submission time in all TDs:\n")
        found = False
        for i, td in enumerate(first.find_all('td')):
            td_text = td.get_text(strip=True)
            if 'Exchange' in td_text or 'Received' in td_text:
                print(f"\nTD #{i}:")
                print(f"Text: {td_text}")
                print(f"Has 'Exchange Received Time': {'Exchange Received Time' in td_text}")
                
                # Try extraction
                submission_match = re.search(r'Exchange Received Time\s*(\d{2}-\d{2}-\d{4}\s+\d{2}:\d{2}:\d{2})', td_text)
                if submission_match:
                    print(f"✓ MATCH FOUND: {submission_match.group(1)}")
                    found = True
                else:
                    print("✗ No match with current regex")
                    
        if not found:
            print("\n" + "="*80)
            print("Could not find submission time. Full table text:")
            print("="*80)
            print(first.get_text())