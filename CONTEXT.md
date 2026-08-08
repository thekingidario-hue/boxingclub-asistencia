# BoxingClub Los Andes — Contexto del Proyecto

Esta carpeta contiene información permanente de contexto para que cualquier IA, desarrollador o herramienta pueda entender rápidamente de qué trata este proyecto, cómo está estructurado y qué decisiones importantes se tomaron.

## 1. Resumen

**BoxingClub Los Andes** es una aplicación web móvil-first para el control de asistencia y seguimiento de entrenamientos de una escuela de boxeo.  
No es un e-commerce ni una red social: es una herramienta operativa para que entrenadores registren asistencias, planifiquen entrenamientos y revisen reportes básicos de alumnos.

## 2. Stack

- **Backend:** FastAPI + SQLAlchemy + SQLite
- **Frontend:** React + Vite + Tailwind CSS
- **Documentación API:** Swagger UI en `/docs`
- **Comunicación:** Fetch nativo desde React a FastAPI (CORS abierto en desarrollo)
- **Auth:** JWT (HS256) + bcrypt; roles ADMIN y COACH
- **Testing:** pytest (backend), vitest (frontend)
- **Auth:** JWT (HS256) + bcrypt; roles `ADMIN` y `COACH`
- **Testing:** pytest (backend), vitest (frontend)

## 3. Estructura

```
backend/
  app/
    main.py           # App FastAPI, CORS, routers
    database.py       # Engine, sesiones, seed
    models/
      models.py       # Modelos SQLAlchemy
    schemas/
      schemas.py      # Pydantic schemas
    routes/
      alumnos.py      # CRUD alumnos, soft delete, fusión
      entrenadores.py # CRUD entrenadores
      horarios.py     # CRUD horarios
      asistencia.py   # Registro/edición/eliminación de asistencias
      entrenamientos.py # CRUD catálogo de entrenamientos
      alumno_entrenamientos.py # Rutas anidadas /alumnos/{id}/entrenamientos
      reportes.py     # Reportes enriquecidos
  requirements.txt
  venv/

frontend/
  src/
    App.jsx           # Componente principal: 4 tabs + modales
    index.css         # Tailwind + estilos base
  tailwind.config.js
  package.json
```

## 4. Entidades principales

### Alumno
- `id`, `nombre_completo`, `telefono`, `activo` (bool), `fecha_registro`
- Soft delete mediante `activo = False`
- Tiene muchas `asistencias` y `alumno_entrenamientos`

### Entrenador
- `id`, `nombre`, `activo`
- Referenciado en `asistencias` y `alumno_entrenamientos`

### ClaseHorario
- `id`, `nombre`, `hora_inicio`, `hora_fin`
- Ejemplos: mañana, tarde, noche

### Asistencia
- `id`, `alumno_id`, `entrenador_id`, `horario_id`, `fecha`, `presente`, `observacion`, `creado_en`
- Unique constraint: `(alumno_id, fecha, horario_id, entrenador_id)`
- Representa una clase asistida por un alumno con uno o varios entrenadores

### Entrenamiento
- `id`, `nombre`, `categoria`, `descripcion`, `dia_sugerido`
- `video_url`, `thumbnail`, `duracion`, `nivel`, `objetivo`, `equipamiento`, `ejercicios`
- `activo`, `creado_en`
- Catálogo de tipos de entrenamiento (técnica, pies, sparring, etc.)

### AlumnoEntrenamiento
- `id`, `alumno_id`, `entrenamiento_id`, `entrenador_id`, `asistencia_id`, `fecha`, `estado` (planificado/realizado), `notas`, `creado_en`
- Vincula un alumno con un entrenamiento asignado, independientemente de la asistencia

## 5. Frontend — Tabs y flujo

La app tiene 4 pestañas en este orden:

