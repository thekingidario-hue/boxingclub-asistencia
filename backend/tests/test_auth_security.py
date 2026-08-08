import pytest
from app.auth.security import hash_password, verify_password


def test_password_hash():
    hashed = hash_password("secreto123")
    assert hashed != "secreto123"
    assert isinstance(hashed, str)
    assert len(hashed) > 0


def test_password_verify_success():
    hashed = hash_password("secreto123")
    assert verify_password("secreto123", hashed) is True


def test_password_verify_failure():
    hashed = hash_password("secreto123")
    assert verify_password("otra-clave", hashed) is False


def test_password_hash_is_deterministic_per_call():
    h1 = hash_password("abc")
    h2 = hash_password("abc")
    assert h1 != h2
    assert verify_password("abc", h1)
    assert verify_password("abc", h2)
