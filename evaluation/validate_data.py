"""
validate_data.py

Standalone CLI to validate brand_pack.json, evaluation_dataset.json, and
answer_key.json without running any analyzer. Useful as a fast pre-commit
check, especially after swapping in a large (e.g. 1000-case) dataset.

Usage:
    python -m evaluation.validate_data
    python -m evaluation.validate_data --data-dir /path/to/data
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
REPO_ROOT = THIS_DIR.parent
sys.path.insert(0, str(REPO_ROOT))

from evaluation.data_loading import category_counts, load_all, validate_all  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate TrueMark Data & Evaluation data files.")
    parser.add_argument("--data-dir", default=str(REPO_ROOT / "data"))
    args = parser.parse_args(argv)

    data = load_all(args.data_dir)
    errors = validate_all(data)

    counts = category_counts(data.dataset)
    print("Category counts:")
    for category, count in sorted(counts.items()):
        print(f"  {category}: {count}")
    print(f"Total cases: {sum(counts.values())}")
    print()

    if errors:
        print(f"Found {len(errors)} validation issue(s):")
        for err in errors:
            print(f"  - {err}")
        return 1

    print("All data files are valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
