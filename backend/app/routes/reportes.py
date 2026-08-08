from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date, datetime
from typing import Optional, List
from app.schemas.schemas import ReporteResumen
from app.database import get_db
from app.models.models import (
    Asistencia as AsistenciaModel, Alumno, Entrenador, ClaseHorario,
    AlumnoEntrenamiento as AlumnoEntrenamientoModel,
    Entrenamiento as EntrenamientoModel,
    Entrenador as EntrenadorModel, ROLE_ADMIN,
)
from app.auth.dependencies import get_current_user

router = APIRouter()

CATEGORIAS_ENTRENAMIENTO = ['tecnica', 'pies', 'sparring', 'acondicionamiento', 'defensa', 'cardio']


def get_user_entrenador_id(db: Session, user) -> Optional[int]:
    ent = db.query(EntrenadorModel).filter(EntrenadorModel.user_id == user.id).first()
    return ent.id if ent else None


def get_alumnos_query(db: Session, current_user):
    if current_user.role == ROLE_ADMIN:
        return db.query(Alumno).filter(Alumno.activo == True)
    entrenador = get_user_entrenador_id(db, current_user)
    if not entrenador:
        raise HTTPException(status_code=403, detail="Usuario sin entrenador asociado")
    return db.query(Alumno).filter(Alumno.activo == True, Alumno.entrenador_id == entrenador)


def get_asistencia_query_base(db: Session, current_user):
    if current_user.role == ROLE_ADMIN:
        return db.query(AsistenciaModel)
    entrenador = get_user_entrenador_id(db, current_user)
    if not entrenador:
        raise HTTPException(status_code=403, detail="Usuario sin entrenador asociado")
    return db.query(AsistenciaModel).filter(AsistenciaModel.entrenador_id == entrenador)


def get_alumno_entrenamiento_query_base(db: Session, current_user):
    if current_user.role == ROLE_ADMIN:
        return db.query(AlumnoEntrenamientoModel)
    entrenador = get_user_entrenador_id(db, current_user)
    if not entrenador:
        raise HTTPException(status_code=403, detail="Usuario sin entrenador asociado")
    alumno_ids_subq = db.query(Alumno.id).filter(Alumno.entrenador_id == entrenador)
    return db.query(AlumnoEntrenamientoModel).filter(AlumnoEntrenamientoModel.alumno_id.in_(alumno_ids_subq))


