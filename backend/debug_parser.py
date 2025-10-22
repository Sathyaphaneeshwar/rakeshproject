import requests
from bs4 import BeautifulSoup

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
        print("First announcement HTML:\n")
        first = tables[0]
        
        # Check for description spans
        print("="*80)
        print("HEADLINE span:")
        desc_short = first.find('span', {'ng-bind-html': 'cann.HEADLINE'})
        if desc_short:
            print(desc_short.get_text(strip=True))
        else:
            print("NOT FOUND")
            
        print("\n" + "="*80)
        print("MORE span:")
        desc_full = first.find('span', {'ng-bind-html': 'cann.MORE'})
        if desc_full:
            print(desc_full.get_text(strip=True))
        else:
            print("NOT FOUND")
            
        print("\n" + "="*80)
        print("All text in table:")
        print(first.get_text())