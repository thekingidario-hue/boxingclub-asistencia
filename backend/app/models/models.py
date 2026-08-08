import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Date, Time, DateTime, ForeignKey, UniqueConstraint, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

ROLE_ADMIN = "ADMIN"
ROLE_COACH = "COACH"
VALID_ROLES = [ROLE_ADMIN, ROLE_COACH]


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, nullable=False, unique=True, index=True)
    nombre_completo = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False, default=ROLE_COACH)
    activo = Column(Boolean, default=True)
    creado_en = Column(DateTime, default=datetime.utcnow)
    ultimo_acceso = Column(DateTime, nullable=True)


class Alumno(Base):
    __tablename__ = "alumnos"
    id = Column(Integer, primary_key=True, index=True)
    nombre_completo = Column(String, nullable=False)
    telefono = Column(String, nullable=True)
    activo = Column(Boolean, default=True)
    fecha_registro = Column(DateTime, default=datetime.utcnow)
    entrenador_id = Column(Integer, ForeignKey("entrenadores.id"), nullable=True)

class Entrenador(Base):
    __tablename__ = "entrenadores"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, unique=True)
    nombre = Column(String, nullable=False)
    activo = Column(Boolean, default=True)

class ClaseHorario(Base):
    __tablename__ = "clases_horarios"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    hora_inicio = Column(Time, nullable=False)
    hora_fin = Column(Time, nullable=False)

class Asistencia(Base):
    __tablename__ = "asistencias"
    id = Column(Integer, primary_key=True, index=True)
    alumno_id = Column(Integer, ForeignKey("alumnos.id"), nullable=False)
    entrenador_id = Column(Integer, ForeignKey("entrenadores.id"), nullable=False)
    horario_id = Column(Integer, ForeignKey("clases_horarios.id"), nullable=False)
    fecha = Column(Date, nullable=False)
    presente = Column(Boolean, default=True)
    observacion = Column(String, nullable=True)
    creado_en = Column(DateTime, default=datetime.utcnow)
    __table_args__ = (
        UniqueConstraint("alumno_id", "fecha", "horario_id", "entrenador_id", name="uq_alumno_fecha_horario_entrenador"),
    )

class Entrenamiento(Base):
    __tablename__ = "entrenamientos"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    categoria = Column(String, nullable=False)
    descripcion = Column(Text, nullable=True)
    dia_sugerido = Column(String, nullable=True)
    video_url = Column(String, nullable=True)
    thumbnail = Column(String, nullable=True)
    duracion = Column(Integer, nullable=True)
    nivel = Column(String, nullable=True)
    objetivo = Column(Text, nullable=True)
    equipamiento = Column(Text, nullable=True)
    ejercicios = Column(Text, nullable=True)
    activo = Column(Boolean, default=True)
    creado_en = Column(DateTime, default=datetime.utcnow)

class AlumnoEntrenamiento(Base):
    __tablename__ = "alumno_entrenamientos"
    id = Column(Integer, primary_key=True, index=True)
    alumno_id = Column(Integer, ForeignKey("alumnos.id"), nullable=False)
    entrenamiento_id = Column(Integer, ForeignKey("entrenamientos.id"), nullable=False)
    entrenador_id = Column(Integer, ForeignKey("entrenadores.id"), nullable=True)
    asistencia_id = Column(Integer, ForeignKey("asistencias.id"), nullable=True)
    fecha = Column(Date, nullable=False)
    estado = Column(String, nullable=False, default="planificado")
    notas = Column(Text, nullable=True)
    creado_en = Column(DateTime, default=datetime.utcnow)
