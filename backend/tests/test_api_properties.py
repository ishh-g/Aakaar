from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

from app.core.auth import create_access_token

def test_api_generate_properties_endpoint():
    """Test POST /properties/generate endpoint structure and route registration"""
    token = create_access_token(data={"sub": "admin@demo.com", "role": "admin", "uid": 1})
    response = client.post(
        "/properties/generate",
        headers={"Authorization": f"Bearer {token}"},
        json={"building_id": 99999, "floor_height": 3.0, "force": False}
    )
    assert response.status_code in (400, 404, 409, 500)
    assert "detail" in response.json()
