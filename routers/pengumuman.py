import re
import time
import random
import string
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc

from database import get_db
import models
import schemas
from utils.auth import get_current_admin

router = APIRouter(prefix="/api/pengumuman", tags=["Pengumuman"])

def slugify(text: str) -> str:
    """Generate slug from title."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    text = re.sub(r'^-+|-+$', '', text)
    return text

def increment_views_task(pengumuman_id: str, db: Session):
    try:
        item = db.query(models.Pengumuman).filter(models.Pengumuman.id == pengumuman_id).first()
        if item:
            item.views += 1
            db.commit()
    except Exception:
        pass

@router.get("", response_model=schemas.ApiResponse[schemas.PengumumanListResponse])
def get_pengumuman_list(
    kategori: Optional[str] = Query(None, description="Filter: kegiatan | oprec | ultah | lainnya"),
    search: Optional[str] = Query(None, description="Search keyword in title or content"),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get announcements list with filtering, searching, and pagination."""
    query = db.query(models.Pengumuman)

    if kategori and kategori != "all":
        query = query.filter(models.Pengumuman.category == kategori)

    if search:
        search_fmt = f"%{search}%"
        query = query.filter(
            or_(
                models.Pengumuman.title.ilike(search_fmt),
                models.Pengumuman.content.ilike(search_fmt)
            )
        )

    total = query.count()
    items = query.order_by(desc(models.Pengumuman.date_published), desc(models.Pengumuman.created_at))\
                 .offset((page - 1) * limit)\
                 .limit(limit)\
                 .all()

    totalPages = (total + limit - 1) // limit if limit > 0 else 0

    return schemas.ApiResponse(
        success=True,
        data=schemas.PengumumanListResponse(
            items=[schemas.PengumumanOut.model_validate(item) for item in items],
            pagination=schemas.PaginationMeta(
                page=page,
                limit=limit,
                total=total,
                totalPages=totalPages
            )
        )
    )

@router.get("/{id_or_slug}", response_model=schemas.ApiResponse[schemas.PengumumanOut])
def get_pengumuman_detail(
    id_or_slug: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Get single announcement detail by ID or Slug."""
    item = db.query(models.Pengumuman).filter(
        or_(models.Pengumuman.id == id_or_slug, models.Pengumuman.slug == id_or_slug)
    ).first()

    if not item:
        raise HTTPException(status_code=404, detail="Pengumuman tidak ditemukan")

    # Increment views in background task
    background_tasks.add_task(increment_views_task, item.id, db)

    return schemas.ApiResponse(
        success=True,
        data=schemas.PengumumanOut.model_validate(item)
    )

@router.post("", response_model=schemas.ApiResponse[schemas.PengumumanOut], status_code=201)
def create_pengumuman(
    payload: schemas.PengumumanCreate,
    current_user: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Create new announcement (Admin only)."""
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
    item_id = f"ann_{int(time.time())}_{random_suffix}"
    slug = f"{slugify(payload.title)}-{random_suffix}"

    new_item = models.Pengumuman(
        id=item_id,
        title=payload.title,
        slug=slug,
        category=payload.category,
        content=payload.content,
        image_url=payload.image_url,
        date_published=payload.date_published,
        author=payload.author or "Pengurus PMK"
    )

    db.add(new_item)
    db.commit()
    db.refresh(new_item)

    return schemas.ApiResponse(
        success=True,
        data=schemas.PengumumanOut.model_validate(new_item),
        message="Pengumuman berhasil dibuat"
    )

@router.put("/{item_id}", response_model=schemas.ApiResponse[schemas.PengumumanOut])
def update_pengumuman(
    item_id: str,
    payload: schemas.PengumumanUpdate,
    current_user: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Update announcement (Admin only)."""
    item = db.query(models.Pengumuman).filter(models.Pengumuman.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Pengumuman tidak ditemukan")

    if payload.title is not None:
        item.title = payload.title
    if payload.category is not None:
        item.category = payload.category
    if payload.content is not None:
        item.content = payload.content
    if payload.image_url is not None:
        item.image_url = payload.image_url
    if payload.date_published is not None:
        item.date_published = payload.date_published
    if payload.author is not None:
        item.author = payload.author

    db.commit()
    db.refresh(item)

    return schemas.ApiResponse(
        success=True,
        data=schemas.PengumumanOut.model_validate(item),
        message="Pengumuman berhasil diperbarui"
    )

@router.delete("/{item_id}", response_model=schemas.ApiResponse[None])
def delete_pengumuman(
    item_id: str,
    current_user: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Delete announcement (Admin only)."""
    item = db.query(models.Pengumuman).filter(models.Pengumuman.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Pengumuman tidak ditemukan")

    db.delete(item)
    db.commit()

    return schemas.ApiResponse(
        success=True,
        message="Pengumuman berhasil dihapus"
    )
