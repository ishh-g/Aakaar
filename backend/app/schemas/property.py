from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

class PropertyCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    parcel_id: int = Field(..., description="Foreign key to parent Parcel")
    building_id: int = Field(..., description="Foreign key to parent Building")
    building_idx: int = Field(default=1, ge=1, description="Building index within parcel for 3D ULPIN (B01, B02...)")
    floor_number: int = Field(default=0, description="Floor number (negative for basements)")
    unit_index: int = Field(default=1, ge=1, description="Unit index on floor (U01, U02...)")
    elevation_min_m: float = Field(..., description="Minimum elevation in meters")
    elevation_max_m: float = Field(..., description="Maximum elevation in meters")
    area_sqm: float = Field(..., description="Recorded area in square meters")
    owner_id: Optional[int] = Field(default=None, description="Optional foreign key to Owner")
    footprint_wkt: Optional[str] = Field(default=None, description="Optional footprint polygon in WKT format")

class PropertyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    property_id: int
    ulpin_3d: str
    building_id: int
    parcel_id: int
    owner_id: Optional[int]
    floor_number: int
    unit_index: int
    elevation_min_m: float
    elevation_max_m: float
    area_sqm: float
    verification_status: str
