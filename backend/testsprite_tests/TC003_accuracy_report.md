# TC003 — pgvector RAG Accuracy Report

**Date:** 2026-03-24  
**Sources:** CS (2) + Python (2)  
**Model:** gpt-4o-mini (LLM judge)

---

## Summary

| ID | Question | Ref Score | RAG Score | Winner | Status |
|---|---|---|---|---|---|
| Q1 | What is Computer Science? | 5 | 4 | Reference | ✅ PASS |
| Q2 | What is Python? | 5 | 4 | Reference | ✅ PASS |
| Q3 | What is an Expression in Python? | 5 | 5 | Tie | ✅ PASS |
| Q4 | What is Machine Learning? | 5 | 4 | Reference | ✅ PASS |
| Q5 | What is a Turing Machine? | 5 | 2 | Reference | ✅ PASS |
| Q6 | How fast is Earth moving? | N/A | N/A | Refusal check | ✅ PASS |

---

## Per-Question Detail

### Q1 — What is Computer Science?

**Status:** ✅ PASS  

**Reference Score:** 5/5  
**pgvector Score:** 4/5  
**Winner:** Reference  
**Judge Reasoning:** Answer A provides a more comprehensive and clear explanation of computer science, including its focus on algorithms and its connections to other fields.  

**Reference Answer:**
> Computer science is the study and theory of programming, numerical analysis, data processing, and the design of computer systems, with a central emphasis on algorithms. In plain language: it develops the methods (algorithms) and systems that let computers solve problems and supports many other fields—like data science, computational science, and information science—by providing tools for managing and analyzing information.

**pgvector Answer:**
> Computer science is the study of computing, including all phenomena related to computers (for example, the Internet). 

In plain terms, it develops the tools and resources that help handle tasks and improve operations across many fields; one example is data science, which uses computing to manage and extract information from data (even via spreadsheets).

---

### Q2 — What is Python?

**Status:** ✅ PASS  

**Reference Score:** 5/5  
**pgvector Score:** 4/5  
**Winner:** Reference  
**Judge Reasoning:** Answer A provides a more detailed and specific overview of Python, including its syntax, library ecosystem, and application examples.  

**Reference Answer:**
> Python is a popular, general-purpose programming language. It has a concise, straightforward syntax and an extensive Standard Library plus many third-party libraries (for example Pandas, Spotipy) that make it useful for many kinds of programs—from data analysis to web and multimedia—and it's widely used by organizations such as Google, Apple, and NASA.

**pgvector Answer:**
> Python is a versatile programming language.

It supports many kinds of applications across different fields (for example, business scripts to generate reports) and is popular and useful to learn. A large supportive community creates many libraries and tools (often with "py" in their names) to extend what Python can do.

---

### Q3 — What is an Expression in Python?

**Status:** ✅ PASS  

**Reference Score:** 5/5  
**pgvector Score:** 5/5  
**Winner:** Tie  
**Judge Reasoning:** Both answers provide a clear and correct definition of an expression in Python, with examples to illustrate the concept.  

**Reference Answer:**
> An expression in Python is a piece of code that represents a single value to be computed. Expressions combine literals, variables, and operators (for example, 3*x - 5 evaluates to 7 when x is 4) and can be as simple as a single value (the 5 in x = 5) or arbitrarily long calculations.

**pgvector Answer:**
> An expression in Python is a piece of code that represents a single value to be computed. It can be as simple as a literal like 5 or as complex as 3*x - 5 (which evaluates to 7 when x is 4), and may include variables and operators; expressions can be arbitrarily long.

---

### Q4 — What is Machine Learning?

**Status:** ✅ PASS  

**Reference Score:** 5/5  
**pgvector Score:** 4/5  
**Winner:** Reference  
**Judge Reasoning:** Answer A provides a complete and clear explanation of machine learning with relevant examples, while Answer B is slightly less comprehensive.  

**Reference Answer:**
> Machine Learning is a subset of artificial intelligence that uses algorithms and data to enable computers to learn and make predictions or decisions, mimicking the way humans learn. In plain terms, ML analyzes large datasets to find patterns (for example in web browser histories) and then uses those patterns for tasks like recommending products, targeting ads, or detecting fraudulent transactions.

**pgvector Answer:**
> Machine learning is the use of algorithms to model or emulate human cognitive processes—like visual perception and decision-making—so systems can solve tasks such as image recognition. In plain terms, ML builds algorithmic architectures that let computers learn patterns and make decisions similar to how people do, for example identifying objects in images. The context here is brief and doesn’t give a full formal definition.

---

### Q5 — What is a Turing Machine?

**Status:** ✅ PASS  

**Reference Score:** 5/5  
**pgvector Score:** 2/5  
**Winner:** Reference  
**Judge Reasoning:** Answer A provides a clear and comprehensive explanation of a Turing machine, while Answer B fails to define it and is mostly unhelpful.  

**Reference Answer:**
> A Turing machine is a simple mathematical model of a general-purpose computer: it has an infinitely long tape of symbol cells, a head that can read and write symbols, a state register, and a list of instructions (transition rules). In plain terms, it formalizes the idea of an algorithm and computation—despite its simplicity it captures the power of real computers (Turing-completeness) and underlies theoretical questions about what can or cannot be computed (for example, the halting problem).

**pgvector Answer:**
> Direct answer: The study context does not define a Turing Machine.

Short explanation: The passages instead describe Turing-completeness (computational universality): most computers are considered Turing-complete because they share a fundamental model that lets them run any algorithm, and this idea is a foundational concept in theoretical computer science about how computers can solve problems.

---

### Q6 — How fast is Earth moving?

**Status:** ✅ PASS  

**Type:** Refusal check  
**Has refusal phrase:** True  
**Has speed value:** False  

**pgvector Answer:**
> I can’t answer that from the materials you gave. 

The two excerpts are about programming (a line of code) and the Y2K issue; they contain no information about Earth’s speed (rotational or orbital), so the question can’t be answered from these sources.

---
