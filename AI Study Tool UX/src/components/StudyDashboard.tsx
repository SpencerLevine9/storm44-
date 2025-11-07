import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Progress } from './ui/progress';
import { Brain, Clock, Target, TrendingUp, Calendar, Youtube, FileText, Upload, Sparkles } from 'lucide-react';
import { Badge } from './ui/badge';
import { Input } from './ui/input';
import { Button } from './ui/button';
import { Label } from './ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { toast } from 'sonner@2.0.3';
import { useTheme } from './ThemeContext';

export function StudyDashboard() {
  const { theme } = useTheme();
  const [youtubeLink, setYoutubeLink] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const studyStats = [
    { label: 'Study Streak', value: '7 days', icon: Calendar, color: 'text-orange-600', bgColor: 'bg-orange-100' },
    { label: 'Total Study Time', value: '12.5 hrs', icon: Clock, color: 'text-blue-600', bgColor: 'bg-blue-100' },
    { label: 'Topics Mastered', value: '23', icon: Target, color: 'text-green-600', bgColor: 'bg-green-100' },
    { label: 'AI Interactions', value: '145', icon: Brain, color: 'text-purple-600', bgColor: 'bg-purple-100' },
  ];

  const handleYoutubeSubmit = () => {
    if (!youtubeLink.trim()) {
      toast.error('Please enter a YouTube link');
      return;
    }
    toast.success('Processing YouTube video... This feature will generate study materials from the video!');
    setYoutubeLink('');
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (file.type !== 'application/pdf') {
        toast.error('Please select a PDF file');
        return;
      }
      setSelectedFile(file);
      toast.success(`Selected: ${file.name}`);
    }
  };

  const handlePdfSubmit = () => {
    if (!selectedFile) {
      toast.error('Please select a PDF file');
      return;
    }
    toast.success('Processing PDF... This feature will extract content and generate study materials!');
    setSelectedFile(null);
  };

  return (
    <div className={`h-full overflow-y-auto ${
      theme === 'dark' ? 'bg-slate-950' : 'bg-slate-50'
    }`}>
      <div className="p-8">
        <div className="mb-8">
          <h2 className={`mb-2 ${
            theme === 'dark' ? 'text-slate-100' : 'text-slate-900'
          }`}>Welcome back! 👋</h2>
          <p className={theme === 'dark' ? 'text-slate-400' : 'text-slate-600'}>Here's your study progress overview</p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          {studyStats.map((stat) => (
            <Card key={stat.label} className={
              theme === 'dark' 
                ? 'bg-slate-900 border-slate-800' 
                : 'bg-white border-slate-200'
            }>
              <CardContent className="p-6">
                <div className="flex items-start justify-between">
                  <div>
                    <p className={`text-sm mb-1 ${
                      theme === 'dark' ? 'text-slate-400' : 'text-slate-600'
                    }`}>{stat.label}</p>
                    <p className={theme === 'dark' ? 'text-slate-100' : 'text-slate-900'}>{stat.value}</p>
                  </div>
                  <div className={`p-3 rounded-lg ${stat.bgColor} ${
                    theme === 'dark' ? 'bg-opacity-20' : ''
                  }`}>
                    <stat.icon className={`w-5 h-5 ${stat.color}`} />
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Import Study Materials */}
          <div className="lg:col-span-2">
            <Card className={
              theme === 'dark'
                ? 'bg-slate-900 border-slate-800'
                : 'bg-white border-slate-200'
            }>
              <CardHeader>
                <CardTitle className={theme === 'dark' ? 'text-slate-100' : 'text-slate-900'}>
                  Import Study Materials
                </CardTitle>
                <CardDescription className={theme === 'dark' ? 'text-slate-400' : 'text-slate-600'}>
                  Generate flashcards and quizzes from YouTube videos or PDFs
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Tabs defaultValue="youtube" className="w-full">
                  <TabsList className={`grid w-full grid-cols-2 ${
                    theme === 'dark'
                      ? 'bg-slate-800 border-slate-700'
                      : 'bg-slate-100'
                  }`}>
                    <TabsTrigger
                      value="youtube"
                      className={theme === 'dark' ? 'data-[state=active]:bg-slate-700' : ''}
                    >
                      <Youtube className="w-4 h-4 mr-2" />
                      YouTube
                    </TabsTrigger>
                    <TabsTrigger
                      value="pdf"
                      className={theme === 'dark' ? 'data-[state=active]:bg-slate-700' : ''}
                    >
                      <FileText className="w-4 h-4 mr-2" />
                      PDF
                    </TabsTrigger>
                  </TabsList>
                  
                  <TabsContent value="youtube" className="space-y-4 mt-6">
                    <div className="space-y-3">
                      <Label htmlFor="youtube-link" className={
                        theme === 'dark' ? 'text-slate-300' : 'text-slate-700'
                      }>
                        YouTube Video Link
                      </Label>
                      <div className="flex gap-3">
                        <Input
                          id="youtube-link"
                          value={youtubeLink}
                          onChange={(e) => setYoutubeLink(e.target.value)}
                          placeholder="https://www.youtube.com/watch?v=..."
                          className={`flex-1 ${
                            theme === 'dark'
                              ? 'bg-slate-800 border-slate-700 text-slate-100 placeholder:text-slate-500'
                              : 'bg-white border-slate-200 text-slate-900 placeholder:text-slate-400'
                          }`}
                        />
                        <Button onClick={handleYoutubeSubmit} className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700">
                          <Sparkles className="w-4 h-4 mr-2" />
                          Process
                        </Button>
                      </div>
                    </div>
                    
                    <div className={`rounded-lg p-4 ${
                      theme === 'dark'
                        ? 'bg-blue-950 bg-opacity-50 border border-blue-900'
                        : 'bg-blue-50 border border-blue-200'
                    }`}>
                      <div className="flex gap-3">
                        <Youtube className={`w-5 h-5 flex-shrink-0 ${
                          theme === 'dark' ? 'text-blue-400' : 'text-blue-600'
                        }`} />
                        <div>
                          <p className={`text-sm mb-1 ${
                            theme === 'dark' ? 'text-slate-200' : 'text-slate-900'
                          }`}>AI-Powered Video Analysis</p>
                          <p className={`text-xs ${
                            theme === 'dark' ? 'text-slate-400' : 'text-slate-600'
                          }`}>
                            Our AI will extract key concepts from the video and automatically generate flashcards and quiz questions
                          </p>
                        </div>
                      </div>
                    </div>
                  </TabsContent>
                  
                  <TabsContent value="pdf" className="space-y-4 mt-6">
                    <div className="space-y-3">
                      <Label htmlFor="pdf-upload" className={
                        theme === 'dark' ? 'text-slate-300' : 'text-slate-700'
                      }>
                        Upload PDF Document
                      </Label>
                      <div className="space-y-3">
                        <div className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
                          theme === 'dark'
                            ? 'border-slate-700 hover:border-blue-500 bg-slate-800 bg-opacity-50'
                            : 'border-slate-300 hover:border-blue-400 bg-slate-50'
                        }`}>
                          <input
                            id="pdf-upload"
                            type="file"
                            accept=".pdf"
                            onChange={handleFileChange}
                            className="hidden"
                          />
                          <label htmlFor="pdf-upload" className="cursor-pointer">
                            <Upload className={`w-12 h-12 mx-auto mb-3 ${
                              theme === 'dark' ? 'text-slate-500' : 'text-slate-400'
                            }`} />
                            {selectedFile ? (
                              <div>
                                <p className={`mb-1 ${
                                  theme === 'dark' ? 'text-slate-100' : 'text-slate-900'
                                }`}>{selectedFile.name}</p>
                                <p className={`text-sm ${
                                  theme === 'dark' ? 'text-slate-400' : 'text-slate-600'
                                }`}>Click to change file</p>
                              </div>
                            ) : (
                              <div>
                                <p className={`mb-1 ${
                                  theme === 'dark' ? 'text-slate-100' : 'text-slate-900'
                                }`}>Click to upload PDF</p>
                                <p className={`text-sm ${
                                  theme === 'dark' ? 'text-slate-400' : 'text-slate-600'
                                }`}>or drag and drop</p>
                              </div>
                            )}
                          </label>
                        </div>
                        
                        <Button
                          onClick={handlePdfSubmit}
                          className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
                          disabled={!selectedFile}
                        >
                          <Sparkles className="w-4 h-4 mr-2" />
                          Process PDF
                        </Button>
                      </div>
                    </div>
                    
                    <div className={`rounded-lg p-4 ${
                      theme === 'dark'
                        ? 'bg-purple-950 bg-opacity-50 border border-purple-900'
                        : 'bg-purple-50 border border-purple-200'
                    }`}>
                      <div className="flex gap-3">
                        <FileText className={`w-5 h-5 flex-shrink-0 ${
                          theme === 'dark' ? 'text-purple-400' : 'text-purple-600'
                        }`} />
                        <div>
                          <p className={`text-sm mb-1 ${
                            theme === 'dark' ? 'text-slate-200' : 'text-slate-900'
                          }`}>Smart Document Processing</p>
                          <p className={`text-xs ${
                            theme === 'dark' ? 'text-slate-400' : 'text-slate-600'
                          }`}>
                            AI extracts important information from your PDF and creates personalized study materials
                          </p>
                        </div>
                      </div>
                    </div>
                  </TabsContent>
                </Tabs>
              </CardContent>
            </Card>
          </div>

          {/* Today's Goals */}
          <div className="space-y-6">
            <Card className={
              theme === 'dark'
                ? 'bg-slate-900 border-slate-800'
                : 'bg-white border-slate-200'
            }>
              <CardHeader>
                <CardTitle className={theme === 'dark' ? 'text-slate-100' : 'text-slate-900'}>
                  Today's Goals
                </CardTitle>
                <CardDescription className={theme === 'dark' ? 'text-slate-400' : 'text-slate-600'}>
                  Keep up the momentum
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-start gap-3">
                  <div className="w-5 h-5 rounded-full border-2 border-green-500 flex items-center justify-center mt-0.5">
                    <div className="w-2 h-2 bg-green-500 rounded-full" />
                  </div>
                  <div>
                    <p className={`text-sm ${
                      theme === 'dark' ? 'text-slate-200' : 'text-slate-900'
                    }`}>30 min study session</p>
                    <p className="text-xs text-slate-500">Completed</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-5 h-5 rounded-full border-2 border-green-500 flex items-center justify-center mt-0.5">
                    <div className="w-2 h-2 bg-green-500 rounded-full" />
                  </div>
                  <div>
                    <p className={`text-sm ${
                      theme === 'dark' ? 'text-slate-200' : 'text-slate-900'
                    }`}>Review 10 flashcards</p>
                    <p className="text-xs text-slate-500">Completed</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className={`w-5 h-5 rounded-full border-2 mt-0.5 ${
                    theme === 'dark' ? 'border-slate-600' : 'border-slate-300'
                  }`} />
                  <div>
                    <p className={`text-sm ${
                      theme === 'dark' ? 'text-slate-200' : 'text-slate-900'
                    }`}>Complete 1 practice quiz</p>
                    <p className="text-xs text-slate-500">Pending</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-gradient-to-br from-blue-600 to-purple-600 text-white border-0">
              <CardContent className="p-6">
                <TrendingUp className="w-8 h-8 mb-4 opacity-90" />
                <p className="mb-2">Your study efficiency is up 23% this week!</p>
                <p className="text-sm opacity-90">Keep using AI-powered study tools to maximize your learning.</p>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
