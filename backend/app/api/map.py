from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional, Dict, Any, List
import json
from app.db import get_db

router = APIRouter(prefix="/map", tags=["Map"])

@router.get("/tiles")
@router.get("/geojson")
def get_map_layers(
    layer: Optional[str] = Query(None, description="Filter by layer: 'parcels', 'buildings', 'properties'"),
    db: Session = Depends(get_db)
):
    """
    GET /map/tiles (or /map/geojson)
    Returns full GeoJSON feature collection for 3D Cesium viewer rendering:
    - 2D Parcel boundaries
    - 2D Building footprints
    - 3D Property extruded volume prisms / footprints with elevation tags and status.
    """
    features: List[Dict[str, Any]] = []

    # 1. Parcels Layer
    if layer in (None, "parcels"):
        p_stmt = text("""
            SELECT parcel_id, ulpin_2d, area_sqm, ST_AsGeoJSON(boundary_geom) AS geojson
            FROM parcels;
        """)
        for r in db.execute(p_stmt).fetchall():
            if r.geojson:
                features.append({
                    "type": "Feature",
                    "id": f"parcel_{r.parcel_id}",
                    "geometry": json.loads(r.geojson),
                    "properties": {
                        "layer": "parcel",
                        "parcel_id": r.parcel_id,
                        "ulpin_2d": r.ulpin_2d,
                        "area_sqm": r.area_sqm
                    }
                })

    # 2. Buildings Layer
    if layer in (None, "buildings"):
        b_stmt = text("""
            SELECT building_id, parcel_id, total_floors, ST_AsGeoJSON(footprint_geom) AS geojson
            FROM buildings;
        """)
        for r in db.execute(b_stmt).fetchall():
            if r.geojson:
                features.append({
                    "type": "Feature",
                    "id": f"building_{r.building_id}",
                    "geometry": json.loads(r.geojson),
                    "properties": {
                        "layer": "building",
                        "building_id": r.building_id,
                        "parcel_id": r.parcel_id,
                        "total_floors": r.total_floors
                    }
                })

    # 3. Properties Layer (with 3D elevation ranges and verification status)
    if layer in (None, "properties"):
        pr_stmt = text("""
            SELECT 
                property_id, ulpin_3d, building_id, parcel_id, floor_number, unit_index,
                elevation_min_m, elevation_max_m, area_sqm, verification_status,
                ST_AsGeoJSON(footprint_geom) AS geojson
            FROM properties;
        """)
        for r in db.execute(pr_stmt).fetchall():
            if r.geojson:
                features.append({
                    "type": "Feature",
                    "id": f"property_{r.property_id}",
                    "geometry": json.loads(r.geojson),
                    "properties": {
                        "layer": "property",
                        "property_id": r.property_id,
                        "ulpin_3d": r.ulpin_3d,
                        "building_id": r.building_id,
                        "parcel_id": r.parcel_id,
                        "floor_number": r.floor_number,
                        "unit_index": r.unit_index,
                        "elevation_min_m": r.elevation_min_m,
                        "elevation_max_m": r.elevation_max_m,
                        "area_sqm": r.area_sqm,
                        "verification_status": r.verification_status
                    }
                })

    return {
        "type": "FeatureCollection",
        "features": features
    }
