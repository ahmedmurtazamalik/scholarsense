"""
Zotero API router — connect, list collections, sync papers.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.user import User
from app.utils.auth import get_current_user

router = APIRouter(prefix="/zotero", tags=["Zotero"])


class ZoteroConnectRequest(BaseModel):
    api_key: str
    library_id: str
    library_type: str = "user"


class ZoteroSyncRequest(BaseModel):
    collection_key: Optional[str] = None


@router.post("/connect")
def connect_zotero(
    req: ZoteroConnectRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Validate and store Zotero API credentials in the db for the current user."""
    from app.services.zotero_service import validate_connection
    try:
        result = validate_connection(req.api_key, req.library_id, req.library_type)
        
        current_user.zotero_api_key = req.api_key
        current_user.zotero_library_id = req.library_id
        current_user.zotero_library_type = req.library_type
        db.commit()

        return {"message": "Connected successfully", "username": result.get("username", "Unknown")}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Connection failed: {str(e)}")


@router.get("/collections")
def list_collections(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List Zotero collections for the authenticated user."""
    from app.services.zotero_service import get_collections
    try:
        collections = get_collections(db, current_user.id)
        return {"collections": collections}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sync")
def sync_from_zotero(
    req: ZoteroSyncRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Sync papers from Zotero library/collection into the user's account."""
    from app.services.zotero_service import sync_papers
    try:
        result = sync_papers(db, user_id=current_user.id, collection_key=req.collection_key)
        return {
            "message": "Sync complete",
            "new_papers": result["new"],
            "updated_papers": result["updated"],
            "total": result["total"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
