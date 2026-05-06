import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 30


def test_config_database_pgvector_extension_is_installed():
    """
    TC010 — Configuration: Database pool active and pgvector installed.
    The health endpoint uses a live DB connection, so a 200 response confirms
    the pool is active. We then probe the ask endpoint with a minimal embedding
    query — if pgvector is missing, the vector-distance query will raise a 500
    with a message referencing 'vector' or 'operator'. A successful retrieval
    (even returning no results) means the extension is present.
    """
    # Confirm DB pool is alive
    health_resp = requests.get(f"{BASE_URL}/api/v1/health", timeout=TIMEOUT)
    assert health_resp.status_code == 200, (
        f"Health check failed — DB pool may be down. Status: {health_resp.status_code}"
    )
    body = health_resp.json()
    assert body.get("status") == "ok", f"Unexpected health status: {body}"

    # Probe the ask endpoint — it exercises a pgvector similarity query
    ask_resp = requests.post(
        f"{BASE_URL}/api/v1/ask",
        json={"query": "test pgvector probe", "source_ids": [], "top_k": 1},
        timeout=TIMEOUT,
    )

    # A 500 with a pgvector-specific error means the extension is missing
    if ask_resp.status_code == 500:
        detail = ask_resp.json().get("detail", "").lower()
        pgvector_errors = ["operator does not exist", "type vector", "function vector"]
        for err in pgvector_errors:
            assert err not in detail, (
                f"pgvector extension appears to be missing. Error: {detail}"
            )

    # Any non-500 response (200, 422, etc.) means the query reached the DB successfully
    assert ask_resp.status_code != 500, (
        f"Ask endpoint returned 500 — possible pgvector issue: {ask_resp.text}"
    )


test_config_database_pgvector_extension_is_installed()
