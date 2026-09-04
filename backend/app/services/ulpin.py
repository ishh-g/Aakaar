"""
3D ULPIN Generator Module
Implements Section 4 of the Technical Build Spec:
Format: <2D_ULPIN>-B<NN>F<NN>U<NN>
"""

def generate_3d_ulpin(ulpin_2d: str, building_idx: int, floor_num: int, unit_idx: int = 1) -> str:
    """
    Pure function to generate a 3D ULPIN string from parent 2D ULPIN, building index,
    floor number, and unit index.

    Segments:
      <2D_ULPIN>   Parent parcel 2D ULPIN string
      B<NN>        2-digit building index (01, 02, ...)
      F<NN>        2-digit floor number (F00 for ground floor, F01, F02, etc.).
                   Basement floors (< 0) are formatted as FB1, FB2, etc.
      U<NN>        2-digit unit index (U01, U02, ...)
    """
    if not ulpin_2d or not isinstance(ulpin_2d, str):
        raise ValueError("ulpin_2d must be a non-empty string.")
    
    building_segment = f"B{building_idx:02d}"
    
    if floor_num < 0:
        floor_segment = f"FB{abs(floor_num)}"
    else:
        floor_segment = f"F{floor_num:02d}"
        
    unit_segment = f"U{unit_idx:02d}"
    
    return f"{ulpin_2d.strip()}-{building_segment}{floor_segment}{unit_segment}"
