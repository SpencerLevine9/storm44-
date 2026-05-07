from __future__ import annotations

import os
from typing import Any, Dict, List
import json

from openai import OpenAI
from .retrieve import top_k, extract_target_phrase, query_keywords, get_chunks_for_sources
import re

MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-5-mini")

MAX_CONTEXT_RESULTS = 2
MAX_CHARS_PER_CHUNK = 500

REFUSAL_MESSAGE = (
    "I can only answer questions grounded in the uploaded materials. "
    "Try asking about topics like computational thinking, Python, computer science, or machine learning."
)

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

# reduces the amount of retrieved material sent into the final answer model while keeping the top evidence.
# implmented this for Data usage / processing minimization and speedup on repeated queries that hit the same chunks, and to improve answer quality by only including the most relevant sources in the context.
def trim_chunk_text(text: str, max_chars: int = MAX_CHARS_PER_CHUNK) -> str:
    text = (text or "").strip()
    if len(text) <= max_chars:
        return text

    trimmed = text[:max_chars]
    last_period = trimmed.rfind(". ")
    if last_period > 150:
        return trimmed[:last_period + 1].strip()

    return trimmed.rstrip() + "..."


def build_context(results: List[Dict[str, Any]]) -> str:
    chunks = []

    for i, r in enumerate(results[:MAX_CONTEXT_RESULTS], start=1):
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

        text = trim_chunk_text(r.get("text") or "")
        chunks.append(f"{source_label}\n{text}")

    return "\n\n" + ("\n\n".join(chunks))

# part of process of backend pdf/video -> generate flashcards and quizzes

def build_study_tool_context(
    results: List[Dict[str, Any]],
    max_results: int = 8,
    max_chars_per_chunk: int = 900,
) -> str:
    chunks = []

    for i, r in enumerate(results[:max_results], start=1):
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

        text = trim_chunk_text(r.get("text") or "", max_chars=max_chars_per_chunk)
        chunks.append(f"{source_label}\n{text}")

    return "\n\n" + "\n\n".join(chunks)


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
        return REFUSAL_MESSAGE

    return answer

