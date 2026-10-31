import unittest
from types import SimpleNamespace
from unittest.mock import patch

from backend.services.ai_json import generate_json
from backend.services.career_ai import _to_list


class AiJsonTests(unittest.TestCase):
    def test_extracts_json_after_unwanted_model_text(self):
        response = SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content='Thinking...\n{"score": 90}'))]
        )
        client = SimpleNamespace(
            chat=SimpleNamespace(completions=SimpleNamespace(create=lambda **_: response))
        )
        with patch("backend.services.ai_json.get_ai_client", return_value=client):
            self.assertEqual(generate_json([{"role": "user", "content": "test"}], 10), {"score": 90})

    def test_normalises_comma_separated_career_lists(self):
        self.assertEqual(_to_list("Python, SQL, FastAPI"), ["Python", "SQL", "FastAPI"])


if __name__ == "__main__":
    unittest.main()
