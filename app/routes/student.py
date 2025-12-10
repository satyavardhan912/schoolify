from fastapi import APIRouter, HTTPException, Depends
from app.db import db
from bson.objectid import ObjectId
from app.deps import get_current_user
from app.crypto import decrypt_field

router = APIRouter(prefix="/students", tags=["students"])
STUDENTS = db["students"]

@router.get("/{student_id}", response_model=dict)
def get_student(student_id: str, current_user: dict = Depends(get_current_user)):
    try:
        doc = STUDENTS.find_one({"_id": ObjectId(student_id)})
    except Exception:
        raise HTTPException(status_code=404, detail="Student not found")
    if not doc:
        raise HTTPException(status_code=404, detail="Student not found")

    role = current_user.get("role")
    uid = current_user.get("id")

    if role == "parent" and doc.get("parent_id") != uid:
        raise HTTPException(
            status_code=403, detail="Parents can only view their own child"
        )
    if role == "teacher" and doc.get("teacher_id") != uid:
        raise HTTPException(
            status_code=403, detail="Teachers can only view their own students"
        )
    name = decrypt_field(doc.get("name_enc")) if doc.get("name_enc") else doc.get("name")

    return {
      "id": str(doc["_id"]),
      "name": name,
      "roll_no": doc.get("roll_no"),
      "class_name": doc.get("class_name"),
      "teacher_id": doc.get("teacher_id"),
      "parent_id": doc.get("parent_id"),
    }

@router.get("/me/children", response_model=list[dict])
def get_my_children(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "parent":
        raise HTTPException(
            status_code=403, detail="Only parents can view their children list"
        )

    cursor = STUDENTS.find({"parent_id": current_user["id"]})
    results = []
    for doc in cursor:
        name = decrypt_field(doc.get("name_enc")) if doc.get("name_enc") else doc.get("name")
        results.append(
            {
                "id": str(doc["_id"]),
                "name": name,
                "roll_no": doc.get("roll_no"),
                "class_name": doc.get("class_name"),
                "teacher_id": doc.get("teacher_id"),
            }
        )
    return results