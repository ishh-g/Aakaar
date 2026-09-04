from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Dict, Any
from app.db import get_db

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.get("/summary")
def get_system_summary(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    GET /reports/summary
    Returns complete system analytics, validation stats, and conflict breakdown.
    """
    # 1. Total counts
    parcel_count = db.execute(text("SELECT COUNT(*) FROM parcels;")).scalar() or 0
    building_count = db.execute(text("SELECT COUNT(*) FROM buildings;")).scalar() or 0
    property_count = db.execute(text("SELECT COUNT(*) FROM properties;")).scalar() or 0

    # 2. Property status counts
    status_counts = db.execute(text("""
        SELECT verification_status, COUNT(*) 
        FROM properties 
        GROUP BY verification_status;
    """)).fetchall()
    statuses = {r[0]: r[1] for r in status_counts}

    # 3. Active conflicts breakdown
    conflict_breakdown = db.execute(text("""
        SELECT conflict_type, COUNT(*) 
        FROM conflict_logs 
        WHERE resolved = FALSE 
        GROUP BY conflict_type;
    """)).fetchall()
    conflicts_by_type = {r[0]: r[1] for r in conflict_breakdown}
    total_unresolved_conflicts = sum(conflicts_by_type.values())

    return {
        "parcels_total": parcel_count,
        "buildings_total": building_count,
        "properties_total": property_count,
        "properties_verified": statuses.get("verified", 0),
        "properties_conflict": statuses.get("conflict", 0),
        "properties_unverified": statuses.get("unverified", 0),
        "total_unresolved_conflicts": total_unresolved_conflicts,
        "conflicts_by_type": conflicts_by_type
    }
