# Storm44 — ProductSpec.md

## 1) Product Summary
Storm44 is a free, AI-powered study workspace that turns user-provided materials (YouTube links, PDFs, and notes) into **organized notes, flashcards, quizzes, and a small learning game**, with an **AI Tutor (chat)** that provides **traceable citations back to sources**. :contentReference[oaicite:0]{index=0}

---

## 2) Target Users
### Primary MVP user
**Deadline Crammer (college student)**: heavy course load, time-constrained, needs fast answers they can verify (citations). (Derived from project context + citations-first UI requirement.) :contentReference[oaicite:1]{index=1}

---

## 3) Problem
Learners waste time manually turning materials into practice content, and don’t trust AI outputs without citations. Storm44 solves this by generating study assets directly from the user’s sources and letting them verify claims via citations. :contentReference[oaicite:2]{index=2}

---

## 4) Goals & Success Metrics (MVP)
### Goals
- Convert sources into a **3-panel “notebook” workspace** (Sources / Chat / Study Tools). :contentReference[oaicite:3]{index=3}
- Provide **chat responses with clickable citations** that open the relevant source excerpt. :contentReference[oaicite:4]{index=4}
- Generate **flashcards**, **MCQ quizzes**, and **one mini-game** from selected sources. :contentReference[oaicite:5]{index=5}
- Keep UI responsive for long chats and many sources (virtualization, lazy loading). :contentReference[oaicite:6]{index=6}

### Success metrics (example targets)
- Time to first useful answer: < 2 minutes
- “Can I verify this claim quickly?” → Yes (page/timestamp/source excerpt)
- Smooth performance with long chats and many sources (e.g., 500+ messages)

---

## 5) MVP Scope (P0)

## 5.1 Workspace Layout (3 Panels)
- Left: **Sources** (collapsible, preview, selection for chat scope)
- Center: **Chat** (streaming responses + citations)
- Right: **Study Tools** (Flashcards / Quizzes / Mini-game), tabbed, collapsible :contentReference[oaicite:7]{index=7}

### Panel behavior
- Desktop: panels resizable via drag handles; widths persist via localStorage
- Tablet/mobile: side panels become slide-over drawers (<=768px) :contentReference[oaicite:8]{index=8}

---

## 5.2 Sources (Left Panel)
### Source types (P0)
- PDF, TXT (DOCX optional), URL sources, manual notes :contentReference[oaicite:9]{index=9}

### Must-have behaviors
- Source list row shows: title, type icon, status (processing/ready/error)
- Search within sources list
- Multi-select sources to define “active scope”
- Source preview (PDF embed or extracted text), large sources must not freeze UI
- Rename + delete with confirmation :contentReference[oaicite:10]{index=10}

---

## 5.3 Chat (Center)
- Message thread + composer (Enter sends, Shift+Enter newline)
- Streaming assistant responses (progressive rendering)
- Citations rendered as clickable chips/links
- Clicking a citation opens the correct source preview and scrolls/highlights excerpt (best effort) :contentReference[oaicite:11]{index=11}

---

## 5.4 Study Tools (Right Panel)
### Tabs (P0)
- Flashcards
- Practice Quizzes
- Mini-game (pick 1: term ↔ definition matching) :contentReference[oaicite:12]{index=12}

### Flashcards (P0)
- Generate N cards from selected sources (or a chosen chat message)
- Edit/delete cards
- Study mode: flip + grade (Know/Don’t know)
- Session summary: reviewed, correct, streak (simple) :contentReference[oaicite:13]{index=13}

### Quizzes (P0)
- Generate MCQ quiz from selected sources with settings (question count + difficulty)
- One question per screen, progress indicator
- Results with explanations + citations that open the source preview :contentReference[oaicite:14]{index=14}

### Mini-game (P0)
- Term ↔ definition matching, scoring, replay, uses selected sources/generated pool :contentReference[oaicite:15]{index=15}

---

## 6) Add-on UI Requirements (V1.1)
### AR-01 Study Tools “Fullscreen” Mode
- Fullscreen toggle in Study Tools header
- When enabled: Study Tools covers chat + sources; minimal top bar shows Exit + active tab name
- When disabled: restore prior layout state exactly (collapsed states + widths)
- State: `studyToolsFullscreen: boolean` (session persistence optional)
- Works desktop + mobile; no scroll lock glitches :contentReference[oaicite:16]{index=16}

### AR-02 Study Tools “Docked Resize” Mode (Chat 1/3, Study 2/3)
- Resize handle between Chat and Study Tools
- Min widths: chat 320px, study tools 420px
- Preset button “2/3 Study” sets 33% chat / 67% study (bounded by mins)
- On small screens (<=768px): disable drag; use preset buttons (“Chat”, “Study Tools”) or drawer behavior
- Persist widths in localStorage :contentReference[oaicite:17]{index=17}

### AR-03 Replace “Add Source” menu with modal (~50% overlay)
- Clicking Sources “+” opens modal overlay with dim backdrop
- Modal tabs: Upload File / Add URL / Create Note
- Close via X, ESC, or clicking backdrop; focus trapped; tabs switch without closing :contentReference[oaicite:18]{index=18}

### AR-04 Upload File tab
- Drag/drop + Browse, show supported types, progress + status, errors in-modal
- Upload succeeds → source appears in Sources list (modal may remain open; toast preferred) :contentReference[oaicite:19]{index=19}

### AR-05 Add URL tab
- URL input + “Add URL” button
- Inline validation; disable submit until valid; Enter submits
- Adds source with processing state; clear/keep input (choose one consistently) :contentReference[oaicite:20]{index=20}

### AR-06 Create Note tab
- Textarea + “Save Note” (disabled until non-empty)
- Optional title (P1); otherwise auto-title
- Note appears immediately and is selectable as chat scope :contentReference[oaicite:21]{index=21}

---

## 7) Non-Functional Requirements (MVP)
- Performance: virtualize sources list + chat; lazy-load study tool modules; keep UI responsive :contentReference[oaicite:22]{index=22}
- Accessibility: keyboard operable core flows; consistent focus states; ARIA roles for tabs/dialogs; focus trap; ESC closes modals :contentReference[oaicite:23]{index=23}
- Security: validate uploads; sanitize rendered HTML from sources :contentReference[oaicite:24]{index=24}
- Observability: error monitoring + analytics events :contentReference[oaicite:25]{index=25}

---

## 8) Analytics Events (MVP)
Track at minimum:
- `source_added`, `source_selected`, `chat_sent`
- `flashcards_generated`, `quiz_completed`, `game_completed` :contentReference[oaicite:26]{index=26}

---

## 9) Out of Scope (MVP)
- Payments/subscriptions
- Multi-tenant admin console
- Native mobile apps
- Offline-first mode
- Full collaborative editing :contentReference[oaicite:27]{index=27}

---

## 10) Suggested Delivery Plan (7 Sprints)
1. Tokens + primitives, 3-panel shell, navigation scaffolding
2. Sources list + add (upload/URL/note) + rename/delete
3. Source preview + scope selection + chat base (streaming if ready)
4. Resizable panels + citations open/highlight + conversation mgmt + chat virtualization
5. Study Tools tabs + flashcards CRUD/generation/study mode
6. Quizzes generation/taking/results + mini-game MVP
7. Accessibility + performance + monitoring/analytics + tests/E2E + bug bash :contentReference[oaicite:28]{index=28}
