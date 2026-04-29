"""
TC004 — Top-K Retrieval Quality Comparison (k=2 vs k=5)

Directly imports answer_question from machine_learning/ingest_pipeline/store/answer.py
and runs 7 questions (3 simple Python, 3 detailed Python, 1 off-topic refusal) with
both k=2 and k=5.

For each question:
  - Prints the full output from both k=2 and k=5
  - Runs a gpt-4o-mini LLM judge comparing the two answers
  - Checks that the off-topic question is refused at both k values

Writes a markdown comparison report to TC004_retrieval_comparison_report.md.
"""

import json
import os
import sys
from pathlib import Path
from datetime import date

from dotenv import load_dotenv
from openai import OpenAI

# ---------------------------------------------------------------------------
# Path setup — add machine_learning to sys.path so we can import answer.py
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[2]
ML_ROOT = REPO_ROOT / "machine_learning"

if str(ML_ROOT) not in sys.path:
    sys.path.insert(0, str(ML_ROOT))

load_dotenv(REPO_ROOT / "backend" / ".env")

from ingest_pipeline.store.answer import answer_question  # noqa: E402

REPORT_PATH = Path(__file__).parent / "TC004_retrieval_comparison_report.md"

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

# ---------------------------------------------------------------------------
# Dataset — 3 simple + 3 detailed Python questions + 1 refusal
# ---------------------------------------------------------------------------

QUESTIONS = [
    # ── Simple Python questions ──────────────────────────────────────────
    {
        "id": "Q1",
        "label": "Simple",
        "question": "What is a variable in Python?",
        "expect_refusal": False,
    },
    {
        "id": "Q2",
        "label": "Simple",
        "question": "What is a list in Python?",
        "expect_refusal": False,
    },
    {
        "id": "Q3",
        "label": "Simple",
        "question": "How do you write a for loop in Python?",
        "expect_refusal": False,
    },
    # ── Detailed Python questions ────────────────────────────────────────
    {
        "id": "Q4",
        "label": "Detailed",
        "question": (
            "What is the difference between mutable and immutable data types "
            "in Python, and can you give examples of each?"
        ),
        "expect_refusal": False,
    },
    {
        "id": "Q5",
        "label": "Detailed",
        "question": (
            "How do functions work in Python? Explain parameters, return values, "
            "and how to define and call a function."
        ),
        "expect_refusal": False,
    },
    {
        "id": "Q6",
        "label": "Detailed",
        "question": (
            "What is the difference between a while loop and a for loop in Python, "
            "and when should you use each one?"
        ),
        "expect_refusal": False,
    },
    # ── Off-topic refusal ────────────────────────────────────────────────
    {
        "id": "Q7",
        "label": "Refusal",
        "question": "What is the boiling point of water in Celsius?",
        "expect_refusal": True,
    },
]

REFUSAL_PHRASES = [
    "only answer questions",
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
    "not discussed",
    "outside the scope",
    "uploaded materials",
    "grounded in",
]

JUDGE_SYSTEM = (
    "You are evaluating the quality of two study-aid answers from the perspective of "
    "a college student trying to understand course material."
)

JUDGE_USER_TEMPLATE = """\
Question: {question}

Answer A (k=2, top-2 chunks retrieved): {answer_k2}

Answer B (k=5, top-5 chunks retrieved): {answer_k5}

Rate each answer on a 1–5 scale for student comprehension value:
- 5: Complete, clear, and correct
- 4: Mostly correct with minor gaps
- 3: Partially correct or unclear
- 2: Mostly incorrect or confusing
- 1: Completely wrong or unhelpful

Then state which retrieval depth produced the better answer or if they are equivalent.

Return only valid JSON with no extra text:
{{"score_k2": <int>, "score_k5": <int>, "winner": "<k2|k5|tie>", "reasoning": "<one sentence>"}}"""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def strip_sources_section(full_output: str) -> str:
    """Return only the Answer section from answer_question output."""
    if "\n\nSources:" in full_output:
        return full_output.split("\n\nSources:")[0].replace("Answer:\n", "").strip()
    return full_output.replace("Answer:\n", "").strip()


def extract_sources_section(full_output: str) -> str:
    """Return only the Sources section from answer_question output."""
    if "\n\nSources:\n" in full_output:
        return full_output.split("\n\nSources:\n", 1)[1].strip()
    return "(no sources listed)"


