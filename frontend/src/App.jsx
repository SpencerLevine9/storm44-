import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ToastProvider } from './components/ui/Toast';
import { NotebookProvider } from './contexts/NotebookContext';
import { FlashcardProvider } from './contexts/FlashcardContext';
import { SourcesProvider } from './contexts/SourcesContext';
import { QuizProvider } from './contexts/QuizContext';
import WorkspacePage from './pages/WorkspacePage';
import SettingsPage from './pages/SettingsPage';

function App() {
  return (
    <BrowserRouter>
      <ToastProvider position="bottom-right">
        <NotebookProvider>
          <SourcesProvider>
            <FlashcardProvider>
              <QuizProvider>
                <Routes>
                  <Route path="/" element={<WorkspacePage />} />
                  <Route path="/settings" element={<SettingsPage />} />
                </Routes>
              </QuizProvider>
            </FlashcardProvider>
          </SourcesProvider>
        </NotebookProvider>
      </ToastProvider>
    </BrowserRouter>
  );
}

export default App;
