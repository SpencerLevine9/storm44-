import { useState, useRef, useEffect } from 'react';
import { Send, Zap, Copy, ThumbsUp, ThumbsDown } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import Button from '../../../components/ui/Button';
import IconButton from '../../../components/ui/IconButton';
import './ChatPanel.css';

// Backend API (local development)
const BACKEND_API_URL = import.meta.env.VITE_BACKEND_API_URL || 'http://127.0.0.1:8000';


// May have to delete later
const OPENAI_API_KEY = import.meta.env.VITE_OPENAI_API_KEY;
const OPENAI_API_URL = 'https://api.openai.com/v1/chat/completions';
const SYSTEM_PROMPT =
  'You are a helpful AI study assistant. You must be brief and concise. ' +
  'Your responses must never exceed 10 sentences. Use markdown formatting when appropriate.';
const TEXTAREA_MAX_HEIGHT = 180; // 8 lines: 15px font * 1.5 line-height * 8

const INITIAL_MESSAGE = {
  id: '1',
  role: 'assistant',
  content:
    "Hello! I'm your AI study assistant. I can help you understand your sources, " +
    'answer questions, and create study materials. What would you like to explore today?',
  timestamp: new Date().toISOString(),
};

function formatTime(timestamp) {
  return new Date(timestamp).toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit',
  });
}

/**
 * Chat panel — center area for AI conversation.
 */
function ChatPanel() {
  const [messages, setMessages] = useState([INITIAL_MESSAGE]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [availableModels, setAvailableModels] = useState([]);
  const [selectedModel, setSelectedModel] = useState('');
  const [modelLoadError, setModelLoadError] = useState('');
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);


  useEffect(() => {
  const loadTutorModels = async () => {
    try {
      const response = await fetch(`${BACKEND_API_URL}/api/v1/ask/models`);

      if (!response.ok) {
        throw new Error(`Failed to load models: ${response.status}`);
      }

      const data = await response.json();
      const models = data?.allowed_models || [];

      setAvailableModels(models);
      setSelectedModel(data?.default_model || models[0] || '');
      setModelLoadError('');
    } catch (error) {
      console.error('Failed to load tutor models:', error);

      // Safe local fallback so the UI still works during development
      setAvailableModels(['gpt-5-mini', 'gpt-4.1-mini']);
      setSelectedModel('gpt-5-mini');
      setModelLoadError('Using default model list');
    }
  };

  loadTutorModels();
}, []);

  const resizeTextarea = () => {
    const textarea = textareaRef.current;
    if (!textarea) return;
    textarea.style.height = 'auto';
    textarea.style.height = `${Math.min(textarea.scrollHeight, TEXTAREA_MAX_HEIGHT)}px`;
  };

  const resetTextareaHeight = () => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleInputChange = (e) => {
    setInputValue(e.target.value);
    resizeTextarea();
  };

  const handleSend = async () => {
  if (!inputValue.trim() || isLoading) return;

  const userMessage = {
    id: Date.now().toString(),
    role: 'user',
    content: inputValue.trim(),
    timestamp: new Date().toISOString(),
  };

  setMessages((prev) => [...prev, userMessage]);
  setInputValue('');
  resetTextareaHeight();
  setIsLoading(true);

  try {
    // Calls our backend
    const response = await fetch(`${BACKEND_API_URL}/api/v1/ask`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
       // Match the AskRequest schema in the backend
      body: JSON.stringify({
        query: userMessage.content,
        source_ids: [], // later: pass selected sources from UI
        top_k: 5,       // later: allow UI to control this
        model: selectedModel || undefined,
      }),
    });

    // If backend returns an error (422 validation, 500, etc.), show it nicely

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      const msg = errorData?.detail
        ? JSON.stringify(errorData.detail)
        : errorData?.message;

      throw new Error(msg || `Backend error: ${response.status}`);
    }

    // Backend returns AskResponse with { answer: string, citations: Source[] }
    const data = await response.json();
    const content = data?.answer || 'No response received.';

    setMessages((prev) => [
      ...prev,
      {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content,
        timestamp: new Date().toISOString(),
        citations: data?.citations || [],
        modelUsed: data?.model_used || null,
      },
    ]);
  } catch (error) {
    setMessages((prev) => [
      ...prev,
      {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `**Error:** ${
          error?.message || 'Failed to get a response. Is the backend running on port 8000?'
        }`,
        timestamp: new Date().toISOString(),
      },
    ]);
  } finally {
    setIsLoading(false);
  }
};

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="chat-panel">
      {/* Messages area */}
      <div className="chat-panel__messages">
        {messages.map(message => (
          <div 
            key={message.id} 
            className={`message message--${message.role}`}
          >
            {message.role === 'assistant' && (
              <div className="message__avatar">
                <Zap size={18} />
              </div>
            )}
            <div className="message__content">
              <div className="message__bubble">
                {message.role === 'assistant' ? (
                  <div className="message__text">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.content}</ReactMarkdown>
                  </div>
                ) : (
                  <p className="message__text">{message.content}</p>
                )}
              </div>
              <div className="message__meta">
                <span className="message__time">{formatTime(message.timestamp)}</span>

                {message.role === 'assistant' && message.modelUsed && (
                  <span className="message__model">Model: {message.modelUsed}</span>
                )}

                {message.role === 'assistant' && (
                  <div className="message__actions">
                    <IconButton variant="ghost" size="sm" label="Copy">
                      <Copy size={14} />
                    </IconButton>
                    <IconButton variant="ghost" size="sm" label="Good response">
                      <ThumbsUp size={14} />
                    </IconButton>
                    <IconButton variant="ghost" size="sm" label="Bad response">
                      <ThumbsDown size={14} />
                    </IconButton>
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="message message--assistant">
            <div className="message__avatar">
              <Zap size={18} />
            </div>
            <div className="message__content">
              <div className="message__bubble message__bubble--loading">
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Composer */}
      <div className="chat-panel__composer">
        <div className="chat-panel__model-row">
          <label htmlFor="tutor-model" className="chat-panel__model-label">
            Tutor model
          </label>

          <select
            id="tutor-model"
            className="chat-panel__model-select"
            value={selectedModel}
            onChange={(e) => setSelectedModel(e.target.value)}
            disabled={isLoading || availableModels.length === 0}
          >
            {availableModels.map((model) => (
              <option key={model} value={model}>
                {model}
              </option>
            ))}
          </select>

          {modelLoadError && (
            <span className="chat-panel__model-warning">{modelLoadError}</span>
          )}
        </div>

        <div className="composer">
          <textarea
            ref={textareaRef}
            className="composer__input"
            placeholder="Ask about your sources..."
            value={inputValue}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            rows={1}
            disabled={isLoading}
          />
          <Button
            variant="primary"
            size="sm"
            onClick={handleSend}
            disabled={!inputValue.trim() || isLoading}
            className="composer__send"
          >
            <Send size={16} />
          </Button>
        </div>
        <p className="chat-panel__hint">
          Press Enter to send, Shift+Enter for new line
        </p>
      </div>
    </div>
  );
}

export default ChatPanel;
