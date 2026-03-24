import requests

BASE_URL = "http://127.0.0.1:8000"
TIMEOUT = 30

def test_get_api_v1_health_returns_service_health_status():
    url = f"{BASE_URL}/api/v1/health"
    try:
        response = requests.get(url, timeout=TIMEOUT)
        # The healthy service case returns 200 with {"status":"ok"}
        if response.status_code == 200:
            json_data = response.json()
            assert isinstance(json_data, dict), "Response JSON should be a dictionary"
            assert "status" in json_data, "'status' key missing in response JSON"
            assert json_data["status"] == "ok", "Expected status 'ok' in healthy response"
        else:
            # The degraded service case returns 500 with error detail
            assert response.status_code == 500, f"Unexpected status code {response.status_code}"
            # Ensure response has error details (string or dict)
            try:
                error_detail = response.json()
                assert error_detail, "Error detail missing in 500 response"
            except Exception:
                # If not JSON, just ensure there is some text content
                assert response.text, "Error detail missing in 500 response text"
    except requests.RequestException as e:
        assert False, f"Request failed: {e}"

test_get_api_v1_health_returns_service_health_status()