def is_refusal(answer_text: str) -> bool:
    normalized = answer_text.lower()
    return any(phrase in normalized for phrase in REFUSAL_PHRASES)


def judge_answers(question: str, answer_k2: str, answer_k5: str) -> dict:
    prompt = JUDGE_USER_TEMPLATE.format(
        question=question,
        answer_k2=answer_k2,
        answer_k5=answer_k5,
    )
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": JUDGE_SYSTEM},
            {"role": "user", "content": prompt},
        ],
    )
    raw = completion.choices[0].message.content.strip()
    return json.loads(raw)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run_tests() -> None:
    results = []
    all_passed = True

    print("\n" + "=" * 70)
    print("TC004 — Top-K Retrieval Quality Comparison (k=2 vs k=5)")
    print("=" * 70)

    for entry in QUESTIONS:
        qid = entry["id"]
        question = entry["question"]
        label = entry["label"]

        print(f"\n[{qid} | {label}] {question}")
        print("-" * 60)

        # ── Retrieve with k=2 ────────────────────────────────────────────
        try:
            raw_k2 = answer_question(question, k=2)
            answer_k2 = strip_sources_section(raw_k2)
            sources_k2 = extract_sources_section(raw_k2)
        except Exception as exc:
            print(f"  k=2 ERROR: {exc}")
            results.append({"id": qid, "label": label, "question": question,
                             "status": "FAIL", "error": f"k=2: {exc}"})
            all_passed = False
            continue

        # ── Retrieve with k=5 ────────────────────────────────────────────
        try:
            raw_k5 = answer_question(question, k=5)
            answer_k5 = strip_sources_section(raw_k5)
            sources_k5 = extract_sources_section(raw_k5)
        except Exception as exc:
            print(f"  k=5 ERROR: {exc}")
            results.append({"id": qid, "label": label, "question": question,
                             "status": "FAIL", "error": f"k=5: {exc}"})
            all_passed = False
            continue

        print(f"  k=2 answer: {answer_k2[:200]}{'...' if len(answer_k2) > 200 else ''}")
        print(f"  k=2 sources:\n    {sources_k2.replace(chr(10), chr(10) + '    ')}")
        print()
        print(f"  k=5 answer: {answer_k5[:200]}{'...' if len(answer_k5) > 200 else ''}")
        print(f"  k=5 sources:\n    {sources_k5.replace(chr(10), chr(10) + '    ')}")

        # ── Refusal check ────────────────────────────────────────────────
        if entry["expect_refusal"]:
            refused_k2 = is_refusal(raw_k2)
            refused_k5 = is_refusal(raw_k5)
            passed = refused_k2 and refused_k5
            status = "PASS" if passed else "FAIL"
            if not passed:
                all_passed = False
            print(f"\n  Refusal k=2: {'✓' if refused_k2 else '✗'}  |  Refusal k=5: {'✓' if refused_k5 else '✗'}")
            print(f"  {status} — {'both correctly refused' if passed else 'expected refusal not detected'}")

            results.append({
                "id": qid,
                "label": label,
                "question": question,
                "answer_k2": answer_k2,
                "answer_k5": answer_k5,
                "sources_k2": sources_k2,
                "sources_k5": sources_k5,
                "refused_k2": refused_k2,
                "refused_k5": refused_k5,
                "status": status,
                "expect_refusal": True,
            })
            continue

        # ── LLM judge ────────────────────────────────────────────────────
        try:
            verdict = judge_answers(question, answer_k2, answer_k5)
            score_k2 = verdict["score_k2"]
            score_k5 = verdict["score_k5"]
            winner_raw = verdict["winner"]
            reasoning = verdict["reasoning"]
            winner_label = {"k2": "k=2", "k5": "k=5", "tie": "Tie"}.get(winner_raw, winner_raw)
            status = "PASS"
            print(f"\n  k=2 score: {score_k2}/5 | k=5 score: {score_k5}/5 | Winner: {winner_label}")
            print(f"  Judge: {reasoning}")
        except Exception as exc:
            score_k2 = score_k5 = winner_raw = reasoning = winner_label = None
            status = "FAIL"
            all_passed = False
            print(f"\n  FAIL — Judge error: {exc}")

        results.append({
            "id": qid,
            "label": label,
            "question": question,
            "answer_k2": answer_k2,
            "answer_k5": answer_k5,
            "sources_k2": sources_k2,
            "sources_k5": sources_k5,
            "score_k2": score_k2,
            "score_k5": score_k5,
            "winner": winner_raw,
            "reasoning": reasoning,
            "status": status,
            "expect_refusal": False,
        })

    # ── Summary ──────────────────────────────────────────────────────────
    passed = sum(1 for r in results if r["status"] == "PASS")
    total = len(results)
    print("\n" + "=" * 70)
    print(f"Result: {passed}/{total} passed")
    print("=" * 70)

    write_report(results)
    print(f"\nReport written to: {REPORT_PATH}")

    if not all_passed:
        sys.exit(1)


