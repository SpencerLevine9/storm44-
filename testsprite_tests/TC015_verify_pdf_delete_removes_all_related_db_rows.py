import io
import uuid
import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 60


def _make_test_pdf(text: str) -> bytes:
    stream_content = f"BT /F1 12 Tf 72 720 Td ({text}) Tj ET".encode()
    stream_len = len(stream_content)
    return (
        b"%PDF-1.4\n"
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792]\n"
        b"   /Contents 4 0 R /Resources << /Font << /F1 << /Type /Font\n"
        b"   /Subtype /Type1 /BaseFont /Helvetica >> >> >> >>\nendobj\n"
        b"4 0 obj\n<< /Length " + str(stream_len).encode() + b" >>\nstream\n"
        + stream_content
        + b"\nendstream\nendobj\n"
        b"xref\n0 5\n0000000000 65535 f \n"
        b"trailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n0\n%%EOF"
    )


def test_verify_pdf_delete_removes_all_related_db_rows():
    """
    TC015 — Verification: DELETE /delete/{source_id} removes the source and
    all related rows.
    Steps:
      1. Upload a test PDF and capture source_id.
      2. Confirm the source is queryable (ask returns citations).
      3. Delete the source via DELETE /delete/{source_id}.
      4. Assert the delete response is 200 with {"deleted": true}.
      5. Ask the same question again — assert no citations reference the
         deleted source_id, proving chunk and embedding rows are gone.
    """
    body_text = (
        "Quantum entanglement is a phenomenon where two particles become "
        "correlated such that the state of one instantly influences the other "
        "regardless of the distance separating them. Einstein called this "
        "spooky action at a distance. Entanglement is a key resource in "
        "quantum computing and quantum cryptography protocols."
    )
    pdf_bytes = _make_test_pdf(body_text)
    title = f"TC015-delete-test-{uuid.uuid4().hex[:8]}"

    # 1. Upload
    upload_resp = requests.post(
        f"{BASE_URL}/api/v1/sources/upload/pdf",
        files={"file": ("tc015_test.pdf", io.BytesIO(pdf_bytes), "application/pdf")},
        data={"title": title},
        timeout=TIMEOUT,
    )
    assert upload_resp.status_code == 200, (
        f"Upload failed with {upload_resp.status_code}: {upload_resp.text}"
    )
    source_id = upload_resp.json()["source_id"]

    # 2. Confirm retrieval works pre-delete
    ask_before = requests.post(
        f"{BASE_URL}/api/v1/ask",
        json={"query": "What is quantum entanglement?", "source_ids": [source_id], "top_k": 3},
        timeout=TIMEOUT,
    )
    assert ask_before.status_code == 200, (
        f"Pre-delete ask failed: {ask_before.status_code}"
    )
    assert len(ask_before.json().get("citations", [])) > 0, (
        "No citations before delete — source may not have ingested correctly"
    )

    # 3. Delete
    delete_resp = requests.delete(
        f"{BASE_URL}/api/v1/sources/delete/{source_id}",
        timeout=TIMEOUT,
    )
    assert delete_resp.status_code == 200, (
        f"DELETE returned {delete_resp.status_code}: {delete_resp.text}"
    )
    delete_body = delete_resp.json()
    assert delete_body.get("deleted") is True, (
        f"Expected {{\"deleted\": true}}, got: {delete_body}"
    )

    # 4. Confirm rows are gone — ask should return no citations for this source
    ask_after = requests.post(
        f"{BASE_URL}/api/v1/ask",
        json={"query": "What is quantum entanglement?", "source_ids": [source_id], "top_k": 3},
        timeout=TIMEOUT,
    )
    assert ask_after.status_code == 200, (
        f"Post-delete ask failed: {ask_after.status_code}"
    )
    after_citations = ask_after.json().get("citations", [])
    cited_sources = [c.get("source_id") for c in after_citations]
    assert source_id not in cited_sources, (
        f"Deleted source_id {source_id} still appears in citations — rows not fully removed"
    )


test_verify_pdf_delete_removes_all_related_db_rows()
