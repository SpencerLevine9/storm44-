import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ToastProvider } from './components/ui/Toast';
import WorkspacePage from './pages/WorkspacePage';
import SettingsPage from './pages/SettingsPage';

function App() {
  return (
    <BrowserRouter>
      <ToastProvider position="bottom-right">
        <Routes>
          <Route path="/" element={<WorkspacePage />} />
          <Route path="/settings" element={<SettingsPage />} />
        </Routes>
      </ToastProvider>
    </BrowserRouter>
  );
}

export default App;
