# Implementation Plan: Custom Study Tools & Sources Management

This plan completely addresses the requested frontend modifications to refine the AI Study Tool UX, ensuring state-of-the-art responsiveness, aesthetics (March 2026 standards), and preparing the architecture for future database/embeddings scaling. 

## Proposed Changes

### Component: Study Tools Panel
Removing the games tab and stretching remaining tabs is a clean UX update.

#### [MODIFY] frontend/src/features/study-tools/StudyToolsPanel/StudyToolsPanel.jsx
- **Remove:** The `game` tab trigger and its `TabPanel` content.
- **Update:** Apply styling classes or inline styles to ensure the `flashcards` and `quizzes` tabs expand functionally across the entire segmented control (`flex: 1` split 50/50).
- **Update:** Implement the trigger logic within the `quizzes` panel to open the newly created `AIQuizModal`.

#### [MODIFY] frontend/src/features/study-tools/StudyToolsPanel/StudyToolsPanel.css
- **Add:** CSS rules targeting the tab triggers inside `.study-tools-panel__tabs` to make them stretch equally, utilizing flexbox layouts for proportional distribution.

---

### Component: Sources Panel
Making sources effortlessly managed immediately opens the path for context-based AI.

#### [MODIFY] frontend/src/features/sources/SourcesPanel/SourcesPanel.jsx
- **State Initialization:** Clear out the `[ ... ]` hardcoded default sources, setting it to `[]`.
- **Selected Logic:** Remove the `selectedSources` logic, UI checkboxes, and the "Select All" header widget entirely. Make list items appear normally (deselected CSS classes) but imply all are active.
- **Rename Feature:** Change the `DropdownItem` placeholder for "Rename" to toggle an inline editing state or a simple popup prompt that updates the item's `title` property.

#### [MODIFY] frontend/src/features/sources/AddSourceModal/tabs/UploadTab.jsx
- **UX Polish:** Enhance the dropzone aesthetics (gentle hover highlights, standard lucid UI icons, and rounded border rings on `:focus-visible` or active drag).
- **Functionality:** Map the "completed upload" simulation to cleanly pipe the resultant file data (name, id, fake path) up to `SourcesPanel` state to be rendered.

#### [MODIFY] frontend/src/features/sources/AddSourceModal/tabs/UrlTab.jsx
- **Functionality:** In addition to validating the URL, explicitly pipe this submission step up to the generic `SourcesPanel` state to be appended as a `type: 'url'` source item.

---

### Component: AI Generation Tools (Flashcards & Quizzes)
Simplifying generation forms to minimize friction when context takes over.

#### [MODIFY] frontend/src/features/study-tools/AIDeckModal/AIDeckModal.jsx
- **UI:** Remove the difficulty row component. 
- **Labels:** Change `Material / Instructions` block label to `Additional Instructions`.
- **Button:** Update the primary submit button to `[LightningBoltIcon] Create With AI`. Consolidate loading logic so the spinner and text inline horizontally, rather than overflowing vertical bounds.

#### [NEW] frontend/src/features/study-tools/AIQuizModal/AIQuizModal.jsx
- **Creation:** Replicate `AIDeckModal.jsx` structure.
- **Fields:** Create fields for "Quiz Name", "Additional Instructions" (textarea), and "Number of Questions" (stepper 5-30).
- **Button:** Utilize the `[LightningBoltIcon] Create With AI` aesthetic.

#### [NEW] frontend/src/contexts/QuizContext.jsx
- **Creation:** Replicate the in-memory architecture of `FlashcardContext.jsx`, implementing methods to `generateAIQuiz`, `getQuizzes`, etc., preparing a seamless transition to a future DB adapter. 
- Ensure this context wraps the components in `App.jsx` or `main.jsx`.

---

## Verification Plan
After executing these changes, we will verify by:

### Manual Verification
1. **Layout Check:** Open the app and observe the right Study Tools Panel. Assert "Games" is gone, and "Flashcards/Quizzes" split the 100% width evenly.
2. **Flashcards AI Tool Check:** Click "Generate AI Deck". Verify "Difficulty" is missing, label says "Additional Instructions", and the submit button has a lightning bolt icon + "Create With AI" text with no bounds overlapping when loading.
3. **Quizzes Integration:** Navigate to the Quizzes tab, click a generation button, to see the new `AIQuizModal`. Generate a quiz to verify it's added to a list (in memory).
4. **Sources Panel UI & Functionality:**
   - Verify the list defaults to empty.
   - Click (+). Upload a dummy file (PDF/txt) via the shiny new UploadTab and wait 2 seconds; ensure it appears on the panel.
   - Click (+). Add a YouTube URL in the UrlTab; ensure it appears on the panel.
   - Click the "more" options icon on an item, click Rename, type a new name, and submit to verify state updates.
   - Ensure you see absolutely NO checkboxes nor "selected" markers.
