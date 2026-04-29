# TC004 — top_k=2 vs top_k=5 Retrieval Quality Report

**Date:** 2026-04-29  
**Endpoint:** `POST /api/v1/ask` at `http://127.0.0.1:8000`  
**Python Source UUIDs:**
- `038c02b0-f624-4e93-8959-562424a89c78`
- `7cce7f29-993c-4a02-a9e5-28d2c774bbe5`

**LLM Judge:** `gpt-4o-mini` (1 = poor, 5 = excellent)  
**Test Status:** ✅ PASSED

---

## Per-Question Results

### Q1 — "What is a variable in Python?" *(Simple)*

**top_k=2 Answer:**  
A variable in Python is a name that refers to a value stored in memory. You give a variable a value with the assignment operator `=` (e.g., `age = 6` or `birth = "May 15"`), where the left side is the variable name and the right side is the value.

**top_k=2 Citations:**
- Source `038c02b0` / Chunk `dc0a6b46` — *"do you live?") b. city = "London" c. print..."*
- Source `038c02b0` / Chunk `1bff7b37` — *"memory locations. Ex: age refers to a person's age..."*

**top_k=5 Answer:**  
A variable in Python is a name that refers to a memory location holding a value. You create or change it with the assignment operator `=` (for example, `age = 6` or `birth = "May 15"`), where the left side is the variable name and the right side is the value assigned.

**top_k=5 Citations:** 5 chunks (same top 2 + 3 additional chunks from same source)

| | top_k=2 | top_k=5 |
|---|---|---|
| LLM Score | 3 | 3 |
| **Winner** | **Tie** | |

---

### Q2 — "What is a list in Python?" *(Simple)*

**top_k=2 Answer:**  
I cannot answer this question from the provided study materials. Please ask about topics covered in your uploaded sources.

**top_k=5 Answer:**  
I cannot answer this question from the provided study materials. Please ask about topics covered in your uploaded sources.

> ⚠️ Both top_k values returned a refusal. The ingested sources (Chapters 1–2: intro and expressions) do not contain content on Python lists.

| | top_k=2 | top_k=5 |
|---|---|---|
| LLM Score | 2 | 3 |
| **Winner** | **top_k=5** | |

---

### Q3 — "How do you write a for loop in Python?" *(Simple)*

**top_k=2 Answer:**  
I cannot answer this question from the provided study materials. Please ask about topics covered in your uploaded sources.

**top_k=5 Answer:**  
I cannot answer this question from the provided study materials. Please ask about topics covered in your uploaded sources.

> ⚠️ Both top_k values returned a refusal. The ingested sources do not cover for loops.

| | top_k=2 | top_k=5 |
|---|---|---|
| LLM Score | 2 | 3 |
| **Winner** | **top_k=5** | |

---

### Q4 — "What is the difference between mutable and immutable data types in Python, and can you give examples of each?" *(Detailed)*

**top_k=2 Answer:**  
I can't fully answer — these sources don't define "mutable" vs "immutable" or give examples of mutable types; they only imply that strings and numeric types behave as immutable. The context shows string concatenation "results in a new string" and numeric operations produce new numeric values rather than changing an existing value, which indicates strings and numbers are immutable; no examples of types that can be changed in place are given.

**top_k=5 Answer:**  
I cannot answer this question from the provided study materials. Please ask about topics covered in your uploaded sources.

> Notable: `top_k=2` retrieved chunks with partial relevance (type/operator descriptions) and generated a partial answer, scoring higher than `top_k=5` which retrieved noisier chunks and fell back to refusal.

| | top_k=2 | top_k=5 |
|---|---|---|
| LLM Score | 3 | 2 |
| **Winner** | **top_k=2** | |

---

### Q5 — "How do functions work in Python? Explain parameters, return values, and how to define and call a function." *(Detailed)*

**top_k=2 Answer:**  
I cannot answer this question from the provided study materials. Please ask about topics covered in your uploaded sources.

