from pydantic import BaseModel, Field
from typing import List


class CareerProfile(BaseModel):
    name: str
    education: str
    skills: List[str]
    experience: str
    interests: List[str]


class RecommendedRole(BaseModel):
    role: str
    match_percentage: int = Field(ge=0, le=100)
    reason: str


class RoadmapStep(BaseModel):
    month: int = Field(ge=1, le=6)
    focus: str


class CareerAnalysis(BaseModel):
    candidate: dict[str, str]
    recommended_roles: list[RecommendedRole] = Field(min_length=3, max_length=5)
    strengths: list[str]
    skill_gaps: list[str]
    recommended_skills: list[str]
    roadmap: list[RoadmapStep] = Field(min_length=3, max_length=6)
