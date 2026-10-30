from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

# Run the real-analyzer smoke test against the bundled pipeline by default.
os.environ.setdefault("TRUEMARK_REAL_ANALYZER_MODULE", "truemark_analyzer.pipeline")


@pytest.fixture
def minimal_brand_pack() -> dict:
    return {
        "schema_version": "1.0.0",
        "brand_id": "testbrand",
        "brand_identity": {},
        "approved_terminology": {
            "prohibited_terms": [
                {"term": "cure", "rule_id": "TERM-001"},
            ]
        },
        "claims_policy": {
            "absolute_claims": {"rule_id": "CLAIM-ABS-001"},
        },
        "verified_brand_facts": [],
        "channel_guidance": {},
        "readability_requirements": {"rule_id": "READ-001"},
        "privacy_guidelines": {"rule_id": "PRIV-001"},
        "severity_levels": {"critical": "x", "high": "x", "medium": "x", "low": "x"},
    }


@pytest.fixture
def minimal_dataset() -> dict:
    return {
        "schema_version": "1.0.0",
        "dataset_version": "test-0.0.1",
        "cases": [
            {
                "case_id": "T-001",
                "category": "compliant",
                "channel": "website_copy",
                "draft": "Plain compliant copy.",
                "scenario_description": "desc",
                "expected_findings": [],
                "expected_status": "compliant",
                "explanation": "No issues.",
            },
            {
                "case_id": "T-002",
                "category": "absolute_claims",
                "channel": "advertising_copy",
                "draft": "This is guaranteed to work.",
                "scenario_description": "desc",
                "expected_findings": [
                    {
                        "rule_id": "CLAIM-ABS-001",
                        "issue_type": "absolute_claim",
                        "severity": "high",
                        "text_span": "guaranteed to work",
                        "explanation": "Absolute claim.",
                    }
                ],
                "expected_status": "problematic",
                "explanation": "Flagged.",
            },
        ],
    }


@pytest.fixture
def minimal_answer_key(minimal_dataset) -> dict:
    answers = []
    for case in minimal_dataset["cases"]:
        answers.append({
            "case_id": case["case_id"],
            "expected_status": case["expected_status"],
            "expected_findings": case["expected_findings"],
            "expected_rule_ids": [f["rule_id"] for f in case["expected_findings"]],
            "expected_issue_types": [f["issue_type"] for f in case["expected_findings"]],
        })
    return {
        "schema_version": "1.0.0",
        "brand_id": "testbrand",
        "dataset_version": "test-0.0.1",
        "answers": answers,
    }


@pytest.fixture
def minimal_source_registry() -> dict:
    return {"schema_version": "1.0.0", "brand_id": "testbrand", "sources": []}


@pytest.fixture
def tmp_data_dir(tmp_path, minimal_brand_pack, minimal_dataset, minimal_answer_key, minimal_source_registry) -> Path:
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "brand_pack.json").write_text(json.dumps(minimal_brand_pack))
    (data_dir / "evaluation_dataset.json").write_text(json.dumps(minimal_dataset))
    (data_dir / "answer_key.json").write_text(json.dumps(minimal_answer_key))
    (data_dir / "source_registry.json").write_text(json.dumps(minimal_source_registry))
    return data_dir
