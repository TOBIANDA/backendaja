from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
import models
import schemas
from utils.auth import hash_password, verify_password, create_access_token, get_current_admin

router = APIRouter(prefix="/api/auth", tags=["Auth"])

@router.post("/login", response_model=schemas.ApiResponse[schemas.LoginResponse])
def login(request: schemas.LoginRequest, db: Session = Depends(get_db)):
    """Admin login endpoint."""
    user = db.query(models.User).filter(models.User.username == request.username).first()
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username atau password salah"
        )

    token = create_access_token(data={"id": user.id, "username": user.username, "role": user.role})
    return schemas.ApiResponse(
        success=True,
        data=schemas.LoginResponse(
            token=token,
            user=schemas.UserResponse(
                id=user.id,
                username=user.username,
                role=user.role
            )
        ),
        message="Login berhasil"
    )

@router.get("/me", response_model=schemas.ApiResponse[schemas.UserResponse])
def get_me(current_user: models.User = Depends(get_current_admin)):
    """Verify active token."""
    return schemas.ApiResponse(
        success=True,
        data=schemas.UserResponse(
            id=current_user.id,
            username=current_user.username,
            role=current_user.role
        ),
        message="Token valid"
    )

@router.put("/change-password", response_model=schemas.ApiResponse[None])
def change_password(
    request: schemas.ChangePasswordRequest,
    current_user: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Change admin password."""
    if not verify_password(request.oldPassword, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Password lama tidak sesuai")

    if len(request.newPassword) < 6:
        raise HTTPException(status_code=400, detail="Password baru minimal 6 karakter")

    current_user.password_hash = hash_password(request.newPassword)
    db.commit()
    return schemas.ApiResponse(success=True, message="Password berhasil diperbarui")
