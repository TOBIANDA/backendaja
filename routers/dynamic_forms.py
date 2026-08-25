import json
import re
import csv
import io
import time
import random
import string
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from database import get_db
import models
import schemas
from utils.auth import get_current_admin
from utils.r2 import upload_to_r2

router = APIRouter(prefix="/api/dynamic-forms", tags=["Dynamic Forms"])

def slugify(text: str) -> str:
    """Generate clean slug from string."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    text = re.sub(r"^-+|-+$", "", text)
    return text or "form"

def parse_form_out(form: models.DynamicForm, submission_count: int = 0) -> schemas.DynamicFormOut:
    """Convert ORM model to Pydantic output."""
    try:
        fields = json.loads(form.fields_schema) if form.fields_schema else []
    except Exception:
        fields = []
    
    return schemas.DynamicFormOut(
        id=form.id,
        title=form.title,
        slug=form.slug,
        description=form.description,
        fields_schema=fields,
        is_active=form.is_active,
        submission_count=submission_count,
        created_at=form.created_at,
        updated_at=form.updated_at
    )

# ----------------- PUBLIC ENDPOINTS -----------------

@router.get("", response_model=schemas.ApiResponse[List[schemas.DynamicFormOut]])
def get_forms(active_only: bool = False, db: Session = Depends(get_db)):
    """Get list of dynamic forms."""
    query = db.query(models.DynamicForm)
    if active_only:
        query = query.filter(models.DynamicForm.is_active == 1)
    
    forms = query.order_by(models.DynamicForm.created_at.desc()).all()
    results = []
    for f in forms:
        count = db.query(models.FormSubmission).filter(models.FormSubmission.form_id == f.id).count()
        results.append(parse_form_out(f, count))

    return schemas.ApiResponse(
        success=True,
        data=results
    )

@router.get("/{id_or_slug}", response_model=schemas.ApiResponse[schemas.DynamicFormOut])
def get_form_by_id_or_slug(id_or_slug: str, db: Session = Depends(get_db)):
    """Get dynamic form schema by ID or slug."""
    form = db.query(models.DynamicForm).filter(
        (models.DynamicForm.id == id_or_slug) | (models.DynamicForm.slug == id_or_slug)
    ).first()

    if not form:
        raise HTTPException(status_code=404, detail="Formulir tidak ditemukan")

    count = db.query(models.FormSubmission).filter(models.FormSubmission.form_id == form.id).count()
    return schemas.ApiResponse(
        success=True,
        data=parse_form_out(form, count)
    )

@router.post("/{id_or_slug}/submit", response_model=schemas.ApiResponse[dict])
def submit_form(id_or_slug: str, payload: schemas.FormSubmissionCreate, db: Session = Depends(get_db)):
    """Submit responses to a dynamic form."""
    form = db.query(models.DynamicForm).filter(
        (models.DynamicForm.id == id_or_slug) | (models.DynamicForm.slug == id_or_slug)
    ).first()

    if not form:
        raise HTTPException(status_code=404, detail="Formulir tidak ditemukan")

    if form.is_active == 0:
        raise HTTPException(status_code=400, detail="Formulir ini sudah ditutup dan tidak menerima tanggapan baru.")

    # Validate required fields
    try:
        fields = json.loads(form.fields_schema) if form.fields_schema else []
    except Exception:
        fields = []

    answers = payload.answers or {}
    for f in fields:
        f_id = f.get("id")
        f_label = f.get("label", "Pertanyaan")
        f_req = f.get("required", False)
        val = answers.get(f_id)

        if f_req:
            if val is None or (isinstance(val, str) and not val.strip()) or (isinstance(val, list) and len(val) == 0):
                raise HTTPException(status_code=400, detail=f"'{f_label}' wajib diisi.")

    sub_id = f"sub_{int(time.time())}_{''.join(random.choices(string.ascii_lowercase + string.digits, k=5))}"
    new_sub = models.FormSubmission(
        id=sub_id,
        form_id=form.id,
        answers_json=json.dumps(answers, ensure_ascii=False),
        submitted_at=datetime.utcnow()
    )
    db.add(new_sub)
    db.commit()

    return schemas.ApiResponse(
        success=True,
        data={"submissionId": sub_id},
        message="Terima kasih, tanggapan Anda berhasil disimpan!"
    )

@router.post("/upload-attachment", response_model=schemas.ApiResponse[dict])
async def upload_form_attachment(file: UploadFile = File(...)):
    """Public file upload for form attachments (e.g. KTM, Bukti Transfer, Foto Diri)."""
    max_size = 10 * 1024 * 1024 # 10MB
    file_bytes = await file.read()
    if len(file_bytes) > max_size:
        raise HTTPException(status_code=400, detail="Ukuran berkas maksimal 10MB")

    ext = file.filename.split(".")[-1] if "." in file.filename else "dat"
    random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    unique_filename = f"form_att_{int(time.time())}_{random_str}.{ext}"

    url = upload_to_r2(file_bytes, unique_filename, file.content_type or "application/octet-stream")

    return schemas.ApiResponse(
        success=True,
        data={
            "fileName": file.filename,
            "url": url,
            "size": len(file_bytes),
            "contentType": file.content_type
        },
        message="Berkas berhasil diunggah"
    )

# ----------------- ADMIN ENDPOINTS -----------------

@router.post("", response_model=schemas.ApiResponse[schemas.DynamicFormOut])
def create_form(
    payload: schemas.DynamicFormCreate,
    current_user: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Create new dynamic form (Admin only)."""
    form_id = f"form_{int(time.time())}_{''.join(random.choices(string.ascii_lowercase + string.digits, k=4))}"
    base_slug = slugify(payload.slug or payload.title)
    
    slug = base_slug
    counter = 1
    while db.query(models.DynamicForm).filter(models.DynamicForm.slug == slug).first():
        slug = f"{base_slug}-{counter}"
        counter += 1

    fields_json = json.dumps([f.model_dump() for f in payload.fields_schema], ensure_ascii=False)

    new_form = models.DynamicForm(
        id=form_id,
        title=payload.title,
        slug=slug,
        description=payload.description,
        fields_schema=fields_json,
        is_active=payload.is_active if payload.is_active is not None else 1
    )
    db.add(new_form)
    db.commit()
    db.refresh(new_form)

    return schemas.ApiResponse(
        success=True,
        data=parse_form_out(new_form, 0),
        message="Formulir berhasil dibuat"
    )

