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
    period: str
    order_priority: Optional[int] = 0

class DivisiOut(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    order_priority: int
    members: List[PengurusOut] = []

    class Config:
        from_attributes = True

class DivisiCreate(BaseModel):
    name: str
    description: Optional[str] = None
    order_priority: Optional[int] = 0

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
