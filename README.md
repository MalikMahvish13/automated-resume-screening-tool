# Automated Resume Screening Tool

A student portfolio project that compares synthetic TXT, PDF, or DOCX resumes
with a job description, extracts evidence of explicitly listed skills, ranks
the resumes, and explains the result in a CSV, FastAPI response, or Next.js
dashboard.

> **Human review is mandatory.** This project is an educational decision
> support demo, not an ATS, hiring recommendation, or validated employment
> assessment. A keyword or similarity score can be wrong. It must not be used
> to automatically reject applicants or evaluate protected characteristics.
> All bundled resumes are synthetic.

## What it does

### Problem statement

Reviewers may need to organize a set of resumes and compare their stated
experience with the needs of a role. This demo shows how text extraction,
explicit skill matching, and basic NLP can surface relevant evidence for a
human reviewer. It does not automate hiring decisions and is not a production
ATS.

### Objectives

- Extract readable resume text from TXT, PDF, and DOCX sample files.
- Compare job-relevant text and explicitly provided required skill phrases.
- Present score components, matches, gaps, and parse warnings for human review.
- Demonstrate a Python CLI, FastAPI service, Next.js dashboard, and CSV export
  using fictional sample resumes only.

1. Extracts selectable text from TXT, PDF, and DOCX resumes.
2. Cleans text and computes TF-IDF/cosine similarity against the job description.
3. Checks required skill phrases and reports matched and missing requirements.
4. Ranks resumes using **60% job-description similarity + 40% required-skill
   coverage** (a transparent demo formula, not an industry standard).
5. Reports explicit years-of-experience mentions as context; experience is not
   inferred from dates and does not change the score.
6. Marks candidates for **human review** and writes a CSV with score components,
   evidence, gaps, and extraction warnings.
7. Offers the same comparison through a FastAPI API and Next.js dashboard, with
   a downloadable CSV of the displayed dashboard results.

The recommendation label means only “meets this demo threshold and has every
listed skill phrase.” It is not a shortlist/reject decision about a person.

## Architecture

```text
TXT / PDF / DOCX ──┐
Job description ───┼──> FastAPI / Python pipeline
Required skills ───┘       │
                           ├─> extraction, normalization, skill phrase matching
                           ├─> TF-IDF + cosine similarity + transparent score
                           └─> ranked evidence and missing-skill flags
                                  ├─> JSON API ──> Next.js recruiter dashboard
                                  └─> Python CLI ──> CSV report
```

Uploaded files are processed in temporary storage and are not saved to a
database. The API supports `/health` and `POST /screen`; the OpenAPI/Swagger
interface is served at `/docs`.

## Workflow and data flow

```text
Resume upload + job description + explicit skill list
  → validate extension and file size
  → extract TXT/PDF/DOCX text and warn about unreadable scans
  → normalize text and match required skill phrases
  → vectorize job and resumes with TF-IDF; calculate cosine similarity
  → combine 60% similarity + 40% skill coverage and rank
  → return matches, gaps, explanation, warnings, and human-review labels
  → display results and export CSV, or create outputs/ranking_report.csv via CLI
```

The explicit experience-years mention is informational only and does not
affect the score. Scores are not probabilities, validated hiring predictions,
or automatic rejection decisions.

## Tech stack and learning outcomes

Python 3.10+, Pandas, scikit-learn TF-IDF and cosine similarity, pdfplumber,
python-docx, FastAPI, Uvicorn, Next.js, React, TypeScript, and CSV.

Learn text extraction, data cleaning, keyword matching, vectorization, ranking,
API design, file uploads, frontend integration, testing, Git, and responsible
AI limitations.

## Repository layout

```text
Automated-Resume-Screening-Tool/
├── data/                 # Demo job description and required skill list
├── docs/                 # Full step-by-step project and interview guide
├── images/               # Add your own project screenshots here
├── outputs/              # Generated CSV reports (ignored by Git)
├── resumes/              # Synthetic sample resumes (TXT/PDF/DOCX accepted)
├── src/                  # Parsing, scoring, API, optional Streamlit UI
├── tests/                # Focused unit tests
├── web/                  # Next.js recruiter dashboard
├── main.py               # CLI entry point
├── requirements.txt
└── README.md
```

## Setup and CLI

Use Python 3.10 or newer. On macOS, from the project root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python main.py
```

On Windows PowerShell, from the project root:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -r requirements-dev.txt
```

For the complete test suite, install its test client dependency as well:

```bash
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
```

The demo reads `resumes/`, `data/job_description.txt`, and
`data/required_skills.txt`, then creates `outputs/ranking_report.csv`.
Customize inputs:

```bash
python main.py --resumes resumes --job-description data/job_description.txt \
  --required-skills data/required_skills.txt --output outputs/ranking_report.csv \
  --threshold 55
```

Use `.txt`, `.pdf`, or `.docx`; scanned/image PDFs need OCR, which is not
included. The required skills file accepts one phrase per line; lines beginning
with `#` are comments.

## API and dashboard

Start the API from the project root:

```bash
uvicorn src.api:app --reload
```

API docs: <http://127.0.0.1:8000/docs>. Health check:
<http://127.0.0.1:8000/health>. `POST /screen` accepts multipart fields
`job_description`, comma-separated `required_skills`, `threshold`, and multiple
`resumes` files (10 MB max each).

Example request (from the project root):

