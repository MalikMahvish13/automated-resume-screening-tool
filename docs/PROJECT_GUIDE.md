# Project Guide: Automated Resume Screening Tool

## Project introduction and objectives

This educational portfolio project demonstrates how Python can extract text
from synthetic resume documents and compare job-related evidence against a
sample job description. It supports a local CLI/CSV workflow, a FastAPI upload
endpoint, and a Next.js recruiter dashboard. It is not a production applicant
tracking system or an automated hiring decision maker.

Objectives:

- Parse TXT, selectable-text PDF, and DOCX resumes.
- Compare job descriptions with explicitly supplied required-skill phrases.
- Show TF-IDF similarity, required-skill coverage, ranked results, and missing
  skills with evidence.
- Generate a CSV report and serve the comparison through the API and dashboard.
- Use synthetic examples only and require human review at every stage.

## Problem statement and project features

Reviewers may need to organize multiple resumes against role requirements.
This project illustrates text extraction and lexical matching as decision
support; commercial applicant tracking systems vary and should not be assumed
to use this demo's scoring approach.

Features include document extraction and readable-text warnings; phrase-level
skill matching; TF-IDF unigram/bigram vectors and cosine similarity; a
transparent 60% similarity/40% skill-coverage demonstration score; sorted
results with matched/missing phrases; explicit experience-years mention as
unscored context; CSV generation; multiple-file FastAPI upload; and a Next.js
dashboard with CSV download.

Scores and thresholds are examples, not calibrated measures of qualification.
Missing information is not proof of ineligibility; humans must inspect source
documents and the job-related evidence.

## 1. Explanation

### Simple explanation

This program reads example resumes and a job description, looks for relevant
words and required skill phrases, and produces an explained ranking. It helps
demonstrate how computers can organize application information. A recruiter
still needs to check the original resume and make every decision.

### Technical explanation

The Python pipeline extracts text from TXT, PDF, and DOCX files; normalizes
whitespace/case; and creates TF-IDF unigram/bigram vectors with scikit-learn.
Cosine similarity measures overlap between each resume and the job description.
A deterministic phrase matcher separately compares explicitly supplied skill
requirements. The demo score is:

```text
overall score = 0.60 × TF-IDF similarity percentage
              + 0.40 × required-skill coverage percentage
```

Required skill coverage is matched skills divided by listed skills. An explicit
experience-years mention is reported but is not scored. The CSV and API expose
the score components, matched/missing phrases, warnings, and explanation so a
reviewer can inspect why scores differ.

### Why organizations use screening software

When application volumes are high, software can help organize files, search
for role-related information, and support consistent review. In real
organizations, applicant tracking systems vary widely and may include workflow,
recruiting, compliance, and reporting features beyond this demo. It would be
misleading to claim that all ATS products use the same keyword weights or
automatic rejection rules. This project illustrates one simple matching
approach; it is not a production ATS.

### Workflow

```text
Resume upload + job description + explicit skill list
    → file type validation and text extraction
    → normalization and empty/scanned-file warnings
    → skill phrase matching + TF-IDF vectors
    → cosine similarity + transparent weighted score
    → sorted results + missing-skill flags
    → advisory human-review label + CSV/API/dashboard explanation
```

## 2. Tech stack options

| Option | Tools | Difficulty | Expected output |
|---|---|---:|---|
| A — Easy | Python, TXT, regex, CSV | Beginner | Matched terms and a basic report |
| B — Intermediate (this project) | Python, Pandas, NumPy ecosystem, pdfplumber, python-docx, regex, scikit-learn TF-IDF/cosine similarity, FastAPI, Next.js | Intermediate | PDF/DOCX/TXT parsing, ranked explainable CSV, upload API and dashboard |
| C — Advanced | Option B plus OCR, spaCy/transformers, database, authentication, deployment, monitoring, fairness evaluation | Advanced | More robust document and workflow handling; requires careful validation and governance |

**Recommended for students:** Option B. It is demonstrable using invented data,
introduces practical NLP and API/frontend integration, and avoids pretending
that an unvalidated model can make employment decisions. Streamlit is an
optional Python-only dashboard alternative (see README).

## 3. Architecture and data flow

