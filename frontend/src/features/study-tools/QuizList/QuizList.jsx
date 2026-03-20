import { useState } from 'react';
import { HelpCircle, Trash2, Layers, Clock, Zap } from 'lucide-react';
import Button from '../../../components/ui/Button';
import IconButton from '../../../components/ui/IconButton';
import { useQuizzes } from '../../../contexts/QuizContext';
import { useNotebooks } from '../../../contexts/NotebookContext';
import AIQuizModal from '../AIQuizModal/AIQuizModal';
import './QuizList.css';

function QuizList({ onSelectQuiz }) {
  const { activeNotebookId } = useNotebooks();
  const { getQuizzesForNotebook, deleteQuiz, getQuestionCount } = useQuizzes();
  const quizzes = getQuizzesForNotebook(activeNotebookId);

  const [isAIModalOpen, setIsAIModalOpen] = useState(false);

  const handleDelete = (e, quizId) => {
    e.stopPropagation();
    deleteQuiz(quizId);
  };

  const formatDate = (isoString) => {
    if (!isoString) return 'Never';
    const date = new Date(isoString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h ago`;
    const diffDays = Math.floor(diffHours / 24);
    return `${diffDays}d ago`;
  };

  if (quizzes.length === 0) {
    return (
      <div className="quiz-list__empty">
        <HelpCircle size={48} className="quiz-list__empty-icon" />
        <h3 className="quiz-list__empty-title">No quizzes yet</h3>
        <p className="quiz-list__empty-text">
          Generate a quiz with AI to test your knowledge.
        </p>
        <div className="quiz-list__button-group">
          <Button
            variant="primary"
            size="sm"
            leftIcon={<Zap size={16} />}
            onClick={() => setIsAIModalOpen(true)}
          >
            Generate Quiz
          </Button>
        </div>
        <AIQuizModal
          isOpen={isAIModalOpen}
          onClose={() => setIsAIModalOpen(false)}
          notebookId={activeNotebookId}
          onQuizCreated={onSelectQuiz}
        />
      </div>
    );
  }

  return (
    <div className="quiz-list">
      <div className="quiz-list__grid">
        {quizzes.map(quiz => {
          const questionCount = getQuestionCount(quiz.id);
          return (
            <div
              key={quiz.id}
              className="quiz-card"
              onClick={() => onSelectQuiz(quiz.id)}
              role="button"
              tabIndex={0}
              onKeyDown={e => { if (e.key === 'Enter') onSelectQuiz(quiz.id); }}
            >
              <div className="quiz-card__header">
                <span className="quiz-card__title">{quiz.title}</span>
                <div className="quiz-card__actions">
                  <button
                    className="quiz-card__action-btn quiz-card__action-btn--danger"
                    onClick={e => handleDelete(e, quiz.id)}
                    type="button"
                    aria-label="Delete quiz"
                  >
                    <Trash2 size={12} />
                  </button>
                </div>
              </div>
              <div className="quiz-card__meta">
                {quiz.isAiGenerated && (
                  <span className="quiz-card__meta-item quiz-card__meta-item--ai">
                    <Zap size={12} />
                    AI
                  </span>
                )}
                <span className="quiz-card__meta-item">
                  <Layers size={12} />
                  {questionCount} {questionCount === 1 ? 'question' : 'questions'}
                </span>
                <span className="quiz-card__meta-item">
                  <Clock size={12} />
                  {formatDate(quiz.createdAt)}
                </span>
              </div>
            </div>
          );
        })}
      </div>
      <div className="quiz-list__footer">
        <div className="quiz-list__button-group">
          <Button
            variant="secondary"
            size="sm"
            leftIcon={<Zap size={16} />}
            onClick={() => setIsAIModalOpen(true)}
          >
            Generate Quiz
          </Button>
        </div>
      </div>
      <AIQuizModal
        isOpen={isAIModalOpen}
        onClose={() => setIsAIModalOpen(false)}
        notebookId={activeNotebookId}
        onQuizCreated={onSelectQuiz}
      />
    </div>
  );
}

export default QuizList;
