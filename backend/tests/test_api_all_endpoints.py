import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.auth import create_access_token

client = TestClient(app)

# Helper tokens
admin_token = create_access_token(data={"sub": "admin@demo.com", "role": "admin", "uid": 1})
surveyor_token = create_access_token(data={"sub": "surveyor@demo.com", "role": "surveyor", "uid": 2})
citizen_token = create_access_token(data={"sub": "citizen@demo.com", "role": "citizen", "uid": 3})

def test_endpoint_auth_login_success():
    """1. Test POST /auth/login with valid demo credentials"""
    response = client.post("/auth/login", json={"email": "admin@demo.com", "password": "demopassword123"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["role"] == "admin"
    assert data["email"] == "admin@demo.com"

def test_endpoint_auth_login_invalid():
    """1. Test POST /auth/login with invalid password"""
    response = client.post("/auth/login", json={"email": "admin@demo.com", "password": "wrongpassword"})
    assert response.status_code == 401

def test_endpoint_parcels_upload_rbac():
    """2. Test POST /parcels/upload role permissions (admin/surveyor vs citizen vs anonymous)"""
    # Anonymous -> 401
    res_anon = client.post("/parcels/upload", json={"ulpin_2d": "TESTPARCEL01", "boundary_wkt": "POLYGON((0 0, 1 0, 1 1, 0 1, 0 0))"})
    assert res_anon.status_code == 401

    # Citizen -> 403
    res_cit = client.post(
        "/parcels/upload",
        headers={"Authorization": f"Bearer {citizen_token}"},
        json={"ulpin_2d": "TESTPARCEL01", "boundary_wkt": "POLYGON((0 0, 1 0, 1 1, 0 1, 0 0))"}
    )
    assert res_cit.status_code == 403

    # Surveyor / Admin -> 201
    res_surv = client.post(
        "/parcels/upload",
        headers={"Authorization": f"Bearer {surveyor_token}"},
        json={"ulpin_2d": "DELHI999999P01", "boundary_wkt": "POLYGON((77.21 28.63, 77.22 28.63, 77.22 28.64, 77.21 28.64, 77.21 28.63))"}
    )
    assert res_surv.status_code == 201
    assert "parcel" in res_surv.json()

def test_endpoint_buildings_create_rbac():
    """3. Test POST /buildings/{parcel_id} role permissions"""
    # Citizen -> 403
    res_cit = client.post(
        "/buildings/1",
        headers={"Authorization": f"Bearer {citizen_token}"},
        json={"total_floors": 2, "footprint_wkt": "POLYGON((77.2181 28.6311, 77.2182 28.6311, 77.2182 28.6312, 77.2181 28.6312, 77.2181 28.6311))"}
    )
    assert res_cit.status_code == 403

    # Admin -> 201
    res_admin = client.post(
        "/buildings/1",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"total_floors": 2, "footprint_wkt": "POLYGON((77.2181 28.6311, 77.2182 28.6311, 77.2182 28.6312, 77.2181 28.6312, 77.2181 28.6311))"}
    )
    assert res_admin.status_code == 201
    assert res_admin.json()["total_floors"] == 2

def test_endpoint_properties_generate_rbac():
    """4. Test POST /properties/generate role permissions"""
    # Anonymous -> 401
    res_anon = client.post("/properties/generate", json={"building_id": 1, "floor_height": 3.0})
    assert res_anon.status_code == 401

    # Citizen -> 403
    res_cit = client.post(
        "/properties/generate",
        headers={"Authorization": f"Bearer {citizen_token}"},
        json={"building_id": 1, "floor_height": 3.0}
    )
    assert res_cit.status_code == 403

def test_endpoint_get_property_by_ulpin():
    """5. Test GET /properties/{ulpin_3d}"""
    # Valid existing property
    res_valid = client.get("/properties/DELHI110001P01-B01F00U01")
    assert res_valid.status_code == 200
    data = res_valid.json()
    assert data["ulpin_3d"] == "DELHI110001P01-B01F00U01"
    assert data["floor_number"] == 0
    assert "elevation_min_m" in data

    # Non-existent property -> 404
    res_invalid = client.get("/properties/NONEXISTENT999")
    assert res_invalid.status_code == 404

def test_endpoint_get_conflicts_list():
    """6. Test GET /properties/conflicts"""
    response = client.get("/properties/conflicts")
    assert response.status_code == 200
    logs = response.json()
    assert isinstance(logs, list)

def test_endpoint_verify_property_rbac():
    """7. Test POST /properties/{id}/verify role permissions"""
    # Citizen -> 403
    res_cit = client.post("/properties/1/verify", headers={"Authorization": f"Bearer {citizen_token}"})
    assert res_cit.status_code == 403

    # Surveyor -> 200
    res_surv = client.post("/properties/1/verify", headers={"Authorization": f"Bearer {surveyor_token}"})
    assert res_surv.status_code == 200
    assert res_surv.json()["status"] == "success"

def test_endpoint_map_tiles_geojson():
    """8. Test GET /map/tiles and GET /map/geojson"""
    response = client.get("/map/tiles")
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "FeatureCollection"
    assert len(data["features"]) > 0
    layers = {f["properties"]["layer"] for f in data["features"]}
    assert "parcel" in layers or "building" in layers or "property" in layers

def test_endpoint_reports_summary():
    """9. Test GET /reports/summary"""
    response = client.get("/reports/summary")
    assert response.status_code == 200
    summary = response.json()
    assert "parcels_total" in summary
    assert "buildings_total" in summary
    assert "properties_total" in summary
    assert "properties_verified" in summary
    assert "properties_conflict" in summary
    assert "conflicts_by_type" in summary

def test_endpoint_ulpin_preview():
    """10. Test GET /ulpin/preview read-only generator"""
    res = client.get("/ulpin/preview?ulpin_2d=DELHI110001P01&building_idx=1&floor_num=3&unit_idx=2")
    assert res.status_code == 200
    data = res.json()
    assert data["final_ulpin_3d"] == "DELHI110001P01-B01F03U02"
    assert data["step1_base"] == "DELHI110001P01"
    assert data["step2_building"] == "DELHI110001P01-B01"
    assert data["step3_floor"] == "DELHI110001P01-B01F03"
    assert data["step4_unit"] == "DELHI110001P01-B01F03U02"

    # Test basement
    res_b = client.get("/ulpin/preview?ulpin_2d=DELHI110001P02&building_idx=2&floor_num=-1&unit_idx=1")
    assert res_b.status_code == 200
    data_b = res_b.json()
    assert data_b["final_ulpin_3d"] == "DELHI110001P02-B02FB1U01"
    assert data_b["is_basement"] is True

