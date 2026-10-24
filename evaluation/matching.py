"""
matching.py

Deterministic, stable matching between expected findings (from the answer
key) and predicted findings (from the analyzer) for a single case.

Matching rule (documented so it is reproducible and auditable):
  1. A predicted finding matches an expected finding if they share the same
     rule_id AND the same issue_type.
  2. Each expected finding may be matched to at most one predicted finding,
     and vice versa (one-to-one matching, no double counting).
  3. Matching is order-stable: expected findings are matched in the order
     they appear in the answer key, each against the first unmatched
     predicted finding satisfying rule (1).
  4. Any expected finding left unmatched after this pass is a False Negative.
  5. Any predicted finding left unmatched after this pass is a False
     Positive.
  6. If expected_status == "compliant" (no expected findings), every
     predicted finding is automatically a False Positive.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from evaluation.analyzer_adapter import Finding


@dataclass
class CaseMatchResult:
    case_id: str
    true_positives: list[tuple[dict, Finding]] = field(default_factory=list)   # (expected, predicted)
    false_negatives: list[dict] = field(default_factory=list)                  # expected, unmatched
    false_positives: list[Finding] = field(default_factory=list)               # predicted, unmatched

    @property
    def tp_count(self) -> int:
        return len(self.true_positives)

    @property
    def fn_count(self) -> int:
        return len(self.false_negatives)

    @property
    def fp_count(self) -> int:
        return len(self.false_positives)


def match_findings(case_id: str, expected_findings: list[dict], predicted_findings: list[Finding]) -> CaseMatchResult:
    result = CaseMatchResult(case_id=case_id)
    remaining_predicted = list(predicted_findings)

    for expected in expected_findings:
        exp_rule_id = expected.get("rule_id")
        exp_issue_type = expected.get("issue_type")

        match_index = None
        for idx, predicted in enumerate(remaining_predicted):
            if predicted.issue_type == exp_issue_type and (
                not exp_rule_id or predicted.rule_id == exp_rule_id
            ):
                match_index = idx
                break

        if match_index is not None:
            matched = remaining_predicted.pop(match_index)
            result.true_positives.append((expected, matched))
        else:
            result.false_negatives.append(expected)

    # Anything left in remaining_predicted had no corresponding expected finding.
    result.false_positives.extend(remaining_predicted)

    return result


def derive_case_status_correct(expected_status: str, predicted_status: str) -> bool:
    return expected_status == predicted_status
