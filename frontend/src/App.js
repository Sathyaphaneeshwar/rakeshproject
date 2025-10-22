import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = 'http://localhost:8000';

function App() {
  const [watchlist, setWatchlist] = useState([]);
  const [allStocks, setAllStocks] = useState([]);
  const [announcements, setAnnouncements] = useState([]);
  const [selectedStock, setSelectedStock] = useState(null);
  const [showSearchModal, setShowSearchModal] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchWatchlist();
    fetchAllStocks();
  }, []);

  // Auto-refresh announcements every 5 seconds
  useEffect(() => {
    if (selectedStock) {
      const interval = setInterval(() => {
        fetchAnnouncements(selectedStock.stock_code);
      }, 5000);
      return () => clearInterval(interval);
    }
  }, [selectedStock]);

  const fetchWatchlist = async () => {
    try {
      const res = await axios.get(`${API_URL}/watchlist`);
      setWatchlist(res.data);
    } catch (err) {
      console.error('Error:', err);
    }
  };

  const fetchAllStocks = async () => {
    try {
      const res = await axios.get(`${API_URL}/stocks`);
      setAllStocks(res.data);
    } catch (err) {
      console.error('Error:', err);
    }
  };

  const fetchAnnouncements = async (stockCode) => {
    try {
      const res = await axios.get(`${API_URL}/announcements?stock_code=${stockCode}`);
      setAnnouncements(res.data);
    } catch (err) {
      console.error('Error:', err);
    }
  };

  const addToWatchlist = async (stockCode) => {
    try {
      await axios.post(`${API_URL}/watchlist/add/${stockCode}`);
      fetchWatchlist();
      setShowSearchModal(false);
      setSearchTerm('');
      alert('Stock added to watchlist! Scraping started...');
    } catch (err) {
      console.error('Error:', err);
    }
  };

  const removeFromWatchlist = async (stockCode) => {
    try {
      await axios.delete(`${API_URL}/watchlist/remove/${stockCode}`);
      fetchWatchlist();
      if (selectedStock?.stock_code === stockCode) {
        setSelectedStock(null);
        setAnnouncements([]);
      }
    } catch (err) {
      console.error('Error:', err);
    }
  };

  const selectStock = (stock) => {
    setSelectedStock(stock);
    fetchAnnouncements(stock.stock_code);
  };

  const filteredStocks = allStocks.filter(stock =>
    (stock.stock_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
     stock.stock_code.toLowerCase().includes(searchTerm.toLowerCase())) &&
    !watchlist.some(w => w.stock_code === stock.stock_code)
  );

  return (
    <div style={{ minHeight: '100vh', background: '#f3f4f6' }}>
      {/* Header */}
      <header className="header">
        <h1>📊 Stock Watchlist Dashboard</h1>
        <p>AI-Powered Announcement Analysis</p>
      </header>

      <div className="container">
        {/* Watchlist Section */}
        <div style={{ marginBottom: '2rem' }}>
          <h2 style={{ marginBottom: '1rem' }}>My Watchlist</h2>
          
          <div style={{ 
            display: 'flex', 
            gap: '1rem', 
            overflowX: 'auto',
            padding: '1rem 0'
          }}>
            {watchlist.map(stock => (
              <div
                key={stock.stock_code}
                onClick={() => selectStock(stock)}
                style={{
                  minWidth: '200px',
                  padding: '1rem',
                  background: selectedStock?.stock_code === stock.stock_code ? '#3b82f6' : 'white',
                  color: selectedStock?.stock_code === stock.stock_code ? 'white' : 'black',
                  borderRadius: '12px',
                  cursor: 'pointer',
                  boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
                  transition: 'all 0.2s',
                  position: 'relative'
                }}
                onMouseEnter={e => e.currentTarget.style.transform = 'translateY(-2px)'}
                onMouseLeave={e => e.currentTarget.style.transform = 'translateY(0)'}
              >
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    removeFromWatchlist(stock.stock_code);
                  }}
                  style={{
                    position: 'absolute',
                    top: '0.5rem',
                    right: '0.5rem',
                    background: 'rgba(0,0,0,0.1)',
                    border: 'none',
                    borderRadius: '50%',
                    width: '24px',
                    height: '24px',
                    cursor: 'pointer',
                    color: selectedStock?.stock_code === stock.stock_code ? 'white' : '#666'
                  }}
                >
                  ×
                </button>
                <div style={{ fontWeight: 'bold', fontSize: '0.9rem' }}>
                  {stock.stock_code}
                </div>
                <div style={{ fontSize: '0.75rem', marginTop: '0.25rem', opacity: 0.8 }}>
                  {stock.stock_name.substring(0, 25)}...
                </div>
              </div>
            ))}

            {/* Add Stock Button */}
            <div
              onClick={() => setShowSearchModal(true)}
              style={{
                minWidth: '200px',
                padding: '1rem',
                background: 'white',
                border: '2px dashed #d1d5db',
                borderRadius: '12px',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexDirection: 'column',
                gap: '0.5rem'
              }}
            >
              <div style={{ fontSize: '2rem' }}>+</div>
              <div style={{ fontSize: '0.875rem', color: '#6b7280' }}>Add Stock</div>
            </div>
          </div>
        </div>

        {/* Announcements Section */}
        {selectedStock && (
          <div>
            <h2 style={{ marginBottom: '1rem' }}>
              Announcements - {selectedStock.stock_name}
            </h2>
            
            {announcements.length === 0 ? (
              <div style={{ 
                background: 'white', 
                padding: '2rem', 
                borderRadius: '8px',
                textAlign: 'center',
                color: '#6b7280'
              }}>
                No announcements yet. Scraping in progress...
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                {announcements.map(ann => (
                  <div key={ann.id} className="announcement-card">
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <div style={{ flex: 1 }}>
                        <h3>{ann.title}</h3>
                        <div className="announcement-meta">
                          {ann.category} | {ann.announcement_date}
                        </div>
                        {ann.llm_summary && (
                          <div className="summary-box">
                            <p>🤖 AI Summary:</p>
                            <p>{ann.llm_summary}</p>
                          </div>
                        )}
                      </div>
                      {ann.processed && (
                        <span className="badge active">✓ Processed</span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Search Modal */}
      {showSearchModal && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0,0,0,0.5)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000
        }}>
          <div style={{
            background: 'white',
            borderRadius: '12px',
            padding: '2rem',
            width: '90%',
            maxWidth: '600px',
            maxHeight: '80vh',
            overflow: 'auto'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
              <h2>Add Stock to Watchlist</h2>
              <button
                onClick={() => {
                  setShowSearchModal(false);
                  setSearchTerm('');
                }}
                style={{
                  background: 'none',
                  border: 'none',
                  fontSize: '1.5rem',
                  cursor: 'pointer'
                }}
              >
                ×
              </button>
            </div>

            <input
              type="text"
              placeholder="Search by name or code..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              autoFocus
              style={{
                width: '100%',
                padding: '0.75rem',
                border: '1px solid #e5e7eb',
                borderRadius: '8px',
                marginBottom: '1rem',
                fontSize: '1rem'
              }}
            />

            <div style={{ maxHeight: '400px', overflow: 'auto' }}>
              {filteredStocks.map(stock => (
                <div
                  key={stock.stock_code}
                  onClick={() => addToWatchlist(stock.stock_code)}
                  style={{
                    padding: '1rem',
                    border: '1px solid #e5e7eb',
                    borderRadius: '8px',
                    marginBottom: '0.5rem',
                    cursor: 'pointer',
                    transition: 'all 0.2s'
                  }}
                  onMouseEnter={e => e.currentTarget.style.background = '#f9fafb'}
                  onMouseLeave={e => e.currentTarget.style.background = 'white'}
                >
                  <div style={{ fontWeight: 'bold' }}>{stock.stock_code}</div>
                  <div style={{ fontSize: '0.875rem', color: '#6b7280' }}>
                    {stock.stock_name} | {stock.sector}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;