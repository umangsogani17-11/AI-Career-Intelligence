def calculate_match(user_skills, job_skills):

    user_skills = {
        skill.lower()
        for skill in user_skills
    }

    job_skills = {
        skill.lower()
        for skill in job_skills
    }

    matched_skills = user_skills.intersection(job_skills)

    missing_skills = job_skills - user_skills

    if len(job_skills) == 0:
        match_percentage = 0
    else:
        match_percentage = (
            len(matched_skills) / len(job_skills)
        ) * 100

    return {
        "match_percentage": round(match_percentage, 2),
        "matched_skills": sorted(matched_skills),
        "missing_skills": sorted(missing_skills)
    }
