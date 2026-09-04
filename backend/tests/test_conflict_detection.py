import pytest
from unittest.mock import MagicMock
from app.services.conflicts import (
    check_property_overlap,
    check_boundary_violation,
    check_floor_overlap,
    check_building_parcel_mismatch,
    check_area_mismatch,
    check_elevation_conflict,
    check_duplicate_property,
    run_conflict_checks_for_property,
    run_all_conflict_checks
)
from app.models.entities import Property, Building, Parcel, ConflictLog

def test_check_property_overlap():
    """Test Check 1: 3D volume or vertical prism overlap between two properties"""
    mock_db = MagicMock()
    # Mock row returned by DB query: property_id_b = 16
    mock_db.execute.return_value.fetchall.return_value = [(16,)]
    
    conflicts = check_property_overlap(mock_db, property_id=15)
    assert len(conflicts) == 1
    assert conflicts[0]["conflict_type"] == "overlap"
    assert conflicts[0]["property_id_a"] == 15
    assert conflicts[0]["property_id_b"] == 16

def test_check_boundary_violation():
    """Test Check 2: Building footprint extending outside parcel boundary"""
    mock_db = MagicMock()
    mock_db.execute.return_value.fetchone.return_value = (3, 3) # building 3, parcel 3
    
    conflict = check_boundary_violation(mock_db, property_id=8)
    assert conflict is not None
    assert conflict["conflict_type"] == "boundary_violation"
    assert conflict["property_id_a"] == 8
    assert conflict["property_id_b"] is None

def test_check_floor_overlap():
    """Test Check 3: Two properties in same building with overlapping floor elevation ranges"""
    mock_db = MagicMock()
    mock_db.execute.return_value.fetchall.return_value = [(16,)]
    
    conflicts = check_floor_overlap(mock_db, property_id=15)
    assert len(conflicts) == 1
    assert conflicts[0]["conflict_type"] == "floor_overlap"

def test_check_building_parcel_mismatch():
    """Test Check 4: ST_Overlaps or ST_Disjoint between building footprint and parcel"""
    mock_db = MagicMock()
    mock_db.execute.return_value.fetchone.return_value = (3,)
    
    conflict = check_building_parcel_mismatch(mock_db, property_id=8)
    assert conflict is not None
    assert conflict["conflict_type"] == "building_parcel_mismatch"

def test_check_area_mismatch():
    """Test Check 5: Area mismatch > 5% tolerance"""
    mock_db = MagicMock()
    # Mock row: recorded 500 sqm, computed 300 sqm (diff ratio > 0.05)
    mock_row = MagicMock()
    mock_row.recorded_area = 500.0
    mock_row.computed_area = 300.0
    mock_db.execute.return_value.fetchone.return_value = mock_row
    
    conflict = check_area_mismatch(mock_db, property_id=1, tolerance=0.05)
    assert conflict is not None
    assert conflict["conflict_type"] == "area_mismatch"

def test_check_elevation_conflict():
    """Test Check 6: Elevation height mismatch (e.g. 1.0m actual vs 3.0m expected)"""
    mock_db = MagicMock()
    mock_row = MagicMock()
    mock_row.elevation_min_m = 0.0
    mock_row.elevation_max_m = 1.0  # only 1.0m height when 3.0m expected
    mock_db.execute.return_value.fetchone.return_value = mock_row
    
    conflict = check_elevation_conflict(mock_db, property_id=1, expected_height=3.0, tolerance=0.05)
    assert conflict is not None
    assert conflict["conflict_type"] == "elevation_conflict"

def test_check_duplicate_property():
    """Test Check 7: ST_Equals footprint and identical/overlapping elevation"""
    mock_db = MagicMock()
    mock_db.execute.return_value.fetchall.return_value = [(20,)]
    
    conflicts = check_duplicate_property(mock_db, property_id=1)
    assert len(conflicts) == 1
    assert conflicts[0]["conflict_type"] == "duplicate"
    assert conflicts[0]["property_id_b"] == 20

def test_run_conflict_checks_for_property_all_pass():
    """Test when no conflicts exist, returns empty list"""
    mock_db = MagicMock()
    mock_db.execute.return_value.fetchall.return_value = []
    mock_db.execute.return_value.fetchone.return_value = None
    
    conflicts = run_conflict_checks_for_property(mock_db, property_id=1)
    assert conflicts == []

def test_run_all_conflict_checks_integration_building3_and_building5():
    """Integration test checking full detection run against Building 3 (boundary violation) and Building 5 (3D overlap)"""
    mock_db = MagicMock()
    
    prop8 = Property(property_id=8, building_id=3, parcel_id=3, verification_status="unverified")
    prop9 = Property(property_id=9, building_id=3, parcel_id=3, verification_status="unverified")
    prop15 = Property(property_id=15, building_id=5, parcel_id=5, verification_status="unverified")
    prop16 = Property(property_id=16, building_id=5, parcel_id=5, verification_status="unverified")
    prop1 = Property(property_id=1, building_id=1, parcel_id=1, verification_status="unverified")
    
    mock_db.query.return_value.all.return_value = [prop1, prop8, prop9, prop15, prop16]
    
    # Mock checks returning boundary violation for 8, 9, and overlap for 15, 16
    def mock_run_checks(db, prop_id):
        if prop_id in (8, 9):
            return [{"property_id_a": prop_id, "property_id_b": None, "conflict_type": "boundary_violation"}]
        elif prop_id == 15:
            return [{"property_id_a": 15, "property_id_b": 16, "conflict_type": "overlap"}]
        return []

    from app.services import conflicts
    original_fn = conflicts.run_conflict_checks_for_property
    conflicts.run_conflict_checks_for_property = mock_run_checks
    try:
        mock_db.execute.return_value.fetchone.return_value = None # No existing log
        res = run_all_conflict_checks(mock_db)
        assert res["conflicts_detected"] == 3
        assert 8 in res["conflicted_property_ids"]
        assert 9 in res["conflicted_property_ids"]
        assert 15 in res["conflicted_property_ids"]
        assert 16 in res["conflicted_property_ids"]
        assert 1 not in res["conflicted_property_ids"]
        assert prop1.verification_status == "verified"
        assert prop8.verification_status == "conflict"
        assert prop15.verification_status == "conflict"
    finally:
        conflicts.run_conflict_checks_for_property = original_fn
