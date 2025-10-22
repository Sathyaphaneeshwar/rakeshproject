# backend/config.py

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'stock_announcements',
    'user': 'stocks',
    'password': 'admin123'
}

# Services
PDF_SERVICE_URL = "http://localhost:5001"
FIRECRAWL_URL = "http://localhost:3002"