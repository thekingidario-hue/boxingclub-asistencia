from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional, List
from app.schemas.schemas import AlumnoEntrenamiento, AlumnoEntrenamientoCreateNested, AlumnoEntrenamientoUpdate
from app.database import get_db
from app.models.models import (
    AlumnoEntrenamiento as AlumnoEntrenamientoModel,
    Alumno, Entrenamiento, Entrenador, Asistencia,
    Entrenador as EntrenadorModel, ROLE_ADMIN,
)
from app.auth.dependencies import get_current_user

router = APIRouter()


def get_user_entrenador_id(db: Session, user) -> Optional[int]:
    ent = db.query(EntrenadorModel).filter(EntrenadorModel.user_id == user.id).first()
    return ent.id if ent else None


def can_access_alumno(db: Session, alumno_id: int, current_user) -> Alumno:
    alumno = db.query(Alumno).filter(Alumno.id == alumno_id).first()
    if not alumno:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")
    if current_user.role != ROLE_ADMIN:
        user_eid = get_user_entrenador_id(db, current_user)
        if alumno.entrenador_id and alumno.entrenador_id != user_eid:
            raise HTTPException(status_code=403, detail="No tienes permiso para este alumno")
    return alumno


def alumno_entrenamiento_to_detalle(ae: AlumnoEntrenamientoModel, db: Session) -> AlumnoEntrenamiento:
    alumno = db.query(Alumno).filter(Alumno.id == ae.alumno_id).first()
    entrenamiento = db.query(Entrenamiento).filter(Entrenamiento.id == ae.entrenamiento_id).first()
    entrenador = db.query(Entrenador).filter(Entrenador.id == ae.entrenador_id).first() if ae.entrenador_id else None
    return AlumnoEntrenamiento(
        id=ae.id,
        alumno_id=ae.alumno_id,
        entrenamiento_id=ae.entrenamiento_id,
        entrenador_id=ae.entrenador_id,
        asistencia_id=ae.asistencia_id,
        fecha=ae.fecha,
        estado=ae.estado,
        notas=ae.notas,
        creado_en=ae.creado_en,
        alumno_nombre=alumno.nombre_completo if alumno else "",
        entrenamiento_nombre=entrenamiento.nombre if entrenamiento else "",
        entrenador_nombre=entrenador.nombre if entrenador else None,
    )


