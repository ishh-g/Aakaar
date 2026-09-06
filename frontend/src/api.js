// Central backend address for every API call in the app.
//
// Local dev works with zero setup: falls back to http://localhost:8000.
// Hosted deploys: set VITE_API_URL in frontend/.env (see .env.example),
// e.g. VITE_API_URL=https://aakaar-backend.onrender.com
export const API_BASE_URL = (
  import.meta.env.VITE_API_URL || 'http://localhost:8000'
).replace(/\/+$/, '');
