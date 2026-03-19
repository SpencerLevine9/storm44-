from __future__ import annotations

import os
from typing import Any, Dict, List

from openai import OpenAI
from .retrieve import top_k

MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-5-mini")


def format_time(seconds: Any) -> str:
    if seconds is None:
        return "unknown"
    total_seconds = int(float(seconds))
    minutes = total_seconds // 60
    secs = total_seconds % 60
    return f"{minutes}:{secs:02d}"


def build_sources(results: List[Dict[str, Any]]) -> str:
    lines = []
    for r in results:
        if r.get("source_type") == "youtube":
            title = r.get("title") or "YouTube Video"
            url = r.get("url") or ""
            start = format_time(r.get("start_time"))
            end = format_time(r.get("end_time"))
            cid = r.get("chunk_id")
            line = f"- {title} time {start}-{end} (chunk_id={cid})"
            if url:
                line += f" — {url}"
        else:
            source_file = r.get("source_file") or "PDF"
            sp = r.get("start_page")
            ep = r.get("end_page")
            cid = r.get("chunk_id")
            line = f"- {source_file} pages {sp}-{ep} (chunk_id={cid})"
        lines.append(line)

    seen = set()
    out = []
    for line in lines:
        if line in seen:
            continue
        seen.add(line)
        out.append(line)
    return "\n".join(out)


def build_context(results: List[Dict[str, Any]]) -> str:
    chunks = []

    for i, r in enumerate(results, start=1):
        if r.get("source_type") == "youtube":
            source_label = (
                f"Source {i} | YouTube | "
                f"{r.get('title') or 'YouTube Video'} | "
                f"time {format_time(r.get('start_time'))}-{format_time(r.get('end_time'))}"
            )
        else:
            source_label = (
                f"Source {i} | PDF | "
                f"{r.get('source_file') or 'PDF'} | "
                f"pages {r.get('start_page')}-{r.get('end_page')}"
            )

        text = (r.get("text") or "").strip()
        chunks.append(f"{source_label}\n{text}")

    return "\n\n" + ("\n\n".join(chunks))


def generate_grounded_answer(question: str, context: str) -> str:
    client = OpenAI()

    system_prompt = """
You are Storm44, an AI study assistant.

Answer the user's question using ONLY the provided study context.

Rules:
- Be accurate, clear, and student-friendly.
- Start with a direct answer.
- Then give a short explanation in plain language.
- Do not sound like a textbook unless necessary.
- Do not mention "based on the provided context" or similar filler.
- Do not invent facts not supported by the context.
- If the context is incomplete or ambiguous, say so clearly.
- If multiple related concepts appear in the context, answer only the one the user asked about.
- Keep the answer concise: usually 2-4 sentences.
""".strip()

    user_prompt = f"""
Question:
{question}

Study Context:
{context}
""".strip()

    response = client.responses.create(
        model=MODEL_NAME,
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    answer = (response.output_text or "").strip()

    if not answer:
        return "I could not generate an answer from the retrieved sources."

    return answer


def answer_question(question: str, k: int = 3) -> str:
    results = top_k(question, k=k)

    if not results:
        return "Answer:\nI could not find any relevant sources.\n\nSources:\n"

    context = build_context(results)
    answer = generate_grounded_answer(question, context)
    sources = build_sources(results)

    return f"Answer:\n{answer}\n\nSources:\n{sources}"

def answer_question_structured(question: str, k: int = 3) -> Dict[str, Any]:
    results = top_k(question, k=k)

# Backend version of answer_question().
# Returns structured JSON-like data instead of one formatted string.

    if not results:
        return {
            "answer": "I could not find any relevant sources.",
            "citations": [],
        }
    context = build_context(results)
    answer = generate_grounded_answer(question, context)

    citations = []
    for r in results:
        citations.append({
            "source_id": r.get("video_id") or r.get("source_file") or "unknown",
            "chunk_id": str(r.get("chunk_id")) if r.get("chunk_id") is not None else None,
            "snippet": (r.get("text") or "")[:180],
            "start_seconds": r.get("start_time"),
            "url": r.get("url"),
        })

    return {
        "answer": answer,
        "citations": citations,
    }

def main() -> None:
    q = input("Question: ").strip()
    if not q:
        print("No question entered.")
        return

    print()
    print(answer_question(q, k=3))


if __name__ == "__main__":
    main()