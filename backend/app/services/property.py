from sqlalchemy.orm import Session
from app.models.entities import Property, Parcel, Building
from app.schemas.property import PropertyCreate
from app.services.ulpin import generate_3d_ulpin

def create_property(db: Session, prop_data: PropertyCreate) -> Property:
    """
    Creates a new Property record.
    Forces automatic calculation of ulpin_3d via generate_3d_ulpin().
    Overwrites/prevents any manual assignment of ulpin_3d.
    """
    # 1. Obtain 2D ULPIN of parent parcel
    parcel = db.query(Parcel).filter(Parcel.parcel_id == prop_data.parcel_id).first()
    if not parcel:
        raise ValueError(f"Parent Parcel with ID {prop_data.parcel_id} not found.")

    # 2. Automatically generate 3D ULPIN
    auto_ulpin_3d = generate_3d_ulpin(
        ulpin_2d=parcel.ulpin_2d,
        building_idx=prop_data.building_idx,
        floor_num=prop_data.floor_number,
        unit_idx=prop_data.unit_index
    )

    # 3. Instantiate Property with auto-populated ulpin_3d
    new_property = Property(
        ulpin_3d=auto_ulpin_3d,
        building_id=prop_data.building_id,
        parcel_id=prop_data.parcel_id,
        owner_id=prop_data.owner_id,
        floor_number=prop_data.floor_number,
        unit_index=prop_data.unit_index,
        elevation_min_m=prop_data.elevation_min_m,
        elevation_max_m=prop_data.elevation_max_m,
        area_sqm=prop_data.area_sqm,
        verification_status="unverified"
    )

    db.add(new_property)
    db.commit()
    db.refresh(new_property)
    return new_property
