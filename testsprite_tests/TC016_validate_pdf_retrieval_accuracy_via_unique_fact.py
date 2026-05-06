import io
import uuid
import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 60

# A unique, specific fact unlikely to appear in any pre-existing DB data.
UNIQUE_FACT = "The melting point of gallium is 29.76 degrees Celsius"
UNIQUE_KEYWORD = "gallium"


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


def test_validate_pdf_retrieval_accuracy_via_unique_fact():
    """
    TC016 — Validation: End-to-end PDF ingestion → RAG retrieval accuracy.
    Uploads a PDF containing a unique fact (gallium melting point), then asks
    about it. Asserts the LLM answer references the unique keyword, confirming
    the chunk was stored, retrieved, and used as context.
    """
    body_text = (
        "Gallium is a soft silvery metal with the chemical symbol Ga. "
        "The melting point of gallium is 29.76 degrees Celsius which means "
        "it melts when held in the human hand at body temperature. "
        "This property makes gallium unique among metals commonly found at room "
        "temperature. Gallium is used in semiconductors and LED manufacturing. "
        "Its boiling point is much higher at approximately 2204 degrees Celsius."
    )
    pdf_bytes = _make_test_pdf(body_text)
    title = f"TC016-gallium-{uuid.uuid4().hex[:8]}"

    # 1. Upload
    upload_resp = requests.post(
        f"{BASE_URL}/api/v1/sources/upload/pdf",
        files={"file": ("tc016_gallium.pdf", io.BytesIO(pdf_bytes), "application/pdf")},
        data={"title": title},
        timeout=TIMEOUT,
    )
    assert upload_resp.status_code == 200, (
        f"Upload failed: {upload_resp.status_code} — {upload_resp.text}"
    )
    source_id = upload_resp.json()["source_id"]

    try:
        # 2. Ask about the unique fact
        ask_resp = requests.post(
            f"{BASE_URL}/api/v1/ask",
            json={
                "query": "What is the melting point of gallium?",
                "source_ids": [source_id],
                "top_k": 5,
            },
            timeout=TIMEOUT,
        )
        assert ask_resp.status_code == 200, (
            f"Ask failed: {ask_resp.status_code} — {ask_resp.text}"
        )

        ask_body = ask_resp.json()
        answer = ask_body.get("answer", "").lower()
        citations = ask_body.get("citations", [])

        # The answer must reference the unique keyword
        assert UNIQUE_KEYWORD in answer, (
            f"Expected '{UNIQUE_KEYWORD}' in answer but got: {ask_body['answer']!r}"
        )

        # Must have at least one citation referencing our source
        assert len(citations) > 0, "No citations returned"
        cited_sources = [c.get("source_id") for c in citations]
        assert source_id in cited_sources, (
            f"source_id {source_id} not in citations: {cited_sources}"
        )

    finally:
        # 3. Cleanup
        requests.delete(
            f"{BASE_URL}/api/v1/sources/delete/{source_id}",
            timeout=TIMEOUT,
        )


test_validate_pdf_retrieval_accuracy_via_unique_fact()
