from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from config import DB_CONFIG

def get_db():
    """Get database connection"""
    return psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)

# Pydantic models
class Stock(BaseModel):
    stock_code: str
    stock_name: str
    sector: str
    is_active: bool

class StockUpdate(BaseModel):
    is_active: bool

class Announcement(BaseModel):
    id: int
    stock_code: str
    title: str
    category: Optional[str]
    announcement_date: Optional[str]
    llm_summary: Optional[str]
    processed: bool

class StockOverview(BaseModel):
    stock_code: str
    stock_name: str
    sector: Optional[str]
    has_transcript: bool
    transcript_count: int
    last_transcript_date: Optional[str]

# API Endpoints

@app.get("/")
async def root():
    return {"message": "BSE Announcements API", "status": "running"}

@app.get("/stocks", response_model=List[Stock])
async def get_stocks(active_only: bool = False):
    """Get all stocks or only active ones"""
    conn = get_db()
    cursor = conn.cursor()
    
    query = "SELECT stock_code, stock_name, sector, is_active FROM stocks"
    if active_only:
        query += " WHERE is_active = TRUE"
    query += " ORDER BY stock_name"
    
    cursor.execute(query)
    stocks = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return stocks

@app.get("/stocks/{stock_code}")
async def get_stock(stock_code: str):
    """Get single stock details"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT stock_code, stock_name, sector, sub_sector, is_active FROM stocks WHERE stock_code = %s",
        (stock_code,)
    )
    stock = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    
    return stock

@app.patch("/stocks/{stock_code}")
async def update_stock(stock_code: str, update: StockUpdate):
    """Activate or deactivate a stock"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute(
        "UPDATE stocks SET is_active = %s WHERE stock_code = %s RETURNING stock_code",
        (update.is_active, stock_code)
    )
    
    updated = cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()
    
    if not updated:
        raise HTTPException(status_code=404, detail="Stock not found")
    
    return {"stock_code": stock_code, "is_active": update.is_active}

@app.get("/announcements")
async def get_announcements(
    stock_code: Optional[str] = None,
    limit: int = 50
):
    """Get announcements, optionally filtered by stock"""
    conn = get_db()
    cursor = conn.cursor()
    
    query = """
        SELECT id, stock_code, title, category, announcement_date, 
               llm_summary, processed, created_at
        FROM announcements
    """
    params = []
    
    if stock_code:
        query += " WHERE stock_code = %s"
        params.append(stock_code)
    
    query += " ORDER BY announcement_date DESC, created_at DESC LIMIT %s"
    params.append(limit)
    
    cursor.execute(query, params)
    announcements = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return announcements

@app.get("/stats")
async def get_stats():
    """Get dashboard statistics"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Total stocks
    cursor.execute("SELECT COUNT(*) as total FROM stocks")
    total_stocks = cursor.fetchone()['total']
    
    # Active stocks
    cursor.execute("SELECT COUNT(*) as active FROM stocks WHERE is_active = TRUE")
    active_stocks = cursor.fetchone()['active']
    
    # Total announcements
    cursor.execute("SELECT COUNT(*) as total FROM announcements")
    total_announcements = cursor.fetchone()['total']
    
    # Processed announcements
    cursor.execute("SELECT COUNT(*) as processed FROM announcements WHERE processed = TRUE")
    processed_announcements = cursor.fetchone()['processed']
    
    cursor.close()
    conn.close()
    
    return {
        "total_stocks": total_stocks,
        "active_stocks": active_stocks,
        "total_announcements": total_announcements,
        "processed_announcements": processed_announcements
    }
# Add after existing endpoints

@app.post("/watchlist/add/{stock_code}")
async def add_to_watchlist(stock_code: str):
    """Add stock to watchlist (activate it)"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute(
        "UPDATE stocks SET is_active = TRUE WHERE stock_code = %s RETURNING stock_code, stock_name",
        (stock_code,)
    )
    
    stock = cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()
    
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    
    # Trigger scraper for this stock immediately
    try:
        import subprocess
        subprocess.Popen(
            ['python', 'scraper.py', stock_code],
            cwd='/Users/sphaneeshwar/Downloads/Project/CallsAnalyzer/backend'
        )
    except:
        pass
    
    return {"stock_code": stock_code, "stock_name": stock['stock_name'], "added": True}

@app.delete("/watchlist/remove/{stock_code}")
async def remove_from_watchlist(stock_code: str):
    """Remove stock from watchlist (deactivate it)"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute(
        "UPDATE stocks SET is_active = FALSE WHERE stock_code = %s RETURNING stock_code",
        (stock_code,)
    )
    
    stock = cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()
    
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    
    return {"stock_code": stock_code, "removed": True}

@app.get("/watchlist")
async def get_watchlist():
    """Get all stocks in watchlist (active stocks)"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT stock_code, stock_name, sector
        FROM stocks
        WHERE is_active = TRUE
        ORDER BY stock_name
    """)

    stocks = cursor.fetchall()
    cursor.close()
    conn.close()

    return stocks

@app.get("/stocks/overview", response_model=List[StockOverview])
async def get_stocks_overview():
    """Get overview of all stocks with transcript summary information"""
    conn = get_db()
    cursor = conn.cursor()

    query = """
        SELECT
            s.stock_code,
            s.stock_name,
            s.sector,
            COUNT(CASE WHEN a.transcript_diarized IS NOT NULL OR a.transcript_link IS NOT NULL THEN 1 END) as transcript_count,
            CASE WHEN COUNT(CASE WHEN a.transcript_diarized IS NOT NULL OR a.transcript_link IS NOT NULL THEN 1 END) > 0
                 THEN TRUE
                 ELSE FALSE
            END as has_transcript,
            MAX(CASE WHEN a.transcript_diarized IS NOT NULL OR a.transcript_link IS NOT NULL
                     THEN a.announcement_date
                     ELSE NULL
                END) as last_transcript_date
        FROM stocks s
        LEFT JOIN announcements a ON s.stock_code = a.stock_code
        GROUP BY s.stock_code, s.stock_name, s.sector
        ORDER BY s.stock_name
    """

    cursor.execute(query)
    stocks_overview = cursor.fetchall()

    cursor.close()
    conn.close()

    return stocks_overview

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)