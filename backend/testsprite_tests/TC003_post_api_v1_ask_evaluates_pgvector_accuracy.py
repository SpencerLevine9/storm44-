"""
TC003 — pgvector RAG Accuracy Evaluation

For each of 6 questions:
  - POST /api/v1/ask and assert a valid 200 response
  - Run a gpt-4o-mini LLM judge comparing the pgvector answer to a hand-written reference
  - For Q6 (Earth speed), assert a refusal response instead of judging quality

Writes a markdown comparison report to TC003_accuracy_report.md.
"""

import json
import os
import re
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv
from openai import OpenAI

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

BASE_URL = "http://127.0.0.1:8000"
TIMEOUT = 30
REPORT_PATH = Path(__file__).parent / "TC003_accuracy_report.md"

# Source IDs by subject (each topic ingested twice — both sets included)
CS_SOURCE_IDS = [
    "a727e300-1381-4716-8239-7b9dedde8f72",  # Intro CS pages 9-36
    "09b79014-7568-48d3-b9e5-4a24d3f93759",  # Intro CS pages 39-87
    "87908c69-f76b-4301-85c8-e96bc7d16776",  # Intro CS pages 9-36 (dup)
    "bd5a3be3-0618-4ac2-b5ac-cfe456c93f3a",  # Intro CS pages 39-87 (dup)
]
PYTHON_SOURCE_IDS = [
    "f64c3841-8f09-420f-b011-264f1ca99ece",  # Intro Python pages 7-35
    "fe2c6cfc-a06f-4fed-b021-1f6d1e4de6e7",  # Intro Python pages 39-67
    "2bc8792b-a411-4afe-a572-c3493849085c",  # Intro Python pages 7-35 (dup)
    "b31691b2-4c4c-4320-b667-eac6d318b489",  # Intro Python pages 39-67 (dup)
]
ALL_SOURCE_IDS = CS_SOURCE_IDS + PYTHON_SOURCE_IDS

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

# ---------------------------------------------------------------------------
# Dataset
# ---------------------------------------------------------------------------

QUESTIONS = [
    {
        "id": "Q1",
        "question": "What is Computer Science?",
        "source_ids": CS_SOURCE_IDS,
        "reference": (
            "Computer science is the study and theory of programming, numerical analysis, "
            "data processing, and the design of computer systems, with a central emphasis on "
            "algorithms. In plain language: it develops the methods (algorithms) and systems "
            "that let computers solve problems and supports many other fields—like data science, "
            "computational science, and information science—by providing tools for managing and "
            "analyzing information."
        ),
        "expect_refusal": False,
    },
    {
        "id": "Q2",
        "question": "What is Python?",
        "source_ids": PYTHON_SOURCE_IDS,
        "reference": (
            "Python is a popular, general-purpose programming language. It has a concise, "
            "straightforward syntax and an extensive Standard Library plus many third-party "
            "libraries (for example Pandas, Spotipy) that make it useful for many kinds of "
            "programs—from data analysis to web and multimedia—and it's widely used by "
            "organizations such as Google, Apple, and NASA."
        ),
        "expect_refusal": False,
    },
    {
        "id": "Q3",
        "question": "What is an Expression in Python?",
        "source_ids": PYTHON_SOURCE_IDS,
        "reference": (
            "An expression in Python is a piece of code that represents a single value to be "
            "computed. Expressions combine literals, variables, and operators (for example, "
            "3*x - 5 evaluates to 7 when x is 4) and can be as simple as a single value "
            "(the 5 in x = 5) or arbitrarily long calculations."
        ),
        "expect_refusal": False,
    },
    {
        "id": "Q4",
        "question": "What is Machine Learning?",
        "source_ids": CS_SOURCE_IDS,
        "reference": (
            "Machine Learning is a subset of artificial intelligence that uses algorithms and "
            "data to enable computers to learn and make predictions or decisions, mimicking the "
            "way humans learn. In plain terms, ML analyzes large datasets to find patterns "
            "(for example in web browser histories) and then uses those patterns for tasks like "
            "recommending products, targeting ads, or detecting fraudulent transactions."
        ),
        "expect_refusal": False,
    },
    {
        "id": "Q5",
        "question": "What is a Turing Machine?",
        "source_ids": CS_SOURCE_IDS,
        "reference": (
            "A Turing machine is a simple mathematical model of a general-purpose computer: "
            "it has an infinitely long tape of symbol cells, a head that can read and write "
            "symbols, a state register, and a list of instructions (transition rules). In plain "
            "terms, it formalizes the idea of an algorithm and computation—despite its simplicity "
            "it captures the power of real computers (Turing-completeness) and underlies "
            "theoretical questions about what can or cannot be computed (for example, the "
            "halting problem)."
        ),
        "expect_refusal": False,
    },
    {
        "id": "Q6",
        "question": "How fast is Earth moving?",
        "source_ids": ALL_SOURCE_IDS,
        "reference": None,  # Expect a refusal, not a quality comparison
        "expect_refusal": True,
    },
]

