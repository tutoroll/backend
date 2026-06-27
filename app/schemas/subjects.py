from pydantic import BaseModel

class SubjectGroupCreate(BaseModel):
    name: str

class SubjectGroupResponse(BaseModel):
    id: int
    name: str

class SubjectCreate(BaseModel):
    name: str
    group_id: int

class SubjectResponse(BaseModel):
    id: int
    name: str

class SubjectWithGroupResponse(SubjectResponse):
    group: SubjectGroupResponse