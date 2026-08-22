from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
import models
import schemas
from utils.auth import get_current_admin

router = APIRouter(prefix="/api/forms", tags=["Form Links"])

@router.get("", response_model=schemas.ApiResponse[List[schemas.FormLinkOut]])
def get_form_links(db: Session = Depends(get_db)):
    """Get active Google Form links."""
    links = db.query(models.FormLink).filter(models.FormLink.is_active == 1).all()
    return schemas.ApiResponse(
        success=True,
        data=[schemas.FormLinkOut.model_validate(link) for link in links]
    )

@router.put("/{key}", response_model=schemas.ApiResponse[schemas.FormLinkOut])
def update_form_link(
    key: str,
    payload: schemas.FormLinkUpdate,
    current_user: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Update Google Form link (Admin only)."""
    link = db.query(models.FormLink).filter(models.FormLink.key == key).first()
    if not link:
        raise HTTPException(status_code=404, detail="Form link tidak ditemukan")

    if payload.title is not None:
        link.title = payload.title
    if payload.google_form_url is not None:
        link.google_form_url = payload.google_form_url
    if payload.is_active is not None:
        link.is_active = payload.is_active

    db.commit()
    db.refresh(link)

    return schemas.ApiResponse(
        success=True,
        data=schemas.FormLinkOut.model_validate(link),
        message="Form link berhasil diperbarui"
    )
