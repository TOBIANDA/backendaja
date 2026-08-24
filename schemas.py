from typing import Optional, List, Generic, TypeVar, Any
from datetime import datetime
from pydantic import BaseModel, Field

T = TypeVar('T')

# Standard API Response Envelope
class ApiResponse(BaseModel, Generic[T]):
    success: bool = True
    data: Optional[T] = None
    message: Optional[str] = None
    error: Optional[str] = None

# Pagination Metadata
class PaginationMeta(BaseModel):
    page: int
    limit: int
    total: int
    totalPages: int

# Auth Schemas
class LoginRequest(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: str
    username: str
    role: str

class LoginResponse(BaseModel):
    token: str
    user: UserResponse

class ChangePasswordRequest(BaseModel):
    oldPassword: str
    newPassword: str

# Pengumuman Schemas
class PengumumanBase(BaseModel):
    title: str
    category: str # 'kegiatan' | 'oprec' | 'ultah' | 'lainnya'
    content: str
    image_url: Optional[str] = None
    date_published: str
    author: Optional[str] = "Pengurus PMK"

class PengumumanCreate(PengumumanBase):
    pass

class PengumumanUpdate(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    content: Optional[str] = None
    image_url: Optional[str] = None
    date_published: Optional[str] = None
    author: Optional[str] = None

class PengumumanOut(PengumumanBase):
    id: str
    slug: str
    views: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class PengumumanListResponse(BaseModel):
    items: List[PengumumanOut]
    pagination: PaginationMeta

# Divisi & Pengurus Schemas
class PengurusOut(BaseModel):
    id: str
    divisi_id: str
    name: str
    role: str
    photo_url: Optional[str] = None
    period: str
    order_priority: int

    class Config:
        from_attributes = True

class PengurusCreate(BaseModel):
    divisi_id: str
    name: str
    role: str
    photo_url: Optional[str] = None
    period: Optional[str] = "2025/2026"
    order_priority: Optional[int] = 0

class PengurusUpdate(BaseModel):
    divisi_id: Optional[str] = None
    name: Optional[str] = None
    role: Optional[str] = None
    photo_url: Optional[str] = None
    period: Optional[str] = None
    order_priority: Optional[int] = None

class DivisiOut(BaseModel):
    id: str
    name: str
    komisi: Optional[str] = None
    icon_name: Optional[str] = None
    description: Optional[str] = None
    group_photo_url: Optional[str] = None
    order_priority: int
    members: List[PengurusOut] = []

    class Config:
        from_attributes = True

class DivisiCreate(BaseModel):
    id: Optional[str] = None
    name: str
    komisi: Optional[str] = None
    icon_name: Optional[str] = None
    description: Optional[str] = None
    group_photo_url: Optional[str] = None
    order_priority: Optional[int] = 0

class DivisiUpdate(BaseModel):
    name: Optional[str] = None
    komisi: Optional[str] = None
    icon_name: Optional[str] = None
    description: Optional[str] = None
    group_photo_url: Optional[str] = None
    order_priority: Optional[int] = None

# Form Link Schemas
class FormLinkOut(BaseModel):
    key: str
    title: str
    google_form_url: str
    is_active: int
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class FormLinkUpdate(BaseModel):
    title: Optional[str] = None
    google_form_url: Optional[str] = None
    is_active: Optional[int] = None

# Stats Schema
class StatsOverview(BaseModel):
    totalPengumuman: int
    totalViews: int
    totalPengurus: int
    totalDivisi: int
    latestPengumuman: List[Any] = []

# Dynamic Forms Schemas
class FormFieldSchema(BaseModel):
    id: str
    label: str
    type: str # 'text' | 'textarea' | 'radio' | 'checkbox' | 'select' | 'file' | 'date'
    placeholder: Optional[str] = None
    required: bool = False
    options: Optional[List[str]] = None
    helpText: Optional[str] = None

class DynamicFormBase(BaseModel):
    title: str
    description: Optional[str] = None
    slug: Optional[str] = None
    fields_schema: List[FormFieldSchema] = []
    is_active: Optional[int] = 1

class DynamicFormCreate(DynamicFormBase):
    pass

class DynamicFormUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    slug: Optional[str] = None
    fields_schema: Optional[List[FormFieldSchema]] = None
    is_active: Optional[int] = None

class DynamicFormOut(BaseModel):
    id: str
    title: str
    slug: str
    description: Optional[str] = None
    fields_schema: List[FormFieldSchema] = []
    is_active: int
    submission_count: Optional[int] = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class FormSubmissionCreate(BaseModel):
    answers: dict # mapping of field_id/question_id -> value

class FormSubmissionOut(BaseModel):
    id: str
    form_id: str
    answers: dict
    submitted_at: datetime

    class Config:
        from_attributes = True

