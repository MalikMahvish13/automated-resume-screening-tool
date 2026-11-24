"""Resume parsing and explainable, job-related candidate comparison."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any
from zipfile import BadZipFile

import pandas as pd
import pdfplumber
from docx import Document
from docx.opc.exceptions import PackageNotFoundError
from pdfplumber.utils.exceptions import PdfminerException
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

SUPPORTED_EXTENSIONS = {".txt", ".pdf", ".docx"}


def extract_text(path: Path) -> tuple[str, list[str]]:
    """Extract text from a text, PDF, or DOCX resume, returning warnings."""
    suffix = path.suffix.lower()
    warnings: list[str] = []

    if suffix == ".txt":
        text = path.read_text(encoding="utf-8", errors="replace")
    elif suffix == ".pdf":
        try:
            with pdfplumber.open(path) as pdf:
                text = "\n".join(page.extract_text() or "" for page in pdf.pages)
        except PdfminerException as exc:
            raise ValueError(f"Could not read PDF {path.name}: {exc}") from exc
        if not text.strip():
            warnings.append(
                "No selectable text found; this may be a scanned PDF and needs OCR."
            )
    elif suffix == ".docx":
        try:
            document = Document(path)
        except (PackageNotFoundError, BadZipFile) as exc:
            raise ValueError(f"Could not read DOCX {path.name}: {exc}") from exc
        paragraphs = [paragraph.text for paragraph in document.paragraphs]
        table_text = [
            cell.text
            for table in document.tables
            for row in table.rows
            for cell in row.cells
        ]
        text = "\n".join(paragraphs + table_text)
    else:
        raise ValueError(f"Unsupported resume format: {path.suffix or '(none)'}")

    if not text.strip():
        warnings.append("No readable resume text was extracted.")
    return text, warnings


def clean_text(text: str) -> str:
    """Normalize whitespace and remove control characters without losing terms."""
    text = text.lower()
    text = re.sub(r"[^\w+#./-]+", " ", text, flags=re.UNICODE)
    return re.sub(r"\s+", " ", text).strip()


def _normalize_skill(skill: str) -> str:
    return re.sub(r"[^a-z0-9+#]+", " ", skill.lower()).strip()


def find_skill_matches(text: str, required_skills: list[str]) -> list[str]:
    """Match complete normalized skill phrases, not arbitrary substrings."""
    normalized_text = f" {_normalize_skill(text)} "
    matches = []
    for skill in required_skills:
        normalized_skill = _normalize_skill(skill)
        if normalized_skill and f" {normalized_skill} " in normalized_text:
            matches.append(skill)
    return matches


def extract_experience_years(text: str) -> float | None:
    """Extract the largest explicit 'N years' mention; this is not a quality score."""
    pattern = re.compile(
        r"\b(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)(?:\s+of\s+experience)?\b",
        flags=re.IGNORECASE,
    )
    values = [float(match.group(1)) for match in pattern.finditer(text)]
    return max(values) if values else None


def load_resumes(directory: Path) -> list[dict[str, Any]]:
    if not directory.is_dir():
        raise FileNotFoundError(f"Resume folder does not exist: {directory}")

    resumes: list[dict[str, Any]] = []
    for path in sorted(directory.iterdir()):
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS:
            text, warnings = extract_text(path)
            resumes.append(
                {
                    "candidate": path.stem.replace("_", " "),
                    "resume_file": path.name,
                    "text": text,
                    "warnings": warnings,
                }
            )
    if not resumes:
        raise ValueError(
            f"No .txt, .pdf, or .docx resumes found in {directory}."
        )
    return resumes


def screen_candidates(
    resumes: list[dict[str, Any]],
    job_description: str,
    required_skills: list[str],
    threshold: float = 55.0,
) -> list[dict[str, Any]]:
    """Rank resumes and return score components, evidence, and missing requirements."""
    if not resumes:
        raise ValueError("Provide at least one resume.")
    if not job_description.strip():
        raise ValueError("Job description cannot be empty.")
    if not 0 <= threshold <= 100:
        raise ValueError("Threshold must be between 0 and 100.")

    job_text = clean_text(job_description)
    resume_texts = [clean_text(str(resume.get("text", ""))) for resume in resumes]
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), stop_words="english")
    vectors = vectorizer.fit_transform([job_text, *resume_texts])
    similarities = cosine_similarity(vectors[0:1], vectors[1:]).flatten()
    results: list[dict[str, Any]] = []

    for resume, text, similarity in zip(resumes, resume_texts, similarities):
        matched = find_skill_matches(text, required_skills)
        missing = [skill for skill in required_skills if skill not in matched]
        skill_coverage = len(matched) / len(required_skills) if required_skills else 0.0
        similarity_score = float(similarity) * 100
        coverage_score = skill_coverage * 100
        overall_score = 0.60 * similarity_score + 0.40 * coverage_score
        eligible = bool(text) and overall_score >= threshold and not missing
        warnings = list(resume.get("warnings", []))

        if not text:
            recommendation = "Needs human review - resume text unreadable"
            if not warnings:
                warnings.append("No readable resume text was extracted.")
        elif missing:
            recommendation = "Needs human review - missing required skills"
        elif overall_score >= threshold:
            recommendation = "Shortlist for human review"
        else:
            recommendation = "Below review threshold - human review"

        evidence = (
            f"Matched {len(matched)} of {len(required_skills)} required skills; "
            f"TF-IDF job-description similarity is {similarity_score:.1f}%."
        )
        results.append(
            {
                "candidate": resume.get("candidate", "Unknown candidate"),
                "resume_file": resume.get("resume_file", ""),
                "overall_score": round(overall_score, 2),
                "similarity_score": round(similarity_score, 2),
                "skill_coverage_score": round(coverage_score, 2),
                "experience_years_mentioned": extract_experience_years(
                    str(resume.get("text", ""))
                ),
                "matched_skills": matched,
                "missing_skills": missing,
                "recommendation": recommendation,
                "meets_review_threshold": eligible,
                "explanation": evidence,
                "warnings": warnings,
            }
        )
    return sorted(results, key=lambda result: result["overall_score"], reverse=True)


def create_report(results: list[dict[str, Any]], output_path: Path) -> Path:
    """Write a flat, spreadsheet-friendly CSV report."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for result in results:
        row = dict(result)
        for field in ("matched_skills", "missing_skills", "warnings"):
            row[field] = "; ".join(row[field])
        rows.append(row)
    pd.DataFrame(rows).to_csv(output_path, index=False)
    return output_path


def read_text_file(path: Path) -> str:
    return path.read_text(encoding="utf-8")
