"""
error_analysis.py

Builds human-reviewable false-positive and false-negative examples from
case-level match results, ranked by severity so the most important misses
and false alarms surface first. Intended output feeds directly back to the
AI and Language Lead as reproducible examples.
"""

from __future__ import annotations

from dataclasses import dataclass, field

_SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}


def _severity_rank(severity: str) -> int:
    return _SEVERITY_ORDER.get(severity, len(_SEVERITY_ORDER))


@dataclass
class FalseNegativeExample:
    case_id: str
    category: str
    channel: str
    draft: str
    rule_id: str
    issue_type: str
    severity: str
    text_span: str
    explanation: str


@dataclass
class FalsePositiveExample:
    case_id: str
    category: str
    channel: str
    draft: str
    rule_id: str
    issue_type: str
    severity: str
    text_span: str
    analyzer_explanation: str


@dataclass
class AnalyzerFailure:
    case_id: str
    category: str
    channel: str
    error_message: str


@dataclass
class ErrorAnalysisReport:
    false_negatives: list[FalseNegativeExample] = field(default_factory=list)
    false_positives: list[FalsePositiveExample] = field(default_factory=list)
    analyzer_failures: list[AnalyzerFailure] = field(default_factory=list)

    def top_missed_detections(self, limit: int = 10) -> list[FalseNegativeExample]:
        return sorted(self.false_negatives, key=lambda e: _severity_rank(e.severity))[:limit]

    def top_false_alarms(self, limit: int = 10) -> list[FalsePositiveExample]:
        return sorted(self.false_positives, key=lambda e: _severity_rank(e.severity))[:limit]


def build_error_analysis(case_records: list[dict]) -> ErrorAnalysisReport:
    """
    case_records: list of dicts, each produced by evaluate.py, shaped as:
        {
            "case_id": str, "category": str, "channel": str, "draft": str,
            "analyzer_error": str | None,
            "false_negatives": [ {rule_id, issue_type, severity, text_span, explanation}, ... ],
            "false_positives": [ {rule_id, issue_type, severity, text_span, explanation}, ... ],
        }
    """
    report = ErrorAnalysisReport()

    for record in case_records:
        case_id = record.get("case_id", "")
        category = record.get("category", "")
        channel = record.get("channel", "")
        draft = record.get("draft", "")

        if record.get("analyzer_error"):
            report.analyzer_failures.append(
                AnalyzerFailure(
                    case_id=case_id, category=category, channel=channel,
                    error_message=str(record["analyzer_error"]),
                )
            )
            continue

        for fn in record.get("false_negatives", []):
            report.false_negatives.append(
                FalseNegativeExample(
                    case_id=case_id, category=category, channel=channel, draft=draft,
                    rule_id=fn.get("rule_id", ""), issue_type=fn.get("issue_type", ""),
                    severity=fn.get("severity", ""), text_span=fn.get("text_span", ""),
                    explanation=fn.get("explanation", ""),
                )
            )

        for fp in record.get("false_positives", []):
            report.false_positives.append(
                FalsePositiveExample(
                    case_id=case_id, category=category, channel=channel, draft=draft,
                    rule_id=fp.get("rule_id", ""), issue_type=fp.get("issue_type", ""),
                    severity=fp.get("severity", ""), text_span=fp.get("text_span", ""),
                    analyzer_explanation=fp.get("explanation", ""),
                )
            )

    return report
