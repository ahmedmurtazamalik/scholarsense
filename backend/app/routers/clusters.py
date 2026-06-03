"""
Clusters API router — generate and retrieve semantic paper clusters.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.analytics import ClusterResponse
from app.utils.auth import get_current_user

router = APIRouter(prefix="/clusters", tags=["Clusters"])


class ClusterGenerateRequest(BaseModel):
    num_clusters: int = 5


@router.post("/generate", response_model=list[ClusterResponse])
def generate_clusters(
    req: ClusterGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate semantic clusters from paper embeddings for the user."""
    from app.services.clustering_service import cluster_papers
    try:
        clusters = cluster_papers(db, user_id=current_user.id, num_clusters=req.num_clusters)
        return clusters
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=list[ClusterResponse])
def get_clusters(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get the latest clustering results (cached) for the user."""
    from app.services.clustering_service import get_cached_clusters
    clusters = get_cached_clusters(user_id=current_user.id)
    if clusters is None:
        raise HTTPException(status_code=404, detail="No clusters generated yet. Call POST /clusters/generate first.")
    return clusters
