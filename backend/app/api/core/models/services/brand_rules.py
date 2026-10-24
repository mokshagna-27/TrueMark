import re
from typing import Any


UNPROFESSIONAL_PHRASES = {
    "buy now": "Use a more informative, brand-appropriate call to action.",
    "best ever": "Replace this unsupported superlative with a specific benefit.",
    "guaranteed": "Verify that this guarantee is authorized and can be substantiated.",
    "cheap": "Consider using 'affordable' or explaining the product's value.",
    "stuff": "Replace this vague word with a specific product or service name.",
    "guys": "Use a more inclusive audience greeting, such as 'everyone'.",
    "omg": "Replace informal slang with wording consistent with your brand voice.",
    "lol": "Remove casual internet slang if your brand uses a professional tone.",
    "!!!": "Use restrained punctuation to maintain a professional tone.",
    "???": "Use a single question mark where appropriate.",
}


def normalize_text(text: str) -> str:
    """Normalize whitespace for consistent comparison."""
    return re.sub(r"\s+", " ", text).strip()


def check_required_terms(
    text: str,
    required_terms: list[str],
) -> list[dict[str, Any]]:
    """Identify required brand terminology missing from content."""
    normalized_text = normalize_text(text).casefold()
    findings = []

    for term in required_terms:
        term = normalize_text(term)

        if not term:
            continue

        pattern = rf"(?<!\w){re.escape(term)}(?!\w)"

        if not re.search(pattern, normalized_text, flags=re.IGNORECASE):
            findings.append({
                "rule": "required_term",
                "severity": "medium",
                "message": f"Required brand term '{term}' is missing.",
                "suggestion": f"Consider including '{term}' where it fits naturally.",
                "matched": False,
            })

    return findings


def check_forbidden_terms(
    text: str,
    forbidden_terms: list[str],
) -> list[dict[str, Any]]:
    """Identify explicitly forbidden brand terminology."""
    normalized_text = normalize_text(text)
    findings = []

    for term in forbidden_terms:
        term = normalize_text(term)

        if not term:
            continue

        pattern = rf"(?<!\w){re.escape(term)}(?!\w)"

        if re.search(pattern, normalized_text, flags=re.IGNORECASE):
            findings.append({
                "rule": "forbidden_term",
                "severity": "high",
                "message": f"Forbidden brand term '{term}' was found.",
                "suggestion": f"Review and replace '{term}' with approved terminology.",
                "matched": True,
            })

    return findings


def check_brand_voice(text: str) -> list[dict[str, Any]]:
    """Flag wording that may conflict with a professional brand voice."""
    findings = []
    normalized_text = normalize_text(text)

    for phrase, suggestion in UNPROFESSIONAL_PHRASES.items():
        if phrase in {"!!!", "???"}:
            matched = phrase in normalized_text
        else:
            pattern = rf"(?<!\w){re.escape(phrase)}(?!\w)"
            matched = bool(
                re.search(pattern, normalized_text, flags=re.IGNORECASE)
            )

        if matched:
            findings.append({
                "rule": "brand_voice",
                "severity": "low",
                "message": f"Potential brand voice concern: '{phrase}'.",
                "suggestion": suggestion,
                "matched": True,
            })

    return findings


def check_repeated_punctuation(text: str) -> list[dict[str, Any]]:
    """Flag excessive repeated punctuation."""
    findings = []

    if re.search(r"[!?]{4,}", text):
        findings.append({
            "rule": "punctuation",
            "severity": "low",
            "message": "Excessive repeated punctuation was detected.",
            "suggestion": "Use one or two punctuation marks to improve readability.",
            "matched": True,
        })

    return findings


def analyze_brand_rules(
    text: str,
    required_terms: list[str] | None = None,
    forbidden_terms: list[str] | None = None,
) -> dict[str, Any]:
    """Run brand consistency checks and produce a structured report."""
    required_terms = required_terms or []
    forbidden_terms = forbidden_terms or []

    findings = [
        *check_required_terms(text, required_terms),
        *check_forbidden_terms(text, forbidden_terms),
        *check_brand_voice(text),
        *check_repeated_punctuation(text),
    ]

    high_count = sum(
        finding["severity"] == "high" for finding in findings
    )
    medium_count = sum(
        finding["severity"] == "medium" for finding in findings
    )
    low_count = sum(
        finding["severity"] == "low" for finding in findings
    )

    if high_count > 0:
        overall_status = "needs_review"
    elif medium_count > 0:
        overall_status = "needs_attention"
    else:
        overall_status = "passed"

    return {
        "checked_characters": len(text),
        "findings_count": len(findings),
        "high_severity_count": high_count,
        "medium_severity_count": medium_count,
        "low_severity_count": low_count,
        "overall_status": overall_status,
        "analysis_engine": "rule_based_brand_consistency",
        "findings": findings,
    }