def generate_flashcards_from_context(topic: str, context: str, count: int) -> List[Dict[str, str]]:
    client = OpenAI()

    system_prompt = """
You are Storm44, an AI study assistant.

Generate study flashcards using ONLY the provided study context.

Rules:
- Use only the provided context.
- Do not invent facts.
- Make the flashcards clear, concise, and useful for studying.
- Each flashcard must have:
  - "front": a term, concept, or question
  - "back": a short answer or definition
- Return valid JSON only.
- Do not include markdown or extra text.
- The JSON must match this shape:
{
  "cards": [
    {
      "front": "string",
      "back": "string"
    }
  ]
}
""".strip()

    user_prompt = f"""
Topic:
{topic}

Study Context:
{context}

Generate exactly {count} flashcards.
""".strip()

    response = client.responses.create(
        model=MODEL_NAME,
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    output_text = (response.output_text or "").strip()
    if not output_text:
        return []

    try:
        parsed = json.loads(output_text)
        cards = parsed.get("cards", [])
        if not isinstance(cards, list):
            return []

        cleaned_cards = []
        for card in cards[:count]:
            front = str(card.get("front", "")).strip()
            back = str(card.get("back", "")).strip()
            if front and back:
                cleaned_cards.append({
                    "front": front,
                    "back": back,
                })

        return cleaned_cards
    except Exception:
        return []


def generate_quiz_from_context(topic: str, context: str, count: int) -> List[Dict[str, Any]]:
    client = OpenAI()

    system_prompt = """
You are Storm44, an AI study assistant.

Generate multiple-choice quiz questions using ONLY the provided study context.

Rules:
- Use only the provided context.
- Do not invent facts.
- Each question must have exactly 4 unique answer options.
- "correct_answer" must exactly match one of the 4 options.
- Include a short explanation.
- Return valid JSON only.
- Do not include markdown or extra text.
- The JSON must match this shape:
{
  "questions": [
    {
      "question": "string",
      "options": ["string", "string", "string", "string"],
      "correct_answer": "string",
      "explanation": "string"
    }
  ]
}
""".strip()

    user_prompt = f"""
Topic:
{topic}

Study Context:
{context}

Generate exactly {count} quiz questions.
""".strip()

    response = client.responses.create(
        model=MODEL_NAME,
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    output_text = (response.output_text or "").strip()
    if not output_text:
        return []

    try:
        parsed = json.loads(output_text)
        questions = parsed.get("questions", [])
        if not isinstance(questions, list):
            return []

        cleaned_questions = []
        for q in questions[:count]:
            question = str(q.get("question", "")).strip()
            options = q.get("options", [])
            correct_answer = str(q.get("correct_answer", "")).strip()
            explanation = str(q.get("explanation", "")).strip()

            if not question or not explanation:
                continue
            if not isinstance(options, list) or len(options) != 4:
                continue

            cleaned_options = [str(opt).strip() for opt in options]
            if len(set(cleaned_options)) != 4:
                continue
            if correct_answer not in cleaned_options:
                continue

            cleaned_questions.append({
                "question": question,
                "options": cleaned_options,
                "correct_answer": correct_answer,
                "explanation": explanation,
            })

        return cleaned_questions
    except Exception:
        return []
    


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
            "answer": REFUSAL_MESSAGE,
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

def generate_flashcards_structured(
    topic: str,
    source_ids: List[str] | None = None,
    count: int = 10,
    k: int = 3,
) -> Dict[str, Any]:
    source_ids = source_ids or []

    if source_ids:
        results = get_chunks_for_sources(source_ids, max_chunks_per_source=8)
    else:
        results = top_k(topic, k=k)

    if not results:
        return {
            "cards": [],
        }

    # Only use rerank threshold when we are doing query-based retrieval.
    # If source_ids were provided, the source itself is the grounding signal.
    if not source_ids:
        best_rerank = results[0].get("rerank_score", 0.0) or 0.0
        if best_rerank < 8.5:
            return {
                "cards": [],
            }

    context = build_study_tool_context(results)
    cards = generate_flashcards_from_context(topic, context, count)

    return {
        "cards": cards,
    }


def generate_quiz_structured(
    topic: str,
    source_ids: List[str] | None = None,
    count: int = 10,
    k: int = 3,
) -> Dict[str, Any]:
    source_ids = source_ids or []

    if source_ids:
        results = get_chunks_for_sources(source_ids, max_chunks_per_source=8)
    else:
        results = top_k(topic, k=k)

    if not results:
        return {
            "questions": [],
        }

    # Only use rerank threshold when we are doing query-based retrieval.
    # If source_ids were provided, the source itself is the grounding signal.
    if not source_ids:
        best_rerank = results[0].get("rerank_score", 0.0) or 0.0
        if best_rerank < 8.5:
            return {
                "questions": [],
            }

    context = build_study_tool_context(results)
    questions = generate_quiz_from_context(topic, context, count)

    return {
        "questions": questions,
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


def _count_term_occurrences(term: str, text: str) -> int:
    term = _normalize_for_match(term)
    text = _normalize_for_match(text)
    if not term or not text:
        return 0
    return len(re.findall(rf"\b{re.escape(term)}s?\b", text))


def _has_definition_sentence(term: str, text: str) -> bool:
    term = _normalize_for_match(term)
    if not term:
        return False

    sentences = re.split(r'(?<=[.!?])\s+', text)
    definitional_patterns = [
        r"\bis\b",
        r"\bare\b",
        r"\brefers to\b",
        r"\bmeans\b",
        r"\bis defined as\b",
        r"\bcan be\b",
    ]

    for sent in sentences:
        s = _normalize_for_match(sent)
        if not re.search(rf"\b{re.escape(term)}s?\b", s):
            continue
        if any(re.search(pat, s) for pat in definitional_patterns):
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
    text_blob = " ".join((r.get("text") or "") for r in results[:2])
    meta_blob = " ".join(
        " ".join(
            filter(
                None,
                [
                    r.get("source_file") or "",
                    r.get("title") or "",
                ],
            )
        )
        for r in results[:2]
    )

    core_topic = strip_prompt_leadin(question)
    raw_terms = list(dict.fromkeys(query_keywords(core_topic)))

    if not raw_terms:
        return False

    generic_context_terms = {"python", "java", "javascript", "programming"}
    nongeneric_terms = [t for t in raw_terms if t not in generic_context_terms]
    generic_terms = [t for t in raw_terms if t in generic_context_terms]

    matched_nongeneric = [t for t in nongeneric_terms if _term_in_text(t, text_blob)]
    matched_generic = [
        t for t in generic_terms
        if _term_in_text(t, text_blob) or _term_in_text(t, meta_blob)
    ]

    # Case 1: single-topic broad prompt like "tell me about python"
    if len(raw_terms) == 1:
        term = raw_terms[0]
        in_text = _term_in_text(term, text_blob)
        in_meta = _term_in_text(term, meta_blob)
        occurrences = _count_term_occurrences(term, text_blob)
        has_definition = _has_definition_sentence(term, text_blob)

        return (in_text or in_meta) and (occurrences >= 2 or has_definition)

    # Case 2: scoped academic prompt like "tell me about expressions in python"
    # Allow one real concept term if the course-context term is grounded by source metadata.
    if len(matched_nongeneric) >= 2:
        return True

    if len(matched_nongeneric) == 1:
        concept = matched_nongeneric[0]
        if matched_generic or _has_definition_sentence(concept, text_blob):
            return True

    return False



def answer_question_structured(question: str, k: int = 3) -> Dict[str, Any]:
    results = top_k(question, k=k)


# Backend version of answer_question().
# Returns structured JSON-like data instead of one formatted string.

    if not results:
        return {
            "answer": REFUSAL_MESSAGE,
            "citations": [],
        }

    
    best_rerank = results[0].get("rerank_score", 0.0) or 0.0
    q_lower = question.lower().strip()

    has_definition_support = has_enough_definition_support(question, results)
    has_topic_support = has_enough_topic_support(question, results)

    if best_rerank < 8.5:
        return {
            "answer": REFUSAL_MESSAGE,
            "citations": [],
        }

    if is_definition_style_question(q_lower) and not has_definition_support:
        return {
            "answer": REFUSAL_MESSAGE,
            "citations": [],
        }

    if is_broad_topic_prompt(q_lower) and not has_topic_support:
        return {
            "answer": REFUSAL_MESSAGE,
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