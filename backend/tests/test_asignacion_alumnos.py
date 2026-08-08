import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.models import User as UserModel, Entrenador as EntrenadorModel, Alumno as AlumnoModel, ROLE_ADMIN
from app.auth.security import hash_password
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
            role="COACH",
            activo=True,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        ent = EntrenadorModel(nombre="Coach Entrenador", user_id=user.id, activo=True)
        db_session.add(ent)
        db_session.commit()
    return login(client, TEST_COACH_EMAIL, TEST_COACH_PASSWORD)


@pytest.fixture
def alumno_sin_entrenador(db_session: Session):
    alumno = db_session.query(AlumnoModel).filter(AlumnoModel.nombre_completo == "Alumno Sin Entrenador").first()
    if not alumno:
        alumno = AlumnoModel(nombre_completo="Alumno Sin Entrenador", telefono="444", activo=True, entrenador_id=None)
        db_session.add(alumno)
        db_session.commit()
        db_session.refresh(alumno)
    return alumno


@pytest.fixture
def alumno_con_entrenador(db_session: Session):
    alumno = db_session.query(AlumnoModel).filter(AlumnoModel.nombre_completo == "Alumno Con Entrenador").first()
    if not alumno:
        alumno = AlumnoModel(nombre_completo="Alumno Con Entrenador", telefono="555", activo=True, entrenador_id=1)
        db_session.add(alumno)
        db_session.commit()
        db_session.refresh(alumno)
    return alumno


class TestAsignacionAlumnos:
    def test_sin_entrenador_admin(self, client: TestClient, admin_token: str, alumno_sin_entrenador: AlumnoModel):
        headers = {"Authorization": f"Bearer {admin_token}"}
        res = client.get("/alumnos/sin-entrenador", headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert isinstance(data, list)
        assert any(a["id"] == alumno_sin_entrenador.id for a in data)

    def test_sin_entrenador_coach_denegado(self, client: TestClient, coach_token: str):
        headers = {"Authorization": f"Bearer {coach_token}"}
        res = client.get("/alumnos/sin-entrenador", headers=headers)
        assert res.status_code == 403

    def test_asignar_individual(self, client: TestClient, admin_token: str, alumno_sin_entrenador: AlumnoModel):
        headers = {"Authorization": f"Bearer {admin_token}"}
        res = client.patch("/alumnos/1/entrenador", json={"entrenador_id": 1}, headers=headers)
        assert res.status_code == 200
        assert res.json()["entrenador_id"] == 1

    def test_asignar_null_individual(self, client: TestClient, admin_token: str, alumno_con_entrenador: AlumnoModel):
        headers = {"Authorization": f"Bearer {admin_token}"}
        res = client.patch(f"/alumnos/{alumno_con_entrenador.id}/entrenador",
                          json={"entrenador_id": None}, headers=headers)
        assert res.status_code == 200
        assert res.json()["entrenador_id"] is None

    def test_asignar_entrenador_inexistente(self, client: TestClient, admin_token: str):
        headers = {"Authorization": f"Bearer {admin_token}"}
        res = client.patch("/alumnos/1/entrenador", json={"entrenador_id": 9999}, headers=headers)
        assert res.status_code == 400
        assert "Entrenador no existe" in res.json()["detail"]

    def test_asignar_alumno_inexistente(self, client: TestClient, admin_token: str):
        headers = {"Authorization": f"Bearer {admin_token}"}
        res = client.patch("/alumnos/99999/entrenador", json={"entrenador_id": 1}, headers=headers)
        assert res.status_code == 404

    def test_asignar_masivo(self, client: TestClient, admin_token: str):
        headers = {"Authorization": f"Bearer {admin_token}"}
        res = client.patch("/alumnos/asignar-entrenador",
                          json={"alumno_ids": [1, 2], "entrenador_id": 1},
                          headers=headers)
        assert res.status_code == 200
        assert res.json()["actualizado"] == 2

    def test_asignar_masivo_alumno_inexistente(self, client: TestClient, admin_token: str):
        headers = {"Authorization": f"Bearer {admin_token}"}
        res = client.patch("/alumnos/asignar-entrenador",
                          json={"alumno_ids": [1, 99999], "entrenador_id": 1},
                          headers=headers)
        assert res.status_code == 404

    def test_asignar_masivo_entrenador_inexistente(self, client: TestClient, admin_token: str):
        headers = {"Authorization": f"Bearer {admin_token}"}
        res = client.patch("/alumnos/asignar-entrenador",
                          json={"alumno_ids": [1], "entrenador_id": 9999},
                          headers=headers)
        assert res.status_code == 400

    def test_asignar_masivo_lista_vacia(self, client: TestClient, admin_token: str):
        headers = {"Authorization": f"Bearer {admin_token}"}
        res = client.patch("/alumnos/asignar-entrenador",
                          json={"alumno_ids": [], "entrenador_id": 1},
                          headers=headers)
        assert res.status_code == 400
        assert "No hay alumnos" in res.json()["detail"]

    def test_coach_no_puede_asignar(self, client: TestClient, coach_token: str):
        headers = {"Authorization": f"Bearer {coach_token}"}
        res = client.patch("/alumnos/1/entrenador",
                          json={"entrenador_id": 1},
                          headers=headers)
        assert res.status_code == 403
