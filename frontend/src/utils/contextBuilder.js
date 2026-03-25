import { parsePdf } from './pdfParser';

// gpt-4o-mini supports ~128k tokens, but we cap context to keep room for
// the system prompt, user prompt, and response (~12k chars ≈ 3k tokens).
const MAX_CONTEXT_CHARS = 48000; // ~12k tokens at 4 chars/token

/**
 * Build a context string from an array of source objects.
 * Parses PDFs and collects note content. Truncates if over budget.
 *
 * @param {Array<{ id: string, type: string, content: string|null, title: string }>} sources
 * @param {(status: string) => void} [onStatus] — optional status callback
 * @returns {Promise<string>} — context string ready to inject into a prompt, or empty string
 */
export async function buildContext(sources, onStatus) {
  if (!sources || sources.length === 0) return '';

  const textParts = [];

  // Gather note content (already stored as text)
  const noteSources = sources.filter((s) => s.type === 'note' && s.content);
  for (const note of noteSources) {
    textParts.push(`[Source: ${note.title}]\n${note.content}`);
  }

  // Parse PDF sources
  const pdfSources = sources.filter((s) => s.type === 'pdf' && s.content);
  if (pdfSources.length > 0) {
    onStatus?.('Reading sources...');

    for (const source of pdfSources) {
      try {
        const result = await parsePdf(source.content);
        textParts.push(`[Source: ${source.title}]\n${result.totalText}`);
      } catch (err) {
        console.warn(`Failed to parse PDF "${source.title}":`, err);
        // Skip this source, don't block generation
      }
    }
  }

  if (textParts.length === 0) return '';

  onStatus?.('Building context...');

  let combined = textParts.join('\n\n---\n\n');

  // Truncate if over budget
  if (combined.length > MAX_CONTEXT_CHARS) {
    combined = combined.slice(0, MAX_CONTEXT_CHARS) + '\n\n[Context truncated due to length]';
  }

  return combined;
}

/**
 * Wrap raw context text in the prompt template.
 */
export function wrapContextPrompt(contextText) {
  if (!contextText) return '';
  return (
    'Use the following source material as context for generating the content. ' +
    'Base your output on this material.\n' +
    `[START CONTEXT]\n${contextText}\n[END CONTEXT]\n\n`
  );
}
