# AI context and sources update

## Goal Description
Enhance the existing "Add Source" functionality to upload PDF files into a temporary frontend storage folder (`tempPDFfolder`) for development purposes. Integrate an AI feature that reads these PDFs, summarizes them if they exceed token limits, and uses the extracted text as context for generating quizzes and flashcards via ChatGPT API. Additionally, improve the UX for YouTube links by fetching and displaying the actual video title instead of the raw URL in the Sources Panel.

## Proposed Changes

### 1. Temporary PDF Folder & File Upload (Vite Dev Server Plugin)
To satisfy the requirement of saving files to a folder "in the frontend" during development, we will build a minimal Vite plugin to handle file system operations since standard browser JavaScript cannot write to the local file system.

- **`frontend/vite-plugin-dev-files.js`**: Create a Vite custom plugin using the `configureServer` hook to add `POST /api/upload-pdf` and `GET /api/list-pdfs` endpoints. This allows the frontend to save uploaded files directly to `frontend/tempPDFfolder` and list them.
- **`frontend/tempPDFfolder/`**: The local directory used to temporarily hold PDF files during development.
- **`frontend/vite.config.js`**: Import and register the new `vite-plugin-dev-files.js`.
- **`frontend/src/features/sources/AddSourceModal/tabs/UploadTab.jsx`**: Update the form submission to take the selected `File` object, pack it in a `FormData`, and POST it to `/api/upload-pdf`. On success, continue with the normal `addSource` state flow.

### 2. PDF Parsing & Summarization
When the AI generation features are requested, we need to extract text from the stored PDFs. If the content length is larger than the ChatGPT token window, we must summarize it first.

- **`frontend/src/utils/pdfParser.js`**: Integrate `pdfjs-dist` (or similar) to fetch and parse the PDF files into raw text strings.
- **`frontend/src/utils/aiSummarizer.js`**: A utility that checks the length of extracted text. If it exceeds a safe token threshold, chunk the text into smaller segments and call the OpenAI API to summarize each segment, appending them together into a master summary for the main generation task.

### 3. AI Flashcard & Quiz Generation with Context
Update the existing context generation files to fetch the PDF context and inject it into the prompt.

- **`frontend/src/contexts/FlashcardContext.jsx`** & **`frontend/src/contexts/QuizContext.jsx`**: 
  - Update `generateAIQuiz` and `generateAIDeck`.
  - Fetch the context from `tempPDFfolder` utilizing `pdfParser.js` and `aiSummarizer.js`.
  - Inject the context into the ChatGPT system prompt: `Use the following source material as context for generating the content. [START CONTEXT] {extractedText} [END CONTEXT]`.
- **`frontend/src/features/study-tools/AIQuizModal/AIQuizModal.jsx`** & **`frontend/src/features/study-tools/AIDeckModal/AIDeckModal.jsx`**: Add dynamic UI feedback letting the user know the current status (e.g., "Reading PDFs...", "Summarizing Context...", "Generating Content...").

### 4. YouTube Link Title Fetching
- **`frontend/src/features/sources/AddSourceModal/tabs/UrlTab.jsx`**: 
  - Upon submission of a URL, check if `urlValue` matches a YouTube URL pattern.
  - If so, call the public YouTube oEmbed endpoint (`https://www.youtube.com/oembed?url=${encodeURIComponent(urlValue)}&format=json`) to fetch the real video `title`.
  - Store this `title` in the source object instead of defaulting to `hostname` (www.youtube.com).

## Verification Plan

### Manual Verification
1. **File Upload Verification**: Open the Add Source Modal, switch to "Upload File", and upload a PDF. Verify the file exists locally in `frontend/tempPDFfolder`.
2. **YouTube Video Title Verification**: Open the Add Source Modal, switch to "Add URL", and add a YouTube link. Check the Sources Panel UI to ensure it displays the valid video title instead of the plain domain name.
3. **AI Context Reading**: Trigger AI Generation for Flashcards. Verify via `console.log` or Network Logs that the API prompt accurately includes text extracted from the temp PDFs.
4. **Token Summarization Limits**: Add a massive 100-page PDF document to the project. Trigger AI generation. Verify that `aiSummarizer.js` invokes an preliminary summarization pass with OpenAI to reduce the size and prevent HTTP `400 Bad Request` context limit errors.
