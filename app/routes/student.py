from fastapi import APIRouter, HTTPException, Depends
from app.db import db
from bson.objectid import ObjectId

from app.deps import get_current_user

router = APIRouter(prefix="/students", tags=["students"])

@router.get("/{student_id}", response_model=dict)
def get_student(student_id: str, current_user: dict = Depends(get_current_user)):
    try:
        doc = db["students"].find_one({"_id": ObjectId(student_id)})
    except Exception:
        raise HTTPException(status_code=404, detail="Student not found")
    if not doc:
        raise HTTPException(status_code=404, detail="Student not found")
    return {
        "id": str(doc["_id"]),
        "name": doc.get("name"),
        "roll_no": doc.get("roll_no"),
        "class_name": doc.get("class_name"),
        "teacher_id": doc.get("teacher_id"),
        "parent_id": doc.get("parent_id"),
    }