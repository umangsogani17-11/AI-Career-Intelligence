from fastapi import APIRouter, HTTPException, status

from backend.models.career import CareerProfile
from backend.services.ai_json import AIResponseError
from backend.services.career_ai import analyze_career
from backend.services.job_matcher import calculate_match
from backend.services.jobs import jobs


router = APIRouter(prefix="/career", tags=["Career"])


def get_recommended_jobs(profile: CareerProfile) -> list[dict]:
    user_skills = {skill.lower() for skill in profile.skills}
    matched_jobs = []
    for job in jobs:
        match = calculate_match(user_skills, job["skills"])
        matched_jobs.append(
            {
                "id": job["id"], "title": job["title"], "company": job["company"],
                "location": job["location"], "salary": job["salary"], **match,
            }
        )
    return sorted(matched_jobs, key=lambda item: item["match_percentage"], reverse=True)


@router.get("/test")
def career_test():
    return {"message": "Career API is working!", "status": "success"}


@router.post("/profile")
def create_profile(profile: CareerProfile):
    return {"message": "Career profile received successfully", "profile": profile}


@router.post("/analyze")
def analyze_profile(profile: CareerProfile):
    try:
        analysis = analyze_career(profile)
    except AIResponseError as error:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(error)) from error
    return {"message": "Career analysis generated successfully", "analysis": analysis}


@router.post("/recommend-jobs")
def recommend_jobs(profile: CareerProfile):
    return {
        "message": "Job recommendations generated successfully",
        "candidate": profile.name,
        "skills": profile.skills,
        "recommended_jobs": get_recommended_jobs(profile),
    }


@router.post("/career-recommendation")
def career_recommendation(profile: CareerProfile):
    try:
        career_analysis = analyze_career(profile)
    except AIResponseError as error:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(error)) from error
    return {
        "message": "Complete career recommendation generated successfully",
        "candidate": profile.model_dump(),
        "career_analysis": career_analysis,
        "recommended_jobs": get_recommended_jobs(profile),
    }
