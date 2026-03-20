import { useState } from 'react';
import { ChevronLeft, ArrowLeft, ArrowRight, RotateCcw, CheckCircle, XCircle } from 'lucide-react';
import Button from '../../../components/ui/Button';
import IconButton from '../../../components/ui/IconButton';
import { useQuizzes } from '../../../contexts/QuizContext';
import './QuizViewer.css';

function QuizViewer({ quizId, onBack }) {
  const { quizzes, getQuestionsForQuiz, getQuestionCount } = useQuizzes();
  const questions = getQuestionsForQuiz(quizId);
  const questionCount = getQuestionCount(quizId);
  const quiz = quizzes.find(q => q.id === quizId);

  const [currentIndex, setCurrentIndex] = useState(0);
  const [selectedAnswers, setSelectedAnswers] = useState({});
  const [submitted, setSubmitted] = useState(false);

  const currentQuestion = questions[currentIndex];
  const progress = questionCount > 0 ? ((currentIndex + 1) / questionCount) * 100 : 0;
  const answeredCount = Object.keys(selectedAnswers).length;
  const allAnswered = answeredCount === questionCount;

  const score = submitted
    ? questions.reduce((acc, q, i) => acc + (selectedAnswers[i] === q.correctAnswer ? 1 : 0), 0)
    : 0;

  const goNext = () => {
    setCurrentIndex(prev => Math.min(prev + 1, questions.length - 1));
  };

  const goPrev = () => {
    setCurrentIndex(prev => Math.max(prev - 1, 0));
  };

  const selectAnswer = (optionIndex) => {
    if (submitted) return;
    setSelectedAnswers(prev => ({ ...prev, [currentIndex]: optionIndex }));
  };

  const handleSubmit = () => {
    setSubmitted(true);
    setCurrentIndex(0);
  };

  const handleRetake = () => {
    setCurrentIndex(0);
    setSelectedAnswers({});
    setSubmitted(false);
  };

  if (!quiz || questionCount === 0) {
    return (
      <div className="quiz-viewer__empty">
        <p>No questions available.</p>
        <Button variant="ghost" size="sm" onClick={onBack}>
          Back to Quizzes
        </Button>
      </div>
    );
  }

  const getOptionClass = (optionIndex) => {
    const base = 'quiz-viewer__option';
    const isSelected = selectedAnswers[currentIndex] === optionIndex;

    if (!submitted) {
      return `${base} ${isSelected ? `${base}--selected` : ''}`;
    }

    const isCorrect = optionIndex === currentQuestion.correctAnswer;
    if (isCorrect) return `${base} ${base}--correct`;
    if (isSelected && !isCorrect) return `${base} ${base}--incorrect`;
    return base;
  };

  return (
    <div className="quiz-viewer">
      {/* Header */}
      <div className="quiz-viewer__header">
        <button className="quiz-viewer__back" onClick={onBack} type="button">
          <ChevronLeft size={18} />
          <span className="quiz-viewer__title">{quiz.title}</span>
        </button>
        <span className="quiz-viewer__counter">
          {currentIndex + 1} / {questionCount}
        </span>
      </div>

      {/* Progress bar */}
      <div className="quiz-viewer__progress">
        <div className="quiz-viewer__progress-fill" style={{ width: `${progress}%` }} />
      </div>

      {/* Results banner */}
      {submitted && (
        <div className="quiz-viewer__results">
          <div className="quiz-viewer__score">
            <CheckCircle size={20} />
            <span>{score} / {questionCount} correct ({Math.round((score / questionCount) * 100)}%)</span>
          </div>
          <Button variant="ghost" size="sm" leftIcon={<RotateCcw size={14} />} onClick={handleRetake}>
            Retake
          </Button>
        </div>
      )}

      {/* Question */}
      <div className="quiz-viewer__question">
        <p className="quiz-viewer__question-text">{currentQuestion.question}</p>
      </div>

      {/* Options */}
      <div className="quiz-viewer__options">
        {currentQuestion.options.map((option, i) => (
          <button
            key={i}
            className={getOptionClass(i)}
            onClick={() => selectAnswer(i)}
            type="button"
            disabled={submitted}
          >
            <span className="quiz-viewer__option-letter">
              {String.fromCharCode(65 + i)}
            </span>
            <span className="quiz-viewer__option-text">{option}</span>
            {submitted && i === currentQuestion.correctAnswer && <CheckCircle size={16} className="quiz-viewer__option-icon" />}
            {submitted && selectedAnswers[currentIndex] === i && i !== currentQuestion.correctAnswer && <XCircle size={16} className="quiz-viewer__option-icon" />}
          </button>
        ))}
      </div>

      {/* Explanation (shown after submit) */}
      {submitted && currentQuestion.explanation && (
        <div className="quiz-viewer__explanation">
          <strong>Explanation:</strong> {currentQuestion.explanation}
        </div>
      )}

      {/* Navigation */}
      <div className="quiz-viewer__nav">
        <IconButton
          variant="ghost"
          size="md"
          label="Previous question"
          onClick={goPrev}
          disabled={currentIndex === 0}
        >
          <ArrowLeft size={18} />
        </IconButton>

        {!submitted && allAnswered && currentIndex === questionCount - 1 ? (
          <Button variant="primary" size="sm" onClick={handleSubmit}>
            Submit Quiz
          </Button>
        ) : (
          <IconButton
            variant="ghost"
            size="md"
            label="Next question"
            onClick={goNext}
            disabled={currentIndex >= questionCount - 1}
          >
            <ArrowRight size={18} />
          </IconButton>
        )}
      </div>
    </div>
  );
}

export default QuizViewer;
