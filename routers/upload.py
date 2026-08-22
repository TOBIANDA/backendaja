import time
import random
import string
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from utils.auth import get_current_admin
from utils.r2 import upload_to_r2
import schemas
import models

router = APIRouter(prefix="/api/upload", tags=["Media Upload"])

ALLOWED_TYPES = ["image/jpeg", "image/png", "image/webp", "image/gif", "image/svg+xml"]
MAX_SIZE = 5 * 1024 * 1024 # 5MB

@router.post("", response_model=schemas.ApiResponse[dict])
async def upload_file(
    file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_admin)
):
    """Upload image file to Cloudflare R2 bucket (or local uploads)."""
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Hanya file gambar (JPEG, PNG, WebP, GIF, SVG) yang diperbolehkan"
        )

    file_bytes = await file.read()
    if len(file_bytes) > MAX_SIZE:
        raise HTTPException(status_code=400, detail="Ukuran file maksimal 5MB")

    ext = file.filename.split(".")[-1] if "." in file.filename else "webp"
    random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    unique_filename = f"pmk_{int(time.time())}_{random_str}.{ext}"

    url = upload_to_r2(file_bytes, unique_filename, file.content_type)

    return schemas.ApiResponse(
        success=True,
        data={
            "fileName": unique_filename,
            "url": url,
            "size": len(file_bytes),
            "contentType": file.content_type
        },
        message="Upload berhasil"
    )
