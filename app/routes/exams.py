from fastapi import APIRouter, HTTPException, Path, Query, Depends
from starlette import status

from app.db import db, get_users_collection
from app import schemas
from bson.objectid import ObjectId
from datetime import datetime
from typing import Optional, List

from app.deps import get_current_user

router = APIRouter(prefix="/exams", tags=["exams"])

EXAMS = db["exams"]
USERS = get_users_collection()
STUDENTS = db["students"]

# Teacher uploads exam scores for a student
@router.post("/teachers/{teacher_id}/students/{student_id}", response_model=schemas.ExamOut)
def upload_exam(
    teacher_id: str = Path(..., description="teacher ObjectId"),
    student_id: str = Path(..., description="student ObjectId"),
    exam: schemas.ExamCreate = None,
    current_user: dict = Depends(get_current_user),
):
    # Only teachers may upload exam results and must be the same teacher
    if current_user.get("role") != "teacher":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only teachers can upload exam results")
    if current_user.get("id") != teacher_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Teacher can only upload exams for their own students")
    # validate teacher exists
    try:
        t = USERS.find_one({"_id": ObjectId(teacher_id)})
    except Exception:
        t = None
    if not t:
        raise HTTPException(status_code=404, detail="Teacher not found")

    # validate student exists
    try:
        s = STUDENTS.find_one({"_id": ObjectId(student_id)})
    except Exception:
        s = None
    if not s:
        raise HTTPException(status_code=404, detail="Student not found")

    # validate scores (pydantic handles types) and store
    doc = {
        "student_id": student_id,
        "teacher_id": teacher_id,
        "term": exam.term or "term1",
        "date": exam.date.isoformat() if exam.date else datetime.utcnow().isoformat(),
        "scores": exam.scores.dict(),
        "created_at": datetime.utcnow().isoformat(),
    }
    res = EXAMS.insert_one(doc)
    doc["id"] = str(res.inserted_id)
    return {
        "id": doc["id"],
        "student_id": doc["student_id"],
        "teacher_id": doc["teacher_id"],
        "term": doc["term"],
        "date": doc["date"],
        "scores": doc["scores"],
    }

@router.get("/students/{student_id}", response_model=List[schemas.ExamOut])
def list_student_exams(
    student_id: str = Path(...),
    current_user: dict = Depends(get_current_user),
):
    # Verify student exists and enforce RBAC
    try:
        student = STUDENTS.find_one({"_id": ObjectId(student_id)})
    except Exception:
        student = None

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    role = current_user.get("role")
    uid = current_user.get("id")

    if role == "parent" and student.get("parent_id") != uid:
        raise HTTPException(
            status_code=403, detail="Parents can only view exams of their own child"
        )
    if role == "teacher" and student.get("teacher_id") != uid:
        raise HTTPException(
            status_code=403, detail="Teachers can only view exams of their own students"
        )
    # principal etc. can view all

    docs = EXAMS.find({"student_id": student_id})
    result = []
    for d in docs:
        result.append(
            {
                "id": str(d["_id"]),
                "student_id": d.get("student_id"),
                "teacher_id": d.get("teacher_id"),
                "term": d.get("term"),
                "scores": d.get("scores"),
                "created_at": d.get("created_at"),
            }
        )
    return result

# Compare two students for a term (if term omitted, compare latest exams)
@router.get("/compare", response_model=schemas.ComparisonOut)
def compare_students(
    student_a: str = Query(..., description="student A id"),
    student_b: str = Query(..., description="student B id"),
    term: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user),
):
    # Only teachers may perform comparisons
    if current_user.get("role") != "teacher":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only teachers can compare students")

    # helper to get exam for student+term
    def get_exam_for(student_id: str, term: Optional[str]):
        query = {"student_id": student_id}
        if term:
            query["term"] = term
            doc = EXAMS.find_one(query, sort=[("date", -1)])
            return doc
        # latest
        doc = EXAMS.find_one(query, sort=[("date", -1)])
        return doc

    a_exam = get_exam_for(student_a, term)
    b_exam = get_exam_for(student_b, term)

    if not a_exam or not b_exam:
        raise HTTPException(status_code=404, detail="Exam data missing for one or both students for specified term")

    subjects = []
    total_a = total_b = 0
    count = 0
    for sub in schemas.SUBJECTS:
        sa = int(a_exam["scores"].get(sub, 0))
        sb = int(b_exam["scores"].get(sub, 0))
        subjects.append({
            "subject": sub,
            "student_a": sa,
            "student_b": sb,
            "diff": sa - sb
        })
        total_a += sa
        total_b += sb
        count += 1

    avg_a = round(total_a / count, 2) if count else 0.0
    avg_b = round(total_b / count, 2) if count else 0.0

    return {
        "student_a": student_a,
        "student_b": student_b,
        "term": term or a_exam.get("term"),
        "subjects": subjects,
        "average_a": avg_a,
        "average_b": avg_b
    }