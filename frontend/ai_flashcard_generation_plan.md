# Goal Description
Add a feature to generate flashcards using AI. A dedicated square button with a lightning logo will be placed next to the "Create Deck" button(s) in the Study Tools panel. Clicking it opens a clean, well-scoped popup window with options to specify deck name, material prompt, difficulty (easy, medium, hard), and the number of flashcards (5 to 30). Upon submission, a loading animation will play, and an AI-generated deck will be injected into the user's collection, distinctively marked with the lightning logo in its metadata.

State of the art (March 2026) implementations recommend:
- **Scoped Portals/Dialogs**: Using the native HTML5 `<dialog>` element styled with modern CSS to ensure the popup stays naturally trapped within the container's bounds while adhering to top-layer accessibility, or using contextual React framing to keep it within the right panel.
- **Segmented Controls for Difficulty**: Using CSS grid with dynamic `::before`/`::after` highlights or `framer-motion` layout animations to create a slick sliding window highlight effect over the active difficulty option.
- **Form Ergonomics**: Using a custom numeric stepper component with strict `inputMode="numeric"` to provide a native feel across desktop and touch, preventing invalid text entry natively rather than relying heavily on JS parsing.

## Proposed Changes

### Context & State Management
#### [MODIFY] [FlashcardContext.jsx](file:///Users/ethangonzalez/Desktop/storm44-/frontend/src/contexts/FlashcardContext.jsx)
- Update `createDeck` (or add `createAIDeck`) to accept an `isAiGenerated` flag.
- Add an asynchronous function `generateAIFlashcards(notebookId, title, prompt, difficulty, count)` that:
  - Fetches from `OPENAI_API_URL` using the `OPENAI_API_KEY` defined similarly to `ChatPanel`.
  - Prompts GPT-4o-mini (or designated model) to create an array of `count` flashcards with `front` and `back` values, given the user `prompt` and `difficulty`. Must request a JSON response for reliability.
  - Automatically creates a new deck and parses the JSON response to add `count` cards to it.

---

### UI Components
#### [MODIFY] [DeckList.jsx](file:///Users/ethangonzalez/Desktop/storm44-/frontend/src/features/study-tools/DeckList/DeckList.jsx)
- Import `Zap` from `lucide-react`.
- Next to the existing "Create Deck" button in both the empty state and the footer, add a square button (with `Zap` logo). Ensure it matches vertical height.
- Add local state `isAIModalOpen` to toggle the AI generation popup.
- Render the new `AIDeckModal` component conditionally, passing necessary callbacks.
- In the deck list mapping, check for `deck.isAiGenerated`. If true, display the `Zap` icon in the `.deck-card__meta` container next to the "0 cards and Never" text.

#### [MODIFY] [DeckList.css](file:///Users/ethangonzalez/Desktop/storm44-/frontend/src/features/study-tools/DeckList/DeckList.css)
- Add Flexbox styling to group the normal "Create Deck" button and the new square AI deck button side-by-side seamlessly.
- Style the `Zap` icon in the card metadata to render appropriately with correct spacing.

#### [NEW] AIDeckModal.jsx
- Create a new component scoped to the Study Tools panel.
- Include a semi-transparent backdrop and a centered clean modal container.
- Inputs:
  - Text input for Deck Name.
  - Textarea for prompt: `defaultValue="Flash cards should cover main and important material"`.
  - Difficulty Segmented Control: "easy", "medium", "hard". Visual sliding highlight.
  - Number Input Stepper: 5 to 30. Buttons for `+` and `-`. Input field restricted to numbers.
- Submit Button: "Create New Deck With AI". Transitions to a loading state with spinner/animation when clicked.

#### [NEW] AIDeckModal.css
- Scoped styles ensuring it stays visually embedded in the right panel.
- Animations for the loading state and sliding difficulty selector.

## Verification Plan

### Automated Tests
Currently, the application relies on visual React components rendered in the Vite dev server. Since no established unit tests (e.g., Jest/Vitest) for contexts seemingly exist, we will focus on manual verification for UI layout and Context state correctness. We can add minor inline assertions if a test runner is present, but otherwise rely on manual UI bounds testing.

### Manual Verification
1. **Button Presence**: Open the Workspace, open Study Tools, go to Flashcards tab. Verify the square `Zap` button is directly right of "Create Deck" and matches its height perfectly.
2. **Modal Experience**: Click the AI button. Ensure the popup stays visually contained in the panel frame, not overlaying the whole window globally.
3. **Form Logic**:
   - Verify typing into the prompt field works.
   - Click "medium" and "hard"; ensure the sliding highlight smoothly animates.
   - Click `-` and `+` on the number picker. Verify it bounds between 5 and 30. Test typing `99` (should cap/prevent) and non-numbers (should prevent).
4. **Generation Flow**: Click "Create New Deck With AI". Observe the loading state. Once complete, modal should close.
5. **Collection Update**: A new deck should be immediately visible. Check the metadata row of the new deck to confirm the lightning logo (`Zap`) appears correctly next to the card count and date.
6. **Deck Integrity**: Click the new deck and verify it was populated with the requested number of simulated placeholder cards.
