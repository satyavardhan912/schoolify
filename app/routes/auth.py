from fastapi import APIRouter, HTTPException, status, Path
from app import schemas
from app.db import get_users_collection, db
from bson.objectid import ObjectId
import os

router = APIRouter(prefix="/auth", tags=["auth"])

USERS = get_users_collection()
STUDENTS = db["students"]

@router.post("/register", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
def register(u: schemas.UserCreate):
    if USERS.find_one({"email": u.email}):
        raise HTTPException(status_code=400, detail="Email already registered")
    doc = {
        "email": u.email,
        "password": u.password,  # VULNERABLE: plaintext for Phase1
        "full_name": u.full_name,
        "role": u.role or "teacher",
    }
    res = USERS.insert_one(doc)
    doc["id"] = str(res.inserted_id)
    return {"id": doc["id"], "email": doc["email"], "full_name": doc.get("full_name"), "role": doc["role"]}

@router.post("/login", response_model=schemas.TokenOut)
def login(creds: schemas.LoginIn):
    user = USERS.find_one({"email": creds.email})
    if not user or user.get("password") != creds.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = f"fake-token-for-{str(user['_id'])}"
    expires = int(os.getenv("ACCESS_TOKEN_EXPIRE_SECONDS", "3600"))
    return {"access_token": token, "token_type": "bearer", "expires_in": expires}

@router.post("/principal/add-teacher", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
def principal_add_teacher(u: schemas.UserCreate):
    # role forced to teacher
    u.role = "teacher"
    if USERS.find_one({"email": u.email}):
        raise HTTPException(status_code=400, detail="Email already registered")
    doc = {
        "email": u.email,
        "password": u.password,
        "full_name": u.full_name,
        "role": "teacher",
    }
    res = USERS.insert_one(doc)
    return {"id": str(res.inserted_id), "email": doc["email"], "full_name": doc["full_name"], "role": doc["role"]}

@router.post("/teachers/{teacher_id}/students", response_model=schemas.StudentOut, status_code=status.HTTP_201_CREATED)
def teacher_add_student(teacher_id: str = Path(...), s: schemas.StudentCreate = None):
    # Ensure teacher exists (no role enforcement in Phase1)
    t = USERS.find_one({"_id": ObjectId(teacher_id)})
    if not t:
        raise HTTPException(status_code=404, detail="Teacher not found")
    parent_id = None
    if s.parent_email:
        existing = USERS.find_one({"email": s.parent_email})
        if existing:
            parent_id = str(existing["_id"])
        else:
            p_doc = {
                "email": s.parent_email,
                "password": "changeme",
                "full_name": None,
                "role": "parent",
            }
            pres = USERS.insert_one(p_doc)
            parent_id = str(pres.inserted_id)

    stud_doc = {
        "name": s.name,
        "roll_no": s.roll_no,
        "class_name": s.class_name,
        "teacher_id": str(teacher_id),
        "parent_id": parent_id,
    }
    r = STUDENTS.insert_one(stud_doc)
    return {
        "id": str(r.inserted_id),
        "name": stud_doc["name"],
        "roll_no": stud_doc.get("roll_no"),
        "class_name": stud_doc.get("class_name"),
        "teacher_id": stud_doc.get("teacher_id"),
        "parent_id": stud_doc.get("parent_id"),
    }