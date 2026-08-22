from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import get_db
import models
import schemas
from utils.auth import get_current_admin

router = APIRouter(prefix="/api/stats", tags=["Dashboard Stats"])

@router.get("", response_model=schemas.ApiResponse[schemas.StatsOverview])
def get_dashboard_stats(
    current_user: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get overview statistics for admin dashboard."""
    total_pengumuman = db.query(models.Pengumuman).count()
    total_views = db.query(func.coalesce(func.sum(models.Pengumuman.views), 0)).scalar()
    total_pengurus = db.query(models.Pengurus).count()
    total_divisi = db.query(models.Divisi).count()

    latest = db.query(
        models.Pengumuman.id,
        models.Pengumuman.title,
        models.Pengumuman.category,
        models.Pengumuman.date_published,
        models.Pengumuman.views
    ).order_by(models.Pengumuman.created_at.desc()).limit(5).all()

    latest_list = [
        {
            "id": row.id,
            "title": row.title,
            "category": row.category,
            "date_published": row.date_published,
            "views": row.views
        } for row in latest
    ]

    return schemas.ApiResponse(
        success=True,
        data=schemas.StatsOverview(
            totalPengumuman=total_pengumuman,
            totalViews=int(total_views),
            totalPengurus=total_pengurus,
            totalDivisi=total_divisi,
            latestPengumuman=latest_list
        )
    )
