from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.auth.dependencies import get_current_admin, get_current_coach
from app.auth.security import hash_password
from app.database import get_db
from app.models.models import User as UserModel, Entrenador as EntrenadorModel, ROLE_ADMIN, ROLE_COACH, VALID_ROLES
from app.schemas.schemas import UserRead, UserCreate, UserUpdate, Entrenador as EntrenadorSchema

router = APIRouter()


@router.get("/users", response_model=List[UserRead])
def listar_usuarios(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), _: UserModel = Depends(get_current_admin)):
    users = db.query(UserModel).offset(skip).limit(limit).all()
    return users


@router.post("/users", response_model=UserRead)
def crear_usuario(
    payload: UserCreate,
    db: Session = Depends(get_db),
    _: UserModel = Depends(get_current_admin),
):
    if payload.role not in VALID_ROLES:
        raise HTTPException(status_code=400, detail=f"Rol inválido. Debe ser uno de: {VALID_ROLES}")
    if db.query(UserModel).filter(UserModel.email == payload.email).first():
        raise HTTPException(status_code=409, detail="El email ya está registrado")
    user = UserModel(
        email=payload.email,
        nombre_completo=payload.nombre_completo,
        hashed_password=hash_password(payload.password),
        role=payload.role,
        activo=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/users/{user_id}", response_model=UserRead)
def obtener_usuario(user_id: int, db: Session = Depends(get_db), _: UserModel = Depends(get_current_admin)):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user


@router.put("/users/{user_id}", response_model=UserRead)
def actualizar_usuario(user_id: int, payload: UserUpdate, db: Session = Depends(get_db), _: UserModel = Depends(get_current_admin)):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    if payload.nombre_completo is not None:
        user.nombre_completo = payload.nombre_completo
    if payload.role is not None:
        if payload.role not in VALID_ROLES:
            raise HTTPException(status_code=400, detail=f"Rol inválido. Debe ser uno de: {VALID_ROLES}")
        user.role = payload.role
    db.commit()
    db.refresh(user)
    return user


@router.patch("/users/{user_id}/activate", response_model=UserRead)
def activar_usuario(user_id: int, db: Session = Depends(get_db), _: UserModel = Depends(get_current_admin)):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    user.activo = True
    db.commit()
    db.refresh(user)
    return user


@router.patch("/users/{user_id}/deactivate", response_model=UserRead)
def desactivar_usuario(user_id: int, db: Session = Depends(get_db), _: UserModel = Depends(get_current_admin)):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    if user.role == ROLE_ADMIN:
        raise HTTPException(status_code=400, detail="No se puede desactivar un administrador")
    user.activo = False
    db.commit()
    db.refresh(user)
    return user


@router.get("/entrenadores/disponibles-para-coach", response_model=List[EntrenadorSchema])
def entrenadores_disponibles(db: Session = Depends(get_db), _: UserModel = Depends(get_current_admin)):
    return db.query(EntrenadorModel).filter(EntrenadorModel.user_id.is_(None)).all()


@router.post("/users/{user_id}/asociar-entrenador/{entrenador_id}")
def asociar_entrenador(user_id: int, entrenador_id: int, db: Session = Depends(get_db), _: UserModel = Depends(get_current_admin)):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    if user.role != ROLE_COACH:
        raise HTTPException(status_code=400, detail="El usuario debe tener rol COACH para asociarlo a un entrenador")
    entrenador = db.query(EntrenadorModel).filter(EntrenadorModel.id == entrenador_id).first()
    if not entrenador:
        raise HTTPException(status_code=404, detail="Entrenador no encontrado")
    existing = db.query(UserModel).filter(UserModel.id != user_id, UserModel.role == ROLE_COACH).all()
    for u in existing:
        ent = db.query(EntrenadorModel).filter(EntrenadorModel.user_id == u.id).first()
        if ent and ent.id == entrenador_id:
            raise HTTPException(status_code=409, detail="Este entrenador ya está asociado a otro usuario activo")
    if entrenador.user_id is not None:
        raise HTTPException(status_code=409, detail="Este entrenador ya está asociado a un usuario")
    user.ultimo_acceso = user.ultimo_acceso
    entrenador.user_id = user_id
    db.commit()
    db.refresh(entrenador)
    return {"mensaje": f"Usuario {user.email} asociado al entrenador {entrenador.nombre}"}
