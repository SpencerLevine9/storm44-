import uuid
import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 90

# Short public video with reliable auto-captions.
# "Python in 100 Seconds" by Fireship.
TEST_YOUTUBE_URL = "https://www.youtube.com/watch?v=x7X9w_GIm1s"


def test_validate_youtube_retrieval_returns_answer_and_citations():
    """
    TC017 — Validation: YouTube ingestion → RAG pipeline returns a grounded answer.
    Asserts structural correctness of the full pipeline, not specific answer content:
      - Upload succeeds and returns a UUID source_id.
      - Ask scoped to that source_id returns a non-empty answer and at least one citation.
      - At least one citation references the uploaded source_id.
      - At least one citation has a non-null start_seconds (video_segment linked).
    """
    # 1. Upload
    try:
        upload_resp = requests.post(
            f"{BASE_URL}/api/v1/sources/upload/youtube",
            json={"url": TEST_YOUTUBE_URL, "title": "TC017 YouTube Test"},
            timeout=TIMEOUT,
        )
    except requests.RequestException as e:
        assert False, f"Upload request failed: {e}"

    assert upload_resp.status_code == 200, (
        f"Expected 200 from upload/youtube, got {upload_resp.status_code}. "
        f"Body: {upload_resp.text}"
    )
    body = upload_resp.json()
    assert "source_id" in body, f"Response missing 'source_id': {body}"
    source_id = body["source_id"]
    try:
        uuid.UUID(source_id)
    except ValueError:
        assert False, f"source_id is not a valid UUID: {source_id!r}"

    try:
        # 2. Ask — query matches general transcript content
        ask_resp = requests.post(
            f"{BASE_URL}/api/v1/ask",
            json={
                "query": "What does this video explain?",
                "source_ids": [source_id],
                "top_k": 5,
            },
            timeout=TIMEOUT,
        )
        assert ask_resp.status_code == 200, (
            f"Ask failed: {ask_resp.status_code} — {ask_resp.text}"
        )

        ask_body = ask_resp.json()
        answer = ask_body.get("answer", "")
        citations = ask_body.get("citations", [])

        assert isinstance(answer, str) and answer.strip(), "Answer is empty"
        assert len(citations) > 0, "No citations returned"

        cited_sources = [c.get("source_id") for c in citations]
        assert source_id in cited_sources, (
            f"source_id {source_id} not found in citations: {cited_sources}"
        )

        citations_with_ts = [c for c in citations if c.get("start_seconds") is not None]
        assert len(citations_with_ts) > 0, (
            "No citation had a start_seconds value — video_segment rows may not be "
            "linked to retrieval results"
        )

    finally:
        # 3. Cleanup
        requests.delete(
            f"{BASE_URL}/api/v1/sources/delete/{source_id}",
            timeout=TIMEOUT,
        )


test_validate_youtube_retrieval_returns_answer_and_citations()
