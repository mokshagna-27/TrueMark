"""Bridge between the web API and the standalone ``truemark_analyzer`` pipeline.

The pipeline (privacy, unsupported-claim and brand-voice rules, PII redaction,
optional source retrieval and optional LLM review) lives in the repository root.
This module runs it and converts its findings into the report shape the
frontend and file-verification endpoint already consume.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

# backend/app/api/core/models/services/ -> repository root is parents[6]
_REPO_ROOT = Path(__file__).resolve().parents[6]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from truemark_analyzer.pipeline import analyze as run_pipeline  # noqa: E402

_SEVERITY_MAP = {"critical": "high", "high": "high", "medium": "medium", "low": "low"}


def _rule_name(rule_id: str, issue_type: str) -> str:
    if rule_id.startswith("BACKEND-"):
        return rule_id[len("BACKEND-"):].lower()
    if rule_id.startswith("LLM-") or rule_id == "LLM-UNSPECIFIED":
        return f"ai_review_{issue_type}"
    return rule_id.lower()


def analyze_content(
    text: str,
    required_terms: list[str] | None = None,
    forbidden_terms: list[str] | None = None,
    channel: str = "web",
) -> dict[str, Any]:
    """Analyze ``text`` and return a frontend-compatible report."""
    raw = run_pipeline(
        text,
        channel,
        required_terms=required_terms,
        forbidden_terms=forbidden_terms,
    )
    meta = raw["metadata"]

    findings: list[dict[str, Any]] = []
    for item in raw["findings"]:
        # The pipeline appends the recommendation to the explanation; undo that
        # so the UI doesn't show the same sentence twice.
        explanation = item["explanation"]
        recommendation = item.get("recommendation") or ""
        if recommendation and explanation.endswith(" " + recommendation):
            explanation = explanation[: -len(recommendation) - 1]
        findings.append({
            "rule": _rule_name(item["rule_id"], item["issue_type"]),
            "severity": _SEVERITY_MAP.get(str(item["severity"]).lower(), "low"),
            "message": explanation,
            "suggestion": item.get("recommendation") or "Review this content manually.",
            "matched": True,
            "matched_text": item.get("text_span", ""),
            "issue_type": item["issue_type"],
            "source": "rules" if item["rule_id"].startswith("BACKEND-") else "ai",
        })

    # Surface detected personal data in the draft itself (informational).
    if meta.get("pii_detected"):
        findings.append({
            "rule": "pii_in_content",
            "severity": "low",
            "message": "Possible personal data detected in the content: "
                       + ", ".join(meta.get("pii_types", [])) + ".",
            "suggestion": "Confirm this contact or personal detail is meant to be public.",
            "matched": True,
            "matched_text": "",
            "issue_type": "privacy_violation",
            "source": "rules",
        })

    counts = {s: sum(f["severity"] == s for f in findings) for s in ("high", "medium", "low")}
    status = "needs_review" if counts["high"] else "needs_attention" if counts["medium"] else "passed"
    llm_state = meta.get("llm_state", "disabled")
    engine = (
        "rule_based_with_ai_review" if llm_state == "used"
        else "rule_based_privacy_claim_brand_checks"
    )
    return {
        "checked_characters": len(text),
        "findings_count": len(findings),
        "high_severity_count": counts["high"],
        "medium_severity_count": counts["medium"],
        "low_severity_count": counts["low"],
        "overall_status": status,
        "analysis_engine": engine,
        "llm_state": llm_state,
        "pii_detected": bool(meta.get("pii_detected")),
        "retrieved_sources": meta.get("retrieved_sources", []),
        "findings": findings,
    }
