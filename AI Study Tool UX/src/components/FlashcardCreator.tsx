import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';
import { Badge } from './ui/badge';
import { Plus, RotateCcw, Trash2, Sparkles } from 'lucide-react';
import { toast } from 'sonner@2.0.3';
import { useTheme } from './ThemeContext';

interface Flashcard {
  id: string;
  front: string;
  back: string;
  topic: string;
}

export function FlashcardCreator() {
  const { theme } = useTheme();
  const [flashcards, setFlashcards] = useState<Flashcard[]>([
    {
      id: '1',
      front: 'What is the speed of light in a vacuum?',
      back: 'Approximately 299,792,458 meters per second (or about 186,282 miles per second)',
      topic: 'Physics',
    },
    {
      id: '2',
      front: 'Define photosynthesis',
      back: 'The process by which green plants and some other organisms use sunlight to synthesize foods from carbon dioxide and water',
      topic: 'Biology',
    },
  ]);
  const [newCard, setNewCard] = useState({ front: '', back: '', topic: '' });
  const [flippedCards, setFlippedCards] = useState<Set<string>>(new Set());
  const [isGenerating, setIsGenerating] = useState(false);

  const addFlashcard = () => {
    if (!newCard.front.trim() || !newCard.back.trim()) {
      toast.error('Please fill in both front and back of the card');
      return;
    }

    const flashcard: Flashcard = {
      id: Date.now().toString(),
      ...newCard,
      topic: newCard.topic || 'General',
    };

    setFlashcards([flashcard, ...flashcards]);
    setNewCard({ front: '', back: '', topic: '' });
    toast.success('Flashcard created!');
  };

  const deleteFlashcard = (id: string) => {
    setFlashcards(flashcards.filter((card) => card.id !== id));
    toast.success('Flashcard deleted');
  };

  const toggleFlip = (id: string) => {
    setFlippedCards((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(id)) {
        newSet.delete(id);
      } else {
        newSet.add(id);
      }
      return newSet;
    });
  };

  const generateWithAI = () => {
    setIsGenerating(true);
    toast.info('Generating flashcards with AI...');
    
    setTimeout(() => {
      setIsGenerating(false);
      toast.success('AI flashcard generation is a premium feature. Connect to Supabase to enable!');
    }, 2000);
  };

  return (
    <div className={`h-full overflow-y-auto ${
      theme === 'dark' ? 'bg-slate-950' : 'bg-slate-50'
    }`}>
      <div className="p-8">
        <div className="mb-8">
          <h2 className={`mb-2 ${
            theme === 'dark' ? 'text-slate-100' : 'text-slate-900'
          }`}>Flashcard Creator</h2>
          <p className={theme === 'dark' ? 'text-slate-400' : 'text-slate-600'}>
            Create and review your study flashcards
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Create New Flashcard */}
          <div className="lg:col-span-1">
            <Card className={
              theme === 'dark'
                ? 'bg-slate-900 border-slate-800'
                : 'bg-white border-slate-200'
            }>
              <CardHeader>
                <CardTitle className={theme === 'dark' ? 'text-slate-100' : 'text-slate-900'}>
                  Create Flashcard
                </CardTitle>
                <CardDescription className={theme === 'dark' ? 'text-slate-400' : 'text-slate-600'}>
                  Add a new card to your deck
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className={`text-sm mb-2 block ${
                    theme === 'dark' ? 'text-slate-300' : 'text-slate-700'
                  }`}>Topic</label>
                  <Input
                    value={newCard.topic}
                    onChange={(e) => setNewCard({ ...newCard, topic: e.target.value })}
                    placeholder="e.g., Biology, Math..."
                    className={
                      theme === 'dark'
                        ? 'bg-slate-800 border-slate-700 text-slate-100 placeholder:text-slate-500'
                        : 'bg-white border-slate-200 text-slate-900 placeholder:text-slate-400'
                    }
                  />
                </div>
                <div>
                  <label className={`text-sm mb-2 block ${
                    theme === 'dark' ? 'text-slate-300' : 'text-slate-700'
                  }`}>Front (Question)</label>
                  <Textarea
                    value={newCard.front}
                    onChange={(e) => setNewCard({ ...newCard, front: e.target.value })}
                    placeholder="Enter question or term..."
                    rows={3}
                    className={
                      theme === 'dark'
                        ? 'bg-slate-800 border-slate-700 text-slate-100 placeholder:text-slate-500'
                        : 'bg-white border-slate-200 text-slate-900 placeholder:text-slate-400'
                    }
                  />
                </div>
                <div>
                  <label className={`text-sm mb-2 block ${
                    theme === 'dark' ? 'text-slate-300' : 'text-slate-700'
                  }`}>Back (Answer)</label>
                  <Textarea
                    value={newCard.back}
                    onChange={(e) => setNewCard({ ...newCard, back: e.target.value })}
                    placeholder="Enter answer or definition..."
                    rows={3}
                    className={
                      theme === 'dark'
                        ? 'bg-slate-800 border-slate-700 text-slate-100 placeholder:text-slate-500'
                        : 'bg-white border-slate-200 text-slate-900 placeholder:text-slate-400'
                    }
                  />
                </div>
                <Button onClick={addFlashcard} className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700">
                  <Plus className="w-4 h-4 mr-2" />
                  Add Flashcard
                </Button>
                <Button
                  variant="outline"
                  onClick={generateWithAI}
                  className={`w-full ${
                    theme === 'dark'
                      ? 'border-slate-700 text-slate-300 hover:bg-slate-800'
                      : 'border-slate-300 text-slate-700 hover:bg-slate-50'
                  }`}
                  disabled={isGenerating}
                >
                  <Sparkles className="w-4 h-4 mr-2" />
                  Generate with AI
                </Button>
              </CardContent>
            </Card>
          </div>

          {/* Flashcard Deck */}
          <div className="lg:col-span-2">
            <div className="mb-4 flex items-center justify-between">
              <div>
                <p className={theme === 'dark' ? 'text-slate-100' : 'text-slate-900'}>
                  Your Deck
                </p>
                <p className={`text-sm ${
                  theme === 'dark' ? 'text-slate-400' : 'text-slate-600'
                }`}>{flashcards.length} cards</p>
              </div>
            </div>

            {flashcards.length === 0 ? (
              <Card className={`py-12 ${
                theme === 'dark'
                  ? 'bg-slate-900 border-slate-800'
                  : 'bg-white border-slate-200'
              }`}>
                <CardContent className="text-center">
                  <div className={`w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4 ${
                    theme === 'dark' ? 'bg-slate-800' : 'bg-slate-100'
                  }`}>
                    <Plus className={`w-8 h-8 ${
                      theme === 'dark' ? 'text-slate-500' : 'text-slate-400'
                    }`} />
                  </div>
                  <p className={`mb-1 ${
                    theme === 'dark' ? 'text-slate-100' : 'text-slate-900'
                  }`}>No flashcards yet</p>
                  <p className={`text-sm ${
                    theme === 'dark' ? 'text-slate-400' : 'text-slate-600'
                  }`}>Create your first flashcard to get started</p>
                </CardContent>
              </Card>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {flashcards.map((card) => (
                  <Card
                    key={card.id}
                    className={`cursor-pointer hover:shadow-md transition-all relative group ${
                      theme === 'dark'
                        ? 'bg-slate-900 border-slate-800 hover:shadow-blue-900/20'
                        : 'bg-white border-slate-200'
                    }`}
                    onClick={() => toggleFlip(card.id)}
                  >
                    <CardContent className="p-6 min-h-[200px] flex flex-col">
                      <div className="flex items-start justify-between mb-4">
                        <Badge variant="secondary" className={
                          theme === 'dark'
                            ? 'bg-slate-800 text-slate-300 border-slate-700'
                            : 'bg-slate-100 text-slate-700'
                        }>{card.topic}</Badge>
                        <Button
                          variant="ghost"
                          size="sm"
                          className={`opacity-0 group-hover:opacity-100 transition-opacity -mt-2 -mr-2 ${
                            theme === 'dark' ? 'hover:bg-slate-800' : 'hover:bg-slate-100'
                          }`}
                          onClick={(e) => {
                            e.stopPropagation();
                            deleteFlashcard(card.id);
                          }}
                        >
                          <Trash2 className="w-4 h-4 text-red-500" />
                        </Button>
                      </div>

                      <div className="flex-1 flex items-center justify-center text-center">
                        {flippedCards.has(card.id) ? (
                          <div>
                            <p className="text-xs text-slate-500 mb-2">ANSWER</p>
                            <p className={
                              theme === 'dark' ? 'text-slate-100' : 'text-slate-900'
                            }>{card.back}</p>
                          </div>
                        ) : (
                          <div>
                            <p className="text-xs text-slate-500 mb-2">QUESTION</p>
                            <p className={
                              theme === 'dark' ? 'text-slate-100' : 'text-slate-900'
                            }>{card.front}</p>
                          </div>
                        )}
                      </div>

                      <div className="flex items-center justify-center gap-2 mt-4 text-xs text-slate-500">
                        <RotateCcw className="w-3 h-3" />
                        Click to flip
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