@router.get("/", response_model=List[AlumnoEntrenamiento])
def listar_entrenamientos_alumno(
    alumno_id: int,
    estado: Optional[str] = Query(None),
    desde: Optional[str] = Query(None),
    hasta: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    can_access_alumno(db, alumno_id, current_user)
    query = db.query(AlumnoEntrenamientoModel).filter(AlumnoEntrenamientoModel.alumno_id == alumno_id)
    if estado:
        query = query.filter(AlumnoEntrenamientoModel.estado == estado)
    if desde:
        try:
            query = query.filter(AlumnoEntrenamientoModel.fecha >= date.fromisoformat(desde))
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de fecha inválido en 'desde'")
    if hasta:
        try:
            query = query.filter(AlumnoEntrenamientoModel.fecha <= date.fromisoformat(hasta))
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de fecha inválido en 'hasta'")
    query = query.order_by(AlumnoEntrenamientoModel.fecha.desc())
    asignaciones = query.all()
    return [alumno_entrenamiento_to_detalle(a, db) for a in asignaciones]

@router.post("/", response_model=AlumnoEntrenamiento)
def crear_entrenamiento_alumno(
    alumno_id: int,
    datos: AlumnoEntrenamientoCreateNested,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    alumno = can_access_alumno(db, alumno_id, current_user)
    entrenamiento = db.query(Entrenamiento).filter(Entrenamiento.id == datos.entrenamiento_id).first()
    if not entrenamiento:
        raise HTTPException(status_code=404, detail="Entrenamiento no encontrado")
    if datos.entrenador_id:
        if current_user.role != ROLE_ADMIN:
            user_eid = get_user_entrenador_id(db, current_user)
            if datos.entrenador_id != user_eid:
                raise HTTPException(status_code=403, detail="No puedes asignar entrenamientos a otro entrenador")
        entrenador = db.query(Entrenador).filter(Entrenador.id == datos.entrenador_id).first()
        if not entrenador:
            raise HTTPException(status_code=404, detail="Entrenador no encontrado")
    if datos.asistencia_id:
        asistencia = db.query(Asistencia).filter(Asistencia.id == datos.asistencia_id).first()
        if not asistencia:
            raise HTTPException(status_code=404, detail="Asistencia no encontrada")
        if asistencia.alumno_id != alumno_id:
            raise HTTPException(status_code=400, detail="La asistencia no corresponde al alumno indicado")
    db_ae = AlumnoEntrenamientoModel(alumno_id=alumno_id, **datos.dict())
    db.add(db_ae)
    db.commit()
    db.refresh(db_ae)
    return alumno_entrenamiento_to_detalle(db_ae, db)

@router.put("/{asignacion_id}", response_model=AlumnoEntrenamiento)
def editar_entrenamiento_alumno(
    alumno_id: int,
    asignacion_id: int,
    datos: AlumnoEntrenamientoUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    can_access_alumno(db, alumno_id, current_user)
    db_ae = db.query(AlumnoEntrenamientoModel).filter(
        AlumnoEntrenamientoModel.id == asignacion_id,
        AlumnoEntrenamientoModel.alumno_id == alumno_id,
    ).first()
    if not db_ae:
        raise HTTPException(status_code=404, detail="Asignación no encontrada")
    if current_user.role != ROLE_ADMIN:
        user_eid = get_user_entrenador_id(db, current_user)
        if datos.entrenador_id is not None and datos.entrenador_id != user_eid:
            raise HTTPException(status_code=403, detail="No puedes cambiar el entrenador de una asignación ajenas")

    if datos.entrenamiento_id is not None:
        ent = db.query(Entrenamiento).filter(Entrenamiento.id == datos.entrenamiento_id).first()
        if not ent:
            raise HTTPException(status_code=404, detail="Entrenamiento no encontrado")
        db_ae.entrenamiento_id = datos.entrenamiento_id
    if datos.entrenador_id is not None:
        if datos.entrenador_id:
            ent = db.query(Entrenador).filter(Entrenador.id == datos.entrenador_id).first()
            if not ent:
                raise HTTPException(status_code=404, detail="Entrenador no encontrado")
        db_ae.entrenador_id = datos.entrenador_id
    if datos.asistencia_id is not None:
        if datos.asistencia_id:
            asi = db.query(Asistencia).filter(Asistencia.id == datos.asistencia_id).first()
            if not asi:
                raise HTTPException(status_code=404, detail="Asistencia no encontrada")
            if asi.alumno_id != alumno_id:
                raise HTTPException(status_code=400, detail="La asistencia no corresponde al alumno indicado")
        db_ae.asistencia_id = datos.asistencia_id
    if datos.fecha is not None:
        db_ae.fecha = datos.fecha
    if datos.estado is not None:
        db_ae.estado = datos.estado
    if datos.notas is not None:
        db_ae.notas = datos.notas
    db.commit()
    db.refresh(db_ae)
    return alumno_entrenamiento_to_detalle(db_ae, db)

@router.delete("/{asignacion_id}")
def eliminar_entrenamiento_alumno(
    alumno_id: int,
    asignacion_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    can_access_alumno(db, alumno_id, current_user)
    db_ae = db.query(AlumnoEntrenamientoModel).filter(
        AlumnoEntrenamientoModel.id == asignacion_id,
        AlumnoEntrenamientoModel.alumno_id == alumno_id,
    ).first()
    if not db_ae:
        raise HTTPException(status_code=404, detail="Asignación no encontrada")
    db.delete(db_ae)
    db.commit()
    return {"message": "Asignación eliminada"}
