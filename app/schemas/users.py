from datetime import datetime
from enum import Enum
from pydantic import BaseModel, ConfigDict

class Role(str, Enum):
    STUDENT='student'
    TUTOR='tutor'

class UserCreate(BaseModel):
    name: str
    surname: str
    email: str
    password: str


class LoginUser(BaseModel):
    email: str
    password: str
    role: Role

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    surname: str
    email: str
    created_at: datetime


class StudentTutorCreate(BaseModel):
    student_id: int
    tutor_id: int
