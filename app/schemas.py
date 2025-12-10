from datetime import datetime

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, List


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    role: Optional[str] = "teacher"

class UserOut(BaseModel):
    id: str
    email: EmailStr
    full_name: Optional[str] = None
    role: str

    class Config:
        orm_mode = True

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class StudentCreate(BaseModel):
    name: str
    roll_no: Optional[str] = None
    class_name: Optional[str] = None
    parent_email: Optional[EmailStr] = None

class StudentOut(BaseModel):
    id: str
    name: str
    roll_no: Optional[str]
    class_name: Optional[str]
    teacher_id: Optional[str]
    parent_id: Optional[str]


SUBJECTS = ["maths", "physics", "chemistry", "biology", "social", "english"]

class ExamScores(BaseModel):
    maths: int
    physics: int
    chemistry: int
    biology: int
    social: int
    english: int

class ExamCreate(BaseModel):
    term: Optional[str] = "term1"       # e.g., term1, midterm, final
    date: Optional[datetime] = None
    scores: ExamScores

class ExamOut(BaseModel):
    id: str
    student_id: str
    teacher_id: str
    term: str
    date: Optional[datetime]
    scores: Dict[str, int]

class ComparisonSubjectStat(BaseModel):
    subject: str
    student_a: int
    student_b: int
    diff: int

class ComparisonOut(BaseModel):
    student_a: str
    student_b: str
    term: Optional[str]
    subjects: List[ComparisonSubjectStat]
    average_a: float
    average_b: float

class ChangePasswordIn(BaseModel):
    current_password: str = Field(..., min_length=3)
    new_password: str = Field(..., min_length=6)