**top_k=5 Answer:**  
I cannot answer this question from the provided study materials. Please ask about topics covered in your uploaded sources.

> ⚠️ Both top_k values returned a refusal. The ingested sources do not cover function definitions.

| | top_k=2 | top_k=5 |
|---|---|---|
| LLM Score | 2 | 3 |
| **Winner** | **top_k=5** | |

---

### Q6 — "What is the difference between a while loop and a for loop in Python, and when should you use each one?" *(Detailed)*

**top_k=2 Answer:**  
I cannot answer this question from the provided study materials. Please ask about topics covered in your uploaded sources.

**top_k=5 Answer:**  
I cannot answer this question from the provided study materials. Please ask about topics covered in your uploaded sources.

> ⚠️ Both top_k values returned a refusal. The ingested sources do not cover while loops or for loops.

| | top_k=2 | top_k=5 |
|---|---|---|
| LLM Score | 2 | 1 |
| **Winner** | **top_k=2** | |

---

### Q7 — "What is the boiling point of water in Celsius?" *(Off-topic refusal check)*

**top_k=2 Answer:**  
I cannot answer this question from the provided study materials. Please ask about topics covered in your uploaded sources.

**top_k=5 Answer:**  
I cannot answer this question from the provided study materials. Please ask about topics covered in your uploaded sources.

> ✅ Both top_k values correctly refused the off-topic question.

---

## Summary Table

| Q# | Question (abbreviated) | top_k=2 Score | top_k=5 Score | Winner |
|----|------------------------|:---:|:---:|--------|
| Q1 | What is a variable? | 3 | 3 | Tie |
| Q2 | What is a list? | 2 | 3 | top_k=5 |
| Q3 | How do you write a for loop? | 2 | 3 | top_k=5 |
| Q4 | Mutable vs immutable? | 3 | 2 | top_k=2 |
| Q5 | How do functions work? | 2 | 3 | top_k=5 |
| Q6 | While loop vs for loop? | 2 | 1 | top_k=2 |
| Q7 | Boiling point of water? | ✅ Refused | ✅ Refused | N/A |

**top_k=5 wins:** 3 (Q2, Q3, Q5)  
**top_k=2 wins:** 2 (Q4, Q6)  
**Ties:** 1 (Q1)

---

## Analysis & Findings

### 1. Limited database coverage is the dominant issue
Only Q1 received a substantive answer. Q2–Q6 all returned refusals at both `top_k=2` and `top_k=5` because the ingested sources only cover **Chapter 1 (intro, variables, I/O) and Chapter 2 (expressions, data types, math)**. Topics like lists, loops, and functions are not present in the vector store, making retrieval quality comparison largely moot for those questions.

### 2. top_k=5 has a marginal edge on "tie-breaker" refusals
When both k values return the same refusal text, the LLM judge still differentiates slightly — `top_k=5` scored higher on Q2, Q3, and Q5 (3 vs 2). This may reflect minor variation in cited snippets providing slightly more context even when the answer is a refusal.

### 3. top_k=2 can outperform top_k=5 for narrow queries
Q4 (mutable/immutable) is the most interesting case: `top_k=2` retrieved the two most relevant chunks (type descriptions and operator table) and assembled a partial answer, while `top_k=5` pulled in noisier chunks that lowered the answer quality below the refusal threshold. This suggests **a tighter retrieval window can be better for focused definitional queries**.

### 4. Off-topic refusal (Q7) works correctly after backend fix
A system-prompt rule was added to `generate_grounded_answer` in `answer.py` to explicitly refuse questions not answerable from the study context. Both `top_k=2` and `top_k=5` correctly returned the refusal message for the boiling point question.

### 5. Recommendation: ingest more source material
The primary actionable finding is that the vector store needs chapters covering lists, loops, functions, and mutable/immutable types before `top_k` comparison becomes meaningful. Once those chapters are ingested, re-running TC004 will produce substantive answers for Q2–Q6 and provide a more statistically significant comparison.
