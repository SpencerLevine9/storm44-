import io
import uuid
import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 60


def _make_test_pdf(text: str) -> bytes:
    """Build a minimal but valid single-page PDF containing the given text."""
    stream_content = f"BT /F1 12 Tf 72 720 Td ({text}) Tj ET".encode()
    stream_len = len(stream_content)
    pdf = (
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
    return pdf


def test_verify_pdf_upload_populates_source_chunk_embedding_tables():
    """
    TC012 — Verification: POST /upload/pdf stores rows in source, chunk, embedding.
    Uploads a minimal test PDF and asserts:
      - Response is 200 with a valid source_id UUID.
      - Subsequent ask query scoped to that source_id returns a non-error response,
        proving the chunk and embedding rows were inserted (a missing embedding
        would cause the vector search to return nothing or error).
    Cleans up by deleting the source after assertions.
    """
    # Enough words to survive the MIN_CHUNK_WORDS=35 filter in chunk.py
    body_text = (
        "The mitochondria is the powerhouse of the cell. "
        "It produces adenosine triphosphate through cellular respiration. "
        "The process involves glycolysis, the Krebs cycle, and oxidative phosphorylation. "
        "Glucose is broken down into pyruvate during glycolysis in the cytoplasm. "
        "The Krebs cycle occurs in the mitochondrial matrix and generates NADH and FADH2."
    )
    pdf_bytes = _make_test_pdf(body_text)
    title = f"TC012-test-{uuid.uuid4().hex[:8]}"

    # 1. Upload
    try:
        upload_resp = requests.post(
            f"{BASE_URL}/api/v1/sources/upload/pdf",
            files={"file": ("tc012_test.pdf", io.BytesIO(pdf_bytes), "application/pdf")},
            data={"title": title},
            timeout=TIMEOUT,
        )
    except requests.RequestException as e:
        assert False, f"Upload request failed: {e}"

    assert upload_resp.status_code == 200, (
        f"Expected 200 from upload/pdf, got {upload_resp.status_code}. Body: {upload_resp.text}"
    )

    body = upload_resp.json()
    assert "source_id" in body, f"Response missing 'source_id': {body}"
    source_id = body["source_id"]

    # Validate UUID format
    try:
        uuid.UUID(source_id)
    except ValueError:
        assert False, f"source_id is not a valid UUID: {source_id!r}"

    # 2. Verify retrieval works (proves chunk + embedding rows exist)
    try:
        ask_resp = requests.post(
            f"{BASE_URL}/api/v1/ask",
            json={
                "query": "What does the mitochondria produce?",
                "source_ids": [source_id],
                "top_k": 3,
            },
            timeout=TIMEOUT,
        )
    except requests.RequestException as e:
        assert False, f"Ask request failed: {e}"

    assert ask_resp.status_code == 200, (
        f"Ask returned {ask_resp.status_code} — chunk/embedding rows may be missing. "
        f"Body: {ask_resp.text}"
    )
    ask_body = ask_resp.json()
    assert "answer" in ask_body, f"Ask response missing 'answer': {ask_body}"
    assert "citations" in ask_body, f"Ask response missing 'citations': {ask_body}"
    assert isinstance(ask_body["citations"], list), "'citations' should be a list"
    assert len(ask_body["citations"]) > 0, (
        "No citations returned — embedding rows may not have been inserted"
    )

    # Confirm citation references our source
    cited_sources = [c.get("source_id") for c in ask_body["citations"]]
    assert source_id in cited_sources, (
        f"Expected source_id {source_id} in citations, got: {cited_sources}"
    )

    # 3. Cleanup
    requests.delete(
        f"{BASE_URL}/api/v1/sources/delete/{source_id}",
        timeout=TIMEOUT,
    )


test_verify_pdf_upload_populates_source_chunk_embedding_tables()
