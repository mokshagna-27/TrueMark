# TrueMark Evaluation — README

This directory implements the Data & Evaluation module's runtime: loading
and validating data, calling the AI analyzer, matching findings, computing
metrics, running error analysis, and generating reports.

## Scripts

| File | Purpose |
|---|---|
| `analyzer_adapter.py` | Defines the expected `analyze(draft, channel) -> dict` interface, normalizes analyzer output into `AnalyzerResult`/`Finding`, provides `RealAnalyzerAdapter` (imports the real analyzer by module path) and `MockAnalyzer` (deterministic stand-in for isolated unit tests only). |
| `data_loading.py` | Loads and structurally validates `brand_pack.json`, `evaluation_dataset.json`, and `answer_key.json`. |
| `matching.py` | One-to-one matching of predicted findings against expected findings, by `(rule_id, issue_type)`. |
| `metrics.py` | Precision / recall / F1 / case-level accuracy, with zero-denominator handling and category-level breakdown. Pure functions, no I/O. |
| `error_analysis.py` | Builds false-negative / false-positive / analyzer-failure lists from case results, ranked by severity. |
| `reporting.py` | Renders the JSON and Markdown evaluation reports from already-computed results. |
| `evaluate.py` | Main CLI: ties the above together end-to-end and writes reports to `evaluation/reports/`. |
| `validate_data.py` | Standalone CLI to validate data files without running any analyzer (fast pre-commit check). |
| `scaffold_answer_key.py` | One-time helper to generate `answer_key.json` from a dataset's own `expected_status`/`expected_findings` fields — useful when dropping in a large (e.g. 1000-case) dataset. |

## Prerequisites and dependencies

- Python 3.10+ (uses `from __future__ import annotations` and `X | Y` type
  unions).
- `pip install -r requirements.txt` (currently just `pytest`, for running
  the test suite — the evaluation scripts themselves have no third-party
  dependencies).
- No API keys are required for the evaluation module itself. If the real
  TrueMark analyzer needs API keys, that is configured on the analyzer's
  own side, not here.

## Running an evaluation

### Pipeline dry run (mock analyzer, no real evaluation)

```bash
python -m evaluation.evaluate --use-mock
```

This exercises the full pipeline (load → validate → match → metrics →
error analysis → reports) using `MockAnalyzer`, which returns `compliant`
for everything unless given canned responses in code. **This does not
produce real accuracy numbers** — it only confirms the pipeline and report
generation work. The generated report is explicitly labeled
`"analyzer_integrated": false` and carries a "pending" notice.

### Real evaluation (once the analyzer is integrated)

```bash
python -m evaluation.evaluate --analyzer-module <import.path.to.analyzer_module> [--analyzer-attr analyze]
```

Example, once the real analyzer's location is confirmed during repo
inspection:

```bash
python -m evaluation.evaluate --analyzer-module backend.ai_engine.analyzer
```

`--analyzer-module` must be an **importable Python module path** (not a
file path) that exposes a callable matching the `attr` name
(`--analyzer-attr`, default `analyze`) with signature `analyze(draft: str,
channel: str) -> dict`. If the module cannot be imported or the function
isn't found, the run reports every case as an analyzer failure and the
report is marked `"analyzer_integrated": false` — it will never silently
report fabricated metrics.

Useful flags:

- `--data-dir PATH` — point at a different data directory (default:
  `../data` relative to this file).
- `--reports-dir PATH` — where to write reports (default:
  `evaluation/reports/`).
- `--limit N` — evaluate only the first N cases; useful for a fast smoke
  test on a large (e.g. 1000-case) dataset before a full run.
- `--fail-on-validation-error` — exit non-zero immediately if
  `validate_data`-style checks fail, instead of continuing with a warning.

## Running tests

```bash
pip install -r requirements.txt
pytest tests/ -v
```

All ordinary unit tests use `MockAnalyzer` or controlled fixtures and
require no API keys or live AI calls. Tests that would call a real analyzer
live under `TestRealAnalyzerIntegration` and are skipped unless the
`TRUEMARK_REAL_ANALYZER_MODULE` environment variable is set:

