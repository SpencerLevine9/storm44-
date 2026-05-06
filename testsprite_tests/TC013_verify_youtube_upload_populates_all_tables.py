import uuid
import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 90  # transcript fetch + embedding can be slow

# A short, public YouTube video with English captions.
# "Python in 100 Seconds" by Fireship — reliable captions, short duration.
TEST_YOUTUBE_URL = "https://www.youtube.com/watch?v=x7X9w_GIm1s"
TEST_YOUTUBE_TITLE = "Python in 100 Seconds"


def test_verify_youtube_upload_populates_all_tables():
    """
    TC013 — Verification: POST /upload/youtube stores rows in source, chunk,
    embedding, and video_segment tables.
    Uploads a known short YouTube video and asserts:
      - Response is 200 with a valid source_id UUID.
      - Ask query scoped to that source_id returns citations, proving chunk +
        embedding rows exist.
      - The citation may include start_seconds, confirming video_segment rows
        were inserted (start_seconds is populated from video_segment.start_time).
    Cleans up after assertions.
    """
    # 1. Upload
    try:
        upload_resp = requests.post(
            f"{BASE_URL}/api/v1/sources/upload/youtube",
            json={"url": TEST_YOUTUBE_URL, "title": TEST_YOUTUBE_TITLE},
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

    # 2. Verify source + chunk + embedding rows exist via ask
    try:
        ask_resp = requests.post(
            f"{BASE_URL}/api/v1/ask",
            json={
                "query": "What is Python used for?",
                "source_ids": [source_id],
                "top_k": 3,
            },
            timeout=TIMEOUT,
        )
    except requests.RequestException as e:
        assert False, f"Ask request failed: {e}"

    assert ask_resp.status_code == 200, (
        f"Ask returned {ask_resp.status_code} — rows may be missing. Body: {ask_resp.text}"
    )
    ask_body = ask_resp.json()
    assert "citations" in ask_body, f"Ask response missing 'citations': {ask_body}"
    assert len(ask_body["citations"]) > 0, (
        "No citations returned — chunk/embedding rows may be missing"
    )

    cited_sources = [c.get("source_id") for c in ask_body["citations"]]
    assert source_id in cited_sources, (
        f"Expected source_id {source_id} in citations, got: {cited_sources}"
    )

    # 3. Confirm video_segment rows were inserted (start_seconds will be non-null)
    citations_with_timestamp = [
        c for c in ask_body["citations"] if c.get("start_seconds") is not None
    ]
    assert len(citations_with_timestamp) > 0, (
        "No citations had start_seconds — video_segment rows may not have been inserted"
    )

    # 4. Cleanup
    requests.delete(
        f"{BASE_URL}/api/v1/sources/delete/{source_id}",
        timeout=TIMEOUT,
    )


test_verify_youtube_upload_populates_all_tables()
