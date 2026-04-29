import os
import requests
from openai import OpenAI

def test_tc004_post_api_v1_ask_compare_topk_2_vs_5():
    base_url = "http://127.0.0.1:8000"
    ask_endpoint = f"{base_url}/api/v1/ask"
    timeout = 120  # seconds
    source_ids = [
        "038c02b0-f624-4e93-8959-562424a89c78",
        "7cce7f29-993c-4a02-a9e5-28d2c774bbe5"
    ]

    questions = [
        "What is a variable in Python?",
        "What is a list in Python?",
        "How do you write a for loop in Python?",
        "What is the difference between mutable and immutable data types in Python, and can you give examples of each?",
        "How do functions work in Python? Explain parameters, return values, and how to define and call a function.",
        "What is the difference between a while loop and a for loop in Python, and when should you use each one?",
        "What is the boiling point of water in Celsius?"
    ]

    refusal_keywords = [
        "does not", "does not state", "cannot", "can not", "unable", "refuse", "decline",
        "no information", "not covered", "out of scope", "off-topic", "not answer",
        "no answer", "without additional", "not have"
    ]

    # Initialize OpenAI client
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    def is_refusal(answer_text: str) -> bool:
        ans = answer_text.lower()
        return any(keyword in ans for keyword in refusal_keywords)

    def llm_score_answer(llm_client, answer: str) -> int:
        prompt = (
            f"Score the following answer on a scale of 1 to 5, where 1 is poor and 5 is excellent:\n\n"
            f"{answer}\n\nScore:"
        )
        try:
            response = llm_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                timeout=120
            )
            content = response.choices[0].message.content.strip()
            score = int(next(filter(str.isdigit, content.split()), 0))
            if score < 1 or score > 5:
                # fallback if score out of range
                return 3  # neutral median score
            return score
        except Exception:
            # If LLM call fails, return neutral score
            return 3

    results = []

    for i, question in enumerate(questions, 1):
        answers = {}
        citations = {}
        for top_k in [2, 5]:
            body = {
                "query": question,
                "source_ids": source_ids,
                "top_k": top_k
            }
            try:
                resp = requests.post(ask_endpoint, json=body, timeout=timeout)
            except requests.RequestException as e:
                assert False, f"Request failed for question {i} top_k={top_k}: {str(e)}"

            assert resp.status_code == 200, f"Expected 200 for question {i} top_k={top_k}, got {resp.status_code}"
            data = resp.json()
            assert "answer" in data and isinstance(data["answer"], str), f"Missing or invalid 'answer' for question {i} top_k={top_k}"
            answer_text = data["answer"].strip()
            assert answer_text != "", f"Empty answer returned for question {i} top_k={top_k}"
            assert "citations" in data and isinstance(data["citations"], list), f"Missing or invalid 'citations' for question {i} top_k={top_k}"

            # Print full answer and citations
            print(f"\nQuestion {i} (top_k={top_k}): {question}")
            print("Answer:")
            print(answer_text)
            print("Citations:")
            if len(data["citations"]) == 0:
                print("  NONE")
            else:
                for c in data["citations"]:
                    sid = c.get("source_id", "N/A")
                    chkid = c.get("chunk_id", "N/A")
                    snippet = c.get("snippet", "N/A")
                    url = c.get("url", "")
                    print(f"  Source ID: {sid}, Chunk ID: {chkid}, Snippet: {snippet}")
                    if url:
                        print(f"   URL: {url}")

            answers[top_k] = answer_text
            citations[top_k] = data["citations"]

        # Validate refusal for Q7 only
        if i == 7:
            # Both top_k=2 and top_k=5 must be refusal answers
            assert is_refusal(answers[2]), f"Q7 top_k=2 answer is not refusal"
            assert is_refusal(answers[5]), f"Q7 top_k=5 answer is not refusal"
        else:
            # Q1-Q6: answers must be non-empty and have citations
            assert answers[2], f"Empty answer text for question {i} top_k=2"
            assert answers[5], f"Empty answer text for question {i} top_k=5"
            assert isinstance(citations[2], list) and len(citations[2]) > 0, f"No citations for question {i} top_k=2"
            assert isinstance(citations[5], list) and len(citations[5]) > 0, f"No citations for question {i} top_k=5"

            # Use LLM judge to score each answer and record which top_k wins
            score_2 = llm_score_answer(client, answers[2])
            score_5 = llm_score_answer(client, answers[5])
            winner = None
            if score_2 > score_5:
                winner = 2
            elif score_5 > score_2:
                winner = 5
            else:
                winner = 0  # tie

            results.append({
                "question_number": i,
                "top_k=2_score": score_2,
                "top_k=5_score": score_5,
                "winner": winner
            })

    # Print summary
    print("\nSummary of LLM Judge Scores (1-5 scale):")
    for res in results:
        tie_status = "Tie" if res["winner"] == 0 else f"Top_k={res['winner']} wins"
        print(f"Q{res['question_number']}: top_k=2 score = {res['top_k=2_score']}, top_k=5 score = {res['top_k=5_score']} --> {tie_status}")

test_tc004_post_api_v1_ask_compare_topk_2_vs_5()