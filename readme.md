# RTR_FASTAPI Web Application

## Overview

RTR_FASTAPI is a modular web application built with FastAPI and SQLAlchemy, designed for managing articles, price histories, and analytics for RTR products. It integrates a scraping engine to collect product data, supports robust CRUD operations, and provides endpoints for advanced analytics.

---

## Features

- **RESTful API**: FastAPI-powered endpoints for articles, categories, and analytics.
- **Database Models**: SQLAlchemy ORM models for articles, price records, and last prices.
- **Data Scraping**: Integrated scraping engine for automated product data collection.
- **Analytics**: Endpoints for category statistics, price history, and product analytics.
- **Validation**: Pydantic schemas for request/response validation.
- **Error Handling**: Centralized error management and logging.
- **Extensible Architecture**: Modular design for easy feature addition and maintenance.

---

## Project Structure

RTR_FASTAPI/
│
├── database/
│   ├── crud_operations.py      # CRUD logic for all models
│   ├── db_models.py            # SQLAlchemy ORM models
│   ├── db_session.py           # Database session manager
│   ├── crud_base.py            # Base CRUD class
│   └── db_utils.py             # Utility functions for data conversion
│
├── schemas/
│   ├── articles.py             # Article schemas
│   ├── analytics.py            # Analytics schemas
│   ├── filters.py              # Filter schemas
│   ├── hist_prices.py          # Price record schemas
│   ├── last_price.py           # Last price schemas
│   └── __init__.py
│
├── routers/
│   ├── articles.py             # Article endpoints
│   ├── categories.py           # Category endpoints
│   ├── analytics.py            # Analytics endpoints
│
├── orchestration/
│   ├── data_orchestrator.py    # Data pipeline orchestration
│   ├── master_orchestrator.py  # Main pipeline controller
│   └── scraping_orchestrator.py# Scraping orchestration
│
├── scrap/                      # Scraping engine and schemas
│
├── main.py                     # FastAPI app entry point
├── requirements.txt            # Python dependencies
└── mireadme.txt                # (Legacy/Spanish notes)


---

## Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone <repo-url>
   cd RTR_FASTAPI

2. **Create and Activate Virtual Environment**
    python3 -m venv venv
    source venv/bin/activate

3. **Install Dependencies**
    pip install -r requirements.txt

4. **Database Initialization**
    The database is SQLite by default (rtr_crawler_Alchemy.db).
    Tables are created automatically on first run via db_manager.create_tables().

5. **Run the Application**
    uvicorn main_app --reload
    
    Access the API docs at http://localhost:8000/docs

6. **Contributing:**
 - Fork the repository and create a feature branch.
 - Follow PEP8 and project coding standards.
 - Add docstrings and comments for clarity.
 - Write tests for new features or bug fixes.
 - Submit a pull request with a clear description of changes.