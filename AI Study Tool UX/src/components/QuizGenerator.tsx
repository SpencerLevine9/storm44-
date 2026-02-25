import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { RadioGroup, RadioGroupItem } from './ui/radio-group';
import { Label } from './ui/label';
import { Badge } from './ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Sparkles, CheckCircle2, XCircle, RotateCcw } from 'lucide-react';
import { Progress } from './ui/progress';
import { toast } from 'sonner@2.0.3';
import { useTheme } from './ThemeContext';

interface Question {
  id: string;
  question: string;
  options: string[];
  correctAnswer: number;
  topic: string;
}

export function QuizGenerator() {
  const { theme } = useTheme();
  const [quizStarted, setQuizStarted] = useState(false);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [selectedAnswers, setSelectedAnswers] = useState<{ [key: number]: number }>({});
  const [showResults, setShowResults] = useState(false);
  const [topic, setTopic] = useState('');
  const [difficulty, setDifficulty] = useState('medium');

  const sampleQuestions: Question[] = [
    {
      id: '1',
      question: 'What is the powerhouse of the cell?',
      options: ['Nucleus', 'Mitochondria', 'Ribosome', 'Endoplasmic Reticulum'],
      correctAnswer: 1,
      topic: 'Biology',
    },
    {
      id: '2',
      question: 'Who painted the Mona Lisa?',
      options: ['Vincent van Gogh', 'Pablo Picasso', 'Leonardo da Vinci', 'Michelangelo'],
      correctAnswer: 2,
      topic: 'Art History',
    },
    {
      id: '3',
      question: 'What is the chemical symbol for gold?',
      options: ['Go', 'Gd', 'Au', 'Ag'],
      correctAnswer: 2,
      topic: 'Chemistry',
    },
  ];

  const [questions] = useState(sampleQuestions);

  const handleStartQuiz = () => {
    if (!topic.trim()) {
      toast.error('Please enter a topic for your quiz');
      return;
    }
    setQuizStarted(true);
    toast.success('Quiz started! Good luck! 🎯');
  };

  const handleAnswerSelect = (answerIndex: number) => {
    setSelectedAnswers({ ...selectedAnswers, [currentQuestion]: answerIndex });
  };

  const handleNext = () => {
    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
    } else {
      setShowResults(true);
    }
  };

  const handlePrevious = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(currentQuestion - 1);
    }
  };

  const calculateScore = () => {
    let correct = 0;
    questions.forEach((q, index) => {
      if (selectedAnswers[index] === q.correctAnswer) {
        correct++;
      }
    });
    return { correct, total: questions.length, percentage: (correct / questions.length) * 100 };
  };

  const resetQuiz = () => {
    setQuizStarted(false);
    setCurrentQuestion(0);
    setSelectedAnswers({});
    setShowResults(false);
    setTopic('');
  };

  if (!quizStarted) {
    return (
      <div className={`h-full overflow-y-auto flex items-center justify-center ${
        theme === 'dark' ? 'bg-slate-950' : 'bg-slate-50'
      }`}>
        <Card className={`w-full max-w-lg mx-4 ${
          theme === 'dark'
            ? 'bg-slate-900 border-slate-800'
            : 'bg-white border-slate-200'
        }`}>
          <CardHeader>
            <CardTitle className={theme === 'dark' ? 'text-slate-100' : 'text-slate-900'}>
              Generate a Quiz
            </CardTitle>
            <CardDescription className={theme === 'dark' ? 'text-slate-400' : 'text-slate-600'}>
              Create an AI-powered quiz on any topic
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div>
              <Label htmlFor="topic" className={`mb-2 block ${
                theme === 'dark' ? 'text-slate-300' : 'text-slate-700'
              }`}>Topic</Label>
              <Input
                id="topic"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                placeholder="e.g., World War II, Calculus, Biology..."
                className={
                  theme === 'dark'
                    ? 'bg-slate-800 border-slate-700 text-slate-100 placeholder:text-slate-500'
                    : 'bg-white border-slate-200 text-slate-900 placeholder:text-slate-400'
                }
              />
            </div>

            <div>
              <Label htmlFor="difficulty" className={`mb-2 block ${
                theme === 'dark' ? 'text-slate-300' : 'text-slate-700'
              }`}>Difficulty</Label>
              <Select value={difficulty} onValueChange={setDifficulty}>
                <SelectTrigger id="difficulty" className={
                  theme === 'dark'
                    ? 'bg-slate-800 border-slate-700 text-slate-100'
                    : 'bg-white border-slate-200 text-slate-900'
                }>
                  <SelectValue placeholder="Select difficulty" />
                </SelectTrigger>
                <SelectContent className={
                  theme === 'dark'
                    ? 'bg-slate-800 border-slate-700'
                    : 'bg-white border-slate-200'
                }>
                  <SelectItem value="easy" className={theme === 'dark' ? 'text-slate-100' : 'text-slate-900'}>Easy</SelectItem>
                  <SelectItem value="medium" className={theme === 'dark' ? 'text-slate-100' : 'text-slate-900'}>Medium</SelectItem>
                  <SelectItem value="hard" className={theme === 'dark' ? 'text-slate-100' : 'text-slate-900'}>Hard</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className={`rounded-lg p-4 ${
              theme === 'dark'
                ? 'bg-blue-950 bg-opacity-50 border border-blue-900'
                : 'bg-blue-50 border border-blue-200'
            }`}>
              <div className="flex items-start gap-3">
                <Sparkles className={`w-5 h-5 flex-shrink-0 mt-0.5 ${
                  theme === 'dark' ? 'text-blue-400' : 'text-blue-600'
                }`} />
                <div>
                  <p className={`text-sm mb-1 ${
                    theme === 'dark' ? 'text-slate-200' : 'text-slate-900'
                  }`}>AI-Powered Quizzes</p>
                  <p className={`text-xs ${
                    theme === 'dark' ? 'text-slate-400' : 'text-slate-600'
                  }`}>
                    Our AI generates custom questions tailored to your topic and difficulty level
                  </p>
                </div>
              </div>
            </div>

            <Button onClick={handleStartQuiz} className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700">
              <Sparkles className="w-4 h-4 mr-2" />
              Generate & Start Quiz
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (showResults) {
    const score = calculateScore();
    return (
      <div className={`h-full overflow-y-auto flex items-center justify-center ${
        theme === 'dark' ? 'bg-slate-950' : 'bg-slate-50'
      }`}>
        <Card className={`w-full max-w-2xl mx-4 ${
          theme === 'dark'
            ? 'bg-slate-900 border-slate-800'
            : 'bg-white border-slate-200'
        }`}>
          <CardHeader>
            <CardTitle className={theme === 'dark' ? 'text-slate-100' : 'text-slate-900'}>
              Quiz Results
            </CardTitle>
            <CardDescription className={theme === 'dark' ? 'text-slate-400' : 'text-slate-600'}>
              Here's how you did!
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="text-center py-8">
              <div className="w-32 h-32 mx-auto mb-6 relative">
                <svg className="transform -rotate-90 w-32 h-32">
                  <circle
                    cx="64"
                    cy="64"
                    r="56"
                    stroke={theme === 'dark' ? '#334155' : '#e2e8f0'}
                    strokeWidth="12"
                    fill="transparent"
                  />
                  <circle
                    cx="64"
                    cy="64"
                    r="56"
                    stroke={score.percentage >= 70 ? '#10b981' : score.percentage >= 50 ? '#f59e0b' : '#ef4444'}
                    strokeWidth="12"
                    fill="transparent"
                    strokeDasharray={`${2 * Math.PI * 56}`}
                    strokeDashoffset={`${2 * Math.PI * 56 * (1 - score.percentage / 100)}`}
                    strokeLinecap="round"
                  />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center">
                  <span className={theme === 'dark' ? 'text-slate-100' : 'text-slate-900'}>
                    {Math.round(score.percentage)}%
                  </span>
                </div>
              </div>
              <p className={`mb-2 ${
                theme === 'dark' ? 'text-slate-100' : 'text-slate-900'
              }`}>
                You got {score.correct} out of {score.total} correct
              </p>
              <p className={theme === 'dark' ? 'text-slate-400' : 'text-slate-600'}>
                {score.percentage >= 70
                  ? '🎉 Excellent work!'
                  : score.percentage >= 50
                  ? '👍 Good effort!'
                  : '💪 Keep practicing!'}
              </p>
            </div>

            <div className="space-y-4">
              {questions.map((q, index) => {
                const userAnswer = selectedAnswers[index];
                const isCorrect = userAnswer === q.correctAnswer;
                return (
                  <div key={q.id} className={`border rounded-lg p-4 ${
                    theme === 'dark'
                      ? 'border-slate-700 bg-slate-800'
                      : 'border-slate-200 bg-white'
                  }`}>
                    <div className="flex items-start gap-3 mb-3">
                      {isCorrect ? (
                        <CheckCircle2 className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
                      ) : (
                        <XCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
                      )}
                      <div className="flex-1">
                        <p className={`mb-2 ${
                          theme === 'dark' ? 'text-slate-100' : 'text-slate-900'
                        }`}>{q.question}</p>
                        <div className="space-y-1">
                          <p className="text-sm">
                            <span className={theme === 'dark' ? 'text-slate-400' : 'text-slate-600'}>Your answer: </span>
                            <span className={isCorrect ? 'text-green-400' : 'text-red-400'}>
                              {userAnswer !== undefined ? q.options[userAnswer] : 'Not answered'}
                            </span>
                          </p>
                          {!isCorrect && (
                            <p className="text-sm">
                              <span className={theme === 'dark' ? 'text-slate-400' : 'text-slate-600'}>Correct answer: </span>
                              <span className="text-green-400">{q.options[q.correctAnswer]}</span>
                            </p>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>

            <Button
              onClick={resetQuiz}
              className={`w-full ${
                theme === 'dark'
                  ? 'border-slate-700 text-slate-300 hover:bg-slate-800'
                  : 'border-slate-300 text-slate-700 hover:bg-slate-50'
              }`}
              variant="outline"
            >
              <RotateCcw className="w-4 h-4 mr-2" />
              Take Another Quiz
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  const currentQ = questions[currentQuestion];
  const progress = ((currentQuestion + 1) / questions.length) * 100;

  return (
    <div className={`h-full overflow-y-auto ${
      theme === 'dark' ? 'bg-slate-950' : 'bg-slate-50'
    }`}>
      <div className="p-8 max-w-3xl mx-auto">
        <div className="mb-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <p className={`text-sm ${
                theme === 'dark' ? 'text-slate-400' : 'text-slate-600'
              }`}>Question {currentQuestion + 1} of {questions.length}</p>
              <Badge variant="secondary" className={`mt-1 ${
                theme === 'dark'
                  ? 'bg-slate-800 text-slate-300 border-slate-700'
                  : 'bg-slate-100 text-slate-700'
              }`}>{currentQ.topic}</Badge>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={resetQuiz}
              className={
                theme === 'dark'
                  ? 'border-slate-700 text-slate-300 hover:bg-slate-800'
                  : 'border-slate-300 text-slate-700 hover:bg-slate-50'
              }
            >
              Exit Quiz
            </Button>
          </div>
          <Progress value={progress} className="h-2" />
        </div>

        <Card className={
          theme === 'dark'
            ? 'bg-slate-900 border-slate-800'
            : 'bg-white border-slate-200'
        }>
          <CardHeader>
            <CardTitle className={`text-xl ${
              theme === 'dark' ? 'text-slate-100' : 'text-slate-900'
            }`}>{currentQ.question}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <RadioGroup
              value={selectedAnswers[currentQuestion]?.toString()}
              onValueChange={(value) => handleAnswerSelect(parseInt(value))}
            >
              {currentQ.options.map((option, index) => (
                <div
                  key={index}
                  className={`flex items-center space-x-3 border rounded-lg p-4 transition-colors cursor-pointer ${
                    theme === 'dark'
                      ? 'border-slate-700 hover:border-blue-500 bg-slate-800'
                      : 'border-slate-200 hover:border-blue-300 bg-white'
                  }`}
                  onClick={() => handleAnswerSelect(index)}
                >
                  <RadioGroupItem value={index.toString()} id={`option-${index}`} />
                  <Label htmlFor={`option-${index}`} className={`flex-1 cursor-pointer ${
                    theme === 'dark' ? 'text-slate-200' : 'text-slate-900'
                  }`}>
                    {option}
                  </Label>
                </div>
              ))}
            </RadioGroup>

            <div className="flex gap-3 pt-4">
              <Button
                variant="outline"
                onClick={handlePrevious}
                disabled={currentQuestion === 0}
                className={`flex-1 ${
                  theme === 'dark'
                    ? 'border-slate-700 text-slate-300 hover:bg-slate-800'
                    : 'border-slate-300 text-slate-700 hover:bg-slate-50'
                }`}
              >
                Previous
              </Button>
              <Button
                onClick={handleNext}
                disabled={selectedAnswers[currentQuestion] === undefined}
                className="flex-1 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
              >
                {currentQuestion === questions.length - 1 ? 'Finish' : 'Next'}
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
