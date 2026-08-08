# BoxingClub Los Andes

App web móvil-first para el control de asistencia y seguimiento de entrenamientos de la escuela de boxeo **BoxingClub Los Andes**.

## Stack

- **Backend:** FastAPI + SQLAlchemy + SQLite
- **Frontend:** React + Vite + Tailwind CSS
- **Documentación API:** Swagger UI en `/docs`
- **Auth:** JWT + bcrypt; roles `ADMIN` y `COACH`

## Estructura

```
backend/
  app/
    main.py                # FastAPI app, CORS, routers
    database.py            # Engine, sesiones, seed
    models/
      models.py            # Modelos SQLAlchemy
    schemas/
      schemas.py           # Pydantic schemas
    routes/
      alumnos.py           # CRUD alumnos, soft delete, fusión de duplicados
      entrenadores.py      # CRUD entrenadores
      horarios.py          # CRUD horarios
      asistencia.py        # Registro/edición/eliminación de asistencias
      entrenamientos.py    # CRUD catálogo de entrenamientos
      alumno_entrenamientos.py # Rutas anidadas /alumnos/{id}/entrenamientos
      reportes.py          # Reportes enriquecidos
  requirements.txt
  venv/

frontend/
  src/
    App.jsx                # Componente principal: 4 tabs + modales
    index.css              # Tailwind + estilos base
  tailwind.config.js
  package.json
```

## Levantar Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

- API: http://localhost:8000
- Docs (Swagger): http://localhost:8000/docs

Al iniciar, se crean automáticamente las tablas y se insertan 3 entrenadores y 3 horarios por defecto.

## Levantar Frontend

```bash
cd frontend
npm install
npm run dev
```

- App: http://localhost:5173

## Pantallas

1. **Alumnos** — Listado, búsqueda, edición, eliminación soft/hard, detección y fusión de duplicados, perfil de alumno con historial de entrenamientos.
2. **Tomar Asistencia** — Registro de asistencia por fecha, horario y entrenadores. Edición y eliminación de asistencias.
3. **Entrenamientos** — Biblioteca visual de entrenamientos con grid/lista, buscador, filtros por categoría y día, estadísticas rápidas, detalle de entrenamiento y CRUD completo. Diseño responsive: móvil 1 columna, tablet 2 columnas, desktop hasta 3 columnas con contenedor amplio.
4. **Historial** — Selector de fechas, botón "Generar Reporte", secciones: huecos de entrenamiento, asistencia por horario, cumplimiento de entrenamientos.

## Campos de Entrenamiento

- `nombre`
- `categoria`
- `descripcion`
- `dia_sugerido`
- `video_url`
- `thumbnail`
- `duracion` (minutos)
- `nivel` (principiante/intermedio/avanzado)
- `objetivo`
- `equipamiento`
- `ejercicios`
- `activo`


## Funcionalidades principales

- Registro de asistencias con múltiples entrenadores por clase
- Catálogo de entrenamientos y asignación por alumno
- Módulo de Entrenamientos rediseñado como biblioteca visual: grid/lista, buscador, filtros por categoría y día, estadísticas rápidas, detalle modal, preparado para video_url/thumbnail/duración/nivel/objetivo/equipamiento/ejercicios
- Reportes accionables para seguimiento de alumnos
- Fusión de alumnos duplicados con preservación de historial
- Soft delete para alumnos y entrenamientos

## Datos de seed inicial

- **Entrenadores:** Miguel Martinez, Iván Álvarez, Moises Jimenez
- **Horarios:** mañana (06:00-07:30), tarde (16:00-17:30), noche (19:00-20:30)
- **Alumnos:** se cargan manualmente desde la app

## Notas

- Backend y frontend se comunican por fetch directo a `http://localhost:8000` (sin proxy de Vite).
- CORS abierto en desarrollo.
- FastAPI redirige rutas sin trailing slash; el frontend siempre usa `/path/` con slash final.
- La base de datos es SQLite en `backend/boxingclub.db`.
- Al iniciar, el backend ejecuta automáticamente una migración para agregar columnas nuevas a `entrenamientos` sin perder datos.

## Autenticación y Multi-User

La aplicación soporta dos roles:

- **ADMIN**: acceso global a todos los datos. Puede crear/editar/desactivar usuarios, asociar entrenadores a usuarios.
- **COACH**: ve solo sus alumnos, asistencias, asignaciones y reportes. Puede crear/editar alumnos (ownership automático), registrar asistencias, asignar entrenamientos a sus alumnos.

### Auth

- **JWT**: expiración de 60 minutos, enviado en header `Authorization: Bearer <token>`.
- **Endpoints**: `POST /auth/login` (público), `GET /auth/users/me` (requiere auth).

### Users (solo ADMIN)

- `GET /users` — Listar usuarios
- `POST /users` — Crear usuario (rol COACH o ADMIN)
- `GET /users/{id}` — Obtener usuario
- `PUT /users/{id}` — Editar usuario
- `PATCH /users/{id}/activate` — Activar usuario
- `PATCH /users/{id}/deactivate` — Desactivar usuario (no admins)
- `POST /users/{id}/asociar-entrenador/{entrenador_id}` — Asociar COACH a entrenador
- `GET /entrenadores/disponibles-para-coach` — Entrenadores sin usuario asociado

### Ownership

- Cada COACH ve solo sus alumnos (filtrado por `entrenador_id`).
- Admin ve todos los alumnos.
- Entrenamientos son globales: COACH puede leer, ADMIN puede crear/editar/borrar.
- Horarios son globales.
- Reportes filtran datos por ownership.

### Credenciales admin

- **Email**: `admin@boxingclub.local`
- **Password**: definido en `.env` (clave segura generada)
