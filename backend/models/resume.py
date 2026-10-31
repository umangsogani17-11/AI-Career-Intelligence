from typing import Any

from pydantic import BaseModel, Field


class ResumeAnalysis(BaseModel):
    resume_score: int = Field(ge=0, le=100)
    summary: str
    strengths: list[str]
    weaknesses: list[str]
    missing_skills: list[str]
    recommended_skills: list[str]
    recommended_roles: list[str] = Field(min_length=3, max_length=5)
    ats_suggestions: list[str]
    project_improvements: list[str]


class ImprovedProject(BaseModel):
    name: str
    description: str
    technologies: list[str]


class ResumeImprovement(BaseModel):
    professional_summary: str
    technical_skills: list[str]
    # Models commonly return education as either a readable string or structured fields.
    education: list[str | dict[str, Any]]
    projects: list[ImprovedProject]
    certifications: list[str]
    achievements: list[str]
    soft_skills: list[str]
    ats_keywords: list[str]
