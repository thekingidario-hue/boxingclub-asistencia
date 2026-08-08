import pytest
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.models.models import Base
from app import database as database_module
from app.database import get_db, migrar_entrenadores, migrar_entrenamientos, migrar_alumnos, migrar_roles
from app.models.models import User as UserModel, ROLE_ADMIN, ROLE_COACH
from app.auth.security import hash_password
from app.config import settings


TEST_DB_PATH = "/tmp/test_boxingclub.db"
TEST_ADMIN_EMAIL = "admin@test.local"
TEST_ADMIN_PASSWORD = "test-admin-password-123"
TEST_ADMIN_NAME = "Admin Test"
TEST_COACH_EMAIL = "coach@test.local"
TEST_COACH_PASSWORD = "test-coach-password-456"
TEST_COACH_NAME = "Coach Test"

settings.ADMIN_EMAIL = TEST_ADMIN_EMAIL
settings.ADMIN_PASSWORD = TEST_ADMIN_PASSWORD
settings.ADMIN_NAME = TEST_ADMIN_NAME


@pytest.fixture(scope="session")
def test_engine():
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
    engine = create_engine(f"sqlite:///{TEST_DB_PATH}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    _seed_test_data(engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)


def _seed_test_data(engine):
    from sqlalchemy.orm import Session
    db = Session(engine)
    migrar_entrenadores(db)
    migrar_entrenamientos(db)
    migrar_alumnos(db)
    migrar_roles(db)
    if db.query(UserModel).count() == 0:
        admin = UserModel(
            email=TEST_ADMIN_EMAIL,
            nombre_completo=TEST_ADMIN_NAME,
            hashed_password=hash_password(TEST_ADMIN_PASSWORD),
            role=ROLE_ADMIN,
            activo=True,
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        db.execute(text(f"UPDATE entrenadores SET user_id = {admin.id} WHERE id = 1 AND user_id IS NULL"))
        db.commit()

        coach = UserModel(
            email=TEST_COACH_EMAIL,
            nombre_completo=TEST_COACH_NAME,
            hashed_password=hash_password(TEST_COACH_PASSWORD),
            role=ROLE_COACH,
            activo=True,
        )
        db.add(coach)
        db.commit()
        db.refresh(coach)
        db.execute(text(f"UPDATE entrenadores SET user_id = {coach.id} WHERE id = 2 AND user_id IS NULL"))
        db.commit()
    db.close()


@pytest.fixture
def db_session(test_engine):
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = SessionLocal()
    yield session
    session.rollback()
    session.close()


@pytest.fixture
def client(test_engine):
    from app.main import app
    from app.database import SessionLocal
    from fastapi.testclient import TestClient

    original_engine = database_module.engine
    original_session = SessionLocal
    test_session_factory = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    database_module.engine = test_engine
    database_module.SessionLocal = test_session_factory

    def override_get_db():
        db = test_session_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides = {get_db: override_get_db}
    try:
        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides.clear()
        database_module.engine = original_engine
        database_module.SessionLocal = original_session
