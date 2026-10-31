import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from calculator import divide
from agent.executor import execute_request
from agent.file_manager import create_project_file, list_project_files, read_project_file
from agent.router import decide_tool
from agent.tools import calculate_from_expression, calculator
from backend.services.ai_json import AIResponseError
from backend.main import app
from backend.services.job_matcher import calculate_match


class FeatureTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.profile = {
            "name": "Demo Candidate",
            "education": "B.Tech Computer Science",
            "skills": ["Python", "SQL", "FastAPI"],
            "experience": "Fresher",
            "interests": ["Backend Development"],
        }

    def test_home_health_and_frontend_are_served(self):
        self.assertEqual(self.client.get("/").status_code, 200)
        self.assertEqual(self.client.get("/health").json(), {"status": "healthy"})
        page = self.client.get("/app/")
        self.assertEqual(page.status_code, 200)
        self.assertIn("CareerOrbit", page.text)

    def test_all_non_ai_career_routes(self):
        self.assertEqual(self.client.get("/career/test").status_code, 200)
        self.assertEqual(self.client.post("/career/profile", json=self.profile).status_code, 200)
        response = self.client.post("/career/recommend-jobs", json=self.profile)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["recommended_jobs"]), 4)

    def test_career_ai_routes_with_valid_service_result(self):
        analysis = {
            "candidate": {"name": "Demo Candidate", "education": "B.Tech Computer Science"},
            "recommended_roles": [{"role": "Backend Developer", "match_percentage": 80, "reason": "Relevant skills"}] * 3,
            "strengths": ["Python"], "skill_gaps": ["Docker"], "recommended_skills": ["Git"],
            "roadmap": [{"month": 1, "focus": "Build a project"}] * 3,
        }
        with patch("backend.routes.career.analyze_career", return_value=analysis):
            self.assertEqual(self.client.post("/career/analyze", json=self.profile).status_code, 200)
            self.assertEqual(self.client.post("/career/career-recommendation", json=self.profile).status_code, 200)

    def test_resume_ai_routes_with_valid_service_result(self):
        pdf_path = Path("temp_resume.pdf")
        analysis = {
            "resume_score": 75, "summary": "Strong foundation", "strengths": ["Python"],
            "weaknesses": ["Experience"], "missing_skills": ["Git"], "recommended_skills": ["Git"],
            "recommended_roles": ["Backend Developer", "Software Developer", "Data Analyst"],
            "ats_suggestions": ["Add metrics"], "project_improvements": ["Describe impact"],
        }
        improvement = {
            "professional_summary": "Summary", "technical_skills": ["Python"], "education": [{"degree": "B.Tech"}],
            "projects": [], "certifications": [], "achievements": [], "soft_skills": [], "ats_keywords": ["Python"],
        }
        with pdf_path.open("rb") as resume_file, patch("backend.routes.resume.analyze_resume", return_value=analysis):
            response = self.client.post("/resume/analyze", files={"file": ("resume.pdf", resume_file, "application/pdf")})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["analysis"]["resume_score"], 75)
        with pdf_path.open("rb") as resume_file, patch("backend.routes.resume.improve_resume", return_value=improvement):
            response = self.client.post("/resume/improve", files={"file": ("resume.pdf", resume_file, "application/pdf")})
            self.assertEqual(response.status_code, 200)
            response_data = response.json()
            self.assertEqual(response_data["improved_resume"]["education"][0]["degree"], "B.Tech")
            download_url = response_data["download_url"]
            try:
                pdf_response = self.client.get(download_url)
                self.assertEqual(pdf_response.status_code, 200)
                self.assertEqual(pdf_response.headers["content-type"], "application/pdf")
                self.assertTrue(pdf_response.content.startswith(b"%PDF"))
            finally:
                Path(download_url.removeprefix("/")).unlink(missing_ok=True)

    def test_matcher_and_agent_utilities(self):
        self.assertEqual(calculate_match({"Python"}, {"Python", "SQL"})["match_percentage"], 50.0)
        self.assertEqual(calculator("multiply", 4, 3), 12)
        self.assertEqual(calculate_from_expression("12 / 3"), 4.0)
        self.assertIn("Invalid expression", calculate_from_expression("12 /"))
        self.assertEqual(divide(8, 2), 4)
        self.assertEqual(divide(1, 0), "Error: Division by zero")

    def test_executor_routes_calculator_without_live_ai(self):
        with patch("agent.executor.decide_tool", return_value='{"tool": "calculator", "reason": "math"}'):
            self.assertEqual(execute_request("10 + 5"), "Calculator Result: 15.0")

    def test_file_manager_blocks_path_traversal(self):
        with self.assertRaises(ValueError):
            read_project_file("../outside.txt")

    def test_file_manager_lists_and_creates_a_safe_file(self):
        probe = "tests/_agent_write_probe.txt"
        probe_path = Path(probe)
        if probe_path.exists():
            probe_path.unlink()
        try:
            self.assertIn("backend/main.py", list_project_files())
            self.assertIn("Created", create_project_file(probe, "probe"))
            self.assertEqual(read_project_file(probe), "probe")
        finally:
            if probe_path.exists():
                probe_path.unlink()

    def test_agent_router_returns_safe_json_on_service_failure(self):
        with patch("agent.router.generate_json", side_effect=AIResponseError("offline")):
            self.assertIn('"tool": "none"', decide_tool("2 + 2"))


if __name__ == "__main__":
    unittest.main()
