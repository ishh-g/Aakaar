"""
Tests for the 3D overlap-severity feature.

The happy-path geometry is the Bharat Mandapam seed data:
  - Property 40: west half of Building 12, elevation 5.0 m -> 10.0 m
  - Property 41: full Building 12,   elevation 7.5 m -> 12.5 m
  - Footprint intersection = the west half
  - Overlapping elevation band = min(10, 12.5) - max(5, 7.5) = 2.5 m
  - True ground area is computed on the WGS84 ellipsoid, matching the
    PostGIS `geography` area used by the API.
"""

from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from pyproj import Geod

from app.db import get_db
from app.main import app
from app.services.conflicts import calculate_overlap_severity

# Building 12 footprints, in (longitude, latitude) order (EPSG:4326).
PROPERTY_40_FOOTPRINT = [
    (77.2422, 28.6192),
    (77.2425, 28.6192),
    (77.2425, 28.6196),
    (77.2422, 28.6196),
]
PROPERTY_41_FOOTPRINT = [
    (77.2422, 28.6192),
    (77.2428, 28.6192),
    (77.2428, 28.6196),
    (77.2422, 28.6196),
]


def _true_ground_area_m2(coords):
    """WGS84 geodesic polygon area in m^2 (same basis as PostGIS geography)."""
    geod = Geod(ellps="WGS84")
    lons = [lon for lon, _ in coords]
    lats = [lat for _, lat in coords]
    area, _ = geod.polygon_area_perimeter(lons, lats)
    return abs(area)


def test_overlap_volume_and_pct_with_known_bharat_mandapam_geometry():
    """Hand calculation must match: 1300.61 m2 x 2.5 m = 3251.53 m3, 50.0%."""
    footprint_40_area = _true_ground_area_m2(PROPERTY_40_FOOTPRINT)
    footprint_41_area = _true_ground_area_m2(PROPERTY_41_FOOTPRINT)

    volume_40 = footprint_40_area * (10.0 - 5.0)
    volume_41 = footprint_41_area * (12.5 - 7.5)

    overlap_height = min(10.0, 12.5) - max(5.0, 7.5)
    expected_volume = footprint_40_area * overlap_height  # intersection == P40
    expected_pct = expected_volume / min(volume_40, volume_41) * 100.0

    volume, pct = calculate_overlap_severity(
        overlap_area_m2=footprint_40_area,
        overlap_height_m=overlap_height,
        volume_a_m3=volume_40,
        volume_b_m3=volume_41,
    )

    assert volume == pytest.approx(3251.53, abs=0.02)
    assert volume == pytest.approx(round(expected_volume, 2), abs=0.01)
    assert pct == pytest.approx(50.0, abs=0.01)
    assert pct == pytest.approx(round(expected_pct, 2), abs=0.01)


def test_touching_footprints_with_elevation_overlap_have_no_severity():
    """Boundary-only contact (0 m2 intersection) must yield null, not 0 or an error."""
    volume, pct = calculate_overlap_severity(
        overlap_area_m2=0.0,
        overlap_height_m=2.5,
        volume_a_m3=6503.06,
        volume_b_m3=13006.11,
    )
    assert volume is None
    assert pct is None


def test_footprint_overlap_without_elevation_overlap_has_no_severity():
    """Stacked floors that share a footprint but not a height band have no 3D overlap."""
    volume, pct = calculate_overlap_severity(
        overlap_area_m2=1300.61,
        overlap_height_m=0.0,
        volume_a_m3=3901.83,
        volume_b_m3=3901.83,
    )
    assert volume is None
    assert pct is None


def test_missing_property_metrics_have_no_severity():
    """A dangling/missing property (LEFT JOIN nulls) must not crash the calculation."""
    assert calculate_overlap_severity(None, None, None, 13006.11) == (None, None)
    assert calculate_overlap_severity(100.0, 1.0, None, 1000.0) == (None, None)


def _conflict_row(**overrides):
    values = {
        "conflict_id": 1,
        "property_id_a": 40,
        "property_id_b": 41,
        "conflict_type": "overlap",
        "detected_at": datetime(2026, 10, 19, 12, 0, tzinfo=timezone.utc),
        "resolved": False,
        "overlap_area_m2": 1300.611341,
        "overlap_height_m": 2.5,
        "volume_a_m3": 6503.056707,
        "volume_b_m3": 13006.113413,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def test_conflicts_api_returns_severity_fields_only_for_two_property_types():
    """GET /properties/conflicts exposes both fields; other types and dangling rows are null."""
    rows = [
        _conflict_row(conflict_id=1),
        _conflict_row(
            conflict_id=2,
            property_id_b=None,
            conflict_type="boundary_violation",
        ),
        _conflict_row(
            conflict_id=3,
            property_id_b=99999,  # property deleted / no longer resolvable
            conflict_type="overlap",
            overlap_area_m2=None,
            overlap_height_m=None,
            volume_b_m3=None,
        ),
    ]

    fake_db = MagicMock()
    fake_db.execute.return_value.fetchall.return_value = rows

    def override_get_db():
        yield fake_db

    app.dependency_overrides[get_db] = override_get_db
    try:
        response = TestClient(app).get("/properties/conflicts")
    finally:
        app.dependency_overrides.pop(get_db, None)

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 3

    for item in payload:
        assert "overlap_volume_m3" in item
        assert "overlap_pct" in item

    happy = payload[0]
    assert happy["conflict_type"] == "overlap"
    assert happy["overlap_volume_m3"] == pytest.approx(3251.53, abs=0.02)
    assert happy["overlap_pct"] == pytest.approx(50.0, abs=0.01)

    # Non-two-property conflict type: both fields must be null.
    assert payload[1]["overlap_volume_m3"] is None
    assert payload[1]["overlap_pct"] is None

    # Deleted/dangling property: null, and crucially not a 500.
    assert payload[2]["overlap_volume_m3"] is None
    assert payload[2]["overlap_pct"] is None
