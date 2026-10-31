import json

from backend.services.ai_client import MODEL, get_ai_client


class AIResponseError(Exception):
    """A safe, user-facing failure from the external AI provider."""


def _parse_json_object(answer: str) -> dict:
    """Parse a complete JSON object without exposing any surrounding model text."""
    try:
        result = json.loads(answer)
    except json.JSONDecodeError:
        start = answer.find("{")
        if start == -1:
            raise AIResponseError("The AI service returned an invalid structured response.")

        depth = 0
        in_string = False
        escaped = False
        end = None
        for index, character in enumerate(answer[start:], start=start):
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == '"':
                in_string = not in_string
            elif not in_string and character == "{":
                depth += 1
            elif not in_string and character == "}":
                depth -= 1
                if depth == 0:
                    end = index + 1
                    break

        if end is None:
            raise AIResponseError("The AI service returned an invalid structured response.")
        try:
            result = json.loads(answer[start:end])
        except json.JSONDecodeError as error:
            raise AIResponseError("The AI service returned an invalid structured response.") from error

    if not isinstance(result, dict):
        raise AIResponseError("The AI service returned an unexpected response format.")
    return result


def generate_json(messages: list[dict[str, str]], max_tokens: int) -> dict:
    """Request one JSON object and reject any non-JSON provider response."""
    try:
        response = get_ai_client().chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.0,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
            # Nemotron otherwise emits its reasoning before the final answer.
            extra_body={"chat_template_kwargs": {"enable_thinking": False}},
        )
    except Exception as error:
        raise AIResponseError("The AI service could not complete this request.") from error

    try:
        answer = response.choices[0].message.content
    except (AttributeError, IndexError, TypeError) as error:
        raise AIResponseError("The AI service returned an unexpected response format.") from error
    if not answer:
        raise AIResponseError("The AI service returned an empty response.")
    return _parse_json_object(answer)
