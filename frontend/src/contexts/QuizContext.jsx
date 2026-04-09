import { createContext, useContext, useState, useCallback } from 'react';
import { chatCompletion } from '../utils/openai';
import { buildContext, wrapContextPrompt } from '../utils/contextBuilder';

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
    const contextText = await buildContext(sources, onStatus);
    const contextBlock = wrapContextPrompt(contextText);

    onStatus?.('Generating content...');

    const systemPrompt =
      contextBlock +
      'You are a quiz generator. You must respond with valid JSON only. ' +
      'Return an object with a "questions" array. Each question has: ' +
      '"question" (string), "options" (array of exactly 4 strings), ' +
      '"correctAnswer" (integer index 0-3 into the options array), ' +
      '"explanation" (string explaining why the correct answer is right). ' +
      `Generate exactly ${count} multiple-choice questions.`;

    const userPrompt =
      `Topic/Material: ${prompt}\n\n` +
      `Create ${count} multiple-choice questions. ` +
      'Each must have 4 options with one correct answer. ' +
      'Make questions clear and explanations concise.';

    const raw = await chatCompletion(systemPrompt, userPrompt, {
      maxTokens: count * 200,
      temperature: 0.7,
      json: true,
    });

    const parsed = JSON.parse(raw);
    const items = parsed.questions || [];

    const quiz = createQuiz(notebookId, title, { isAiGenerated: true });

    const newQuestions = items.slice(0, count).map((item, i) => ({
      id: generateQuestionId(),
      quizId: quiz.id,
      question: item.question || '',
      options: item.options || ['', '', '', ''],
      correctAnswer: typeof item.correctAnswer === 'number' ? item.correctAnswer : 0,
      explanation: item.explanation || '',
      position: i,
    }));

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
