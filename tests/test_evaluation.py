"""
test_evaluation.py

Unit tests for the Data & Evaluation module. These tests do NOT require
API keys or live AI calls: the MockAnalyzer and controlled fixtures stand
in for the real TrueMark analyzer. Tests that would exercise the real
analyzer are clearly separated and skipped unless TRUEMARK_REAL_ANALYZER_MODULE
is set (see TestRealAnalyzerIntegration at the bottom).
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from evaluation.analyzer_adapter import (
    AnalyzerNotIntegratedError,
    Finding,
    MockAnalyzer,
    RealAnalyzerAdapter,
    build_adapter,
)
from evaluation.data_loading import (
    DataValidationError,
    category_counts,
    load_all,
    load_json,
    validate_all,
    validate_answer_key,
    validate_brand_pack,
    validate_dataset,
)
from evaluation.error_analysis import build_error_analysis
from evaluation.matching import match_findings
from evaluation.metrics import CaseOutcome, category_breakdown, precision_recall_f1, safe_divide, summarize
from evaluation.reporting import build_json_report, build_markdown_report


# ---------------------------------------------------------------------------
# Data loading / JSON validity
# ---------------------------------------------------------------------------

class TestDataLoading:
    def test_load_all_succeeds_on_valid_data(self, tmp_data_dir):
        data = load_all(tmp_data_dir)
        assert data.brand_pack["brand_id"] == "testbrand"
        assert len(data.dataset["cases"]) == 2
        assert len(data.answer_key["answers"]) == 2

    def test_load_json_missing_file_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            load_json(tmp_path / "does_not_exist.json")

    def test_load_json_malformed_raises_data_validation_error(self, tmp_path):
        bad_file = tmp_path / "bad.json"
        bad_file.write_text("{not valid json")
        with pytest.raises(DataValidationError):
            load_json(bad_file)


# ---------------------------------------------------------------------------
# Structural validation
# ---------------------------------------------------------------------------

class TestValidation:
    def test_valid_data_has_no_errors(self, minimal_brand_pack, minimal_dataset, minimal_answer_key):
        errors = validate_brand_pack(minimal_brand_pack)
        errors += validate_dataset(minimal_dataset, minimal_brand_pack)
        errors += validate_answer_key(minimal_answer_key, minimal_dataset)
        assert errors == []

    def test_duplicate_case_ids_detected(self, minimal_dataset, minimal_brand_pack):
        minimal_dataset["cases"].append(dict(minimal_dataset["cases"][0]))
        errors = validate_dataset(minimal_dataset, minimal_brand_pack)
        assert any("Duplicate case_id" in e for e in errors)

    def test_unknown_rule_id_detected(self, minimal_dataset, minimal_brand_pack):
        minimal_dataset["cases"][1]["expected_findings"][0]["rule_id"] = "NOT-A-REAL-RULE"
        errors = validate_dataset(minimal_dataset, minimal_brand_pack)
        assert any("unknown rule_id" in e for e in errors)

    def test_compliant_case_with_findings_detected(self, minimal_dataset, minimal_brand_pack):
        minimal_dataset["cases"][0]["expected_findings"] = [
            {"rule_id": "CLAIM-ABS-001", "issue_type": "absolute_claim", "severity": "high"}
        ]
        errors = validate_dataset(minimal_dataset, minimal_brand_pack)
        assert any("marked compliant but has" in e for e in errors)

    def test_problematic_case_without_findings_detected(self, minimal_dataset, minimal_brand_pack):
        minimal_dataset["cases"][1]["expected_findings"] = []
        errors = validate_dataset(minimal_dataset, minimal_brand_pack)
        assert any("marked problematic but has" in e for e in errors)

    def test_missing_answer_key_entry_detected(self, minimal_dataset, minimal_answer_key):
        minimal_answer_key["answers"].pop()
        errors = validate_answer_key(minimal_answer_key, minimal_dataset)
        assert any("has no corresponding entry in answer_key.json" in e for e in errors)

    def test_extra_answer_key_entry_detected(self, minimal_dataset, minimal_answer_key):
        minimal_answer_key["answers"].append({"case_id": "GHOST-999", "expected_status": "compliant", "expected_findings": []})
        errors = validate_answer_key(minimal_answer_key, minimal_dataset)
        assert any("GHOST-999" in e for e in errors)

    def test_empty_dataset_flagged(self, minimal_brand_pack):
        errors = validate_dataset({"cases": []}, minimal_brand_pack)
        assert errors and "empty" in errors[0]

    def test_required_dataset_categories_present_via_counts(self, minimal_dataset):
        counts = category_counts(minimal_dataset)
        assert counts == {"compliant": 1, "absolute_claims": 1}

    def test_missing_brand_pack_keys_detected(self):
        errors = validate_brand_pack({"schema_version": "1.0.0"})
        assert len(errors) > 1


# ---------------------------------------------------------------------------
# Finding matching
# ---------------------------------------------------------------------------

class TestMatching:
    def test_exact_match_is_true_positive(self):
        expected = [{"rule_id": "CLAIM-ABS-001", "issue_type": "absolute_claim", "severity": "high"}]
        predicted = [Finding(rule_id="CLAIM-ABS-001", issue_type="absolute_claim", severity="high")]
        result = match_findings("C1", expected, predicted)
        assert result.tp_count == 1
        assert result.fp_count == 0
        assert result.fn_count == 0

    def test_unmatched_expected_is_false_negative(self):
        expected = [{"rule_id": "CLAIM-ABS-001", "issue_type": "absolute_claim", "severity": "high"}]
        predicted: list[Finding] = []
        result = match_findings("C1", expected, predicted)
        assert result.fn_count == 1
        assert result.tp_count == 0

    def test_unmatched_predicted_is_false_positive(self):
        expected: list[dict] = []
        predicted = [Finding(rule_id="TERM-001", issue_type="prohibited_term", severity="medium")]
        result = match_findings("C1", expected, predicted)
        assert result.fp_count == 1
        assert result.tp_count == 0

    def test_matching_is_one_to_one_no_double_counting(self):
        expected = [
            {"rule_id": "CLAIM-ABS-001", "issue_type": "absolute_claim", "severity": "high"},
            {"rule_id": "CLAIM-ABS-001", "issue_type": "absolute_claim", "severity": "high"},
        ]
        predicted = [Finding(rule_id="CLAIM-ABS-001", issue_type="absolute_claim", severity="high")]
        result = match_findings("C1", expected, predicted)
        assert result.tp_count == 1
        assert result.fn_count == 1
        assert result.fp_count == 0

    def test_different_issue_type_does_not_match(self):
        expected = [{"rule_id": "CLAIM-ABS-001", "issue_type": "absolute_claim", "severity": "high"}]
        predicted = [Finding(rule_id="CLAIM-ABS-001", issue_type="different_type", severity="high")]
        result = match_findings("C1", expected, predicted)
        assert result.tp_count == 0
        assert result.fn_count == 1
        assert result.fp_count == 1

    def test_matching_is_stable_order(self):
        expected = [
            {"rule_id": "A", "issue_type": "x", "severity": "low"},
            {"rule_id": "B", "issue_type": "y", "severity": "low"},
        ]
        predicted = [
            Finding(rule_id="B", issue_type="y", severity="low"),
            Finding(rule_id="A", issue_type="x", severity="low"),
        ]
        result = match_findings("C1", expected, predicted)
        assert result.tp_count == 2
        assert result.fp_count == 0
        assert result.fn_count == 0


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------

class TestMetrics:
    def test_safe_divide_handles_zero_denominator(self):
        assert safe_divide(5, 0) == 0.0
        assert safe_divide(0, 0) == 0.0
        assert safe_divide(4, 2) == 2.0

    def test_precision_recall_f1_known_values(self):
        precision, recall, f1 = precision_recall_f1(tp=8, fp=2, fn=2)
        assert precision == 0.8
        assert recall == 0.8
        assert round(f1, 4) == 0.8

    def test_precision_recall_f1_all_zero(self):
        precision, recall, f1 = precision_recall_f1(tp=0, fp=0, fn=0)
        assert precision == 0.0
        assert recall == 0.0
        assert f1 == 0.0

    def test_summarize_basic(self):
        outcomes = [
            CaseOutcome("C1", "cat_a", "compliant", "compliant", tp=0, fp=0, fn=0),
            CaseOutcome("C2", "cat_a", "problematic", "problematic", tp=1, fp=0, fn=0),
            CaseOutcome("C3", "cat_b", "problematic", "compliant", tp=0, fp=0, fn=1),
        ]
        summary = summarize(outcomes)
        assert summary.total_cases == 3
        assert summary.true_positives == 1
        assert summary.false_negatives == 1
        assert summary.case_level_accuracy == round(2 / 3, 4)

    def test_summarize_excludes_failed_cases_from_accuracy(self):
        outcomes = [
            CaseOutcome("C1", "cat_a", "compliant", "error", tp=0, fp=0, fn=0, analyzer_error=True),
            CaseOutcome("C2", "cat_a", "compliant", "compliant", tp=0, fp=0, fn=0),
        ]
        summary = summarize(outcomes)
        assert summary.failed_cases == 1
        assert summary.completed_cases == 1
        assert summary.case_level_accuracy == 1.0

    def test_category_breakdown_groups_correctly(self):
        outcomes = [
            CaseOutcome("C1", "cat_a", "compliant", "compliant", tp=0, fp=0, fn=0),
            CaseOutcome("C2", "cat_b", "problematic", "problematic", tp=1, fp=0, fn=0),
        ]
        breakdown = category_breakdown(outcomes)
        assert set(breakdown.keys()) == {"cat_a", "cat_b"}
        assert breakdown["cat_b"].true_positives == 1

    def test_empty_outcomes_do_not_crash(self):
        summary = summarize([])
        assert summary.total_cases == 0
        assert summary.precision == 0.0
        assert summary.case_level_accuracy == 0.0


# ---------------------------------------------------------------------------
# Error analysis
# ---------------------------------------------------------------------------

class TestErrorAnalysis:
    def test_build_error_analysis_separates_categories(self):
        records = [
            {
                "case_id": "C1", "category": "cat_a", "channel": "web", "draft": "d1",
                "analyzer_error": None,
                "false_negatives": [{"rule_id": "R1", "issue_type": "t1", "severity": "critical", "text_span": "x", "explanation": "e"}],
                "false_positives": [],
            },
            {
                "case_id": "C2", "category": "cat_a", "channel": "web", "draft": "d2",
                "analyzer_error": None,
                "false_negatives": [],
                "false_positives": [{"rule_id": "R2", "issue_type": "t2", "severity": "low", "text_span": "y", "explanation": "e2"}],
            },
            {
                "case_id": "C3", "category": "cat_b", "channel": "web", "draft": "d3",
                "analyzer_error": "boom",
            },
        ]
        report = build_error_analysis(records)
        assert len(report.false_negatives) == 1
        assert len(report.false_positives) == 1
        assert len(report.analyzer_failures) == 1
        assert report.analyzer_failures[0].error_message == "boom"

    def test_top_missed_detections_sorted_by_severity(self):
        records = [
            {"case_id": "A", "category": "c", "channel": "w", "draft": "d", "analyzer_error": None,
             "false_negatives": [{"rule_id": "R", "issue_type": "t", "severity": "low", "text_span": "", "explanation": ""}],
             "false_positives": []},
            {"case_id": "B", "category": "c", "channel": "w", "draft": "d", "analyzer_error": None,
             "false_negatives": [{"rule_id": "R", "issue_type": "t", "severity": "critical", "text_span": "", "explanation": ""}],
             "false_positives": []},
        ]
        report = build_error_analysis(records)
        top = report.top_missed_detections()
        assert top[0].case_id == "B"  # critical before low


# ---------------------------------------------------------------------------
# Analyzer adapter
# ---------------------------------------------------------------------------

class TestAnalyzerAdapter:
    def test_mock_analyzer_canned_response(self):
        mock = MockAnalyzer()
        mock.set_response("bad draft", {"status": "problematic", "findings": [
            {"rule_id": "TERM-001", "issue_type": "prohibited_term", "severity": "medium"}
        ]})
        result = mock.run("bad draft", "website_copy")
        assert result.status == "problematic"
        assert len(result.findings) == 1
        assert result.findings[0].rule_id == "TERM-001"

    def test_mock_analyzer_default_is_compliant(self):
        mock = MockAnalyzer()
        result = mock.run("unseen draft", "website_copy")
        assert result.status == "compliant"
        assert result.findings == []

    def test_normalize_handles_non_dict_output(self):
        mock = MockAnalyzer()
        mock.set_response("weird", ["not", "a", "dict"])  # type: ignore[arg-type]
        result = mock.run("weird", "web")
        assert not result.ok
        assert "non-dict" in result.error

    def test_normalize_handles_bad_findings_field(self):
        mock = MockAnalyzer()
        mock.set_response("weird2", {"status": "problematic", "findings": "not-a-list"})
        result = mock.run("weird2", "web")
        assert not result.ok

    def test_normalize_derives_status_when_missing(self):
        mock = MockAnalyzer()
        mock.set_response("derive", {"findings": [{"rule_id": "R", "issue_type": "t", "severity": "low"}]})
        result = mock.run("derive", "web")
        assert result.status == "problematic"

    def test_real_analyzer_adapter_raises_when_module_missing(self):
        adapter = RealAnalyzerAdapter(module_path="definitely_not_a_real_module_xyz")
        with pytest.raises(AnalyzerNotIntegratedError):
            adapter.run("draft", "web")

    def test_build_adapter_requires_module_path_for_real(self):
        with pytest.raises(ValueError):
            build_adapter(use_mock=False, module_path="")

    def test_analyzer_exception_becomes_error_result(self):
        class ExplodingAnalyzer(MockAnalyzer):
            def _call(self, draft, channel):
                raise RuntimeError("analyzer crashed")

        result = ExplodingAnalyzer().run("draft", "web")
        assert not result.ok
        assert "analyzer crashed" in result.error


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

class TestReporting:
    def test_build_json_report_shape(self):
        from evaluation.error_analysis import ErrorAnalysisReport

        outcomes = [CaseOutcome("C1", "cat_a", "compliant", "compliant", tp=0, fp=0, fn=0)]
        overall = summarize(outcomes)
        by_category = category_breakdown(outcomes)
        report = build_json_report(
            dataset_version="v1", analyzer_integrated=True, overall=overall,
            by_category=by_category, error_report=ErrorAnalysisReport(),
            recommendations=["ok"], dataset_limitations=["none"], methodology="m",
        )
        assert report["dataset_version"] == "v1"
        assert "overall_metrics" in report
        assert "category_metrics" in report

    def test_build_markdown_report_contains_key_sections(self):
        from evaluation.error_analysis import ErrorAnalysisReport

        outcomes = [CaseOutcome("C1", "cat_a", "compliant", "compliant", tp=0, fp=0, fn=0)]
        overall = summarize(outcomes)
        by_category = category_breakdown(outcomes)
        json_report = build_json_report(
            dataset_version="v1", analyzer_integrated=False, overall=overall,
            by_category=by_category, error_report=ErrorAnalysisReport(),
            recommendations=["ok"], dataset_limitations=["none"], methodology="m",
        )
        markdown = build_markdown_report(json_report)
        assert "# TrueMark Evaluation Report" in markdown
        assert "Important Missed Detections" in markdown
        assert "pending" in markdown.lower()


# ---------------------------------------------------------------------------
# End-to-end pipeline (mocked analyzer only)
# ---------------------------------------------------------------------------

class TestEndToEndPipelineWithMock:
    """Exercises evaluate.run() against controlled fixtures with MockAnalyzer.
    This validates the pipeline, NOT real analyzer accuracy."""

    def test_full_pipeline_runs_and_produces_reports(self, tmp_data_dir, tmp_path, monkeypatch):
        from evaluation import evaluate

        reports_dir = tmp_path / "reports"
        args = evaluate.parse_args([
            "--data-dir", str(tmp_data_dir),
            "--reports-dir", str(reports_dir),
            "--use-mock",
        ])
        exit_code = evaluate.run(args)
        assert exit_code == 0
        assert (reports_dir / "evaluation_report.json").exists()
        assert (reports_dir / "evaluation_report.md").exists()

        report_data = json.loads((reports_dir / "evaluation_report.json").read_text())
        assert report_data["overall_metrics"]["total_cases"] == 2

    def test_pipeline_reports_pending_when_no_analyzer_given(self, tmp_data_dir, tmp_path):
        from evaluation import evaluate

        reports_dir = tmp_path / "reports2"
        args = evaluate.parse_args([
            "--data-dir", str(tmp_data_dir),
            "--reports-dir", str(reports_dir),
        ])
        exit_code = evaluate.run(args)
        assert exit_code == 2  # no analyzer specified at all

    def test_pipeline_validation_failure_can_stop_run(self, tmp_data_dir, tmp_path):
        from evaluation import evaluate

        # Corrupt the dataset to trigger a validation error.
        dataset_path = tmp_data_dir / "evaluation_dataset.json"
        dataset = json.loads(dataset_path.read_text())
        dataset["cases"][0]["case_id"] = dataset["cases"][1]["case_id"]  # duplicate id
        dataset_path.write_text(json.dumps(dataset))

        reports_dir = tmp_path / "reports3"
        args = evaluate.parse_args([
            "--data-dir", str(tmp_data_dir),
            "--reports-dir", str(reports_dir),
            "--use-mock",
            "--fail-on-validation-error",
        ])
        exit_code = evaluate.run(args)
        assert exit_code == 2


# ---------------------------------------------------------------------------
# Real analyzer integration (skipped unless explicitly configured)
# ---------------------------------------------------------------------------

class TestRealAnalyzerIntegration:
    """
    These tests call the REAL TrueMark analyzer and are skipped by default.
    To run them, set TRUEMARK_REAL_ANALYZER_MODULE to the real analyzer's
    import path before running pytest, e.g.:

        TRUEMARK_REAL_ANALYZER_MODULE=backend.ai_engine.analyzer pytest tests/ -k RealAnalyzer
    """

    @pytest.mark.skipif(
        not os.environ.get("TRUEMARK_REAL_ANALYZER_MODULE"),
        reason="Real analyzer not configured; set TRUEMARK_REAL_ANALYZER_MODULE to run this test.",
    )
    def test_real_analyzer_smoke(self):
        module_path = os.environ["TRUEMARK_REAL_ANALYZER_MODULE"]
        adapter = RealAnalyzerAdapter(module_path=module_path)
        result = adapter.run("This product is guaranteed to work.", "website_copy")
        assert result.ok
