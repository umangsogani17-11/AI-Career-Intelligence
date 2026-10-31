import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from backend.main import app


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_health_and_jobs(self):
        self.assertEqual(self.client.get("/health").status_code, 200)
        response = self.client.post("/jobs/match", json=["Python", "SQL"])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["matched_jobs"][0]["match_percentage"], 50.0)

    def test_career_recommendations(self):
        response = self.client.post(
            "/career/recommend-jobs",
            json={
                "name": "Test Candidate", "education": "B.Tech",
                "skills": ["Python", "SQL"], "experience": "Fresher",
                "interests": ["Software Development"],
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["recommended_jobs"]), 4)

    def test_resume_upload_rejects_non_pdf(self):
        response = self.client.post(
            "/resume/upload", files={"file": ("resume.txt", b"text", "text/plain")}
        )
        self.assertEqual(response.status_code, 415)

    def test_resume_upload_extracts_pdf(self):
        pdf_path = Path("temp_resume.pdf")
        with pdf_path.open("rb") as resume_file:
            response = self.client.post(
                "/resume/upload", files={"file": ("resume.pdf", resume_file, "application/pdf")}
            )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["text"].strip())


if __name__ == "__main__":
    unittest.main()
