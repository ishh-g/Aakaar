from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Dict, Any, Optional
from app.models.entities import Property, ConflictLog

def check_property_overlap(db: Session, property_id: int) -> List[Dict[str, Any]]:
    """
    Check 1: Property overlap
    Detects 3D volumetric overlap between any two properties not in an explicit parent-child relation.
    Requires intersecting footprint AND overlapping vertical elevation ranges (excluding touching boundaries).
    """
    stmt = text("""
        SELECT p2.property_id
        FROM properties p1
        JOIN properties p2 ON p1.property_id != p2.property_id
        WHERE p1.property_id = :prop_id
          AND p1.property_id < p2.property_id
          AND ST_Intersects(p1.footprint_geom, p2.footprint_geom)
          AND NOT ST_Touches(p1.footprint_geom, p2.footprint_geom)
          AND p1.elevation_min_m < (p2.elevation_max_m - 0.01)
          AND p1.elevation_max_m > (p2.elevation_min_m + 0.01);
    """)
    rows = db.execute(stmt, {"prop_id": property_id}).fetchall()
    conflicts = []
    for r in rows:
        conflicts.append({
            "property_id_a": property_id,
            "property_id_b": r[0],
            "conflict_type": "overlap"
        })
    return conflicts

def check_boundary_violation(db: Session, property_id: int) -> Optional[Dict[str, Any]]:
    """
    Check 2: Boundary violation
    Detects if the parent building footprint is NOT completely contained within the parcel boundary:
    NOT ST_Contains(parcel.boundary_geom, building.footprint_geom).
    """
    stmt = text("""
        SELECT b.building_id, par.parcel_id
        FROM properties prop
        JOIN buildings b ON prop.building_id = b.building_id
        JOIN parcels par ON prop.parcel_id = par.parcel_id
        WHERE prop.property_id = :prop_id
          AND NOT ST_Contains(par.boundary_geom, b.footprint_geom);
    """)
    row = db.execute(stmt, {"prop_id": property_id}).fetchone()
    if row:
        return {
            "property_id_a": property_id,
            "property_id_b": None,
            "conflict_type": "boundary_violation"
        }
    return None

def check_floor_overlap(db: Session, property_id: int) -> List[Dict[str, Any]]:
    """
    Check 3: Floor overlap
    Two properties in the same building with overlapping [elevation_min, elevation_max] ranges.
    """
    stmt = text("""
        SELECT p2.property_id
        FROM properties p1
        JOIN properties p2 ON p1.building_id = p2.building_id AND p1.property_id != p2.property_id
        WHERE p1.property_id = :prop_id
          AND p1.property_id < p2.property_id
          AND ST_Intersects(p1.footprint_geom, p2.footprint_geom)
          AND p1.elevation_min_m < (p2.elevation_max_m - 0.01)
          AND p1.elevation_max_m > (p2.elevation_min_m + 0.01);
    """)
    rows = db.execute(stmt, {"prop_id": property_id}).fetchall()
    conflicts = []
    for r in rows:
        conflicts.append({
            "property_id_a": property_id,
            "property_id_b": r[0],
            "conflict_type": "floor_overlap"
        })
    return conflicts

def check_building_parcel_mismatch(db: Session, property_id: int) -> Optional[Dict[str, Any]]:
    """
    Check 4: Building-parcel mismatch
    ST_Overlaps or ST_Disjoint between building footprint and parcel boundary.
    """
    stmt = text("""
        SELECT b.building_id
        FROM properties prop
        JOIN buildings b ON prop.building_id = b.building_id
        JOIN parcels par ON prop.parcel_id = par.parcel_id
        WHERE prop.property_id = :prop_id
          AND (ST_Overlaps(b.footprint_geom, par.boundary_geom) OR ST_Disjoint(b.footprint_geom, par.boundary_geom));
    """)
    row = db.execute(stmt, {"prop_id": property_id}).fetchone()
    if row:
        return {
            "property_id_a": property_id,
            "property_id_b": None,
            "conflict_type": "building_parcel_mismatch"
        }
    return None

def check_area_mismatch(db: Session, property_id: int, tolerance: float = 0.05) -> Optional[Dict[str, Any]]:
    """
    Check 5: Area mismatch
    abs(recorded_area - ST_Area(footprint_geom::geography)) / ST_Area(footprint_geom::geography) > tolerance (default 5%).
    """
    stmt = text("""
        SELECT 
            prop.area_sqm AS recorded_area,
            ST_Area(prop.footprint_geom::geography) AS computed_area
        FROM properties prop
        WHERE prop.property_id = :prop_id;
    """)
    row = db.execute(stmt, {"prop_id": property_id}).fetchone()
    if row and row.computed_area and row.computed_area > 0:
        recorded = row.recorded_area
        computed = row.computed_area
        diff_ratio = abs(recorded - computed) / computed
        if diff_ratio > tolerance:
            return {
                "property_id_a": property_id,
                "property_id_b": None,
                "conflict_type": "area_mismatch"
            }
    return None

