# 3D ULPIN Generation & Vertical Property Mapping System (SIH26011)

Technical prototype for 3D Property Volume Segmentation, Vertical 3D ULPIN Encoding, Spatial Conflict Detection, and CesiumJS 3D Visualization.

## Project Architecture

- `/backend`: Python FastAPI service for geospatial volume processing, 3D ULPIN creation, and PostGIS spatial conflict validation algorithms.
- `/frontend`: React + Vite application leveraging CesiumJS for native 3D geospatial rendering of parcels, buildings, and vertical property units.
- `/db`: PostgreSQL + PostGIS database DDL schema (`schema.sql`) and initial seed data (`seed.sql`).

## Scaffolding Quick Start

### 1. Backend (`/backend`)
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
Health Check Endpoint: `GET http://localhost:8000/health`

### 2. Frontend (`/frontend`)
```bash
cd frontend
npm install
npm run dev
```
Interactive 3D Globe: `http://localhost:5173`

### 3. Database (`/db`)
```bash
psql -U postgres -d ulpin_db -f db/schema.sql
psql -U postgres -d ulpin_db -f db/seed.sql
```
