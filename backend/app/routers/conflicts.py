"""
Conflicts API router — detect contradictory findings across papers.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models.user import User
from app.schemas.analytics import ConflictResponse
from app.utils.auth import get_current_user

router = APIRouter(prefix="/conflicts", tags=["Conflicts"])


class ConflictDetectRequest(BaseModel):
    field_name: Optional[str] = None
    schema_id: Optional[str] = None


@router.post("/detect", response_model=list[ConflictResponse])
def detect_conflicts(
    req: ConflictDetectRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Detect conflicts in extracted values across papers for the user."""
    from app.services.conflict_detector import detect_conflicts
    try:
        conflicts = detect_conflicts(
            db,
            user_id=current_user.id,
            field_name=req.field_name,
            schema_id=req.schema_id,
        )
        return conflicts
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=list[ConflictResponse])
def get_conflicts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get cached conflict results for the user."""
    from app.services.conflict_detector import get_cached_conflicts
    conflicts = get_cached_conflicts(user_id=current_user.id)
    if conflicts is None:
        raise HTTPException(status_code=404, detail="No conflict analysis run yet.")
    return conflicts
