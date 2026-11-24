"""Command-line entry point for the resume screening demo."""

from __future__ import annotations

import argparse
from pathlib import Path

from src.screening import create_report, load_resumes, read_text_file, screen_candidates


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare sample resumes with a job description."
    )
    parser.add_argument("--resumes", type=Path, default=Path("resumes"))
    parser.add_argument(
        "--job-description", type=Path, default=Path("data/job_description.txt")
    )
    parser.add_argument(
        "--required-skills", type=Path, default=Path("data/required_skills.txt")
    )
    parser.add_argument("--output", type=Path, default=Path("outputs/ranking_report.csv"))
    parser.add_argument(
        "--threshold",
        type=float,
        default=55.0,
        help="Score threshold for the advisory 'shortlist for review' label.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not 0 <= args.threshold <= 100:
        raise SystemExit("--threshold must be between 0 and 100.")

    try:
        job_description = read_text_file(args.job_description)
        required_skills = [
            skill.strip()
            for skill in read_text_file(args.required_skills).splitlines()
            if skill.strip() and not skill.strip().startswith("#")
        ]
        resumes = load_resumes(args.resumes)
        results = screen_candidates(
            resumes, job_description, required_skills, args.threshold
        )
        report_path = create_report(results, args.output)
    except (OSError, ValueError) as exc:
        raise SystemExit(f"Error: {exc}") from exc

    print(f"Analyzed {len(results)} resume(s).")
    print(f"Report: {report_path}")
    print()
    for result in results:
        gaps = ", ".join(result["missing_skills"]) or "None"
        print(
            f'{result["candidate"]}: {result["overall_score"]:.1f}/100 | '
            f'{result["recommendation"]} | Missing required skills: {gaps}'
        )
    print("\nRecommendations are decision support only; a person must review every candidate.")


if __name__ == "__main__":
    main()
