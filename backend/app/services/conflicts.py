from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Dict, Any, Optional, Tuple
from app.models.entities import Property, ConflictLog

# Conflict types that involve two properties and therefore have a measurable
# 3D overlap volume. All other types (boundary_violation, area_mismatch, ...)
# report null severity.
SEVERITY_CONFLICT_TYPES = frozenset({"overlap", "floor_overlap", "duplicate"})


def calculate_overlap_severity(
    overlap_area_m2: Optional[float],
    overlap_height_m: Optional[float],
    volume_a_m3: Optional[float],
    volume_b_m3: Optional[float],
) -> Tuple[Optional[float], Optional[float]]:
    """
    Convert raw geometric metrics into (overlap_volume_m3, overlap_pct).

    overlap_volume_m3 = footprint intersection area * overlapping height
    overlap_pct       = overlap_volume_m3 / smaller property volume * 100

    Returns (None, None) when there is no genuine 3D overlap (touching
    boundaries, disjoint footprints, or non-overlapping elevation ranges) or
    when either property is missing/has invalid dimensions.
    """
    try:
        if overlap_area_m2 is None or overlap_height_m is None:
            return (None, None)

        area_m2 = float(overlap_area_m2)
        height_m = float(overlap_height_m)
        if area_m2 <= 0.0 or height_m <= 0.0:
            return (None, None)

        if (
            volume_a_m3 is None
            or volume_b_m3 is None
            or float(volume_a_m3) <= 0.0
            or float(volume_b_m3) <= 0.0
        ):
            return (None, None)

        smaller_volume_m3 = min(float(volume_a_m3), float(volume_b_m3))
        overlap_volume_m3 = area_m2 * height_m
        overlap_pct = (overlap_volume_m3 / smaller_volume_m3) * 100.0

        return (round(overlap_volume_m3, 2), round(overlap_pct, 2))
    except (TypeError, ValueError, ZeroDivisionError):
        # Malformed numeric data must never take the conflicts endpoint down.
        return (None, None)


def get_unresolved_conflicts_with_severity(db: Session) -> List[Dict[str, Any]]:
    """
    Fetch every unresolved conflict log together with its overlap severity.

    One query computes, per log:
      - intersection area of both footprints as true ground area
        (PostGIS geography -> square metres on the WGS84 ellipsoid, so no
        Web-Mercator distortion at Delhi's latitude),
      - the height of the overlapping elevation band,
      - both properties' full volumes (true ground area * height).

    LEFT JOINs are deliberate: a conflict row whose property no longer exists
    yields NULL metrics and therefore null severity instead of a 500.
    Severity is only calculated for two-property conflict types.
    """
    stmt = text("""
        SELECT
            cl.conflict_id,
            cl.property_id_a,
            cl.property_id_b,
            cl.conflict_type,
            cl.detected_at,
            cl.resolved,
            CASE
                WHEN cl.conflict_type NOT IN ('overlap', 'floor_overlap', 'duplicate')
                     OR cl.property_id_b IS NULL
                     OR p1.property_id IS NULL
                     OR p2.property_id IS NULL
                THEN NULL
                ELSE ST_Area(
                    ST_Intersection(p1.footprint_geom, p2.footprint_geom)::geography
                )
            END AS overlap_area_m2,
            CASE
                WHEN cl.conflict_type NOT IN ('overlap', 'floor_overlap', 'duplicate')
                     OR cl.property_id_b IS NULL
                     OR p1.property_id IS NULL
                     OR p2.property_id IS NULL
                THEN NULL
                ELSE GREATEST(
                    0.0,
                    LEAST(p1.elevation_max_m, p2.elevation_max_m)
                    - GREATEST(p1.elevation_min_m, p2.elevation_min_m)
                )
            END AS overlap_height_m,
            ST_Area(p1.footprint_geom::geography)
                * (p1.elevation_max_m - p1.elevation_min_m) AS volume_a_m3,
            ST_Area(p2.footprint_geom::geography)
                * (p2.elevation_max_m - p2.elevation_min_m) AS volume_b_m3
        FROM conflict_logs cl
        LEFT JOIN properties p1 ON p1.property_id = cl.property_id_a
        LEFT JOIN properties p2 ON p2.property_id = cl.property_id_b
        WHERE cl.resolved = FALSE
        ORDER BY cl.conflict_id ASC;
    """)

    rows = db.execute(stmt).fetchall()
    enriched: List[Dict[str, Any]] = []

    for row in rows:
        overlap_volume_m3: Optional[float] = None
        overlap_pct: Optional[float] = None

        if row.conflict_type in SEVERITY_CONFLICT_TYPES:
            overlap_volume_m3, overlap_pct = calculate_overlap_severity(
                overlap_area_m2=row.overlap_area_m2,
                overlap_height_m=row.overlap_height_m,
                volume_a_m3=row.volume_a_m3,
                volume_b_m3=row.volume_b_m3,
            )

        enriched.append({
            "conflict_id": row.conflict_id,
            "property_id_a": row.property_id_a,
            "property_id_b": row.property_id_b,
            "conflict_type": row.conflict_type,
            "detected_at": row.detected_at,
            "resolved": row.resolved,
            "overlap_volume_m3": overlap_volume_m3,
            "overlap_pct": overlap_pct,
        })

    return enriched


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
