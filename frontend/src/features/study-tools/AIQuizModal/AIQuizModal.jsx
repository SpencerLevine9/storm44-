import { useState } from 'react';
import { Minus, Plus, Loader2, Zap } from 'lucide-react';
import Modal from '../../../components/ui/Modal';
import Button from '../../../components/ui/Button';
import { useQuizzes } from '../../../contexts/QuizContext';
import './AIQuizModal.css';

const MIN_QUESTIONS = 5;
const MAX_QUESTIONS = 30;
const DEFAULT_PROMPT = 'Quiz should cover main and important material';

function AIQuizModal({ isOpen, onClose, notebookId, onQuizCreated }) {
  const { generateAIQuiz } = useQuizzes();

  const [title, setTitle] = useState('');
  const [prompt, setPrompt] = useState(DEFAULT_PROMPT);
  const [count, setCount] = useState(10);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const canSubmit = title.trim() && prompt.trim() && !isLoading;

  const handleCountChange = (delta) => {
    setCount((prev) => Math.min(MAX_QUESTIONS, Math.max(MIN_QUESTIONS, prev + delta)));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!canSubmit) return;

    setIsLoading(true);
    setError('');

    try {
      const quiz = await generateAIQuiz(
        notebookId,
        title.trim(),
        prompt.trim(),
        count,
      );
      onQuizCreated(quiz.id);
      handleClose();
    } catch (err) {
      setError(err.message || 'Failed to generate quiz. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleClose = () => {
    if (isLoading) return;
    setTitle('');
    setPrompt(DEFAULT_PROMPT);
    setCount(10);
    setError('');
    onClose();
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      title="Generate AI Quiz"
      size="md"
      closeOnBackdrop={!isLoading}
      closeOnEscape={!isLoading}
    >
      <form className="ai-quiz-form" onSubmit={handleSubmit}>
        {/* Quiz Name */}
        <div className="ai-quiz-form__field">
          <label className="ai-quiz-form__label" htmlFor="ai-quiz-title">
            Quiz Name
          </label>
          <input
            id="ai-quiz-title"
            className="ai-quiz-form__input"
            type="text"
            placeholder="e.g. Biology Chapter 5 Quiz"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            disabled={isLoading}
            autoFocus
          />
        </div>

        {/* Prompt */}
        <div className="ai-quiz-form__field">
          <label className="ai-quiz-form__label" htmlFor="ai-quiz-prompt">
            Additional Instructions
          </label>
          <textarea
            id="ai-quiz-prompt"
            className="ai-quiz-form__textarea"
            rows={3}
            placeholder="Describe the material to generate quiz questions from..."
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            disabled={isLoading}
          />
        </div>

        {/* Question Count */}
        <div className="ai-quiz-form__field">
          <span className="ai-quiz-form__label">
            Number of Questions
          </span>
          <div className="ai-quiz-form__stepper">
            <button
              type="button"
              className="ai-quiz-form__step-btn"
              onClick={() => handleCountChange(-5)}
              disabled={isLoading || count <= MIN_QUESTIONS}
              aria-label="Decrease count"
            >
              <Minus size={14} />
            </button>
            <span className="ai-quiz-form__step-value">{count}</span>
            <button
              type="button"
              className="ai-quiz-form__step-btn"
              onClick={() => handleCountChange(5)}
              disabled={isLoading || count >= MAX_QUESTIONS}
              aria-label="Increase count"
            >
              <Plus size={14} />
            </button>
          </div>
        </div>

        {/* Error */}
        {error && (
          <p className="ai-quiz-form__error">{error}</p>
        )}

        {/* Actions */}
        <div className="ai-quiz-form__actions">
          <Button variant="ghost" size="sm" type="button" onClick={handleClose} disabled={isLoading}>
            Cancel
          </Button>
          <Button variant="primary" size="sm" type="submit" disabled={!canSubmit}>
            {isLoading ? (
              <>
                <Loader2 size={16} className="ai-quiz-form__spinner" />
                Generating...
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

export default AIQuizModal;
