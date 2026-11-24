"use client";

import { FormEvent, useState } from "react";

type Result = {
  candidate: string;
  resume_file: string;
  overall_score: number;
  similarity_score: number;
  skill_coverage_score: number;
  experience_years_mentioned: number | null;
  matched_skills: string[];
  missing_skills: string[];
  recommendation: string;
  meets_review_threshold: boolean;
  explanation: string;
  warnings: string[];
};

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const csvColumns: (keyof Result)[] = [
  "candidate",
  "resume_file",
  "overall_score",
  "similarity_score",
  "skill_coverage_score",
  "experience_years_mentioned",
  "matched_skills",
  "missing_skills",
  "recommendation",
  "meets_review_threshold",
  "explanation",
  "warnings",
];

function csvCell(value: Result[keyof Result]): string {
  const text = Array.isArray(value)
    ? value.join("; ")
    : value === null
      ? ""
      : String(value);
  return `"${text.replaceAll('"', '""')}"`;
}

function downloadCsv(results: Result[]): void {
  const rows = [
    csvColumns.map(csvCell).join(","),
    ...results.map((result) =>
      csvColumns.map((column) => csvCell(result[column])).join(","),
    ),
  ];
  const url = URL.createObjectURL(
    new Blob([rows.join("\r\n")], { type: "text/csv;charset=utf-8" }),
  );
  const link = document.createElement("a");
  link.href = url;
  link.download = "ranking_report.csv";
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.setTimeout(() => URL.revokeObjectURL(url), 1000);
}

export default function Home() {
  const [results, setResults] = useState<Result[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setResults([]);
    setLoading(true);
    const form = event.currentTarget;
    const payload = new FormData(form);
    try {
      const response = await fetch(`${API_URL}/screen`, {
        method: "POST",
        body: payload,
      }).catch((reason: unknown) => {
        const detail =
          reason instanceof Error ? reason.message : "Unknown connection error";
        throw new Error(`Could not reach the screening API at ${API_URL}: ${detail}`);
      });
      const body = await response.json();
      if (!response.ok) {
        throw new Error(body.detail ?? `Screening request failed (${response.status}).`);
      }
      setResults(body.results as Result[]);
    } catch (reason) {
      setError(
        reason instanceof Error ? reason.message : "Unexpected screening error.",
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="container">
      <header>
        <p className="eyebrow">STUDENT PORTFOLIO PROJECT</p>
        <h1>Automated Resume Screening</h1>
        <p className="lede">
          Compare resume evidence with role requirements. Every result is
          decision support, not an automated hiring decision.
        </p>
      </header>

      <form className="panel form" onSubmit={submit}>
        <label>
          Job description
          <textarea name="job_description" required rows={7} />
        </label>
        <label>
          Required skills <span className="hint">(comma-separated)</span>
          <input name="required_skills" placeholder="Python, SQL, Excel" />
        </label>
        <label>
          Review threshold (0–100)
          <input name="threshold" type="number" min="0" max="100" defaultValue="55" />
        </label>
        <label>
          Resumes <span className="hint">(PDF, DOCX, TXT; max 10 MB each)</span>
          <input name="resumes" type="file" accept=".pdf,.docx,.txt" multiple required />
        </label>
        <button disabled={loading}>{loading ? "Comparing…" : "Compare resumes"}</button>
        {error && <p className="error" role="alert">{error}</p>}
      </form>

      {results.length > 0 && (
        <section className="results">
          <h2>Ranked candidates</h2>
          <p className="notice">
            Review the source documents and job-related evidence before making
            any decision. Do not use protected traits or proxy variables.
          </p>
          <button onClick={() => downloadCsv(results)} type="button">
            Download ranking CSV
          </button>
          {results.map((result, index) => (
            <article className="panel result" key={`${result.resume_file}-${index}`}>
              <div className="result-heading">
                <div>
                  <h3>{result.candidate}</h3>
                  <p>{result.recommendation}</p>
                </div>
                <strong>{result.overall_score.toFixed(1)}<small> / 100</small></strong>
              </div>
              <p>{result.explanation}</p>
              <dl>
                <div><dt>Job text similarity</dt><dd>{result.similarity_score.toFixed(1)}%</dd></div>
                <div><dt>Required skill coverage</dt><dd>{result.skill_coverage_score.toFixed(1)}%</dd></div>
                <div>
                  <dt>Experience stated</dt>
                  <dd>{result.experience_years_mentioned === null ? "Not detected" : `${result.experience_years_mentioned} years`}</dd>
                </div>
              </dl>
              <p><b>Matched:</b> {result.matched_skills.join(", ") || "None detected"}</p>
              <p><b>Missing:</b> {result.missing_skills.join(", ") || "None detected"}</p>
              {result.warnings.map((warning) => <p className="warning" key={warning}>{warning}</p>)}
            </article>
          ))}
        </section>
      )}
      <footer>Demo uses synthetic resumes. Scores can be incomplete or misleading; human review is required.</footer>
    </main>
  );
}
