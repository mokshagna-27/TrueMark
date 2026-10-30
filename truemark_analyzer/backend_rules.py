"""Local rule-based checks for privacy, claims, and brand voice."""
import re
from typing import Any

UNPROFESSIONAL_PHRASES = {
    "buy now": "Use a more informative, brand-appropriate call to action.",
    "best ever": "Replace this unsupported superlative with a specific benefit.",
    "cheap": "Consider using 'affordable' or explaining the product's value.",
    "stuff": "Replace this vague word with a specific product or service name.",
    "guys": "Use a more inclusive audience greeting, such as 'everyone'.",
    "omg": "Replace informal slang with wording consistent with your brand voice.",
    "lol": "Remove casual internet slang if your brand uses a professional tone.",
    "!!!": "Use restrained punctuation to maintain a professional tone.",
    "???": "Use a single question mark where appropriate.",
}

PRIVACY_PATTERNS = [
    (
        r"\b(include|share|publish|post|send|expose|disclose|reveal|leak)"
        r"\b.{0,120}\b(student|customer|client|patient|employee|person|user)"
        r"\b.{0,100}\b(personal|private|sensitive|contact|phone|email|address|details|information|data)\b",
        "Potential disclosure of personal information about an identifiable person.",
    ),
    (
        r"\b(personal|private|sensitive)\s+(contact\s+)?"
        r"(details|information|data|records)\b.{0,100}\b"
        r"(public|publicly|public email|social media|website|post)\b",
        "Personal or sensitive information may be exposed publicly.",
    ),
    (
        r"\b(share|publish|post|email|send|expose|disclose|leak)\b"
        r".{0,100}\b(passwords?|social security numbers?|SSNs?|"
        r"bank account numbers?|credit card numbers?|medical records?)\b",
        "Potential disclosure of highly sensitive personal information.",
    ),
    (
        r"\b(public email|public website|public post|social media)\b"
        r".{0,100}\b(student|customer|client|patient|employee)\b"
        r".{0,100}\b(personal|private|contact|phone|email|address|details|information)\b",
        "A public channel may expose someone's personal information.",
    ),
]

UNSUPPORTED_CLAIM_PATTERNS = [
    (r"\bguaranteed\b", "A guarantee may require authorization and substantiation."),
    (r"\b100\s*%\s*(safe|effective|accurate|secure|risk[- ]free)\b",
     "An absolute performance or safety claim needs strong supporting evidence."),
    (r"\b(risk[- ]free|zero risk|no side effects)\b",
     "An absolute risk or side-effect claim requires substantiation."),
    (r"\b(cures?|prevents?)\s+(cancer|diabetes|depression|disease|illness)\b",
     "This health-related claim requires reliable evidence and appropriate review."),
    (r"\b(clinically proven|scientifically proven)\b",
     "The claim of proof should be supported by relevant evidence."),
    (r"\b(best ever|number one|#1)\b",
     "A superiority claim may need objective evidence."),
]

def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()

def analyze_brand_rules(text: str, required_terms=None, forbidden_terms=None) -> dict[str, Any]:
    required_terms, forbidden_terms = required_terms or [], forbidden_terms or []
    findings = []
    normalized = normalize_text(text)

    for term in required_terms:
        term = normalize_text(str(term))
        if term and not re.search(rf"(?<!\w){re.escape(term)}(?!\w)", normalized, re.I):
            findings.append({
                "rule": "required_term", "severity": "medium",
                "message": f"Required brand term '{term}' is missing.",
                "suggestion": f"Consider including '{term}' where it fits naturally.",
            })

    for term in forbidden_terms:
        term = normalize_text(str(term))
        if term and re.search(rf"(?<!\w){re.escape(term)}(?!\w)", normalized, re.I):
            findings.append({
                "rule": "forbidden_term", "severity": "high",
                "message": f"Forbidden brand term '{term}' was found.",
                "suggestion": f"Review and replace '{term}' with approved terminology.",
            })

    for pattern, explanation in PRIVACY_PATTERNS:
        match = re.search(pattern, normalized, re.I)
        if match:
            findings.append({
                "rule": "privacy_disclosure", "severity": "high",
                "message": explanation,
                "suggestion": "Remove personal details or use an approved, access-controlled channel.",
                "matched_text": match.group(0),
            })

    for pattern, explanation in UNSUPPORTED_CLAIM_PATTERNS:
        match = re.search(pattern, normalized, re.I)
        if match:
            findings.append({
                "rule": "unsupported_claim", "severity": "medium",
                "message": explanation,
                "suggestion": "Verify the claim against reliable evidence and approved product documentation.",
                "matched_text": match.group(0),
            })

    for phrase, suggestion in UNPROFESSIONAL_PHRASES.items():
        found = phrase in normalized if phrase in {"!!!", "???"} else bool(
            re.search(rf"(?<!\w){re.escape(phrase)}(?!\w)", normalized, re.I)
        )
        if found:
            findings.append({
                "rule": "brand_voice", "severity": "low",
                "message": f"Potential brand voice concern: '{phrase}'.",
                "suggestion": suggestion,
                "matched_text": phrase,
            })

    if re.search(r"[!?]{4,}", text):
        findings.append({
            "rule": "punctuation", "severity": "low",
            "message": "Excessive repeated punctuation was detected.",
            "suggestion": "Use one or two punctuation marks to improve readability.",
        })

    counts = {
        severity: sum(f["severity"] == severity for f in findings)
        for severity in ("high", "medium", "low")
    }
    return {
        "checked_characters": len(text),
        "findings_count": len(findings),
        "high_severity_count": counts["high"],
        "medium_severity_count": counts["medium"],
        "low_severity_count": counts["low"],
        "overall_status": "needs_review" if counts["high"] else (
            "needs_attention" if counts["medium"] else "passed"
        ),
        "analysis_engine": "rule_based_privacy_claim_brand_checks",
        "findings": findings,
    }
