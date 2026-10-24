"""
metrics.py

Pure, deterministic metric calculations over already-computed case-level
match results. No analyzer calls and no file I/O here, so this module is
trivially unit-testable with fixtures.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class CaseOutcome:
    """Minimal per-case record metrics.py needs; produced by evaluate.py."""
    case_id: str
    category: str
    expected_status: str
    predicted_status: str
    tp: int
    fp: int
    fn: int
    analyzer_error: bool = False


@dataclass
class MetricsSummary:
    total_cases: int
    completed_cases: int
    failed_cases: int
    true_positives: int
    false_positives: int
    false_negatives: int
    precision: float
    recall: float
    f1: float
    case_level_accuracy: float
    compliant_case_count: int
    problematic_case_count: int


def safe_divide(numerator: float, denominator: float) -> float:
    """Zero-denominator handling: returns 0.0 rather than raising."""
    if denominator == 0:
        return 0.0
    return numerator / denominator


def precision_recall_f1(tp: int, fp: int, fn: int) -> tuple[float, float, float]:
    precision = safe_divide(tp, tp + fp)
    recall = safe_divide(tp, tp + fn)
    f1 = safe_divide(2 * precision * recall, precision + recall)
    return precision, recall, f1


def case_level_accuracy(outcomes: list[CaseOutcome]) -> float:
    evaluable = [o for o in outcomes if not o.analyzer_error]
    if not evaluable:
        return 0.0
    correct = sum(1 for o in evaluable if o.expected_status == o.predicted_status)
    return safe_divide(correct, len(evaluable))


def summarize(outcomes: list[CaseOutcome]) -> MetricsSummary:
    total = len(outcomes)
    failed = [o for o in outcomes if o.analyzer_error]
    completed = [o for o in outcomes if not o.analyzer_error]

    tp = sum(o.tp for o in completed)
    fp = sum(o.fp for o in completed)
    fn = sum(o.fn for o in completed)
    precision, recall, f1 = precision_recall_f1(tp, fp, fn)

    compliant_count = sum(1 for o in outcomes if o.expected_status == "compliant")
    problematic_count = sum(1 for o in outcomes if o.expected_status == "problematic")

    return MetricsSummary(
        total_cases=total,
        completed_cases=len(completed),
        failed_cases=len(failed),
        true_positives=tp,
        false_positives=fp,
        false_negatives=fn,
        precision=round(precision, 4),
        recall=round(recall, 4),
        f1=round(f1, 4),
        case_level_accuracy=round(case_level_accuracy(outcomes), 4),
        compliant_case_count=compliant_count,
        problematic_case_count=problematic_count,
    )


def category_breakdown(outcomes: list[CaseOutcome]) -> dict[str, MetricsSummary]:
    by_category: dict[str, list[CaseOutcome]] = {}
    for o in outcomes:
        by_category.setdefault(o.category, []).append(o)
    return {category: summarize(cases) for category, cases in by_category.items()}
