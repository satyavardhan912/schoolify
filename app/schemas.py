from pydantic import BaseModel, EmailStr
from typing import Optional

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