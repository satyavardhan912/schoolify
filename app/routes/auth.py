from fastapi import APIRouter, HTTPException, status, Path
from app import schemas
from app.crypto import encrypt_field
from app.db import get_users_collection, db
from bson.objectid import ObjectId
import os

from app.security import hash_password, verify_password, create_access_token
from fastapi import Depends
from app.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

USERS = get_users_collection()
STUDENTS = db["students"]

@router.post("/register", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
def register(u: schemas.UserCreate):
    if USERS.find_one({"email": u.email}):
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed = hash_password(u.password)
    full_name_enc = encrypt_field(u.full_name) if u.full_name else None
    doc = {
        "email": u.email,
        "password": hashed,
        "full_name_enc": full_name_enc,
        "full_name": u.full_name if full_name_enc is None else None,
        "role": u.role or "teacher",
    }
    res = USERS.insert_one(doc)
    doc["id"] = str(res.inserted_id)
    returned_full_name = u.full_name
    return {"id": doc["id"], "email": doc["email"], "full_name": returned_full_name, "role": doc["role"]}

@router.post("/login", response_model=schemas.TokenOut)
def login(creds: schemas.LoginIn):
    user = USERS.find_one({"email": creds.email})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    # Support both hashed and legacy plaintext passwords:
    stored_hash = user.get("password_hash") or user.get("password")
    if stored_hash is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    # If string starts with $2 (Bcrypt string), verify it
    if isinstance(stored_hash, str) and stored_hash.startswith("$2"):
        ok = verify_password(creds.password, stored_hash)
    else:
        # Migrate to hash if the plaintext password is in-use
        ok = (creds.password == stored_hash)
        if ok:
            USERS.update_one({"_id": user["_id"]},
                             {"$set": {"password_hash": hash_password(creds.password)}, "$unset": {"password": ""}})
    if not ok:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(subject=str(user["_id"]), role=user.get("role", "teacher"))
    expires = int(os.getenv("ACCESS_TOKEN_EXPIRE_SECONDS", "3600"))
    return {"access_token": token, "token_type": "bearer", "expires_in": expires}

@router.post("/principal/add-teacher", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
def principal_add_teacher(u: schemas.UserCreate, current_user: dict = Depends(get_current_user)):
    # Only principal can create teachers
    if current_user.get("role") != "principal":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only principal can create teachers")
    # role forced to teacher
    u.role = "teacher"
    if USERS.find_one({"email": u.email}):
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed = hash_password(u.password)
    full_name_enc = encrypt_field(u.full_name) if u.full_name else None
    doc = {
        "email": u.email,
        "password_hash": hashed,
        "full_name_enc": full_name_enc,
        "full_name": u.full_name if full_name_enc is None else None,
        "role": "teacher",
    }
    res = USERS.insert_one(doc)
    returned_full_name = u.full_name
    return {"id": str(res.inserted_id), "email": doc["email"], "full_name": returned_full_name, "role": doc["role"]}


@router.post("/teachers/{teacher_id}/students", response_model=schemas.StudentOut, status_code=status.HTTP_201_CREATED)
def teacher_add_student(teacher_id: str = Path(...), s: schemas.StudentCreate = None, current_user: dict = Depends(get_current_user)):
    # Only teachers may add students and the current_user id must match teacher_id
    if current_user.get("role") != "teacher":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only teachers can add students")
    if current_user.get("id") != teacher_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Teacher can only add students for their own account")

    # Ensure teacher exists (no role enforcement in Phase1 aside from above)
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
                "password_hash": hash_password("changeme"),
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


@router.delete(
    "/principal/teachers/{teacher_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def principal_delete_teacher(
    teacher_id: str,
    current_user: dict = Depends(get_current_user),
):
    # Only principal can delete teachers
    if current_user.get("role") != "principal":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only principal can delete teachers",
        )

    try:
        oid = ObjectId(teacher_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid teacher id")

    teacher = USERS.find_one({"_id": oid})
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    if teacher.get("role") != "teacher":
        raise HTTPException(status_code=400, detail="Target user is not a teacher")

    USERS.delete_one({"_id": oid})
    # we just return 204 No Content
    return

@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(
    body: schemas.ChangePasswordIn,
    current_user: dict = Depends(get_current_user),
):
    user = USERS.find_one({"_id": ObjectId(current_user["id"])})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    stored_hash = user.get("password_hash") or user.get("password")
    if stored_hash is None:
        raise HTTPException(status_code=400, detail="Password not set")

    # verify current password (supports legacy)
    if isinstance(stored_hash, str) and stored_hash.startswith("$2"):
        ok = verify_password(body.current_password, stored_hash)
    else:
        ok = (body.current_password == stored_hash)

    if not ok:
        raise HTTPException(status_code=401, detail="Current password is incorrect")

    new_hash = hash_password(body.new_password)
    USERS.update_one(
        {"_id": user["_id"]},
        {"$set": {"password_hash": new_hash}, "$unset": {"password": ""}},
    )
    return