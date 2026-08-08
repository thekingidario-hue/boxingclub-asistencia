import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.models import User as UserModel, Entrenador as EntrenadorModel, ROLE_ADMIN, ROLE_COACH
from app.auth.security import hash_password
from app.config import settings

settings.ADMIN_EMAIL = "admin@boxingclub.test"
settings.ADMIN_PASSWORD = "admin-seguro"
settings.ADMIN_NAME = "Admin Test"


@pytest.fixture
def admin_user(db_session: Session):
    existing = db_session.query(UserModel).filter(UserModel.email == "admin@boxingclub.test").first()
    if existing:
        existing.activo = True
        existing.role = ROLE_ADMIN
        db_session.commit()
        db_session.refresh(existing)
        return existing
    user = UserModel(
        email="admin@boxingclub.test",
        nombre_completo="Admin Test",
        hashed_password=hash_password("admin-seguro"),
        role=ROLE_ADMIN,
        activo=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def coach_user(db_session: Session):
    existing = db_session.query(UserModel).filter(UserModel.email == "coach@boxingclub.test").first()
    if existing:
        existing.activo = True
        existing.role = ROLE_COACH
        db_session.commit()
        db_session.refresh(existing)
        return existing
    user = UserModel(
        email="coach@boxingclub.test",
        nombre_completo="Coach Test",
        hashed_password=hash_password("coach-seguro"),
        role=ROLE_COACH,
        activo=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def entrenador_for_coach(db_session: Session, coach_user: UserModel):
    ent = db_session.query(EntrenadorModel).filter(EntrenadorModel.user_id == coach_user.id).first()
    if not ent:
        ent = EntrenadorModel(nombre="Coach Entrenador", user_id=coach_user.id, activo=True)
        db_session.add(ent)
        db_session.commit()
        db_session.refresh(ent)
    return ent


@pytest.fixture
def entrenador_for_admin(db_session: Session, admin_user: UserModel):
    ent = db_session.query(EntrenadorModel).filter(EntrenadorModel.user_id == admin_user.id).first()
    if not ent:
        ent = EntrenadorModel(nombre="Admin Entrenador", user_id=admin_user.id, activo=True)
        db_session.add(ent)
        db_session.commit()
        db_session.refresh(ent)
    return ent


class TestLogin:
    def test_login_success(self, client: TestClient, admin_user: UserModel):
        resp = client.post("/auth/login", json={"email": "admin@boxingclub.test", "password": "admin-seguro"})
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == "admin@boxingclub.test"
        assert data["user"]["role"] == "ADMIN"
        assert "hashed_password" not in data["user"]

    def test_login_invalid_password(self, client: TestClient, admin_user: UserModel):
        resp = client.post("/auth/login", json={"email": "admin@boxingclub.test", "password": "incorrecta"})
        assert resp.status_code == 401
        assert resp.json()["detail"] == "Credenciales incorrectas"

    def test_login_nonexistent_email(self, client: TestClient):
        resp = client.post("/auth/login", json={"email": "noexiste@boxingclub.test", "password": "1234"})
        assert resp.status_code == 401
        assert resp.json()["detail"] == "Credenciales incorrectas"

    def test_login_inactive_user(self, client: TestClient, db_session: Session, admin_user: UserModel):
        admin_user.activo = False
        db_session.commit()
        resp = client.post("/auth/login", json={"email": "admin@boxingclub.test", "password": "admin-seguro"})
        assert resp.status_code == 403
        assert resp.json()["detail"] == "Usuario inactivo"


class TestUsersMe:
    def test_users_me_with_valid_token(self, client: TestClient, admin_user: UserModel):
        login_resp = client.post("/auth/login", json={"email": "admin@boxingclub.test", "password": "admin-seguro"})
        token = login_resp.json()["access_token"]
        resp = client.get("/auth/users/me", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["email"] == "admin@boxingclub.test"
        assert "hashed_password" not in data

    def test_users_me_without_token(self, client: TestClient):
        resp = client.get("/auth/users/me")
        assert resp.status_code == 401

    def test_users_me_invalid_token(self, client: TestClient):
        resp = client.get("/auth/users/me", headers={"Authorization": "Bearer token-invalido"})
        assert resp.status_code == 401


class TestAdminAccess:
    def test_admin_access_allowed(self, client: TestClient, admin_user: UserModel):
        login_resp = client.post("/auth/login", json={"email": "admin@boxingclub.test", "password": "admin-seguro"})
        token = login_resp.json()["access_token"]
        resp = client.get("/auth/users/me", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200

    def test_coach_denied_admin_access(self, client: TestClient, coach_user: UserModel):
        from app.auth.security import create_access_token
        token = create_access_token({"sub": str(coach_user.id), "role": coach_user.role})
        resp = client.get("/auth/users/me", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["role"] == "COACH"
