"""Local source loader and simple lexical retrieval."""
import json, re
from pathlib import Path

def load_sources(data_dir):
    base = Path(data_dir)
    sources = []
    registry = base / "source_registry.json"
    if registry.exists():
        try:
            raw = json.loads(registry.read_text(encoding="utf-8"))
            items = raw if isinstance(raw, list) else raw.get("sources", []) if isinstance(raw, dict) else []
            for item in items:
                if not isinstance(item, dict):
                    continue
                title = str(item.get("title") or item.get("name") or item.get("id") or "Registered source")
                content = str(item.get("content") or item.get("text") or item.get("summary") or "")
                if content:
                    sources.append({"title":title,"content":content})
                else:
                    rel = item.get("path") or item.get("file")
                    if rel:
                        p = (base / str(rel)).resolve()
                        if base.resolve() in p.parents and p.is_file() and p.suffix.lower() in {".txt",".md"}:
                            sources.append({"title":title,"content":p.read_text(encoding="utf-8")})
        except (OSError, json.JSONDecodeError):
            pass
    for p in list(base.glob("*.md")) + list(base.glob("*.txt")):
        if p.name.lower() != "readme.md":
            try: sources.append({"title":p.name,"content":p.read_text(encoding="utf-8")})
            except OSError: pass
    return sources

def retrieve_relevant_sources(query, sources, limit=4):
    terms = set(re.findall(r"[A-Za-z0-9_-]{3,}", query.lower()))
    scored = []
    for source in sources:
        haystack = (source.get("title","") + " " + source.get("content","")).lower()
        score = sum(term in haystack for term in terms)
        if score:
            scored.append((score, source))
    scored.sort(key=lambda x:x[0], reverse=True)
    return [{"title":s["title"],"content":s.get("content","")[:3000],"overlap_score":score}
            for score,s in scored[:limit]]
