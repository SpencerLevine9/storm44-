from __future__ import annotations

import os
from typing import Any, Dict, List

from openai import OpenAI
from .retrieve import top_k, extract_target_phrase, query_keywords
import re

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

# citation quality improvement helper that picks the best sentence from the chunk based on the query.

def best_snippet_for_query(query: str, text: str, max_len: int = 220) -> str:
    text = (text or "").strip()
    if not text:
        return ""

    sentences = re.split(r'(?<=[.!?])\s+', text)
    query_words = {
        w.lower()
        for w in re.findall(r"[a-zA-Z0-9_]+", query)
        if len(w) > 2
    }

    best_sentence = text[:max_len]
    best_score = -1

    for sent in sentences:
        s = sent.strip()
        if not s:
            continue
        words = set(re.findall(r"[a-zA-Z0-9_]+", s.lower()))
        score = len(query_words & words)
        if score > best_score:
            best_score = score
            best_sentence = s

    if len(best_sentence) > max_len:
        best_sentence = best_sentence[:max_len].rstrip() + "..."

    return best_sentence

# Heuristic to check if retrieved chunks have enough relevant content to support a definition-style answer.
def _normalize_for_match(text: str) -> str:
    text = (text or "").lower()
    text = re.sub(r"[^a-zA-Z0-9_ ]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _term_in_text(term: str, text: str) -> bool:
    term = _normalize_for_match(term)
    text = _normalize_for_match(text)

    if not term or not text:
        return False

    if term in text:
        return True

    # simple singular/plural tolerance
    if term.endswith("s") and term[:-1] and term[:-1] in text:
        return True
    if f"{term}s" in text:
        return True

    return False


def has_enough_definition_support(question: str, results: List[Dict[str, Any]]) -> bool:
    searchable = " ".join(
        " ".join(
            filter(
                None,
                [
                    r.get("text") or "",
                    r.get("source_file") or "",
                    r.get("title") or "",
                ],
            )
        )
        for r in results[:2]
    )

    target = extract_target_phrase(question)
    terms = query_keywords(target or question)

    # For questions like "What is an expression in Python?",
    # don't require the word "python" to appear in the chunk text.
    generic_context_terms = {"python", "java", "javascript", "programming"}
    filtered_terms = [t for t in terms if t not in generic_context_terms]
    if filtered_terms:
        terms = filtered_terms

    if not terms:
        return False

    matched = sum(1 for t in set(terms) if _term_in_text(t, searchable))

    # one core term is enough for single-concept questions
    needed = 1 if len(set(terms)) == 1 else 2
    return matched >= needed
# This is a more structured version of the answer_question function, which returns a dictionary containing the answer and a list of citations with metadata. This can be useful for frontend applications that want to display the answer and sources in a more interactive way.


# to get rid of tell me about style questions that are too broad and don't have enough support in the retrieved chunks, we can add some heuristics to detect such questions and check if the retrieved sources have enough relevant content to support a confident answer. If not, we can return a fallback answer instead of trying to generate an answer from weak sources.
def is_definition_style_question(q_lower: str) -> bool:
    return q_lower.startswith(("what is", "what are", "define", "explain"))


def is_broad_topic_prompt(q_lower: str) -> bool:
    return q_lower.startswith((
        "tell me about",
        "talk to me about",
        "what do you know about",
        "describe",
    ))


def strip_prompt_leadin(question: str) -> str:
    q = (question or "").strip()
    q_lower = q.lower()

    leadins = [
        "tell me about",
        "talk to me about",
        "what do you know about",
        "describe",
    ]

    for leadin in leadins:
        if q_lower.startswith(leadin):
            return q[len(leadin):].strip(" ?.!")

    return q.strip(" ?.!")

    
def has_enough_topic_support(question: str, results: List[Dict[str, Any]]) -> bool:
    searchable = " ".join(
        " ".join(
            filter(
                None,
                [
                    r.get("text") or "",
                    r.get("source_file") or "",
                    r.get("title") or "",
                ],
            )
        )
        for r in results[:2]
    )

    core_topic = strip_prompt_leadin(question)
    terms = query_keywords(core_topic)

    filler_terms = {
        "tell", "talk", "about", "know", "describe", "explain",
        "please", "thing", "things", "topic", "topics",
        "python", "java", "javascript", "programming",
    }
    terms = [t for t in terms if t not in filler_terms]

    unique_terms = list(set(terms))

    # Strict demo guardrail:
    # broad prompts with only one core term are too vague
    # e.g. "tell me about cooking", "what do you know about the internet"
    if len(unique_terms) < 2:
        return False

    matched = sum(1 for t in unique_terms if _term_in_text(t, searchable))
    return matched >= 2



def answer_question_structured(question: str, k: int = 3) -> Dict[str, Any]:
    results = top_k(question, k=k)


# Backend version of answer_question().
# Returns structured JSON-like data instead of one formatted string.

    if not results:
        return {
            "answer": "I could not find any relevant sources.",
            "citations": [],
        }

    
    best_rerank = results[0].get("rerank_score", 0.0) or 0.0
    q_lower = question.lower().strip()

    has_definition_support = has_enough_definition_support(question, results)
    has_topic_support = has_enough_topic_support(question, results)

    if best_rerank < 8.5:
        return {
            "answer": "I do not have enough strong support in the uploaded material to answer that confidently.",
            "citations": [],
        }

    if is_definition_style_question(q_lower) and not has_definition_support:
        return {
            "answer": "I do not have enough strong support in the uploaded material to answer that confidently.",
            "citations": [],
        }

    if is_broad_topic_prompt(q_lower) and not has_topic_support:
        return {
            "answer": "I do not have enough strong support in the uploaded material to answer that confidently.",
            "citations": [],
        }
    

    context = build_context(results)
    answer = generate_grounded_answer(question, context)

    citations = []  
    for r in results[:2]:   # Only include top 2 citations for brevity and relevance. for citation quality improvement
        citations.append({  
            "source_id": r.get("video_id") or r.get("source_file") or "unknown",
            "chunk_id": str(r.get("chunk_id")) if r.get("chunk_id") is not None else None,
            "snippet": best_snippet_for_query(question, r.get("text") or ""),
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