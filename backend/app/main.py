from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.health import router as health_router
from app.api.auth import router as auth_router
from app.api.parcels import router as parcels_router
from app.api.buildings import router as buildings_router
from app.api.properties import router as properties_router
from app.api.conflicts import router as conflicts_router
from app.api.map import router as map_router
from app.api.reports import router as reports_router
from app.api.ulpin import router as ulpin_router

app = FastAPI(
    title="3D ULPIN Generation & Vertical Property Mapping System",
    description="Backend API for 3D spatial property volumes, 3D ULPIN generation, and conflict detection.",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all Section 7 API routers (conflicts before properties to prevent /{ulpin_3d} shadowing /conflicts)
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(parcels_router)
app.include_router(buildings_router)
app.include_router(conflicts_router)
app.include_router(properties_router)
app.include_router(map_router)
app.include_router(reports_router)
app.include_router(ulpin_router)

@app.get("/")
def read_root():
    return {
        "title": "3D ULPIN Generation & Vertical Property Mapping System",
        "health_check": "/health",
        "docs": "/docs",
        "endpoints": [
            "POST /auth/login",
            "POST /parcels/upload",
            "POST /buildings/{parcel_id}",
            "POST /properties/generate",
            "GET /properties/{ulpin_3d}",
            "GET /properties/conflicts",
            "POST /properties/{id}/verify",
            "GET /map/tiles",
            "GET /reports/summary"
        ]
    }
