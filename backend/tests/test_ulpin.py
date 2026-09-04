import pytest
from app.services.ulpin import generate_3d_ulpin

def test_generate_3d_ulpin_normal():
    """Test normal floor case (Floor 3, Unit 2, Building 1)"""
    ulpin_3d = generate_3d_ulpin("XXXXAAAA1234", 1, 3, 2)
    assert ulpin_3d == "XXXXAAAA1234-B01F03U02"

def test_generate_3d_ulpin_basement():
    """Test basement floor case (Floor -1 -> FB1, Building 1, Unit 1)"""
    ulpin_3d = generate_3d_ulpin("XXXXAAAA1234", 1, -1, 1)
    assert ulpin_3d == "XXXXAAAA1234-B01FB1U01"

def test_generate_3d_ulpin_multi_unit_ground():
    """Test multi-unit ground floor case (Floor 0 -> F00, Building 1, Unit 2 -> U02)"""
    ulpin_3d = generate_3d_ulpin("XXXXAAAA1234", 1, 0, 2)
    assert ulpin_3d == "XXXXAAAA1234-B01F00U02"

def test_generate_3d_ulpin_invalid_ulpin():
    """Test invalid ulpin_2d input handling"""
    with pytest.raises(ValueError):
        generate_3d_ulpin("", 1, 0, 1)
