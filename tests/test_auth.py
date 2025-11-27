import os
import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("MONGODB_URI", "mongodb://localhost:27017/schoolify_test")
from app.main import app
from app.db import db, get_users_collection

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def cleanup_db():
    # ensure clean test DB
    db.users.delete_many({})
    db.students.delete_many({})
    yield
    db.users.delete_many({})
    db.students.delete_many({})

def test_register_and_login_and_plaintext_storage():
    # register user
    payload = {"email": "teacher1@test", "password": "TopSecret123", "full_name": "Teacher One", "role": "teacher"}
    r = client.post("/auth/register", json=payload)
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["email"] == payload["email"]

    # login
    r = client.post("/auth/login", json={"email": payload["email"], "password": payload["password"]})
    assert r.status_code == 200, r.text
    tok = r.json().get("access_token")
    assert tok and "fake-token-for" in tok

    # check raw storage in Mongo
    doc = get_users_collection().find_one({"email": payload["email"]})
    assert doc is not None
    assert doc.get("password") == "TopSecret123"

def test_principal_add_teacher_and_teacher_add_student():
    # principal adds teacher
    principal_payload = {"email": "principal@test", "password": "adminpass", "role": "principal"}
    client.post("/auth/register", json=principal_payload)
    teacher_payload = {"email": "teacher2@test", "password": "teachpass", "full_name": "Teacher Two"}
    r = client.post("/auth/principal/add-teacher", json=teacher_payload)
    assert r.status_code == 201

    # teacher create student
    teacher_doc = get_users_collection().find_one({"email": teacher_payload["email"]})
    teacher_id = str(teacher_doc["_id"])
    student_payload = {"name": "Student A", "roll_no": "A1", "class_name": "1A", "parent_email": "parent1@test"}
    r = client.post(f"/auth/teachers/{teacher_id}/students", json=student_payload)
    assert r.status_code == 201
    s = r.json()
    assert s["name"] == "Student A"