# AI tutor layer
# answer.py responsibility
# Accept a user question
# Call retrieve.py to get top chunks
# Build a prompt
# Call OpenAI Chat API
# Return an answer with sources

from openai import OpenAI
from retrieve import retrieve_top_k

client = OpenAI()

SYSTEM_PROMPT = """
You are an AI tutor.
Answer the question using ONLY the provided context.
If the answer is not in the context, say you don't know.
Cite sources by filename and page numbers.
"""

def answer_question(question: str, k: int = 5):
    results = retrieve_top_k(question, k=k)

    context = "\n\n".join(
        f"[{r['source_file']} pages {r['start_page']}-{r['end_page']}]\n{r['text']}"
        for r in results
    )

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}
        ]
    )

    return response.choices[0].message.content
