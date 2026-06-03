"""
Analytics API router — methods frequency, year trends, distributions.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.paper import Paper
from app.models.user import User
from app.models.extraction import ExtractionResult
from app.schemas.analytics import (
    MethodsFrequencyResponse, YearTrendsResponse,
    DistributionResponse, FrequencyItem, TrendItem,
)
from app.utils.auth import get_current_user

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/methods-frequency", response_model=MethodsFrequencyResponse)
def methods_frequency(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Compute frequency of methodology values across papers for the current user."""
    results = (
        db.query(ExtractionResult.value, func.count(ExtractionResult.id))
        .join(Paper, ExtractionResult.paper_id == Paper.id)
        .filter(Paper.user_id == current_user.id)
        .filter(ExtractionResult.field_name == "methodology")
        .filter(ExtractionResult.value.isnot(None))
        .group_by(ExtractionResult.value)
        .order_by(func.count(ExtractionResult.id).desc())
        .all()
    )
    return MethodsFrequencyResponse(
        data=[FrequencyItem(label=r[0], count=r[1]) for r in results]
    )


@router.get("/year-trends", response_model=YearTrendsResponse)
def year_trends(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Count papers by publication year for the current user."""
    results = (
        db.query(Paper.year, func.count(Paper.id))
        .filter(Paper.user_id == current_user.id)
        .filter(Paper.year.isnot(None))
        .group_by(Paper.year)
        .order_by(Paper.year)
        .all()
    )
    return YearTrendsResponse(
        data=[TrendItem(year=r[0], count=r[1]) for r in results]
    )


@router.get("/distributions/{field_name}", response_model=DistributionResponse)
def field_distribution(
    field_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get distribution of values for a given extraction field for the current user."""
    results = (
        db.query(ExtractionResult.value, func.count(ExtractionResult.id))
        .join(Paper, ExtractionResult.paper_id == Paper.id)
        .filter(Paper.user_id == current_user.id)
        .filter(ExtractionResult.field_name == field_name)
        .filter(ExtractionResult.value.isnot(None))
        .group_by(ExtractionResult.value)
        .order_by(func.count(ExtractionResult.id).desc())
        .limit(50)
        .all()
    )
    return DistributionResponse(
        field=field_name,
        data=[FrequencyItem(label=r[0], count=r[1]) for r in results],
    )
