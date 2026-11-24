"""Optional local Streamlit interface; install Streamlit separately to use it."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pandas as pd
import streamlit as st

from src.screening import extract_text, screen_candidates

st.set_page_config(page_title="Resume Screening Demo", layout="wide")
st.title("Automated Resume Screening Tool")
st.caption("Educational decision support only. Review every source resume yourself.")

job_description = st.text_area("Job description", height=180)
skills_input = st.text_input("Required skills (comma-separated)")
uploads = st.file_uploader(
    "Upload resumes (PDF, DOCX, or TXT)",
    type=["pdf", "docx", "txt"],
    accept_multiple_files=True,
)
threshold = st.slider("Review threshold", min_value=0, max_value=100, value=55)

if st.button("Compare resumes", type="primary"):
    if not job_description.strip() or not uploads:
        st.error("Enter a job description and upload at least one resume.")
    else:
        candidates = []
        with tempfile.TemporaryDirectory(prefix="resume-screen-") as temp_dir:
            for index, uploaded in enumerate(uploads):
                suffix = Path(uploaded.name).suffix.lower()
                path = Path(temp_dir) / f"resume_{index}{suffix}"
                path.write_bytes(uploaded.getvalue())
                text, warnings = extract_text(path)
                candidates.append(
                    {
                        "candidate": Path(uploaded.name).stem,
                        "resume_file": Path(uploaded.name).name,
                        "text": text,
                        "warnings": warnings,
                    }
                )
        skills = [item.strip() for item in skills_input.split(",") if item.strip()]
        try:
            results = screen_candidates(candidates, job_description, skills, threshold)
        except ValueError as exc:
            st.error(str(exc))
        else:
            frame = pd.DataFrame(results)
            st.dataframe(frame, use_container_width=True, hide_index=True)
            st.download_button(
                "Download ranking CSV",
                data=frame.to_csv(index=False),
                file_name="ranking_report.csv",
                mime="text/csv",
            )