@router.get("/resumen", response_model=List[ReporteResumen])
def reporte_resumen(
    desde: Optional[str] = Query(None),
    hasta: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    alumnos = get_alumnos_query(db, current_user).all()
    resultado = []
    for alumno in alumnos:
        query = db.query(AsistenciaModel).filter(AsistenciaModel.alumno_id == alumno.id)
        if desde:
            try:
                query = query.filter(AsistenciaModel.fecha >= date.fromisoformat(desde))
            except ValueError:
                raise HTTPException(status_code=400, detail="Formato de fecha inválido en 'desde'")
        if hasta:
            try:
                query = query.filter(AsistenciaModel.fecha <= date.fromisoformat(hasta))
            except ValueError:
                raise HTTPException(status_code=400, detail="Formato de fecha inválido en 'hasta'")
        asistencias = query.all()
        total = len(asistencias)
        por_entrenador = []
        por_horario = []
        if current_user.role == ROLE_ADMIN:
            entrenadores = db.query(Entrenador).all()
            horarios = db.query(ClaseHorario).all()
        else:
            user_eid = get_user_entrenador_id(db, current_user)
            entrenadores = [e for e in db.query(Entrenador).all() if e.id == user_eid]
            horarios = db.query(ClaseHorario).all()
        for ent in entrenadores:
            count = sum(1 for a in asistencias if a.entrenador_id == ent.id)
            por_entrenador.append({"entrenador_id": ent.id, "entrenador_nombre": ent.nombre, "count": count})
        for hor in horarios:
            count = sum(1 for a in asistencias if a.horario_id == hor.id)
            por_horario.append({"horario_id": hor.id, "horario_nombre": hor.nombre, "count": count})
        resultado.append(ReporteResumen(
            alumno_id=alumno.id,
            alumno_nombre=alumno.nombre_completo,
            total_asistencias=total,
            por_entrenador=por_entrenador,
            por_horario=por_horario,
        ))
    return resultado

@router.get("/asistencia-por-alumno")
def asistencia_por_alumno(
    desde: Optional[str] = Query(None),
    hasta: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    alumnos = get_alumnos_query(db, current_user).all()
    query_base = get_asistencia_query_base(db, current_user)
    if desde:
        try:
            query_base = query_base.filter(AsistenciaModel.fecha >= date.fromisoformat(desde))
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de fecha inválido en 'desde'")
    if hasta:
        try:
            query_base = query_base.filter(AsistenciaModel.fecha <= date.fromisoformat(hasta))
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de fecha inválido en 'hasta'")
    asistencias = query_base.all()
    por_alumno = {}
    horario_counts = {}
    for a in asistencias:
        por_alumno.setdefault(a.alumno_id, []).append(a)
        horario_counts.setdefault(a.alumno_id, {})
        horario_counts[a.alumno_id][a.horario_id] = horario_counts[a.alumno_id].get(a.horario_id, 0) + 1
    resultado = []
    for alumno in alumnos:
        asis = por_alumno.get(alumno.id, [])
        total = len(asis)
        ultima_fecha = None
        for a in asis:
            if ultima_fecha is None or a.fecha > ultima_fecha:
                ultima_fecha = a.fecha
        dias_desde_ultima = (datetime.utcnow().date() - ultima_fecha).days if ultima_fecha is not None else None
        hc = horario_counts.get(alumno.id, {})
        horario_mas_frecuente_id = max(hc, key=hc.get) if hc else None
        horario_mas_frecuente_nombre = None
        if horario_mas_frecuente_id is not None:
            hor = db.query(ClaseHorario).filter(ClaseHorario.id == horario_mas_frecuente_id).first()
            horario_mas_frecuente_nombre = hor.nombre if hor else None
        resultado.append({
            "alumno_id": alumno.id,
            "alumno_nombre": alumno.nombre_completo,
            "total_clases_asistidas": total,
            "dias_desde_ultima_asistencia": dias_desde_ultima,
            "horario_mas_frecuente_id": horario_mas_frecuente_id,
            "horario_mas_frecuente_nombre": horario_mas_frecuente_nombre,
        })
    resultado.sort(key=lambda x: x["dias_desde_ultima_asistencia"] if x["dias_desde_ultima_asistencia"] is not None else -1, reverse=True)
    return resultado

@router.get("/cobertura-entrenamientos")
def cobertura_entrenamientos(
    desde: Optional[str] = Query(None),
    hasta: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    alumnos = get_alumnos_query(db, current_user).all()
    entrenamientos_query = get_alumno_entrenamiento_query_base(db, current_user).filter(AlumnoEntrenamientoModel.estado == "realizado")
    if desde:
        try:
            entrenamientos_query = entrenamientos_query.filter(AlumnoEntrenamientoModel.fecha >= date.fromisoformat(desde))
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de fecha inválido en 'desde'")
    if hasta:
        try:
            entrenamientos_query = entrenamientos_query.filter(AlumnoEntrenamientoModel.fecha <= date.fromisoformat(hasta))
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de fecha inválido en 'hasta'")
    asignaciones = entrenamientos_query.all()
    por_alumno = {}
    for ae in asignaciones:
        por_alumno.setdefault(ae.alumno_id, set()).add(ae.entrenamiento_id)
    entrenamientos_por_categoria = {}
    for ent in db.query(EntrenamientoModel).all():
        entrenamientos_por_categoria[ent.id] = ent.categoria
    resultado = []
    for alumno in alumnos:
        cats = set()
        for ent_id in por_alumno.get(alumno.id, set()):
            cat = entrenamientos_por_categoria.get(ent_id)
            if cat:
                cats.add(cat)
        faltantes = [c for c in CATEGORIAS_ENTRENAMIENTO if c not in cats]
        if faltantes:
            resultado.append({
                "alumno_id": alumno.id,
                "alumno_nombre": alumno.nombre_completo,
                "categorias_cubiertas": sorted(cats),
                "categorias_faltantes": sorted(faltantes),
            })
    return resultado

@router.get("/carga-entrenadores")
def carga_entrenadores(
    desde: Optional[str] = Query(None),
    hasta: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role == ROLE_ADMIN:
        entrenadores = db.query(Entrenador).all()
    else:
        user_eid = get_user_entrenador_id(db, current_user)
        entrenadores = db.query(Entrenador).filter(Entrenador.id == user_eid).all()
    resultado = []
    for ent in entrenadores:
        asis_query = db.query(AsistenciaModel).filter(AsistenciaModel.entrenador_id == ent.id)
        if desde:
            try:
                asis_query = asis_query.filter(AsistenciaModel.fecha >= date.fromisoformat(desde))
            except ValueError:
                raise HTTPException(status_code=400, detail="Formato de fecha inválido en 'desde'")
        if hasta:
            try:
                asis_query = asis_query.filter(AsistenciaModel.fecha <= date.fromisoformat(hasta))
            except ValueError:
                raise HTTPException(status_code=400, detail="Formato de fecha inválido en 'hasta'")
        asistencias = asis_query.all()
        alumnos_distintos = len(set(a.alumno_id for a in asistencias))
        ent_query = get_alumno_entrenamiento_query_base(db, current_user)
        if desde:
            try:
                ent_query = ent_query.filter(AlumnoEntrenamientoModel.fecha >= date.fromisoformat(desde))
            except ValueError:
                raise HTTPException(status_code=400, detail="Formato de fecha inválido en 'desde'")
        if hasta:
            try:
                ent_query = ent_query.filter(AlumnoEntrenamientoModel.fecha <= date.fromisoformat(hasta))
            except ValueError:
                raise HTTPException(status_code=400, detail="Formato de fecha inválido en 'hasta'")
        entrenamientos_asignados = ent_query.filter(AlumnoEntrenamientoModel.entrenador_id == ent.id).count()
        resultado.append({
            "entrenador_id": ent.id,
            "entrenador_nombre": ent.nombre,
            "total_asistencias_atendidas": len(asistencias),
            "total_alumnos_distintos": alumnos_distintos,
            "total_entrenamientos_asignados": entrenamientos_asignados,
        })
    return resultado

@router.get("/asistencia-por-horario")
def asistencia_por_horario(
    desde: Optional[str] = Query(None),
    hasta: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    horarios = db.query(ClaseHorario).all()
    resultado = []
    for hor in horarios:
        query = get_asistencia_query_base(db, current_user).filter(AsistenciaModel.horario_id == hor.id)
        if desde:
            try:
                query = query.filter(AsistenciaModel.fecha >= date.fromisoformat(desde))
            except ValueError:
                raise HTTPException(status_code=400, detail="Formato de fecha inválido en 'desde'")
        if hasta:
            try:
                query = query.filter(AsistenciaModel.fecha <= date.fromisoformat(hasta))
            except ValueError:
                raise HTTPException(status_code=400, detail="Formato de fecha inválido en 'hasta'")
        total = query.count()
        resultado.append({
            "horario_id": hor.id,
            "horario_nombre": hor.nombre,
            "total_asistencias": total,
        })
    return resultado

@router.get("/cumplimiento-entrenamientos")
def cumplimiento_entrenamientos(
    desde: Optional[str] = Query(None),
    hasta: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    alumnos = get_alumnos_query(db, current_user).all()
    base_query = get_alumno_entrenamiento_query_base(db, current_user)
    if desde:
        try:
            base_query = base_query.filter(AlumnoEntrenamientoModel.fecha >= date.fromisoformat(desde))
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de fecha inválido en 'desde'")
    if hasta:
        try:
            base_query = base_query.filter(AlumnoEntrenamientoModel.fecha <= date.fromisoformat(hasta))
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de fecha inválido en 'hasta'")
    asignaciones = base_query.all()
    por_alumno = {}
    for ae in asignaciones:
        por_alumno.setdefault(ae.alumno_id, {"planificados": 0, "realizados": 0})
        if ae.estado == "planificado":
            por_alumno[ae.alumno_id]["planificados"] += 1
        elif ae.estado == "realizado":
            por_alumno[ae.alumno_id]["realizados"] += 1
    resultado = []
    for alumno in alumnos:
        datos = por_alumno.get(alumno.id, {"planificados": 0, "realizados": 0})
        total = datos["planificados"] + datos["realizados"]
        tasa = (datos["realizados"] / total) if total > 0 else None
        resultado.append({
            "alumno_id": alumno.id,
            "alumno_nombre": alumno.nombre_completo,
            "planificados": datos["planificados"],
            "realizados": datos["realizados"],
            "tasa_cumplimiento": round(tasa, 2) if tasa is not None else None,
        })
    return resultado
