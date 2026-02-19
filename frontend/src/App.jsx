import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ToastProvider } from './components/ui/Toast';
import { NotebookProvider } from './contexts/NotebookContext';
import { FlashcardProvider } from './contexts/FlashcardContext';
import WorkspacePage from './pages/WorkspacePage';
import SettingsPage from './pages/SettingsPage';

function App() {
  return (
    <BrowserRouter>
      <ToastProvider position="bottom-right">
        <NotebookProvider>
          <FlashcardProvider>
            <Routes>
              <Route path="/" element={<WorkspacePage />} />
              <Route path="/settings" element={<SettingsPage />} />
            </Routes>
          </FlashcardProvider>
        </NotebookProvider>
      </ToastProvider>
    </BrowserRouter>
  );
}

export default App;
