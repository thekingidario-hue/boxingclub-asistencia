from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from app import schemas
from app.database import get_db
from app.models.models import Entrenamiento
from app.auth.dependencies import get_current_user, get_current_admin

router = APIRouter()

@router.get("/", response_model=List[schemas.Entrenamiento])
def listar_entrenamientos(
    categoria: Optional[str] = Query(None),
    dia: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    query = db.query(Entrenamiento).filter(Entrenamiento.activo == True)
    if categoria:
        query = query.filter(Entrenamiento.categoria == categoria)
    if dia:
        query = query.filter(Entrenamiento.dia_sugerido == dia)
    return query.all()

@router.get("/{entrenamiento_id}", response_model=schemas.Entrenamiento)
def detalle_entrenamiento(
    entrenamiento_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    ent = db.query(Entrenamiento).filter(Entrenamiento.id == entrenamiento_id, Entrenamiento.activo == True).first()
    if not ent:
        raise HTTPException(status_code=404, detail="Entrenamiento no encontrado")
    return ent

@router.post("/", response_model=schemas.Entrenamiento)
def crear_entrenamiento(
    entrenamiento: schemas.EntrenamientoCreate,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    db_ent = Entrenamiento(**entrenamiento.dict())
    db.add(db_ent)
    db.commit()
    db.refresh(db_ent)
    return db_ent

@router.put("/{entrenamiento_id}", response_model=schemas.Entrenamiento)
def editar_entrenamiento(
    entrenamiento_id: int,
    entrenamiento: schemas.EntrenamientoUpdate,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    db_ent = db.query(Entrenamiento).filter(Entrenamiento.id == entrenamiento_id).first()
    if not db_ent:
        raise HTTPException(status_code=404, detail="Entrenamiento no encontrado")
    if entrenamiento.nombre is not None:
        db_ent.nombre = entrenamiento.nombre
    if entrenamiento.categoria is not None:
        db_ent.categoria = entrenamiento.categoria
    if entrenamiento.descripcion is not None:
        db_ent.descripcion = entrenamiento.descripcion
    if entrenamiento.dia_sugerido is not None:
        db_ent.dia_sugerido = entrenamiento.dia_sugerido
    if entrenamiento.video_url is not None:
        db_ent.video_url = entrenamiento.video_url
    if entrenamiento.thumbnail is not None:
        db_ent.thumbnail = entrenamiento.thumbnail
    if entrenamiento.duracion is not None:
        db_ent.duracion = entrenamiento.duracion
    if entrenamiento.nivel is not None:
        db_ent.nivel = entrenamiento.nivel
    if entrenamiento.objetivo is not None:
        db_ent.objetivo = entrenamiento.objetivo
    if entrenamiento.equipamiento is not None:
        db_ent.equipamiento = entrenamiento.equipamiento
    if entrenamiento.ejercicios is not None:
        db_ent.ejercicios = entrenamiento.ejercicios
    if entrenamiento.activo is not None:
        db_ent.activo = entrenamiento.activo
    db.commit()
    db.refresh(db_ent)
    return db_ent

@router.delete("/{entrenamiento_id}")
def desactivar_entrenamiento(
    entrenamiento_id: int,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    db_ent = db.query(Entrenamiento).filter(Entrenamiento.id == entrenamiento_id).first()
    if not db_ent:
        raise HTTPException(status_code=404, detail="Entrenamiento no encontrado")
    db_ent.activo = False
    db.commit()
    return {"message": "Entrenamiento desactivado"}
