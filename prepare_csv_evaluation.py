
import csv
import json
from pathlib import Path

CSV_PATH = Path(r"C:\Users\asram\STruemark\data\truemark_mock_test_data.csv")
OUTPUT_DIR = Path("data") / "csv_1000"

CATEGORY_MAP = {
    "privacy_violation": "privacy_violation",
    "factual_inaccuracy": "factual_inaccuracy",
    "multiple_violations": "multiple_violations",
    "unsupported_claim": "unsupported_claim",
    "compliant": "compliant",
    "terminology_error": "terminology_error",
    "brand_voice_violation": "brand_voice_violation",
}

SEVERITY_MAP = {
    "critical": "critical",
    "high": "high",
    "medium": "medium",
    "low": "low",
}

def main():
    if not CSV_PATH.is_file():
        raise FileNotFoundError(f"CSV not found: {CSV_PATH}")

    with CSV_PATH.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))

    if len(rows) != 1000:
        raise ValueError(f"Expected 1000 rows; found {len(rows)}")

    cases = []
    answers = []
    seen_ids = set()

    for row in rows:
        case_id = f"CSV-{row['id'].strip()}"

        if case_id in seen_ids:
            raise ValueError(f"Duplicate case ID: {case_id}")
        seen_ids.add(case_id)

        category = row["scenario_type"].strip()
        status = row["expected_status"].strip()
        severity = row["severity_classification"].strip().lower()
        draft = row["input_text"].strip()

        if category not in CATEGORY_MAP:
            raise ValueError(f"Unknown scenario_type: {category}")
        if status not in ("compliant", "non_compliant"):
            raise ValueError(f"Unknown expected_status: {status}")
        if not draft:
            raise ValueError(f"Empty input_text for {case_id}")

        expected_status = (
            "compliant" if status == "compliant" else "problematic"
        )

        # Deliberately do not invent detailed findings or rule IDs.
        # The source CSV only supplies a primary violation category.
        findings = []
        if expected_status == "problematic":
            findings = [{
                "rule_id": "",
                "issue_type": category,
                "severity": SEVERITY_MAP.get(severity, "medium"),
                "text_span": "",
                "explanation": (
                    "Provisional category/severity mapped from the source CSV; "
                    "detailed finding and rule mapping require human review."
                ),
            }]

        cases.append({
            "case_id": case_id,
            "category": CATEGORY_MAP[category],
            "channel": "unspecified",
            "draft": draft,
            "scenario_description": (
                f"Source CSV scenario_type={category}; "
                f"contains_pii={row['contains_pii'].strip()}"
            ),
            "expected_findings": findings,
            "expected_status": expected_status,
            "explanation": (
                "Imported from the source CSV. Labels are provisional and "
                "have not been independently verified."
            ),
        })

        answers.append({
            "case_id": case_id,
            "expected_status": expected_status,
            "expected_findings": findings,
            "expected_rule_ids": [],
            "expected_issue_types": [category] if findings else [],
        })

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    dataset = {
        "_comment": (
            "Imported 1000-row CSV. Expected labels and findings are provisional; "
            "not independently verified ground truth."
        ),
        "schema_version": "1.0.0",
        "dataset_version": "csv-import-provisional-1.0",
        "cases": cases,
    }

    answer_key = {
        "_comment": (
            "Generated from source CSV labels, not independently reviewed."
        ),
        "schema_version": "1.0.0",
        "brand_id": "brightpath",
        "dataset_version": "csv-import-provisional-1.0",
        "answers": answers,
    }

    (OUTPUT_DIR / "evaluation_dataset.json").write_text(
        json.dumps(dataset, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (OUTPUT_DIR / "answer_key.json").write_text(
        json.dumps(answer_key, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"Source rows: {len(rows)}")
    print(f"Generated cases: {len(cases)}")
    print(f"Generated answer entries: {len(answers)}")
    print(f"Output folder: {OUTPUT_DIR.resolve()}")
    print("WARNING: findings and labels are provisional, not verified ground truth.")

if __name__ == "__main__":
    main()
