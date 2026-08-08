from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import alumnos, entrenadores, horarios, asistencia, reportes, entrenamientos, alumno_entrenamientos, users
from app.auth import routes as auth_routes
from app.database import Base, seed_data, migrar_entrenamientos, migrar_entrenadores, migrar_alumnos, migrar_roles
from app import database as database_module
from contextlib import asynccontextmanager
from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    database_module.Base.metadata.create_all(bind=database_module.engine)
    from sqlalchemy.orm import Session
    db = Session(database_module.engine)
    migrar_entrenadores(db)
    migrar_entrenamientos(db)
    migrar_alumnos(db)
    migrar_roles(db)
    seed_data(db)
    db.close()
    yield


app = FastAPI(title="BoxingClub Los Andes", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(",") if settings.CORS_ORIGINS else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "BoxingClub Los Andes API"}


app.include_router(auth_routes.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="", tags=["users"])
app.include_router(alumnos.router, prefix="/alumnos", tags=["alumnos"])
app.include_router(entrenadores.router, prefix="/entrenadores", tags=["entrenadores"])
app.include_router(horarios.router, prefix="/horarios", tags=["horarios"])
app.include_router(asistencia.router, prefix="/asistencia", tags=["asistencia"])
app.include_router(reportes.router, prefix="/reportes", tags=["reportes"])
app.include_router(entrenamientos.router, prefix="/entrenamientos", tags=["entrenamientos"])
app.include_router(alumno_entrenamientos.router, prefix="/alumnos/{alumno_id}/entrenamientos", tags=["alumno_entrenamientos"])