```bash
curl -F 'job_description=Python SQL Pandas analyst' \
  -F 'required_skills=Python,SQL,Pandas' -F 'threshold=55' \
  -F 'resumes=@resumes/alex_analyst.txt' \
  -F 'resumes=@resumes/jordan_developer.txt' \
  http://127.0.0.1:8000/screen
```

In another terminal:

```bash
cd web
npm install
npm run dev
```

Open <http://127.0.0.1:3000>. After screening, use **Download ranking CSV** to
export the displayed results. The CLI separately writes
`outputs/ranking_report.csv`. The UI talks to `http://localhost:8000`; set
`NEXT_PUBLIC_API_URL` at build time if the API runs elsewhere. Node.js 20.9+
or newer is required by the configured Next.js version.

Check the production build and dependency audit:

```bash
cd web
npm run lint
npm run build
npm audit
```

Optional Streamlit alternative (install separately):

```bash
python -m pip install "streamlit>=1.40,<2.0"
streamlit run src/streamlit_app.py
```

## Sample result and output

The sample data has a Data Analyst role. `alex analyst` contains all seven
listed must-have skill phrases and should be ranked above the other two sample
resumes. `jordan developer` and `sam generalist` are expected to show skill
gaps; they are **not automatically rejected**.

Observed CLI output with the bundled sample files:

```text
Analyzed 3 resume(s).
Report: outputs/ranking_report.csv

alex analyst: 61.8/100 | Shortlist for human review | Missing required skills: None
jordan developer: 8.2/100 | Needs human review - missing required skills | Missing required skills: SQL, Pandas, Excel, Tableau, data visualization, statistics
sam generalist: 2.5/100 | Needs human review - missing required skills | Missing required skills: Python, SQL, Pandas, Excel, Tableau, data visualization, statistics
```

CSV fields include `candidate`, `resume_file`, `overall_score`,
`similarity_score`, `skill_coverage_score`, `experience_years_mentioned`,
`matched_skills`, `missing_skills`, `recommendation`, `explanation`, and
`warnings`. Scores are specific to this toy corpus and are not calibrated.

## Tests

```bash
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
```

## Screenshots and portfolio evidence

Genuine screenshots captured from the running app and project files are saved in
[`images/`](images/):

| Evidence | Screenshot |
|---|---|
| Project folder structure | [`project-structure.png`](images/project-structure.png) |
| Synthetic sample resumes | [`sample-resumes.png`](images/sample-resumes.png) |
| Python CLI and actual scores | [`cli-ranking.png`](images/cli-ranking.png) |
| Ranked candidates and skill gaps | [`candidate-ranking.png`](images/candidate-ranking.png) |
| Matched and missing skill evidence | [`matched-missing-skills.png`](images/matched-missing-skills.png) |
| Generated sample CSV | [`csv-report.png`](images/csv-report.png) |
| FastAPI Swagger documentation | [`api-swagger.png`](images/api-swagger.png) |
| Next.js recruiter dashboard | [`dashboard.png`](images/dashboard.png) |
| Uploaded resumes and displayed results | [`dashboard-results.png`](images/dashboard-results.png) |
| Git-ready project tree | [`github-ready-structure.png`](images/github-ready-structure.png) |

Screenshots contain synthetic project data only. The generated `outputs/`
directory is ignored; the committed CSV image is illustrative evidence from
the actual generated report, not a new applicant record.

## Limitations

- TF-IDF and phrase matching are lexical, not semantic; synonyms, context,
  parsing errors, and scanned PDFs can be missed.
- The score weights and review threshold are illustrative and are not trained,
  calibrated, or validated against hiring outcomes.
- Experience is only reported when an explicit years phrase is detected; it
  does not measure ability or employment duration.
- A missing skill or low score must not be used to auto-reject anyone. A
  qualified human must review source documents and job-related evidence.
- This demo does not perform OCR, authentication, deployment hardening,
  applicant data retention controls, or fairness/impact validation.

## Future improvements

Add OCR with clear extraction warnings, reviewed skill aliases, broader parser
fixtures, role-specific evaluation, accessible UI improvements, and secure
authentication/retention controls before any real-world deployment. Any
evaluation should use lawfully obtained, representative data and appropriate
privacy, legal, and fairness review. Do not rank using protected traits or
proxies.

## Interview questions

1. **Explain your project.** Describe text extraction, TF-IDF and skill scoring,
   ranked results, the API/dashboard, and the required human review.
2. How do TF-IDF and cosine similarity compare a resume with a job description?
3. How does the project identify and report missing required skill phrases?
4. What limitations or fairness risks would you address before real-world use?

See [`docs/PROJECT_GUIDE.md`](docs/PROJECT_GUIDE.md) for strong sample answers
and additional questions.

## GitHub

Suggested repository: `automated-resume-screening-tool`

Description: `Educational Python/NLP demo for explainable resume-to-job matching with FastAPI and Next.js.`

Suggested topics: `python`, `nlp`, `resume-screening`, `fastapi`, `scikit-learn`,
`tfidf`, `nextjs`, `hr-tech`, `portfolio-project`, `responsible-ai`.

The local project is committed. To publish it, create an empty GitHub repository
named `automated-resume-screening-tool`, then connect and push to **your own**
repository URL:

```bash
git remote add origin https://github.com/YOUR-USERNAME/automated-resume-screening-tool.git
git push -u origin main
```

Never commit real resumes, secrets, or applicant information. See
[`docs/PROJECT_GUIDE.md`](docs/PROJECT_GUIDE.md) for the full explanation,
architecture, phase plan, simulation, GitHub proof schedule, screenshot
checklist, and interview questions.