@router.put("/{id}", response_model=schemas.ApiResponse[schemas.DynamicFormOut])
def update_form(
    id: str,
    payload: schemas.DynamicFormUpdate,
    current_user: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Update existing dynamic form (Admin only)."""
    form = db.query(models.DynamicForm).filter(models.DynamicForm.id == id).first()
    if not form:
        raise HTTPException(status_code=404, detail="Formulir tidak ditemukan")

    if payload.title is not None:
        form.title = payload.title
    if payload.description is not None:
        form.description = payload.description
    if payload.slug is not None and payload.slug != form.slug:
        base_slug = slugify(payload.slug)
        slug = base_slug
        counter = 1
        while db.query(models.DynamicForm).filter((models.DynamicForm.slug == slug) & (models.DynamicForm.id != form.id)).first():
            slug = f"{base_slug}-{counter}"
            counter += 1
        form.slug = slug
    if payload.fields_schema is not None:
        form.fields_schema = json.dumps([f.model_dump() for f in payload.fields_schema], ensure_ascii=False)
    if payload.is_active is not None:
        form.is_active = payload.is_active

    form.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(form)

    count = db.query(models.FormSubmission).filter(models.FormSubmission.form_id == form.id).count()
    return schemas.ApiResponse(
        success=True,
        data=parse_form_out(form, count),
        message="Formulir berhasil diperbarui"
    )

@router.delete("/{id}", response_model=schemas.ApiResponse[None])
def delete_form(
    id: str,
    current_user: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Delete dynamic form & all its submissions (Admin only)."""
    form = db.query(models.DynamicForm).filter(models.DynamicForm.id == id).first()
    if not form:
        raise HTTPException(status_code=404, detail="Formulir tidak ditemukan")

    db.delete(form)
    db.commit()
    return schemas.ApiResponse(success=True, message="Formulir berhasil dihapus")

@router.get("/{id}/submissions", response_model=schemas.ApiResponse[List[schemas.FormSubmissionOut]])
def get_form_submissions(
    id: str,
    current_user: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get all submissions for a dynamic form (Admin only)."""
    form = db.query(models.DynamicForm).filter(models.DynamicForm.id == id).first()
    if not form:
        raise HTTPException(status_code=404, detail="Formulir tidak ditemukan")

    subs = db.query(models.FormSubmission).filter(
        models.FormSubmission.form_id == form.id
    ).order_by(models.FormSubmission.submitted_at.desc()).all()

    results = []
    for s in subs:
        try:
            ans = json.loads(s.answers_json) if s.answers_json else {}
        except Exception:
            ans = {}
        results.append(schemas.FormSubmissionOut(
            id=s.id,
            form_id=s.form_id,
            answers=ans,
            submitted_at=s.submitted_at
        ))

    return schemas.ApiResponse(success=True, data=results)

@router.delete("/submissions/{submission_id}", response_model=schemas.ApiResponse[None])
def delete_submission(
    submission_id: str,
    current_user: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Delete a single submission (Admin only)."""
    sub = db.query(models.FormSubmission).filter(models.FormSubmission.id == submission_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Tanggapan tidak ditemukan")

    db.delete(sub)
    db.commit()
    return schemas.ApiResponse(success=True, message="Tanggapan berhasil dihapus")

@router.get("/{id_or_slug}/export-csv")
def export_form_csv(
    id_or_slug: str,
    db: Session = Depends(get_db)
):
    """Export all submissions to a formatted CSV spreadsheet."""
    form = db.query(models.DynamicForm).filter(
        (models.DynamicForm.id == id_or_slug) | (models.DynamicForm.slug == id_or_slug)
    ).first()
    if not form:
        raise HTTPException(status_code=404, detail="Formulir tidak ditemukan")

    try:
        fields = json.loads(form.fields_schema) if form.fields_schema else []
    except Exception:
        fields = []

    subs = db.query(models.FormSubmission).filter(
        models.FormSubmission.form_id == form.id
    ).order_by(models.FormSubmission.submitted_at.asc()).all()

    output = io.StringIO()
    # Write UTF-8 BOM so Excel opens indonesian special characters cleanly
    output.write('\ufeff')
    writer = csv.writer(output, delimiter=',', quoting=csv.QUOTE_MINIMAL)

    # 1. Build Header Row from Questions
    headers = ["No", "ID Respon", "Waktu Pengisian (WIB)"]
    for f in fields:
        label = f.get("label") or f.get("id") or "Pertanyaan"
        headers.append(label)
    writer.writerow(headers)

    # 2. Build Data Rows
    for idx, s in enumerate(subs, 1):
        try:
            ans = json.loads(s.answers_json) if s.answers_json else {}
        except Exception:
            ans = {}
        
        # Format timestamp
        time_str = s.submitted_at.strftime("%d/%m/%Y %H:%M:%S") if s.submitted_at else "-"
        row = [idx, s.id, time_str]

        for f in fields:
            f_id = f.get("id")
            val = ans.get(f_id, "")
            if isinstance(val, list):
                val_str = ", ".join(str(v) for v in val)
            elif isinstance(val, dict):
                val_str = json.dumps(val, ensure_ascii=False)
            else:
                val_str = str(val) if val is not None else ""
            row.append(val_str)

        writer.writerow(row)

    output.seek(0)
    clean_title = re.sub(r"[^\w\s-]", "", form.title).strip().replace(" ", "_")
    filename = f"Respon_{clean_title}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )
