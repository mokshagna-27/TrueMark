"""
evaluate.py

Main evaluation runner. Loads the brand pack, dataset, and answer key,
calls the AI analyzer (real or mock) for every case, matches predicted
findings against expected findings, computes metrics, runs error analysis,
and writes JSON + Markdown reports.

Usage:
    python -m evaluation.evaluate --use-mock
    python -m evaluation.evaluate --analyzer-module backend.ai_engine.analyzer
    python -m evaluation.evaluate --analyzer-module backend.ai_engine.analyzer --analyzer-attr analyze --limit 50

Real evaluation requires a real, importable analyzer module exposing
analyze(draft, channel) -> dict. If it cannot be found, this script reports
that real evaluation is pending instead of fabricating numbers (see
analyzer_adapter.RealAnalyzerAdapter).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
REPO_ROOT = THIS_DIR.parent
sys.path.insert(0, str(REPO_ROOT))

from evaluation.analyzer_adapter import (  # noqa: E402
    AnalyzerNotIntegratedError,
    AnalyzerResult,
    build_adapter,
)
from evaluation.data_loading import DataValidationError, load_all, validate_all  # noqa: E402
from evaluation.error_analysis import build_error_analysis  # noqa: E402
from evaluation.matching import match_findings  # noqa: E402
from evaluation.metrics import CaseOutcome, category_breakdown, summarize  # noqa: E402
from evaluation.reporting import (  # noqa: E402
    build_json_report,
    build_markdown_report,
    write_json_report,
    write_markdown_report,
)

DEFAULT_DATA_DIR = REPO_ROOT / "data"
DEFAULT_REPORTS_DIR = THIS_DIR / "reports"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the TrueMark Data & Evaluation suite.")
    parser.add_argument("--data-dir", default=str(DEFAULT_DATA_DIR), help="Directory containing brand_pack.json etc.")
    parser.add_argument("--reports-dir", default=str(DEFAULT_REPORTS_DIR), help="Directory to write reports into.")
    parser.add_argument("--use-mock", action="store_true", help="Use the mock analyzer (pipeline validation only).")
    parser.add_argument("--analyzer-module", default="", help="Import path of the real analyzer module, e.g. backend.ai_engine.analyzer")
    parser.add_argument("--analyzer-attr", default="analyze", help="Attribute name of the analyze function in that module (default: analyze).")
    parser.add_argument("--limit", type=int, default=0, help="Only evaluate the first N cases (0 = all). Useful for smoke tests on large datasets.")
    parser.add_argument("--fail-on-validation-error", action="store_true", help="Exit non-zero if data validation finds errors, instead of continuing.")
    return parser.parse_args(argv)


def run(args: argparse.Namespace) -> int:
    data_dir = Path(args.data_dir)
    reports_dir = Path(args.reports_dir)

    try:
        data = load_all(data_dir)
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}")
        return 2
    except DataValidationError as exc:
        print(f"ERROR: {exc}")
        return 2

    validation_errors = validate_all(data)
    if validation_errors:
        print(f"Data validation found {len(validation_errors)} issue(s):")
        for err in validation_errors:
            print(f"  - {err}")
        if args.fail_on_validation_error:
            return 2
        print("Continuing evaluation despite validation issues (use --fail-on-validation-error to stop here).\n")

    if not args.use_mock and not args.analyzer_module:
        print(
            "No analyzer specified. Pass --use-mock for a pipeline-only dry run, "
            "or --analyzer-module <import.path> to run against the real analyzer."
        )
        return 2

    adapter = build_adapter(
        use_mock=args.use_mock,
        module_path=args.analyzer_module,
        attr_path=args.analyzer_attr,
    )

    cases = data.dataset.get("cases", [])
    if args.limit:
        cases = cases[: args.limit]

    answers_by_id = {a["case_id"]: a for a in data.answer_key.get("answers", []) if "case_id" in a}

    outcomes: list[CaseOutcome] = []
    case_records: list[dict] = []
    skipped_no_answer = 0
    analyzer_not_integrated = False

    for case in cases:
        case_id = case.get("case_id")
        answer = answers_by_id.get(case_id)
        if answer is None:
            skipped_no_answer += 1
            continue

        draft = case.get("draft", "")
        channel = case.get("channel", "")
        category = case.get("category", "uncategorized")
        expected_status = answer.get("expected_status", case.get("expected_status", "compliant"))
        expected_findings = answer.get("expected_findings", case.get("expected_findings", []))

        try:
            result: AnalyzerResult = adapter.run(draft, channel)
        except AnalyzerNotIntegratedError as exc:
            analyzer_not_integrated = True
            case_records.append({
                "case_id": case_id, "category": category, "channel": channel, "draft": draft,
                "analyzer_error": str(exc),
            })
            outcomes.append(CaseOutcome(
                case_id=case_id, category=category, expected_status=expected_status,
                predicted_status="error", tp=0, fp=0, fn=0, analyzer_error=True,
            ))
            continue

        if not result.ok:
            case_records.append({
                "case_id": case_id, "category": category, "channel": channel, "draft": draft,
                "analyzer_error": result.error,
            })
            outcomes.append(CaseOutcome(
                case_id=case_id, category=category, expected_status=expected_status,
                predicted_status="error", tp=0, fp=0, fn=0, analyzer_error=True,
            ))
            continue

        match = match_findings(case_id, expected_findings, result.findings)

        outcomes.append(CaseOutcome(
            case_id=case_id, category=category, expected_status=expected_status,
            predicted_status=result.status, tp=match.tp_count, fp=match.fp_count, fn=match.fn_count,
            analyzer_error=False,
        ))

        case_records.append({
            "case_id": case_id, "category": category, "channel": channel, "draft": draft,
            "analyzer_error": None,
            "false_negatives": [
                {
                    "rule_id": fn.get("rule_id", ""), "issue_type": fn.get("issue_type", ""),
                    "severity": fn.get("severity", ""), "text_span": fn.get("text_span", ""),
                    "explanation": fn.get("explanation", ""),
                }
                for fn in match.false_negatives
            ],
            "false_positives": [
                {
                    "rule_id": fp.rule_id, "issue_type": fp.issue_type,
                    "severity": fp.severity, "text_span": fp.text_span,
                    "explanation": fp.explanation,
                }
                for fp in match.false_positives
            ],
        })

    if skipped_no_answer:
        print(f"WARNING: {skipped_no_answer} case(s) had no matching answer_key entry and were skipped.")

    overall = summarize(outcomes)
    by_category = category_breakdown(outcomes)
    error_report = build_error_analysis(case_records)

    analyzer_integrated = args.use_mock is False and not analyzer_not_integrated and len(outcomes) > 0

    recommendations: list[str] = []
    if error_report.false_negatives:
        recommendations.append(
            f"{len(error_report.false_negatives)} expected finding(s) were missed. "
            f"Share top_missed_detections with the AI and Language Lead, prioritized by severity."
        )
    if error_report.false_positives:
        recommendations.append(
            f"{len(error_report.false_positives)} unexpected finding(s) were raised. "
            f"Review top_false_alarms for over-triggering rules."
        )
    if error_report.analyzer_failures:
        recommendations.append(
            f"{len(error_report.analyzer_failures)} case(s) failed to evaluate due to analyzer errors "
            f"or missing integration; see 'analyzer_failures' in this report."
        )
    if not analyzer_integrated:
        recommendations.append(
            "Real analyzer evaluation is pending. Run again with --analyzer-module pointing at the "
            "real analyzer once it is available."
        )
    if not recommendations:
        recommendations.append("No issues detected in this run.")

    dataset_limitations = [
        f"Dataset version: {data.dataset.get('dataset_version', 'unknown')}.",
        "Matching is rule_id + issue_type based; it does not score partial text-span overlap.",
        "Severity-weighted scoring is not implemented; all findings are weighted equally in precision/recall.",
    ]
    if skipped_no_answer:
        dataset_limitations.append(f"{skipped_no_answer} dataset case(s) had no answer_key entry and were excluded from metrics.")
    if validation_errors:
        dataset_limitations.append(f"{len(validation_errors)} data validation issue(s) were present during this run.")

    methodology = (
        "Each dataset case's draft and channel are passed to the analyzer via "
        "analyzer_adapter. Predicted findings are matched 1:1 against the "
        "answer key's expected findings by (rule_id, issue_type); unmatched "
        "expected findings are false negatives, unmatched predicted findings "
        "are false positives. Precision/recall/F1 are computed over pooled "
        "TP/FP/FN counts; case-level accuracy compares the analyzer's overall "
        "status (compliant/problematic) against the answer key's expected_status."
    )

    json_report = build_json_report(
        dataset_version=str(data.dataset.get("dataset_version", "unknown")),
        analyzer_integrated=analyzer_integrated,
        overall=overall,
        by_category=by_category,
        error_report=error_report,
        recommendations=recommendations,
        dataset_limitations=dataset_limitations,
        methodology=methodology,
    )
    markdown_report = build_markdown_report(json_report)

    json_path = reports_dir / "evaluation_report.json"
    md_path = reports_dir / "evaluation_report.md"
    write_json_report(json_report, json_path)
    write_markdown_report(markdown_report, md_path)

    print(f"Evaluated {overall.completed_cases}/{overall.total_cases} cases "
          f"({overall.failed_cases} failed). Precision={overall.precision:.2%} "
          f"Recall={overall.recall:.2%} F1={overall.f1:.2%} "
          f"Case accuracy={overall.case_level_accuracy:.2%}")
    print(f"Reports written to:\n  {json_path}\n  {md_path}")

    return 0


def main() -> None:
    args = parse_args()
    sys.exit(run(args))


if __name__ == "__main__":
    main()
