"""
data_loading.py

Loading and structural validation for brand_pack.json, evaluation_dataset.json,
answer_key.json, and source_registry.json.

Kept separate from evaluate.py / metrics.py so it can be reused by
validate_data.py and the test suite without pulling in analyzer or reporting
dependencies.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class DataValidationError(ValueError):
    """Raised when a data file is missing required structure."""


def load_json(path: str | Path) -> dict:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Required data file not found: {path}")
    with path.open("r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError as exc:
            raise DataValidationError(f"Invalid JSON in {path}: {exc}") from exc


@dataclass
class LoadedData:
    brand_pack: dict
    dataset: dict
    answer_key: dict
    source_registry: dict


def load_all(data_dir: str | Path) -> LoadedData:
    data_dir = Path(data_dir)
    return LoadedData(
        brand_pack=load_json(data_dir / "brand_pack.json"),
        dataset=load_json(data_dir / "evaluation_dataset.json"),
        answer_key=load_json(data_dir / "answer_key.json"),
        source_registry=load_json(data_dir / "source_registry.json"),
    )


def _collect_rule_ids(brand_pack: dict) -> set[str]:
    """
    Recursively scans the entire brand pack for any 'rule_id' key, regardless
    of how deeply nested it is (direct dict, list of dicts, nested 'rules'
    lists, etc.). This keeps validation working even as the brand pack's
    internal structure evolves, without requiring data_loading.py to track
    every section's exact shape.
    """
    rule_ids: set[str] = set()

    def _walk(node: Any) -> None:
        if isinstance(node, dict):
            rule_id = node.get("rule_id")
            if isinstance(rule_id, str) and rule_id:
                rule_ids.add(rule_id)
            for value in node.values():
                _walk(value)
        elif isinstance(node, list):
            for item in node:
                _walk(item)

    _walk(brand_pack)
    return rule_ids


def validate_brand_pack(brand_pack: dict) -> list[str]:
    """Returns a list of validation error messages (empty = valid)."""
    errors: list[str] = []
    required_top_level = [
        "schema_version", "brand_id", "brand_identity", "approved_terminology",
        "claims_policy", "verified_brand_facts", "channel_guidance",
        "readability_requirements", "privacy_guidelines", "severity_levels",
    ]
    for key in required_top_level:
        if key not in brand_pack:
            errors.append(f"brand_pack.json missing required top-level key: '{key}'")

    severity_levels = brand_pack.get("severity_levels", {})
    for level in ("critical", "high", "medium", "low"):
        if level not in severity_levels:
            errors.append(f"brand_pack.json severity_levels missing '{level}'")

    return errors


def validate_dataset(dataset: dict, brand_pack: dict) -> list[str]:
    errors: list[str] = []
    cases = dataset.get("cases")
    if not isinstance(cases, list) or not cases:
        errors.append("evaluation_dataset.json has no 'cases' list (or it is empty).")
        return errors

    known_rule_ids = _collect_rule_ids(brand_pack)
    seen_ids: set[str] = set()
    required_case_fields = [
        "case_id", "category", "channel", "draft", "scenario_description",
        "expected_findings", "expected_status", "explanation",
    ]

    for i, case in enumerate(cases):
        prefix = f"cases[{i}]"
        if not isinstance(case, dict):
            errors.append(f"{prefix} is not an object.")
            continue

        for field_name in required_case_fields:
            if field_name not in case:
                errors.append(f"{prefix} (case_id={case.get('case_id', '?')}) missing field '{field_name}'")

        case_id = case.get("case_id")
        if case_id is None:
            errors.append(f"{prefix} has no case_id.")
        elif case_id in seen_ids:
            errors.append(f"Duplicate case_id: '{case_id}'")
        else:
            seen_ids.add(case_id)

        expected_status = case.get("expected_status")
        if expected_status not in ("compliant", "problematic"):
            errors.append(
                f"{prefix} (case_id={case_id}) has invalid expected_status "
                f"'{expected_status}' (must be 'compliant' or 'problematic')."
            )

        expected_findings = case.get("expected_findings", [])
        if expected_status == "compliant" and expected_findings:
            errors.append(
                f"{prefix} (case_id={case_id}) is marked compliant but has "
                f"non-empty expected_findings."
            )
        if expected_status == "problematic" and not expected_findings:
            errors.append(
                f"{prefix} (case_id={case_id}) is marked problematic but has "
                f"no expected_findings."
            )

        if isinstance(expected_findings, list):
            for j, finding in enumerate(expected_findings):
                if not isinstance(finding, dict):
                    errors.append(f"{prefix}.expected_findings[{j}] is not an object.")
                    continue
                rule_id = finding.get("rule_id")
                if rule_id and known_rule_ids and rule_id not in known_rule_ids:
                    errors.append(
                        f"{prefix} (case_id={case_id}) expected_findings[{j}] "
                        f"references unknown rule_id '{rule_id}' not found in brand_pack.json."
                    )
                if "issue_type" not in finding:
                    errors.append(
                        f"{prefix} (case_id={case_id}) expected_findings[{j}] missing 'issue_type'."
                    )
                if "severity" not in finding:
                    errors.append(
                        f"{prefix} (case_id={case_id}) expected_findings[{j}] missing 'severity'."
                    )

    return errors


def validate_answer_key(answer_key: dict, dataset: dict) -> list[str]:
    errors: list[str] = []
    answers = answer_key.get("answers")
    if not isinstance(answers, list):
        errors.append("answer_key.json has no 'answers' list.")
        return errors

    dataset_ids = {c.get("case_id") for c in dataset.get("cases", []) if isinstance(c, dict)}
    answer_ids = {a.get("case_id") for a in answers if isinstance(a, dict)}

    missing_in_answer_key = dataset_ids - answer_ids
    extra_in_answer_key = answer_ids - dataset_ids

    for case_id in sorted(filter(None, missing_in_answer_key)):
        errors.append(f"Dataset case '{case_id}' has no corresponding entry in answer_key.json.")

    for case_id in sorted(filter(None, extra_in_answer_key)):
        errors.append(f"answer_key.json has entry '{case_id}' with no matching dataset case.")

    return errors


def validate_all(data: LoadedData) -> list[str]:
    errors: list[str] = []
    errors.extend(validate_brand_pack(data.brand_pack))
    errors.extend(validate_dataset(data.dataset, data.brand_pack))
    errors.extend(validate_answer_key(data.answer_key, data.dataset))
    return errors


def category_counts(dataset: dict) -> dict[str, int]:
    counts: dict[str, int] = {}
    for case in dataset.get("cases", []):
        cat = case.get("category", "uncategorized")
        counts[cat] = counts.get(cat, 0) + 1
    return counts
