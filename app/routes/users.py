from fastapi import APIRouter, HTTPException

from app.crypto import decrypt_field
from app.db import get_users_collection
from bson.objectid import ObjectId
from typing import List

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/teachers", response_model=List[dict])
def list_teachers():
    users = get_users_collection()
    docs = users.find({"role": "teacher"})
    out = []
    for d in docs:
        out.append({"id": str(d["_id"]), "email": d.get("email"), "full_name": decrypt_field(d.get("full_name_enc"))})
    return out

@router.get("/{user_id}", response_model=dict)
def get_user(user_id: str):
    users = get_users_collection()
    try:
        doc = users.find_one({"_id": ObjectId(user_id)})
    except Exception:
        raise HTTPException(status_code=404, detail="User not found")
    if not doc:
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": str(doc["_id"]), "email": doc.get("email"), "full_name": doc.get("full_name"), "role": doc.get("role")}