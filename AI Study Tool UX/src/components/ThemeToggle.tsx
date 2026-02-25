import { Moon, Sun } from 'lucide-react';
import { Switch } from './ui/switch';
import { useTheme } from './ThemeContext';

export function ThemeToggle() {
  const { theme, toggleTheme } = useTheme();

  return (
    <div className={`flex items-center gap-3 px-4 py-2 rounded-lg ${
      theme === 'dark' ? 'bg-slate-800' : 'bg-slate-100'
    }`}>
      <Sun className={`w-4 h-4 ${
        theme === 'light' ? 'text-amber-500' : 'text-slate-500'
      }`} />
      <Switch
        checked={theme === 'dark'}
        onCheckedChange={toggleTheme}
      />
      <Moon className={`w-4 h-4 ${
        theme === 'dark' ? 'text-blue-400' : 'text-slate-400'
      }`} />
    </div>
  );
}
