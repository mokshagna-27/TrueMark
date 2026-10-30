"""Analyzer pipeline exposed to the evaluation module."""
import json, os, re
from pathlib import Path
from .backend_rules import analyze_brand_rules
from .redaction import redact_pii
from .retrieval import load_sources, retrieve_relevant_sources
from .llm import analyze_with_llm

def _terms_from_brand_pack(data_dir):
    required, forbidden = [], []
    if not data_dir: return required, forbidden
    path = Path(data_dir) / "brand_pack.json"
    try: raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError): return required, forbidden
    def walk(obj):
        if isinstance(obj, dict):
            for key, value in obj.items():
                k = key.lower()
                if k in {"required_terms","approved_terms"} and isinstance(value,list):
                    required.extend(str(x) for x in value if isinstance(x,str))
                elif k in {"forbidden_terms","prohibited_terms","banned_terms"} and isinstance(value,list):
                    forbidden.extend(str(x) for x in value if isinstance(x,str))
                else: walk(value)
        elif isinstance(obj,list):
            for value in obj: walk(value)
    walk(raw)
    return list(dict.fromkeys(required)), list(dict.fromkeys(forbidden))

def analyze(draft, channel="unknown", required_terms=None, forbidden_terms=None):
    draft = draft if isinstance(draft,str) else str(draft or "")
    data_dir = os.getenv("TRUEMARK_DATA_DIR")
    required, forbidden = _terms_from_brand_pack(data_dir)
    # Caller-supplied terms (e.g. from the web app) extend any brand-pack terms.
    required = list(dict.fromkeys([*required, *(required_terms or [])]))
    forbidden = list(dict.fromkeys([*forbidden, *(forbidden_terms or [])]))
    redacted = redact_pii(draft)
    rule_result = analyze_brand_rules(draft, required, forbidden)
    findings = []
    for item in rule_result["findings"]:
        msg = item.get("message","")
        match = re.search(r"'([^']+)'", msg)
        span = ""
        if match:
            found = re.search(re.escape(match.group(1)), draft, re.I)
            if found: span = found.group(0)
        rule = item.get("rule","brand_voice")
        findings.append({"rule_id":"BACKEND-"+rule.upper(),
            "issue_type": (
                "privacy_violation" if rule.startswith("privacy")
                else "unsupported_claim" if rule == "unsupported_claim"
                else "terminology_error" if rule in {"required_term", "forbidden_term"}
                else "brand_voice_violation"
            ),
            "severity":item.get("severity","low"),"text_span":span,
            "explanation":msg + (" "+item.get("suggestion","") if item.get("suggestion") else ""),
            "recommendation":item.get("suggestion","")})
    sources = load_sources(data_dir) if data_dir else []
    relevant = retrieve_relevant_sources(redacted.redacted_text, sources)
    llm_state = "disabled"
    if os.getenv("TRUEMARK_LLM_API_KEY") and os.getenv("TRUEMARK_LLM_MODEL"):
        # Only redacted text is sent to the configured endpoint.
        try:
            model_result = analyze_with_llm(redacted.redacted_text, channel, relevant)
            llm_state = "used"
        except Exception as exc:  # LLM is optional: never lose the rule-based result.
            model_result = {"findings": []}
            llm_state = "error: " + str(exc)[:200]
        for item in model_result["findings"]:
            findings.append({"rule_id":str(item.get("rule_id") or "LLM-UNSPECIFIED"),
                "issue_type":str(item.get("issue_type") or "other"),
                "severity":str(item.get("severity") or "medium").lower(),
                "text_span":str(item.get("text_span") or ""),
                "explanation":str(item.get("explanation") or ""),
                "recommendation":str(item.get("recommendation") or "")})
    # Deduplicate exact repeats while preserving order.
    unique, seen = [], set()
    for item in findings:
        key = (item["rule_id"],item["issue_type"],item["text_span"],item["explanation"])
        if key not in seen: seen.add(key); unique.append(item)
    return {"status":"problematic" if unique else "compliant","findings":unique,
        "metadata":{"analyzer":"truemark_independent_pipeline","channel":channel,
          "rule_engine":rule_result["analysis_engine"],"llm_state":llm_state,
          "pii_detected":redacted.count>0,"pii_types":redacted.detected_types,
          "redacted_before_llm":True,"retrieved_sources":[s["title"] for s in relevant],
          "is_llm":llm_state=="used"}}
