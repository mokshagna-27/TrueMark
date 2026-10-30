"""End-to-end tests for the FastAPI web backend."""
import io
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient  # noqa: E402

from main import app  # noqa: E402


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200 and r.json()["status"] == "healthy"


def test_text_analysis_rules_and_terms(client):
    r = client.post("/api/v1/analysis/text", json={
        "text": "OMG!!! Our cheap products are the best ever! Guaranteed results.",
        "required_terms": ["TrueMark"],
        "forbidden_terms": ["cheap"],
    })
    assert r.status_code == 200
    result = r.json()["result"]
    rules = {f["rule"] for f in result["findings"]}
    assert {"required_term", "forbidden_term", "unsupported_claim", "brand_voice"} <= rules
    assert result["overall_status"] == "needs_review"
    assert result["findings_count"] == len(result["findings"])
    assert result["llm_state"] == "disabled"


def test_text_analysis_clean(client):
    r = client.post("/api/v1/analysis/text", json={
        "text": "TrueMark helps teams review content for brand consistency.",
        "required_terms": ["TrueMark"],
    })
    result = r.json()["result"]
    assert result["overall_status"] == "passed" and result["findings"] == []


def test_privacy_and_pii_detection(client):
    r = client.post("/api/v1/analysis/text", json={
        "text": "Please email jane.doe@example.com or call 555-123-4567.",
    })
    result = r.json()["result"]
    assert result["pii_detected"] is True
    assert any(f["rule"] == "pii_in_content" for f in result["findings"])


def test_empty_text_rejected(client):
    assert client.post("/api/v1/analysis/text", json={"text": ""}).status_code == 422


def test_llm_failure_falls_back_to_rules(client, monkeypatch):
    monkeypatch.setenv("TRUEMARK_LLM_API_KEY", "k")
    monkeypatch.setenv("TRUEMARK_LLM_MODEL", "m")
    monkeypatch.setenv("TRUEMARK_LLM_BASE_URL", "http://127.0.0.1:9")  # unreachable
    r = client.post("/api/v1/analysis/text", json={"text": "This is guaranteed."})
    assert r.status_code == 200
    result = r.json()["result"]
    assert result["llm_state"].startswith("error")
    assert any(f["rule"] == "unsupported_claim" for f in result["findings"])


def test_docx_upload_verification(client):
    from docx import Document
    doc = Document()
    doc.add_paragraph("Buy now! Our product is guaranteed.")
    buf = io.BytesIO()
    doc.save(buf)
    r = client.post("/api/v1/verification/file", files={
        "file": ("t.docx", buf.getvalue(),
                 "application/vnd.openxmlformats-officedocument.wordprocessingml.document")})
    assert r.status_code == 200
    names = {c["check_name"] for c in r.json()["accessible_checks"]}
    assert {"brand_voice", "unsupported_claim", "readable_text"} <= names


def test_invalid_upload_rejected(client):
    r = client.post("/api/v1/verification/file", files={"file": ("x.png", b"not a png", "image/png")})
    assert r.status_code == 415


def test_png_upload(client):
    from PIL import Image
    buf = io.BytesIO()
    Image.new("RGB", (20, 20), (10, 20, 200)).save(buf, "PNG")
    r = client.post("/api/v1/verification/file", files={"file": ("a.png", buf.getvalue(), "image/png")})
    assert r.status_code == 200
    assert r.json()["file"]["dimensions"] == {"width": 20, "height": 20}


def test_versions_crud(client):
    vid, did = str(uuid.uuid4()), str(uuid.uuid4())
    body = {"id": vid, "document_id": did, "document_title": "Doc", "version_number": 1,
            "content": "hello", "note": "n",
            "created_at": datetime.now(timezone.utc).isoformat()}
    assert client.post("/api/v1/versions", json=body).status_code == 201
    assert client.post("/api/v1/versions", json=body).status_code == 409
    assert any(v["id"] == vid for v in client.get("/api/v1/versions").json())
    assert client.delete(f"/api/v1/versions/{vid}").status_code == 204
    assert client.delete(f"/api/v1/versions/{vid}").status_code == 404


def test_brand_profile_roundtrip(client):
    r = client.post("/brands", json={"brand_name": "Acme"})
    assert r.status_code == 201
    bid = r.json()["profile"]["id"]
    assert client.get(f"/brands/{bid}").json()["brand_name"] == "Acme"


def test_message_does_not_repeat_suggestion(client):
    r = client.post("/api/v1/analysis/text", json={"text": "We are cheap.", "forbidden_terms": ["cheap"]})
    f = next(x for x in r.json()["result"]["findings"] if x["rule"] == "forbidden_term")
    assert f["suggestion"] not in f["message"]
