from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.auth.security import verify_password, create_access_token
from app.auth.dependencies import get_current_user
from app.config import settings
from app.database import get_db
from app.models.models import User as UserModel, ROLE_ADMIN
from app.schemas.schemas import LoginRequest, LoginResponse, UserRead

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo",
        )
    user.ultimo_acceso = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)
    token = create_access_token({"sub": str(user.id), "role": user.role})
    return LoginResponse(access_token=token, user=UserRead.model_validate(user))


@router.get("/users/me", response_model=UserRead)
def users_me(current_user=Depends(get_current_user)):
    return UserRead.model_validate(current_user)