```bash
TRUEMARK_REAL_ANALYZER_MODULE=backend.ai_engine.analyzer pytest tests/ -k RealAnalyzer
```

## The analyzer integration interface

Expected real-analyzer call:

```python
result = analyze(draft: str, channel: str) -> dict
```

Expected return shape:

```json
{
  "status": "compliant" | "problematic",
  "findings": [
    {
      "rule_id": "CLAIM-001",
      "issue_type": "absolute_claim",
      "severity": "high",
      "text_span": "guaranteed to help you sleep",
      "explanation": "..."
    }
  ]
}
```

`status` is optional — if omitted, it's derived as `"problematic"` when
`findings` is non-empty, else `"compliant"`. If the real analyzer's actual
signature or schema differs from this, **update only `analyzer_adapter.py`**
(not the real analyzer) and note the change here.

## Matching methodology

See the docstring at the top of `matching.py` for the authoritative
description. Summary: a predicted finding matches an expected finding when
they share the same `rule_id` **and** `issue_type`; matching is one-to-one
and order-stable; anything left over on either side becomes a false
negative (expected, unmatched) or false positive (predicted, unmatched).
Compliant cases (empty `expected_findings`) treat every predicted finding as
a false positive.

## What the metrics mean

- **Precision** = TP / (TP + FP) — of everything the analyzer flagged, how
  much was actually expected.
- **Recall** = TP / (TP + FN) — of everything that should have been
  flagged, how much the analyzer caught.
- **F1** = harmonic mean of precision and recall.
- **Case-level accuracy** = fraction of cases where the analyzer's overall
  `status` (`compliant`/`problematic`) matched the answer key's
  `expected_status`, over cases that didn't error out.
- All of the above are also broken down per `category`.
- Zero-denominator cases (e.g. no predicted findings at all) report `0.0`
  rather than raising.

## How reports are generated

`evaluate.py` always writes two files to `evaluation/reports/`:

- `evaluation_report.json` — machine-readable, includes
  `evaluation_date`, `dataset_version`, `analyzer_integrated`,
  `overall_metrics`, `category_metrics`, top missed detections, top false
  alarms, analyzer failures, recommendations, dataset limitations, and
  methodology.
- `evaluation_report.md` — the same content formatted as a human-readable
  Markdown report.

Reports are always regenerated from the actual run's results — nothing is
cached or hand-edited into them. If `analyzer_integrated` is `false`, the
Markdown report explicitly states that real evaluation is pending.

## Diagnosing missing files and schema mismatches

- `FileNotFoundError: Required data file not found: ...` — one of the four
  data files is missing from `--data-dir`. Check the path.
- `DataValidationError: Invalid JSON in ...` — the file isn't valid JSON;
  check for a trailing comma or unescaped quote.
- `evaluation_dataset.json has no 'cases' list` — the dataset file is
  missing its top-level `cases` array or it's empty.
- `Dataset case '...' has no corresponding entry in answer_key.json` — run
  `python -m evaluation.scaffold_answer_key` (see `data/README.md`) or add
  the entry manually.
- Every case reported as an analyzer failure with "not found" in the
  message — `--analyzer-module` is wrong, or the real analyzer isn't
  importable from this environment (check `PYTHONPATH`/working directory).
- `Analyzer 'findings' field is not a list.` / `non-dict output` — the real
  analyzer's return shape doesn't match the expected schema; update
  `analyzer_adapter.py`'s normalization logic to match reality and document
  the change in this README.

## Rerunning evaluations after analyzer updates

```bash
python -m evaluation.validate_data            # confirm data is still valid
python -m evaluation.evaluate --analyzer-module <path>   # full real run
```

Because matching and metrics are deterministic given the same inputs,
re-running after an analyzer change and diffing `evaluation_report.json`
(or comparing `top_missed_detections`/`top_false_alarms` between runs) is
the fastest way to confirm whether a detection-rule change actually
improved results.
