"""
analyzer_adapter.py

Defines the integration boundary between the Data & Evaluation module and
TrueMark's real AI engine (owned by the AI and Language Lead).

IMPORTANT: This module does NOT invent or fake the real analyzer. It defines
the *expected* interface and finding schema documented in the role prompt,
provides a clearly-labeled MockAnalyzer for isolated unit tests, and a
RealAnalyzerAdapter that will only run if the real analyzer module is found
and actually importable. If it is not available, RealAnalyzerAdapter raises
AnalyzerNotIntegratedError with a clear message instead of silently
fabricating results.

Expected real-analyzer interface (to be confirmed against the actual
repository during inspection):

    analyze(draft: str, channel: str) -> dict

Expected return schema (AnalyzerResult, see below). If the real analyzer's
actual signature or schema differs, update ONLY this adapter file (not the
real analyzer) and document the change in evaluation/README.md.
"""

from __future__ import annotations

import importlib
import importlib.util
from dataclasses import dataclass, field
from typing import Any, Optional, Protocol


class AnalyzerNotIntegratedError(RuntimeError):
    """Raised when the real TrueMark analyzer cannot be located or imported."""


@dataclass
class Finding:
    rule_id: str
    issue_type: str
    severity: str
    text_span: str = ""
    explanation: str = ""

    @staticmethod
    def from_dict(d: dict) -> "Finding":
        return Finding(
            rule_id=str(d.get("rule_id", "")),
            issue_type=str(d.get("issue_type", "")),
            severity=str(d.get("severity", "")),
            text_span=str(d.get("text_span", d.get("span", ""))),
            explanation=str(d.get("explanation", "")),
        )


@dataclass
class AnalyzerResult:
    """Normalized shape the rest of the evaluation module relies on."""
    status: str  # "compliant" | "problematic" | "error"
    findings: list[Finding] = field(default_factory=list)
    raw: Optional[dict] = None
    error: Optional[str] = None

    @property
    def ok(self) -> bool:
        return self.error is None


class SupportsAnalyze(Protocol):
    def analyze(self, draft: str, channel: str) -> dict: ...


class BaseAnalyzerAdapter:
    """Common normalization logic shared by real and mock adapters."""

    def run(self, draft: str, channel: str) -> AnalyzerResult:
        try:
            raw = self._call(draft, channel)
        except AnalyzerNotIntegratedError:
            # Integration-missing is a distinct, fail-fast condition (the real
            # analyzer module/attr could not be found at all) -- it must
            # propagate so callers can tell "not integrated" apart from a
            # per-case analyzer runtime error.
            raise
        except Exception as exc:  # noqa: BLE001 - capture any per-case analyzer failure
            return AnalyzerResult(status="error", findings=[], raw=None, error=str(exc))
        return self._normalize(raw)

    def _call(self, draft: str, channel: str) -> dict:
        raise NotImplementedError

    @staticmethod
    def _normalize(raw: dict) -> AnalyzerResult:
        if not isinstance(raw, dict):
            return AnalyzerResult(
                status="error", findings=[], raw=None,
                error=f"Analyzer returned non-dict output: {type(raw)!r}",
            )

        findings_raw = raw.get("findings", [])
        if not isinstance(findings_raw, list):
            return AnalyzerResult(
                status="error", findings=[], raw=raw,
                error="Analyzer 'findings' field is not a list.",
            )

        findings = [Finding.from_dict(f) for f in findings_raw]

        status = raw.get("status")
        if status not in ("compliant", "problematic"):
            # Derive status if the real analyzer doesn't supply one explicitly.
            status = "problematic" if findings else "compliant"

        return AnalyzerResult(status=status, findings=findings, raw=raw, error=None)


class RealAnalyzerAdapter(BaseAnalyzerAdapter):
    """
    Attempts to import and call the real TrueMark analyzer.

    Configure `module_path` and `attr_path` to match wherever the AI and
    Language Lead's analyzer actually lives once confirmed during repo
    inspection (e.g. "backend.ai_engine.analyzer", "analyze").

    This class intentionally does NOT fall back to mock behavior: if the
    real analyzer cannot be found, every call raises
    AnalyzerNotIntegratedError so evaluation runs can never silently use
    fake results.
    """

    def __init__(self, module_path: str, attr_path: str = "analyze"):
        self.module_path = module_path
        self.attr_path = attr_path
        self._fn = None

    def _resolve(self):
        if self._fn is not None:
            return self._fn
        spec = importlib.util.find_spec(self.module_path)
        if spec is None:
            raise AnalyzerNotIntegratedError(
                f"Real analyzer module '{self.module_path}' was not found. "
                f"Real evaluation is pending integration with the AI and "
                f"Language Lead's component. Update RealAnalyzerAdapter's "
                f"module_path/attr_path once the analyzer module and its "
                f"import path are confirmed."
            )
        module = importlib.import_module(self.module_path)
        fn = getattr(module, self.attr_path, None)
        if fn is None or not callable(fn):
            raise AnalyzerNotIntegratedError(
                f"Module '{self.module_path}' has no callable "
                f"'{self.attr_path}(draft, channel)'. Confirm the real "
                f"analyzer interface and update RealAnalyzerAdapter."
            )
        self._fn = fn
        return fn

    def _call(self, draft: str, channel: str) -> dict:
        fn = self._resolve()
        return fn(draft, channel)


class MockAnalyzer(BaseAnalyzerAdapter):
    """
    Deterministic, keyword-based stand-in analyzer used ONLY for isolated
    unit tests of the evaluation pipeline (matching, metrics, reporting).

    This is NOT a substitute for real evaluation and must never be used to
    produce or report real accuracy numbers. Tests that use this must be
    clearly labeled as unit tests of the pipeline, not analyzer evaluation.
    """

    def __init__(self, canned_responses: Optional[dict[str, dict]] = None):
        # canned_responses: {case_id_or_draft: raw_response_dict}
        self.canned_responses = canned_responses or {}

    def set_response(self, key: str, raw_response: dict) -> None:
        self.canned_responses[key] = raw_response

    def _call(self, draft: str, channel: str) -> dict:
        if draft in self.canned_responses:
            return self.canned_responses[draft]
        # Trivial deterministic fallback: flag nothing.
        return {"status": "compliant", "findings": []}


def build_adapter(use_mock: bool, module_path: str = "", attr_path: str = "analyze"):
    """Factory used by evaluate.py / tests to pick the right adapter."""
    if use_mock:
        return MockAnalyzer()
    if not module_path:
        raise ValueError("module_path is required when use_mock=False")
    return RealAnalyzerAdapter(module_path=module_path, attr_path=attr_path)