# ---------------------------------------------------------------------------
# Report writer
# ---------------------------------------------------------------------------

def write_report(results: list[dict]) -> None:
    today = date.today().isoformat()
    lines = [
        "# TC004 — Top-K Retrieval Quality Comparison Report\n",
        f"**Date:** {today}  ",
        "**Retrieval depths tested:** k=2 vs k=5  ",
        "**LLM judge:** gpt-4o-mini  ",
        "**Questions:** 3 Simple Python · 3 Detailed Python · 1 Off-topic refusal\n",
        "---\n",
        "## Summary\n",
        "| ID | Label | Question | k=2 Score | k=5 Score | Winner | Status |",
        "|---|---|---|---|---|---|---|",
    ]

    for r in results:
        if r.get("expect_refusal"):
            k2_score = "Refusal ✓" if r.get("refused_k2") else "Refusal ✗"
            k5_score = "Refusal ✓" if r.get("refused_k5") else "Refusal ✗"
            winner = "—"
        else:
            k2_score = f"{r.get('score_k2', '—')}/5"
            k5_score = f"{r.get('score_k5', '—')}/5"
            winner_raw = r.get("winner", "—")
            winner = {"k2": "k=2", "k5": "k=5", "tie": "Tie"}.get(winner_raw, winner_raw or "—")

        q_short = r["question"][:55] + "…" if len(r["question"]) > 55 else r["question"]
        status = "✅ PASS" if r["status"] == "PASS" else "❌ FAIL"
        lines.append(
            f"| {r['id']} | {r['label']} | {q_short} | {k2_score} | {k5_score} | {winner} | {status} |"
        )

    lines += ["\n---\n", "## Per-Question Detail\n"]

    for r in results:
        lines.append(f"### {r['id']} ({r['label']}) — {r['question']}\n")
        lines.append(f"**Status:** {'✅ PASS' if r['status'] == 'PASS' else '❌ FAIL'}  \n")

        if r.get("expect_refusal"):
            lines.append(f"**Type:** Off-topic refusal check  ")
            lines.append(f"**k=2 refused:** {r.get('refused_k2')}  ")
            lines.append(f"**k=5 refused:** {r.get('refused_k5')}  \n")
            lines.append(f"**k=2 raw output:**\n> {r.get('answer_k2', '(error)')}\n")
            lines.append(f"**k=5 raw output:**\n> {r.get('answer_k5', '(error)')}\n")
        else:
            winner_raw = r.get("winner", "—")
            winner = {"k2": "k=2", "k5": "k=5", "tie": "Tie"}.get(winner_raw, winner_raw or "—")
            lines.append(f"**k=2 Score:** {r.get('score_k2', '—')}/5  ")
            lines.append(f"**k=5 Score:** {r.get('score_k5', '—')}/5  ")
            lines.append(f"**Winner:** {winner}  ")
            lines.append(f"**Judge Reasoning:** {r.get('reasoning', '—')}  \n")

            lines.append("**k=2 Answer:**")
            lines.append(f"> {r.get('answer_k2', '(error)')}\n")
            lines.append("**k=2 Sources:**")
            for src_line in (r.get("sources_k2") or "(none)").splitlines():
                lines.append(f"> {src_line}")
            lines.append("")

            lines.append("**k=5 Answer:**")
            lines.append(f"> {r.get('answer_k5', '(error)')}\n")
            lines.append("**k=5 Sources:**")
            for src_line in (r.get("sources_k5") or "(none)").splitlines():
                lines.append(f"> {src_line}")
            lines.append("")

        lines.append("---\n")

    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    run_tests()
