import requests
import json
import hashlib
import psycopg2
from bs4 import BeautifulSoup
from datetime import datetime
import re

from config import DB_CONFIG, FIRECRAWL_URL

def get_active_stocks():
    """Get all active stocks from database"""
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    cursor.execute("SELECT stock_code, stock_name, bse_url FROM stocks WHERE is_active = TRUE")
    stocks = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return stocks

def create_announcement_hash(stock_code, title, date_str):
    """Create unique hash for announcement"""
    unique_string = f"{stock_code}_{title}_{date_str}"
    return hashlib.sha256(unique_string.encode()).hexdigest()

def announcement_exists(unique_hash):
    """Check if announcement already exists in database"""
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM announcements WHERE unique_hash = %s", (unique_hash,))
    exists = cursor.fetchone() is not None
    
    cursor.close()
    conn.close()
    
    return exists

def save_announcement(announcement):
    """Save new announcement to database"""
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO announcements 
            (stock_code, title, description, category, pdf_link, 
             announcement_date, announcement_time, announcement_datetime, submission_time, unique_hash)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            announcement['stock_code'],
            announcement['title'],
            announcement['description'],
            announcement['category'],
            announcement['pdf_link'],
            announcement['date'],
            announcement['time'],
            announcement['datetime'],
            announcement['submission_time'],  # ADDED THIS
            announcement['unique_hash']
        ))
        
        announcement_id = cursor.fetchone()[0]
        conn.commit()
        
        print(f"  ✓ Saved: {announcement['title'][:50]}...")
        
    except Exception as e:
        print(f"  ✗ Error saving: {e}")
    finally:
        cursor.close()
        conn.close()

        
def parse_announcements(html_content, stock_code):
    """Extract announcements from HTML"""
    soup = BeautifulSoup(html_content, 'html.parser')
    announcements = []
    
    tables = soup.find_all('table', {'ng-repeat': 'cann in CorpannData.Table'})
    
    for table in tables:
        announcement = {}
        
        # Extract data
        first_row = table.find('tr')
        tds = first_row.find_all('td', class_='tdcolumngrey')
        
        if len(tds) > 0:
            # Title
            title_span = tds[0].find('span', {'ng-bind-html': 'cann.NEWSSUB'})
            announcement['title'] = title_span.get_text(strip=True) if title_span else ''
        
        # Category
        if len(tds) > 1:
            announcement['category'] = tds[1].get_text(strip=True)
        
        # PDF link
        pdf_link = table.find('a', href=True)
        announcement['pdf_link'] = pdf_link['href'] if pdf_link and '.pdf' in pdf_link['href'] else ''
        
        desc_span_full = table.find('span', {'ng-bind-html': 'cann.MORE'})
        desc_span_short = table.find('span', {'ng-bind-html': 'cann.HEADLINE'})

        if desc_span_full and desc_span_full.get_text(strip=True):
            announcement['description'] = desc_span_full.get_text(strip=True)
        elif desc_span_short:
            announcement['description'] = desc_span_short.get_text(strip=True)
        else:
            announcement['description'] = ''
        
        # Date extraction
        date_row = None
        for td in table.find_all('td'):
            td_text = td.get_text(strip=True)
            if 'Exchange Disseminated Time' in td_text:
                date_row = td
                break
        
        if date_row:
            date_text = date_row.get_text(strip=True)
            try:
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
            except:
                announcement['datetime'] = None
                announcement['date'] = None
                announcement['time'] = None
        else:
            announcement['datetime'] = None
            announcement['date'] = None
            announcement['time'] = None

        
        announcement['stock_code'] = stock_code
        submission_time = None
        for td in table.find_all('td'):
            td_text = td.get_text(strip=True)
            if 'Exchange Received Time' in td_text:
                try:
                    submission_match = re.search(r'Exchange Received Time\s*(\d{2}-\d{2}-\d{4}\s+\d{2}:\d{2}:\d{2})', td_text)
                    if submission_match:
                        submission_str = submission_match.group(1)
                        submission_time = datetime.strptime(submission_str, '%d-%m-%Y %H:%M:%S')
                        print(f"    → Found submission time: {submission_time}")  # DEBUG
                        break
                except Exception as e:
                    print(f"    ✗ Submission time parse error: {e}")  # DEBUG
                    pass
                
        announcement['submission_time'] = submission_time
    
        
        # Create unique hash (this should already be below)
        hash_date = announcement['date'] if announcement['date'] else 'no-date'
        announcement['unique_hash'] = create_announcement_hash(
            stock_code, 
            announcement['title'], 
            hash_date
        )
        
        # Create unique hash
        hash_date = announcement['date'] if announcement['date'] else 'no-date'
        announcement['unique_hash'] = create_announcement_hash(
            stock_code, 
            announcement['title'], 
            hash_date
        )
        
        announcements.append(announcement)
    
    return announcements

def scrape_stock(stock_code, stock_name, bse_url):
    """Scrape announcements for a single stock"""
    print(f"\n📊 Scraping {stock_code} - {stock_name}...")
    
    payload = {
        "url": bse_url,
        "formats": ["html"],
        "waitFor": 5000,
        "timeout": 90000,
        "onlyMainContent": True
    }
    
    try:
        response = requests.post(f"{FIRECRAWL_URL}/v1/scrape", json=payload, timeout=120)
        
        if response.status_code == 200:
            data = response.json()
            html_content = data.get('data', {}).get('html', '')
            
            announcements = parse_announcements(html_content, stock_code)
            
            print(f"  Found {len(announcements)} announcements")
            
            # Save only new announcements
            new_count = 0
            for ann in announcements:
                if not announcement_exists(ann['unique_hash']):
                    save_announcement(ann)
                    new_count += 1
            
            print(f"  💾 Saved {new_count} new announcements")
            
            # Update last scraped time
            update_last_scraped(stock_code)
            
        else:
            print(f"  ✗ Error: {response.status_code}")
            
    except Exception as e:
        print(f"  ✗ Exception: {e}")

def update_last_scraped(stock_code):
    """Update last scraped timestamp for stock"""
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    cursor.execute(
        "UPDATE stocks SET last_scraped_at = CURRENT_TIMESTAMP WHERE stock_code = %s",
        (stock_code,)
    )
    
    conn.commit()
    cursor.close()
    conn.close()

def main():
    """Main scraping function"""
    print("🚀 Starting scraper...")
    
    stocks = get_active_stocks()
    print(f"📋 Found {len(stocks)} active stocks to scrape\n")
    
    for stock_code, stock_name, bse_url in stocks:
        scrape_stock(stock_code, stock_name, bse_url)
    
    print("\n✅ Scraping completed!")

if __name__ == "__main__":
    main()