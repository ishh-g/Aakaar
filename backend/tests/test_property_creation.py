import pytest
from unittest.mock import MagicMock
from pydantic import ValidationError
from app.schemas.property import PropertyCreate
from app.services.property import create_property
from app.models.entities import Parcel

def test_property_creation_auto_generates_ulpin_3d():
    """Verify create_property automatically populates ulpin_3d from parent parcel 2D ULPIN"""
    mock_db = MagicMock()
    mock_parcel = Parcel(parcel_id=1, ulpin_2d="DELHI110001P01", area_sqm=1000.0)
    mock_db.query().filter().first.return_value = mock_parcel

    prop_in = PropertyCreate(
        parcel_id=1,
        building_id=1,
        building_idx=1,
        floor_number=3,
        unit_index=2,
        elevation_min_m=9.0,
        elevation_max_m=12.0,
        area_sqm=300.0,
        owner_id=1
    )

    created_prop = create_property(mock_db, prop_in)
    
    # Assert ulpin_3d is auto-populated matching generate_3d_ulpin spec format
    assert created_prop.ulpin_3d == "DELHI110001P01-B01F03U02"
    assert mock_db.add.called
    assert mock_db.commit.called

def test_property_creation_rejects_manual_ulpin_3d():
    """Verify PropertyCreate schema raises ValidationError if ulpin_3d is manually provided"""
    with pytest.raises(ValidationError) as exc_info:
        PropertyCreate(
            parcel_id=1,
            building_id=1,
            building_idx=1,
            floor_number=3,
            unit_index=2,
            elevation_min_m=9.0,
            elevation_max_m=12.0,
            area_sqm=300.0,
            owner_id=1,
            ulpin_3d="MANUAL_CUSTOM_ID"  # Attempt manual assignment
        )
    assert "Extra inputs are not permitted" in str(exc_info.value)
