from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import json
from shapely.geometry import shape
from app.db import get_db
from app.models.entities import Parcel, User
from app.core.auth import require_roles

router = APIRouter(prefix="/parcels", tags=["Parcels"])

class ParcelCreateRequest(BaseModel):
    ulpin_2d: str = Field(..., max_length=14, description="14-character 2D ULPIN")
    boundary_wkt: Optional[str] = Field(default=None, description="WKT string e.g. POLYGON((...))")
    boundary_geojson: Optional[Dict[str, Any]] = Field(default=None, description="GeoJSON polygon geometry")

@router.post("/upload", status_code=status.HTTP_201_CREATED)
def upload_parcel(
    payload: ParcelCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "surveyor"]))
):
    """
    POST /parcels/upload
    Uploads parcel boundary in WKT or GeoJSON format.
    Restricted to admin and surveyor roles.
    """
    if payload.boundary_wkt:
        wkt_str = payload.boundary_wkt
    elif payload.boundary_geojson:
        poly = shape(payload.boundary_geojson)
        wkt_str = poly.wkt
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Must provide boundary_wkt or boundary_geojson")

    try:
        # Sync sequence
        db.execute(text("SELECT setval('parcels_parcel_id_seq', COALESCE((SELECT MAX(parcel_id) FROM parcels), 1));"))
        insert_stmt = text("""
            INSERT INTO parcels (ulpin_2d, boundary_geom, area_sqm)
            VALUES (:ulpin, ST_GeomFromText(:wkt, 4326), ST_Area(ST_GeomFromText(:wkt, 4326)::geography))
            ON CONFLICT (ulpin_2d) DO UPDATE SET
                boundary_geom = EXCLUDED.boundary_geom,
                area_sqm = EXCLUDED.area_sqm
            RETURNING parcel_id, ulpin_2d, area_sqm;
        """)
        res = db.execute(insert_stmt, {"ulpin": payload.ulpin_2d, "wkt": wkt_str}).fetchone()
        db.commit()
        return {"status": "success", "parcel": {"parcel_id": res[0], "ulpin_2d": res[1], "area_sqm": res[2]}}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Database error: {str(e)}")

@router.post("/upload/file", status_code=status.HTTP_201_CREATED)
async def upload_parcels_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "surveyor"]))
):
    """
    POST /parcels/upload/file
    Batch uploads GeoJSON FeatureCollection file of parcels.
    """
    try:
        content = await file.read()
        geojson_data = json.loads(content.decode("utf-8"))
        features = geojson_data.get("features", [geojson_data])
        created_parcels = []
        db.execute(text("SELECT setval('parcels_parcel_id_seq', COALESCE((SELECT MAX(parcel_id) FROM parcels), 1));"))

        for feat in features:
            geom = feat.get("geometry", feat)
            props = feat.get("properties", {})
            poly = shape(geom)
            ulpin_2d = props.get("ulpin_2d", f"DELHI{len(created_parcels)+1:08d}P")
            
            insert_stmt = text("""
                INSERT INTO parcels (ulpin_2d, boundary_geom, area_sqm)
                VALUES (:ulpin, ST_GeomFromText(:wkt, 4326), ST_Area(ST_GeomFromText(:wkt, 4326)::geography))
                ON CONFLICT (ulpin_2d) DO UPDATE SET
                    boundary_geom = EXCLUDED.boundary_geom,
                    area_sqm = EXCLUDED.area_sqm
                RETURNING parcel_id, ulpin_2d, area_sqm;
            """)
            res = db.execute(insert_stmt, {"ulpin": ulpin_2d, "wkt": poly.wkt}).fetchone()
            created_parcels.append({"parcel_id": res[0], "ulpin_2d": res[1], "area_sqm": res[2]})
        db.commit()
        return {"status": "success", "count": len(created_parcels), "parcels": created_parcels}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to parse GeoJSON file: {str(e)}")

@router.get("")
def list_parcels(db: Session = Depends(get_db)):
    """
    GET /parcels
    Lists all parcels with boundary GeoJSON/WKT.
    """
    stmt = text("SELECT parcel_id, ulpin_2d, area_sqm, ST_AsGeoJSON(boundary_geom) AS geojson FROM parcels ORDER BY parcel_id;")
    rows = db.execute(stmt).fetchall()
    return [{"parcel_id": r[0], "ulpin_2d": r[1], "area_sqm": r[2], "geometry": json.loads(r[3]) if r[3] else None} for r in rows]
