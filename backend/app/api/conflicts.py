from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from app.db import get_db
from app.models.entities import Property, ConflictLog, User
from app.services.conflicts import run_all_conflict_checks
from app.core.auth import require_roles

router = APIRouter(prefix="/properties", tags=["Conflicts"])

class ConflictCheckRequest(BaseModel):
    building_id: Optional[int] = Field(default=None, description="Optional building ID to limit check scope")

class ConflictLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    conflict_id: int
    property_id_a: int
    property_id_b: Optional[int]
    conflict_type: str
    detected_at: Any
    resolved: bool

@router.post("/conflicts/check", status_code=status.HTTP_200_OK)
def trigger_conflict_check(
    payload: ConflictCheckRequest = ConflictCheckRequest(),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "surveyor"]))
):
    """
    POST /properties/conflicts/check
    Triggers on-demand spatial conflict detection pass across all 7 geometric checks.
    Restricted to admin and surveyor roles.
    """
    try:
        summary = run_all_conflict_checks(db=db, building_id=payload.building_id)
        return {
            "status": "success",
            "summary": summary
        }
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Conflict detection failed: {str(err)}"
        )

@router.get("/conflicts", response_model=List[ConflictLogResponse])
def list_unresolved_conflicts(
    db: Session = Depends(get_db)
):
    """
    GET /properties/conflicts
    Lists all unresolved spatial conflict logs.
    """
    logs = db.query(ConflictLog).filter(ConflictLog.resolved == False).order_by(ConflictLog.conflict_id.asc()).all()
    return logs

@router.post("/{property_id}/verify", status_code=status.HTTP_200_OK)
def manually_verify_property(
    property_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "surveyor"]))
):
    """
    POST /properties/{id}/verify
    Officer manually verifies a flagged property and resolves associated conflict logs.
    Restricted to admin and surveyor roles.
    """
    prop = db.query(Property).filter(Property.property_id == property_id).first()
    if not prop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Property {property_id} not found")

    prop.verification_status = "verified"
    
    # Mark associated conflict logs as resolved
    db.query(ConflictLog).filter(
        (ConflictLog.property_id_a == property_id) | (ConflictLog.property_id_b == property_id)
    ).update({"resolved": True}, synchronize_session=False)

    db.commit()
    return {
        "status": "success",
        "message": f"Property {property_id} successfully verified and conflicts resolved."
    }
