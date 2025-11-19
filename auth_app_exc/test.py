import copy
import jwt
import pytest
from fastapi.testclient import TestClient

try:
    try:
        from auth_app_exc.main import app, SECRET_KEY, ALGORITHM
        from auth_app_exc.users_db import USERS_DB
    except Exception:
        from main import app, SECRET_KEY, ALGORITHM
        from users_db import USERS_DB
except Exception:

    from main import app, SECRET_KEY, ALGORITHM
    from users_db import USERS_DB

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_db():
    orig = copy.deepcopy(USERS_DB)
    try:
        yield
    finally:
        USERS_DB.clear()
        USERS_DB.update(orig)


def login(u, p):
    return client.post("/login", json={"username": u, "password": p})


def test_login_success_admin():
    r = login("admin", "admin123")
    assert r.status_code == 200
    token = r.json()["access_token"]
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["sub"] == "admin"
    assert "ROLE_ADMIN" in payload.get("roles", [])


def test_login_failure_wrong_password():
    r = login("user1", "wrong")
    assert r.status_code == 401


def test_user_creation_without_admin_is_forbidden():
    r = login("user1", "secure_password")
    token = r.json()["access_token"]
    r2 = client.post("/users", json={"username": "x", "password": "p"}, headers={"Authorization": f"Bearer {token}"})
    assert r2.status_code == 403


def test_user_creation_with_admin_succeeds():
    r = login("admin", "admin123")
    token = r.json()["access_token"]
    name = "created_by_admin"
    if name in USERS_DB:
        del USERS_DB[name]
    r2 = client.post("/users", json={"username": name, "password": "p"}, headers={"Authorization": f"Bearer {token}"})
    assert r2.status_code == 200
    assert name in USERS_DB


def test_user_details_authorized_returns_payload():
    r = login("user1", "secure_password")
    token = r.json()["access_token"]
    r2 = client.get("/user_details", headers={"Authorization": f"Bearer {token}"})
    assert r2.status_code == 200
    data = r2.json()
    assert data["username"] == "user1"
    assert "ROLE_USER" in data["roles"]


def test_user_details_missing_token_returns_401():
    r = client.get("/user_details")
    assert r.status_code == 401
