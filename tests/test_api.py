from __future__ import annotations

import unittest

from fastapi.testclient import TestClient

from src.api import app


class ApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.client = TestClient(app)

    def test_health_and_swagger_documentation(self) -> None:
        self.assertEqual(self.client.get("/health").json(), {"status": "ok"})
        self.assertEqual(self.client.get("/docs").status_code, 200)
        spec = self.client.get("/openapi.json")
        self.assertEqual(spec.status_code, 200)
        self.assertIn("/screen", spec.json()["paths"])
        preflight = self.client.options(
            "/screen",
            headers={
                "Origin": "http://127.0.0.1:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "content-type",
            },
        )
        self.assertEqual(
            preflight.headers["access-control-allow-origin"],
            "http://127.0.0.1:3000",
        )

    def test_multiple_uploads_with_duplicate_names_return_separate_results(self) -> None:
        response = self.client.post(
            "/screen",
            data={
                "job_description": "Python SQL Pandas analyst",
                "required_skills": "Python, SQL, Pandas",
                "threshold": "55",
            },
            files=[
                ("resumes", ("same.txt", b"Python SQL Pandas", "text/plain")),
                ("resumes", ("same.txt", b"Python only", "text/plain")),
            ],
        )
        self.assertEqual(response.status_code, 200, response.text)
        payload = response.json()
        self.assertIn("human must review", payload["notice"])
        self.assertEqual(len(payload["results"]), 2)
        self.assertEqual(
            {result["resume_file"] for result in payload["results"]}, {"same.txt"}
        )
        partial = next(
            result for result in payload["results"] if result["missing_skills"]
        )
        self.assertIn("SQL", partial["missing_skills"])

    def test_rejects_unsupported_and_malformed_files_and_empty_job(self) -> None:
        unsupported = self.client.post(
            "/screen",
            data={"job_description": "Python"},
            files=[("resumes", ("resume.exe", b"no", "application/octet-stream"))],
        )
        self.assertEqual(unsupported.status_code, 415)

        malformed = self.client.post(
            "/screen",
            data={"job_description": "Python"},
            files=[("resumes", ("resume.pdf", b"not a PDF", "application/pdf"))],
        )
        self.assertEqual(malformed.status_code, 422)

        malformed_docx = self.client.post(
            "/screen",
            data={"job_description": "Python"},
            files=[("resumes", ("resume.docx", b"not a DOCX", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"))],
        )
        self.assertEqual(malformed_docx.status_code, 422)

        empty_job = self.client.post(
            "/screen",
            data={"job_description": "  "},
            files=[("resumes", ("resume.txt", b"Python", "text/plain"))],
        )
        self.assertEqual(empty_job.status_code, 422)

    def test_empty_resume_returns_warning_for_human_review(self) -> None:
        response = self.client.post(
            "/screen",
            data={
                "job_description": "Python analyst",
                "required_skills": "Python",
            },
            files=[("resumes", ("empty.txt", b"  \n", "text/plain"))],
        )
        self.assertEqual(response.status_code, 200, response.text)
        result = response.json()["results"][0]
        self.assertIn("unreadable", result["recommendation"])
        self.assertTrue(result["warnings"])
        self.assertFalse(result["meets_review_threshold"])

    def test_rejects_uploads_over_ten_megabytes(self) -> None:
        response = self.client.post(
            "/screen",
            data={"job_description": "Python"},
            files=[
                (
                    "resumes",
                    ("large.txt", b"x" * (10 * 1024 * 1024 + 1), "text/plain"),
                )
            ],
        )
        self.assertEqual(response.status_code, 413)


if __name__ == "__main__":
    unittest.main()
