import { useState } from 'react';
import { Send, Sparkles, BookOpen, Calculator, Lightbulb } from 'lucide-react';
import { Button } from './ui/button';
import { Textarea } from './ui/textarea';
import { Card, CardContent } from './ui/card';
import { Badge } from './ui/badge';
import { useTheme } from './ThemeContext';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export function ChatInterface() {
  const { theme } = useTheme();
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: "Hi! I'm your AI study tutor. I can help you understand complex topics, solve problems, create study materials, and answer questions. What would you like to study today?",
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');

  const quickPrompts = [
    { text: 'Explain quantum mechanics', icon: BookOpen },
    { text: 'Help me solve this equation', icon: Calculator },
    { text: 'Create a study plan', icon: Lightbulb },
  ];

  const handleSend = () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');

    // Simulate AI response
    setTimeout(() => {
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: "I'd be happy to help you with that! This is a simulated response. In a real implementation, this would connect to an AI service to provide intelligent, contextual answers to your study questions.",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, aiMessage]);
    }, 1000);
  };

  return (
    <div className={`h-full flex flex-col ${
      theme === 'dark' ? 'bg-slate-950' : 'bg-white'
    }`}>
      {/* Header */}
      <div className={`border-b p-6 ${
        theme === 'dark' ? 'border-slate-800' : 'border-slate-200'
      }`}>
        <div className="flex items-center gap-2 mb-2">
          <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-purple-600 rounded-full flex items-center justify-center">
            <Sparkles className="w-4 h-4 text-white" />
          </div>
          <h2 className={theme === 'dark' ? 'text-slate-100' : 'text-slate-900'}>AI Study Tutor</h2>
        </div>
        <p className={theme === 'dark' ? 'text-slate-400' : 'text-slate-600'}>Ask me anything about your studies</p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div className={`max-w-2xl ${message.role === 'user' ? 'order-2' : 'order-1'}`}>
              <div
                className={`rounded-2xl p-4 ${
                  message.role === 'user'
                    ? 'bg-gradient-to-br from-blue-600 to-purple-600 text-white'
                    : theme === 'dark'
                    ? 'bg-slate-800 text-slate-100 border border-slate-700'
                    : 'bg-slate-100 text-slate-900'
                }`}
              >
                <p className="whitespace-pre-wrap">{message.content}</p>
              </div>
              <p className={`text-xs mt-2 px-4 ${
                theme === 'dark' ? 'text-slate-600' : 'text-slate-500'
              }`}>
                {message.timestamp.toLocaleTimeString()}
              </p>
            </div>
          </div>
        ))}

        {/* Quick Prompts - show only when few messages */}
        {messages.length <= 1 && (
          <div className="space-y-3">
            <p className={`text-sm ${
              theme === 'dark' ? 'text-slate-400' : 'text-slate-600'
            }`}>Try asking:</p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              {quickPrompts.map((prompt, index) => (
                <Card
                  key={index}
                  className={`cursor-pointer hover:shadow-sm transition-all ${
                    theme === 'dark'
                      ? 'bg-slate-900 border-slate-800 hover:border-blue-500'
                      : 'bg-white border-slate-200 hover:border-blue-300'
                  }`}
                  onClick={() => setInput(prompt.text)}
                >
                  <CardContent className="p-4 flex items-start gap-3">
                    <prompt.icon className={`w-5 h-5 flex-shrink-0 ${
                      theme === 'dark' ? 'text-blue-400' : 'text-blue-600'
                    }`} />
                    <p className={`text-sm ${
                      theme === 'dark' ? 'text-slate-200' : 'text-slate-900'
                    }`}>{prompt.text}</p>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className={`border-t p-6 ${
        theme === 'dark'
          ? 'border-slate-800 bg-slate-900'
          : 'border-slate-200 bg-slate-50'
      }`}>
        <div className="flex gap-3">
          <Textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSend();
              }
            }}
            placeholder="Ask a study question..."
            className={`resize-none ${
              theme === 'dark'
                ? 'bg-slate-800 border-slate-700 text-slate-100 placeholder:text-slate-500'
                : 'bg-white border-slate-200 text-slate-900 placeholder:text-slate-400'
            }`}
            rows={3}
          />
          <Button
            onClick={handleSend}
            className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 self-end"
            disabled={!input.trim()}
          >
            <Send className="w-4 h-4" />
          </Button>
        </div>
        <p className={`text-xs mt-2 ${
          theme === 'dark' ? 'text-slate-600' : 'text-slate-500'
        }`}>Press Enter to send, Shift+Enter for new line</p>
      </div>
    </div>
  );
}
