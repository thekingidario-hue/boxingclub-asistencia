from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.auth.security import decode_access_token
from app.database import get_db
from app.models.models import User as UserModel, Entrenador as EntrenadorModel, ROLE_ADMIN, ROLE_COACH

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> UserModel:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No autenticado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    user = db.query(UserModel).filter(UserModel.id == int(user_id)).first()
    if user is None:
        raise credentials_exception
    if not user.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo",
        )
    return user


def get_current_admin(current_user=Depends(get_current_user)) -> UserModel:
    if current_user.role != ROLE_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permiso denegado: se requiere rol ADMIN",
        )
    return current_user


def get_current_coach(current_user=Depends(get_current_user), db: Session = Depends(get_db)) -> EntrenadorModel:
    if current_user.role not in [ROLE_ADMIN, ROLE_COACH]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permiso denegado: se requiere rol COACH",
        )
    entrenador = db.query(EntrenadorModel).filter(
        EntrenadorModel.user_id == current_user.id,
        EntrenadorModel.activo == True,
    ).first()
    if not entrenador:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El usuario no está asociado a un entrenador activo",
        )
    return entrenador
