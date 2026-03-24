import requests

def test_post_api_v1_ask_returns_rag_generated_answer_with_citations():
    base_url = "http://127.0.0.1:8000"
    endpoint = "/api/v1/ask"
    url = base_url + endpoint
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "query": "Explain the core concept of Storm44 AI Tutor",
        "top_k": 5
    }
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        # Assert HTTP 200
        assert response.status_code == 200, f"Expected status code 200 but got {response.status_code} with response {response.text}"

        json_data = response.json()

        # Assert answer is present and is a non-empty string
        assert "answer" in json_data, "Response JSON missing 'answer' field"
        assert isinstance(json_data["answer"], str), "'answer' field is not a string"
        assert len(json_data["answer"].strip()) > 0, "'answer' field is empty"

        # Assert citations is present and is a list
        assert "citations" in json_data, "Response JSON missing 'citations' field"
        assert isinstance(json_data["citations"], list), "'citations' field is not a list"

        # Validate each citation object fields
        for citation in json_data["citations"]:
            assert "source_id" in citation, "Citation missing 'source_id'"
            assert isinstance(citation["source_id"], str), "'source_id' is not a string"
            # chunk_id is optional but if present must be string
            if "chunk_id" in citation:
                assert isinstance(citation["chunk_id"], str), "'chunk_id' is not a string"
            # snippet must be present and string
            assert "snippet" in citation, "Citation missing 'snippet'"
            assert isinstance(citation["snippet"], str), "'snippet' is not a string"
            # start_seconds is optional but if present must be float or int
            if "start_seconds" in citation:
                assert isinstance(citation["start_seconds"], (float, int)), "'start_seconds' is not float or int"
            # url is optional but if present must be string
            if "url" in citation:
                assert isinstance(citation["url"], str), "'url' is not a string"

    except requests.RequestException as e:
        assert False, f"Request to {url} failed with exception: {e}"

test_post_api_v1_ask_returns_rag_generated_answer_with_citations()
