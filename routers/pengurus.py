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
    div_id = payload.id
    if not div_id:
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
        div_id = f"div_{int(time.time())}_{random_suffix}"

    divisi = models.Divisi(
        id=div_id,
        name=payload.name,
        komisi=payload.komisi,
        icon_name=payload.icon_name,
        description=payload.description,
        group_photo_url=payload.group_photo_url,
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

@router.put("/divisi/{divisi_id}", response_model=schemas.ApiResponse[schemas.DivisiOut])
def update_divisi(
    divisi_id: str,
    payload: schemas.DivisiUpdate,
    current_user: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Update division (Admin only)."""
    divisi = db.query(models.Divisi).filter(models.Divisi.id == divisi_id).first()
    if not divisi:
        raise HTTPException(status_code=404, detail="Divisi tidak ditemukan")

    if payload.name is not None:
        divisi.name = payload.name
    if payload.komisi is not None:
        divisi.komisi = payload.komisi
    if payload.icon_name is not None:
        divisi.icon_name = payload.icon_name
    if payload.description is not None:
        divisi.description = payload.description
    if payload.group_photo_url is not None:
        divisi.group_photo_url = payload.group_photo_url
    if payload.order_priority is not None:
        divisi.order_priority = payload.order_priority

    db.commit()
    db.refresh(divisi)

    return schemas.ApiResponse(
        success=True,
        data=schemas.DivisiOut.model_validate(divisi),
        message="Divisi berhasil diperbarui"
    )

@router.delete("/divisi/{divisi_id}", response_model=schemas.ApiResponse[None])
def delete_divisi(
    divisi_id: str,
    current_user: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Delete division (Admin only)."""
    divisi = db.query(models.Divisi).filter(models.Divisi.id == divisi_id).first()
    if not divisi:
        raise HTTPException(status_code=404, detail="Divisi tidak ditemukan")

    db.delete(divisi)
    db.commit()
    return schemas.ApiResponse(success=True, message="Divisi berhasil dihapus")

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
        period=payload.period or "2025/2026",
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

@router.put("/member/{member_id}", response_model=schemas.ApiResponse[schemas.PengurusOut])
def update_member(
    member_id: str,
    payload: schemas.PengurusUpdate,
    current_user: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Update board member (Admin only)."""
    member = db.query(models.Pengurus).filter(models.Pengurus.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Pengurus tidak ditemukan")

    if payload.divisi_id is not None:
        member.divisi_id = payload.divisi_id
    if payload.name is not None:
        member.name = payload.name
    if payload.role is not None:
        member.role = payload.role
    if payload.photo_url is not None:
        member.photo_url = payload.photo_url
    if payload.period is not None:
        member.period = payload.period
    if payload.order_priority is not None:
        member.order_priority = payload.order_priority

    db.commit()
    db.refresh(member)

    return schemas.ApiResponse(
        success=True,
        data=schemas.PengurusOut.model_validate(member),
        message="Data pengurus berhasil diperbarui"
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
