import requests
import psycopg2
import re
import json

DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'n8n',
    'user': 'n8n',
    'password': 'n8n'
}

def fetch_bse_equity_stocks_direct():
    """Fetch BSE equity stocks directly from API"""
    
    api_url = "https://api.bseindia.com/BseIndiaAPI/api/ListofScripData/w?Group=&Scripcode=&segment=Equity&status="
    
    print("📥 Fetching BSE Equity stocks from API...\n")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Referer': 'https://www.bseindia.com/'
    }
    
    try:
        response = requests.get(api_url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            # Save raw response
            with open('bse_api_response.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            
            print(f"✓ API returned {len(data)} records\n")
            
            stocks = []
            for item in data:
                stock = {
                    'security_code': str(item.get('SCRIP_CD', '')).strip(),
                    'security_name': item.get('Scrip_Name', '').strip(),
                    'issuer_name': item.get('Issuer_Name', '').strip(),
                    'security_id': item.get('scrip_id', '').strip(),
                    'status': item.get('Status', '').strip(),
                    'group': item.get('GROUP', '').strip(),
                    'face_value': item.get('FACE_VALUE', '').strip(),
                    'isin': item.get('ISIN_NUMBER', '').strip(),
                    'market_cap': item.get('Mktcap', '').strip(),
                    'industry': item.get('INDUSTRY', '').strip() if item.get('INDUSTRY') else 'Others',
                    'segment': item.get('Segment', '').strip()
                }
                
                if stock['security_code'] and stock['security_name']:
                    stocks.append(stock)
            
            print(f"✓ Parsed {len(stocks)} stocks!\n")
            
            if stocks:
                print("First stock:")
                first = stocks[0]
                print(f"  Code: {first['security_code']}")
                print(f"  Name: {first['security_name']}")
                print(f"  ID: {first['security_id']}")
                print(f"  Status: {first['status']}")
                print()
            
            return stocks
                
        else:
            print(f"✗ HTTP Error: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return []

def construct_bse_url(security_code, security_id, security_name):
    """Construct BSE announcement URL"""
    # Use security_id if available, otherwise construct from name
    if security_id:
        url = f"https://www.bseindia.com/stock-share-price/{security_name.lower().replace(' ', '-')}/{security_id}/{security_code}/corp-announcements/"
    else:
        clean_name = security_name.lower()
        clean_name = re.sub(r'\s*(ltd|limited|pvt|private|corporation|corp|inc)\s*\.?\s*$', '', clean_name, flags=re.IGNORECASE)
        clean_name = re.sub(r'[^a-z0-9\s-]', '', clean_name)
        clean_name = re.sub(r'\s+', '-', clean_name.strip())
        clean_name = re.sub(r'-+', '-', clean_name).strip('-')
        
        url = f"https://www.bseindia.com/stock-share-price/{clean_name}/{security_code}/corp-announcements/"
    
    return url

def determine_sector(name, industry):
    """Determine sector from industry or name"""
    # Try industry first
    if industry and industry.lower() != 'others':
        industry_lower = industry.lower()
        
        if any(word in industry_lower for word in ['bank', 'financ', 'insurance', 'nbfc']):
            return 'Finance'
        elif any(word in industry_lower for word in ['pharma', 'health', 'hospital', 'medic']):
            return 'Healthcare'
        elif any(word in industry_lower for word in ['software', 'it service', 'technology']):
            return 'IT'
        elif any(word in industry_lower for word in ['oil', 'gas', 'power', 'energy']):
            return 'Energy'
        elif any(word in industry_lower for word in ['fmcg', 'consumer', 'retail', 'auto']):
            return 'Consumer'
        elif any(word in industry_lower for word in ['construct', 'cement', 'steel', 'infra']):
            return 'Industrial'
        elif any(word in industry_lower for word in ['telecom']):
            return 'Telecom'
        elif any(word in industry_lower for word in ['real estate']):
            return 'Real Estate'
    
    # Fallback to name
    name_lower = name.lower()
    if any(word in name_lower for word in ['bank', 'financ', 'insurance']):
        return 'Finance'
    elif any(word in name_lower for word in ['pharma', 'health', 'hospital']):
        return 'Healthcare'
    elif any(word in name_lower for word in ['tech', 'software', 'info']):
        return 'IT'
    elif any(word in name_lower for word in ['oil', 'gas', 'power', 'energy']):
        return 'Energy'
    
    return 'Others'

def save_stocks_to_db(stocks):
    """Save stocks to database with better error handling"""
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    count = 0
    skipped = 0
    errors = 0
    
    print("💾 Saving stocks to database...\n")
    
    for stock in stocks:
        try:
            status = stock.get('status', '').upper()
            if status != 'ACTIVE':
                skipped += 1
                continue
            
            bse_url = construct_bse_url(
                stock['security_code'], 
                stock['security_id'], 
                stock['security_name']
            )
            sector = determine_sector(stock['security_name'], stock.get('industry', ''))
            
            cursor.execute("""
                INSERT INTO stocks (stock_code, stock_name, bse_url, sector, sub_sector, is_active)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (stock_code) DO UPDATE 
                SET stock_name = EXCLUDED.stock_name,
                    bse_url = EXCLUDED.bse_url,
                    sector = EXCLUDED.sector,
                    sub_sector = EXCLUDED.sub_sector;
            """, (
                stock['security_code'], 
                stock['security_name'], 
                bse_url, 
                sector, 
                stock.get('industry', 'Others'), 
                False
            ))
            
            conn.commit()  # Commit after each successful insert
            count += 1
            
            if count % 100 == 0:
                print(f"  ... saved {count} stocks")
                
        except Exception as e:
            conn.rollback()  # Rollback on error
            errors += 1
            if errors <= 5:  # Show first 5 errors only
                print(f"  ✗ Error saving {stock.get('security_code')}: {e}")
    
    cursor.close()
    conn.close()
    
    print(f"\n✓ Saved {count} active stocks to database")
    print(f"⊘ Skipped {skipped} inactive stocks")
    if errors > 0:
        print(f"✗ Errors: {errors} stocks failed")

if __name__ == "__main__":
    print("=== BSE Equity Stock Fetcher ===\n")
    
    stocks = fetch_bse_equity_stocks_direct()
    
    if stocks:
        print(f"📊 Total: {len(stocks)} stocks\n")
        
        # Count by status
        active = sum(1 for s in stocks if s['status'].upper() == 'ACTIVE')
        print(f"Active stocks: {active}")
        print(f"Other stocks: {len(stocks) - active}\n")
        
        save_choice = input("Save ACTIVE stocks to database? (yes/no): ").strip().lower()
        
        if save_choice == 'yes':
            save_stocks_to_db(stocks)
            print("\n✅ Done! Stocks saved (inactive by default)")
            print("💡 Activate specific stocks via frontend or SQL")
        else:
            print("Skipped saving")
    else:
        print("❌ No stocks fetched")
    
    print("\n=== Done ===")