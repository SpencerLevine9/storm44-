import { useState } from 'react';
import { Navigation } from './components/Navigation';
import { ChatInterface } from './components/ChatInterface';
import { FlashcardCreator } from './components/FlashcardCreator';
import { QuizGenerator } from './components/QuizGenerator';
import { StudyDashboard } from './components/StudyDashboard';
import { ThemeToggle } from './components/ThemeToggle';
import { ThemeProvider, useTheme } from './components/ThemeContext';
import { Toaster } from './components/ui/sonner';

function AppContent() {
  const [activeView, setActiveView] = useState<'chat' | 'flashcards' | 'quiz' | 'dashboard'>('dashboard');
  const { theme } = useTheme();

  return (
    <div className={`flex h-screen ${theme === 'dark' ? 'bg-slate-950' : 'bg-slate-50'}`}>
      <Navigation activeView={activeView} setActiveView={setActiveView} />
      
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header with theme toggle */}
        <header className={`border-b ${
          theme === 'dark' ? 'border-slate-800 bg-slate-900' : 'border-slate-200 bg-white'
        } px-6 py-4 flex justify-end items-center`}>
          <ThemeToggle />
        </header>

        <main className="flex-1 overflow-hidden">
          {activeView === 'dashboard' && <StudyDashboard />}
          {activeView === 'chat' && <ChatInterface />}
          {activeView === 'flashcards' && <FlashcardCreator />}
          {activeView === 'quiz' && <QuizGenerator />}
        </main>
      </div>
      
      <Toaster />
    </div>
  );
}

export default function App() {
  return (
    <ThemeProvider>
      <AppContent />
    </ThemeProvider>
  );
}
