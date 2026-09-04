from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import json
from shapely.geometry import shape
from app.db import get_db
from app.models.entities import Building, Parcel, User
from app.core.auth import require_roles

router = APIRouter(prefix="/buildings", tags=["Buildings"])

class BuildingCreateRequest(BaseModel):
    total_floors: int = Field(default=1, ge=1, description="Total number of floors")
    footprint_wkt: Optional[str] = Field(default=None, description="WKT string e.g. POLYGON((...))")
    footprint_geojson: Optional[Dict[str, Any]] = Field(default=None, description="GeoJSON polygon geometry")

class BuildingResponse(BaseModel):
    building_id: int
    parcel_id: int
    total_floors: int
    footprint: Optional[Dict[str, Any]] = None

@router.post("/{parcel_id}", response_model=BuildingResponse, status_code=status.HTTP_201_CREATED)
def create_building_on_parcel(
    parcel_id: int,
    payload: BuildingCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "surveyor"]))
):
    """
    POST /buildings/{parcel_id}
    Adds a new building with footprint polygon and total floor count on a parcel.
    Restricted to admin and surveyor roles.
    """
    parcel = db.query(Parcel).filter(Parcel.parcel_id == parcel_id).first()
    if not parcel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Parcel {parcel_id} not found")

    if payload.footprint_wkt:
        wkt_str = payload.footprint_wkt
    elif payload.footprint_geojson:
        poly = shape(payload.footprint_geojson)
        wkt_str = poly.wkt
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Must provide footprint_wkt or footprint_geojson")

    try:
        # Sync building sequence
        db.execute(text("SELECT setval('buildings_building_id_seq', COALESCE((SELECT MAX(building_id) FROM buildings), 1));"))
        insert_stmt = text("""
            INSERT INTO buildings (parcel_id, footprint_geom, total_floors)
            VALUES (:pid, ST_GeomFromText(:wkt, 4326), :floors)
            RETURNING building_id, parcel_id, total_floors, ST_AsGeoJSON(footprint_geom) AS geojson;
        """)
        res = db.execute(insert_stmt, {"pid": parcel_id, "wkt": wkt_str, "floors": payload.total_floors}).fetchone()
        db.commit()
        return BuildingResponse(
            building_id=res[0],
            parcel_id=res[1],
            total_floors=res[2],
            footprint=json.loads(res[3]) if res[3] else None
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Database error: {str(e)}")

@router.get("/{parcel_id}", response_model=List[BuildingResponse])
def list_buildings_by_parcel(
    parcel_id: int,
    db: Session = Depends(get_db)
):
    """
    GET /buildings/{parcel_id}
    Retrieves all buildings belonging to a parcel.
    """
    stmt = text("SELECT building_id, parcel_id, total_floors, ST_AsGeoJSON(footprint_geom) AS geojson FROM buildings WHERE parcel_id = :pid ORDER BY building_id;")
    rows = db.execute(stmt, {"pid": parcel_id}).fetchall()
    return [
        BuildingResponse(
            building_id=r[0],
            parcel_id=r[1],
            total_floors=r[2],
            footprint=json.loads(r[3]) if r[3] else None
        )
        for r in rows
    ]
