# Aakaar

3D land-record system generating vertical ULPINs from GIS data, with automated conflict detection. Built for SIH26011.

## Stack
- Frontend: React + CesiumJS
- Backend: FastAPI
- Database: PostgreSQL + PostGIS

## Setup

### Backend
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

### Frontend
cd frontend
npm install
npm run dev

## Environment Variables
Create a `.env` file in `backend/` with:
DATABASE_URL=your_postgres_connection_string

## Team
- Ishika Goel (Team Lead)
- Parv Ahuja
- Pratham Nebhinani
- Arpit Titoria
- Deepak Parmar
- Suhani Bhatia
