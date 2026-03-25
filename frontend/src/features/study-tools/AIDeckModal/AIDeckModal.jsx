import { useState } from 'react';
import { Minus, Plus, Loader2, Zap } from 'lucide-react';
import Modal from '../../../components/ui/Modal';
import Button from '../../../components/ui/Button';
import { useFlashcards } from '../../../contexts/FlashcardContext';
import { useSourcesContext } from '../../../contexts/SourcesContext';
import './AIDeckModal.css';

const MIN_CARDS = 5;
const MAX_CARDS = 30;
const DEFAULT_PROMPT = 'Flash cards should cover main and important material';

function AIDeckModal({ isOpen, onClose, notebookId, onDeckCreated }) {
  const { generateAIDeck } = useFlashcards();
  const { getSourcesForNotebook } = useSourcesContext();

  const [title, setTitle] = useState('');
  const [prompt, setPrompt] = useState(DEFAULT_PROMPT);
  const [count, setCount] = useState(10);
  const [isLoading, setIsLoading] = useState(false);
  const [status, setStatus] = useState('');
  const [error, setError] = useState('');

  const canSubmit = title.trim() && prompt.trim() && !isLoading;

  const handleCountChange = (delta) => {
    setCount((prev) => Math.min(MAX_CARDS, Math.max(MIN_CARDS, prev + delta)));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!canSubmit) return;

    setIsLoading(true);
    setError('');

    try {
      const sources = getSourcesForNotebook(notebookId);
      const deck = await generateAIDeck(
        notebookId,
        title.trim(),
        prompt.trim(),
        count,
        { sources, onStatus: setStatus },
      );
      onDeckCreated(deck.id);
      handleClose();
    } catch (err) {
      setError(err.message || 'Failed to generate deck. Please try again.');
    } finally {
      setIsLoading(false);
      setStatus('');
    }
  };

  const handleClose = () => {
    if (isLoading) return;
    setTitle('');
    setPrompt(DEFAULT_PROMPT);
    setCount(10);
    setError('');
    setStatus('');
    onClose();
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      title="Generate AI Deck"
      size="md"
      closeOnBackdrop={!isLoading}
      closeOnEscape={!isLoading}
    >
      <form className="ai-deck-form" onSubmit={handleSubmit}>
        {/* Deck Name */}
        <div className="ai-deck-form__field">
          <label className="ai-deck-form__label" htmlFor="ai-deck-title">
            Deck Name
          </label>
          <input
            id="ai-deck-title"
            className="ai-deck-form__input"
            type="text"
            placeholder="e.g. Biology Chapter 5"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            disabled={isLoading}
            autoFocus
          />
        </div>

        {/* Prompt */}
        <div className="ai-deck-form__field">
          <label className="ai-deck-form__label" htmlFor="ai-deck-prompt">
            Additional Instructions
          </label>
          <textarea
            id="ai-deck-prompt"
            className="ai-deck-form__textarea"
            rows={3}
            placeholder="Describe the material to generate flashcards from..."
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            disabled={isLoading}
          />
        </div>

        {/* Card Count */}
        <div className="ai-deck-form__field">
          <span className="ai-deck-form__label">
            Number of Cards
          </span>
          <div className="ai-deck-form__stepper">
            <button
              type="button"
              className="ai-deck-form__step-btn"
              onClick={() => handleCountChange(-5)}
              disabled={isLoading || count <= MIN_CARDS}
              aria-label="Decrease count"
            >
              <Minus size={14} />
            </button>
            <span className="ai-deck-form__step-value">{count}</span>
            <button
              type="button"
              className="ai-deck-form__step-btn"
              onClick={() => handleCountChange(5)}
              disabled={isLoading || count >= MAX_CARDS}
              aria-label="Increase count"
            >
              <Plus size={14} />
            </button>
          </div>
        </div>

        {/* Error */}
        {error && (
          <p className="ai-deck-form__error">{error}</p>
        )}

        {/* Actions */}
        <div className="ai-deck-form__actions">
          <Button variant="ghost" size="sm" type="button" onClick={handleClose} disabled={isLoading}>
            Cancel
          </Button>
          <Button variant="primary" size="sm" type="submit" disabled={!canSubmit}>
            {isLoading ? (
              <>
                <Loader2 size={16} className="ai-deck-form__spinner" />
                {status || 'Generating...'}
              </>
            ) : (
              <><Zap size={16} /> Create With AI</>
            )}
          </Button>
        </div>
      </form>
    </Modal>
  );
}

export default AIDeckModal;