```text
                ┌─────────────────────────────┐
                │ TXT / PDF / DOCX resumes    │
                └──────────────┬──────────────┘
                               │
┌───────────────────┐          ▼       ┌────────────────────┐
│ Job description   ├──────► FastAPI / Python pipeline ◄───┤ Required skill list │
└───────────────────┘          │       └────────────────────┘
                               ▼
             text extraction → cleaning → phrase matching
                               │
                TF-IDF + cosine similarity + score
                               │
                   ranking + evidence + gap flags
                   ┌───────────┴────────────┐
                   ▼                        ▼
            CSV report (CLI)       JSON API → Next.js UI
```

The local CLI reads files from folders. The API validates upload types and
individual file sizes, processes temporary files, and returns JSON. It does not
save uploaded resumes to a database. The Next.js page posts the form to the
API and exports the displayed rows when its CSV button is used. The browser
allows only localhost development origins by default; review
deployment/security configuration before exposing a service publicly.

## 4. Phase-wise implementation plan

| Phase | What to do / why | Expected output | Common beginner mistake |
|---|---|---|---|
| 1. Setup | Install Python 3.10+, create and activate a virtual environment so packages are isolated. | `.venv` and working Python/pip | Installing packages into a different interpreter |
| 2. Project folders | Create `resumes`, `data`, `src`, `outputs`, `images`, `docs`, `tests`, and `web`. Separation makes the project understandable. | Clean project tree | Putting every concern in one script |
| 3. Sample resumes | Create synthetic, role-varied resumes as TXT; optionally create PDF/DOCX versions. Do not use real applicant data. | Three fictional resumes | Publishing personal data or making every resume identical |
| 4. Job description | Write a role-specific sample JD and explicitly list must-have phrases. | `job_description.txt`, `required_skills.txt` | Treating every word in a JD as a hard requirement |
| 5. Text extraction | Use pdfplumber and python-docx; retain TXT for easy checks. | Extracted text or clear warnings | Assuming scanned PDFs contain selectable text |
| 6. Text cleaning | Normalize case and whitespace while preserving useful tokens. | Consistent text for matching | Removing punctuation that matters in skills such as C++ |
| 7. Skill matching | Match whole normalized phrases from the supplied list. | Matched and missing skill lists | Naive substring matching (e.g. Python in CPython) |
| 8. Scoring | Calculate separate similarity and coverage values; make weights visible. | Score components and explanation | Treating a demo score as a probability or validated quality measure |
| 9. Ranking/review | Sort scores and flag missing explicit requirements. Threshold is advisory. | Ranked candidates and review labels | Automatically rejecting a person based on one score |
| 10. Report | Save structured CSV and display component-level evidence. | `outputs/ranking_report.csv` | Committing output that contains real candidate data |
| 11. GitHub | Add docs/tests, inspect staged files, push synthetic data only. | Public reproducible portfolio repository | Committing `.venv`, credentials, or personal resumes |

## 5. Folder structure

```text
Automated-Resume-Screening-Tool/
├── resumes/                 # Fictional TXT/PDF/DOCX inputs
├── data/                    # Example JD and required skill phrases
├── src/                     # Shared logic, API, optional Streamlit page
├── outputs/                 # Generated CSV; ignored from Git by default
├── images/                  # Screenshots you capture for portfolio proof
├── docs/                    # This guide and later design notes
├── tests/                   # Unit tests for key behaviors
├── web/                     # Next.js dashboard client
├── main.py                  # CLI entry point
├── requirements.txt         # Python dependencies
├── .gitignore
└── README.md
```

## 6. Installation

### macOS/Linux

```bash
python3 --version
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Windows PowerShell

```powershell
py --version
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If PowerShell blocks activation, use Command Prompt's
`.\.venv\Scripts\activate.bat`, or invoke `.venv`'s Python directly. For the
web UI install Node.js 20.9+ and npm, then run `cd web; npm install`.

### Install test dependency

With the virtual environment activated:

```bash
python -m pip install -r requirements-dev.txt
```

### Exact MacBook startup, test, and CLI commands

Open two terminals in the project root (the directory containing `main.py`).
Terminal 1 starts the backend:

```bash
cd "/Users/mahvish/automated resume python"
source .venv/bin/activate
uvicorn src.api:app --host 127.0.0.1 --port 8000 --reload
```

Terminal 2 starts the dashboard:

```bash
cd "/Users/mahvish/automated resume python/web"
npm run dev -- --hostname 127.0.0.1
```

