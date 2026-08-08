from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import time, datetime
from app.config import settings
from app.models.models import (
    Base, Alumno, Entrenador, ClaseHorario, Asistencia,
    Entrenamiento, AlumnoEntrenamiento, User, ROLE_ADMIN, ROLE_COACH,
)
from app.auth.security import hash_password
from sqlalchemy.orm import Session

DATABASE_URL = settings.DATABASE_URL

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def migrar_alumnos(db: Session):
    existentes = {row[1] for row in db.execute(text("PRAGMA table_info(alumnos)")).fetchall()}
    if "entrenador_id" not in existentes:
        db.execute(text("ALTER TABLE alumnos ADD COLUMN entrenador_id INTEGER REFERENCES entrenadores(id)"))
    db.commit()


def migrar_entrenadores(db: Session):
    existentes = {row[1] for row in db.execute(text("PRAGMA table_info(entrenadores)")).fetchall()}
    if "user_id" not in existentes:
        db.execute(text("ALTER TABLE entrenadores ADD COLUMN user_id INTEGER"))
        db.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS ix_entrenadores_user_id ON entrenadores (user_id)"))
    admin = db.query(User).filter(User.email == settings.ADMIN_EMAIL).first()
    if admin:
        db.execute(text(f'UPDATE entrenadores SET user_id = {admin.id} WHERE user_id IS NULL AND id = 1'))
    db.commit()


def migrar_entrenamientos(db: Session):
    columnas = {
        "video_url": "TEXT",
        "thumbnail": "TEXT",
        "duracion": "INTEGER",
        "nivel": "TEXT",
        "objetivo": "TEXT",
        "equipamiento": "TEXT",
        "ejercicios": "TEXT",
    }
    existentes = {row[1] for row in db.execute(text("PRAGMA table_info(entrenamientos)")).fetchall()}
    for columna, tipo in columnas.items():
        if columna not in existentes:
            db.execute(text(f"ALTER TABLE entrenamientos ADD COLUMN {columna} {tipo}"))
    db.commit()


def migrar_roles(db: Session):
    db.execute(text(f'UPDATE users SET role = UPPER(role) WHERE role IN ("admin", "coach")'))
    db.commit()


def seed_data(db: Session):
    if settings.ADMIN_EMAIL and settings.ADMIN_PASSWORD:
        existing = db.query(User).filter(User.email == settings.ADMIN_EMAIL).first()
        if existing:
            existing.nombre_completo = settings.ADMIN_NAME or existing.nombre_completo or "Administrador"
            existing.hashed_password = hash_password(settings.ADMIN_PASSWORD)
            existing.role = ROLE_ADMIN
            existing.activo = True
            db.commit()
        else:
            admin = User(
                email=settings.ADMIN_EMAIL,
                nombre_completo=settings.ADMIN_NAME or "Administrador",
                hashed_password=hash_password(settings.ADMIN_PASSWORD),
                role=ROLE_ADMIN,
                activo=True,
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)
        admin = db.query(User).filter(User.email == settings.ADMIN_EMAIL).first()
        db.execute(text(f"UPDATE entrenadores SET user_id = {admin.id} WHERE user_id IS NULL AND id = 1"))
        db.commit()
    if db.query(Entrenador).count() == 0:
        entrenadores = [
            Entrenador(nombre="Miguel Martinez"),
            Entrenador(nombre="Iván Álvarez"),
            Entrenador(nombre="Moises Jimenez"),
        ]
        db.add_all(entrenadores)
        db.commit()
    if db.query(ClaseHorario).count() == 0:
        horarios = [
            ClaseHorario(nombre="mañana", hora_inicio=time(8, 0), hora_fin=time(12, 0)),
            ClaseHorario(nombre="tarde", hora_inicio=time(15, 0), hora_fin=time(18, 0)),
            ClaseHorario(nombre="noche", hora_inicio=time(19, 0), hora_fin=time(21, 0)),
        ]
        db.add_all(horarios)
        db.commit()
    if db.query(Entrenamiento).count() == 0:
        entrenamientos = [
            Entrenamiento(
                nombre="Técnica de golpes (jab, directo, gancho, uppercut)",
                categoria="tecnica",
                dia_sugerido="lunes",
                descripcion="Trabajo fundamental de los 4 golpes básicos, repetición y forma",
            ),
            Entrenamiento(
                nombre="Trabajo de pies y desplazamiento",
                categoria="pies",
                dia_sugerido="martes",
                descripcion="Footwork, pivotes, entrada y salida de distancia",
            ),
            Entrenamiento(
                nombre="Sparring controlado / mitts",
                categoria="sparring",
                dia_sugerido="miercoles",
                descripcion="Práctica de contacto controlado con guantes de foco",
            ),
            Entrenamiento(
                nombre="Acondicionamiento físico",
                categoria="acondicionamiento",
                dia_sugerido="jueves",
                descripcion="Circuitos, cuerda, trabajo de core y resistencia",
            ),
            Entrenamiento(
                nombre="Defensa (slip, block, parry) y contraataque",
                categoria="defensa",
                dia_sugerido="viernes",
                descripcion="Técnicas defensivas y transición a contraataque",
            ),
            Entrenamiento(
                nombre="Sparring libre / evaluación técnica",
                categoria="sparring",
                dia_sugerido="sabado",
                descripcion="Sesión de sparring de mayor intensidad, evaluación de progreso",
            ),
        ]
        db.add_all(entrenamientos)
        db.commit()

