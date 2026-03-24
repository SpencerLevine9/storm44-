# TC003 — pgvector RAG Accuracy Report

**Date:** 2026-03-24  
**Sources:** CS (4) + Python (4)  
**Model:** gpt-5-mini (LLM judge)

---

## Summary

| ID | Question | Ref Score | RAG Score | Winner | Status |
|---|---|---|---|---|---|
| Q1 | What is Computer Science? | 5 | 4 | Reference | ✅ PASS |
| Q2 | What is Python? | 5 | 4 | Reference | ✅ PASS |
| Q3 | What is an Expression in Python? | 5 | 5 | Tie | ✅ PASS |
| Q4 | What is Machine Learning? | 5 | 5 | Tie | ✅ PASS |
| Q5 | What is a Turing Machine? | 5 | 4 | Reference | ✅ PASS |
| Q6 | How fast is Earth moving? | N/A | N/A | Refusal check | ✅ PASS |

---

## Per-Question Detail

### Q1 — What is Computer Science?

**Status:** ✅ PASS  

**Reference Score:** 5/5  
**pgvector Score:** 4/5  
**Winner:** Reference  
**Judge Reasoning:** Answer A is slightly more comprehensive and explicit about core areas like programming, numerical analysis, and systems design, while Answer B is accurate but briefer and less specific.  

**Reference Answer:**
> Computer science is the study and theory of programming, numerical analysis, data processing, and the design of computer systems, with a central emphasis on algorithms. In plain language: it develops the methods (algorithms) and systems that let computers solve problems and supports many other fields—like data science, computational science, and information science—by providing tools for managing and analyzing information.

**pgvector Answer:**
> Computer science is the study of computing, focusing on algorithms and the components that enable computers to process information. 

In plain terms, it uses foundations from engineering and mathematics to design and analyze precise sequences of instructions (algorithms) and build applications, tools, and simulations that solve problems and support many other fields like data science and computational science.

---

### Q2 — What is Python?

**Status:** ✅ PASS  

**Reference Score:** 5/5  
**pgvector Score:** 4/5  
**Winner:** Reference  
**Judge Reasoning:** Answer A is more complete and specific (mentions syntax, standard and third-party libraries, and example use cases), while B is correct but briefer and less detailed.  

**Reference Answer:**
> Python is a popular, general-purpose programming language. It has a concise, straightforward syntax and an extensive Standard Library plus many third-party libraries (for example Pandas, Spotipy) that make it useful for many kinds of programs—from data analysis to web and multimedia—and it's widely used by organizations such as Google, Apple, and NASA.

**pgvector Answer:**
> Python is a widely used, versatile programming language.

It’s popular with organizations like Google, Apple, and NASA because it has many reusable libraries (including a large Standard Library) that make it easy to build programs for many fields—business, education, science, art, and more.

---

### Q3 — What is an Expression in Python?

**Status:** ✅ PASS  

**Reference Score:** 5/5  
**pgvector Score:** 5/5  
**Winner:** Tie  
**Judge Reasoning:** Both answers are accurate, clear, and effectively equivalent in explaining what a Python expression is, so neither is superior.  

**Reference Answer:**
> An expression in Python is a piece of code that represents a single value to be computed. Expressions combine literals, variables, and operators (for example, 3*x - 5 evaluates to 7 when x is 4) and can be as simple as a single value (the 5 in x = 5) or arbitrarily long calculations.

**pgvector Answer:**
> An expression in Python is a piece of code that represents a single value to be computed. It can combine literals, variables, and operators (for example, 3*x - 5 evaluates to 7 when x is 4) and can be as simple as a single value (the literal 5 in x = 5) or a long sequence of calculations.

---

### Q4 — What is Machine Learning?

**Status:** ✅ PASS  

**Reference Score:** 5/5  
**pgvector Score:** 5/5  
**Winner:** Tie  
**Judge Reasoning:** Both answers are concise, accurate, and provide clear examples that make the core idea of machine learning understandable to a student.  

**Reference Answer:**
> Machine Learning is a subset of artificial intelligence that uses algorithms and data to enable computers to learn and make predictions or decisions, mimicking the way humans learn. In plain terms, ML analyzes large datasets to find patterns (for example in web browser histories) and then uses those patterns for tasks like recommending products, targeting ads, or detecting fraudulent transactions.

**pgvector Answer:**
> Machine learning is a subset of artificial intelligence that uses algorithms and data to enable computers to learn, mimicking how humans learn. It finds patterns in large datasets so systems can perform tasks—like fraud detection, product recommendations, targeted advertising, or image recognition—without being explicitly programmed with strict rules.

---

### Q5 — What is a Turing Machine?

**Status:** ✅ PASS  

**Reference Score:** 5/5  
**pgvector Score:** 4/5  
**Winner:** Reference  
**Judge Reasoning:** A gives a clear, specific description of the machine components and theoretical implications, while B is correct but briefer and omits key details (tape, head, states, transition rules).  

**Reference Answer:**
> A Turing machine is a simple mathematical model of a general-purpose computer: it has an infinitely long tape of symbol cells, a head that can read and write symbols, a state register, and a list of instructions (transition rules). In plain terms, it formalizes the idea of an algorithm and computation—despite its simplicity it captures the power of real computers (Turing-completeness) and underlies theoretical questions about what can or cannot be computed (for example, the halting problem).

**pgvector Answer:**
> A Turing machine is a formal mathematical model of algorithm and computation introduced by Alan Turing. 

It serves as the foundational theoretical model in computer science for defining what it means to compute: representing programs as symbols and instructions and showing how a machine can store and manipulate data, which underlies the notion of Turing-completeness (the ability to run any algorithm).

---

### Q6 — How fast is Earth moving?

**Status:** ✅ PASS  

**Type:** Refusal check  
**Has refusal phrase:** True  
**Has speed value:** False  

**pgvector Answer:**
> I can’t determine how fast Earth is moving from the materials you provided. The study pages cover programming exercises and a note about Y2K but include no information on Earth’s rotation, orbital, or galactic velocities — tell me which motion you mean (rotation, orbit around the Sun, motion through the galaxy, etc.) or provide relevant data if you want a numeric answer.

---
