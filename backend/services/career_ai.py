from pydantic import ValidationError

from backend.models.career import CareerAnalysis
from backend.services.ai_json import AIResponseError, generate_json


def _to_list(value) -> list[str]:
    """Normalise a comma-separated model response to the documented list format."""
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        return [item.strip() for item in value.split(",") if item.strip()]
    return []


def analyze_career(profile) -> dict:
    prompt = f"""
You are an AI career advisor. Analyze this candidate using only the supplied data.

Name: {profile.name}
Education: {profile.education}
Skills: {", ".join(profile.skills)}
Experience: {profile.experience}
Interests: {", ".join(profile.interests)}

Return exactly one JSON object with candidate, recommended_roles (3-5 items with
role, match_percentage, reason), strengths, skill_gaps, recommended_skills, and
roadmap (3-6 items with month and focus). Match percentages must be 0-100.
Do not include reasoning, markdown, or information not supported by the profile.
"""
    try:
        result = generate_json(
            [
                {"role": "system", "content": "Return only a valid JSON object. Never include reasoning, markdown, or code fences."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=2000,
        )
        for field in ("strengths", "skill_gaps", "recommended_skills"):
            result[field] = _to_list(result.get(field))
        return CareerAnalysis.model_validate(result).model_dump()
    except AIResponseError:
        raise
    except ValidationError as error:
        raise AIResponseError("The AI service returned an incomplete career analysis.") from error
