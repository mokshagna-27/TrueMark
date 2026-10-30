"""Heuristic masking for common PII patterns."""
import re
from dataclasses import dataclass, field

PATTERNS = [
    ("email", re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)),
    ("phone", re.compile(r"(?<!\w)(?:\+?\d{1,3}[- .]?)?(?:\(?\d{3}\)?[- .]?)\d{3}[- .]?\d{4}(?!\w)")),
    ("ssn_like", re.compile(r"\b\d{3}-\d{2}-\d{4}\b")),
    ("credential", re.compile(r"(?i)\b(?:password|passcode|api[_ -]?key|access[_ -]?token)\s*[:=]\s*\S+")),
]
@dataclass
class RedactionResult:
    redacted_text: str
    detected_types: list[str] = field(default_factory=list)
    count: int = 0

def redact_pii(text: str) -> RedactionResult:
    output, found, count = text, [], 0
    for kind, pattern in PATTERNS:
        def replace(match):
            nonlocal count
            count += 1
            found.append(kind)
            return f"[REDACTED_{kind.upper()}]"
        output = pattern.sub(replace, output)
    return RedactionResult(output, sorted(set(found)), count)