1. **Alumnos** — Lista de alumnos activos, búsqueda, botones perfil/editar/eliminar, detector de duplicados, modal nuevo alumno.
2. **Tomar Asistencia** — Selector de fecha y horario, búsqueda de alumno, selección múltiple de entrenadores, confirmación de asistencia. Lista de "ya asistieron" con edición/borrado.
3. **Entrenamientos** — Biblioteca visual de entrenamientos con grid/lista, buscador, filtros por categoría y día, estadísticas rápidas, detalle de entrenamiento y CRUD completo.
4. **Historial** — Selector de fechas, botón "Generar Reporte", secciones: huecos de entrenamiento, asistencia por horario, cumplimiento de entrenamientos.

### Modales globales
- Nuevo alumno
- Editar alumno
- Eliminar alumno (con advertencia de preservación de datos)
- Asignar/editar entrenamiento a alumno (desde perfil)
- Eliminar asignación

## 6. Endpoints principales

### Alumnos
- `GET /alumnos` — Solo activos por defecto
- `GET /alumnos?incluir_inactivos=true` — Todos
- `POST /alumnos` — Crear
- `PUT /alumnos/{id}` — Editar
- `DELETE /alumnos/{id}` — Soft delete
- `DELETE /alumnos/{id}?force=true` — Hard delete
- `POST /alumnos/{id}/fusionar` — Fusionar duplicados

### Entrenadores
- `GET /entrenadores`
- `POST /entrenadores`
- `PUT /entrenadores/{id}`
- `DELETE /entrenadores/{id}`

### Horarios
- `GET /horarios`
- `POST /horarios`
- `PUT /horarios/{id}`
- `DELETE /horarios/{id}`

### Asistencia
- `POST /asistencia` — Registrar con `entrenador_ids` array
- `GET /asistencia` — Listar con filtros `fecha` y `horario_id`
- `GET /asistencia/alumno/{alumno_id}` — Historial por alumno
- `PUT /asistencia/{id}` — Editar observación
- `DELETE /asistencia/{id}` — Eliminar individual
- `PUT /asistencia/alumno/{alumno_id}/fecha/{fecha}/horario/{horario_id}` — Reemplazar entrenadores de una asistencia
- `DELETE /asistencia/alumno/{alumno_id}/fecha/{fecha}/horario/{horario_id}` — Eliminar todas las asistencias de un alumno en un horario/fecha

### Entrenamientos
- `GET /entrenamientos/` — Lista activos con filtros `categoria` y `dia`. Devuelve campos extendidos.
- `POST /entrenamientos/` — Crear con campos extendidos opcionales.
- `PUT /entrenamientos/{id}` — Editar campos extendidos.
- `DELETE /entrenamientos/{id}` — Soft delete (`activo=False`).

### AlumnoEntrenamientos (rutas anidadas)
- `GET /alumnos/{alumno_id}/entrenamientos/`
- `POST /alumnos/{alumno_id}/entrenamientos/`
- `PUT /alumnos/{alumno_id}/entrenamientos/{asignacion_id}`
- `DELETE /alumnos/{alumno_id}/entrenamientos/{asignacion_id}`

### Reportes
- `GET /reportes/resumen` — Resumen viejo (se mantiene)
- `GET /reportes/asistencia-por-alumno` — Alumnos ordenados por días sin asistir
- `GET /reportes/cobertura-entrenamientos` — Categorías faltantes por alumno
- `GET /reportes/carga-entrenadores` — Carga de trabajo por entrenador
- `GET /reportes/asistencia-por-horario` — Asistencias por horario
- `GET /reportes/cumplimiento-entrenamientos` — Tasa de cumplimiento por alumno

## 8. Decisiones técnicas importantes

