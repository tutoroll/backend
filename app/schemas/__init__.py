from app.schemas.subjects import (
    SubjectCreate,
    SubjectGroupCreate,
    SubjectGroupResponse,
    SubjectResponse,
    SubjectWithGroupResponse,
)
from app.schemas.tasks import (
    AnswerCreate,
    AnswerResponse,
    HomeworkCreate,
    HomeworkResponse,
    SolutionCreate,
    SolutionResponse,
    TaskCreate,
    TaskResponse,
)
from app.schemas.users import (
    StudentTutorCreate,
    UserCreate,
    UserResponse,
    LoginUser,
    UserAvatar,
)

__all__ = [
    "AnswerCreate",
    "AnswerResponse",
    "HomeworkCreate",
    "HomeworkResponse",
    "SolutionCreate",
    "SolutionResponse",
    "StudentTutorCreate",
    "SubjectCreate",
    "SubjectGroupCreate",
    "SubjectGroupResponse",
    "SubjectResponse",
    "SubjectWithGroupResponse",
    "TaskCreate",
    "TaskResponse",
    "UserCreate",
    "UserResponse",
    "LoginUser",
    "UserAvatar",
]
