from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from shapely.geometry import Polygon
from shapely.wkt import loads as wkt_loads
from app.models.entities import Property, Building, Parcel
from app.services.ulpin import generate_3d_ulpin
from app.services.geometry import extrude_footprint_to_polyhedral_surface

def sync_property_sequence(db: Session):
    """Sync properties_property_id_seq sequence with current max property_id in DB."""
    db.execute(text("SELECT setval('properties_property_id_seq', COALESCE((SELECT MAX(property_id) FROM properties), 1));"))
    db.commit()

def segment_building_footprint_to_properties(
    db: Session,
    building_id: int,
    floor_height: float = 3.0,
    base_elevation: float = 0.0,
    building_idx: int = 1,
    owner_id: Optional[int] = None,
    force: bool = False
) -> List[Property]:
    """
    Automatic 3D Segmentation (footprint -> volume) per Section 5 of Technical Build Spec.

    Safeguard: Refuses to overwrite properties with verification_status='conflict' unless force=True.
    """
    # 1. Fetch Building and parent Parcel
    building = db.query(Building).filter(Building.building_id == building_id).first()
    if not building:
        raise ValueError(f"Building with ID {building_id} not found.")

    parcel = db.query(Parcel).filter(Parcel.parcel_id == building.parcel_id).first()
    if not parcel:
        raise ValueError(f"Parent Parcel with ID {building.parcel_id} not found.")

    # 2. Conflict Safeguard: Check if building contains conflict properties
    conflict_props = db.query(Property).filter(
        Property.building_id == building_id,
        Property.verification_status == "conflict"
    ).all()

    if conflict_props and not force:
        conflict_ids = [p.property_id for p in conflict_props]
        raise ValueError(
            f"Building {building_id} contains active spatial conflict properties "
            f"(Property IDs: {conflict_ids}). Segmentation aborted to protect conflict test data. "
            f"Set force=True to override."
        )

    sync_property_sequence(db)

    # 3. Fetch footprint geometry WKT from PostGIS or Shapely ORM
    footprint_wkt_res = db.execute(
        text("SELECT ST_AsText(footprint_geom) FROM buildings WHERE building_id = :b_id"),
        {"b_id": building_id}
    ).fetchone()

    if not footprint_wkt_res or not footprint_wkt_res[0]:
        raise ValueError(f"Building {building_id} does not have a valid footprint_geom.")

    footprint_wkt = footprint_wkt_res[0]
    footprint_poly = wkt_loads(footprint_wkt)
    
    # Calculate area using PostGIS ST_Area
    area_res = db.execute(
        text("SELECT ST_Area(ST_Transform(footprint_geom, 3857)) FROM buildings WHERE building_id = :b_id"),
        {"b_id": building_id}
    ).fetchone()
    
    area_sqm = area_res[0] if area_res and area_res[0] else footprint_poly.area

    created_properties = []

    # 4. Iterate over each floor to generate 3D volume property
    for i in range(building.total_floors):
        elev_min = base_elevation + i * floor_height
        elev_max = elev_min + floor_height

        # Extrude 2D footprint into 3D PolyhedralSurfaceZ prism WKT
        volume_wkt = extrude_footprint_to_polyhedral_surface(
            footprint=footprint_poly,
            elevation_min=elev_min,
            elevation_max=elev_max
        )

        # Generate 3D ULPIN
        auto_ulpin_3d = generate_3d_ulpin(
            ulpin_2d=parcel.ulpin_2d,
            building_idx=building_idx,
            floor_num=i,
            unit_idx=1
        )

        # Insert/Update Property with UPSERT
        upsert_stmt = text("""
            INSERT INTO properties (
                ulpin_3d, building_id, parcel_id, owner_id, floor_number, unit_index,
                elevation_min_m, elevation_max_m, footprint_geom, volume_geom, area_sqm, verification_status
            )
            VALUES (
                :ulpin_3d, :building_id, :parcel_id, :owner_id, :floor_number, :unit_index,
                :elevation_min_m, :elevation_max_m, ST_GeomFromText(:footprint_wkt, 4326), ST_GeomFromText(:volume_wkt, 4326), :area_sqm, 'unverified'
            )
            ON CONFLICT (parcel_id, building_id, floor_number, unit_index) DO UPDATE SET
                ulpin_3d = EXCLUDED.ulpin_3d,
                elevation_min_m = EXCLUDED.elevation_min_m,
                elevation_max_m = EXCLUDED.elevation_max_m,
                footprint_geom = EXCLUDED.footprint_geom,
                volume_geom = EXCLUDED.volume_geom,
                area_sqm = EXCLUDED.area_sqm
            RETURNING property_id;
        """)

        res = db.execute(upsert_stmt, {
            "ulpin_3d": auto_ulpin_3d,
            "building_id": building.building_id,
            "parcel_id": building.parcel_id,
            "owner_id": owner_id,
            "floor_number": i,
            "unit_index": 1,
            "elevation_min_m": elev_min,
            "elevation_max_m": elev_max,
            "footprint_wkt": footprint_wkt,
            "volume_wkt": volume_wkt,
            "area_sqm": area_sqm
        })
        
        prop_id = res.fetchone()[0]
        
        # Retrieve created/updated property ORM object
        prop = db.query(Property).filter(Property.property_id == prop_id).first()
        created_properties.append(prop)

    db.commit()

    # 5. Run automatic conflict validation pass over the newly generated properties
    from app.services.conflicts import run_all_conflict_checks
    run_all_conflict_checks(db, building_id=building_id)

    # Refresh status on created properties
    for prop in created_properties:
        db.refresh(prop)

    return created_properties
