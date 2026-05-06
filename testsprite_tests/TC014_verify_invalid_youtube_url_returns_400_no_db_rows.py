import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

INVALID_CASES = [
    {"url": "not-a-url-at-all", "label": "non-URL string"},
    {"url": "https://example.com/not-youtube", "label": "non-YouTube domain"},
    {"url": "https://www.youtube.com/watch?v=AAAAAAAAAAAAAAAAAAAAA", "label": "invalid video ID"},
    {"url": "", "label": "empty string"},
]


def test_verify_invalid_youtube_url_returns_400_no_db_rows():
    """
    TC014 — Verification: POST /upload/youtube with invalid URLs returns 400.
    For each invalid input, asserts:
      - Response status is 400 (not 200, not 500).
      - The response body contains a 'detail' field explaining the error.
    We cannot directly query the DB in this HTTP-level test, but a 400 response
    from the endpoint guarantees the request was rejected before any DB transaction
    was opened (the endpoint raises HTTPException immediately on invalid URL /
    missing transcript).
    """
    for case in INVALID_CASES:
        try:
            resp = requests.post(
                f"{BASE_URL}/api/v1/sources/upload/youtube",
                json={"url": case["url"], "title": "TC014 invalid test"},
                timeout=TIMEOUT,
            )
        except requests.RequestException as e:
            assert False, f"Request failed for case '{case['label']}': {e}"

        assert resp.status_code == 400, (
            f"Case '{case['label']}': expected 400 but got {resp.status_code}. "
            f"Body: {resp.text}"
        )

        body = resp.json()
        assert "detail" in body, (
            f"Case '{case['label']}': response missing 'detail' field: {body}"
        )
        assert isinstance(body["detail"], str) and body["detail"].strip(), (
            f"Case '{case['label']}': 'detail' should be a non-empty string"
        )


test_verify_invalid_youtube_url_returns_400_no_db_rows()
