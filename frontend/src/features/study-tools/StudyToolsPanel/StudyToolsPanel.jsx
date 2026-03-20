import { useState } from 'react';
import { BookOpen, HelpCircle, Maximize2, Minimize2 } from 'lucide-react';
import { Tabs, TabList, Tab, TabPanel } from '../../../components/ui/Tabs';
import Button from '../../../components/ui/Button';
import IconButton from '../../../components/ui/IconButton';
import { useLayout } from '../../../components/layout/WorkspaceLayout/LayoutContext';
import DeckList from '../DeckList/DeckList';
import FlashcardViewer from '../FlashcardViewer/FlashcardViewer';
import QuizList from '../QuizList/QuizList';
import QuizViewer from '../QuizViewer/QuizViewer';
import './StudyToolsPanel.css';

// Storage key for persisting last selected tab
const TAB_STORAGE_KEY = 'study-tools-tab';

/**
 * Study Tools panel - right sidebar with tabs for Flashcards and Quizzes
 */
function StudyToolsPanel() {
  const {
    studyToolsFullscreen,
    enterFullscreen,
    exitFullscreen,
    setRightPanelWidthPreset,
    studyPresetActive,
    revertPreset,
    isMobile
  } = useLayout();

  const [activeTab, setActiveTab] = useState(() => {
    try {
      const stored = localStorage.getItem(TAB_STORAGE_KEY);
      // If the stored tab was "game" (now removed), default to flashcards
      return stored === 'game' ? 'flashcards' : (stored || 'flashcards');
    } catch {
      return 'flashcards';
    }
  });

  // null = show list, string = show viewer for that item
  const [activeDeckId, setActiveDeckId] = useState(null);
  const [activeQuizId, setActiveQuizId] = useState(null);

  const handleTabChange = (value) => {
    setActiveTab(value);
    setActiveDeckId(null);
    setActiveQuizId(null);
    try {
      localStorage.setItem(TAB_STORAGE_KEY, value);
    } catch {
      // Ignore storage errors
    }
  };

  return (
    <div className="study-tools-panel">
      {/* Header */}
      <div className="panel-header">
        <h2 className="panel-header__title">Study Tools</h2>
        <div className="panel-header__actions">
          {!isMobile && !studyToolsFullscreen && (
            studyPresetActive ? (
              <Button
                variant="ghost"
                size="sm"
                onClick={revertPreset}
                title="Revert to default layout"
              >
                Revert
              </Button>
            ) : (
              <Button
                variant="ghost"
                size="sm"
                onClick={setRightPanelWidthPreset}
                title="Resize view to 2/3 width"
              >
                2/3 Study
              </Button>
            )
          )}
          <IconButton
            variant="ghost"
            size="sm"
            label={studyToolsFullscreen ? "Exit Fullscreen" : "Enter Fullscreen"}
            onClick={studyToolsFullscreen ? exitFullscreen : enterFullscreen}
          >
            {studyToolsFullscreen ? <Minimize2 size={18} /> : <Maximize2 size={18} />}
          </IconButton>
        </div>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={handleTabChange}>
        <div className="study-tools-panel__tabs">
          <TabList aria-label="Study tools">
            <Tab value="flashcards">
              <BookOpen size={16} />
              <span>Flashcards</span>
            </Tab>
            <Tab value="quizzes">
              <HelpCircle size={16} />
              <span>Quizzes</span>
            </Tab>
          </TabList>
        </div>

        {/* Flashcards Panel */}
        <TabPanel value="flashcards">
          <div className="study-tools-panel__content">
            {activeDeckId ? (
              <FlashcardViewer
                deckId={activeDeckId}
                onBack={() => setActiveDeckId(null)}
              />
            ) : (
              <DeckList onSelectDeck={setActiveDeckId} />
            )}
          </div>
        </TabPanel>

        {/* Quizzes Panel */}
        <TabPanel value="quizzes">
          <div className="study-tools-panel__content">
            {activeQuizId ? (
              <QuizViewer
                quizId={activeQuizId}
                onBack={() => setActiveQuizId(null)}
              />
            ) : (
              <QuizList onSelectQuiz={setActiveQuizId} />
            )}
          </div>
        </TabPanel>
      </Tabs>
    </div>
  );
}

export default StudyToolsPanel;
