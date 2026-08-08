import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.models import User as UserModel, Entrenador as EntrenadorModel, Alumno as AlumnoModel, ROLE_ADMIN, ROLE_COACH
from app.auth.security import hash_password, create_access_token
from tests.conftest import TEST_ADMIN_EMAIL, TEST_ADMIN_PASSWORD, TEST_COACH_EMAIL, TEST_COACH_PASSWORD


def login(client: TestClient, email: str, password: str) -> str:
    resp = client.post("/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200, f"Login failed: {resp.json()}"
    return resp.json()["access_token"]


@pytest.fixture
def admin_token(client: TestClient):
    return login(client, TEST_ADMIN_EMAIL, TEST_ADMIN_PASSWORD)


@pytest.fixture
def coach_token(client: TestClient, db_session: Session):
    user = db_session.query(UserModel).filter(UserModel.email == TEST_COACH_EMAIL).first()
    if not user:
        user = UserModel(
            email=TEST_COACH_EMAIL,
            nombre_completo="Coach Test",
            hashed_password=hash_password(TEST_COACH_PASSWORD),
            role=ROLE_COACH,
            activo=True,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
    return login(client, TEST_COACH_EMAIL, TEST_COACH_PASSWORD)


@pytest.fixture
def coach_entrenador(db_session: Session):
    from sqlalchemy.orm import Session as SQLSession
    user = db_session.query(UserModel).filter(UserModel.email == TEST_COACH_EMAIL).first()
    if not user:
        user = UserModel(
            email=TEST_COACH_EMAIL,
            nombre_completo="Coach Test",
            hashed_password=hash_password(TEST_COACH_PASSWORD),
            role=ROLE_COACH,
            activo=True,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
    ent = db_session.query(EntrenadorModel).filter(EntrenadorModel.user_id == user.id).first()
    if not ent:
        ent = EntrenadorModel(nombre="Coach Ent", user_id=user.id, activo=True)
        db_session.add(ent)
        db_session.commit()
        db_session.refresh(ent)
    return ent


@pytest.fixture
def other_entrenador(db_session: Session):
    ent = db_session.query(EntrenadorModel).filter(EntrenadorModel.nombre == "Otro Entrenador").first()
    if not ent:
        ent = EntrenadorModel(nombre="Otro Entrenador", activo=True)
        db_session.add(ent)
        db_session.commit()
        db_session.refresh(ent)
    return ent


@pytest.fixture
def admin_entrenador(db_session: Session):
    user = db_session.query(UserModel).filter(UserModel.email == TEST_ADMIN_EMAIL).first()
    ent = db_session.query(EntrenadorModel).filter(EntrenadorModel.user_id == user.id).first()
    if not ent:
        ent = EntrenadorModel(nombre="Admin Ent", user_id=user.id, activo=True)
        db_session.add(ent)
        db_session.commit()
        db_session.refresh(ent)
    return ent


@pytest.fixture
def alumno_coach_a(db_session: Session, coach_entrenador):
    alumno = db_session.query(AlumnoModel).filter(AlumnoModel.nombre_completo == "Alumno Coach A").first()
    if not alumno:
        alumno = AlumnoModel(nombre_completo="Alumno Coach A", telefono="111", activo=True, entrenador_id=coach_entrenador.id)
        db_session.add(alumno)
        db_session.commit()
        db_session.refresh(alumno)
    return alumno


@pytest.fixture
def alumno_coach_b(db_session: Session, other_entrenador):
    alumno = db_session.query(AlumnoModel).filter(AlumnoModel.nombre_completo == "Alumno Coach B").first()
    if not alumno:
        alumno = AlumnoModel(nombre_completo="Alumno Coach B", telefono="222", activo=True, entrenador_id=other_entrenador.id)
        db_session.add(alumno)
        db_session.commit()
        db_session.refresh(alumno)
    return alumno


@pytest.fixture
def alumno_admin(db_session: Session, admin_entrenador):
    alumno = db_session.query(AlumnoModel).filter(AlumnoModel.nombre_completo == "Alumno Admin").first()
    if not alumno:
        alumno = AlumnoModel(nombre_completo="Alumno Admin", telefono="333", activo=True, entrenador_id=admin_entrenador.id)
        db_session.add(alumno)
        db_session.commit()
        db_session.refresh(alumno)
    return alumno


class TestAdminUsers:
    def test_admin_puede_listar_usuarios(self, client: TestClient, admin_token: str):
        resp = client.get("/users", headers={"Authorization": f"Bearer {admin_token}"})
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_admin_puede_crear_coach(self, client: TestClient, admin_token: str, db_session: Session):
        resp = client.post("/users", headers={"Authorization": f"Bearer {admin_token}"}, json={
            "email": "nuevo@coach.test",
            "nombre_completo": "Nuevo Coach",
            "password": "password123",
            "role": "COACH",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["email"] == "nuevo@coach.test"
        assert data["role"] == "COACH"
        assert "hashed_password" not in data
        db_session.query(UserModel).filter(UserModel.email == "nuevo@coach.test").delete(synchronize_session="fetch")
        db_session.commit()

    def test_coach_no_puede_listar_usuarios(self, client: TestClient, coach_token: str):
        resp = client.get("/users", headers={"Authorization": f"Bearer {coach_token}"})
        assert resp.status_code == 403

    def test_coach_no_puede_crear_usuarios(self, client: TestClient, coach_token: str):
        resp = client.post("/users", headers={"Authorization": f"Bearer {coach_token}"}, json={
            "email": "rogue@coach.test",
            "nombre_completo": "Rogue",
            "password": "password123",
            "role": "COACH",
        })
        assert resp.status_code == 403

    def test_admin_puede_activar_desactivar(self, client: TestClient, admin_token: str, db_session: Session):
        user = db_session.query(UserModel).filter(UserModel.email == "coach@boxingclub.test").first()
        resp = client.patch(f"/users/{user.id}/deactivate", headers={"Authorization": f"Bearer {admin_token}"})
        assert resp.status_code == 200
        assert resp.json()["activo"] is False

        resp = client.patch(f"/users/{user.id}/activate", headers={"Authorization": f"Bearer {admin_token}"})
        assert resp.status_code == 200
        assert resp.json()["activo"] is True

    def test_coach_no_puede_activar_desactivar(self, client: TestClient, coach_token: str, db_session: Session):
        resp = client.patch("/users/1/activate", headers={"Authorization": f"Bearer {coach_token}"})
        assert resp.status_code == 403

    def test_admin_puede_editar_usuario(self, client: TestClient, admin_token: str, db_session: Session):
        user = db_session.query(UserModel).filter(UserModel.email == "coach@boxingclub.test").first()
        resp = client.put(f"/users/{user.id}", headers={"Authorization": f"Bearer {admin_token}"}, json={
            "nombre_completo": "Coach Editado"
        })
        assert resp.status_code == 200
        assert resp.json()["nombre_completo"] == "Coach Editado"

    def test_coach_no_puede_editar_usuario(self, client: TestClient, coach_token: str):
        resp = client.put("/users/1", headers={"Authorization": f"Bearer {coach_token}"}, json={
            "nombre_completo": "Intento"
        })
        assert resp.status_code == 403


class TestOwnershipAlumnos:
    def test_coach_ve_sus_alumnos(self, client: TestClient, admin_token: str, coach_token: str, alumno_coach_a: AlumnoModel):
        resp = client.get("/alumnos/", headers={"Authorization": f"Bearer {coach_token}"})
        assert resp.status_code == 200
        data = resp.json()
        ids = [a["id"] for a in data]
        assert alumno_coach_a.id in ids

    def test_coach_no_ve_alumnos_de_otro(self, client: TestClient, coach_token: str, alumno_coach_b: AlumnoModel):
        resp = client.get("/alumnos/", headers={"Authorization": f"Bearer {coach_token}"})
        assert resp.status_code == 200
        data = resp.json()
        ids = [a["id"] for a in data]
        assert alumno_coach_b.id not in ids

    def test_coach_no_puede_ver_alumno_de_otro_coach(self, client: TestClient, coach_token: str, alumno_coach_b: AlumnoModel):
        resp = client.get(f"/alumnos/{alumno_coach_b.id}", headers={"Authorization": f"Bearer {coach_token}"})
        assert resp.status_code == 403

    def test_admin_ve_todos_los_alumnos(self, client: TestClient, admin_token: str, alumno_coach_a: AlumnoModel, alumno_coach_b: AlumnoModel):
        resp = client.get("/alumnos/", headers={"Authorization": f"Bearer {admin_token}"})
        assert resp.status_code == 200
        data = resp.json()
        ids = [a["id"] for a in data]
        assert alumno_coach_a.id in ids
        assert alumno_coach_b.id in ids

    def test_coach_crea_alumno_con_su_entrenador(self, client: TestClient, coach_token: str, db_session: Session):
        resp = client.post("/alumnos/", headers={"Authorization": f"Bearer {coach_token}"}, json={
            "nombre_completo": "Alumno Nuevo Coach",
            "telefono": "555",
        })
        assert resp.status_code == 200
        data = resp.json()
        alumno = db_session.query(AlumnoModel).filter(AlumnoModel.id == data["id"]).first()
        assert alumno.entrenador_id is not None
        from app.auth.dependencies import get_current_coach
        from app.auth.security import decode_access_token
        from app.config import settings
        from jose import jwt
        payload = jwt.decode(coach_token, settings.JWT_SECRET, algorithms=["HS256"])
        from app.models.models import Entrenador as EntrenadorModel, User as UserModel
        user = db_session.query(UserModel).filter(UserModel.id == int(payload["sub"])).first()
        ent = db_session.query(EntrenadorModel).filter(EntrenadorModel.user_id == user.id).first()
        assert alumno.entrenador_id == ent.id
        db_session.delete(alumno)
        db_session.commit()

    def test_coach_no_puede_cambiar_entrenador_alumno(self, client: TestClient, coach_token: str, alumno_coach_a: AlumnoModel):
        resp = client.put(f"/alumnos/{alumno_coach_a.id}", headers={"Authorization": f"Bearer {coach_token}"}, json={
            "entrenador_id": 999
        })
        assert resp.status_code == 403


class TestOwnershipAsistencia:
    def test_coach_puede_registrar_asistencia_de_sus_alumnos(self, client: TestClient, coach_token: str, alumno_coach_a: AlumnoModel, db_session: Session):
        from app.models.models import Entrenador as EntrenadorModel, ClaseHorario as ClaseHorarioModel
        user_id_resp = client.get("/auth/users/me", headers={"Authorization": f"Bearer {coach_token}"})
        user_id = user_id_resp.json()["id"]
        ent = db_session.query(EntrenadorModel).filter(EntrenadorModel.user_id == user_id).first()
        horario = db_session.query(ClaseHorarioModel).first()
        from datetime import date
        resp = client.post("/asistencia/", headers={"Authorization": f"Bearer {coach_token}"}, json={
            "alumno_id": alumno_coach_a.id,
            "entrenador_ids": [ent.id],
            "horario_id": horario.id,
            "fecha": str(date.today()),
        })
        assert resp.status_code == 200

    def test_coach_no_puede_registrar_asistencia_con_entrenador_ajeno(self, client: TestClient, coach_token: str, alumno_coach_a: AlumnoModel, db_session: Session):
        from app.models.models import ClaseHorario as ClaseHorarioModel
        horario = db_session.query(ClaseHorarioModel).first()
        from datetime import date
        resp = client.post("/asistencia/", headers={"Authorization": f"Bearer {coach_token}"}, json={
            "alumno_id": alumno_coach_a.id,
            "entrenador_ids": [999],
            "horario_id": horario.id,
            "fecha": str(date.today()),
        })
        assert resp.status_code == 403

    def test_coach_no_puede_ver_asistencia_de_otro(self, client: TestClient, coach_token: str, alumno_coach_a: AlumnoModel, alumno_coach_b: AlumnoModel, db_session: Session):
        from app.models.models import Entrenador as EntrenadorModel, Asistencia as AsistenciaModel, ClaseHorario as ClaseHorarioModel
        from datetime import date
        other_ent = db_session.query(EntrenadorModel).filter(EntrenadorModel.nombre == "Otro Entrenador").first()
        horario = db_session.query(ClaseHorarioModel).first()
        asis = AsistenciaModel(alumno_id=alumno_coach_b.id, entrenador_id=other_ent.id, horario_id=horario.id, fecha=date.today())
        db_session.add(asis)
        db_session.commit()
        resp = client.get(f"/asistencia/alumno/{alumno_coach_b.id}", headers={"Authorization": f"Bearer {coach_token}"})
        assert resp.status_code == 403
        db_session.delete(asis)
        db_session.commit()


class TestOwnershipAlumnoEntrenamiento:
    def test_coach_puede_asignar_entrenamiento_a_su_alumno(self, client: TestClient, coach_token: str, alumno_coach_a: AlumnoModel, db_session: Session):
        from app.models.models import Entrenamiento as EntrenamientoModel
        ent = db_session.query(EntrenamientoModel).first()
        from datetime import date
        resp = client.post(f"/alumnos/{alumno_coach_a.id}/entrenamientos/", headers={"Authorization": f"Bearer {coach_token}"}, json={
            "entrenamiento_id": ent.id,
            "fecha": str(date.today()),
            "estado": "planificado",
        })
        assert resp.status_code == 200

    def test_coach_no_puede_asignar_entrenamiento_a_alumno_de_otro(self, client: TestClient, coach_token: str, alumno_coach_b: AlumnoModel, db_session: Session):
        from app.models.models import Entrenamiento as EntrenamientoModel
        from datetime import date
        ent = db_session.query(EntrenamientoModel).first()
        resp = client.post(f"/alumnos/{alumno_coach_b.id}/entrenamientos/", headers={"Authorization": f"Bearer {coach_token}"}, json={
            "entrenamiento_id": ent.id,
            "fecha": str(date.today()),
            "estado": "planificado",
        })
        assert resp.status_code == 403


class TestEscaladaPrivilegios:
    def test_coach_no_puede_ver_admin(self, client: TestClient, coach_token: str):
        resp = client.get("/users", headers={"Authorization": f"Bearer {coach_token}"})
        assert resp.status_code == 403

    def test_coach_no_puede_crear_users(self, client: TestClient, coach_token: str):
        resp = client.post("/users", headers={"Authorization": f"Bearer {coach_token}"}, json={
            "email": "x@x.com", "nombre_completo": "X", "password": "123", "role": "COACH"
        })
        assert resp.status_code == 403

    def test_coach_no_puede_crear_entrenamiento(self, client: TestClient, coach_token: str):
        resp = client.post("/entrenamientos/", headers={"Authorization": f"Bearer {coach_token}"}, json={
            "nombre": "Test", "categoria": "tecnica"
        })
        assert resp.status_code == 403

    def test_coach_no_puede_editar_entrenamiento(self, client: TestClient, coach_token: str, db_session: Session):
        from app.models.models import Entrenamiento as EntrenamientoModel
        ent = db_session.query(EntrenamientoModel).first()
        resp = client.put(f"/entrenamientos/{ent.id}", headers={"Authorization": f"Bearer {coach_token}"}, json={
            "nombre": "Hacked"
        })
        assert resp.status_code == 403

    def test_coach_no_puede_eliminar_entrenamiento(self, client: TestClient, coach_token: str, db_session: Session):
        from app.models.models import Entrenamiento as EntrenamientoModel
        ent = db_session.query(EntrenamientoModel).first()
        resp = client.delete(f"/entrenamientos/{ent.id}", headers={"Authorization": f"Bearer {coach_token}"})
        assert resp.status_code == 403

    def test_no_auth_no_puede_accder_alumnos(self, client: TestClient):
        resp = client.get("/alumnos/")
        assert resp.status_code == 401

    def test_no_auth_no_puede_ver_entrenamientos(self, client: TestClient):
        resp = client.get("/entrenamientos/")
        assert resp.status_code == 401

    def test_coach_puede_ver_entrenamientos(self, client: TestClient, coach_token: str):
        resp = client.get("/entrenamientos/", headers={"Authorization": f"Bearer {coach_token}"})
        assert resp.status_code == 200


class TestAdminFullAccess:
    def test_admin_ve_alumnos_de_todos(self, client: TestClient, admin_token: str, alumno_coach_a: AlumnoModel, alumno_coach_b: AlumnoModel):
        resp = client.get("/alumnos/", headers={"Authorization": f"Bearer {admin_token}"})
        assert resp.status_code == 200
        data = resp.json()
        ids = [a["id"] for a in data]
        assert alumno_coach_a.id in ids
        assert alumno_coach_b.id in ids

    def test_admin_puede_gestionar_asistencia(self, client: TestClient, admin_token: str):
        resp = client.get("/asistencia/", headers={"Authorization": f"Bearer {admin_token}"})
        assert resp.status_code == 200
