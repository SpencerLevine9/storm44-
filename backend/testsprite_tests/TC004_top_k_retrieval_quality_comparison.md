# TC004 — Top-K Retrieval Quality Comparison (k=2 vs k=5)

**Type:** Backend · Retrieval Quality  
**File:** `TC004_top_k_retrieval_quality_comparison.py`  
**Module under test:** `machine_learning/ingest_pipeline/store/answer.py`  
**LLM judge:** gpt-4o-mini  
**Questions:** 3 Simple Python · 3 Detailed Python · 1 Off-topic refusal

---

## Objective

Compare retrieval quality when `answer_question()` is called with `k=2` (top-2 chunks) versus `k=5` (top-5 chunks) across a mix of simple and detailed Python questions.

Both runs draw from a candidate pool of 20 via `top_k()` and rerank before returning results. `build_context()` caps the LLM context at `MAX_CONTEXT_RESULTS=2` regardless of `k`, so the comparison reveals whether a wider candidate pool surfaces meaningfully different top-2 chunks through reranking, or whether the two settings produce equivalent answers. Source citation breadth also differs: `build_sources()` lists all `k` returned chunks, so k=5 exposes up to 5 citations.

---

## Test Cases

### Q1 (Simple) — What is a variable in Python?

**Expected behavior:** Both k=2 and k=5 return a clear, grounded definition of a Python variable. The answer should mention assignment syntax (e.g. `x = 5`) and the concept of storing a value.  
**Expect refusal:** No

---

### Q2 (Simple) — What is a list in Python?

**Expected behavior:** Both k=2 and k=5 return a correct description of a Python list as an ordered, mutable sequence. May include examples of list literals or indexing.  
**Expect refusal:** No

---

### Q3 (Simple) — How do you write a for loop in Python?

**Expected behavior:** Both k=2 and k=5 return an answer that covers the `for <var> in <iterable>:` syntax and gives a brief usage example. Should not describe while loops.  
**Expect refusal:** No

---

### Q4 (Detailed) — What is the difference between mutable and immutable data types in Python, and can you give examples of each?

**Expected behavior:** Both k=2 and k=5 return an answer distinguishing mutability. Immutable examples expected: `int`, `str`, `tuple`. Mutable examples expected: `list`, `dict`. k=5 may surface additional supporting chunks with more examples.  
**Expect refusal:** No

---

### Q5 (Detailed) — How do functions work in Python? Explain parameters, return values, and how to define and call a function.

**Expected behavior:** Both k=2 and k=5 cover `def`, parameters/arguments, `return`, and a call-site example. k=5 may retrieve an additional chunk covering edge cases (default args, multiple returns).  
**Expect refusal:** No

---

### Q6 (Detailed) — What is the difference between a while loop and a for loop in Python, and when should you use each one?

**Expected behavior:** Both k=2 and k=5 correctly distinguish iteration-count-known (for) vs condition-based (while) usage. Answer should not conflate the two.  
**Expect refusal:** No

---

### Q7 (Refusal) — What is the boiling point of water in Celsius?

**Expected behavior:** Both k=2 and k=5 must return a refusal — the question is outside the uploaded study materials. Neither answer should contain a numeric temperature value.  
**Expect refusal:** Yes (both k values)

---

## Pass / Fail Criteria

| Condition | Criterion |
|---|---|
| Q1–Q6 HTTP / runtime | No exception raised; non-empty answer string returned |
| Q1–Q6 quality | LLM judge awards ≥ 3/5 to both k=2 and k=5 answers |
| Q7 refusal | Both k=2 and k=5 answers contain a recognized refusal phrase and no boiling-point value |
| Overall | All 7 questions meet their criteria → `PASS`; any failure → `FAIL` + `sys.exit(1)` |

---

## Output

Full answer text and source citations for every question at both k values are printed to stdout and written to `TC004_retrieval_comparison_report.md` in the same directory.

---

## Notes

- The sentence-transformer model (`all-MiniLM-L6-v2`) is loaded on first call; allow ~60 s for the initial warm-up.
- Set `OPENAI_API_KEY` in `backend/.env` before running.
- Run from the repo root: `python -m backend.testsprite_tests.TC004_top_k_retrieval_quality_comparison`
