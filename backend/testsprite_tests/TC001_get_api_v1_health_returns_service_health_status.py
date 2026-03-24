import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

def test_get_api_v1_health_returns_service_health_status():
    url = f"{BASE_URL}/api/v1/health"
    try:
        response = requests.get(url, timeout=TIMEOUT)
        # Expect either 200 with {"status":"ok"} or 500 with error detail
        if response.status_code == 200:
            json_data = response.json()
            assert isinstance(json_data, dict), "Response JSON should be a dictionary"
            assert "status" in json_data, "'status' key missing in response"
            assert json_data["status"] == "ok", f"Expected status 'ok', got {json_data['status']}"
        elif response.status_code == 500:
            try:
                json_data = response.json()
                # Error details expected as some form of message or detail
                assert isinstance(json_data, dict), "Error response JSON should be a dictionary"
                assert any(k in json_data for k in ["detail", "error", "message"]), "Expected error detail field in 500 response"
            except ValueError:
                # If response is not JSON, just check text is non-empty
                assert response.text.strip(), "500 response should have error details"
        else:
            assert False, f"Unexpected status code {response.status_code} received"
    except requests.RequestException as e:
        assert False, f"Request to /api/v1/health failed: {e}"

test_get_api_v1_health_returns_service_health_status()