Open <http://127.0.0.1:3000> for the dashboard and
<http://127.0.0.1:8000/docs> for Swagger. Run the tests and CLI in another
terminal from the project root:

```bash
cd "/Users/mahvish/automated resume python"
source .venv/bin/activate
python -m unittest discover -s tests -v
python main.py
```

The CLI writes `outputs/ranking_report.csv`. In the dashboard, submit resumes,
then click **Download ranking CSV** to save the displayed results.

## 6.5. How the code is organized

- `main.py`: command-line arguments and report/summary output.
- `src/screening.py`: extraction, normalization, skill matching, experience
  mention extraction, scoring, sorting, and CSV writer.
- `src/api.py`: `/health` and multipart `/screen` endpoints.
- `src/streamlit_app.py`: optional Streamlit interface.
- `web/app/page.tsx`: Next.js upload form and score/evidence display.
- `tests/test_screening.py`: parser, matching, scoring, ranking, and CSV tests.
- `tests/test_api.py`: API routes, uploads, validation, duplicate names, and CORS.

The complete runnable code is in those repository files; this guide explains
how to exercise and extend it.

## 7. Input and output behavior

Supported input: `.txt`, `.pdf`, `.docx`. Text PDFs work; scanned PDFs return a
warning because OCR is deliberately outside this beginner project. DOCX
paragraphs and tables are included. Empty/unreadable content is called out
rather than scored as a successful match.

The required-skill file has one phrase per line; blank lines and `#` comments
are ignored. Matching is case-insensitive phrase matching on normalized
alphanumeric tokens. Keep skill phrases concise and role-relevant. The
experience extractor only recognizes explicit year counts; it does not
calculate employment duration from dates.

`overall_score` combines 60% TF-IDF similarity and 40% skill coverage. If a
required skill is missing, the report says “Needs human review - missing
required skills.” If all listed phrases match and the threshold is met, it says
“Shortlist for human review.” Otherwise, the label asks for review below
threshold. There is no reject label.

### API endpoints and documentation

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Return `{"status":"ok"}` when the API responds. |
| POST | `/screen` | Accept a job description, comma-separated skill phrases, optional threshold, and multiple resume files. |
| GET | `/docs` | Interactive Swagger UI. |
| GET | `/openapi.json` | OpenAPI schema used by Swagger. |

For `/screen`, field names are `job_description`, `required_skills`,
`threshold`, and repeated `resumes` file fields. Supported extensions are TXT,
PDF, and DOCX, limited to 10 MB per resume. Unsupported types return HTTP 415;
invalid documents and empty descriptions return HTTP 422; oversized files
return HTTP 413.

### CSV report

The CLI report is `outputs/ranking_report.csv`. Columns include the candidate
and filename, overall score, TF-IDF similarity, skill coverage,
experience-years-mentioned, matched and missing skills, review recommendation,
threshold flag, explanation, and warnings. Lists are semicolon-separated in
CSV cells. Output files are ignored by Git by default so uploaded personal
data cannot be accidentally committed. The dashboard export is named
`ranking_report.csv` and contains the displayed result evidence.

## 8. Virtual simulation

1. Open `resumes/` and inspect the three invented resumes.
2. Read `data/job_description.txt`; treat the phrases in
   `data/required_skills.txt` as demo requirements.
3. Run `python main.py`. The loader reads each supported file and the text
   extractor returns text and warnings.
4. For each resume, the scorer counts matched skill phrases and calculates
   cosine similarity between its TF-IDF vector and the JD vector.
5. It combines the two displayed score components, sorts descending, and flags
   gaps against the required list.
6. Open the generated CSV in a spreadsheet; compare score and explanation with
   the original synthetic resume.
7. Run API/dashboard if desired to simulate uploaded applications.

This is not a model trained on hiring outcomes; no company data or ATS access is
needed. Avoid claiming measured accuracy, real-world fairness, or predictive
validity.

## 9. Run and expected terminal output

From the activated environment at the project root:

```bash
python main.py
python -m unittest discover -s tests -v
```

CLI output lists the number processed, report path, ordered score, advisory
review label, and missing requirements. With the included sample data and
current scoring formula, the observed result is:

