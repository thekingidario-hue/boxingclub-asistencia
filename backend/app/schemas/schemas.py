from datetime import datetime, date, time
from typing import Optional, List
from pydantic import BaseModel
from app.models.models import ROLE_ADMIN, ROLE_COACH


class UserBase(BaseModel):
    email: str
    nombre_completo: str
    role: str = ROLE_COACH
    activo: bool = True


class UserCreate(UserBase):
    password: str


class UserRead(BaseModel):
    id: int
    email: str
    nombre_completo: str
    role: str
    activo: bool
    creado_en: Optional[datetime] = None
    ultimo_acceso: Optional[datetime] = None

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    nombre_completo: Optional[str] = None
    role: Optional[str] = None
    activo: Optional[bool] = None


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str
    role: str = ROLE_COACH


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead


class AlumnoBase(BaseModel):
    nombre_completo: str
    telefono: Optional[str] = None
    activo: bool = True
    entrenador_id: Optional[int] = None

class AlumnoCreate(AlumnoBase):
    pass

class AlumnoUpdate(BaseModel):
    nombre_completo: Optional[str] = None
    telefono: Optional[str] = None
    activo: Optional[bool] = None
    entrenador_id: Optional[int] = None

class Alumno(AlumnoBase):
    id: int
    fecha_registro: datetime
    class Config:
        from_attributes = True

class AsignarEntrenadorSchema(BaseModel):
    entrenador_id: Optional[int] = None

class AsignarMasivoSchema(BaseModel):
    alumno_ids: List[int]
    entrenador_id: int

class EntrenadorBase(BaseModel):
    nombre: str
    activo: bool = True

class EntrenadorCreate(EntrenadorBase):
    user_id: Optional[int] = None

class Entrenador(EntrenadorBase):
    id: int
    user_id: Optional[int] = None
    class Config:
        from_attributes = True

class ClaseHorarioBase(BaseModel):
    nombre: str
    hora_inicio: time
    hora_fin: time

class ClaseHorario(ClaseHorarioBase):
    id: int
    class Config:
        from_attributes = True

class AsistenciaBase(BaseModel):
    alumno_id: int
    entrenador_id: int
    horario_id: int
    fecha: date
    observacion: Optional[str] = None

class AsistenciaCreate(AsistenciaBase):
    pass

class AsistenciaBatchCreate(BaseModel):
    alumno_id: int
    entrenador_ids: List[int]
    horario_id: int
    fecha: date
    observacion: Optional[str] = None

class AsistenciaUpdate(BaseModel):
    entrenador_ids: Optional[List[int]] = None
    observacion: Optional[str] = None

class Asistencia(AsistenciaBase):
    id: int
    presente: bool
    creado_en: datetime
    class Config:
        from_attributes = True

class AsistenciaDetalle(Asistencia):
    alumno_nombre: str
    entrenador_nombre: str
    horario_nombre: str
    class Config:
        from_attributes = True

class ReporteResumen(BaseModel):
    alumno_id: int
    alumno_nombre: str
    total_asistencias: int
    por_entrenador: List[dict]
    por_horario: List[dict]

class EntrenamientoBase(BaseModel):
    nombre: str
    categoria: str
    descripcion: Optional[str] = None
    dia_sugerido: Optional[str] = None
    video_url: Optional[str] = None
    thumbnail: Optional[str] = None
    duracion: Optional[int] = None
    nivel: Optional[str] = None
    objetivo: Optional[str] = None
    equipamiento: Optional[str] = None
    ejercicios: Optional[str] = None
    activo: bool = True

class EntrenamientoCreate(EntrenamientoBase):
    pass

class EntrenamientoUpdate(BaseModel):
    nombre: Optional[str] = None
    categoria: Optional[str] = None
    descripcion: Optional[str] = None
    dia_sugerido: Optional[str] = None
    video_url: Optional[str] = None
    thumbnail: Optional[str] = None
    duracion: Optional[int] = None
    nivel: Optional[str] = None
    objetivo: Optional[str] = None
    equipamiento: Optional[str] = None
    ejercicios: Optional[str] = None
    activo: Optional[bool] = None

class Entrenamiento(EntrenamientoBase):
    id: int
    creado_en: datetime
    class Config:
        from_attributes = True

class AlumnoEntrenamientoBase(BaseModel):
    alumno_id: int
    entrenamiento_id: int
    entrenador_id: Optional[int] = None
    asistencia_id: Optional[int] = None
    fecha: date
    estado: str = "planificado"
    notas: Optional[str] = None

class AlumnoEntrenamientoCreate(AlumnoEntrenamientoBase):
    pass

class AlumnoEntrenamientoCreateNested(BaseModel):
    entrenamiento_id: int
    entrenador_id: Optional[int] = None
    asistencia_id: Optional[int] = None
    fecha: date
    estado: str = "planificado"
    notas: Optional[str] = None

class AlumnoEntrenamientoUpdate(BaseModel):
    entrenamiento_id: Optional[int] = None
    entrenador_id: Optional[int] = None
    asistencia_id: Optional[int] = None
    fecha: Optional[date] = None
    estado: Optional[str] = None
    notas: Optional[str] = None

class AlumnoEntrenamiento(AlumnoEntrenamientoBase):
    id: int
    creado_en: datetime
    class Config:
        from_attributes = True
