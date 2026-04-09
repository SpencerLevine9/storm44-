# ChatGPT Integration Implementation Plan (State of the Art - Feb 2026)

This document outlines the best approach for integrating ChatGPT into your frontend's middle chat panel, adhering to all your requirements: local testing only, no message continuity, brief outputs (max 10 sentences), wrapping text neatly, an 8-line auto-scrolling input, and removing the blue focus outline.

## Goal Description
Implement a direct, frontend-only connection to the OpenAI ChatGPT API for testing purposes. Customize the chat input box and message rendering to ensure a smooth, modern UI without distracting focus rings.

## State of the Art Research (February 2026)
- **Model Selection**: The current standard for responsive, brief, and cost-effective chat is `gpt-4o-mini` (or standard `gpt-4o`). We will use this in the API call.
- **Frontend Direct API Call**: While normally discouraged due to API key exposure, doing this inside the frontend codebase is completely fine for a local, non-production test. We'll use the native `fetch` Web API to call `https://api.openai.com/v1/chat/completions`.
- **Stateless Chat (No Continuity)**: To eliminate continuity as requested, we will not send the history of the conversation to the API. We will only send a system prompt containing the behavior constraints, followed by the user's latest message.
- **Output Constraint**: We enforce the 10-sentence limit reliably using a strict System Prompt: `"You are a helpful AI assistant. You must be brief. Your responses must never exceed 10 sentences."`
- **Markdown Rendering**: ChatGPT naturally outputs markdown. To ensure responses are "wrapped neatly and proper", the state-of-the-art approach for React is to parse this markdown with `react-markdown` rather than just dumping plain text, creating properly formatted paragraphs, lists, and code blocks.

## Proposed Changes

### Chat Panel Component
Modifications to the main chat layout and logic.

#### [MODIFY] [ChatPanel.jsx](file:///Users/ethangonzalez/Desktop/storm44-/frontend/src/features/chat/ChatPanel/ChatPanel.jsx)
- **API Integration**: Replace the `setTimeout` simulation in `handleSend` with a `fetch` call to the OpenAI API.
  - The API key will be placed in a constant variable at the top, which you can fill in.
  - The payload will only consist of the system prompt and the current user message (no history).
- **Auto-Resizing Input**: Add a reference and logic in `onChange` to automatically adjust the `textarea` height as the user types, up to 8 lines.
- **Neat Wrapping**: We will install and import `react-markdown` to render `message.content` instead of just using `<p>`. This ensures that ChatGPT's naturally formatted text (like bullet points or bold text) renders beautifully and wraps correctly inside the bubble.

### Chat Panel Styles
Updates to fix the UI quirks requested.

#### [MODIFY] [ChatPanel.css](file:///Users/ethangonzalez/Desktop/storm44-/frontend/src/features/chat/ChatPanel/ChatPanel.css)
- **Remove Blue Focus Outline**: 
  - Locate `.composer:focus-within` and remove `border-color: var(--color-border-focus);` and `box-shadow: var(--shadow-focus-ring);`.
  - Ensure `.composer__input:focus` has `outline: none;` (it currently does, but we'll double check the composer container).
- **8-Line Max Height**: 
  - Update `.composer__input`'s `max-height`. Assuming standard line height, 8 lines is exactly `calc(var(--line-height-normal) * var(--font-size-base) * 8)`. We'll set this exact value and ensure `overflow-y: auto;` is applied.
- **Message Wrapping**:
  - Add specific styles for the markdown output (if used) so that paragraphs, lists, and other elements inside `.message__text` have proper margins and word-breaking applied.

## Verification Plan

### Manual Verification
1. **API Key Setup**: You will paste your OpenAI API key into the designated variable in `ChatPanel.jsx`.
2. **Start Dev Server**: Run `npm run dev` in the frontend directory.
3. **UI Testing**: 
   - Click the chat input box. Verify that the blue focus outline is gone.
   - Type multiple lines into the input. Verify that the text box expands up to 8 lines and then begins to scroll.
4. **Integration Testing**:
   - Send a prompt like "Explain quantum physics."
   - Verify that the chat loading indicator appears.
   - Verify that the response arrives and is neatly formatted.
   - Verify that the response is remarkably brief (under 10 sentences) despite the complex topic.
   - Send a follow-up test: "What was my last question?" -> The AI should be completely unaware, verifying that continuity/context is correctly disabled.
