"""
scaffold_answer_key.py

One-time helper for when you drop in a large real dataset (e.g. your
1000-case evaluation_dataset.json). It does NOT invent expected findings --
it only scaffolds an answer_key.json entry per case using whatever
expected_status / expected_findings are already present on each dataset
case, so you don't have to hand-type 1000 case_id entries.

If your dataset cases already carry correct expected_status/expected_findings
(as the schema in section 5/6 of the role prompt implies they should, since
the dataset and answer key must stay logically consistent), this produces a
ready-to-use answer_key.json. If a case is missing expected_status or
expected_findings, this script flags it instead of guessing.

This script does NOT overwrite an existing answer_key.json unless --force
is passed, and never silently invents findings not present in the dataset.

Usage:
    python -m evaluation.scaffold_answer_key --dataset data/evaluation_dataset.json --out data/answer_key.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
REPO_ROOT = THIS_DIR.parent
sys.path.insert(0, str(REPO_ROOT))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Scaffold answer_key.json from a dataset's own expected_* fields.")
    parser.add_argument("--dataset", default=str(REPO_ROOT / "data" / "evaluation_dataset.json"))
    parser.add_argument("--out", default=str(REPO_ROOT / "data" / "answer_key.json"))
    parser.add_argument("--brand-id", default="brightpath")
    parser.add_argument("--force", action="store_true", help="Overwrite an existing answer_key.json.")
    args = parser.parse_args(argv)

    dataset_path = Path(args.dataset)
    out_path = Path(args.out)

    if out_path.exists() and not args.force:
        print(f"ERROR: {out_path} already exists. Pass --force to overwrite.")
        return 2

    with dataset_path.open("r", encoding="utf-8") as f:
        dataset = json.load(f)

    cases = dataset.get("cases", [])
    if not cases:
        print("ERROR: dataset has no cases.")
        return 2

    answers = []
    incomplete_case_ids = []

    for case in cases:
        case_id = case.get("case_id")
        expected_status = case.get("expected_status")
        expected_findings = case.get("expected_findings")

        if case_id is None or expected_status is None or expected_findings is None:
            incomplete_case_ids.append(case_id or "<missing case_id>")
            continue

        answers.append({
            "case_id": case_id,
            "expected_status": expected_status,
            "expected_findings": expected_findings,
            "expected_rule_ids": [f.get("rule_id") for f in expected_findings if isinstance(f, dict)],
            "expected_issue_types": [f.get("issue_type") for f in expected_findings if isinstance(f, dict)],
        })

    answer_key = {
        "schema_version": "1.0.0",
        "brand_id": args.brand_id,
        "dataset_version": dataset.get("dataset_version", "unknown"),
        "answers": answers,
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(answer_key, f, indent=2)

    print(f"Wrote {len(answers)} answer_key entries to {out_path}.")
    if incomplete_case_ids:
        print(
            f"WARNING: {len(incomplete_case_ids)} case(s) were missing "
            f"expected_status/expected_findings and were skipped. You must "
            f"add these manually and independently of the analyzer: "
            f"{incomplete_case_ids[:20]}{'...' if len(incomplete_case_ids) > 20 else ''}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
