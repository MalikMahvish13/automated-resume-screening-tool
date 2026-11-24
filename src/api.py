"""FastAPI upload endpoint for running a resume comparison."""

from __future__ import annotations

import tempfile
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from src.screening import extract_text, screen_candidates

app = FastAPI(
    title="Automated Resume Screening Tool",
    description=(
        "Educational decision-support demo. Scores are not hiring decisions; "
        "review resumes and evidence yourself."
    ),
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

MAX_UPLOAD_BYTES = 10 * 1024 * 1024


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/screen")
async def screen(
    job_description: str = Form(...),
    required_skills: str = Form(""),
    threshold: float = Form(55.0),
    resumes: list[UploadFile] = File(...),
) -> dict[str, object]:
    if not job_description.strip():
        raise HTTPException(status_code=422, detail="Job description cannot be empty.")
    if not 0 <= threshold <= 100:
        raise HTTPException(status_code=422, detail="Threshold must be between 0 and 100.")
    if not resumes:
        raise HTTPException(status_code=422, detail="Upload at least one resume.")

    candidates = []
    try:
        with tempfile.TemporaryDirectory(prefix="resume-screen-") as temp_dir:
            for index, upload in enumerate(resumes):
                suffix = Path(upload.filename or "").suffix.lower()
                if suffix not in {".txt", ".pdf", ".docx"}:
                    raise HTTPException(
                        status_code=415,
                        detail=f"Unsupported file type for upload {index + 1}; use TXT, PDF, or DOCX.",
                    )
                content = await upload.read(MAX_UPLOAD_BYTES + 1)
                if len(content) > MAX_UPLOAD_BYTES:
                    raise HTTPException(
                        status_code=413,
                        detail=f"Upload {index + 1} exceeds the 10 MB limit.",
                    )
                file_path = Path(temp_dir) / f"resume_{index}{suffix}"
                file_path.write_bytes(content)
                text, warnings = extract_text(file_path)
                candidates.append(
                    {
                        "candidate": Path(upload.filename or f"resume_{index}").stem,
                        "resume_file": Path(upload.filename or file_path.name).name,
                        "text": text,
                        "warnings": warnings,
                    }
                )
            skills = [item.strip() for item in required_skills.split(",") if item.strip()]
            results = screen_candidates(candidates, job_description, skills, threshold)
    except HTTPException:
        raise
    except (ValueError, OSError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return {
        "notice": "Decision support only. A human must review candidates and source resumes.",
        "results": results,
    }
