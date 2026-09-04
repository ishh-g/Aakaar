import pytest
from unittest.mock import MagicMock
from shapely.geometry import Polygon
from app.services.geometry import extrude_footprint_to_polyhedral_surface, parse_footprint_geometry
from app.services.segmentation import segment_building_footprint_to_properties
from app.models.entities import Building, Parcel, Property

def test_extrude_footprint_to_polyhedral_surface():
    """Test 3D extrusion of a square footprint polygon into PolyhedralSurfaceZ WKT"""
    footprint = Polygon([(0, 0), (10, 0), (10, 10), (0, 10), (0, 0)])
    
    # Extrude floor 0: elevation 0.0m to 3.0m
    wkt = extrude_footprint_to_polyhedral_surface(footprint, elevation_min=0.0, elevation_max=3.0)
    
    assert wkt.startswith("POLYHEDRALSURFACE Z")
    assert "0.0 0.0 0.0" in wkt
    assert "10.0 0.0 3.0" in wkt
    assert "0.0 10.0 3.0" in wkt

def test_extrude_invalid_elevations():
    """Test elevation_max <= elevation_min validation"""
    footprint = Polygon([(0, 0), (10, 0), (10, 10), (0, 10)])
    with pytest.raises(ValueError):
        extrude_footprint_to_polyhedral_surface(footprint, elevation_min=5.0, elevation_max=3.0)

def test_parse_footprint_geometry():
    """Test parsing WKT and GeoJSON into Shapely Polygon"""
    wkt_str = "POLYGON((0 0, 10 0, 10 10, 0 10, 0 0))"
    poly = parse_footprint_geometry(wkt_str)
    assert isinstance(poly, Polygon)
    assert poly.area == 100.0

def test_segmentation_safeguard_blocks_conflict_properties():
    """Test that segmentation aborts with ValueError if conflict properties exist and force=False"""
    mock_db = MagicMock()
    
    mock_building = Building(building_id=3, parcel_id=3, total_floors=3)
    mock_parcel = Parcel(parcel_id=3, ulpin_2d="DELHI110001P03", area_sqm=1500.0)
    conflict_prop = Property(property_id=8, building_id=3, parcel_id=3, ulpin_3d="DELHI110001P03-B01F00U01", verification_status="conflict")
    
    def mock_query(model):
        q = MagicMock()
        if model == Building:
            q.filter.return_value.first.return_value = mock_building
        elif model == Parcel:
            q.filter.return_value.first.return_value = mock_parcel
        elif model == Property:
            q.filter.return_value.all.return_value = [conflict_prop]
        return q

    mock_db.query.side_effect = mock_query
    
    with pytest.raises(ValueError) as exc_info:
        segment_building_footprint_to_properties(mock_db, building_id=3, force=False)
    
    assert "contains active spatial conflict properties" in str(exc_info.value)
    assert "force=True" in str(exc_info.value)

def test_segmentation_safeguard_bypassed_with_force(monkeypatch):
    """Test that segmentation proceeds when force=True even if conflict properties exist"""
    mock_db = MagicMock()
    
    mock_building = Building(building_id=3, parcel_id=3, total_floors=2)
    mock_parcel = Parcel(parcel_id=3, ulpin_2d="DELHI110001P03", area_sqm=1500.0)
    conflict_prop = Property(property_id=8, building_id=3, parcel_id=3, ulpin_3d="DELHI110001P03-B01F00U01", verification_status="conflict")
    
    created_prop_1 = Property(property_id=8, building_id=3, parcel_id=3, ulpin_3d="DELHI110001P03-B01F00U01", floor_number=0, verification_status="unverified")
    created_prop_2 = Property(property_id=9, building_id=3, parcel_id=3, ulpin_3d="DELHI110001P03-B01F01U01", floor_number=1, verification_status="unverified")
    
    def mock_query(model):
        q = MagicMock()
        if model == Building:
            q.filter.return_value.first.return_value = mock_building
        elif model == Parcel:
            q.filter.return_value.first.return_value = mock_parcel
        elif model == Property:
            q.filter.return_value.all.return_value = [conflict_prop]
            q.filter.return_value.first.side_effect = [created_prop_1, created_prop_2]
        return q

    mock_db.query.side_effect = mock_query
    
    wkt_res = ("POLYGON((77.2192 28.6311, 77.2197 28.6311, 77.2197 28.6313, 77.2192 28.6313, 77.2192 28.6311))",)
    area_res = (400.0,)
    insert_res_1 = (8,)
    insert_res_2 = (9,)
    
    exec_mock = MagicMock()
    exec_mock.fetchone.side_effect = [wkt_res, area_res, insert_res_1, insert_res_2]
    mock_db.execute.return_value = exec_mock

    # Monkeypatch run_all_conflict_checks so unit test isolates segmentation logic
    from app.services import conflicts
    monkeypatch.setattr(conflicts, "run_all_conflict_checks", lambda db, building_id: None)

    props = segment_building_footprint_to_properties(mock_db, building_id=3, force=True)
    assert len(props) == 2
