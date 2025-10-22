import requests
import json

FIRECRAWL_URL = "http://localhost:3002"
bse_url = "https://www.bseindia.com/stock-share-price/indegene-ltd/INDGN/544172/corp-announcements/"

payload = {
    "url": bse_url,
    "formats": ["markdown", "html"],
    "waitFor": 5000,  # Wait 5 seconds for JS to load
    "timeout": 90000
}

print("Scraping BSE page with JavaScript rendering...")
response = requests.post(f"{FIRECRAWL_URL}/v1/scrape", json=payload, timeout=120)

if response.status_code == 200:
    data = response.json()
    
    # Save full response
    with open('bse_scrape_result.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    # Save just the HTML for inspection
    html_content = data.get('data', {}).get('html', '')
    with open('bse_page.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✓ Success! Saved to:")
    print(f"  - bse_scrape_result.json (full data)")
    print(f"  - bse_page.html (rendered HTML)")
    
    # Quick check for announcements
    markdown = data.get('data', {}).get('markdown', '')
    if 'Compliances-Certificate' in markdown or 'Announcement under Regulation' in markdown:
        print("\n✓ Announcements found in content!")
    else:
        print("\n⚠ Announcements might not be loaded. Try increasing waitFor value.")
else:
    print(f"Error {response.status_code}: {response.json()}")