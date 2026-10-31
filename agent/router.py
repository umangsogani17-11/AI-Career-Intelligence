import json

from backend.services.ai_json import AIResponseError, generate_json


VALID_TOOLS = {"calculator", "file_manager", "none"}


def decide_tool(user_request: str) -> str:
    """Return a JSON-encoded, validated tool decision for the CLI executor."""
    prompt = f"""
You are a tool router for an AI Career Intelligence application.

Choose one tool for the user's request:
- calculator: mathematical calculations
- file_manager: creating, reading, updating, deleting, listing, or managing project files
- none: no tool is required

User request: {user_request}

Return exactly one JSON object: {{"tool": "calculator|file_manager|none", "reason": "short reason"}}.
"""
    try:
        decision = generate_json(
            [
                {"role": "system", "content": "Return only a valid JSON object. Never include reasoning or markdown."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=200,
        )
    except AIResponseError:
        return json.dumps({"tool": "none", "reason": "The routing service is unavailable."})

    if decision.get("tool") not in VALID_TOOLS:
        return json.dumps({"tool": "none", "reason": "The routing service returned an unsupported tool."})
    if not isinstance(decision.get("reason"), str):
        decision["reason"] = "No reason was provided."
    return json.dumps({"tool": decision["tool"], "reason": decision["reason"]})


if __name__ == "__main__":
    print("AI TOOL ROUTER")
    print("----------------")
    question = input("Enter your request: ")
    print("\nNemotron decision:")
    print(decide_tool(question))
