import { createContext, useContext, useState, useCallback } from 'react';

const BACKEND_API_URL = import.meta.env.VITE_BACKEND_API_URL || 'http://127.0.0.1:8000';
const QuizContext = createContext(null);

let nextQuizId = 1;
let nextQuestionId = 1;

function generateQuizId() {
  return `quiz-${Date.now()}-${nextQuizId++}`;
}
function generateQuestionId() {
  return `ques-${Date.now()}-${nextQuestionId++}`;
}

export function QuizProvider({ children }) {
  const [quizzes, setQuizzes] = useState([]);
  const [questions, setQuestions] = useState([]);

  // --- Quiz CRUD ---
  const createQuiz = useCallback((notebookId, title = 'Untitled Quiz', { isAiGenerated = false } = {}) => {
    const newQuiz = {
      id: generateQuizId(),
      notebookId,
      title,
      createdAt: new Date().toISOString(),
      isAiGenerated,
    };
    setQuizzes(prev => [...prev, newQuiz]);
    return newQuiz;
  }, []);

  const deleteQuiz = useCallback((quizId) => {
    setQuizzes(prev => prev.filter(q => q.id !== quizId));
    setQuestions(prev => prev.filter(q => q.quizId !== quizId));
  }, []);

  const getQuizzesForNotebook = useCallback((notebookId) => {
    return quizzes.filter(q => q.notebookId === notebookId);
  }, [quizzes]);

  const getQuestionsForQuiz = useCallback((quizId) => {
    return questions
      .filter(q => q.quizId === quizId)
      .sort((a, b) => a.position - b.position);
  }, [questions]);

  const getQuestionCount = useCallback((quizId) => {
    return questions.filter(q => q.quizId === quizId).length;
  }, [questions]);

  // --- AI Quiz Generation ---
  const generateAIQuiz = useCallback(async (notebookId, title, prompt, count, { sources = [], onStatus } = {}) => {
  onStatus?.('Generating quiz...');

  const sourceIds = sources
    .map((source) => source.fileName || source.url || source.title || source.id)
    .filter(Boolean);

  const response = await fetch(`${BACKEND_API_URL}/api/v1/quizzes`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      topic: prompt,
      source_ids: sourceIds,
      count,
    }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    const msg = errorData?.detail
      ? JSON.stringify(errorData.detail)
      : errorData?.message;

    throw new Error(msg || `Backend error: ${response.status}`);
  }

  const data = await response.json();
  const items = data?.questions || [];

  if (items.length === 0) {
    throw new Error('No quiz questions could be generated from the selected source.');
  }

  const quiz = createQuiz(notebookId, title, { isAiGenerated: true });

  const newQuestions = items.slice(0, count).map((item, i) => {
    const options = Array.isArray(item.options) ? item.options : ['', '', '', ''];
    const correctAnswerIndex = options.findIndex(
      (option) => option === item.correct_answer
    );

    return {
      id: generateQuestionId(),
      quizId: quiz.id,
      question: item.question || '',
      options,
      correctAnswer: correctAnswerIndex >= 0 ? correctAnswerIndex : 0,
      explanation: item.explanation || '',
      position: i,
    };
  });

  setQuestions(prev => [...prev, ...newQuestions]);
  return quiz;
}, [createQuiz]);

  return (
    <QuizContext.Provider value={{
      quizzes,
      questions,
      createQuiz,
      deleteQuiz,
      getQuizzesForNotebook,
      getQuestionsForQuiz,
      getQuestionCount,
      generateAIQuiz,
    }}>
      {children}
    </QuizContext.Provider>
  );
}

// eslint-disable-next-line react-refresh/only-export-components
export function useQuizzes() {
  const context = useContext(QuizContext);
  if (!context) {
    throw new Error('useQuizzes must be used within QuizProvider');
  }
  return context;
}

export default QuizContext;