REFUSAL_PHRASES = [
    "not mentioned",
    "cannot determine",
    "no information",
    "not covered",
    "don't have",
    "not found in",
    "can't determine",
    "do not include",
    "doesn't include",
    "not provided",
    "unable to find",
    "does not provide",
    "does not contain",
    "not available",
    "unclear based on",
    "remains unclear",
    "not discussed",
    "outside the scope",
]

SPEED_PATTERN = re.compile(r"\d[\d,.]*\s*(km|miles|mph|km/h|m/s)", re.IGNORECASE)

JUDGE_SYSTEM = (
    "You are evaluating the quality of two study-aid answers from the perspective of a "
    "college student trying to understand course material."
)

JUDGE_USER_TEMPLATE = """\
Question: {question}

Answer A (Reference): {reference}
Answer B (pgvector RAG): {rag_answer}

Rate each answer on a 1–5 scale for student comprehension value:
- 5: Complete, clear, and correct
- 4: Mostly correct with minor gaps
- 3: Partially correct or unclear
- 2: Mostly incorrect or confusing
- 1: Completely wrong or unhelpful

Return only valid JSON with no extra text:
{{"score_a": <int>, "score_b": <int>, "winner": "<A|B|tie>", "reasoning": "<one sentence>"}}"""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def ask(question: str, source_ids: list[str], top_k: int = 3) -> dict:
    resp = requests.post(
        f"{BASE_URL}/api/v1/ask",
        json={"query": question, "source_ids": source_ids, "top_k": top_k},
        headers={"Content-Type": "application/json"},
        timeout=TIMEOUT,
    )
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    data = resp.json()
    assert isinstance(data, dict), "Response is not a JSON object"
    assert "answer" in data and isinstance(data["answer"], str) and data["answer"], \
        "Missing or empty 'answer' field"
    assert "citations" in data and isinstance(data["citations"], list), \
        "Missing or invalid 'citations' field"
    return data


def judge(question: str, reference: str, rag_answer: str) -> dict:
    prompt = JUDGE_USER_TEMPLATE.format(
        question=question,
        reference=reference,
        rag_answer=rag_answer,
    )
    completion = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[
            {"role": "system", "content": JUDGE_SYSTEM},
            {"role": "user", "content": prompt},
        ],
    )
    raw = completion.choices[0].message.content.strip()
    return json.loads(raw)


