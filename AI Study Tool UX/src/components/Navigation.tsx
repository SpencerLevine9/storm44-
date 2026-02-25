import { MessageSquare, Layers, FileQuestion, LayoutDashboard, BookOpen } from 'lucide-react';
import { Button } from './ui/button';
import { useTheme } from './ThemeContext';

interface NavigationProps {
  activeView: 'chat' | 'flashcards' | 'quiz' | 'dashboard';
  setActiveView: (view: 'chat' | 'flashcards' | 'quiz' | 'dashboard') => void;
}

export function Navigation({ activeView, setActiveView }: NavigationProps) {
  const { theme } = useTheme();
  const navItems = [
    { id: 'dashboard' as const, icon: LayoutDashboard, label: 'Dashboard' },
    { id: 'chat' as const, icon: MessageSquare, label: 'AI Tutor' },
    { id: 'flashcards' as const, icon: Layers, label: 'Flashcards' },
    { id: 'quiz' as const, icon: FileQuestion, label: 'Quiz Me' },
  ];

  return (
    <nav className={`w-64 border-r flex flex-col ${
      theme === 'dark' 
        ? 'bg-slate-900 border-slate-800' 
        : 'bg-white border-slate-200'
    }`}>
      <div className={`p-6 border-b ${
        theme === 'dark' ? 'border-slate-800' : 'border-slate-200'
      }`}>
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
            <BookOpen className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className={theme === 'dark' ? 'text-slate-100' : 'text-slate-900'}>Storm44</h1>
            <p className={`text-xs ${theme === 'dark' ? 'text-slate-400' : 'text-slate-500'}`}>Your AI Study Companion</p>
          </div>
        </div>
      </div>

      <div className="flex-1 p-4 space-y-2">
        {navItems.map((item) => (
          <Button
            key={item.id}
            variant={activeView === item.id ? 'secondary' : 'ghost'}
            className={`w-full justify-start ${
              theme === 'dark'
                ? 'text-slate-300 hover:text-slate-100 hover:bg-slate-800'
                : 'text-slate-700 hover:text-slate-900 hover:bg-slate-100'
            }`}
            onClick={() => setActiveView(item.id)}
          >
            <item.icon className="w-4 h-4 mr-3" />
            {item.label}
          </Button>
        ))}
      </div>

      <div className={`p-4 border-t ${
        theme === 'dark' ? 'border-slate-800' : 'border-slate-200'
      }`}>
        <div className={`p-4 rounded-lg border ${
          theme === 'dark'
            ? 'bg-gradient-to-br from-blue-950 to-purple-950 border-blue-900'
            : 'bg-gradient-to-br from-blue-50 to-purple-50 border-blue-100'
        }`}>
          <p className={`text-xs mb-2 ${
            theme === 'dark' ? 'text-slate-300' : 'text-slate-600'
          }`}>
            Keep your study sessions, flashcards, and progress synced across devices
          </p>
          <Button size="sm" className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700">
            Save Progress
          </Button>
        </div>
      </div>
    </nav>
  );
}
