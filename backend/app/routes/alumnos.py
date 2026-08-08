from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.schemas.schemas import AlumnoBase, AlumnoCreate, AlumnoUpdate, Alumno, AsignarEntrenadorSchema, AsignarMasivoSchema
from app.database import get_db
from app.models.models import (
    Alumno as AlumnoModel, Asistencia as AsistenciaModel,
    AlumnoEntrenamiento as AlumnoEntrenamientoModel,
    Entrenador as EntrenadorModel, ROLE_ADMIN,
)
from app.auth.dependencies import get_current_user, get_current_coach, get_current_admin

router = APIRouter()


def get_alumnos_query(db: Session, current_user):
    if current_user.role == ROLE_ADMIN:
        return db.query(AlumnoModel)
    entrenador = db.query(EntrenadorModel).filter(EntrenadorModel.user_id == current_user.id).first()
    if not entrenador:
        raise HTTPException(status_code=403, detail="Usuario sin entrenador asociado")
    return db.query(AlumnoModel).filter(AlumnoModel.entrenador_id == entrenador.id)


@router.get("/", response_model=List[Alumno])
def listar_alumnos(
    incluir_inactivos: bool = Query(False),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    query = get_alumnos_query(db, current_user)
    if not incluir_inactivos:
        query = query.filter(AlumnoModel.activo == True)
    return query.all()

@router.post("/", response_model=Alumno)
def crear_alumno(
    alumno: AlumnoCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role == ROLE_ADMIN:
        if alumno.entrenador_id is None:
            raise HTTPException(status_code=400, detail="ADMIN debe especificar entrenador_id")
        ent = db.query(EntrenadorModel).filter(EntrenadorModel.id == alumno.entrenador_id).first()
        if not ent:
            raise HTTPException(status_code=404, detail="Entrenador no encontrado")
        db_alumno = AlumnoModel(
            nombre_completo=alumno.nombre_completo,
            telefono=alumno.telefono,
            activo=alumno.activo,
            entrenador_id=alumno.entrenador_id,
        )
    else:
        entrenador = db.query(EntrenadorModel).filter(EntrenadorModel.user_id == current_user.id).first()
        if not entrenador:
            raise HTTPException(status_code=403, detail="Usuario sin entrenador asociado")
        db_alumno = AlumnoModel(
            nombre_completo=alumno.nombre_completo,
            telefono=alumno.telefono,
            activo=alumno.activo,
            entrenador_id=entrenador.id,
        )
    db.add(db_alumno)
    db.commit()
    db.refresh(db_alumno)
    return db_alumno

@router.get("/sin-entrenador", response_model=List[Alumno])
def alumnos_sin_entrenador(
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    alumnos = db.query(AlumnoModel).filter(
        AlumnoModel.entrenador_id.is_(None),
        AlumnoModel.activo == True,
    ).all()
    return alumnos

@router.patch("/{alumno_id}/entrenador", response_model=Alumno)
def asignar_entrenador_alumno(
    alumno_id: int,
    data: AsignarEntrenadorSchema,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    db_alumno = db.query(AlumnoModel).filter(AlumnoModel.id == alumno_id).first()
    if not db_alumno:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")

    if data.entrenador_id is not None:
        entrenador = db.query(EntrenadorModel).filter(EntrenadorModel.id == data.entrenador_id).first()
        if not entrenador:
            raise HTTPException(status_code=400, detail="Entrenador no existe")

    db_alumno.entrenador_id = data.entrenador_id
    db.commit()
    db.refresh(db_alumno)
    return db_alumno

@router.patch("/asignar-entrenador")
def asignar_entrenador_masivo(
    data: AsignarMasivoSchema,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    if not data.alumno_ids:
        raise HTTPException(status_code=400, detail="No hay alumnos para asignar")

    entrenador = db.query(EntrenadorModel).filter(EntrenadorModel.id == data.entrenador_id).first()
    if not entrenador:
        raise HTTPException(status_code=400, detail="Entrenador no existe")

    alumnos = db.query(AlumnoModel).filter(AlumnoModel.id.in_(data.alumno_ids)).all()
    if len(alumnos) != len(data.alumno_ids):
        raise HTTPException(status_code=404, detail="Uno o más alumnos no existen")

    for alumno in alumnos:
        alumno.entrenador_id = data.entrenador_id

    db.commit()
    return {"actualizado": len(alumnos)}

@router.get("/{alumno_id}", response_model=Alumno)
def obtener_alumno(alumno_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    db_alumno = db.query(AlumnoModel).filter(AlumnoModel.id == alumno_id).first()
    if not db_alumno:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")
    if current_user.role != ROLE_ADMIN:
        user_eid = get_user_entrenador_id(db, current_user)
        if db_alumno.entrenador_id and db_alumno.entrenador_id != user_eid:
            raise HTTPException(status_code=403, detail="No tienes permiso para acceder a este alumno")
    return db_alumno

@router.put("/{alumno_id}", response_model=Alumno)
def editar_alumno(
    alumno_id: int,
    alumno: AlumnoUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    db_alumno = db.query(AlumnoModel).filter(AlumnoModel.id == alumno_id).first()
    if not db_alumno:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")
    if current_user.role != ROLE_ADMIN:
        if db_alumno.entrenador_id and db_alumno.entrenador_id != get_user_entrenador_id(db, current_user):
            raise HTTPException(status_code=403, detail="No tienes permiso para editar este alumno")
        if alumno.entrenador_id is not None and alumno.entrenador_id != db_alumno.entrenador_id:
            raise HTTPException(status_code=403, detail="No puedes cambiar el entrenador de un alumno")
    if alumno.nombre_completo is not None:
        db_alumno.nombre_completo = alumno.nombre_completo
    if alumno.telefono is not None:
        db_alumno.telefono = alumno.telefono
    if alumno.activo is not None:
        db_alumno.activo = alumno.activo
    if alumno.entrenador_id is not None and current_user.role == ROLE_ADMIN:
        db_alumno.entrenador_id = alumno.entrenador_id
    db.commit()
    db.refresh(db_alumno)
    return db_alumno

def get_user_entrenador_id(db: Session, user):
    ent = db.query(EntrenadorModel).filter(EntrenadorModel.user_id == user.id).first()
    return ent.id if ent else None

@router.delete("/{alumno_id}")
def eliminar_alumno(
    alumno_id: int,
    force: bool = Query(False),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    db_alumno = db.query(AlumnoModel).filter(AlumnoModel.id == alumno_id).first()
    if not db_alumno:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")
    if current_user.role != ROLE_ADMIN:
        if db_alumno.entrenador_id and db_alumno.entrenador_id != get_user_entrenador_id(db, current_user):
            raise HTTPException(status_code=403, detail="No tienes permiso para eliminar este alumno")

    asistencias = db.query(AsistenciaModel).filter(AsistenciaModel.alumno_id == alumno_id).count()
    entrenamientos = db.query(AlumnoEntrenamientoModel).filter(AlumnoEntrenamientoModel.alumno_id == alumno_id).count()

    if force:
        db.query(AlumnoEntrenamientoModel).filter(AlumnoEntrenamientoModel.alumno_id == alumno_id).delete()
        db.query(AsistenciaModel).filter(AsistenciaModel.alumno_id == alumno_id).delete()
        db.delete(db_alumno)
        db.commit()
        return {
            "mensaje": f"Alumno '{db_alumno.nombre_completo}' eliminado completamente",
            "asistencias_eliminadas": asistencias,
            "entrenamientos_eliminados": entrenamientos,
        }

    db_alumno.activo = False
    db.commit()
    return {
        "mensaje": f"Alumno '{db_alumno.nombre_completo}' desactivado",
        "asistencias_preservadas": asistencias,
        "entrenamientos_preservados": entrenamientos,
        "nota": "El historial se conserva para auditoría",
    }

@router.post("/{alumno_id}/fusionar")
def fusionar_alumnos(
    alumno_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    principal = db.query(AlumnoModel).filter(AlumnoModel.id == alumno_id).first()
    if not principal:
        raise HTTPException(status_code=404, detail="Alumno principal no encontrado")
    if current_user.role != ROLE_ADMIN:
        if principal.entrenador_id and principal.entrenador_id != get_user_entrenador_id(db, current_user):
            raise HTTPException(status_code=403, detail="No tienes permiso para este alumno")

    ids_duplicados = payload.get("ids_duplicados", [])
    nombre_final = payload.get("nombre_final")
    if not ids_duplicados or not isinstance(ids_duplicados, list):
        raise HTTPException(status_code=400, detail="ids_duplicados debe ser una lista")

    duplicados = db.query(AlumnoModel).filter(AlumnoModel.id.in_(ids_duplicados)).all()
    if len(duplicados) != len(ids_duplicados):
        raise HTTPException(status_code=404, detail="Alguno de los duplicados no existe")

    if current_user.role != ROLE_ADMIN:
        user_eid = get_user_entrenador_id(db, current_user)
        for dup in duplicados:
            if dup.entrenador_id and dup.entrenador_id != user_eid:
                raise HTTPException(status_code=403, detail="No tienes permiso para fusionar uno de los duplicados")

    asistencias_reasignadas = 0
    entrenamientos_reasignados = 0

    for dup in duplicados:
        asistencias = db.query(AsistenciaModel).filter(AsistenciaModel.alumno_id == dup.id).all()
        for asi in asistencias:
            existente = (
                db.query(AsistenciaModel)
                .filter(
                    AsistenciaModel.alumno_id == principal.id,
                    AsistenciaModel.fecha == asi.fecha,
                    AsistenciaModel.horario_id == asi.horario_id,
                    AsistenciaModel.entrenador_id == asi.entrenador_id,
                )
                .first()
            )
            if not existente:
                asi.alumno_id = principal.id
                asistencias_reasignadas += 1
            else:
                db.delete(asi)

        ent_asis = db.query(AlumnoEntrenamientoModel).filter(AlumnoEntrenamientoModel.alumno_id == dup.id).all()
        for ae in ent_asis:
            ae.alumno_id = principal.id
            entrenamientos_reasignados += 1

        db.delete(dup)

    if nombre_final:
        principal.nombre_completo = nombre_final

    db.commit()
    return {
        "mensaje": f"Fusionados {len(ids_duplicados)} duplicados",
        "asistencias_reasignadas": asistencias_reasignadas,
        "entrenamientos_reasignados": entrenamientos_reasignados,
        "ids_eliminados": ids_duplicados,
    }
