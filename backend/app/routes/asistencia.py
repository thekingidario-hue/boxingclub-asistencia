from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional, List
from app.schemas.schemas import AsistenciaCreate, AsistenciaBatchCreate, AsistenciaUpdate, Asistencia, AsistenciaDetalle
from app.database import get_db
from app.models.models import (
    Asistencia as AsistenciaModel, Alumno, Entrenador, ClaseHorario,
    Entrenador as EntrenadorModel, ROLE_ADMIN,
)
from app.auth.dependencies import get_current_user

router = APIRouter()


def get_user_entrenador_id(db: Session, user) -> Optional[int]:
    ent = db.query(EntrenadorModel).filter(EntrenadorModel.user_id == user.id).first()
    return ent.id if ent else None


def get_asistencia_query(db: Session, current_user):
    if current_user.role == ROLE_ADMIN:
        return db.query(AsistenciaModel)
    entrenador = get_user_entrenador_id(db, current_user)
    if not entrenador:
        raise HTTPException(status_code=403, detail="Usuario sin entrenador asociado")
    return db.query(AsistenciaModel).filter(AsistenciaModel.entrenador_id == entrenador)


@router.post("/", response_model=List[Asistencia])
def registrar_asistencia(
    asistencia: AsistenciaBatchCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role != ROLE_ADMIN:
        user_ent_id = get_user_entrenador_id(db, current_user)
        if not user_ent_id:
            raise HTTPException(status_code=403, detail="Usuario sin entrenador asociado")
        if set(asistencia.entrenador_ids) != {user_ent_id}:
            raise HTTPException(status_code=403, detail="No puedes registrar asistencia con entrenadores que no te pertenecen")
    if not asistencia.entrenador_ids:
        raise HTTPException(status_code=400, detail="Debe seleccionar al menos un entrenador")
    creados = []
    for entrenador_id in asistencia.entrenador_ids:
        existe = db.query(AsistenciaModel).filter(
            AsistenciaModel.alumno_id == asistencia.alumno_id,
            AsistenciaModel.fecha == asistencia.fecha,
            AsistenciaModel.horario_id == asistencia.horario_id,
            AsistenciaModel.entrenador_id == entrenador_id,
        ).first()
        if existe:
            raise HTTPException(status_code=409, detail=f"Ya existe asistencia registrada para este alumno con el entrenador {entrenador_id} en este horario y fecha")
        db_asistencia = AsistenciaModel(
            alumno_id=asistencia.alumno_id,
            entrenador_id=entrenador_id,
            horario_id=asistencia.horario_id,
            fecha=asistencia.fecha,
            observacion=asistencia.observacion,
        )
        db.add(db_asistencia)
        creados.append(db_asistencia)
    db.commit()
    for c in creados:
        db.refresh(c)
    return creados

def asistencia_to_detalle(a: AsistenciaModel, db: Session) -> AsistenciaDetalle:
    alumno = db.query(Alumno).filter(Alumno.id == a.alumno_id).first()
    entrenador = db.query(Entrenador).filter(Entrenador.id == a.entrenador_id).first()
    horario = db.query(ClaseHorario).filter(ClaseHorario.id == a.horario_id).first()
    return AsistenciaDetalle(
        id=a.id,
        alumno_id=a.alumno_id,
        entrenador_id=a.entrenador_id,
        horario_id=a.horario_id,
        fecha=a.fecha,
        presente=a.presente,
        observacion=a.observacion,
        creado_en=a.creado_en,
        alumno_nombre=alumno.nombre_completo if alumno else "",
        entrenador_nombre=entrenador.nombre if entrenador else "",
        horario_nombre=horario.nombre if horario else "",
    )

@router.get("/", response_model=List[AsistenciaDetalle])
def listar_asistencia(
    fecha: Optional[str] = Query(None),
    horario_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    query = get_asistencia_query(db, current_user)
    if fecha:
        try:
            f = date.fromisoformat(fecha)
            query = query.filter(AsistenciaModel.fecha == f)
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de fecha inválido. Usa YYYY-MM-DD")
    if horario_id:
        query = query.filter(AsistenciaModel.horario_id == horario_id)
    asistencias = query.all()
    return [asistencia_to_detalle(a, db) for a in asistencias]

@router.get("/alumno/{alumno_id}", response_model=List[AsistenciaDetalle])
def historial_alumno(
    alumno_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    alumno = db.query(Alumno).filter(Alumno.id == alumno_id).first()
    if not alumno:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")
    if current_user.role != ROLE_ADMIN:
        user_eid = get_user_entrenador_id(db, current_user)
        if alumno.entrenador_id and alumno.entrenador_id != user_eid:
            raise HTTPException(status_code=403, detail="No tienes permiso para ver este alumno")
    asistencias = db.query(AsistenciaModel).filter(AsistenciaModel.alumno_id == alumno_id).all()
    return [asistencia_to_detalle(a, db) for a in asistencias]

@router.delete("/{asistencia_id}")
def eliminar_asistencia(
    asistencia_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    db_asistencia = db.query(AsistenciaModel).filter(AsistenciaModel.id == asistencia_id).first()
    if not db_asistencia:
        raise HTTPException(status_code=404, detail="Asistencia no encontrada")
    if current_user.role != ROLE_ADMIN:
        user_eid = get_user_entrenador_id(db, current_user)
        if db_asistencia.entrenador_id != user_eid:
            raise HTTPException(status_code=403, detail="No tienes permiso para eliminar esta asistencia")
    db.delete(db_asistencia)
    db.commit()
    return {"message": "Asistencia eliminada"}

@router.put("/{asistencia_id}", response_model=AsistenciaDetalle)
def editar_asistencia(
    asistencia_id: int,
    datos: AsistenciaUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    db_asistencia = db.query(AsistenciaModel).filter(AsistenciaModel.id == asistencia_id).first()
    if not db_asistencia:
        raise HTTPException(status_code=404, detail="Asistencia no encontrada")
    if current_user.role != ROLE_ADMIN:
        user_eid = get_user_entrenador_id(db, current_user)
        if db_asistencia.entrenador_id != user_eid:
            raise HTTPException(status_code=403, detail="No tienes permiso para editar esta asistencia")
    if datos.observacion is not None:
        db_asistencia.observacion = datos.observacion
    db.commit()
    db.refresh(db_asistencia)
    return asistencia_to_detalle(db_asistencia, db)

@router.put("/alumno/{alumno_id}/fecha/{fecha}/horario/{horario_id}", response_model=List[AsistenciaDetalle])
def reemplazar_asistencias_alumno_clase(
    alumno_id: int,
    fecha: str,
    horario_id: int,
    datos: AsistenciaUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        f = date.fromisoformat(fecha)
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de fecha inválido. Usa YYYY-MM-DD")

    alumno = db.query(Alumno).filter(Alumno.id == alumno_id).first()
    if not alumno:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")

    if current_user.role != ROLE_ADMIN:
        user_eid = get_user_entrenador_id(db, current_user)
        if alumno.entrenador_id and alumno.entrenador_id != user_eid:
            raise HTTPException(status_code=403, detail="No tienes permiso para este alumno")
        if set(datos.entrenador_ids) != {user_eid}:
            raise HTTPException(status_code=403, detail="No puedes modificar asistencia con entrenadores que no te pertenecen")

    if not datos.entrenador_ids:
        raise HTTPException(status_code=400, detail="Debe seleccionar al menos un entrenador")

    existentes = db.query(AsistenciaModel).filter(
        AsistenciaModel.alumno_id == alumno_id,
        AsistenciaModel.fecha == f,
        AsistenciaModel.horario_id == horario_id,
    ).all()
    existentes_ids = {e.entrenador_id for e in existentes}
    nuevos_ids = set(datos.entrenador_ids)
    for e in existentes:
        if e.entrenador_id not in nuevos_ids:
            db.delete(e)
    for entrenador_id in nuevos_ids - existentes_ids:
        existe = db.query(AsistenciaModel).filter(
            AsistenciaModel.alumno_id == alumno_id,
            AsistenciaModel.fecha == f,
            AsistenciaModel.horario_id == horario_id,
            AsistenciaModel.entrenador_id == entrenador_id,
        ).first()
        if not existe:
            nuevo = AsistenciaModel(
                alumno_id=alumno_id,
                entrenador_id=entrenador_id,
                horario_id=horario_id,
                fecha=f,
                observacion=datos.observacion,
            )
            db.add(nuevo)
    db.commit()
    resultado = db.query(AsistenciaModel).filter(
        AsistenciaModel.alumno_id == alumno_id,
        AsistenciaModel.fecha == f,
        AsistenciaModel.horario_id == horario_id,
    ).all()
    return [asistencia_to_detalle(a, db) for a in resultado]

@router.delete("/alumno/{alumno_id}/fecha/{fecha}/horario/{horario_id}")
def eliminar_todos_asistencias_alumno_clase(
    alumno_id: int,
    fecha: str,
    horario_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        f = date.fromisoformat(fecha)
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de fecha inválido. Usa YYYY-MM-DD")

    alumno = db.query(Alumno).filter(Alumno.id == alumno_id).first()
    if not alumno:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")

    if current_user.role != ROLE_ADMIN:
        user_eid = get_user_entrenador_id(db, current_user)
        if alumno.entrenador_id and alumno.entrenador_id != user_eid:
            raise HTTPException(status_code=403, detail="No tienes permiso para este alumno")
        existentes = db.query(AsistenciaModel).filter(
            AsistenciaModel.alumno_id == alumno_id,
            AsistenciaModel.fecha == f,
            AsistenciaModel.horario_id == horario_id,
            AsistenciaModel.entrenador_id != user_eid,
        ).all()
        if existentes:
            raise HTTPException(status_code=403, detail="No puedes borrar asistencias de otros entrenadores")

    q = db.query(AsistenciaModel).filter(
        AsistenciaModel.alumno_id == alumno_id,
        AsistenciaModel.fecha == f,
        AsistenciaModel.horario_id == horario_id,
    )
    if current_user.role != ROLE_ADMIN:
        user_eid = get_user_entrenador_id(db, current_user)
        q = q.filter(AsistenciaModel.entrenador_id == user_eid)
    q.delete(synchronize_session=False)
    db.commit()
    return {"message": "Asistencias eliminadas"}
