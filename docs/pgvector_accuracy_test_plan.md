# Goal Description

Create a Testsprite test script to systematically verify the accuracy of the new pgvector RAG implementation. The test will evaluate 6 specific questions against their expected answers from the original layout to ensure the new vector similarity search retrieves relevant context and the LLM provides high-quality answers.

---

## Test Dataset

Each entry below defines a question, the `source_id(s)` to scope the query, and a hand-written reference answer that serves as the "Original Answer" baseline in the comparison report.

> **Note:** "Original Answer" means a manually written reference answer that represents the expected student-quality explanation. It is embedded directly in the test script as a string constant — not retrieved from any external system.

| # | Question | Source ID(s) | Reference Answer (Original) |
|---|---|---|---|
| Q1 | What is Computer Science? | `a727e300-1381-4716-8239-7b9dedde8f72` | Computer science is the study and theory of programming, numerical analysis, data processing, and the design of computer systems, with a central emphasis on algorithms. In plain language: it develops the methods (algorithms) and systems that let computers solve problems and supports many other fields—like data science, computational science, and information science—by providing tools for managing and analyzing information. |
| Q2 | What is Python? | `a727e300-1381-4716-8239-7b9dedde8f72` | Python is a popular, general-purpose programming language. It has a concise, straightforward syntax and an extensive Standard Library plus many third-party libraries (for example Pandas, Spotipy) that make it useful for many kinds of programs—from data analysis to web and multimedia—and it's widely used by organizations such as Google, Apple, and NASA. |
| Q3 | What is an Expression in Python? | `a727e300-1381-4716-8239-7b9dedde8f72` | An expression in Python is a piece of code that represents a single value to be computed. Expressions combine literals, variables, and operators (for example, 3*x - 5 evaluates to 7 when x is 4) and can be as simple as a single value (the 5 in x = 5) or arbitrarily long calculations. |
| Q4 | What is Machine Learning? | `a727e300-1381-4716-8239-7b9dedde8f72` | Machine Learning is a subset of artificial intelligence that uses algorithms and data to enable computers to learn and make predictions or decisions, mimicking the way humans learn. In plain terms, ML analyzes large datasets to find patterns (for example in web browser histories) and then uses those patterns for tasks like recommending products, targeting ads, or detecting fraudulent transactions. |
| Q5 | What is a Turing Machine? | `a727e300-1381-4716-8239-7b9dedde8f72` | A Turing machine is a simple mathematical model of a general-purpose computer: it has an infinitely long tape of symbol cells, a head that can read and write symbols, a state register, and a list of instructions (transition rules). In plain terms, it formalizes the idea of an algorithm and computation—despite its simplicity it captures the power of real computers (Turing-completeness) and underlies theoretical questions about what can or cannot be computed (for example, the halting problem). |
| Q6 | How fast is Earth moving? | `a727e300-1381-4716-8239-7b9dedde8f72` | *(N/A — expected refusal: "I can't determine how fast Earth is moving from these materials. The study excerpts discuss computer science topics and do not include any information about Earth's motion.")* |

> If any question requires a different source, replace the `source_id` in that row.

---

## Proposed Changes

### Testsprite Tests

#### [NEW] TC003_post_api_v1_ask_evaluates_pgvector_accuracy.py
Create a new standalone Python test script in `backend/testsprite_tests/`.

- **Dataset:** The 6 questions and reference answers defined in the table above, embedded as constants in the script.
- **Execution:** For each question, send `POST /api/v1/ask` with the question text and its mapped `source_id(s)`.
- **LLM Judge:** Use `gpt-4o-mini` (same model as the RAG pipeline) with the prompt structure below to evaluate answer quality on a 1–5 student comprehension scale.
- **Output:** Write a markdown comparison report to `backend/testsprite_tests/TC003_accuracy_report.md` in addition to printing to stdout.

#### LLM Judge Prompt Structure

```
You are evaluating the quality of two study-aid answers from the perspective of a college student.

Question: {question}

Answer A (Reference): {reference_answer}
Answer B (pgvector RAG): {rag_answer}

Rate each answer on a 1–5 scale for student comprehension value:
- 5: Complete, clear, and correct
- 4: Mostly correct with minor gaps
- 3: Partially correct or unclear
- 2: Mostly incorrect or confusing
- 1: Completely wrong or unhelpful

Return JSON: {"score_a": int, "score_b": int, "winner": "A" | "B" | "tie", "reasoning": str}
```

#### Validation

1. **HTTP check:** Assert `status_code == 200` and response is valid JSON with `answer` (non-empty string) and `citations` (list).
2. **Quality check (Q1–Q5):** LLM judge runs and returns valid JSON. Log the scores and reasoning.
3. **Refusal check (Q6 — "How fast is Earth moving?"):**
   - Assert the answer does **not** contain a numeric speed value (regex: `\d+[\.,]?\d*\s*(km|miles|mph|km/h|m/s)`).
   - Assert the answer **does** contain a refusal phrase — one of: `"not mentioned"`, `"cannot determine"`, `"no information"`, `"not covered"`, `"don't have"`, `"not found in"` (case-insensitive).
4. **Report:** Write `TC003_accuracy_report.md` with:
   - Per-question section: Question, Reference Answer, pgvector Answer, Judge scores, Winner, Reasoning
   - Summary table: question index, score_a, score_b, winner

---

## Verification Plan

### Automated Tests
Run the new testsprite test script to verify the pgvector accuracy and review the comparison output:
```bash
python backend/testsprite_tests/TC003_post_api_v1_ask_evaluates_pgvector_accuracy.py
```

Then review the generated report:
```bash
open backend/testsprite_tests/TC003_accuracy_report.md
```

### Cost Note
Each test run invokes `gpt-4o-mini` once per question (6 judge calls + 6 RAG calls = 12 API calls total). At current pricing this is approximately $0.01–$0.03 per full run.
