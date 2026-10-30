"""Optional OpenAI-compatible chat-completions integration (stdlib only)."""
import json, os, urllib.error, urllib.request

class LLMNotConfigured(RuntimeError): pass

def analyze_with_llm(draft, channel, sources=None):
    base = os.getenv("TRUEMARK_LLM_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    key, model = os.getenv("TRUEMARK_LLM_API_KEY"), os.getenv("TRUEMARK_LLM_MODEL")
    if not key or not model:
        raise LLMNotConfigured("Set TRUEMARK_LLM_API_KEY and TRUEMARK_LLM_MODEL.")
    source_text = "\n\n".join(f"[{s.get('title','Source')}]\n{s.get('content','')}" for s in (sources or []))
    system = """Act as a cautious brand compliance reviewer. Use only supplied sources for factual substantiation.
Return only JSON: {"status":"compliant"|"problematic","findings":[{"rule_id":"...","issue_type":"privacy_violation|unsupported_claim|factual_inaccuracy|terminology_error|brand_voice_violation|readability|other","severity":"low|medium|high|critical","text_span":"exact text span","explanation":"reason","recommendation":"fix"}]}.
Do not invent sources. Missing evidence means unverified, not necessarily false."""
    payload = json.dumps({"model":model,"temperature":0,
      "messages":[{"role":"system","content":system},
                  {"role":"user","content":f"Channel: {channel}\nDraft:\n{draft}\n\nApproved source excerpts:\n{source_text or '[No approved sources found.]'}"}],
      "response_format":{"type":"json_object"}}).encode()
    req = urllib.request.Request(base+"/chat/completions", data=payload, method="POST",
        headers={"Authorization":"Bearer "+key,"Content-Type":"application/json"})
    try:
        with urllib.request.urlopen(req, timeout=45) as response:
            data = json.loads(response.read().decode())
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"LLM endpoint HTTP {exc.code}: {exc.read().decode(errors='replace')[:300]}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"LLM endpoint unavailable: {exc.reason}") from exc
    parsed = json.loads(data["choices"][0]["message"]["content"])
    if parsed.get("status") not in {"compliant","problematic"} or not isinstance(parsed.get("findings"),list):
        raise ValueError("LLM response did not match required JSON schema.")
    return parsed
