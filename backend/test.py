import requests
import json
from bs4 import BeautifulSoup
from datetime import datetime
import re

def parse_announcements(html_content):
    """Extract announcements from BSE HTML"""
    soup = BeautifulSoup(html_content, 'html.parser')
    announcements = []
    
    # Find all announcement tables
    tables = soup.find_all('table', {'ng-repeat': 'cann in CorpannData.Table'})
    
    print(f"\nFound {len(tables)} announcements")
    
    for table in tables:
        announcement = {}
        
        # Extract data from first row
        first_row = table.find('tr')
        tds = first_row.find_all('td', class_='tdcolumngrey')
        
        # Stock code and title
        if len(tds) > 0:
            first_td_text = tds[0].get_text(strip=True)
            parts = first_td_text.split('|')
            announcement['stock_code'] = parts[0].strip() if parts else ''
            
            # Title from span
            title_span = tds[0].find('span', {'ng-bind-html': 'cann.NEWSSUB'})
            announcement['title'] = title_span.get_text(strip=True) if title_span else ''
        
        # Category
        if len(tds) > 1:
            announcement['category'] = tds[1].get_text(strip=True)
        
        # PDF link
        pdf_link = table.find('a', href=True)
        announcement['pdf_link'] = pdf_link['href'] if pdf_link and '.pdf' in pdf_link['href'] else ''
        
        # Description from second row
        desc_span = table.find('span', {'ng-bind-html': 'cann.HEADLINE'})
        announcement['description'] = desc_span.get_text(strip=True) if desc_span else ''

        # Date and time extraction - NEW APPROACH
        # Find all td elements and search their text content
        date_row = None
        for td in table.find_all('td'):
            td_text = td.get_text(strip=True)
            if 'Exchange Disseminated Time' in td_text:
                date_row = td
                break
            

        if date_row:
            date_text = date_row.get_text(strip=True)

            # Extract datetime from text
            try:
                import re
                date_match = re.search(r'Exchange Disseminated Time\s*(\d{2}-\d{2}-\d{4}\s+\d{2}:\d{2}:\d{2})', date_text)

                if date_match:
                    date_str = date_match.group(1)
                    announcement['datetime'] = datetime.strptime(date_str, '%d-%m-%Y %H:%M:%S')
                    announcement['date'] = announcement['datetime'].strftime('%Y-%m-%d')
                    announcement['time'] = announcement['datetime'].strftime('%H:%M:%S')
                else:
                    announcement['datetime'] = None
                    announcement['date'] = None
                    announcement['time'] = None
            except Exception as e:
                announcement['datetime'] = None
                announcement['date'] = None
                announcement['time'] = None
        else:
            announcement['datetime'] = None
            announcement['date'] = None
            announcement['time'] = None

        announcements.append(announcement)
                    
    return announcements

FIRECRAWL_URL = "http://localhost:3002"
bse_url = "https://www.bseindia.com/stock-share-price/reliance-industries-ltd/reliance/500325/corp-announcements/"

payload = {
    "url": bse_url,
    "formats": ["markdown", "html"],
    "waitFor": 5000,  # Wait 5 seconds for JS to load
    "timeout": 90000,
    "onlyMainContent": True

}

print("Scraping BSE page with JavaScript rendering...")
response = requests.post(f"{FIRECRAWL_URL}/v1/scrape", json=payload, timeout=120)

if response.status_code == 200:
    data = response.json()
    
    # Save full response
    with open('bse_scrape_result.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    # Get HTML content
    html_content = data.get('data', {}).get('html', '')
    
    # Save HTML
    with open('bse_page.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✓ Success! Saved files")
    
    # NEW: Parse announcements
    announcements = parse_announcements(html_content)

    
    # NEW: Print structured output
    print("\n" + "="*80)
    print("EXTRACTED ANNOUNCEMENTS")
    print("="*80)
    
    for i, ann in enumerate(announcements, 1):
        print(f"\n--- Announcement {i} ---")
        print(f"Stock Code: {ann.get('stock_code', 'N/A')}")
        print(f"Title: {ann.get('title', 'N/A')}")
        print(f"Category: {ann.get('category', 'N/A')}")
        print(f"Description: {ann.get('description', 'N/A')}")
        print(f"Date: {ann.get('date', 'N/A')}")
        print(f"Time: {ann.get('time', 'N/A')}")
        print(f"PDF Link: {ann.get('pdf_link', 'N/A')}")