```text
Analyzed 3 resume(s).
Report: outputs/ranking_report.csv

alex analyst: 61.8/100 | Shortlist for human review | Missing required skills: None
jordan developer: 8.2/100 | Needs human review - missing required skills | Missing required skills: SQL, Pandas, Excel, Tableau, data visualization, statistics
sam generalist: 2.5/100 | Needs human review - missing required skills | Missing required skills: Python, SQL, Pandas, Excel, Tableau, data visualization, statistics
```

The CSV is at `outputs/ranking_report.csv`. These are demo scores, not
calibrated measures of candidate suitability.

API and Next.js:

```bash
# Terminal 1, project root
uvicorn src.api:app --reload

# Terminal 2
cd web
npm install
npm run dev
```

Visit `http://localhost:3000`; API docs are at `http://localhost:8000/docs`.
The API accepts up to 10 MB per resume.

On macOS this project's local report path is
`/Users/mahvish/automated resume python/outputs/ranking_report.csv`.

## 10. GitHub upload steps

1. Create a public GitHub repository named `automated-resume-screening-tool`.
2. Suggested description: “Educational Python/NLP demo for explainable
   resume-to-job matching with FastAPI and Next.js.”
3. This workspace has already been initialized and locally committed. Create
   an empty GitHub repository under your own account, then add its real URL as
   `origin` and push `main` using the commands in README. Do not copy a
   placeholder URL literally.
4. Use small descriptive commits, e.g. `Add document text extraction`,
   `Implement explainable skill scoring`, `Add FastAPI screening endpoint`,
   `Build recruiter dashboard`, `Document setup and responsible use`.
5. Add screenshots to `images/`; generated `outputs/` are intentionally
   ignored. Review `git status` and staged filenames before pushing.
6. Suggested GitHub topics: `python`, `nlp`, `resume-screening`, `fastapi`,
   `scikit-learn`, `tfidf`, `nextjs`, `hr-tech`, `responsible-ai`.

Never push real resumes, names/contact details, secrets, or employer data.

## 11. README and project description

The repository root `README.md` is the ready-to-publish project README. It
contains the overview, problem, relevance, features, tools, folder structure,
install/run steps, sample behavior, tests, screenshots checklist, and GitHub
metadata. Keep claims honest: present this as an educational prototype, not a
production hiring system.

The README includes an equivalent macOS/POSIX setup; for Windows PowerShell,
create and activate the environment using:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip install -r requirements-dev.txt
```

In the project root, run `uvicorn src.api:app --reload`; in another
PowerShell terminal run `cd web`, `npm install`, and `npm run dev`. Open
`http://127.0.0.1:3000` and `http://127.0.0.1:8000/docs`.

## 12. Six-day proof-building plan

| Day | Build and commit | Evidence screenshot |
|---|---|---|
| 1 — Setup | Create folders, venv, dependencies, and README foundation. `Set up project structure and dependencies` | Project folder tree |
| 2 — Extraction | Add TXT/PDF/DOCX parsing, sample fictional resumes, extraction tests. `Add resume text extraction` | Resume samples and parser output |
| 3 — JD matching | Add sample JD, skill phrase matching, and extraction/matching tests. `Match resumes to job requirements` | JD and skill list |
| 4 — Scoring | Add TF-IDF, cosine similarity, transparent score components, and ranking. `Add explainable resume scoring` | Ranking/score table |
| 5 — Reporting | Add CSV, FastAPI and browser interface. `Generate reports and expose screening API` | Terminal, CSV, API docs, dashboard |
| 6 — Documentation | Finish guide, test clean install, review privacy, push changes. `Document project and responsible use` | GitHub repository home/README |

Commit after each cohesive phase rather than one giant last-minute commit.

## 13. Screenshots and outputs

The `images/` folder contains genuine screenshots captured from the running
Next.js dashboard and FastAPI Swagger UI. Dashboard screenshots use the bundled
synthetic resumes and show the actual upload form, ranked results, scores,
matched/missing skills, and CSV download control.

| Screenshot | Evidence |
|---|---|
| `images/dashboard.png` | Main recruiter dashboard before upload. |
| `images/resume-upload.png` | Job description, required skills, and selected synthetic resumes. |
| `images/dashboard-results.png` | Dashboard after submitting all three synthetic resumes. |
| `images/candidate-ranking.png` | Ranked candidate scores and review recommendations. |
| `images/matched-missing-skills.png` | Candidate score with matched and missing requirements. |
| `images/csv-report.png` | CSV download control on the populated results page. |
| `images/api-swagger.png` | Live FastAPI Swagger documentation page. |

