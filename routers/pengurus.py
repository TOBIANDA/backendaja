import time
import random
import string
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
import models
import schemas
from utils.auth import get_current_admin

router = APIRouter(prefix="/api/pengurus", tags=["Divisi & Pengurus"])

@router.get("", response_model=schemas.ApiResponse[List[schemas.DivisiOut]])
def get_all_divisions_and_members(db: Session = Depends(get_db)):
    """Get all divisions with nested members."""
    divisions = db.query(models.Divisi).order_by(models.Divisi.order_priority.asc()).all()
    return schemas.ApiResponse(
        success=True,
        data=[schemas.DivisiOut.model_validate(div) for div in divisions]
    )

@router.post("/divisi", response_model=schemas.ApiResponse[schemas.DivisiOut], status_code=201)
def create_divisi(
    payload: schemas.DivisiCreate,
    current_user: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Create new division (Admin only)."""
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
    div_id = f"div_{int(time.time())}_{random_suffix}"

    divisi = models.Divisi(
        id=div_id,
        name=payload.name,
        description=payload.description,
        order_priority=payload.order_priority or 0
    )
    db.add(divisi)
    db.commit()
    db.refresh(divisi)

    return schemas.ApiResponse(
        success=True,
        data=schemas.DivisiOut.model_validate(divisi),
        message="Divisi berhasil dibuat"
    )

@router.post("/member", response_model=schemas.ApiResponse[schemas.PengurusOut], status_code=201)
def create_member(
    payload: schemas.PengurusCreate,
    current_user: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Create new board member (Admin only)."""
    divisi = db.query(models.Divisi).filter(models.Divisi.id == payload.divisi_id).first()
    if not divisi:
        raise HTTPException(status_code=404, detail="Divisi tidak ditemukan")

    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
    member_id = f"png_{int(time.time())}_{random_suffix}"

    member = models.Pengurus(
        id=member_id,
        divisi_id=payload.divisi_id,
        name=payload.name,
        role=payload.role,
        photo_url=payload.photo_url,
        period=payload.period,
        order_priority=payload.order_priority or 0
    )
    db.add(member)
    db.commit()
    db.refresh(member)

    return schemas.ApiResponse(
        success=True,
        data=schemas.PengurusOut.model_validate(member),
        message="Pengurus berhasil ditambahkan"
    )

@router.delete("/member/{member_id}", response_model=schemas.ApiResponse[None])
def delete_member(
    member_id: str,
    current_user: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Delete board member (Admin only)."""
    member = db.query(models.Pengurus).filter(models.Pengurus.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Pengurus tidak ditemukan")

    db.delete(member)
    db.commit()
    return schemas.ApiResponse(success=True, message="Pengurus berhasil dihapus")
