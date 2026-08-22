from datetime import datetime
from sqlalchemy import Column, String, Integer, Text, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String(50), primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="admin", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Pengumuman(Base):
    __tablename__ = "pengumuman"

    id = Column(String(50), primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, index=True, nullable=False)
    category = Column(String(50), nullable=False) # 'kegiatan', 'oprec', 'ultah', 'lainnya'
    content = Column(Text, nullable=False)
    image_url = Column(String(500), nullable=True)
    date_published = Column(String(50), nullable=False)
    author = Column(String(100), default="Pengurus PMK", nullable=False)
    views = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Divisi(Base):
    __tablename__ = "divisi"

    id = Column(String(50), primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    order_priority = Column(Integer, default=0)

    members = relationship("Pengurus", back_populates="divisi", cascade="all, delete-orphan")

class Pengurus(Base):
    __tablename__ = "pengurus"

    id = Column(String(50), primary_key=True, index=True)
    divisi_id = Column(String(50), ForeignKey("divisi.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    role = Column(String(100), nullable=False)
    photo_url = Column(String(500), nullable=True)
    period = Column(String(50), nullable=False) # e.g. "2025/2026"
    order_priority = Column(Integer, default=0)

    divisi = relationship("Divisi", back_populates="members")

class FormLink(Base):
    __tablename__ = "form_links"

    key = Column(String(50), primary_key=True, index=True) # 'maba', 'alumni', 'kepanitiaan'
    title = Column(String(150), nullable=False)
    google_form_url = Column(String(500), nullable=False)
    is_active = Column(Integer, default=1, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
