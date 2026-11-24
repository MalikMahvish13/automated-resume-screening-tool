from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import pandas as pd
from docx import Document

from src.screening import (
    create_report,
    extract_experience_years,
    extract_text,
    find_skill_matches,
    screen_candidates,
)


def make_pdf(text: str) -> bytes:
    content = f"BT /F1 12 Tf 72 720 Td ({text}) Tj ET".encode("ascii")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length "
        + str(len(content)).encode()
        + b" >>\nstream\n"
        + content
        + b"\nendstream",
    ]
    data = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for number, body in enumerate(objects, 1):
        offsets.append(len(data))
        data.extend(f"{number} 0 obj\n".encode() + body + b"\nendobj\n")
    xref_offset = len(data)
    data.extend(f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode())
    for offset in offsets[1:]:
        data.extend(f"{offset:010d} 00000 n \n".encode())
    data.extend(
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
        f"startxref\n{xref_offset}\n%%EOF".encode()
    )
    return bytes(data)


class ScreeningTests(unittest.TestCase):
    def test_phrase_matching_does_not_match_substrings(self) -> None:
        self.assertEqual(find_skill_matches("I use CPython.", ["Python"]), [])
        self.assertEqual(find_skill_matches("I use Python.", ["Python"]), ["Python"])
        self.assertEqual(find_skill_matches("I write C++.", ["C++"]), ["C++"])
        self.assertEqual(find_skill_matches("I write C code.", ["C++"]), [])

    def test_experience_is_reported_without_inventing_a_value(self) -> None:
        self.assertEqual(extract_experience_years("4 years of experience"), 4.0)
        self.assertIsNone(extract_experience_years("Experienced analyst"))

    def test_screen_flags_missing_required_skills_and_ranks(self) -> None:
        resumes = [
            {
                "candidate": "Complete",
                "resume_file": "complete.txt",
                "text": "Python SQL Pandas Excel Tableau data visualization statistics",
            },
            {
                "candidate": "Partial",
                "resume_file": "partial.txt",
                "text": "Python SQL and Excel reporting",
            },
        ]
        results = screen_candidates(
            resumes,
            "Data analyst using Python SQL Pandas Excel Tableau statistics",
            ["Python", "SQL", "Pandas", "Excel", "Tableau", "statistics"],
        )
        self.assertEqual(results[0]["candidate"], "Complete")
        self.assertEqual(results[0]["missing_skills"], [])
        self.assertIn("Pandas", results[1]["missing_skills"])
        self.assertTrue(results[0]["meets_review_threshold"])
        self.assertFalse(results[1]["meets_review_threshold"])
        self.assertAlmostEqual(
            results[0]["overall_score"],
            round(
                0.60 * results[0]["similarity_score"]
                + 0.40 * results[0]["skill_coverage_score"],
                2,
            ),
        )

    def test_txt_extraction(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "resume.txt"
            path.write_text("Python and SQL", encoding="utf-8")
            text, warnings = extract_text(path)
        self.assertEqual(text, "Python and SQL")
        self.assertEqual(warnings, [])

    def test_pdf_extraction(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "resume.pdf"
            path.write_bytes(make_pdf("Python and SQL"))
            text, warnings = extract_text(path)
        self.assertIn("Python and SQL", text)
        self.assertEqual(warnings, [])

    def test_docx_paragraph_and_table_extraction(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "resume.docx"
            document = Document()
            document.add_paragraph("Python developer")
            table = document.add_table(rows=1, cols=1)
            table.cell(0, 0).text = "SQL experience"
            document.save(path)
            text, warnings = extract_text(path)
        self.assertIn("Python developer", text)
        self.assertIn("SQL experience", text)
        self.assertEqual(warnings, [])

    def test_unreadable_resume_is_flagged_instead_of_scored_as_a_match(self) -> None:
        results = screen_candidates(
            [{"candidate": "Scanned", "resume_file": "scan.pdf", "text": ""}],
            "Python analyst",
            ["Python"],
            threshold=0,
        )
        self.assertEqual(results[0]["overall_score"], 0)
        self.assertFalse(results[0]["meets_review_threshold"])
        self.assertIn("unreadable", results[0]["recommendation"])
        self.assertTrue(results[0]["warnings"])

    def test_report_contains_ranked_scores_and_skill_gaps(self) -> None:
        results = screen_candidates(
            [
                {"candidate": "Complete", "text": "Python SQL Pandas", "resume_file": "complete.txt"},
                {"candidate": "Partial", "text": "Python", "resume_file": "partial.txt"},
            ],
            "Python SQL Pandas",
            ["Python", "SQL", "Pandas"],
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            report_path = create_report(results, Path(temp_dir) / "nested" / "report.csv")
            frame = pd.read_csv(report_path, keep_default_na=False)
        self.assertEqual(frame["candidate"].tolist(), ["Complete", "Partial"])
        self.assertEqual(frame.loc[0, "missing_skills"], "")
        self.assertIn("SQL", frame.loc[1, "missing_skills"])
        self.assertGreaterEqual(frame.loc[0, "overall_score"], frame.loc[1, "overall_score"])


if __name__ == "__main__":
    unittest.main()
