import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

function StocksOverview() {
  const [stocks, setStocks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [sectorFilter, setSectorFilter] = useState('all');
  const [transcriptFilter, setTranscriptFilter] = useState('all');

  useEffect(() => {
    fetchStocksOverview();
  }, []);

  const fetchStocksOverview = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE_URL}/stocks/overview`);
      setStocks(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to fetch stocks overview');
      console.error('Error fetching stocks overview:', err);
    } finally {
      setLoading(false);
    }
  };

  // Get unique sectors for filter
  const sectors = ['all', ...new Set(stocks.map(s => s.sector).filter(Boolean))];

  // Filter stocks based on search and filters
  const filteredStocks = stocks.filter(stock => {
    const matchesSearch =
      stock.stock_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      stock.stock_code.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesSector = sectorFilter === 'all' || stock.sector === sectorFilter;

    const matchesTranscript =
      transcriptFilter === 'all' ||
      (transcriptFilter === 'with' && stock.has_transcript) ||
      (transcriptFilter === 'without' && !stock.has_transcript);

    return matchesSearch && matchesSector && matchesTranscript;
  });

  const formatDate = (dateStr) => {
    if (!dateStr) return 'N/A';
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  if (loading) {
    return (
      <div className="stocks-overview">
        <div className="loading">Loading stocks overview...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="stocks-overview">
        <div className="error">{error}</div>
        <button onClick={fetchStocksOverview} className="retry-button">
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="stocks-overview">
      <div className="overview-header">
        <h1>Stocks Overview</h1>
        <p className="subtitle">
          Total Stocks: {filteredStocks.length} / {stocks.length}
        </p>
      </div>

      <div className="filters-container">
        <div className="filter-group">
          <input
            type="text"
            placeholder="Search by name or code..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
        </div>

        <div className="filter-group">
          <label>Sector:</label>
          <select
            value={sectorFilter}
            onChange={(e) => setSectorFilter(e.target.value)}
            className="filter-select"
          >
            {sectors.map(sector => (
              <option key={sector} value={sector}>
                {sector === 'all' ? 'All Sectors' : sector || 'Unknown'}
              </option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label>Transcript:</label>
          <select
            value={transcriptFilter}
            onChange={(e) => setTranscriptFilter(e.target.value)}
            className="filter-select"
          >
            <option value="all">All Stocks</option>
            <option value="with">With Transcripts</option>
            <option value="without">Without Transcripts</option>
          </select>
        </div>
      </div>

      <div className="table-container">
        <table className="stocks-table">
          <thead>
            <tr>
              <th>Stock Code</th>
              <th>Stock Name</th>
              <th>Sector</th>
              <th>Transcript Available</th>
              <th>Transcript Count</th>
              <th>Last Transcript Date</th>
            </tr>
          </thead>
          <tbody>
            {filteredStocks.length === 0 ? (
              <tr>
                <td colSpan="6" className="no-data">
                  No stocks found matching your criteria
                </td>
              </tr>
            ) : (
              filteredStocks.map(stock => (
                <tr key={stock.stock_code}>
                  <td className="stock-code">{stock.stock_code}</td>
                  <td className="stock-name">{stock.stock_name}</td>
                  <td className="sector">{stock.sector || 'N/A'}</td>
                  <td className="transcript-status">
                    {stock.has_transcript ? (
                      <span className="badge badge-success">Yes</span>
                    ) : (
                      <span className="badge badge-inactive">No</span>
                    )}
                  </td>
                  <td className="transcript-count">
                    {stock.transcript_count > 0 ? stock.transcript_count : '-'}
                  </td>
                  <td className="transcript-date">
                    {formatDate(stock.last_transcript_date)}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default StocksOverview;
