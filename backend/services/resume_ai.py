from pydantic import ValidationError

from backend.models.resume import ResumeAnalysis, ResumeImprovement
from backend.services.ai_json import AIResponseError, generate_json


def analyze_resume(resume_text: str) -> dict:
    prompt = f"""
Analyze this resume for a fresher or early-career software role.
Use only information found in the resume. Do not invent experience, projects,
certifications, achievements, or skills. Keep each item concise and practical.
Return exactly one JSON object with this shape:
{{
  "resume_score": 0, "summary": "", "strengths": [], "weaknesses": [],
  "missing_skills": [], "recommended_skills": [], "recommended_roles": [],
  "ats_suggestions": [], "project_improvements": []
}}
Rules: resume_score must be 0-100. Recommend 3-5 suitable roles.

RESUME:
{resume_text}
"""
    try:
        result = generate_json(
            [
                {"role": "system", "content": "Return only a valid JSON object. Never include reasoning, markdown, or code fences."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=2500,
        )
        return ResumeAnalysis.model_validate(result).model_dump()
    except AIResponseError:
        raise
    except ValidationError as error:
        raise AIResponseError("The AI service returned an incomplete resume analysis.") from error


def improve_resume(resume_text: str) -> dict:
    prompt = f"""
Rewrite the candidate's existing resume in a clearer, professional, ATS-friendly form.
Use only facts present in the resume. Do not add skills, projects, internships,
certifications, achievements, or experience. Improve wording and grammar only.
Return exactly one JSON object with this shape:
{{
  "professional_summary": "", "technical_skills": [], "education": [],
  "projects": [{{"name": "", "description": "", "technologies": []}}],
  "certifications": [], "achievements": [], "soft_skills": [], "ats_keywords": []
}}

RESUME:
{resume_text}
"""
    try:
        result = generate_json(
            [
                {"role": "system", "content": "Return only a valid JSON object. Never include reasoning, markdown, or code fences."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=2500,
        )
        return ResumeImprovement.model_validate(result).model_dump()
    except AIResponseError:
        raise
    except ValidationError as error:
        raise AIResponseError("The AI service returned an incomplete resume improvement.") from error
