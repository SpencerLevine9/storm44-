import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 30


def test_config_temp_directory_is_writable_for_pdf_processing():
    """
    TC009 — Configuration: Temp directory write access.
    The backend health endpoint must be reachable, and the /upload/pdf route
    must exist (405 or 422 on an empty POST is fine — a 404 means the route
    was never registered, which would also mean temp-dir logic is unreachable).
    We also confirm the OS-level temp dir is writable from within this process
    as a proxy for the backend's environment.
    """
    import os
    import tempfile

    # Verify the backend is up
    health_resp = requests.get(f"{BASE_URL}/api/v1/health", timeout=TIMEOUT)
    assert health_resp.status_code == 200, (
        f"Backend not healthy — got {health_resp.status_code}"
    )

    # Verify the PDF upload route is registered (not 404)
    probe = requests.post(
        f"{BASE_URL}/api/v1/sources/upload/pdf",
        data={},
        timeout=TIMEOUT,
    )
    assert probe.status_code != 404, (
        "PDF upload route not found — endpoint may not be registered"
    )

    # Verify temp-dir write access in the test environment
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(b"%PDF-1.4 test")
            tmp_path = tmp.name
        assert os.path.exists(tmp_path), "Temp file was not created"
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)

    assert not os.path.exists(tmp_path), "Temp file was not cleaned up"


test_config_temp_directory_is_writable_for_pdf_processing()