def check_refusal(answer: str) -> tuple[bool, bool]:
    """Returns (has_refusal_phrase, has_speed_value)."""
    # Normalize curly apostrophes/quotes to straight so phrase matching works
    # regardless of which quote style the model uses.
    normalized = answer.replace("\u2019", "'").replace("\u2018", "'").lower()
    has_refusal = any(p in normalized for p in REFUSAL_PHRASES)
    has_speed = bool(SPEED_PATTERN.search(normalized))
    return has_refusal, has_speed


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run_tests() -> None:
    results = []
    all_passed = True

    print("\n" + "=" * 70)
    print("TC003 — pgvector RAG Accuracy Evaluation")
    print("=" * 70)

    for entry in QUESTIONS:
        qid = entry["id"]
        question = entry["question"]
        print(f"\n[{qid}] {question}")
        print("-" * 60)

        try:
            data = ask(question, entry["source_ids"])
            rag_answer = data["answer"]
            citations = data["citations"]
            print(f"  pgvector answer ({len(citations)} citations):\n  {rag_answer[:200]}{'...' if len(rag_answer) > 200 else ''}")
        except AssertionError as e:
            print(f"  FAIL — HTTP/schema assertion: {e}")
            results.append({"id": qid, "question": question, "status": "FAIL", "error": str(e)})
            all_passed = False
            continue

        if entry["expect_refusal"]:
            has_refusal, has_speed = check_refusal(rag_answer)
            if has_refusal and not has_speed:
                status = "PASS"
                print(f"  PASS — Correct refusal detected, no speed value present")
            else:
                status = "FAIL"
                msg_parts = []
                if not has_refusal:
                    msg_parts.append("no refusal phrase found")
                if has_speed:
                    msg_parts.append("numeric speed value present")
                print(f"  FAIL — {'; '.join(msg_parts)}")
                all_passed = False

            results.append({
                "id": qid,
                "question": question,
                "rag_answer": rag_answer,
                "reference": "(expected refusal)",
                "status": status,
                "has_refusal": has_refusal,
                "has_speed": has_speed,
            })
        else:
            try:
                verdict = judge(question, entry["reference"], rag_answer)
                score_a = verdict["score_a"]
                score_b = verdict["score_b"]
                winner = verdict["winner"]
                reasoning = verdict["reasoning"]
                status = "PASS"
                winner_label = {"A": "Reference", "B": "pgvector", "tie": "Tie"}.get(winner, winner)
                print(f"  Reference score: {score_a}/5 | pgvector score: {score_b}/5 | Winner: {winner_label}")
                print(f"  Judge: {reasoning}")
            except Exception as e:
                status = "FAIL"
                verdict = {}
                score_a = score_b = winner = reasoning = None
                print(f"  FAIL — Judge error: {e}")
                all_passed = False

            results.append({
                "id": qid,
                "question": question,
                "rag_answer": rag_answer,
                "reference": entry["reference"],
                "status": status,
                "score_a": score_a,
                "score_b": score_b,
                "winner": winner,
                "reasoning": reasoning,
            })

    # Summary
    passed = sum(1 for r in results if r["status"] == "PASS")
    total = len(results)
    print("\n" + "=" * 70)
    print(f"Result: {passed}/{total} passed")
    print("=" * 70)

    write_report(results)
    print(f"\nReport written to: {REPORT_PATH}")

    if not all_passed:
        sys.exit(1)


def write_report(results: list[dict]) -> None:
    lines = [
        "# TC003 — pgvector RAG Accuracy Report\n",
        f"**Date:** 2026-03-24  ",
        f"**Sources:** CS ({len(CS_SOURCE_IDS)}) + Python ({len(PYTHON_SOURCE_IDS)})  ",
        f"**Model:** gpt-5-mini (LLM judge)\n",
        "---\n",
        "## Summary\n",
        "| ID | Question | Ref Score | RAG Score | Winner | Status |",
        "|---|---|---|---|---|---|",
    ]

    for r in results:
        if r.get("expect_refusal") or "has_refusal" in r:
            ref_score = "N/A"
            rag_score = "N/A"
            winner = "Refusal check"
        else:
            ref_score = str(r.get("score_a", "—"))
            rag_score = str(r.get("score_b", "—"))
            winner_raw = r.get("winner", "—")
            winner = {"A": "Reference", "B": "pgvector", "tie": "Tie"}.get(winner_raw, winner_raw or "—")
        status = "✅ PASS" if r["status"] == "PASS" else "❌ FAIL"
        lines.append(f"| {r['id']} | {r['question']} | {ref_score} | {rag_score} | {winner} | {status} |")

    lines.append("\n---\n")
    lines.append("## Per-Question Detail\n")

    for r in results:
        lines.append(f"### {r['id']} — {r['question']}\n")
        lines.append(f"**Status:** {'✅ PASS' if r['status'] == 'PASS' else '❌ FAIL'}  \n")

        if "has_refusal" in r:
            lines.append(f"**Type:** Refusal check  ")
            lines.append(f"**Has refusal phrase:** {r['has_refusal']}  ")
            lines.append(f"**Has speed value:** {r['has_speed']}  \n")
            lines.append(f"**pgvector Answer:**\n> {r.get('rag_answer', '(error)')}\n")
        else:
            lines.append(f"**Reference Score:** {r.get('score_a', '—')}/5  ")
            lines.append(f"**pgvector Score:** {r.get('score_b', '—')}/5  ")
            winner_raw = r.get("winner", "—")
            winner = {"A": "Reference", "B": "pgvector", "tie": "Tie"}.get(winner_raw, winner_raw or "—")
            lines.append(f"**Winner:** {winner}  ")
            lines.append(f"**Judge Reasoning:** {r.get('reasoning', '—')}  \n")
            lines.append(f"**Reference Answer:**\n> {r.get('reference', '—')}\n")
            rag = r.get("rag_answer", "(error)")
            lines.append(f"**pgvector Answer:**\n> {rag}\n")

        lines.append("---\n")

    REPORT_PATH.write_text("\n".join(lines))


if __name__ == "__main__":
    run_tests()
