# Inventory Management Dashboard

Full-stack inventory management system with a React/TypeScript frontend and FastAPI backend. Tracks products, stock movements, and suppliers with real-time analytics.

![CI](https://github.com/eugen-goebel/inventory-management/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3.10+-blue)
![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-3178C6)
![License](https://img.shields.io/badge/License-MIT-green)

## Architecture

```
┌─────────────────────────────────┐
│     React + TypeScript          │
│     Vite + Tailwind CSS         │
│     Recharts                    │
│     Port 5173 (dev)             │
└──────────────┬──────────────────┘
               │ REST API
               ▼
┌─────────────────────────────────┐
│     FastAPI + Python            │
│     SQLAlchemy ORM              │
│     Pydantic v2                 │
│     Port 8000                   │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│     SQLite                      │
│     inventory.db                │
└─────────────────────────────────┘
```

## Features

- **Dashboard**: KPI cards, stock value by category (bar chart), top products, recent movements
- **Product Management**: CRUD operations, search, category filter, low-stock alerts
- **Stock Movements**: Record inbound/outbound stock with reference tracking
- **Supplier Management**: CRUD with product count tracking
- **Analytics API**: Real-time stock value, category breakdown, movement history
- **Data Validation**: Pydantic v2 schemas, unique SKU enforcement, stock integrity checks
- **30+ Backend Tests** with pytest

## Tech Stack

### Frontend
![React](https://img.shields.io/badge/React-61DAFB?style=flat&logo=react&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=flat&logo=typescript&logoColor=white)
![Vite](https://img.shields.io/badge/Vite-646CFF?style=flat&logo=vite&logoColor=white)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-06B6D4?style=flat&logo=tailwindcss&logoColor=white)

### Backend
![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?style=flat&logo=sqlalchemy&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=flat&logo=sqlite&logoColor=white)

### DevOps
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)
![pytest](https://img.shields.io/badge/pytest-0A9EDC?style=flat&logo=pytest&logoColor=white)

## Quick Start

### With Docker

```bash
docker build -t inventory-management .
docker run -p 8000:8000 inventory-management
```

Open http://localhost:8000 in your browser.

### Manual Setup

**Backend:**
```bash
cd backend
pip install -r requirements.txt
python -m data.seed          # Generate sample data
uvicorn main:app --reload    # Start API at localhost:8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev                  # Start dev server at localhost:5173
```

### API Documentation

Once the backend is running, visit http://localhost:8000/docs for interactive Swagger documentation.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/products | List products (search, category, low_stock filter) |
| POST | /api/products | Create product |
| PUT | /api/products/{id} | Update product |
| DELETE | /api/products/{id} | Delete product (only if stock is 0) |
| GET | /api/movements | List stock movements |
| POST | /api/movements | Record stock in/out |
| GET | /api/suppliers | List suppliers |
| POST | /api/suppliers | Create supplier |
| PUT | /api/suppliers/{id} | Update supplier |
| DELETE | /api/suppliers/{id} | Delete supplier (only if no products) |
| GET | /api/analytics/dashboard | Dashboard KPIs and charts |

## Project Structure

```
inventory-management/
├── backend/
│   ├── agents/
│   │   ├── routes.py              # API endpoint definitions
│   │   ├── product_service.py     # Product CRUD logic
│   │   ├── movement_service.py    # Stock movement logic
│   │   ├── supplier_service.py    # Supplier CRUD logic
│   │   └── analytics_service.py   # Dashboard analytics
│   ├── models/
│   │   ├── orm.py                 # SQLAlchemy table definitions
│   │   └── schemas.py             # Pydantic request/response models
│   ├── db/
│   │   └── database.py            # Database connection and session
│   ├── data/
│   │   └── seed.py                # Sample data generator
│   ├── tests/                     # 30+ pytest tests
│   ├── main.py                    # FastAPI application entry point
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── pages/                 # Dashboard, Products, Movements, Suppliers
│   │   ├── components/            # KpiCard, Modal, Layout, LoadingSpinner
│   │   ├── api/                   # API client with fetch wrapper
│   │   └── types/                 # TypeScript interfaces
│   ├── package.json
│   └── vite.config.ts
├── Dockerfile
└── README.md
```

## Running Tests

```bash
cd backend
pytest -v
```

## License

MIT
