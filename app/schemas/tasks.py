import datetime
from pydantic import BaseModel

from app.schemas.subjects import SubjectResponse
from app.schemas.users import UserResponse

class TaskCreate(BaseModel):
    question: str
    correct_answer: str

class TaskResponse(BaseModel):
    id: int
    question: str
    correct_answer: str

class HomeworkCreate(BaseModel):
    title: str
    author_id: int
    assignee_id: int

class HomeworkResponse(BaseModel):
    id: int
    title: str
    author: UserResponse
    assignee: UserResponse
    subject: SubjectResponse
    tasks: list[TaskResponse]

class AnswerCreate(BaseModel):
    task_id: int
    answer: str

class SolutionCreate(BaseModel):
    answers: list[AnswerCreate]

class AnswerResponse(BaseModel):
    id: int
    task: TaskResponse
    answer: str
    is_correct: bool

class SolutionResponse(BaseModel):
    id: int
    published_at: datetime.datetime
    answers: list[AnswerResponse]