def check_elevation_conflict(db: Session, property_id: int, expected_height: float = 3.0, tolerance: float = 0.05) -> Optional[Dict[str, Any]]:
    """
    Check 6: Elevation/height conflict
    Recorded floor height vs elevation_max - elevation_min differs beyond tolerance or inverted.
    """
    stmt = text("""
        SELECT elevation_min_m, elevation_max_m
        FROM properties
        WHERE property_id = :prop_id;
    """)
    row = db.execute(stmt, {"prop_id": property_id}).fetchone()
    if row:
        elev_min = row.elevation_min_m
        elev_max = row.elevation_max_m
        actual_height = elev_max - elev_min
        if actual_height <= 0 or abs(actual_height - expected_height) > tolerance:
            return {
                "property_id_a": property_id,
                "property_id_b": None,
                "conflict_type": "elevation_conflict"
            }
    return None

def check_duplicate_property(db: Session, property_id: int) -> List[Dict[str, Any]]:
    """
    Check 7: Duplicate property
    Two properties with ST_Equals footprint geometry AND overlapping elevation range.
    """
    stmt = text("""
        SELECT p2.property_id
        FROM properties p1
        JOIN properties p2 ON p1.property_id != p2.property_id
        WHERE p1.property_id = :prop_id
          AND p1.property_id < p2.property_id
          AND ST_Equals(p1.footprint_geom, p2.footprint_geom)
          AND p1.elevation_min_m < (p2.elevation_max_m - 0.01)
          AND p1.elevation_max_m > (p2.elevation_min_m + 0.01);
    """)
    rows = db.execute(stmt, {"prop_id": property_id}).fetchall()
    conflicts = []
    for r in rows:
        conflicts.append({
            "property_id_a": property_id,
            "property_id_b": r[0],
            "conflict_type": "duplicate"
        })
    return conflicts

def run_conflict_checks_for_property(db: Session, property_id: int) -> List[Dict[str, Any]]:
    """
    Runs all 7 checks for a single property and returns detected conflict dictionaries.
    """
    detected = []

    # 1. Property overlap
    detected.extend(check_property_overlap(db, property_id))

    # 2. Boundary violation
    if (c := check_boundary_violation(db, property_id)):
        detected.append(c)

    # 3. Floor overlap
    detected.extend(check_floor_overlap(db, property_id))

    # 4. Building-parcel mismatch
    if (c := check_building_parcel_mismatch(db, property_id)):
        detected.append(c)

    # 5. Area mismatch
    if (c := check_area_mismatch(db, property_id)):
        detected.append(c)

    # 6. Elevation conflict
    if (c := check_elevation_conflict(db, property_id)):
        detected.append(c)

    # 7. Duplicate property
    detected.extend(check_duplicate_property(db, property_id))

    return detected

def run_all_conflict_checks(db: Session, building_id: Optional[int] = None) -> Dict[str, Any]:
    """
    Orchestrates spatial conflict detection across properties.
    Writes new ConflictLog rows and updates verification_status:
    - Sets verification_status to 'conflict' on affected properties.
    - Sets verification_status to 'verified' on properties with 0 conflicts.
    """
    # 1. Fetch properties in scope
    query = db.query(Property)
    if building_id is not None:
        query = query.filter(Property.building_id == building_id)
    properties = query.all()

    all_detected_conflicts: List[Dict[str, Any]] = []
    conflicted_prop_ids = set()

    for prop in properties:
        prop_conflicts = run_conflict_checks_for_property(db, prop.property_id)
        if prop_conflicts:
            all_detected_conflicts.extend(prop_conflicts)
            conflicted_prop_ids.add(prop.property_id)
            for c in prop_conflicts:
                if c.get("property_id_b"):
                    conflicted_prop_ids.add(c["property_id_b"])

    # 2. Write new ConflictLogs to DB (preventing duplicate unresolved log entries)
    created_count = 0
    for c in all_detected_conflicts:
        prop_a = c["property_id_a"]
        prop_b = c.get("property_id_b")
        c_type = c["conflict_type"]

        # Check if identical open conflict already exists
        existing_log_stmt = text("""
            SELECT conflict_id FROM conflict_logs
            WHERE property_id_a = :pa 
              AND (property_id_b = :pb OR (:pb IS NULL AND property_id_b IS NULL))
              AND conflict_type = CAST(:ctype AS conflict_type)
              AND resolved = FALSE;
        """)
        exists = db.execute(existing_log_stmt, {"pa": prop_a, "pb": prop_b, "ctype": c_type}).fetchone()
        if not exists:
            insert_stmt = text("""
                INSERT INTO conflict_logs (property_id_a, property_id_b, conflict_type, resolved)
                VALUES (:pa, :pb, CAST(:ctype AS conflict_type), FALSE);
            """)
            db.execute(insert_stmt, {"pa": prop_a, "pb": prop_b, "ctype": c_type})
            created_count += 1

    # 3. Update verification_status on properties in scope
    for prop in properties:
        if prop.property_id in conflicted_prop_ids:
            prop.verification_status = "conflict"
        else:
            prop.verification_status = "verified"

    db.commit()

    return {
        "properties_checked": len(properties),
        "conflicts_detected": len(all_detected_conflicts),
        "conflict_logs_created": created_count,
        "conflicted_property_ids": sorted(list(conflicted_prop_ids))
    }
