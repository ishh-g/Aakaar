from fastapi import APIRouter, Query, HTTPException, status
from pydantic import BaseModel, Field
from app.services.ulpin import generate_3d_ulpin

router = APIRouter(prefix="/ulpin", tags=["3D ULPIN Generator"])

class UlpinPreviewResponse(BaseModel):
    ulpin_2d: str
    building_idx: int
    floor_num: int
    unit_idx: int
    is_basement: bool
    building_segment: str
    floor_segment: str
    unit_segment: str
    step1_base: str
    step2_building: str
    step3_floor: str
    step4_unit: str
    final_ulpin_3d: str

@router.get("/preview", response_model=UlpinPreviewResponse, status_code=status.HTTP_200_OK)
def preview_3d_ulpin(
    ulpin_2d: str = Query(..., description="Parent 2D ULPIN code (e.g., DELHI110001P01)"),
    building_idx: int = Query(default=1, ge=1, description="Building index (1 for B01, 2 for B02)"),
    floor_num: int = Query(default=0, description="Floor number (0 for Ground, >0 for upper floors, <0 for basements)"),
    unit_idx: int = Query(default=1, ge=1, description="Unit index (1 for U01, 2 for U02)")
):
    """
    GET /ulpin/preview
    Pure, side-effect free endpoint that computes the standard 3D ULPIN
    string and its step-by-step assembly breakdown.
    Does NOT write to or modify the database.
    """
    try:
        clean_2d = ulpin_2d.strip().upper()
        final_ulpin = generate_3d_ulpin(clean_2d, building_idx, floor_num, unit_idx)
        
        b_seg = f"B{building_idx:02d}"
        if floor_num < 0:
            f_seg = f"FB{abs(floor_num)}"
        else:
            f_seg = f"F{floor_num:02d}"
        u_seg = f"U{unit_idx:02d}"

        step1 = clean_2d
        step2 = f"{clean_2d}-{b_seg}"
        step3 = f"{clean_2d}-{b_seg}{f_seg}"
        step4 = final_ulpin

        return UlpinPreviewResponse(
            ulpin_2d=clean_2d,
            building_idx=building_idx,
            floor_num=floor_num,
            unit_idx=unit_idx,
            is_basement=(floor_num < 0),
            building_segment=b_seg,
            floor_segment=f_seg,
            unit_segment=u_seg,
            step1_base=step1,
            step2_building=step2,
            step3_floor=step3,
            step4_unit=step4,
            final_ulpin_3d=final_ulpin
        )
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to generate 3D ULPIN preview: {str(err)}"
        )