1. **SQLite** como base de datos: simple, sin servidor, suficiente para un gimnasio chico-mediano.
2. **Soft delete** para alumnos y entrenamientos: preserva historial. Solo se permite hard delete con `?force=true` y con advertencia.
3. **Multi-entrenador por asistencia**: una asistencia puede tener varios entrenadores, representados como múltiples registros `Asistencia` con el mismo `alumno_id`, `fecha` y `horario_id` pero distinto `entrenador_id`.
4. **Rutas anidadas** para entrenamientos de alumnos: `/alumnos/{id}/entrenamientos/`.
5. **CORS abierto** (`allow_origins=["*"]`) en desarrollo.
6. **FastAPI redirect** sin trailing slash: el frontend siempre usa `/path/` con slash final.
7. **Alias en imports** para evitar conflictos: `from app.models.models import Alumno as AlumnoModel`.
8. **Seed inicial**: 3 entrenadores y 3 horarios por defecto. Los alumnos se crean manualmente.
9. **Frontend proxy**: el frontend llama a `http://localhost:8000` directo (no proxy de Vite).
10. **Mobile-first**: UI diseñada para celular, max-width `max-w-lg`, botones grandes, sticky header + tabs.
11. **Módulo Entrenamientos responsive**: contenedor adaptativo hasta `max-w-7xl`, grid 1/2/3 columnas según viewport, modal de detalle 1 columna en móvil y 2 columnas en desktop, videos `aspect-video`, filtros con scroll horizontal en móvil.

## 9. Datos de seed inicial

- **Entrenadores:** Miguel Martinez, Iván Álvarez, Moises Jimenez
- **Horarios:** mañana (06:00-07:30), tarde (16:00-17:30), noche (19:00-20:30)
- **Alumnos:** se cargan manualmente desde la app

## 10. Cómo levantar

### Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- App: http://localhost:5173

## 11. Estado actual

- Backend funcionando con todos los bloques A-I.
- Multi-user auth implementado (JWT + bcrypt, roles ADMIN/COACH, ownership aplicado).
- Frontend compilando y con 4 tabs funcionales.
- Base de datos SQLite en `backend/boxingclub.db`.
- Endpoints de reportes enriquecidos funcionando.
- Módulo de Entrenamientos rediseñado con experiencia de biblioteca visual.
- Modelo de Entrenamiento enriquecido con `video_url`, `thumbnail`, `duracion`, `nivel`, `objetivo`, `equipamiento`, `ejercicios`.
- Migración SQLite aplicada automáticamente al iniciar el backend.
- **Multi-user**: autenticación JWT + bcrypt con roles `ADMIN` y `COACH`. Cada COACH ve solo sus alumnos y datos asociados. Ownership aplicado en alumnos, asistencia, alumno_entrenamientos y reportes. ADMIN accede global. Entrenamientos globales (COACH lectura, ADMIN CRUD). Horarios globales.

## 12. Auth y Multi-User

- **Modelo User**: `id`, `email` (UNIQUE+INDEX), `nombre_completo`, `hashed_password`, `role` (ADMIN/COACH), `activo`, `creado_en`, `ultimo_acceso`
- **User ↔ Entrenador**: relación 1:1 (`entrenador.user_id`), nullable. El admin (entrenador id=1) está vinculado al usuario admin.
- **Ownership**: el `entrenador_id` del entrenador autenticado filtra resultados en alumnos, asistencia, alumno_entrenamientos y reportes.
- **JWT**: expiración de 60 minutos, header `Authorization: Bearer <token>`.
- **Credenciales admin**: `admin@boxingclub.local` / definidas en `.env` (no hardcodeadas).

### Endpoints de Auth y Users

#### Auth
- `POST /auth/login` — Login con email + password, devuelve `access_token`, `token_type`, `user`
- `GET /auth/users/me` — Usuario actual (requiere auth)

#### Users (solo ADMIN)
- `GET /users` — Listar usuarios
- `POST /users` — Crear usuario (COACH/ADMIN)
- `GET /users/{id}` — Obtener usuario
- `PUT /users/{id}` — Editar usuario
- `PATCH /users/{id}/activate` — Activar usuario
- `PATCH /users/{id}/deactivate` — Desactivar usuario (no admins)
- `POST /users/{id}/asociar-entrenador/{entrenador_id}` — Asociar COACH a entrenador
- `GET /entrenadores/disponibles-para-coach` — Entrenadores sin usuario asociado


