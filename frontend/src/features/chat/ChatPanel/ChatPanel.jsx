import { useState, useRef, useEffect } from 'react';
import { Send, Sparkles, Copy, ThumbsUp, ThumbsDown } from 'lucide-react';
import Button from '../../../components/ui/Button';
import IconButton from '../../../components/ui/IconButton';
import './ChatPanel.css';

// Initial welcome message - created once outside component
const createInitialMessage = () => ({
  id: '1',
  role: 'assistant',
  content: 'Hello! I\'m your AI study assistant. I can help you understand your sources, answer questions, and create study materials. What would you like to explore today?',
  timestamp: new Date().toISOString(),
});

/**
 * Chat panel - center area for conversation
 */
function ChatPanel() {
  const [messages, setMessages] = useState(() => [createInitialMessage()]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: inputValue.trim(),
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    // Simulate AI response
    setTimeout(() => {
      const assistantMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'This is a simulated response. In the full implementation, this would be a streaming response from your AI backend with citations to your selected sources. The response would include inline citations like [1] that link back to specific passages in your documents.',
        timestamp: new Date().toISOString(),
        citations: [
          { id: '1', sourceId: '1', text: 'Introduction to Machine Learning, p.12' }
        ]
      };
      setMessages(prev => [...prev, assistantMessage]);
      setIsLoading(false);
    }, 1500);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
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
            <div className="message__avatar">
              {message.role === 'assistant' ? (
                <Sparkles size={18} />
              ) : (
                <span>You</span>
              )}
            </div>
            <div className="message__content">
              <div className="message__bubble">
                <p className="message__text">{message.content}</p>
                {message.citations && message.citations.length > 0 && (
                  <div className="message__citations">
                    {message.citations.map(citation => (
                      <button 
                        key={citation.id}
                        className="citation-chip"
                        title={citation.text}
                      >
                        [{citation.id}] {citation.text}
                      </button>
                    ))}
                  </div>
                )}
              </div>
              <div className="message__meta">
                <span className="message__time">{formatTime(message.timestamp)}</span>
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
              <Sparkles size={18} />
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
        <div className="composer">
          <textarea
            ref={textareaRef}
            className="composer__input"
            placeholder="Ask about your sources..."
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
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
