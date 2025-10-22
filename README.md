# Stock Scraper & Analyzer Project

## Overview
This project scrapes corporate announcements from BSE (Bombay Stock Exchange), extracts PDFs, analyzes them using LLM, and presents the information in a dashboard.

## Architecture
- **n8n**: Workflow automation (scraping & scheduling)
- **PostgreSQL**: Database for storing stock data and analysis
- **Redis**: Caching and queue management
- **Frontend**: User dashboard (to be built)
- **Backend**: Custom scripts and API endpoints

## Setup

### Prerequisites
- Docker Desktop installed
- Node.js installed

### Running the Project

1. Start all services:
```bash
   docker compose up -d