Review the CSV directly at `outputs/ranking_report.csv`. The CLI writes the
report; the dashboard offers its displayed response rows as a browser CSV
download.

## 14. Limitations, future scope, and learning outcomes

The matching is lexical, the score weights are illustrative, scanned-PDF OCR
is not included, and there is no validated hiring-outcome data. Parsing can
omit information; neither a score nor a missing keyword establishes
qualification. Do not use protected traits or proxies to rank candidates.
Always require a qualified human to review the source resume and job-related
evidence. The demo has no authentication, deployed security controls, or
applicant-data retention system and is not suitable for real hiring.

Future learning extensions include OCR with clear verification, reviewed
skill aliases, accessibility improvements, additional parser fixtures,
privacy-safe evaluation, and security/retention controls before any real-world
use.

Learning outcomes include Python modules and CLI design, document extraction,
regex-based normalization and phrase matching, Pandas CSV workflows,
scikit-learn TF-IDF/cosine similarity, score validation, FastAPI multipart
uploads, Next.js/TypeScript form integration, unit/integration testing,
documentation, Git/GitHub, and responsible AI limitations.

## 15. Interview preparation

### 1. “Explain your project.”

**Strong answer:** “I built an educational resume-to-job comparison tool in
Python. It extracts text from TXT, PDF, and DOCX files, compares each resume
with a job description using TF-IDF and cosine similarity, and checks an
explicit list of required skill phrases. It ranks candidates and writes a CSV
with score components, matched skills, gaps, and warnings. I exposed the
pipeline through FastAPI and built a Next.js dashboard. It is decision support
only: the score is a transparent demo formula, and a human must inspect the
original resume.”

### 2. What problem does the project address?

It demonstrates how to organize and compare resume information against a
specific role, reducing repetitive manual searching in a synthetic portfolio
scenario. It does not replace recruiter judgment.

### 3. What is TF-IDF?

Term Frequency–Inverse Document Frequency weights terms by their occurrence
within a document and how uncommon they are across the comparison corpus. Here
it helps represent job and resume text as numeric vectors.

### 4. How does cosine similarity work?

It measures the cosine of the angle between two vectors. A higher value usually
means more similar term patterns. It is not a probability that someone is
qualified.

### 5. How do you handle must-have skills?

The user supplies skill phrases explicitly. The matcher normalizes punctuation
and case and compares full phrases, then reports present and missing phrases.
The list should be reviewed for each role and should not include arbitrary
preferences.

### 6. How is the final score calculated?

Sixty percent is TF-IDF similarity and forty percent is required skill
coverage. Both components are shown. Those weights are illustrative, not
learned from validated hiring data.

### 7. How do you parse PDF and Word files?

pdfplumber extracts selectable PDF text, and python-docx reads DOCX paragraphs
and tables. A scanned PDF may have no text layer, so the project flags it and
does not claim OCR support.

### 8. What are the limitations and bias risks?

Keyword matching misses synonyms and context, document extraction can fail,
and historic or poorly chosen requirements can unfairly exclude people.
Similarity and years mentioned are not measures of ability. I use synthetic
data, avoid protected traits, expose evidence, and require human review. A
real deployment would need legal/privacy review, validation, accessibility
and fairness testing, security controls, and monitoring.

### 9. What is a limitation and how did you address it?

TF-IDF and skill phrase matching can miss synonyms and context, so their
scores are not hiring probabilities. Scanned PDFs also require OCR, which is
not part of this demo. I show score evidence and gaps and require a human to
review the original resume.

### 10. How would you improve it?

Add carefully tested skill aliases, OCR with a clear human verification step,
robust parser fixtures, role-specific evaluation, access controls and retention
limits, audit logs, accessibility work, and a validated human-centered
evaluation process. Do not add a more complex model without representative,
lawfully sourced data and impact assessment.

### 11. Why provide both an API and dashboard?

The API separates parsing/scoring from presentation and can serve other
clients. The Next.js interface gives a recruiter a simple upload form and
readable evidence view. Keeping one Python scoring function avoids divergent
results across the CLI and API.

### 12. How would you verify the generated CSV?

Check that rows follow score order, and that matched/missing phrases and
explanations correspond to each result. In the browser, verify the exported
filename is `ranking_report.csv` and its candidate rows match the displayed
ranking.
