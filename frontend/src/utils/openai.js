const OPENAI_API_KEY = import.meta.env.VITE_OPENAI_API_KEY;
const OPENAI_API_URL = 'https://api.openai.com/v1/chat/completions';
const DEFAULT_MODEL = 'gpt-4o-mini';

/**
 * Send a chat completion request to the OpenAI API.
 *
 * @param {string} systemPrompt - The system message.
 * @param {string} userPrompt - The user message.
 * @param {object} [options] - Optional overrides.
 * @param {number} [options.maxTokens=500] - Max tokens in response.
 * @param {number} [options.temperature=0.7] - Sampling temperature.
 * @param {boolean} [options.json=false] - Request JSON response format.
 * @returns {Promise<string>} The assistant's response content.
 */
export async function chatCompletion(systemPrompt, userPrompt, options = {}) {
  const { maxTokens = 500, temperature = 0.7, json = false } = options;

  const body = {
    model: DEFAULT_MODEL,
    messages: [
      { role: 'system', content: systemPrompt },
      { role: 'user', content: userPrompt },
    ],
    max_tokens: maxTokens,
    temperature,
  };

  if (json) {
    body.response_format = { type: 'json_object' };
  }

  const response = await fetch(OPENAI_API_URL, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${OPENAI_API_KEY}`,
    },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.error?.message || `API error: ${response.status}`);
  }

  const data = await response.json();
  return data.choices?.[0]?.message?.content || '';
}
