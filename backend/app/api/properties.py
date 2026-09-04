from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
import json
from app.db import get_db
from app.models.entities import Property, Building, Parcel, Owner, User
from app.schemas.property import PropertyResponse
from app.services.segmentation import segment_building_footprint_to_properties
from app.core.auth import require_roles

router = APIRouter(prefix="/properties", tags=["Properties"])

class GeneratePropertiesRequest(BaseModel):
    building_id: int = Field(..., description="Target building ID for 3D segmentation")
    floor_height: float = Field(default=3.0, gt=0, description="Configurable floor-to-floor height in meters (default 3.0m)")
    base_elevation: float = Field(default=0.0, description="Base ground elevation in meters")
    building_idx: int = Field(default=1, ge=1, description="Building index within parcel (for B01, B02...)")
    owner_id: Optional[int] = Field(default=None, description="Optional default owner ID")
    force: bool = Field(default=False, description="Set True to override safeguard when building contains conflict properties")

class PropertyDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    property_id: int
    ulpin_3d: str
    building_id: int
    parcel_id: int
    floor_number: int
    unit_index: int
    elevation_min_m: float
    elevation_max_m: float
    area_sqm: float
    verification_status: str
    owner: Optional[Dict[str, Any]] = None
    footprint: Optional[Dict[str, Any]] = None
    volume_wkt: Optional[str] = None

@router.post("/generate", response_model=List[PropertyResponse], status_code=status.HTTP_201_CREATED)
def generate_building_3d_properties(
    payload: GeneratePropertiesRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "surveyor"]))
):
    """
    POST /properties/generate
    Triggers automatic 3D footprint-to-volume segmentation for a building.
    Generates one Property record per floor with extruded 3D volume geometry.
    Safeguard: Refuses to overwrite conflict properties unless force=True.
    Restricted to admin and surveyor roles.
    """
    try:
        properties = segment_building_footprint_to_properties(
            db=db,
            building_id=payload.building_id,
            floor_height=payload.floor_height,
            base_elevation=payload.base_elevation,
            building_idx=payload.building_idx,
            owner_id=payload.owner_id,
            force=payload.force
        )
        return properties
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(err))
    except Exception as err:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"3D Segmentation error: {str(err)}")

@router.get("/{ulpin_3d}", response_model=PropertyDetailResponse)
def get_property_by_ulpin(
    ulpin_3d: str,
    db: Session = Depends(get_db)
):
    """
    GET /properties/{ulpin_3d}
    Fetches full 3D property details, geometry, owner information, and verification status.
    """
    stmt = text("""
        SELECT 
            p.property_id, p.ulpin_3d, p.building_id, p.parcel_id, p.floor_number, p.unit_index,
            p.elevation_min_m, p.elevation_max_m, p.area_sqm, p.verification_status,
            o.owner_id, o.name AS owner_name, o.contact_info,
            ST_AsGeoJSON(p.footprint_geom) AS footprint_geojson,
            ST_AsText(p.volume_geom) AS volume_wkt
        FROM properties p
        LEFT JOIN owners o ON p.owner_id = o.owner_id
        WHERE p.ulpin_3d = :ulpin;
    """)
    row = db.execute(stmt, {"ulpin": ulpin_3d}).fetchone()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Property with 3D ULPIN '{ulpin_3d}' not found")

    owner_data = None
    if row.owner_id:
        owner_data = {
            "owner_id": row.owner_id,
            "name": row.owner_name,
            "contact_info": row.contact_info
        }

    return PropertyDetailResponse(
        property_id=row.property_id,
        ulpin_3d=row.ulpin_3d,
        building_id=row.building_id,
        parcel_id=row.parcel_id,
        floor_number=row.floor_number,
        unit_index=row.unit_index,
        elevation_min_m=row.elevation_min_m,
        elevation_max_m=row.elevation_max_m,
        area_sqm=row.area_sqm,
        verification_status=row.verification_status,
        owner=owner_data,
        footprint=json.loads(row.footprint_geojson) if row.footprint_geojson else None,
        volume_wkt=row.volume_wkt
    )
