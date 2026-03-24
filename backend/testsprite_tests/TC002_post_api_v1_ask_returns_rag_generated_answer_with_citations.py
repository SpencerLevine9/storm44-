import requests

def test_post_api_v1_ask_returns_rag_generated_answer_with_citations():
    base_url = "http://127.0.0.1:8000"
    endpoint = "/api/v1/ask"
    url = base_url + endpoint

    payload = {
        "query": "what is a variable?",
        "source_ids": ["a727e300-1381-4716-8239-7b9dedde8f72"],
        "top_k": 3
    }
    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
    except requests.RequestException as e:
        assert False, f"Request failed: {e}"

    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"

    try:
        data = response.json()
    except ValueError:
        assert False, "Response is not valid JSON"

    assert isinstance(data, dict), "Response JSON is not a dictionary"
    assert "answer" in data, "Response JSON missing 'answer'"
    assert isinstance(data["answer"], str), "'answer' should be a string"
    assert data["answer"], "'answer' should not be empty"

    assert "citations" in data, "Response JSON missing 'citations'"
    assert isinstance(data["citations"], list), "'citations' should be a list"

    for citation in data["citations"]:
        assert isinstance(citation, dict), "Each citation should be a dictionary"
        assert "source_id" in citation, "Citation missing 'source_id'"
        assert isinstance(citation["source_id"], str), "'source_id' should be a string"
        assert citation["source_id"], "'source_id' should not be empty"

        # chunk_id is optional according to PRD (optional in description, but schema says optional)
        if "chunk_id" in citation:
            assert isinstance(citation["chunk_id"], str), "'chunk_id' should be a string if present"
            assert citation["chunk_id"], "'chunk_id' should not be empty if present"

        assert "snippet" in citation, "Citation missing 'snippet'"
        assert isinstance(citation["snippet"], str), "'snippet' should be a string"
        assert citation["snippet"], "'snippet' should not be empty"

        if "start_seconds" in citation:
            # start_seconds is optional float
            assert isinstance(citation["start_seconds"], (int, float)), "'start_seconds' should be a number if present"

        if "url" in citation:
            assert isinstance(citation["url"], str), "'url' should be a string if present"
            assert citation["url"], "'url' should not be empty if present"

test_post_api_v1_ask_returns_rag_generated_answer_with_citations()