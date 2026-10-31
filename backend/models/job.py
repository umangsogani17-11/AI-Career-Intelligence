from pydantic import BaseModel
from typing import List


class Job(BaseModel):
    id: int
    title: str
    company: str
    location: str
    skills: List[str]
    experience: str
    salary: str

