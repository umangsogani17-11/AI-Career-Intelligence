from fastapi import APIRouter
from backend.services.jobs import jobs
from backend.services.job_matcher import calculate_match

router = APIRouter(
    prefix="/jobs",
    tags=["Jobs"]
)


@router.get("/")
def get_jobs():
    return {
        "message": "Jobs fetched successfully",
        "jobs": jobs
    }


@router.post("/match")
def match_jobs(user_skills: list[str]):
    results = []

    user_skills_set = set(skill.lower() for skill in user_skills)

    for job in jobs:

        job_skills_set = set(
            skill.lower()
            for skill in job["skills"]
        )

        match = calculate_match(
            user_skills_set,
            job_skills_set
        )

        results.append({
            "id": job["id"],
            "title": job["title"],
            "company": job["company"],
            "location": job["location"],
            "salary": job["salary"],
            "match_percentage": match["match_percentage"],
            "matched_skills": match["matched_skills"],
            "missing_skills": match["missing_skills"]
        })

    results.sort(
        key=lambda x: x["match_percentage"],
        reverse=True
    )

    return {
        "message": "Job matching completed successfully",
        "user_skills": user_skills,
        "matched_jobs": results
    }