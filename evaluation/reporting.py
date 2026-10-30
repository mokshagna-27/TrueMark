"""
reporting.py

Renders the JSON and Markdown evaluation reports from already-computed
results. Never computes metrics itself and never fabricates numbers --
it only formats what evaluate.py / metrics.py / error_analysis.py produced.
"""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from evaluation.error_analysis import ErrorAnalysisReport
from evaluation.metrics import MetricsSummary


def _metrics_to_dict(m: MetricsSummary) -> dict:
    return asdict(m)


def build_json_report(
    dataset_version: str,
    analyzer_integrated: bool,
    overall: MetricsSummary,
    by_category: dict[str, MetricsSummary],
    error_report: ErrorAnalysisReport,
    recommendations: list[str],
    dataset_limitations: list[str],
    methodology: str,
) -> dict:
    return {
        "evaluation_date": datetime.now(timezone.utc).isoformat(),
        "dataset_version": dataset_version,
        "analyzer_integrated": analyzer_integrated,
        "overall_metrics": _metrics_to_dict(overall),
        "category_metrics": {cat: _metrics_to_dict(m) for cat, m in by_category.items()},
        "false_negative_count": len(error_report.false_negatives),
        "false_positive_count": len(error_report.false_positives),
        "analyzer_failure_count": len(error_report.analyzer_failures),
        "top_missed_detections": [asdict(e) for e in error_report.top_missed_detections()],
        "top_false_alarms": [asdict(e) for e in error_report.top_false_alarms()],
        "analyzer_failures": [asdict(e) for e in error_report.analyzer_failures],
        "recommendations": recommendations,
        "dataset_limitations": dataset_limitations,
        "methodology": methodology,
    }


def write_json_report(report: dict, output_path: str | Path) -> None:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)


def _metrics_table_row(label: str, m: MetricsSummary) -> str:
    return (
        f"| {label} | {m.total_cases} | {m.true_positives} | {m.false_positives} | "
        f"{m.false_negatives} | {m.precision:.2%} | {m.recall:.2%} | {m.f1:.2%} | "
        f"{m.case_level_accuracy:.2%} |"
    )


def build_markdown_report(json_report: dict) -> str:
    lines: list[str] = []
    lines.append("# TrueMark Evaluation Report")
    lines.append("")
    lines.append(f"- **Evaluation date:** {json_report['evaluation_date']}")
    lines.append(f"- **Dataset version:** {json_report['dataset_version']}")
    lines.append(f"- **Analyzer integrated:** {json_report['analyzer_integrated']}")
    lines.append("")

    if not json_report["analyzer_integrated"]:
        lines.append(
            "> **Note:** The real TrueMark analyzer is not yet integrated. "
            "The metrics below reflect pipeline validation only and are "
            "**not** real evaluation results. Real evaluation is pending."
        )
        lines.append("")

    overall = json_report["overall_metrics"]
    lines.append("## Overall Results")
    lines.append("")
    lines.append(f"- Total cases: {overall['total_cases']}")
    lines.append(f"- Completed evaluations: {overall['completed_cases']}")
    lines.append(f"- Failed evaluations (analyzer errors): {overall['failed_cases']}")
    lines.append(f"- Compliant drafts (expected): {overall['compliant_case_count']}")
    lines.append(f"- Problematic drafts (expected): {overall['problematic_case_count']}")
    lines.append("")
    lines.append("| Scope | Total | TP | FP | FN | Precision | Recall | F1 | Case Accuracy |")
    lines.append("|---|---|---|---|---|---|---|---|---|")
    lines.append(_metrics_table_row("Overall", _dict_to_metrics(overall)))
    lines.append("")

    lines.append("## Category-Level Metrics")
    lines.append("")
    lines.append("| Category | Total | TP | FP | FN | Precision | Recall | F1 | Case Accuracy |")
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for category, m in json_report["category_metrics"].items():
        lines.append(_metrics_table_row(category, _dict_to_metrics(m)))
    lines.append("")

    lines.append("## Important Missed Detections (False Negatives)")
    lines.append("")
    if json_report["top_missed_detections"]:
        for e in json_report["top_missed_detections"]:
            lines.append(
                f"- **[{e['severity']}]** `{e['case_id']}` ({e['category']} / {e['channel']}) "
                f"— missed `{e['rule_id']}` / `{e['issue_type']}` on \"{e['text_span']}\": {e['explanation']}"
            )
    else:
        lines.append("_None recorded._")
    lines.append("")

    lines.append("## Important False Alarms (False Positives)")
    lines.append("")
    if json_report["top_false_alarms"]:
        for e in json_report["top_false_alarms"]:
            lines.append(
                f"- **[{e['severity']}]** `{e['case_id']}` ({e['category']} / {e['channel']}) "
                f"— unexpected `{e['rule_id']}` / `{e['issue_type']}` on \"{e['text_span']}\": {e['analyzer_explanation']}"
            )
    else:
        lines.append("_None recorded._")
    lines.append("")

    lines.append("## Analyzer Failures")
    lines.append("")
    if json_report["analyzer_failures"]:
        for e in json_report["analyzer_failures"]:
            lines.append(f"- `{e['case_id']}` ({e['category']} / {e['channel']}): {e['error_message']}")
    else:
        lines.append("_None recorded._")
    lines.append("")

    lines.append("## Recommendations")
    lines.append("")
    for rec in json_report["recommendations"]:
        lines.append(f"- {rec}")
    lines.append("")

    lines.append("## Dataset Limitations")
    lines.append("")
    for lim in json_report["dataset_limitations"]:
        lines.append(f"- {lim}")
    lines.append("")

    lines.append("## Methodology")
    lines.append("")
    lines.append(json_report["methodology"])
    lines.append("")

    return "\n".join(lines)


def _dict_to_metrics(d: dict) -> MetricsSummary:
    return MetricsSummary(**d)


def write_markdown_report(markdown: str, output_path: str | Path) -> None:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        f.write(markdown)
